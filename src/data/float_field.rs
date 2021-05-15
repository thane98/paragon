use super::{Field, ReadState, Types, WriteState, diff_value::DiffValue};
use pyo3::types::PyDict;
use pyo3::{PyObject, PyResult, Python, ToPyObject};
use serde::Deserialize;

#[derive(Clone, Debug, Deserialize)]
pub struct FloatField {
    pub id: String,

    #[serde(default)]
    pub name: Option<String>,

    #[serde(default)]
    pub value: f32,

    #[serde(skip, default)]
    pub value_at_read_time: Option<f32>,
}

impl FloatField {
    pub fn read(&mut self, state: &mut ReadState) -> anyhow::Result<()> {
        self.value = state.reader.read_f32()?;
        self.value_at_read_time = Some(self.value);
        Ok(())
    }

    pub fn write(&self, state: &mut WriteState) -> anyhow::Result<()> {
        state.writer.write_f32(self.value)?;
        Ok(())
    }

    pub fn metadata(&self, py: Python) -> PyResult<PyObject> {
        let dict = PyDict::new(py);
        dict.set_item("type", "float")?;
        dict.set_item("id", self.id.clone())?;
        dict.set_item("name", self.name.clone())?;
        Ok(dict.to_object(py))
    }

    pub fn clone_with_allocations(&self, _types: &mut Types) -> anyhow::Result<Field> {
        Ok(Field::Float(self.clone()))
    }

    pub fn diff(&self) -> Option<DiffValue> {
        if let Some(value) = self.value_at_read_time {
            if self.value == value {
                None
            } else {
                Some(DiffValue::Float(self.value))
            }
        } else {
            None
        }
    }
}
