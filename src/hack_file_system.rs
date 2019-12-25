use pyo3::prelude::*;
use pyo3::types::PyAny;
use std::io::{Read, Write, Error, ErrorKind};
use std::fs::{OpenOptions, create_dir_all};
use std::path::Path;
use std::thread;
use crate::lz13::*;
use crate::bin_archive::BinArchive;

enum Language {
    EnglishNA = 0,
    EnglishEU = 1,
    Japanese = 2,
    Spanish = 3,
    French = 4,
    German = 5,
    Italian = 6
}

fn get_parent_as_string(path: &Path) -> PyResult<String> {
    let parent = path.parent();
    match parent {
        Some(value) => Ok(value.to_str().unwrap().to_string()),
        None => Err(PyErr::from(Error::new(ErrorKind::NotFound, "Path has no parent")))
    }
}

fn get_file_name(path: &Path) -> PyResult<String> {
    let file_name_opt = path.file_name();
    match file_name_opt {
        Some(value) => Ok(value.to_str().unwrap().to_string()),
        None => Err(PyErr::from(Error::new(ErrorKind::NotFound, "Path has no file name")))
    }
}

fn u8_to_language(raw_language: u8) -> Language {
    match raw_language {
        0 => Language::EnglishNA,
        1 => Language::EnglishEU,
        2 => Language::Japanese,
        3 => Language::Spanish,
        4 => Language::French,
        5 => Language::German,
        6 => Language::Italian,
        _ => Language::EnglishNA
    }
}


pub trait HackFileSystem {
    fn source_path(&self) -> PyResult<String>;
    fn dest_path(&self) -> PyResult<String>;
    fn localized_path(&self, unlocalized_path: &str) -> PyResult<String>;
    
    fn path_exists(&self, path: &str) -> PyResult<bool> {
        let mut path_in_source = self.source_path().unwrap();
        path_in_source.push_str(path);
        let mut path_in_dest = self.dest_path().unwrap();
        path_in_dest.push_str(path);
        if Path::new(&path_in_dest).exists() {
            return Ok(true);
        }
        else if Path::new(&path_in_source).exists() {
            return Ok(true);
        }
        Ok(false)
    }

    fn open_file(&self, path: &str) -> PyResult<Vec<u8>> {
        // If the file exists in destionation, use that version.
        // Otherwise, pull from the source.
        let mut path_in_source = self.source_path().unwrap();
        path_in_source.push_str(path);
        let mut path_in_dest = self.dest_path().unwrap();
        path_in_dest.push_str(path);
        let full_path = if Path::new(&path_in_dest).exists() {
            path_in_dest
        }
        else {
            path_in_source
        };

        // Read the contents of the file.
        let mut file = OpenOptions::new()
            .read(true)
            .open(&full_path)?;
        let mut file_contents: Vec<u8> = Vec::new();
        file.read_to_end(&mut file_contents)?;

        // If the path ends in .lz, decompress before returning.
        if full_path.ends_with(".lz") {
            let decompressed_contents = decompress_lz13(&file_contents)?;
            Ok(decompressed_contents)
        }
        else {
            Ok(file_contents)
        }
    }

    fn open_archive(&self, path: &str) -> PyResult<PyObject> {
        let file_contents = self.open_file(path)?;
        let archive = BinArchive::from_raw_archive(&file_contents)?;
        let gil = GILGuard::acquire();
        let py = gil.python();
        let obj = archive.into_py(py);
        Ok(obj)
    }

    fn write_file(&self, path: &str, contents: Vec<u8>) -> PyResult<()> {
        let mut path_in_dest = self.dest_path().unwrap();
        path_in_dest.push_str(path);
        let full_path = Path::new(&path_in_dest);
        let parent = get_parent_as_string(&full_path).unwrap();
        thread::spawn(move || {
            create_dir_all(Path::new(&parent)).unwrap();
            let mut file = OpenOptions::new()
                .write(true)
                .create(true)
                .truncate(true)
                .open(&path_in_dest).unwrap();
            if path_in_dest.ends_with(".lz") {
                let compressed_contents = compress_lz13(&contents);
                file.write_all(&compressed_contents).unwrap();
            }
            else {
                file.write_all(&contents).unwrap();
            }
        });
        
        Ok(())
    }

