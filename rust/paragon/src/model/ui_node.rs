use pyo3::prelude::*;
use serde::Deserialize;

use super::id::RecordId;

#[derive(Deserialize, Debug, Clone)]
pub struct NodeStoreContext {
    pub id_suffix: String,

    pub name_suffix: String,
}

#[pyclass]
#[derive(Deserialize, Debug, Clone, Default)]
pub struct UINode {
    #[pyo3(get)]
    pub id: String,

    #[pyo3(get)]
    pub name: String,

    #[pyo3(get)]
    #[serde(skip, default)]
    pub rid: Option<RecordId>,

    #[pyo3(get)]
    #[serde(default)]
    pub store: String,
}

impl UINode {
    pub fn new() -> Self {
        UINode::default()
    }
}
