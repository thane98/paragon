pub mod bin_archive;
pub mod lz13;
pub mod hack_file_system;
pub mod arc;    // Might integrate to bch since doesn't look like anything else uses arc files
pub mod bch;
pub mod texture_compression;

use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use crate::hack_file_system::*;
use crate::bin_archive::BinArchive;

#[pyfunction]
fn create_bin_archive() -> PyResult<BinArchive> {
    Ok(BinArchive::new())
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
    Ok(())
}
