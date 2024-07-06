use std::sync::Arc;

use pyo3::types::{PyDict, PyDictMethods};
use pyo3::{PyObject, PyResult, Python, ToPyObject};
use serde::Deserialize;

use crate::data::fields::field::Field;
use crate::data::Types;
use crate::model::id::StoreNumber;
use crate::model::read_state::ReadState;
use crate::model::write_state::WriteState;

#[derive(Clone, Debug, Deserialize)]
pub struct FloatFieldInfo {
    pub id: String,

    #[serde(default)]
    pub name: Option<String>,
}

#[derive(Clone, Debug, Deserialize)]
pub struct FloatField {
    #[serde(flatten)]
    pub info: Arc<FloatFieldInfo>,

    #[serde(default)]
    pub value: f32,
}

impl FloatField {
    pub fn read(&mut self, state: &mut ReadState) -> anyhow::Result<()> {
        self.value = state.reader.read_f32()?;
        Ok(())
    }

    pub fn write(&self, state: &mut WriteState) -> anyhow::Result<()> {
        state.writer.write_f32(self.value)?;
        Ok(())
    }

    pub fn metadata(&self, py: Python) -> PyResult<PyObject> {
        let dict = PyDict::new_bound(py);
        dict.set_item("type", "float")?;
        dict.set_item("id", self.info.id.clone())?;
        dict.set_item("name", self.info.name.clone())?;
        Ok(dict.to_object(py))
    }

    pub fn clone_with_allocations(
        &self,
        _types: &mut Types,
        _store_number: StoreNumber,
    ) -> anyhow::Result<Field> {
        Ok(Field::Float(self.clone()))
    }
}
