use std::sync::Arc;

use pyo3::types::PyDict;
use pyo3::{PyObject, PyResult, Python, ToPyObject};
use serde::Deserialize;

use crate::data::fields::field::Field;
use crate::data::Types;
use crate::model::id::StoreNumber;
use crate::model::read_state::ReadState;
use crate::model::write_state::WriteState;


#[derive(Clone, Debug, Deserialize, Default)]
pub struct StringFieldInfo {
    pub id: String,

    #[serde(default)]
    pub name: Option<String>,

    #[serde(default)]
    pub cstring: bool,
}

#[derive(Clone, Debug, Deserialize, Default)]
pub struct StringField {
    #[serde(flatten)]
    pub info: Arc<StringFieldInfo>,

    #[serde(default)]
    pub value: Option<String>,
}

impl StringField {
    pub fn new(id: String) -> Self {
        StringField {
            info: Arc::new(StringFieldInfo {
                id,
                ..Default::default()
            }),
            ..Default::default()
        }
    }

    pub fn read(&mut self, state: &mut ReadState) -> anyhow::Result<()> {
        if self.info.cstring {
            self.value = state.reader.read_c_string()?;
        } else {
            self.value = state.reader.read_string()?;
        }
        Ok(())
    }

    pub fn write(&self, state: &mut WriteState) -> anyhow::Result<()> {
        match &self.value {
            Some(v) => {
                if self.info.cstring {
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
        dict.set_item("id", self.info.id.clone())?;
        dict.set_item("name", self.info.name.clone())?;
        Ok(dict.to_object(py))
    }

    pub fn clone_with_allocations(
        &self,
        _types: &mut Types,
        _store_number: StoreNumber,
    ) -> anyhow::Result<Field> {
        Ok(Field::String(self.clone()))
    }
}
