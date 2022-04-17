use pyo3::types::PyDict;
use pyo3::{PyObject, PyResult, Python, ToPyObject};
use serde::Deserialize;

use crate::data::fields::field::Field;
use crate::data::Types;
use crate::model::read_state::ReadState;
use crate::model::write_state::WriteState;

#[derive(Clone, Debug, Deserialize)]
pub struct LabelField {
    pub id: String,

    #[serde(default)]
    pub name: Option<String>,

    #[serde(default)]
    pub value: Option<String>,

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

impl LabelField {
    pub fn read(&mut self, state: &mut ReadState) -> anyhow::Result<()> {
        self.value = self.forced_value.clone();
        if let None = self.value {
            self.value = state.reader.read_labels()?
                .map(|v| {
                    let index = self.index.unwrap_or(v.len() - 1);
                    if index < v.len() {
                        Some(v[index].clone())
                    } else {
                        None
                    }
                })
                .flatten();
        }

        Ok(())
    }

    pub fn write(&self, state: &mut WriteState) -> anyhow::Result<()> {
        let value = if let Some(id) = &self.generate_from {
            if let Some(rid) = state.rid_stack.last() {
                state.types.string(*rid, id)
            } else {
                None
            }
        } else {
            self.value.clone()
        };
        match value {
            Some(v) => state.writer.write_label(&v)?,
            None => {}
        }
        Ok(())
    }

    pub fn metadata(&self, py: Python) -> PyResult<PyObject> {
        let dict = PyDict::new(py);
        dict.set_item("type", "label")?;
        dict.set_item("id", self.id.clone())?;
        dict.set_item("name", self.name.clone())?;
        Ok(dict.to_object(py))
    }

    pub fn clone_with_allocations(&self, _types: &mut Types) -> anyhow::Result<Field> {
        Ok(Field::Label(self.clone()))
    }
}
