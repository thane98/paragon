pub mod bin_archive;
pub mod lz13;
pub mod arc;
pub mod bch;
pub mod hack_file_system;
pub mod etc1;
pub mod texture;
pub mod ctpk;
pub mod cgfx;

use pyo3::prelude::*;
use pyo3::{wrap_pyfunction, types::PyBytes};
use crate::hack_file_system::*;
use crate::bin_archive::BinArchive;

#[pyfunction]
fn create_bin_archive() -> PyResult<BinArchive> {
    Ok(BinArchive::new())
}

#[pyfunction]
fn merge_images_and_increase_alpha(image1: &[u8], image2: &[u8]) -> PyObject {
    let mut result: Vec<u8> = Vec::new();
    result.reserve(image1.len());
    for i in (0..image1.len()).step_by(4) {
        if image1[i + 3] > image2[i + 3] {
            result.extend_from_slice(&image1[i..i+3]);
        } else {
            result.extend_from_slice(&image2[i..i+3]);
        }
        if image1[i + 3] == 0 && image2[i + 3] == 0 {
            result.push(0);
        } else {
            result.push(0xFF);   
        }
    }

    let gil = GILGuard::acquire();
    let py = gil.python();
    PyBytes::new(py, &result).to_object(py)
}

#[pyfunction]
fn increase_alpha(image: &[u8]) -> PyObject {
    let mut result: Vec<u8> = Vec::new();
    result.reserve(image.len());
    for i in (0..image.len()).step_by(4) {
        result.extend_from_slice(&image[i..i+3]);
        if image[i + 3] == 0 {
            result.push(0);
        } else {
            result.push(0xFF);
        }
    }
    let gil = GILGuard::acquire();
    let py = gil.python();
    PyBytes::new(py, &result).to_object(py)
}

#[pymodule]
fn fefeditor2(_py: Python, m: &PyModule) -> PyResult<()> {
    #[pyfn (m, "create_fe13_file_system")]
    fn create_fe13_file_system(py: Python, source_path: &str, dest_path: &str, raw_language: u8) -> PyResult<PyObject> {
        let file_system = FE13FileSystem::new(source_path, dest_path, raw_language);
        let obj = file_system.into_py(py);
        Ok(obj)
    }

    #[pyfn (m, "create_fe14_file_system")]
    fn create_fe14_file_system(py: Python, source_path: &str, dest_path: &str, raw_language: u8) -> PyResult<PyObject> {
        let file_system = FE14FileSystem::new(source_path, dest_path, raw_language);
        let obj = file_system.into_py(py);
        Ok(obj)
    }

    #[pyfn (m, "create_fe15_file_system")]
    fn create_fe15_file_system(py: Python, source_path: &str, dest_path: &str, raw_language: u8) -> PyResult<PyObject> {
        let file_system = FE15FileSystem::new(source_path, dest_path, raw_language);
        let obj = file_system.into_py(py);
        Ok(obj)
    }

    m.add_wrapped(wrap_pyfunction!(create_bin_archive))?;
    m.add_wrapped(wrap_pyfunction!(merge_images_and_increase_alpha))?;
    m.add_wrapped(wrap_pyfunction!(increase_alpha))?;
    Ok(())
}
