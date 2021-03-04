use anyhow::{anyhow, Context};
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
    archives: HashMap<String, TextArchive>,
    localizer: mila::PathLocalizer,
    language: mila::Language,
}

impl TextData {
    fn finalized_path(&self, path: &str, localized: bool) -> anyhow::Result<String> {
        if localized {
            let path = self.localizer.localize(path, &self.language)?;
            Ok(path)
        } else {
            Ok(path.to_owned())
        }
    }

    pub fn dirty_files(&self) -> Vec<String> {
        self.archives
            .iter()
            .filter(|(_, v)| v.is_dirty())
            .map(|(k, _)| k.to_owned())
            .collect()
    }

    pub fn load(fs: &LayeredFilesystem, path: &PathBuf) -> anyhow::Result<Self> {
        let raw_defs = std::fs::read_to_string(path).with_context(|| {
            format!(
                "Failed to read text definitions from path '{}'",
                path.display()
            )
        })?;
        let defs: Vec<TextDataDefinition> = serde_yaml::from_str(&raw_defs).with_context(|| {
            format!(
                "Failed to parse text definitions from path '{}'",
                path.display()
            )
        })?;
        Ok(TextData {
            defs,
            archives: HashMap::new(),
            localizer: fs.localizer(),
            language: fs.language(),
        })
    }

    pub fn new_archive(&mut self, path: &str, localized: bool) -> anyhow::Result<()> {
        self.archives.insert(self.finalized_path(path, localized)?, TextArchive::new());
        Ok(())
    }

    pub fn open_archive(
        &mut self,
        fs: &LayeredFilesystem,
        path: &str,
        localized: bool,
    ) -> anyhow::Result<()> {
        let archive_key = self.finalized_path(path, localized)?;
        if self.archives.contains_key(&archive_key) {
            return Ok(());
        }
        let archive = fs.read_text_archive(&path, localized).with_context(|| {
            format!(
                "Failed to read text from path: {}, localized: {}",
                path, localized
            )
        })?;
        self.archives.insert(archive_key, archive);
        Ok(())
    }

    pub fn archive_is_open(&self, path: &str, localized: bool) -> anyhow::Result<bool> {
        let archive_key = self.finalized_path(path, localized)?;
        Ok(self.archives.contains_key(&archive_key))
    }

    pub fn read(&mut self, fs: &LayeredFilesystem) -> anyhow::Result<()> {
        self.archives.clear();
        for def in &self.defs {
            let key = self.finalized_path(&def.path, def.localized)?;
            let archive = fs
                .read_text_archive(&key, false)
                .with_context(|| format!("Failed to read text from definition '{:?}'", def))?;
            self.archives
                .insert(key, archive);
        }
        Ok(())
    }

    pub fn save(&self, fs: &LayeredFilesystem) -> anyhow::Result<()> {
        for (p, v) in &self.archives {
            if v.is_dirty() {
                fs.write_text_archive(p, v, false).with_context(|| {
                    format!("Failed to write text data to path: {}", p)
                })?;
            }
        }
        Ok(())
    }

    pub fn has_message(&self, path: &str, localized: bool, key: &str) -> bool {
        match self.finalized_path(path, localized) {
            Ok(p) => match self.archives.get(&p) {
                Some(a) => a.has_message(key),
                None => false,
            },
            Err(_) => false,
        }
    }

    pub fn message(&self, path: &str, localized: bool, key: &str) -> Option<String> {
        match self.finalized_path(path, localized) {
            Ok(p) => match self.archives.get(&p) {
                Some(a) => a.get_message(key),
                None => None,
            }
            Err(_) => None
        }
        
    }

    pub fn enumerate_messages(&self, path: &str, localized: bool) -> Option<Vec<String>> {
        match self.finalized_path(path, localized) {
            Ok(p) => match self.archives.get(&p) {
                Some(a) => Some(a.get_entries().iter().map(|(k, _)| k.clone()).collect()),
                None => None,
            },
            Err(_) => None
        }
        
    }

    pub fn set_message(
        &mut self,
        path: &str,
        localized: bool,
        key: &str,
        value: Option<String>,
    ) -> anyhow::Result<()> {
        let archive_key = self.finalized_path(path, localized)?;
        match self.archives.get_mut(&archive_key) {
            Some(a) => Ok(match value {
                Some(v) => a.set_message(key, &v),
                None => a.delete_message(key),
            }),
            None => Err(anyhow!("Archive {:?} is not loaded.", archive_key)),
        }
    }

    pub fn enumerate_archives(&self, fs: &LayeredFilesystem) -> anyhow::Result<Vec<String>> {
        let res = fs
            .list("m", Some("**/*.bin.lz"))
            .context("Failed to enumerate text archives.")?;
        Ok(res)
    }
}
