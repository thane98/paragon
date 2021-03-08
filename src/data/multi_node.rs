use pyo3::prelude::*;

#[pyclass]
pub struct MultiNode {
    #[pyo3(get)]
    pub id: String,

    #[pyo3(get)]
    pub name: String,

    #[pyo3(get)]
    pub typename: String,

    #[pyo3(get)]
    pub hidden: bool,

    #[pyo3(get)]
    pub wrap_ids: Vec<String>,
}
