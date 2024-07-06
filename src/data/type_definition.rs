use crate::data::fields::field::Field;
use crate::model::ui_node::UINode;
use pyo3::types::{PyDict, PyDictMethods};
use serde::Deserialize;
use std::collections::HashSet;

use pyo3::prelude::*;

#[derive(Clone, Debug, Default, Deserialize)]
pub struct TypeDefinition {
    fields: Vec<Field>,

    pub size: usize,

    #[serde(default)]
    pub key: Option<String>,

    #[serde(default)]
    pub display: Option<String>,

    #[serde(default)]
    pub display_function: Option<String>,

    #[serde(default)]
    pub ignore_for_copy: HashSet<String>,

    #[serde(default)]
    pub icon: Option<String>,

    #[serde(default)]
    pub index: Option<String>,

    #[serde(default)]
    pub node: Option<UINode>,
}

impl TypeDefinition {
    pub fn with_fields(fields: Vec<Field>) -> Self {
        TypeDefinition {
            fields,
            ..Default::default()
        }
    }

    pub fn get_fields(&self) -> &[Field] {
        &self.fields
    }

    pub fn get_field(&self, field_id: &str) -> Option<&Field> {
        self.fields.iter().find(|f| f.id() == field_id)
    }

    pub fn type_metadata(&self, py: Python) -> PyResult<PyObject> {
        let dict = PyDict::new_bound(py);
        dict.set_item("size", self.size)?;
        dict.set_item("key", self.key.clone())?;
        dict.set_item("display", self.display.clone())?;
        dict.set_item("display_function", self.display_function.clone())?;
        Ok(dict.to_object(py))
    }

    pub fn field_metadata(&self, py: Python) -> PyResult<PyObject> {
        let dict = PyDict::new_bound(py);
        for field in &self.fields {
            let field_metadata = field.metadata(py)?;
            dict.set_item(field.id(), field_metadata)?;
        }
        Ok(dict.to_object(py))
    }

    pub fn post_init(&mut self) {
        for field in &mut self.fields {
            if let Field::Bytes(f) = field {
                if f.value.len() != f.info.length {
                    f.value = vec![0; f.info.length];
                }
            }
        }
    }
}
