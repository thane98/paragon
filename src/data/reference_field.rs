use super::{Field, ReadState, Types, WriteState};
use pyo3::types::PyDict;
use pyo3::{PyObject, PyResult, Python, ToPyObject};
use serde::Deserialize;

#[derive(Clone, Debug, Deserialize)]
#[serde(rename_all = "snake_case")]
enum Format {
    U8,
    U16,
    U32,
    String,
    Pointer,
}

#[derive(Clone, Debug)]
enum ReadReferenceInfo {
    Index(usize),
    Key(String),
    Pointer(usize),
}

#[derive(Clone, Debug, Deserialize)]
pub struct ReferenceField {
    pub id: String,

    #[serde(default)]
    pub name: Option<String>,

    #[serde(default)]
    pub value: Option<u64>,

    #[serde(default, skip)]
    read_reference_info: Option<ReadReferenceInfo>,

    format: Format,

    table: String,
}

impl ReferenceField {
    pub fn read(&mut self, state: &mut ReadState) -> anyhow::Result<()> {
        match self.format {
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
            Format::String => match state.reader.read_string()? {
                Some(key) => self.read_reference_info = Some(ReadReferenceInfo::Key(key)),
                None => {}
            },
            Format::Pointer => match state.reader.read_pointer()? {
                Some(address) => {
                    self.read_reference_info = Some(ReadReferenceInfo::Pointer(address))
                }
                None => {}
            },
        }
        Ok(())
    }

    pub fn post_register_read(&self, rid: u64, state: &mut ReadState) {
        match &self.read_reference_info {
            Some(info) => match info {
                ReadReferenceInfo::Index(r) => {
                    state
                        .references
                        .add_id(*r, self.table.clone(), rid, self.id.clone());
                }
                ReadReferenceInfo::Key(r) => {
                    state
                        .references
                        .add_key(r.clone(), self.table.clone(), rid, self.id.clone());
                }
                ReadReferenceInfo::Pointer(r) => {
                    state
                        .references
                        .add_pointer(*r, self.table.clone(), rid, self.id.clone());
                }
            },
            None => {}
        }
    }

    pub fn write(&self, state: &mut WriteState) -> anyhow::Result<()> {
        match self.format {
            Format::U8 => state.writer.write_u8(self.resolve_index(state) as u8)?,
            Format::U16 => state.writer.write_u16(self.resolve_index(state) as u16)?,
            Format::U32 => state.writer.write_u32(self.resolve_index(state) as u32)?,
            Format::String => {
                let key = self
                    .value
                    .map(|rid| state.references.resolve_key(rid))
                    .flatten();
                match key {
                    Some(key) => state.writer.write_string(Some(&key))?,
                    None => state.writer.write_string(None)?,
                }
            }
            Format::Pointer => {
                if let Some(rid) = self.value {
                    state.references.add_known_pointer(rid, state.writer.tell());
                }
                state.writer.write_pointer(None)?;
            }
        }
        Ok(())
    }

    fn resolve_index(&self, state: &WriteState) -> usize {
        self.value
            .map(|rid| state.references.resolve_index(rid, &self.table))
            .flatten()
            .unwrap_or_default()
    }

    pub fn metadata(&self, py: Python) -> PyResult<PyObject> {
        let dict = PyDict::new(py);
        dict.set_item("type", "reference")?;
        dict.set_item("id", self.id.clone())?;
        dict.set_item("name", self.name.clone())?;
        dict.set_item("table", self.table.clone())?;
        Ok(dict.to_object(py))
    }

    pub fn clone_with_allocations(&self, _types: &mut Types) -> anyhow::Result<Field> {
        Ok(Field::Reference(self.clone()))
    }
}
