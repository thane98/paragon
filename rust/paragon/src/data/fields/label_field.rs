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
pub struct LabelFieldInfo {
    pub id: String,

    #[serde(default)]
    pub name: Option<String>,

    // Generate the value at write time from another string field.
    #[serde(default)]
    generate_from: Option<String>,

    // Legacy disambiguation tool for labels. If we get a list of labels when reading, take the label at the provided index.
    // Default is to take the last label in the list.
    #[serde(default)]
    index: Option<usize>,

    // Force a value regardless of what's found during reading.
    // This is for labels where anything else will break the file.
    #[serde(default)]
    forced_value: Option<String>,
}

#[derive(Clone, Debug, Deserialize)]
pub struct LabelField {
    #[serde(flatten)]
    pub info: Arc<LabelFieldInfo>,

    #[serde(default)]
    pub value: Option<String>,
}

impl LabelField {
    pub fn read(&mut self, state: &mut ReadState) -> anyhow::Result<()> {
        self.value.clone_from(&self.info.forced_value);
        if self.value.is_none() {
            self.value = state.reader.read_labels()?.and_then(|v| {
                let index = self.info.index.unwrap_or(v.len() - 1);
                if index < v.len() {
                    Some(v[index].clone())
                } else {
                    None
                }
            });
        }

        Ok(())
    }

    pub fn write(&self, state: &mut WriteState) -> anyhow::Result<()> {
        let value = if let Some(id) = &self.info.generate_from {
            if let Some(rid) = state.rid_stack.last() {
                state.types.string(*rid, id)
            } else {
                None
            }
        } else {
            self.value.clone()
        };
        if let Some(v) = value {
            state.writer.write_label(&v)?;
        }
        Ok(())
    }

    pub fn metadata(&self, py: Python) -> PyResult<PyObject> {
        let dict = PyDict::new_bound(py);
        dict.set_item("type", "label")?;
        dict.set_item("id", self.info.id.clone())?;
        dict.set_item("name", self.info.name.clone())?;
        Ok(dict.to_object(py))
    }

    pub fn clone_with_allocations(
        &self,
        _types: &mut Types,
        _store_number: StoreNumber,
    ) -> anyhow::Result<Field> {
        Ok(Field::Label(self.clone()))
    }
}
