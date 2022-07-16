use pyo3::types::PyDict;
use pyo3::{PyObject, PyResult, Python, ToPyObject};
use serde::Deserialize;

use crate::data::fields::field::Field;
use crate::data::Types;
use crate::model::id::StoreNumber;
use crate::model::read_state::ReadState;
use crate::model::write_state::WriteState;

#[derive(Clone, Debug, Deserialize, Default)]
pub struct StringField {
    pub id: String,

    #[serde(default)]
    pub name: Option<String>,

    #[serde(skip, default)]
    pub value_at_read_time: Option<String>,

    #[serde(default)]
    pub value: Option<String>,

    #[serde(default)]
    pub cstring: bool,
}

impl StringField {
    pub fn new(id: String) -> Self {
        StringField {
            id,
            ..Default::default()
        }
    }

    pub fn read(&mut self, state: &mut ReadState) -> anyhow::Result<()> {
        if self.cstring {
            self.value = state.reader.read_c_string()?;
        } else {
            self.value = state.reader.read_string()?;
        }
        Ok(())
    }

    pub fn write(&self, state: &mut WriteState) -> anyhow::Result<()> {
        match &self.value {
            Some(v) => {
                if self.cstring {
                    state.writer.write_c_string(v.clone())?
                } else {
                    state.writer.write_string(Some(v))?
                }
            }
            None => state.writer.write_u32(0)?,
        }
        Ok(())
    }

    pub fn metadata(&self, py: Python) -> PyResult<PyObject> {
        let dict = PyDict::new(py);
        dict.set_item("type", "string")?;
        dict.set_item("id", self.id.clone())?;
        dict.set_item("name", self.name.clone())?;
        Ok(dict.to_object(py))
    }

    pub fn clone_with_allocations(&self, _types: &mut Types, _store_number: StoreNumber) -> anyhow::Result<Field> {
        Ok(Field::String(self.clone()))
    }
}