    fn write_archive(&self, path: &str, archive: &PyAny) -> PyResult<()> {
        let archive: &mut BinArchive = FromPyObject::extract(archive)?;
        let serialized_contents = archive.serialize()?;
        self.write_file(path, serialized_contents)?;
        Ok(())
    }

    fn open_localized_archive(&self, path: &str) -> PyResult<PyObject> { 
        let localized_path = self.localized_path(path)?;
        self.open_archive(&localized_path)
    }

    fn write_localized_archive(&self, path: &str, archive: &PyAny) -> PyResult<()> {
        let localized_path = self.localized_path(path)?;
        self.write_archive(&localized_path, archive)
    }
}

#[pyclass]
pub struct FE13FileSystem {
    source_path: String,
    dest_path: String,
    language: Language
}

impl FE13FileSystem {
    pub fn new(source_path: &str, dest_path: &str, raw_language: u8) -> Self {
        let language = u8_to_language(raw_language);
        FE13FileSystem {
            source_path: source_path.to_string(),
            dest_path: dest_path.to_string(),
            language
        }
    }
}

impl HackFileSystem for FE13FileSystem {
    fn source_path(&self) -> PyResult<String> {
        Ok(self.source_path.clone())
    }

    fn dest_path(&self) -> PyResult<String> {
        Ok(self.dest_path.clone())
    }

    fn localized_path(&self, unlocalized_path: &str) -> PyResult<String> {
        let mut result = String::new();
        let path_info = Path::new(unlocalized_path);
        let dir_name = get_parent_as_string(path_info)?;
        let file_name = get_file_name(path_info)?;
        result.push_str(&dir_name);
        match self.language {
            Language::EnglishNA => result.push_str("/E/"),
            Language::EnglishEU => result.push_str("/U/"),
            Language::Japanese => {},
            Language::Spanish => result.push_str("/S/"),
            Language::French => result.push_str("/F/"),
            Language::German => result.push_str("/G/"),
            Language::Italian => result.push_str("/I/"),
        }
        result.push_str(&file_name);
        Ok(result)
    }
}

// PyO3 doesn't support pymethods for traits currently.
// As a workaround, we'll expose wrappers.
#[pymethods]
impl FE13FileSystem {
    pub fn open(&self, path: &str) -> PyResult<Vec<u8>> {
        self.open_file(path)
    }

    pub fn get_source_path(&self) -> PyResult<String> {
        self.source_path()
    }

    pub fn get_dest_path(&self) -> PyResult<String> {
        self.dest_path()
    }

    pub fn open_bin(&self, path: &str) -> PyResult<PyObject> {
        self.open_archive(path)
    }

    pub fn open_localized_bin(&self, path: &str) -> PyResult<PyObject> {
        self.open_localized_archive(path)
    }

    fn write_bin(&self, path: &str, archive: &PyAny) -> PyResult<()> {
        self.write_archive(path, archive)
    }

    fn write_localized_bin(&self, path: &str, archive: &PyAny) -> PyResult<()> {
        self.write_localized_archive(path, archive)
    }
    
    pub fn exists(&self, path: &str) -> PyResult<bool> {
        self.path_exists(path)
    }
}

#[pyclass]
pub struct FE14FileSystem {
    source_path: String,
    dest_path: String,
    language: Language
}

impl FE14FileSystem {
    pub fn new(source_path: &str, dest_path: &str, raw_language: u8) -> Self {
        let language = u8_to_language(raw_language);
        FE14FileSystem {
            source_path: source_path.to_string(),
            dest_path: dest_path.to_string(),
            language
        }
    }
}

impl HackFileSystem for FE14FileSystem {
    fn source_path(&self) -> PyResult<String> {
        Ok(self.source_path.clone())
    }

    fn dest_path(&self) -> PyResult<String> {
        Ok(self.dest_path.clone())
    }

    fn localized_path(&self, unlocalized_path: &str) -> PyResult<String> {
        let mut result = String::new();
        let path_info = Path::new(unlocalized_path);
        let dir_name = get_parent_as_string(path_info)?;
        let file_name = get_file_name(path_info)?;
        result.push_str(&dir_name);
        match self.language {
            Language::EnglishNA => result.push_str("/@E/"),
            Language::EnglishEU => result.push_str("/@U/"),
            Language::Japanese => {},
            Language::Spanish => result.push_str("/@S/"),
            Language::French => result.push_str("/@F/"),
            Language::German => result.push_str("/@G/"),
            Language::Italian => result.push_str("/@I/"),
        }
        result.push_str(&file_name);
        Ok(result)
    }
}

