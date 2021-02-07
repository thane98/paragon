use super::{ReadReferences, SingleStore, Types};
use anyhow::{anyhow, Context};
use mila::LayeredFilesystem;
use serde::Deserialize;
use std::collections::HashMap;

struct OpenInfo {
    pub rid: u64,

    pub store: SingleStore,

    pub dirty: bool,
}

#[derive(Deserialize)]
pub struct MultiStore {
    pub id: String,

    pub name: String,

    pub typename: String,

    pub directory: String,

    pub glob: Option<String>,

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
    ) -> anyhow::Result<u64> {
        match self.stores.get(&key) {
            Some(o) => Ok(o.rid),
            None => {
                let (store, rid) = self.open_uncached(types, references, fs, key.clone())?;
                let info = OpenInfo {
                    rid,
                    store,
                    dirty: false,
                };
                self.stores.insert(key, info);
                Ok(rid)
            }
        }
    }

    fn open_uncached(
        &self,
        types: &mut Types,
        references: &mut ReadReferences,
        fs: &LayeredFilesystem,
        key: String,
    ) -> anyhow::Result<(SingleStore, u64)> {
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
        Ok((store, rid))
    }

    pub fn duplicate(
        &mut self,
        types: &mut Types,
        references: &mut ReadReferences,
        fs: &LayeredFilesystem,
        source: String,
        destination: String,
    ) -> anyhow::Result<u64> {
        let (store, rid) = self.open_uncached(types, references, fs, source)?;
        let info = OpenInfo {
            rid,
            store,
            dirty: false,
        };
        self.stores.insert(destination, info);
        Ok(rid)
    }

    pub fn write(
        &self,
        types: &Types,
        tables: &HashMap<String, (u64, String)>,
        fs: &LayeredFilesystem,
    ) -> anyhow::Result<()> {
        for (k, v) in &self.stores {
            if v.dirty {
                v.store.write(types, tables, fs).with_context(|| {
                    format!("Failed to write key '{}' for multi '{}'", k, self.id)
                })?;
            }
        }
        Ok(())
    }

    pub fn mark_dirty(&mut self, key: &str) -> anyhow::Result<()> {
        match self.stores.get_mut(key) {
            Some(i) => {
                i.dirty = true;
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
}
