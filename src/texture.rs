use pyo3::prelude::*;

#[pyclass]
pub struct Texture {
    #[pyo3(get)]
    pub filename: String,

    #[pyo3(get)]
    pub height: usize,

    #[pyo3(get)]
    pub width: usize,

    pub pixel_data: Vec<u8>,
}

#[pymethods]
impl Texture {
    #[getter]
    pub fn pixel_data(&self) -> &[u8] {
        &self.pixel_data
    }
}

impl From<mila::Texture> for Texture {
    fn from(tex: mila::Texture) -> Self {
        Texture {
            filename: tex.filename,
            height: tex.height,
            width: tex.width,
            pixel_data: tex.pixel_data,
        }
    }
}