// PyO3 doesn't support pymethods for traits currently.
// As a workaround, we'll expose wrappers.
#[pymethods]
impl FE14FileSystem {
    pub fn open(&self, path: &str) -> PyResult<Vec<u8>> {
        self.open_file(path)
    }

    pub fn get_source_path(&self) -> PyResult<String> {
        self.source_path()
    }

    pub fn get_dest_path(&self) -> PyResult<String> {
        self.dest_path()
    }

    pub fn open_bin(&self, path: &str) -> PyResult<PyObject> {
        self.open_archive(path)
    }

    pub fn open_localized_bin(&self, path: &str) -> PyResult<PyObject> {
        self.open_localized_archive(path)
    }

    fn write_bin(&self, path: &str, archive: &PyAny) -> PyResult<()> {
        self.write_archive(path, archive)
    }

    fn write_localized_bin(&self, path: &str, archive: &PyAny) -> PyResult<()> {
        self.write_localized_archive(path, archive)
    }
    
    pub fn exists(&self, path: &str) -> PyResult<bool> {
        self.path_exists(path)
    }
}

#[pyclass]
pub struct FE15FileSystem {
    source_path: String,
    dest_path: String,
    language: Language
}

impl FE15FileSystem {
    pub fn new(source_path: &str, dest_path: &str, raw_language: u8) -> Self {
        let language = u8_to_language(raw_language);
        FE15FileSystem {
            source_path: source_path.to_string(),
            dest_path: dest_path.to_string(),
            language
        }
    }
}

impl HackFileSystem for FE15FileSystem {
    fn open_localized_archive(&self, path: &str) -> PyResult<PyObject> { 
        let localized_path = self.localized_path(path)?;
        self.open_archive(&localized_path)
    }

    fn write_localized_archive(&self, path: &str, archive: &PyAny) -> PyResult<()> {
        let localized_path = self.localized_path(path)?;
        self.write_archive(&localized_path, archive)
    }
    
    fn source_path(&self) -> PyResult<String> {
        Ok(self.source_path.clone())
    }

    fn dest_path(&self) -> PyResult<String> {
        Ok(self.dest_path.clone())
    }

    fn localized_path(&self, unlocalized_path: &str) -> PyResult<String> {
        let mut result = String::new();
        let path_info = Path::new(unlocalized_path);
        let dir_name = get_parent_as_string(path_info)?;
        let file_name = get_file_name(path_info)?;
        result.push_str(&dir_name);
        match self.language {
            Language::EnglishNA => result.push_str("/@NOA_EN/"),
            Language::EnglishEU => result.push_str("/@NOE_EN/"),
            Language::Japanese => {},
            Language::Spanish => result.push_str("/@NOE_SP/"),
            Language::French => result.push_str("/@NOE_FR/"),
            Language::German => result.push_str("/@NOE_GE/"),
            Language::Italian => result.push_str("/@NOE_IT/"),
        }
        result.push_str(&file_name);
        Ok(result)
    }
}

// PyO3 doesn't support pymethods for traits currently.
// As a workaround, we'll expose wrappers.
#[pymethods]
impl FE15FileSystem {
    pub fn open(&self, path: &str) -> PyResult<Vec<u8>> {
        self.open_file(path)
    }

    pub fn get_source_path(&self) -> PyResult<String> {
        self.source_path()
    }

    pub fn get_dest_path(&self) -> PyResult<String> {
        self.dest_path()
    }

    pub fn open_bin(&self, path: &str) -> PyResult<PyObject> {
        self.open_archive(path)
    }

    pub fn open_localized_bin(&self, path: &str) -> PyResult<PyObject> {
        self.open_localized_archive(path)
    }

    fn write_bin(&self, path: &str, archive: &PyAny) -> PyResult<()> {
        self.write_archive(path, archive)
    }

    fn write_localized_bin(&self, path: &str, archive: &PyAny) -> PyResult<()> {
        self.write_localized_archive(path, archive)
    }
    
    pub fn exists(&self, path: &str) -> PyResult<bool> {
        self.path_exists(path)
    }
}
