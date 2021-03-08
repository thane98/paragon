use super::{ReadReferences, SingleStore, Types};
use anyhow::{anyhow, Context};
use mila::LayeredFilesystem;
use serde::Deserialize;
use std::collections::HashMap;

struct OpenInfo {
    pub rid: u64,

    pub store: SingleStore,

    pub dirty: bool,

    pub tables: HashMap<String, (u64, String)>,
}

#[derive(Deserialize)]
pub struct MultiStore {
    pub id: String,

    pub name: String,

    pub typename: String,

    pub directory: String,

    pub glob: Option<String>,

    #[serde(default)]
    pub hidden: bool,

    #[serde(default)]
    pub wrap_ids: Vec<String>,

    #[serde(default)]
    pub merge_tables: bool,

    #[serde(skip, default)]
    stores: HashMap<String, OpenInfo>,
}

impl MultiStore {
    pub fn dirty_files(&self) -> Vec<String> {
        self.stores
            .iter()
            .filter(|(_, v)| v.dirty)
            .map(|(k, _)| k.to_owned())
            .collect()
    }

    pub fn open(
        &mut self,
        types: &mut Types,
        references: &mut ReadReferences,
        fs: &LayeredFilesystem,
        key: String,
    ) -> anyhow::Result<(u64, HashMap<String, (u64, String)>)> {
        match self.stores.get(&key) {
            Some(o) => Ok((o.rid, o.tables.clone())),
            None => {
                let info = self.open_uncached(types, references, fs, key.clone())?;
                let rid = info.rid;
                let tables = info.tables.clone();
                self.stores.insert(key, info);
                Ok((rid, tables))
            }
        }
    }

    fn open_uncached(
        &self,
        types: &mut Types,
        references: &mut ReadReferences,
        fs: &LayeredFilesystem,
        key: String,
    ) -> anyhow::Result<OpenInfo> {
        let mut store = SingleStore::new(self.typename.clone(), key.clone(), true);
        let output = store
            .read(types, references, fs)
            .with_context(|| format!("Failed to read from key '{}' multi '{}'", key, self.id))?;
        let rid = output
            .nodes
            .into_iter()
            .next()
            .ok_or(anyhow!("Multi produced no nodes."))?
            .rid;
        Ok(OpenInfo {
            rid,
            store,
            dirty: false,
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
        fs: &LayeredFilesystem,
        source: String,
        destination: String,
    ) -> anyhow::Result<(u64, HashMap<String, (u64, String)>)> {
        let mut info = self.open_uncached(types, references, fs, source)?;
        let rid = info.rid;
        let tables = info.tables.clone();
        info.store.filename = destination.clone();
        self.stores.insert(destination, info);
        Ok((rid, tables))
    }

    pub fn write(
        &self,
        types: &Types,
        tables: &HashMap<String, (u64, String)>,
        fs: &LayeredFilesystem,
    ) -> anyhow::Result<()> {
        for (k, v) in &self.stores {
            if v.dirty {
                if self.merge_tables {
                    let mut effective_tables: HashMap<String, (u64, String)> = HashMap::new();
                    effective_tables.extend(tables.clone());
                    effective_tables.extend(v.tables.clone());
                    v.store.write(types, &effective_tables, fs)
                } else {
                    v.store.write(types, &tables, fs)
                }
                .with_context(|| format!("Failed to write key '{}' for multi '{}'", k, self.id))?;
            }
        }
        Ok(())
    }

    pub fn set_dirty(&mut self, key: &str, dirty: bool) -> anyhow::Result<()> {
        match self.stores.get_mut(key) {
            Some(i) => {
                i.dirty = dirty;
                Ok(())
            }
            None => Err(anyhow!("{} is not an open store.", key)),
        }
    }

    pub fn keys(&self, fs: &LayeredFilesystem) -> anyhow::Result<Vec<String>> {
        let files = match &self.glob {
            Some(p) => fs.list(&self.directory, Some(p)),
            None => fs.list(&self.directory, None),
        }?;
        Ok(files)
    }

    pub fn is_dirty(&self) -> bool {
        self.stores.values().find(|i| i.dirty).is_some()
    }

    pub fn table(&self, key: &str, table: &str) -> Option<(u64, String)> {
        self.stores
            .get(key)
            .map(|info| info.tables.get(table))
            .flatten()
            .map(|(rid, field_id)| (*rid, field_id.to_owned()))
    }
}
