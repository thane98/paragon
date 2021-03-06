use super::{references::ReadReferences, Field, MultiNode, Stores, TextData, Types, UINode};
use crate::texture::Texture;
use anyhow::Context;
use mila::LayeredFilesystem;
use pyo3::exceptions::Exception;
use pyo3::prelude::*;
use std::collections::{HashMap, HashSet};
use std::path::PathBuf;
use std::str::FromStr;

#[pyclass]
pub struct GameData {
    fs: LayeredFilesystem,
    types: Types,
    stores: Stores,
    text_data: TextData,
    nodes: HashMap<String, UINode>,
    tables: HashMap<String, (u64, String)>,
}

impl GameData {
    fn load_impl(
        output_path: String,
        rom_path: String,
        game: String,
        language: String,
        config_root: String,
    ) -> anyhow::Result<Self> {
        // Create the filesystem.
        let game = mila::Game::from_str(&game)?;
        let language = mila::Language::from_str(&language)?;
        let layers = vec![rom_path, output_path];
        let fs = mila::LayeredFilesystem::new(layers, language, game)?;

        // Load text data.
        let mut text_data_path = PathBuf::new();
        text_data_path.push(config_root.clone());
        text_data_path.push("Text.yml");
        let text_data = TextData::load(&fs, &text_data_path)
            .context("Failed to load text data definitions.")?;

        // Load type definitions.
        let mut types_path = PathBuf::new();
        types_path.push(config_root.clone());
        types_path.push("Types");
        let types = Types::load(&types_path).context("Failed to load type definitions.")?;

        let mut stores_path = PathBuf::new();
        stores_path.push(config_root.clone());
        stores_path.push("Stores");
        let stores = Stores::load(&stores_path).context("Failed to load store definitions.")?;

        Ok(GameData {
            fs,
            types,
            stores,
            text_data,
            nodes: HashMap::new(),
            tables: HashMap::new(),
        })
    }

    fn read_impl(&mut self) -> anyhow::Result<()> {
        let mut references = ReadReferences::new();
        let output = self
            .stores
            .read(&mut self.types, &mut references, &self.fs)
            .context("Failed to read data from stores.")?;
        self.text_data
            .read(&self.fs)
            .context("Failed to read text data.")?;

        self.nodes.clear();
        for node in output.nodes.into_iter() {
            self.nodes.insert(node.id.clone(), node);
        }
        self.tables = output.tables;

        references.resolve(&self.tables, &mut self.types).context(
            "Failed to resolve references. This may be caused by missing core game data.",
        )?;
        Ok(())
    }

    pub fn write_impl(&self) -> anyhow::Result<()> {
        self.text_data
            .save(&self.fs)
            .context("Failed to write text data.")?;
        self.stores
            .write(&self.types, &self.tables, &self.fs)
            .context("Failed to write store data.")?;
        Ok(())
    }
}

#[pymethods]
impl GameData {
    #[staticmethod]
    pub fn load(
        output_path: String,
        rom_path: String,
        game: String,
        language: String,
        config_root: String,
    ) -> PyResult<Self> {
        match GameData::load_impl(output_path, rom_path, game, language, config_root) {
            Ok(gd) => Ok(gd),
            Err(err) => Err(Exception::py_err(format!("{:?}", err))),
        }
    }

    pub fn read(&mut self) -> PyResult<()> {
        match self.read_impl() {
            Ok(gd) => Ok(gd),
            Err(err) => Err(Exception::py_err(format!("{:?}", err))),
        }
    }

    pub fn write(&self) -> PyResult<()> {
        match self.write_impl() {
            Ok(gd) => Ok(gd),
            Err(err) => Err(Exception::py_err(format!("{:?}", err))),
        }
    }

    pub fn dirty_files(&self) -> HashSet<String> {
        let store_files = self.stores.dirty_files();
        let text_files = self.text_data.dirty_files();
        let mut res = HashSet::new();
        res.extend(store_files);
        res.extend(text_files);
        res
    }

    pub fn file_exists(&self, path_in_rom: &str, localized: bool) -> PyResult<bool> {
        match self.fs.file_exists(path_in_rom, localized) {
            Ok(b) => Ok(b),
            Err(err) => Err(Exception::py_err(format!("{:?}", err))),
        }
    }

    pub fn has_message(&self, path: &str, localized: bool, key: &str) -> bool {
        self.text_data.has_message(path, localized, key)
    }

    pub fn message(&self, path: &str, localized: bool, key: &str) -> Option<String> {
        self.text_data.message(path, localized, key)
    }

