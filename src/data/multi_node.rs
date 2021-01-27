use pyo3::prelude::*;

#[pyclass]
pub struct MultiNode {
    #[pyo3(get)]
    pub id: String,

    #[pyo3(get)]
    pub name: String,

    #[pyo3(get)]
    pub typename: String,
}
