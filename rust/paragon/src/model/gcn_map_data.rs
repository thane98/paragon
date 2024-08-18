use pyo3::prelude::*;

#[pyclass]
#[derive(Debug, Clone)]
pub struct GcnMapData {
    #[pyo3(get)]
    pub width: usize,
    #[pyo3(get)]
    pub height: usize,
    #[pyo3(get)]
    pub margin: usize,
    pub tiles: Vec<Option<String>>,
}

#[pymethods]
impl GcnMapData {
    pub fn len(&self) -> usize {
        self.tiles.len()
    }

    pub fn get_tile(&self, index: usize) -> Option<String> {
        self.tiles.get(index).cloned().flatten()
    }
}