    pub fn has_text_data(&self, path: &str, localized: bool) -> PyResult<bool> {
        match self.text_data.archive_is_open(path, localized) {
            Ok(v) => Ok(v),
            Err(err) => Err(Exception::py_err(format!("{:?}", err))),
        }
    }

    pub fn new_text_data(&mut self, path: &str, localized: bool) -> PyResult<()> {
        match self.text_data.new_archive(path, localized) {
            Ok(_) => Ok(()),
            Err(err) => Err(Exception::py_err(format!("{:?}", err))),
        }
    }

    pub fn open_text_data(&mut self, path: String, localized: bool) -> PyResult<()> {
        match self.text_data.open_archive(&self.fs, &path, localized) {
            Ok(_) => Ok(()),
            Err(err) => Err(Exception::py_err(format!("{:?}", err))),
        }
    }

    pub fn enumerate_messages(&self, path: &str, localized: bool) -> Option<Vec<String>> {
        self.text_data.enumerate_messages(path, localized)
    }

    pub fn enumerate_text_archives(&self) -> PyResult<Vec<String>> {
        match self.text_data.enumerate_archives(&self.fs) {
            Ok(v) => Ok(v),
            Err(err) => Err(Exception::py_err(format!("{:?}", err))),
        }
    }

    pub fn set_message(
        &mut self,
        path: &str,
        localized: bool,
        key: &str,
        value: Option<String>,
    ) -> PyResult<()> {
        match self.text_data.set_message(path, localized, key, value) {
            Ok(_) => Ok(()),
            Err(err) => Err(Exception::py_err(format!("{:?}", err))),
        }
    }

    pub fn type_metadata(&self, py: Python, typename: &str) -> PyResult<Option<PyObject>> {
        self.types.type_metadata(py, typename)
    }

    pub fn field_metadata(&self, py: Python, typename: &str) -> PyResult<Option<PyObject>> {
        self.types.field_metadata(py, typename)
    }

    pub fn icon_category(&self, rid: u64) -> Option<String> {
        self.types.icon_category(rid)
    }

    pub fn copy(&mut self, source: u64, destination: u64, fields: Vec<String>) -> PyResult<()> {
        if source == destination {
            return Ok(());
        }
        match self.types.copy(source, destination, &fields) {
            Ok(_) => Ok(()),
            Err(err) => Err(Exception::py_err(format!("{:?}", err))),
        }
    }

    pub fn store_is_dirty(&self, store_id: &str) -> bool {
        self.stores.is_dirty(store_id)
    }

    pub fn set_store_dirty(&mut self, store_id: &str, dirty: bool) -> PyResult<()> {
        match self.stores.set_dirty(store_id, dirty) {
            Ok(_) => Ok(()),
            Err(err) => Err(Exception::py_err(format!("{:?}", err))),
        }
    }

    pub fn multi_open(&mut self, multi_id: &str, key: String) -> PyResult<u64> {
        let mut refs = ReadReferences::new();
        match self
            .stores
            .multi_open(&mut self.types, &mut refs, &self.fs, multi_id, key)
        {
            Ok(rid) => match refs.resolve(&self.tables, &mut self.types) {
                Ok(_) => Ok(rid),
                Err(err) => Err(Exception::py_err(format!("{:?}", err))),
            },
            Err(err) => Err(Exception::py_err(format!("{:?}", err))),
        }
    }

    pub fn multi_duplicate(
        &mut self,
        multi_id: &str,
        source: String,
        destination: String,
    ) -> PyResult<u64> {
        let mut refs = ReadReferences::new();
        match self.stores.multi_duplicate(
            &mut self.types,
            &mut refs,
            &self.fs,
            multi_id,
            source,
            destination,
        ) {
            Ok(rid) => match refs.resolve(&self.tables, &mut self.types) {
                Ok(_) => Ok(rid),
                Err(err) => Err(Exception::py_err(format!("{:?}", err))),
            },
            Err(err) => Err(Exception::py_err(format!("{:?}", err))),
        }
    }

    pub fn multi_set_dirty(&mut self, multi_id: &str, key: &str, dirty: bool) -> PyResult<()> {
        match self.stores.multi_set_dirty(multi_id, key, dirty) {
            Ok(_) => Ok(()),
            Err(err) => Err(Exception::py_err(format!("{:?}", err))),
        }
    }

    pub fn multi_keys(&self, multi_id: &str) -> PyResult<Vec<String>> {
        match self.stores.multi_keys(multi_id, &self.fs) {
            Ok(k) => Ok(k),
            Err(err) => Err(Exception::py_err(format!("{:?}", err))),
        }
    }

