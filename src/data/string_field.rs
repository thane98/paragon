use super::{Field, ReadState, Types, WriteState, diff_value::DiffValue};
use pyo3::types::PyDict;
use pyo3::{PyObject, PyResult, Python, ToPyObject};
use serde::Deserialize;

#[derive(Clone, Debug, Deserialize)]
pub struct StringField {
    pub id: String,

    #[serde(default)]
    pub name: Option<String>,

    #[serde(skip, default)]
    pub value_at_read_time: Option<String>,

    #[serde(default)]
    pub value: Option<String>,
}

impl StringField {
    pub fn read(&mut self, state: &mut ReadState) -> anyhow::Result<()> {
        self.value = state.reader.read_string()?;
        self.value_at_read_time = self.value.clone();
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
        dict.set_item("type", "string")?;
        dict.set_item("id", self.id.clone())?;
        dict.set_item("name", self.name.clone())?;
        Ok(dict.to_object(py))
    }

    pub fn clone_with_allocations(&self, _types: &mut Types) -> anyhow::Result<Field> {
        Ok(Field::String(self.clone()))
    }

    pub fn diff(&self) -> Option<DiffValue> {
        if self.value == self.value_at_read_time {
            None
        } else {
            Some(DiffValue::Str(self.value.clone()))
        }
    }
}
