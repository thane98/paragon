use std::collections::HashMap;

use crate::data::archives::Archives;
use anyhow::anyhow;
use mila::LayeredFilesystem;
use serde::Deserialize;

use crate::data::serialization::references::ReadReferences;
use crate::data::storage::asset_store::AssetStore;
use crate::data::storage::cmp_store::CmpStore;
use crate::data::storage::multi_store::MultiStore;
use crate::data::storage::single_store::SingleStore;
use crate::data::storage::table_inject_store::TableInjectStore;
use crate::data::Types;
use crate::model::id::{RecordId, StoreNumber};
use crate::model::read_output::ReadOutput;
use crate::model::store_description::StoreDescription;

use super::fe14_aset_store::FE14ASetStore;

#[derive(Deserialize, Debug)]
#[serde(rename_all = "snake_case", tag = "type")]
pub enum Store {
    Single(SingleStore),
    Multi(MultiStore),
    Asset(AssetStore),
    TableInject(TableInjectStore),
    #[serde(rename(deserialize = "fe14_aset"))]
    FE14ASet(FE14ASetStore),
    Cmp(CmpStore),
}

macro_rules! on_store {
    ($on:ident, $with:ident, $body:tt) => {
        match $on {
            Store::Single($with) => $body,
            Store::Asset($with) => $body,
            Store::Multi($with) => $body,
            Store::TableInject($with) => $body,
            Store::FE14ASet($with) => $body,
            Store::Cmp($with) => $body,
        }
    };
}

impl Store {
    pub fn dirty_files(&self) -> Vec<String> {
        on_store!(self, s, { s.dirty_files() })
    }

    pub fn filename(&self) -> String {
        on_store!(self, s, { s.filename() })
    }

    pub fn set_filename(&mut self, filename: String) -> anyhow::Result<()> {
        match self {
            Store::Single(s) => s.set_filename(filename),
            Store::Asset(s) => s.set_filename(filename),
            Store::Multi(_) => return Err(anyhow!("Unsupported operation.")),
            Store::TableInject(s) => s.set_filename(filename),
            Store::FE14ASet(s) => s.set_filename(filename),
            Store::Cmp(s) => s.set_archive(filename),
        }
        Ok(())
    }

    pub fn id(&self) -> &str {
        on_store!(self, s, { &s.id })
    }

    pub fn describe(&self) -> Vec<StoreDescription> {
        let mut items = if let Store::Multi(m) = self {
            m.describe()
        } else {
            vec![]
        };
        let store_type = match self {
            Store::Single(_) => "Single",
            Store::Multi(_) => "Multi",
            Store::Asset(_) => "Asset",
            Store::TableInject(_) => "TableInject",
            Store::FE14ASet(_) => "FE14ASet",
            Store::Cmp(_) => "Cmp",
        };
        items.push(StoreDescription {
            store_number: self.store_number().unwrap_or_default(),
            path: self.filename(),
            store_type: store_type.to_owned(),
            dirty: self.is_dirty(),
        });
        items
    }

    pub fn read(
        &mut self,
        types: &mut Types,
        references: &mut ReadReferences,
        archives: &mut Archives,
        fs: &LayeredFilesystem,
    ) -> anyhow::Result<ReadOutput> {
        match self {
            Store::Single(s) => s.read(types, references, fs),
            Store::Asset(s) => s.read(types, fs),
            Store::Multi(_) => Ok(ReadOutput::new()),
            Store::TableInject(s) => s.read(types, references, fs),
            Store::FE14ASet(s) => s.read(types, fs),
            Store::Cmp(s) => s.read(types, references, archives, fs),
        }
    }

    pub fn write(
        &self,
        types: &Types,
        tables: &HashMap<String, (RecordId, String)>,
        archives: &mut Archives,
        fs: &LayeredFilesystem,
    ) -> anyhow::Result<()> {
        match self {
            Store::Single(s) => s.write(types, tables, fs),
            Store::Asset(s) => s.write(types, fs),
            Store::Multi(s) => s.write(types, tables, archives, fs),
            Store::TableInject(s) => s.write(types, tables, fs),
            Store::FE14ASet(s) => s.write(types, fs),
            Store::Cmp(s) => s.write(types, tables, archives, fs),
        }
    }

    pub fn is_dirty(&self) -> bool {
        match self {
            Store::Single(s) => s.dirty,
            Store::Asset(s) => s.dirty,
            Store::Multi(s) => s.is_dirty(),
            Store::TableInject(s) => s.dirty,
            Store::FE14ASet(s) => s.dirty,
            Store::Cmp(s) => s.dirty,
        }
    }

    pub fn is_forced_dirty_value(&self) -> bool {
        match self {
            Store::Single(s) => s.force_dirty,
            Store::Asset(s) => s.force_dirty,
            Store::Multi(_) => false,
            Store::TableInject(s) => s.force_dirty,
            Store::FE14ASet(s) => s.force_dirty,
            Store::Cmp(s) => s.force_dirty,
        }
    }

    pub fn mark_forced_dirty(&mut self) -> anyhow::Result<()> {
        match self {
            Store::Single(s) => s.force_dirty = true,
            Store::Asset(s) => s.force_dirty = true,
            Store::TableInject(s) => s.force_dirty = true,
            Store::Multi(_) => {
                return Err(anyhow!(
                    "Cannot mark a multi as dirty. Mark individual keys instead."
                ));
            }
            Store::FE14ASet(s) => s.force_dirty = true,
            Store::Cmp(s) => s.force_dirty = true,
        }
        Ok(())
    }

    pub fn set_dirty(&mut self, dirty: bool, force: bool) -> anyhow::Result<()> {
        // If a client forced a particular value and isn't trying to force a new value, ignore the request.
        if self.is_forced_dirty_value() && !force {
            return Ok(());
        }
        match self {
            Store::Single(s) => s.dirty = dirty,
            Store::Asset(s) => s.dirty = dirty,
            Store::TableInject(s) => s.dirty = dirty,
            Store::Multi(_) => {
                return Err(anyhow!(
                    "Cannot mark a multi as dirty. Mark individual keys instead."
                ));
            }
            Store::FE14ASet(s) => s.dirty = dirty,
            Store::Cmp(s) => s.dirty = dirty,
        }
        if force {
            self.mark_forced_dirty()?;
        }
        Ok(())
    }

    pub fn store_number(&self) -> anyhow::Result<StoreNumber> {
        on_store!(self, s, { s.store_number })
            .ok_or_else(|| anyhow!("Store number is uninitialized"))
    }

    pub fn set_store_number(&mut self, store_number: StoreNumber) {
        on_store!(self, s, { s.store_number = Some(store_number) });
    }
}
