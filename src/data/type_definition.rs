use super::{Field, UINode};
use pyo3::types::PyDict;
use pyo3::{PyObject, PyResult, Python, ToPyObject};
use serde::Deserialize;

#[derive(Clone, Debug, Deserialize)]
pub struct TypeDefinition {
    fields: Vec<Field>,

    pub size: usize,

    #[serde(default)]
    pub key: Option<String>,

    #[serde(default)]
    pub display: Option<String>,

    #[serde(default)]
    pub icon: Option<String>,

    #[serde(default)]
    pub node: Option<UINode>,
}

impl TypeDefinition {
    pub fn get_fields(&self) -> &[Field] {
        &self.fields
    }

    pub fn type_metadata(&self, py: Python) -> PyResult<PyObject> {
        let dict = PyDict::new(py);
        dict.set_item("size", self.size)?;
        dict.set_item("key", self.key.clone())?;
        dict.set_item("display", self.display.clone())?;
        Ok(dict.to_object(py))
    }

    pub fn field_metadata(&self, py: Python) -> PyResult<PyObject> {
        let dict = PyDict::new(py);
        for field in &self.fields {
            let field_metadata = field.metadata(py)?;
            dict.set_item(field.id().clone(), field_metadata)?;
        }
        Ok(dict.to_object(py))
    }

    pub fn post_init(&mut self) {
        for field in &mut self.fields {
            match field {
                Field::Bytes(f) => f.value = vec![0; f.length],
                _ => {}
            }
        }
    }
}
