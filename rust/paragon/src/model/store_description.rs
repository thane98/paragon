use pyo3::prelude::*;

use super::id::StoreNumber;

#[pyclass]
pub struct StoreDescription {
    #[pyo3(get)]
    pub store_number: StoreNumber,

    #[pyo3(get)]
    pub path: String,

    #[pyo3(get)]
    pub store_type: String,

    #[pyo3(get)]
    pub dirty: bool,
}
