use std::sync::Arc;

use pyo3::types::PyDict;
use pyo3::{PyObject, PyResult, Python, ToPyObject};
use serde::Deserialize;

use crate::data::fields::field::Field;
use crate::data::Types;
use crate::model::id::StoreNumber;
use crate::model::read_state::ReadState;
use crate::model::write_state::WriteState;

fn default_localized_value() -> bool {
    true
}

#[derive(Clone, Debug, Deserialize)]
pub struct MessageFieldInfo {
    pub id: String,

    #[serde(default)]
    pub name: Option<String>,

    pub paths: Vec<String>,

    #[serde(default = "default_localized_value")]
    pub localized: bool,

    #[serde(default)]
    pub cstring: bool,
}

#[derive(Clone, Debug, Deserialize)]
pub struct MessageField {
    #[serde(flatten)]
    pub info: Arc<MessageFieldInfo>,

    #[serde(default)]
    pub value: Option<String>,
}

impl MessageField {
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
                    state.writer.write_c_string(v.to_string())?
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
        dict.set_item("type", "message")?;
        dict.set_item("id", self.info.id.clone())?;
        dict.set_item("name", self.info.name.clone())?;
        dict.set_item("paths", self.info.paths.clone())?;
        dict.set_item("localized", self.info.localized)?;
        Ok(dict.to_object(py))
    }

    pub fn clone_with_allocations(
        &self,
        _types: &mut Types,
        _store_number: StoreNumber,
    ) -> anyhow::Result<Field> {
        Ok(Field::Message(self.clone()))
    }
}
