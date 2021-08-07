use pyo3::{PyObject, PyResult, Python, ToPyObject};
use pyo3::types::PyDict;
use serde::Deserialize;

use crate::model::diff_value::DiffValue;

use crate::data::Types;
use crate::model::read_state::ReadState;
use crate::model::write_state::WriteState;
use crate::data::fields::field::Field;

fn default_localized_value() -> bool {
    true
}

#[derive(Clone, Debug, Deserialize)]
pub struct MessageField {
    pub id: String,

    #[serde(default)]
    pub name: Option<String>,

    #[serde(default)]
    pub value: Option<String>,

    #[serde(skip, default)]
    pub value_at_read_time: Option<String>,

    pub paths: Vec<String>,

    #[serde(default = "default_localized_value")]
    pub localized: bool,

    #[serde(default)]
    pub cstring: bool,
}

impl MessageField {
    pub fn read(&mut self, state: &mut ReadState) -> anyhow::Result<()> {
        if self.cstring {
            self.value = state.reader.read_c_string()?;
        } else {
            self.value = state.reader.read_string()?;
        }
        self.value_at_read_time = self.value.clone();
        Ok(())
    }

    pub fn write(&self, state: &mut WriteState) -> anyhow::Result<()> {
        match &self.value {
            Some(v) => if self.cstring {
                state.writer.write_c_string(v.to_string())?
            } else {
                state.writer.write_string(Some(v))?
            },
            None => state.writer.write_u32(0)?,
        }
        Ok(())
    }

    pub fn metadata(&self, py: Python) -> PyResult<PyObject> {
        let dict = PyDict::new(py);
        dict.set_item("type", "message")?;
        dict.set_item("id", self.id.clone())?;
        dict.set_item("name", self.name.clone())?;
        dict.set_item("paths", self.paths.clone())?;
        dict.set_item("localized", self.localized)?;
        Ok(dict.to_object(py))
    }

    pub fn clone_with_allocations(&self, _types: &mut Types) -> anyhow::Result<Field> {
        Ok(Field::Message(self.clone()))
    }

    pub fn diff(&self) -> Option<DiffValue> {
        if self.value == self.value_at_read_time {
            None
        } else {
            Some(DiffValue::Str(self.value.clone()))
        }
    }
}