    pub fn read_file(&self, path: &str) -> PyResult<Vec<u8>> {
        match self.fs.read(path, false) {
            Ok(b) => Ok(b),
            Err(e) => Err(Exception::py_err(format!(
                "Failed to read file {}, error {}",
                path, e
            ))),
        }
    }

    pub fn read_bch_textures(&self, path: String) -> PyResult<HashMap<String, Texture>> {
        match self.fs.read_bch_textures(&path, false) {
            Ok(t) => Ok(t
                .into_iter()
                .map(|(k, v)| -> (String, Texture) { (k, v.into()) })
                .collect()),
            Err(err) => Err(Exception::py_err(format!("{:?}", err))),
        }
    }

    pub fn read_cgfx_textures(&self, path: String) -> PyResult<HashMap<String, Texture>> {
        match self.fs.read_cgfx_textures(&path, false) {
            Ok(t) => Ok(t
                .into_iter()
                .map(|(k, v)| -> (String, Texture) { (k, v.into()) })
                .collect()),
            Err(err) => Err(Exception::py_err(format!("{:?}", err))),
        }
    }

    pub fn read_ctpk_textures(&self, path: String) -> PyResult<HashMap<String, Texture>> {
        match self.fs.read_ctpk_textures(&path, false) {
            Ok(t) => Ok(t
                .into_iter()
                .map(|(k, v)| -> (String, Texture) { (k, v.into()) })
                .collect()),
            Err(err) => Err(Exception::py_err(format!("{:?}", err))),
        }
    }

    pub fn read_arc(&self, path: String) -> PyResult<HashMap<String, Vec<u8>>> {
        match self.fs.read_arc(&path, false) {
            Ok(a) => Ok(a),
            Err(err) => Err(Exception::py_err(format!("{:?}", err))),
        }
    }

    pub fn nodes(&self) -> Vec<UINode> {
        self.nodes.values().map(|n| n.clone()).collect()
    }

    pub fn multis(&self) -> Vec<MultiNode> {
        self.stores.multi_nodes()
    }

    pub fn table(&self, table: &str) -> Option<(u64, String)> {
        match self.tables.get(table) {
            Some(t) => Some(t.clone()),
            None => None,
        }
    }

    pub fn key_to_rid(&self, table: &str, key: &str) -> Option<u64> {
        match self.table(table) {
            Some((rid, id)) => self.list_key_to_rid(rid, &id, key),
            None => None,
        }
    }

    pub fn list_key_to_rid(&self, rid: u64, field_id: &str, key: &str) -> Option<u64> {
        match self.types.field(rid, field_id) {
            Some(f) => match f {
                Field::List(l) => l.rid_from_key(key, &self.types),
                _ => None,
            },
            None => None,
        }
    }

    pub fn key(&self, rid: u64) -> Option<String> {
        self.types.key(rid)
    }

    pub fn display(&self, rid: u64) -> Option<String> {
        self.types.display(&self.text_data, rid)
    }

    pub fn new_instance(&mut self, typename: &str) -> Option<u64> {
        self.types.instantiate_and_register(typename)
    }

    pub fn delete_instance(&mut self, rid: u64) -> PyResult<()> {
        match self.types.delete_instance(rid) {
            Ok(_) => Ok(()),
            Err(err) => Err(Exception::py_err(format!("{:?}", err))),
        }
    }

    pub fn type_of(&self, rid: u64) -> Option<String> {
        self.types.type_of(rid)
    }

    pub fn items(&self, rid: u64, id: &str) -> Option<Vec<u64>> {
        self.types.items(rid, id)
    }

    pub fn stored_type(&self, rid: u64, id: &str) -> Option<String> {
        self.types.stored_type(rid, id)
    }

    pub fn range(&self, rid: u64, id: &str) -> Option<(i64, i64)> {
        self.types.range(rid, id)
    }

    pub fn length(&self, rid: u64, id: &str) -> Option<usize> {
        self.types.length(rid, id)
    }

    pub fn string(&self, rid: u64, id: &str) -> Option<String> {
        self.types.string(rid, id)
    }

    pub fn list_index_of(&self, list_rid: u64, id: &str, rid: u64) -> Option<usize> {
        match self.types.field(list_rid, id) {
            Some(f) => match f {
                Field::List(l) => l.index_from_rid(rid),
                _ => None,
            },
            None => None,
        }
    }

    pub fn list_size(&self, rid: u64, id: &str) -> PyResult<usize> {
        match self.types.list_size(rid, id) {
            Ok(size) => Ok(size),
            Err(err) => Err(Exception::py_err(format!("{:?}", err))),
        }
    }

