use super::{ReadState, WriteState, Types, Field};
use pyo3::types::PyDict;
use pyo3::{PyObject, PyResult, Python, ToPyObject};
use serde::Deserialize;

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

    pub paths: Vec<String>,

    #[serde(default = "default_localized_value")]
    pub localized: bool,
}

impl MessageField {
    pub fn read(&mut self, state: &mut ReadState) -> anyhow::Result<()> {
        self.value = state.reader.read_string()?;
        Ok(())
    }

    pub fn write(&self, state: &mut WriteState) -> anyhow::Result<()> {
        match &self.value {
            Some(v) => state.writer.write_string(Some(v))?,
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
}
