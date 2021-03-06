use super::{MultiNode, ReadOutput, ReadReferences, Store, Types};
use anyhow::{anyhow, Context};
use mila::LayeredFilesystem;
use serde::Deserialize;
use std::collections::HashMap;
use std::path::PathBuf;

#[derive(Deserialize)]
pub struct Stores {
    stores: Vec<Store>,
}

impl Stores {
    pub fn dirty_files(&self) -> Vec<String> {
        let mut res: Vec<String> = Vec::new();
        for store in &self.stores {
            res.extend(store.dirty_files());
        }
        res
    }

    pub fn load(dir: &PathBuf) -> anyhow::Result<Self> {
        let mut all_stores: Vec<Store> = Vec::new();
        if dir.exists() {
            let paths = std::fs::read_dir(dir).with_context(|| {
                format!("Failed to walk directory {} in Stores.", dir.display())
            })?;
            for path in paths {
                match path {
                    Ok(p) => {
                        let metadata = p.metadata()?;
                        if metadata.is_file() {
                            all_stores.extend(Stores::read_definitions(p.path())?);
                        }
                    }
                    Err(_) => {}
                }
            }
        }
        Ok(Stores { stores: all_stores })
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
        fs: &LayeredFilesystem,
    ) -> anyhow::Result<ReadOutput> {
        let mut final_output = ReadOutput::new();
        for store in &mut self.stores {
            let output = store
                .read(types, references, fs)
                .with_context(|| format!("Failed to read data from store '{}'.", store.id()))?;
            final_output.merge(output);
        }
        Ok(final_output)
    }

    pub fn write(
        &self,
        types: &Types,
        tables: &HashMap<String, (u64, String)>,
        fs: &LayeredFilesystem,
    ) -> anyhow::Result<()> {
        for store in &self.stores {
            if self.is_dirty(&store.id()) {
                store
                    .write(types, tables, fs)
                    .with_context(|| format!("Failed to write store '{}'.", store.id()))?;
            }
        }
        Ok(())
    }

    pub fn is_dirty(&self, id: &str) -> bool {
        let store = self.stores.iter().find(|s| id == s.id());
        match store {
            Some(s) => s.is_dirty(),
            None => false,
        }
    }

    pub fn set_dirty(&mut self, id: &str, dirty: bool) -> anyhow::Result<()> {
        let store = self.stores.iter_mut().find(|s| id == s.id());
        match store {
            Some(s) => s.set_dirty(dirty),
            None => Err(anyhow!("Store {} does not exist.", id)),
        }
    }

    pub fn multi_keys(
        &self,
        multi_id: &str,
        fs: &LayeredFilesystem,
    ) -> anyhow::Result<Vec<String>> {
        let store = self
            .stores
            .iter()
            .find(|s| multi_id == s.id())
            .ok_or(anyhow!("Multi {} is not registered.", multi_id))?;
        match store {
            Store::Multi(m) => m.keys(fs),
            _ => Err(anyhow!("Store {} is not a multi.", multi_id)),
        }
    }

    pub fn multi_open(
        &mut self,
        types: &mut Types,
        references: &mut ReadReferences,
        fs: &LayeredFilesystem,
        multi_id: &str,
        key: String,
    ) -> anyhow::Result<u64> {
        let store = self
            .stores
            .iter_mut()
            .find(|s| multi_id == s.id())
            .ok_or(anyhow!("Multi {} is not registered.", multi_id))?;
        match store {
            Store::Multi(m) => m.open(types, references, fs, key),
            _ => Err(anyhow!("Store {} is not a multi.", multi_id)),
        }
    }

    pub fn multi_duplicate(
        &mut self,
        types: &mut Types,
        references: &mut ReadReferences,
        fs: &LayeredFilesystem,
        multi_id: &str,
        source: String,
        destination: String,
    ) -> anyhow::Result<u64> {
        let store = self
            .stores
            .iter_mut()
            .find(|s| multi_id == s.id())
            .ok_or(anyhow!("Multi {} is not registered.", multi_id))?;
        match store {
            Store::Multi(m) => m.duplicate(types, references, fs, source, destination),
            _ => Err(anyhow!("Store {} is not a multi.", multi_id)),
        }
    }

    pub fn multi_set_dirty(
        &mut self,
        multi_id: &str,
        key: &str,
        dirty: bool,
    ) -> anyhow::Result<()> {
        let store = self
            .stores
            .iter_mut()
            .find(|s| multi_id == s.id())
            .ok_or(anyhow!("Multi {} is not registered.", multi_id))?;
        match store {
            Store::Multi(m) => m.set_dirty(key, dirty),
            _ => Err(anyhow!("Store {} is not a multi.", multi_id)),
        }
    }

    pub fn multi_nodes(&self) -> Vec<MultiNode> {
        self.stores
            .iter()
            .filter_map(|s| match s {
                Store::Multi(m) => Some(MultiNode {
                    id: m.id.clone(),
                    name: m.name.clone(),
                    typename: m.typename.clone(),
                }),
                _ => None,
            })
            .collect()
    }
}