    pub fn list_get(&self, rid: u64, id: &str, index: usize) -> PyResult<u64> {
        match self.types.list_get(rid, id, index) {
            Ok(rid) => Ok(rid),
            Err(err) => Err(Exception::py_err(format!("{:?}", err))),
        }
    }

    pub fn list_insert(&mut self, rid: u64, id: &str, index: usize) -> PyResult<u64> {
        match self.types.list_insert(rid, id, index) {
            Ok(rid) => Ok(rid),
            Err(err) => Err(Exception::py_err(format!("{:?}", err))),
        }
    }

    pub fn list_insert_existing(
        &mut self,
        list_rid: u64,
        id: &str,
        rid: u64,
        index: usize,
    ) -> PyResult<()> {
        match self.types.list_insert_existing(list_rid, id, rid, index) {
            Ok(rid) => Ok(rid),
            Err(err) => Err(Exception::py_err(format!("{:?}", err))),
        }
    }

    pub fn list_add(&mut self, rid: u64, id: &str) -> PyResult<u64> {
        match self.types.list_add(rid, id) {
            Ok(rid) => Ok(rid),
            Err(err) => Err(Exception::py_err(format!("{:?}", err))),
        }
    }

    pub fn list_remove(&mut self, rid: u64, id: &str, index: usize) -> PyResult<()> {
        match self.types.list_remove(rid, id, index) {
            Ok(_) => Ok(()),
            Err(err) => Err(Exception::py_err(format!("{:?}", err))),
        }
    }

    pub fn list_swap(&mut self, rid: u64, id: &str, a: usize, b: usize) -> PyResult<()> {
        match self.types.list_swap(rid, id, a, b) {
            Ok(_) => Ok(()),
            Err(err) => Err(Exception::py_err(format!("{:?}", err))),
        }
    }

    pub fn set_string(&mut self, rid: u64, id: &str, value: Option<String>) -> PyResult<()> {
        match self.types.set_string(rid, id, value) {
            Ok(_) => Ok(()),
            Err(err) => Err(Exception::py_err(format!("{:?}", err))),
        }
    }

    pub fn int(&self, rid: u64, id: &str) -> Option<i64> {
        self.types.int(rid, id)
    }

    pub fn set_int(&mut self, rid: u64, id: &str, value: i64) -> PyResult<()> {
        match self.types.set_int(rid, id, value) {
            Ok(_) => Ok(()),
            Err(err) => Err(Exception::py_err(format!("{:?}", err))),
        }
    }

    pub fn float(&self, rid: u64, id: &str) -> Option<f32> {
        self.types.float(rid, id)
    }

    pub fn set_float(&mut self, rid: u64, id: &str, value: f32) -> PyResult<()> {
        match self.types.set_float(rid, id, value) {
            Ok(_) => Ok(()),
            Err(err) => Err(Exception::py_err(format!("{:?}", err))),
        }
    }

    pub fn bool(&self, rid: u64, id: &str) -> Option<bool> {
        self.types.bool(rid, id)
    }

    pub fn set_bool(&mut self, rid: u64, id: &str, value: bool) -> PyResult<()> {
        match self.types.set_bool(rid, id, value) {
            Ok(_) => Ok(()),
            Err(err) => Err(Exception::py_err(format!("{:?}", err))),
        }
    }

    pub fn bytes(&self, rid: u64, id: &str) -> Option<Vec<u8>> {
        self.types.bytes(rid, id)
    }

    pub fn get_byte(&self, rid: u64, id: &str, index: usize) -> PyResult<u8> {
        match self.types.get_byte(rid, id, index) {
            Ok(v) => Ok(v),
            Err(err) => Err(Exception::py_err(format!("{:?}", err))),
        }
    }

    pub fn set_bytes(&mut self, rid: u64, id: &str, value: Vec<u8>) -> PyResult<()> {
        match self.types.set_bytes(rid, id, value) {
            Ok(_) => Ok(()),
            Err(err) => Err(Exception::py_err(format!("{:?}", err))),
        }
    }

    pub fn set_byte(&mut self, rid: u64, id: &str, index: usize, value: u8) -> PyResult<()> {
        match self.types.set_byte(rid, id, index, value) {
            Ok(_) => Ok(()),
            Err(err) => Err(Exception::py_err(format!("{:?}", err))),
        }
    }

    pub fn rid(&self, rid: u64, id: &str) -> Option<u64> {
        self.types.rid(rid, id)
    }

    pub fn set_rid(&mut self, rid: u64, id: &str, value: Option<u64>) -> PyResult<()> {
        match self.types.set_rid(rid, id, value) {
            Ok(_) => Ok(()),
            Err(err) => Err(Exception::py_err(format!("{:?}", err))),
        }
    }
}
