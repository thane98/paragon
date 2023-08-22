use std::collections::HashMap;

use crate::data::archives::Archives;
use crate::model::store_description::StoreDescription;
use anyhow::{anyhow, Context};
use mila::LayeredFilesystem;
use serde::Deserialize;

use crate::data::serialization::inject_count_strategy::CountStrategy;
use crate::data::serialization::inject_location_strategy::LocationStrategy;
use crate::data::serialization::references::ReadReferences;
use crate::data::storage::asset_store::AssetStore;
use crate::data::storage::cmp_store::CmpStore;
use crate::data::storage::single_store::SingleStore;
use crate::data::storage::store::Store;
use crate::data::storage::table_inject_store::TableInjectStore;
use crate::data::Types;
use crate::model::id::{RecordId, StoreNumber};

#[derive(Deserialize, Debug, Clone)]
#[serde(rename_all = "snake_case")]
enum MultiStoreType {
    Single,
    Asset,
    TableInject {
        location_strategy: LocationStrategy,
        count_strategy: CountStrategy,
    },
    Cmp {
        internal_file: String,
    },
}

fn default_multi_store_type() -> MultiStoreType {
    MultiStoreType::Single
}

#[derive(Debug)]
struct OpenInfo {
    pub rid: RecordId,
    pub store: Store,
    pub key: String,
    pub tables: HashMap<String, (RecordId, String)>,
}

#[derive(Deserialize, Debug)]
pub struct MultiStore {
    pub id: String,

    pub name: String,

    pub typename: String,

    pub directory: String,

    pub glob: Option<String>,

    #[serde(default = "default_multi_store_type")]
    multi_store_type: MultiStoreType,

    #[serde(default)]
    pub hidden: bool,

    #[serde(default)]
    pub wrap_ids: Vec<String>,

    #[serde(default)]
    pub merge_tables: bool,

    #[serde(skip, default)]
    pub store_number: Option<StoreNumber>,

    #[serde(skip, default)]
    stores_by_id: HashMap<String, StoreNumber>,

    #[serde(skip, default)]
    stores_by_number: HashMap<StoreNumber, OpenInfo>,
}

fn create_instance_for_multi(
    instance_type: MultiStoreType,
    typename: String,
    filename: String,
    store_number: StoreNumber,
    dirty: bool,
) -> Store {
    match instance_type {
        MultiStoreType::Single => Store::Single(SingleStore::create_instance_for_multi(
            typename,
            filename,
            store_number,
            dirty,
        )),
        MultiStoreType::Asset => Store::Asset(AssetStore::create_instance_for_multi(
            typename,
            filename,
            store_number,
            dirty,
        )),
        MultiStoreType::TableInject {
            location_strategy,
            count_strategy,
        } => Store::TableInject(TableInjectStore::create_instance_for_multi(
            typename,
            filename,
            store_number,
            dirty,
            location_strategy,
            count_strategy,
        )),
        MultiStoreType::Cmp { internal_file } => Store::Cmp(CmpStore::create_instance_for_multi(
            typename,
            filename,
            internal_file,
            store_number,
            dirty,
        )),
    }
}

impl MultiStore {
    pub fn filename(&self) -> String {
        self.directory.clone()
    }

    pub fn dirty_files(&self) -> Vec<String> {
        self.stores_by_number
            .values()
            .filter(|info| info.store.is_dirty())
            .map(|info| info.key.to_owned())
            .collect()
    }

    pub fn open(
        &mut self,
        types: &mut Types,
        references: &mut ReadReferences,
        archives: &mut Archives,
        fs: &LayeredFilesystem,
        key: String,
        store_number: StoreNumber,
    ) -> anyhow::Result<(RecordId, HashMap<String, (RecordId, String)>, bool)> {
        match self.info_from_id(&key) {
            Some(o) => Ok((o.rid, o.tables.clone(), false)),
            None => {
                let info =
                    self.open_uncached(types, references, archives, fs, key.clone(), store_number)?;
                let rid = info.rid;
                let tables = info.tables.clone();
                self.stores_by_id.insert(key, store_number);
                self.stores_by_number.insert(store_number, info);
                Ok((rid, tables, true))
            }
        }
    }

