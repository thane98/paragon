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
