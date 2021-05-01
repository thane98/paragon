mod data;
mod texture;

pub use data::GameData;

use pyo3::exceptions::Exception;
use pyo3::prelude::*;
use pyo3::types::PyBytes;
use pyo3::wrap_pyfunction;

#[pyfunction]
pub fn compress_lz13(py: Python, contents: &[u8]) -> PyResult<PyObject> {
    let format = mila::LZ13CompressionFormat {};
    match format.compress(contents) {
        Ok(b) => Ok(PyBytes::new(py, &b).to_object(py)),
        Err(err) => Err(Exception::py_err(format!("{}", err))),
    }
}

#[pyfunction]
pub fn decompress_lz13(py: Python, contents: &[u8]) -> PyResult<PyObject> {
    let format = mila::LZ13CompressionFormat {};
    match format.decompress(contents) {
        Ok(b) => Ok(PyBytes::new(py, &b).to_object(py)),
        Err(err) => Err(Exception::py_err(format!("{}", err))),
    }
}

#[pyfunction]
pub fn read_bch(contents: &[u8]) -> PyResult<Vec<texture::Texture>> {
    match mila::bch::read(contents) {
        Ok(textures) => Ok(textures
            .into_iter()
            .map(|tex| tex.into())
            .collect::<Vec<texture::Texture>>()),
        Err(err) => Err(Exception::py_err(format!("{}", err))),
    }
}

#[pyfunction]
pub fn read_cgfx(contents: &[u8]) -> PyResult<Vec<texture::Texture>> {
    match mila::cgfx::read(contents) {
        Ok(textures) => Ok(textures
            .into_iter()
            .map(|tex| tex.into())
            .collect::<Vec<texture::Texture>>()),
        Err(err) => Err(Exception::py_err(format!("{}", err))),
    }
}

#[pyfunction]
pub fn read_ctpk(contents: &[u8]) -> PyResult<Vec<texture::Texture>> {
    match mila::ctpk::read(contents) {
        Ok(textures) => Ok(textures
            .into_iter()
            .map(|tex| tex.into())
            .collect::<Vec<texture::Texture>>()),
        Err(err) => Err(Exception::py_err(format!("{}", err))),
    }
}

