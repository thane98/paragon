use std::sync::Arc;
use std::usize;

use crate::data::fields::field::Field;
use crate::data::Types;
use crate::model::id::{RecordId, StoreNumber};
use crate::model::read_state::ReadState;
use crate::model::write_state::WriteState;
use pyo3::types::PyDict;
use pyo3::{PyObject, PyResult, Python, ToPyObject};
use serde::Deserialize;

#[derive(Clone, Debug, Deserialize)]
pub struct AppendPrefixKeyTransform {
    prefix: String,
}

#[derive(Clone, Debug, Deserialize)]
#[serde(rename_all = "snake_case", tag = "type")]
pub enum KeyTransform {
    AppendPrefix(AppendPrefixKeyTransform),
}

#[derive(Clone, Debug, Deserialize)]
#[serde(rename_all = "snake_case")]
enum Format {
    U8,
    U16,
    U32,
    String,
    Label,
    Pointer,
    FieldU16 { id: String },
}

#[derive(Clone, Debug)]
pub enum ReadReferenceInfo {
    Index(usize),
    Key(String),
    Pointer(usize),
    Field(String, i64),
}

#[derive(Clone, Debug, Deserialize)]
pub struct ReferenceFieldInfo {
    pub id: String,

    #[serde(default)]
    pub name: Option<String>,

    #[serde(default)]
    pub key_transform: Option<KeyTransform>,

    #[serde(default)]
    pub index_default_value: i64,

    #[serde(default)]
    pub string_default_value: Option<String>,

    #[serde(default)]
    pub cstring: bool,

    format: Format,

    table: String,
}

#[derive(Clone, Debug, Deserialize)]
pub struct ReferenceField {
    #[serde(flatten)]
    pub info: Arc<ReferenceFieldInfo>,

    #[serde(default, skip)]
    pub read_reference_info: Option<ReadReferenceInfo>,

    #[serde(skip, default)]
    pub value: Option<RecordId>,
}

impl AppendPrefixKeyTransform {
    pub fn apply(&self, original: String) -> String {
        format!("{}{}", self.prefix, original)
    }

    pub fn remove(&self, original: String) -> String {
        original.trim_start_matches(&self.prefix).to_string()
    }
}

impl KeyTransform {
    pub fn apply(&self, original: String) -> String {
        match self {
            KeyTransform::AppendPrefix(t) => t.apply(original),
        }
    }

    pub fn remove(&self, original: String) -> String {
        match self {
            KeyTransform::AppendPrefix(t) => t.remove(original),
        }
    }
}

impl ReferenceField {
    pub fn read(&mut self, state: &mut ReadState) -> anyhow::Result<()> {
        self.read_reference_info = None;
        match self.info.format.clone() {
            Format::U8 => {
                self.read_reference_info =
                    Some(ReadReferenceInfo::Index(state.reader.read_u8()? as usize))
            }
            Format::U16 => {
                self.read_reference_info =
                    Some(ReadReferenceInfo::Index(state.reader.read_u16()? as usize))
            }
            Format::U32 => {
                self.read_reference_info =
                    Some(ReadReferenceInfo::Index(state.reader.read_u32()? as usize))
            }
            Format::String => {
                let data = if self.info.cstring {
                    state.reader.read_c_string()?
                } else {
                    state.reader.read_string()?
                };
                match data {
                    Some(t) => {
                        let value = if let Some(transform) = &self.info.key_transform {
                            transform.apply(t)
                        } else {
                            t
                        };
                        self.read_reference_info = Some(ReadReferenceInfo::Key(value));
                    }
                    None => {}
                }
            }
            Format::Label => {
                let data = state
                    .reader
                    .read_labels()?
                    .and_then(|v| v.last().map(|v| v.to_string()));
                match data {
                    Some(t) => {
                        let value = if let Some(transform) = &self.info.key_transform {
                            transform.apply(t)
                        } else {
                            t
                        };
                        self.read_reference_info = Some(ReadReferenceInfo::Key(value));
                    }
                    None => {}
                }
            }
            Format::Pointer => match state.reader.read_pointer()? {
                Some(address) => {
                    self.read_reference_info = Some(ReadReferenceInfo::Pointer(address))
                }
                None => {}
            },
            Format::FieldU16 { id } => {
                let value = state.reader.read_u16()?;
                self.read_reference_info = Some(ReadReferenceInfo::Field(id, value as i64));
            }
        }
        Ok(())
    }

