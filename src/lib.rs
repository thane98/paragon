mod data;
mod texture;

use pyo3::exceptions::Exception;
use pyo3::prelude::*;
use pyo3::types::PyBytes;
use pyo3::wrap_pyfunction;

#[pyfunction]
fn compress_lz13(py: Python, contents: &[u8]) -> PyResult<PyObject> {
    let format = mila::LZ13CompressionFormat {};
    match format.compress(contents) {
        Ok(b) => Ok(PyBytes::new(py, &b).to_object(py)),
        Err(err) => Err(Exception::py_err(format!("{}", err))),
    }
}

#[pyfunction]
fn decompress_lz13(py: Python, contents: &[u8]) -> PyResult<PyObject> {
    let format = mila::LZ13CompressionFormat {};
    match format.decompress(contents) {
        Ok(b) => Ok(PyBytes::new(py, &b).to_object(py)),
        Err(err) => Err(Exception::py_err(format!("{}", err))),
    }
}

#[pyfunction]
fn read_bch(contents: &[u8]) -> PyResult<Vec<texture::Texture>> {
    match mila::bch::read(contents) {
        Ok(textures) => Ok(textures
            .into_iter()
            .map(|tex| tex.into())
            .collect::<Vec<texture::Texture>>()),
        Err(err) => Err(Exception::py_err(format!("{}", err))),
    }
}

#[pyfunction]
fn read_cgfx(contents: &[u8]) -> PyResult<Vec<texture::Texture>> {
    match mila::cgfx::read(contents) {
        Ok(textures) => Ok(textures
            .into_iter()
            .map(|tex| tex.into())
            .collect::<Vec<texture::Texture>>()),
        Err(err) => Err(Exception::py_err(format!("{}", err))),
    }
}

#[pyfunction]
fn read_ctpk(contents: &[u8]) -> PyResult<Vec<texture::Texture>> {
    match mila::ctpk::read(contents) {
        Ok(textures) => Ok(textures
            .into_iter()
            .map(|tex| tex.into())
            .collect::<Vec<texture::Texture>>()),
        Err(err) => Err(Exception::py_err(format!("{}", err))),
    }
}

#[pyfunction]
fn merge_images_and_increase_alpha(image1: &[u8], image2: &[u8]) -> PyObject {
    let mut result: Vec<u8> = Vec::new();
    result.reserve(image1.len());
    for i in (0..image1.len()).step_by(4) {
        if image1[i + 3] > image2[i + 3] {
            result.extend_from_slice(&image1[i..i + 3]);
        } else {
            result.extend_from_slice(&image2[i..i + 3]);
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
        result.extend_from_slice(&image[i..i + 3]);
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
pub fn paragon(_: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<texture::Texture>()?;
    m.add_class::<data::GameData>()?;
    m.add_wrapped(wrap_pyfunction!(compress_lz13))?;
    m.add_wrapped(wrap_pyfunction!(decompress_lz13))?;
    m.add_wrapped(wrap_pyfunction!(read_bch))?;
    m.add_wrapped(wrap_pyfunction!(read_cgfx))?;
    m.add_wrapped(wrap_pyfunction!(read_ctpk))?;
    m.add_wrapped(wrap_pyfunction!(merge_images_and_increase_alpha))?;
    m.add_wrapped(wrap_pyfunction!(increase_alpha))?;
    Ok(())
}
