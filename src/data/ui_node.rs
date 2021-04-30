use pyo3::prelude::*;
use serde::Deserialize;

#[derive(Deserialize, Debug, Clone)]
pub struct NodeStoreContext {
    pub id_suffix: String,

    pub name_suffix: String,
}

#[pyclass]
#[derive(Deserialize, Debug, Clone)]
pub struct UINode {
    #[pyo3(get)]
    pub id: String,

    #[pyo3(get)]
    pub name: String,

    #[pyo3(get)]
    #[serde(default)]
    pub rid: u64,

    #[pyo3(get)]
    #[serde(default)]
    pub store: String,
}

impl UINode {
    pub fn new() -> Self {
        UINode {
            id: String::new(),
            name: String::new(),
            rid: 0,
            store: String::new(),
        }
    }
}
