use crate::data::archives::Archives;
use crate::data::serialization::references::ReadReferences;
use crate::data::storage::store::Store;
use crate::data::Types;
use crate::model::id::{RecordId, StoreNumber};
use crate::model::multi_node::MultiNode;
use crate::model::read_output::ReadOutput;
use anyhow::{anyhow, bail, Context};
use mila::LayeredFilesystem;
use std::collections::HashMap;
use std::path::PathBuf;

pub struct Stores {
    next_store_number: StoreNumber,
    stores_by_id: HashMap<String, StoreNumber>,
    stores_by_number: HashMap<StoreNumber, Store>,
    stores_owned_by_multi: HashMap<StoreNumber, StoreNumber>,
}

impl Stores {
    pub fn dirty_files(&self) -> Vec<String> {
        let mut res: Vec<String> = Vec::new();
        for store in self.stores_by_number.values() {
            res.extend(store.dirty_files());
        }
        res
    }

    pub fn load(dir: &PathBuf) -> anyhow::Result<Self> {
        let mut next_store_number = StoreNumber::default();
        let mut stores_by_id = HashMap::new();
        let mut stores_by_number = HashMap::new();
        if dir.exists() {
            let paths = std::fs::read_dir(dir).with_context(|| {
                format!("Failed to walk directory {} in Stores.", dir.display())
            })?;
            for path in paths {
                if let Ok(p) = path {
                    if p.metadata()?.is_file() {
                        for mut store in Stores::read_definitions(p.path())? {
                            store.set_store_number(next_store_number);
                            stores_by_id.insert(store.id().to_owned(), next_store_number);
                            stores_by_number.insert(next_store_number, store);
                            next_store_number.increment();
                        }
                    }
                }
            }
        }
        Ok(Stores {
            next_store_number,
            stores_by_id,
            stores_by_number,
            stores_owned_by_multi: HashMap::new(),
        })
    }

    fn read_definitions(path: PathBuf) -> anyhow::Result<Vec<Store>> {
        let raw_stores = std::fs::read_to_string(&path).with_context(|| {
            format!(
                "Failed to read store definitions from path '{}'",
                path.display()
            )
        })?;
        let stores: Vec<Store> = serde_yaml::from_str(&raw_stores).with_context(|| {
            format!(
                "Failed to parse store definitions from path '{}'",
                path.display()
            )
        })?;
        Ok(stores)
    }

    pub fn read(
        &mut self,
        types: &mut Types,
        references: &mut ReadReferences,
        archives: &mut Archives,
        fs: &LayeredFilesystem,
    ) -> anyhow::Result<ReadOutput> {
        let mut final_output = ReadOutput::new();
        for store in self.stores_by_number.values_mut() {
            let output = store
                .read(types, references, archives, fs)
                .with_context(|| format!("Failed to read data from store '{}'.", store.id()))?;
            final_output.merge(output);
        }
        Ok(final_output)
    }

    pub fn write(
        &self,
        types: &Types,
        tables: &HashMap<String, (RecordId, String)>,
        archives: &mut Archives,
        fs: &LayeredFilesystem,
    ) -> anyhow::Result<()> {
        for store in self.stores_by_number.values() {
            if self.is_dirty(store.id()) {
                store
                    .write(types, tables, archives, fs)
                    .with_context(|| format!("Failed to write store '{}'.", store.id()))?;
            }
        }
        Ok(())
    }

    pub fn is_dirty(&self, id: &str) -> bool {
        self.store_from_id(id)
            .map(|s| s.is_dirty())
            .unwrap_or_default()
    }

    pub fn set_dirty(&mut self, id: &str, dirty: bool) -> anyhow::Result<()> {
        self.store_from_id_mut(id)?.set_dirty(dirty)
    }

    pub fn set_dirty_by_number(
        &mut self,
        store_number: StoreNumber,
        dirty: bool,
    ) -> anyhow::Result<()> {
        if self.stores_by_number.contains_key(&store_number) {
            self.stores_by_number
                .get_mut(&store_number)
                .unwrap()
                .set_dirty(dirty)?;
            return Ok(());
        }

        let multi_store_number = self.stores_owned_by_multi.get(&store_number).cloned();
        if let Some(multi_store_number) = multi_store_number {
            let store = self.store_from_store_number_mut(multi_store_number)?;
            if let Store::Multi(m) = store {
                m.set_dirty_by_number(store_number, dirty)?;
                return Ok(());
            }
        }
        bail!("Bad store number '{:?}'", store_number)
    }

