use pyo3::{PyObject, PyResult, Python, ToPyObject};
use pyo3::types::PyDict;
use serde::Deserialize;

use crate::model::diff_value::DiffValue;

use crate::data::Types;
use crate::model::write_state::WriteState;
use crate::model::read_state::ReadState;
use crate::data::fields::field::Field;

#[derive(Clone, Debug, Deserialize)]
pub struct LabelField {
    pub id: String,

    #[serde(default)]
    pub name: Option<String>,

    #[serde(default)]
    pub value: Option<String>,

    #[serde(skip, default)]
    pub value_at_read_time: Option<String>,

    #[serde(default)]
    generate_from: Option<String>,

    #[serde(default)]
    index: Option<usize>,
}

impl LabelField {
    pub fn read(&mut self, state: &mut ReadState) -> anyhow::Result<()> {
        self.value = match state.reader.read_labels()? {
            Some(v) => {
                let index = self.index.unwrap_or(v.len() - 1);
                if index < v.len() {
                    Some(v[index].clone())
                } else {
                    None
                }
            }
            None => None,
        };
        self.value_at_read_time = self.value.clone();
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

    pub fn diff(&self) -> Option<DiffValue> {
        if self.value == self.value_at_read_time {
            None
        } else {
            Some(DiffValue::Str(self.value.clone()))
        }
    }
}