#[pyfunction]
pub fn merge_images_and_increase_alpha(image1: &[u8], image2: &[u8]) -> PyObject {
    let mut result: Vec<u8> = Vec::new();
    result.reserve(image1.len());
    for i in (0..image1.len()).step_by(4) {
        if image1[i + 3] > image2[i + 3] && image1[i + 3] == 0xFF && image2[i + 3] == 0x88 {
            result.extend_from_slice(&image2[i..i + 3]);
        } else if image1[i + 3] > image2[i + 3] && image1[i + 3] == 0xEE && image2[i + 3] != 0x0 {
            result.extend_from_slice(&image2[i..i + 3]);
        } else if image1[i + 3] > image2[i + 3] {
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
pub fn increase_alpha(image: &[u8]) -> PyObject {
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

// Used by the testing script to make Awakening's GameData suitable for
// testing. The modules are expected to produce some minor differences
// which can be safely ignored, so we strip those out here.
// This is included in the Rust piece because the archive is not directly
// accessible from Python.
#[pyfunction]
pub fn load_awakening_gamedata_for_tests(py: Python, path: &str) -> PyResult<PyObject> {
    let raw = std::fs::read(path)?;
    let raw = mila::LZ13CompressionFormat {}
        .decompress(&raw)
        .map_err(|_| Exception::py_err("Failed to decompress input."))?;
    let mut archive = mila::BinArchive::from_bytes(&raw)
        .map_err(|_| Exception::py_err("Failed to parse BinArchive."))?;
    let item_count_addr = archive
        .find_label_address("ItemDataNum")
        .ok_or(Exception::py_err("Could not find ItemDataNum label."))?;
    let refine_addr = archive
        .find_label_address("ItemRefineData")
        .ok_or(Exception::py_err("Could not find ItemRefineData label."))?;
    let refine_count_addr = archive
        .find_label_address("ItemRefineDataNum")
        .ok_or(Exception::py_err("Could not find ItemRefineDataNum label."))?;
    if refine_addr == item_count_addr + 4 {
        archive.allocate(refine_count_addr, 4, false).unwrap();
        archive
            .write_labels(refine_count_addr, vec!["ItemDataNum".to_string()])
            .unwrap();
        archive.write_u32(refine_count_addr, 0xCA).unwrap();
        archive
            .write_labels(refine_count_addr + 4, vec!["ItemRefineDataNum".to_string()])
            .unwrap();
        archive.write_u32(refine_count_addr + 4, 0x96).unwrap();
    } else if refine_count_addr == item_count_addr + 4 {
        archive.allocate(refine_addr, 4, false).unwrap();
        archive
            .write_labels(refine_addr, vec!["ItemDataNum".to_string()])
            .unwrap();
        archive.write_u32(refine_addr, 0xCA).unwrap();
        archive
            .write_labels(
                refine_addr + 4,
                vec!["ItemRefineData".to_string(), "IID_REFINE1".to_string()],
            )
            .unwrap();
    }
    let result = archive.serialize().unwrap();
    Ok(PyBytes::new(py, &result).to_object(py))
}

#[pyfunction]
pub fn compare_fe14_gamedatas(
    original: &str,
    new: &str,
    regions: Vec<(usize, usize, usize)>,
) -> PyResult<()> {
    let raw_original = std::fs::read(original)?;
    let raw_new = std::fs::read(new)?;
    let raw_original = mila::LZ13CompressionFormat {}
        .decompress(&raw_original)
        .map_err(|_| Exception::py_err("Failed to decompress input."))?;
    let raw_new = mila::LZ13CompressionFormat {}
        .decompress(&raw_new)
        .map_err(|_| Exception::py_err("Failed to decompress input."))?;
    let original_archive = mila::BinArchive::from_bytes(&raw_original)
        .map_err(|_| Exception::py_err("Failed to parse BinArchive."))?;
    let new_archive = mila::BinArchive::from_bytes(&raw_new)
        .map_err(|_| Exception::py_err("Failed to parse BinArchive."))?;
    for (original_start, new_start, length) in regions {
        if let Err(e) =
            original_archive.assert_equal_regions(&new_archive, original_start, new_start, length)
        {
            return Err(Exception::py_err(format!("{}", e)));
        }
    }
    Ok(())
}

#[pyfunction]
pub fn disassemble_cmb(raw: &[u8]) -> PyResult<String> {
    match exalt::disassemble_v3ds(raw) {
        Ok(functions) => match serde_yaml::to_string(&functions) {
            Ok(script) => Ok(script),
            Err(err) => Err(Exception::py_err(format!("{}", err))),
        },
        Err(err) => Err(Exception::py_err(format!("{:?}", err))),
    }
}

#[pyfunction]
pub fn assemble_cmb(script_name: &str, raw: &str) -> PyResult<Vec<u8>> {
    let functions: Vec<exalt::V3dsFunctionData> =
        serde_yaml::from_str(raw).map_err(|err| Exception::py_err(format!("{}", err)))?;
    let code = exalt::gen_v3ds_code(script_name, &functions)
        .map_err(|err| Exception::py_err(format!("{:?}", err)))?;
    Ok(code)
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
    m.add_wrapped(wrap_pyfunction!(load_awakening_gamedata_for_tests))?;
    m.add_wrapped(wrap_pyfunction!(compare_fe14_gamedatas))?;
    m.add_wrapped(wrap_pyfunction!(disassemble_cmb))?;
    m.add_wrapped(wrap_pyfunction!(assemble_cmb))?;
    Ok(())
}