    pub fn multi_keys(
        &self,
        multi_id: &str,
        fs: &LayeredFilesystem,
    ) -> anyhow::Result<Vec<String>> {
        match self.store_from_id(multi_id)? {
            Store::Multi(m) => m.keys(fs),
            _ => Err(anyhow!("Store {} is not a multi.", multi_id)),
        }
    }

    pub fn multi_open(
        &mut self,
        types: &mut Types,
        references: &mut ReadReferences,
        archives: &mut Archives,
        fs: &LayeredFilesystem,
        multi_id: &str,
        key: String,
    ) -> anyhow::Result<(RecordId, HashMap<String, (RecordId, String)>)> {
        let store_number = self.next_store_number;
        match self.store_from_id_mut(multi_id)? {
            Store::Multi(m) => {
                let (rid, tables, consumed_store_number) =
                    m.open(types, references, archives, fs, key, store_number)?;
                if consumed_store_number {
                    self.next_store_number.increment();
                    let multi_number = *self.stores_by_id.get(multi_id).unwrap();
                    self.stores_owned_by_multi
                        .insert(store_number, multi_number);
                }
                Ok((rid, tables))
            }
            _ => Err(anyhow!("Store {} is not a multi.", multi_id)),
        }
    }

    pub fn multi_duplicate(
        &mut self,
        types: &mut Types,
        references: &mut ReadReferences,
        archives: &mut Archives,
        fs: &LayeredFilesystem,
        multi_id: &str,
        source: String,
        destination: String,
    ) -> anyhow::Result<(RecordId, HashMap<String, (RecordId, String)>)> {
        let store_number = self.next_store_number;
        match self.store_from_id_mut(multi_id)? {
            Store::Multi(m) => {
                let result = m.duplicate(
                    types,
                    references,
                    archives,
                    fs,
                    store_number,
                    source,
                    destination,
                )?;
                self.next_store_number.increment();
                let multi_number = *self.stores_by_id.get(multi_id).unwrap();
                self.stores_owned_by_multi
                    .insert(store_number, multi_number);
                Ok(result)
            }
            _ => Err(anyhow!("Store {} is not a multi.", multi_id)),
        }
    }

    pub fn multi_set_dirty(
        &mut self,
        multi_id: &str,
        key: &str,
        dirty: bool,
    ) -> anyhow::Result<()> {
        match self.store_from_id_mut(multi_id)? {
            Store::Multi(m) => m.set_dirty(key, dirty),
            _ => Err(anyhow!("Store {} is not a multi.", multi_id)),
        }
    }

    pub fn multi_nodes(&self) -> Vec<MultiNode> {
        self.stores_by_number
            .values()
            .filter_map(|s| match s {
                Store::Multi(m) => Some(MultiNode {
                    id: m.id.clone(),
                    name: m.name.clone(),
                    typename: m.typename.clone(),
                    hidden: m.hidden,
                    wrap_ids: m.wrap_ids.clone(),
                }),
                _ => None,
            })
            .collect()
    }

    pub fn multi_table(
        &self,
        multi_id: &str,
        key: &str,
        table: &str,
    ) -> anyhow::Result<Option<(RecordId, String)>> {
        match self.store_from_id(multi_id)? {
            Store::Multi(m) => Ok(m.table(key, table)),
            _ => Err(anyhow!("Store {} is not a multi.", multi_id)),
        }
    }

    fn store_from_id(&self, id: &str) -> anyhow::Result<&Store> {
        let store_number = *self
            .stores_by_id
            .get(id)
            .ok_or_else(|| anyhow!("Store '{}' does not exist", id))?;
        self.store_from_store_number(store_number)
    }

    fn store_from_id_mut(&mut self, id: &str) -> anyhow::Result<&mut Store> {
        let store_number = *self
            .stores_by_id
            .get(id)
            .ok_or_else(|| anyhow!("Store '{}' does not exist", id))?;
        self.store_from_store_number_mut(store_number)
    }

    fn store_from_store_number(&self, store_number: StoreNumber) -> anyhow::Result<&Store> {
        if let Some(store) = self.stores_by_number.get(&store_number) {
            Ok(store)
        } else {
            bail!("Bad store number '{:?}'", store_number)
        }
    }

    fn store_from_store_number_mut(
        &mut self,
        store_number: StoreNumber,
    ) -> anyhow::Result<&mut Store> {
        if let Some(store) = self.stores_by_number.get_mut(&store_number) {
            Ok(store)
        } else {
            bail!("Bad store number '{:?}'", store_number)
        }
    }
}