    pub fn post_register_read(&self, rid: RecordId, state: &mut ReadState) {
        match &self.read_reference_info {
            Some(info) => match info {
                ReadReferenceInfo::Index(r) => {
                    state
                        .references
                        .add_id(*r, self.info.table.clone(), rid, self.info.id.clone());
                }
                ReadReferenceInfo::Key(r) => {
                    state
                        .references
                        .add_key(r.clone(), self.info.table.clone(), rid, self.info.id.clone());
                }
                ReadReferenceInfo::Pointer(r) => {
                    state
                        .references
                        .add_pointer(*r, self.info.table.clone(), rid, self.info.id.clone());
                }
                ReadReferenceInfo::Field(target_field, v) => {
                    state.references.add_field(
                        *v,
                        self.info.table.clone(),
                        target_field.clone(),
                        rid,
                        self.info.id.clone(),
                    );
                }
            },
            None => {}
        }
    }

    pub fn write(&self, state: &mut WriteState) -> anyhow::Result<()> {
        match self.info.format.clone() {
            Format::U8 => state.writer.write_u8(self.resolve_index(state) as u8)?,
            Format::U16 => state.writer.write_u16(self.resolve_index(state) as u16)?,
            Format::U32 => state.writer.write_u32(self.resolve_index(state) as u32)?,
            Format::Label => {
                let key = self.value.and_then(|rid| state.references.resolve_key(rid));
                match key {
                    Some(key) => {
                        if let Some(t) = &self.info.key_transform {
                            state.writer.write_label(&t.remove(key))
                        } else {
                            state.writer.write_label(&key)
                        }?
                    }
                    None => {}
                }
            }
            Format::String => {
                let key = self.value.and_then(|rid| state.references.resolve_key(rid));
                match key {
                    Some(key) => {
                        if let Some(t) = &self.info.key_transform {
                            self.write_string(state, &t.remove(key))
                        } else {
                            self.write_string(state, &key)
                        }?
                    }
                    None => {
                        if let Some(s) = &self.info.string_default_value {
                            self.write_string(state, s)?;
                        } else {
                            state.writer.write_string(None)?;
                        }
                    }
                }
            }
            Format::Pointer => {
                if let Some(rid) = self.value {
                    state.references.add_known_pointer(rid, state.writer.tell());
                }
                state.writer.write_pointer(None)?;
            }
            Format::FieldU16 { id } => {
                let value = self
                    .value
                    .and_then(|rid| state.references.resolve_field(rid, &id))
                    .unwrap_or_default();
                state.writer.write_u16(value as u16)?;
            }
        }
        Ok(())
    }

    fn write_string(&self, state: &mut WriteState, value: &str) -> anyhow::Result<()> {
        if self.info.cstring {
            state.writer.write_c_string(value.to_string())
        } else {
            state.writer.write_string(Some(value))
        }?;
        Ok(())
    }

    fn resolve_index(&self, state: &WriteState) -> usize {
        self.value
            .and_then(|rid| state.references.resolve_index(rid, &self.info.table))
            .unwrap_or(self.info.index_default_value as usize)
    }

    pub fn metadata(&self, py: Python) -> PyResult<PyObject> {
        let dict = PyDict::new(py);
        dict.set_item("type", "reference")?;
        dict.set_item("id", self.info.id.clone())?;
        dict.set_item("name", self.info.name.clone())?;
        dict.set_item("table", self.info.table.clone())?;
        Ok(dict.to_object(py))
    }

    pub fn clone_with_allocations(
        &self,
        _types: &mut Types,
        _store_number: StoreNumber,
    ) -> anyhow::Result<Field> {
        Ok(Field::Reference(self.clone()))
    }
}
