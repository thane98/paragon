pub mod ctpk;
pub mod cgfx;
pub mod bch;
pub mod compression;

use pyo3::prelude::*;
use std::io::Result;

#[allow(dead_code)]
#[pyclass(module = "fefeditor2")]
pub struct Texture {
    pub filename: String,
    pub width: usize,
    pub height: usize,
    pub pixel_data: Vec<u8>,
    pub pixel_format: u32,
}

impl Texture {
    pub fn decode(&self) -> Result<Self> {
        let decoded_pixel_data =
        compression::decode_pixel_data(&self.pixel_data, self.width, self.height, self.pixel_format)?;
        Ok(Texture {
            filename: self.filename.clone(),
            width: self.width,
            height: self.height,
            pixel_data: decoded_pixel_data,
            pixel_format: self.pixel_format,
        })
    }
}

#[pymethods]
impl Texture {
    fn get_filename(&self) -> &str {
        &self.filename
    }

    fn get_width(&self) -> usize {
        self.width
    }

    fn get_height(&self) -> usize {
        self.height
    }

    fn get_pixel_data(&self) -> &[u8] {
        &self.pixel_data
    }

    fn get_pixel_format(&self) -> u32 {
        self.pixel_format
    }
}