    fn open_uncached(
        &self,
        types: &mut Types,
        references: &mut ReadReferences,
        archives: &mut Archives,
        fs: &LayeredFilesystem,
        key: String,
        store_number: StoreNumber,
    ) -> anyhow::Result<OpenInfo> {
        let mut store = create_instance_for_multi(
            self.multi_store_type.clone(),
            self.typename.clone(),
            key.clone(),
            store_number,
            false,
        );
        let output = store
            .read(types, references, archives, fs)
            .with_context(|| format!("Failed to read from key '{}' multi '{}'", key, self.id))?;
        let rid = output
            .nodes
            .into_iter()
            .next()
            .ok_or_else(|| anyhow!("Multi produced no nodes."))?
            .rid
            .unwrap();
        Ok(OpenInfo {
            rid,
            key,
            store,
            tables: if self.merge_tables {
                output.tables
            } else {
                HashMap::new()
            },
        })
    }

    pub fn duplicate(
        &mut self,
        types: &mut Types,
        references: &mut ReadReferences,
        archives: &mut Archives,
        fs: &LayeredFilesystem,
        store_number: StoreNumber,
        source: String,
        destination: String,
    ) -> anyhow::Result<(RecordId, HashMap<String, (RecordId, String)>)> {
        let mut info = self.open_uncached(types, references, archives, fs, source, store_number)?;
        let rid = info.rid;
        let tables = info.tables.clone();
        info.store.set_filename(destination.clone())?;
        info.store.set_dirty(true, false)?;
        info.key = destination.clone();
        self.stores_by_id.insert(destination, store_number);
        self.stores_by_number.insert(store_number, info);
        Ok((rid, tables))
    }

    pub fn write(
        &self,
        types: &Types,
        tables: &HashMap<String, (RecordId, String)>,
        archives: &mut Archives,
        fs: &LayeredFilesystem,
    ) -> anyhow::Result<()> {
        for info in self.stores_by_number.values() {
            if info.store.is_dirty() {
                if self.merge_tables {
                    let mut effective_tables: HashMap<String, (RecordId, String)> = HashMap::new();
                    effective_tables.extend(tables.clone());
                    effective_tables.extend(info.tables.clone());
                    info.store.write(types, &effective_tables, archives, fs)
                } else {
                    info.store.write(types, tables, archives, fs)
                }
                .with_context(|| {
                    format!("Failed to write key '{}' for multi '{}'", info.key, self.id)
                })?;
            }
        }
        Ok(())
    }

    pub fn describe(&self) -> Vec<StoreDescription> {
        self.stores_by_number
            .values()
            .fold(Vec::new(), |mut accum, info| {
                accum.extend(info.store.describe());
                accum
            })
    }

    pub fn is_dirty(&self) -> bool {
        self.stores_by_number.values().any(|i| i.store.is_dirty())
    }

    pub fn set_dirty(&mut self, key: &str, dirty: bool, force: bool) -> anyhow::Result<()> {
        match self.info_from_id_mut(key) {
            Some(i) => i.store.set_dirty(dirty, force),
            None => Err(anyhow!("{} is not an open store.", key)),
        }
    }

    pub fn set_dirty_by_number(
        &mut self,
        store_number: StoreNumber,
        dirty: bool,
        force: bool,
    ) -> anyhow::Result<()> {
        match self.info_from_number_mut(store_number) {
            Some(i) => i.store.set_dirty(dirty, force),
            None => Err(anyhow!("{:?} is not an open store.", store_number)),
        }
    }

    pub fn keys(&self, fs: &LayeredFilesystem) -> anyhow::Result<Vec<String>> {
        let files = match &self.glob {
            Some(p) => fs.list(&self.directory, Some(p), false),
            None => fs.list(&self.directory, None, false),
        }?;
        Ok(files)
    }

    pub fn table(&self, key: &str, table: &str) -> Option<(RecordId, String)> {
        self.info_from_id(key)
            .and_then(|info| info.tables.get(table))
            .map(|(rid, field_id)| (*rid, field_id.to_owned()))
    }

    fn info_from_id(&self, id: &str) -> Option<&OpenInfo> {
        self.stores_by_id
            .get(id)
            .and_then(|store_number| self.info_from_number(*store_number))
    }

    fn info_from_id_mut(&mut self, id: &str) -> Option<&mut OpenInfo> {
        self.info_from_number_mut(self.stores_by_id.get(id)?.to_owned())
    }

    fn info_from_number(&self, store_number: StoreNumber) -> Option<&OpenInfo> {
        self.stores_by_number.get(&store_number)
    }

    fn info_from_number_mut(&mut self, store_number: StoreNumber) -> Option<&mut OpenInfo> {
        self.stores_by_number.get_mut(&store_number)
    }
}
