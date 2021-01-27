use anyhow::anyhow;
use mila::{LayeredFilesystem, TextArchive};
use serde::Deserialize;
use std::collections::HashMap;
use std::path::PathBuf;

fn default_localized_value() -> bool {
    true
}

#[derive(Debug, Deserialize)]
struct TextDataDefinition {
    pub path: String,

    #[serde(default = "default_localized_value")]
    pub localized: bool,
}

pub struct TextData {
    defs: Vec<TextDataDefinition>,
    archives: HashMap<(String, bool), TextArchive>,
}

impl TextData {
    pub fn load(path: &PathBuf) -> anyhow::Result<Self> {
        let raw_defs = std::fs::read_to_string(path)?;
        let defs: Vec<TextDataDefinition> = serde_yaml::from_str(&raw_defs)?;
        Ok(TextData {
            defs,
            archives: HashMap::new(),
        })
    }

    pub fn open_archive(&mut self, fs: &LayeredFilesystem, path: &str, localized: bool) -> anyhow::Result<()> {
        let archive = fs.read_text_archive(&path, localized)?;
        let archive_key = (path.to_owned(), localized);
        self.archives.insert(archive_key, archive);
        Ok(())
    }

    pub fn read(&mut self, fs: &LayeredFilesystem) -> anyhow::Result<()> {
        self.archives.clear();
        for def in &self.defs {
            let archive = fs.read_text_archive(&def.path, def.localized)?;
            self.archives
                .insert((def.path.clone(), def.localized), archive);
        }
        Ok(())
    }

    pub fn save(&self, fs: &LayeredFilesystem) -> anyhow::Result<()> {
        for ((p, l), v) in &self.archives {
            if v.is_dirty() {
                fs.write_text_archive(p, v, *l)?;
            }
        }
        Ok(())
    }

    pub fn has_message(&self, path: String, localized: bool, key: &str) -> bool {
        let archive_key = (path, localized);
        match self.archives.get(&archive_key) {
            Some(a) => a.has_message(key),
            None => false,
        }
    }

    pub fn message(&self, path: String, localized: bool, key: &str) -> Option<String> {
        let archive_key = (path, localized);
        match self.archives.get(&archive_key) {
            Some(a) => a.get_message(key),
            None => None,
        }
    }

    pub fn enumerate_messages(&self, path: String, localized: bool) -> Option<Vec<String>> {
        let archive_key = (path, localized);
        match self.archives.get(&archive_key) {
            Some(a) => Some(a.get_entries().iter().map(|(k, _)| k.clone()).collect()),
            None => None,
        }
    }

    pub fn set_message(
        &mut self,
        path: String,
        localized: bool,
        key: &str,
        value: Option<String>,
    ) -> anyhow::Result<()> {
        let archive_key = (path, localized);
        match self.archives.get_mut(&archive_key) {
            Some(a) => Ok(match value {
                Some(v) => a.set_message(key, &v),
                None => a.delete_message(key),
            }),
            None => Err(anyhow!("Archive {:?} is not loaded.", archive_key)),
        }
    }

    pub fn enumerate_archives(&self, fs: &LayeredFilesystem) -> anyhow::Result<Vec<String>> {
        let res = fs.list("m", Some("**/*.bin.lz"))?;
        Ok(res)
    }
}
