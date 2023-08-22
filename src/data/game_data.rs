use std::collections::{HashMap, HashSet};
use std::path::PathBuf;
use std::str::FromStr;

use anyhow::Context;
use mila::LayeredFilesystem;
use pyo3::exceptions::PyException;
use pyo3::prelude::*;

use crate::data::{TextData, Types};
use crate::model::id::{RecordId, StoreNumber};
use crate::model::store_description::StoreDescription;
use crate::model::texture::Texture;

use crate::data::archives::Archives;
use crate::data::fields::field::Field;
use crate::data::serialization::references::ReadReferences;
use crate::data::storage::stores::Stores;
use crate::model::multi_node::MultiNode;
use crate::model::ui_node::UINode;

use super::scripts::Scripts;

#[pyclass]
pub struct GameData {
    fs: LayeredFilesystem,
    types: Types,
    stores: Stores,
    text_data: TextData,
    scripts: Scripts,
    nodes: HashMap<String, UINode>,
    tables: HashMap<String, (RecordId, String)>,
    archives: Archives,
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
        let language_enum = mila::Language::from_str(&language)?;
        let layers = vec![rom_path, output_path];
        let fs = LayeredFilesystem::new(layers, language_enum, game)?;

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
        let types =
            Types::load(&types_path, &language).context("Failed to load type definitions.")?;

        let mut stores_path = PathBuf::new();
        stores_path.push(config_root);
        stores_path.push("Stores");
        let stores = Stores::load(&stores_path).context("Failed to load store definitions.")?;

        Ok(GameData {
            fs,
            types,
            stores,
            text_data,
            scripts: Scripts::new(game),
            nodes: HashMap::new(),
            tables: HashMap::new(),
            archives: Archives::new(),
        })
    }

    fn read_impl(&mut self) -> anyhow::Result<()> {
        let mut references = ReadReferences::new();
        let output = self
            .stores
            .read(
                &mut self.types,
                &mut references,
                &mut self.archives,
                &self.fs,
            )
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

    pub fn write_impl(&mut self) -> anyhow::Result<()> {
        self.scripts
            .save(&self.fs)
            .context("Failed to write scripts.")?;
        self.text_data
            .save(&self.fs)
            .context("Failed to write text data.")?;
        self.stores
            .write(&self.types, &self.tables, &mut self.archives, &self.fs)
            .context("Failed to write store data.")?;
        self.archives
            .save(&self.fs)
            .context("Failed to write CMP archives.")?;
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
            Err(err) => Err(PyException::new_err(format!("{:?}", err))),
        }
    }

    pub fn read(&mut self) -> PyResult<()> {
        match self.read_impl() {
            Ok(gd) => Ok(gd),
            Err(err) => Err(PyException::new_err(format!("{:?}", err))),
        }
    }

    pub fn write(&mut self) -> PyResult<()> {
        match self.write_impl() {
            Ok(gd) => Ok(gd),
            Err(err) => Err(PyException::new_err(format!("{:?}", err))),
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
            Err(err) => Err(PyException::new_err(format!("{:?}", err))),
        }
    }

    pub fn list_files(
        &self,
        dir: &str,
        glob: Option<&str>,
        localized: bool,
    ) -> PyResult<Vec<String>> {
        self.fs
            .list(dir, glob, localized)
            .map_err(|err| PyException::new_err(format!("{:?}", err)))
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
            Err(err) => Err(PyException::new_err(format!("{:?}", err))),
        }
    }

    pub fn new_text_data(&mut self, path: &str, localized: bool) -> PyResult<()> {
        match self.text_data.new_archive(&self.fs, path, localized) {
            Ok(_) => Ok(()),
            Err(err) => Err(PyException::new_err(format!("{:?}", err))),
        }
    }

    pub fn open_text_data(&mut self, path: String, localized: bool) -> PyResult<()> {
        match self.text_data.open_archive(&self.fs, &path, localized) {
            Ok(_) => Ok(()),
            Err(err) => Err(PyException::new_err(format!("{:?}", err))),
        }
    }

    pub fn open_script(&mut self, path: String) -> PyResult<String> {
        match self.scripts.open(&self.fs, path) {
            Ok(s) => Ok(s),
            Err(err) => Err(PyException::new_err(format!("{:?}", err))),
        }
    }

    pub fn set_script(&mut self, path: String, script: String) {
        self.scripts.set_script(path, script);
    }

    pub fn enumerate_messages(&self, path: &str, localized: bool) -> Option<Vec<String>> {
        self.text_data.enumerate_messages(path, localized)
    }

    pub fn enumerate_text_archives(&self) -> PyResult<Vec<String>> {
        match self.text_data.enumerate_archives(&self.fs) {
            Ok(v) => Ok(v),
            Err(err) => Err(PyException::new_err(format!("{:?}", err))),
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
            Err(err) => Err(PyException::new_err(format!("{:?}", err))),
        }
    }

    pub fn set_text_archive_title(
        &mut self,
        path: &str,
        localized: bool,
        title: String,
    ) -> PyResult<()> {
        match self.text_data.set_archive_title(path, localized, title) {
            Ok(_) => Ok(()),
            Err(err) => Err(PyException::new_err(format!("{:?}", err))),
        }
    }

    pub fn type_metadata(&self, py: Python, typename: &str) -> PyResult<Option<PyObject>> {
        self.types.type_metadata(py, typename)
    }

    pub fn field_metadata(&self, py: Python, typename: &str) -> PyResult<Option<PyObject>> {
        self.types.field_metadata(py, typename)
    }

    pub fn metadata_from_field_id(
        &self,
        py: Python,
        typename: &str,
        field_id: &str,
    ) -> PyResult<Option<PyObject>> {
        self.types.metadata_from_field_id(py, typename, field_id)
    }

    pub fn icon_category(&self, rid: RecordId) -> Option<String> {
        self.types.icon_category(rid)
    }

    pub fn copy(
        &mut self,
        source: RecordId,
        destination: RecordId,
        fields: Vec<String>,
    ) -> PyResult<()> {
        if source == destination {
            return Ok(());
        }
        self.types
            .copy(source, destination, &fields)
            .and_then(|_| {
                self.stores
                    .set_dirty_by_number(destination.store_number(), true, false)
            })
            .map_err(|err| PyException::new_err(format!("{:?}", err)))
    }

    pub fn store_is_dirty(&self, store_id: &str) -> bool {
        self.stores.is_dirty(store_id)
    }

    pub fn set_store_dirty(&mut self, store_id: &str, dirty: bool) -> PyResult<()> {
        match self.stores.set_dirty(store_id, dirty, false) {
            Ok(_) => Ok(()),
            Err(err) => Err(PyException::new_err(format!("{:?}", err))),
        }
    }

    pub fn set_forced_dirty(&mut self, store_number: StoreNumber, dirty: bool) -> PyResult<()> {
        match self.stores.set_dirty_by_number(store_number, dirty, true) {
            Ok(_) => Ok(()),
            Err(err) => Err(PyException::new_err(format!("{:?}", err))),
        }
    }

    pub fn multi_table(
        &self,
        multi_id: &str,
        key: &str,
        table: &str,
    ) -> PyResult<Option<(RecordId, String)>> {
        match self.stores.multi_table(multi_id, key, table) {
            Ok(v) => Ok(v),
            Err(err) => Err(PyException::new_err(format!("{:?}", err))),
        }
    }

    pub fn multi_open(&mut self, multi_id: &str, key: String) -> PyResult<RecordId> {
        let mut refs = ReadReferences::new();
        match self.stores.multi_open(
            &mut self.types,
            &mut refs,
            &mut self.archives,
            &self.fs,
            multi_id,
            key,
        ) {
            Ok((rid, tables)) => {
                let mut effective_tables = self.tables.clone();
                effective_tables.extend(tables);
                match refs.resolve(&effective_tables, &mut self.types) {
                    Ok(_) => Ok(rid),
                    Err(err) => Err(PyException::new_err(format!("{:?}", err))),
                }
            }
            Err(err) => Err(PyException::new_err(format!("{:?}", err))),
        }
    }

    pub fn multi_duplicate(
        &mut self,
        multi_id: &str,
        source: String,
        destination: String,
    ) -> PyResult<RecordId> {
        let mut refs = ReadReferences::new();
        match self.stores.multi_duplicate(
            &mut self.types,
            &mut refs,
            &mut self.archives,
            &self.fs,
            multi_id,
            source,
            destination,
        ) {
            Ok((rid, tables)) => {
                let mut effective_tables = self.tables.clone();
                effective_tables.extend(tables);
                match refs.resolve(&effective_tables, &mut self.types) {
                    Ok(_) => Ok(rid),
                    Err(err) => Err(PyException::new_err(format!("{:?}", err))),
                }
            }
            Err(err) => Err(PyException::new_err(format!("{:?}", err))),
        }
    }

    pub fn multi_set_dirty(&mut self, multi_id: &str, key: &str, dirty: bool) -> PyResult<()> {
        match self.stores.multi_set_dirty(multi_id, key, dirty, false) {
            Ok(_) => Ok(()),
            Err(err) => Err(PyException::new_err(format!("{:?}", err))),
        }
    }

    pub fn multi_keys(&self, multi_id: &str) -> PyResult<Vec<String>> {
        match self.stores.multi_keys(multi_id, &self.fs) {
            Ok(k) => Ok(k),
            Err(err) => Err(PyException::new_err(format!("{:?}", err))),
        }
    }

    pub fn list_cmp_files(&self, archive: &str) -> PyResult<Vec<String>> {
        self.archives
            .list_files(archive)
            .map_err(|err| PyException::new_err(format!("{:?}", err)))
    }

    pub fn read_cmp_file(&mut self, archive: &str, filename: &str) -> PyResult<Vec<u8>> {
        // TODO: Rework this API so reading does not require a mutable borrow
        self.archives
            .load_file(&self.fs, archive, filename)
            .map(|v| v.to_vec())
            .map_err(|err| PyException::new_err(format!("{:?}", err)))
    }

    pub fn write_to_cmp(
        &mut self,
        archive: &str,
        filename: &str,
        contents: Vec<u8>,
    ) -> PyResult<()> {
        self.archives
            .insert(archive, filename, contents)
            .map_err(|err| PyException::new_err(format!("{:?}", err)))
    }

    pub fn delete_cmp_file(&mut self, archive: &str, filename: &str) -> PyResult<()> {
        self.archives
            .delete(archive, filename)
            .map_err(|err| PyException::new_err(format!("{:?}", err)))
    }

    pub fn write_file(&self, path: &str, contents: &[u8]) -> PyResult<()> {
        match self.fs.write(path, contents, false) {
            Ok(_) => Ok(()),
            Err(e) => Err(PyException::new_err(format!(
                "Failed to write file {}, error {:?}",
                path, e
            ))),
        }
    }

    pub fn read_file(&self, path: &str) -> PyResult<Vec<u8>> {
        match self.fs.read(path, false) {
            Ok(b) => Ok(b),
            Err(e) => Err(PyException::new_err(format!(
                "Failed to read file {}, error {:?}",
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
            Err(err) => Err(PyException::new_err(format!("{:?}", err))),
        }
    }

    pub fn read_cgfx_textures(&self, path: String) -> PyResult<HashMap<String, Texture>> {
        match self.fs.read_cgfx_textures(&path, false) {
            Ok(t) => Ok(t
                .into_iter()
                .map(|(k, v)| -> (String, Texture) { (k, v.into()) })
                .collect()),
            Err(err) => Err(PyException::new_err(format!("{:?}", err))),
        }
    }

    pub fn read_ctpk_textures(&self, path: String) -> PyResult<HashMap<String, Texture>> {
        match self.fs.read_ctpk_textures(&path, false) {
            Ok(t) => Ok(t
                .into_iter()
                .map(|(k, v)| -> (String, Texture) { (k, v.into()) })
                .collect()),
            Err(err) => Err(PyException::new_err(format!("{:?}", err))),
        }
    }

    pub fn read_tpl_textures(&self, path: String) -> PyResult<Vec<Texture>> {
        match self.fs.read_tpl_textures(&path, false) {
            Ok(t) => Ok(t.into_iter().map(|t| t.into()).collect()),
            Err(err) => Err(PyException::new_err(format!("{:?}", err))),
        }
    }

    pub fn read_arc(&self, path: String) -> PyResult<HashMap<String, Vec<u8>>> {
        match self.fs.read_arc(&path, false) {
            Ok(a) => Ok(a),
            Err(err) => Err(PyException::new_err(format!("{:?}", err))),
        }
    }

    pub fn describe_stores(&self) -> Vec<StoreDescription> {
        self.stores.describe()
    }

    pub fn node(&self, id: &str) -> Option<UINode> {
        self.nodes.get(id).cloned()
    }

    pub fn nodes(&self) -> Vec<UINode> {
        self.nodes.values().cloned().collect()
    }

    pub fn multis(&self) -> Vec<MultiNode> {
        self.stores.multi_nodes()
    }

    pub fn table(&self, table: &str) -> Option<(RecordId, String)> {
        self.tables.get(table).cloned()
    }

    pub fn key_to_rid(&self, table: &str, key: &str) -> Option<RecordId> {
        match self.table(table) {
            Some((rid, id)) => self.list_key_to_rid(rid, &id, key),
            None => None,
        }
    }

    pub fn list_key_to_rid(&self, rid: RecordId, field_id: &str, key: &str) -> Option<RecordId> {
        match self.types.field(rid, field_id) {
            Some(Field::List(l)) => l.rid_from_key(key, &self.types),
            _ => None,
        }
    }

    pub fn key(&self, rid: RecordId) -> Option<String> {
        self.types.key(rid)
    }

    pub fn display(&self, rid: RecordId) -> Option<String> {
        self.types.display(&self.text_data, rid)
    }

    pub fn new_instance(
        &mut self,
        typename: &str,
        store_number: StoreNumber,
    ) -> PyResult<RecordId> {
        self.types
            .instantiate_and_register(typename, store_number)
            .ok_or_else(|| PyException::new_err(format!("Type '{}' does not exist", typename)))
    }

    pub fn delete_instance(&mut self, rid: RecordId) -> PyResult<()> {
        self.types
            .delete_instance(rid)
            .and_then(|_| {
                self.stores
                    .set_dirty_by_number(rid.store_number(), true, false)
            })
            .map_err(|err| PyException::new_err(format!("{:?}", err)))
    }

    pub fn type_of(&self, rid: RecordId) -> Option<String> {
        self.types.type_of(rid)
    }

    pub fn store_number_of(&self, rid: RecordId) -> StoreNumber {
        rid.store_number()
    }

    pub fn items(&self, rid: RecordId, id: &str) -> Option<Vec<RecordId>> {
        self.types.items(rid, id)
    }

    pub fn stored_type(&self, rid: RecordId, id: &str) -> Option<String> {
        self.types.stored_type(rid, id)
    }

    pub fn range(&self, rid: RecordId, id: &str) -> Option<(i64, i64)> {
        self.types.range(rid, id)
    }

    pub fn length(&self, rid: RecordId, id: &str) -> Option<usize> {
        self.types.length(rid, id)
    }

    pub fn string(&self, rid: RecordId, id: &str) -> Option<String> {
        self.types.string(rid, id)
    }

    pub fn list_index_of(&self, list_rid: RecordId, id: &str, rid: RecordId) -> Option<usize> {
        match self.types.field(list_rid, id) {
            Some(Field::List(l)) => l.index_from_rid(rid),
            _ => None,
        }
    }

    pub fn list_size(&self, rid: RecordId, id: &str) -> PyResult<usize> {
        match self.types.list_size(rid, id) {
            Ok(size) => Ok(size),
            Err(err) => Err(PyException::new_err(format!("{:?}", err))),
        }
    }

    pub fn list_get(&self, rid: RecordId, id: &str, index: usize) -> PyResult<RecordId> {
        match self.types.list_get(rid, id, index) {
            Ok(rid) => Ok(rid),
            Err(err) => Err(PyException::new_err(format!("{:?}", err))),
        }
    }

    pub fn list_get_by_field_value(
        &self,
        rid: RecordId,
        id: &str,
        field: &str,
        value: i64,
    ) -> Option<RecordId> {
        self.types.list_get_by_field_value(rid, id, field, value)
    }

    pub fn list_insert(&mut self, rid: RecordId, id: &str, index: usize) -> PyResult<RecordId> {
        self.types
            .list_insert(rid, id, index)
            .and_then(|rid| {
                self.stores
                    .set_dirty_by_number(rid.store_number(), true, false)?;
                Ok(rid)
            })
            .map_err(|err| PyException::new_err(format!("{:?}", err)))
    }

    pub fn list_insert_existing(
        &mut self,
        list_rid: RecordId,
        id: &str,
        rid: RecordId,
        index: usize,
    ) -> PyResult<()> {
        self.types
            .list_insert_existing(list_rid, id, rid, index)
            .and_then(|_| {
                self.stores
                    .set_dirty_by_number(list_rid.store_number(), true, false)
            })
            .map_err(|err| PyException::new_err(format!("{:?}", err)))
    }

    pub fn list_add(&mut self, rid: RecordId, id: &str) -> PyResult<RecordId> {
        self.types
            .list_add(rid, id)
            .and_then(|rid| {
                self.stores
                    .set_dirty_by_number(rid.store_number(), true, false)?;
                Ok(rid)
            })
            .map_err(|err| PyException::new_err(format!("{:?}", err)))
    }

    pub fn list_remove(&mut self, rid: RecordId, id: &str, index: usize) -> PyResult<()> {
        self.types
            .list_remove(rid, id, index)
            .and_then(|_| {
                self.stores
                    .set_dirty_by_number(rid.store_number(), true, false)
            })
            .map_err(|err| PyException::new_err(format!("{:?}", err)))
    }

    pub fn list_swap(&mut self, rid: RecordId, id: &str, a: usize, b: usize) -> PyResult<()> {
        self.types
            .list_swap(rid, id, a, b)
            .and_then(|_| {
                self.stores
                    .set_dirty_by_number(rid.store_number(), true, false)
            })
            .map_err(|err| PyException::new_err(format!("{:?}", err)))
    }

    pub fn list_regenerate_ids(&mut self, rid: RecordId, id: &str, base_id: usize) -> PyResult<()> {
        self.types
            .list_regenerate_ids(rid, id, base_id)
            .and_then(|_| {
                self.stores
                    .set_dirty_by_number(rid.store_number(), true, false)
            })
            .map_err(|err| PyException::new_err(format!("{:?}", err)))
    }

    pub fn key_to_rid_mapping(
        &self,
        rid: RecordId,
        id: &str,
    ) -> PyResult<HashMap<String, RecordId>> {
        self.types
            .key_to_rid_mapping(rid, id)
            .map_err(|err| PyException::new_err(format!("{:?}", err)))
    }

    pub fn set_string(&mut self, rid: RecordId, id: &str, value: Option<String>) -> PyResult<()> {
        let dirty = self.string(rid, id) != value;
        self.types
            .set_string(rid, id, value)
            .and_then(|_| {
                self.stores
                    .set_dirty_by_number(rid.store_number(), dirty, false)
            })
            .map_err(|err| PyException::new_err(format!("{:?}", err)))
    }

    pub fn int(&self, rid: RecordId, id: &str) -> Option<i64> {
        self.types.int(rid, id)
    }

    pub fn set_int(&mut self, rid: RecordId, id: &str, value: i64) -> PyResult<()> {
        let dirty = self.int(rid, id).unwrap_or_default() != value;
        self.types
            .set_int(rid, id, value)
            .and_then(|_| {
                self.stores
                    .set_dirty_by_number(rid.store_number(), dirty, false)
            })
            .map_err(|err| PyException::new_err(format!("{:?}", err)))
    }

    pub fn float(&self, rid: RecordId, id: &str) -> Option<f32> {
        self.types.float(rid, id)
    }

    pub fn set_float(&mut self, rid: RecordId, id: &str, value: f32) -> PyResult<()> {
        let dirty = self.float(rid, id).unwrap_or_default() != value;
        self.types
            .set_float(rid, id, value)
            .and_then(|_| {
                self.stores
                    .set_dirty_by_number(rid.store_number(), dirty, false)
            })
            .map_err(|err| PyException::new_err(format!("{:?}", err)))
    }

    pub fn bool(&self, rid: RecordId, id: &str) -> Option<bool> {
        self.types.bool(rid, id)
    }

    pub fn set_bool(&mut self, rid: RecordId, id: &str, value: bool) -> PyResult<()> {
        let dirty = self.bool(rid, id).unwrap_or_default() != value;
        self.types
            .set_bool(rid, id, value)
            .and_then(|_| {
                self.stores
                    .set_dirty_by_number(rid.store_number(), dirty, false)
            })
            .map_err(|err| PyException::new_err(format!("{:?}", err)))
    }

    pub fn bytes(&self, rid: RecordId, id: &str) -> Option<Vec<u8>> {
        self.types.bytes(rid, id)
    }

    pub fn get_byte(&self, rid: RecordId, id: &str, index: usize) -> PyResult<u8> {
        match self.types.get_byte(rid, id, index) {
            Ok(v) => Ok(v),
            Err(err) => Err(PyException::new_err(format!("{:?}", err))),
        }
    }

    pub fn set_bytes(&mut self, rid: RecordId, id: &str, value: Vec<u8>) -> PyResult<()> {
        let dirty = self.bytes(rid, id).unwrap_or_default() != value;
        self.types
            .set_bytes(rid, id, value)
            .and_then(|_| {
                self.stores
                    .set_dirty_by_number(rid.store_number(), dirty, false)
            })
            .map_err(|err| PyException::new_err(format!("{:?}", err)))
    }

    pub fn set_byte(&mut self, rid: RecordId, id: &str, index: usize, value: u8) -> PyResult<()> {
        let dirty = self.get_byte(rid, id, index).unwrap_or_default() != value;
        self.types
            .set_byte(rid, id, index, value)
            .and_then(|_| {
                self.stores
                    .set_dirty_by_number(rid.store_number(), dirty, false)
            })
            .map_err(|err| PyException::new_err(format!("{:?}", err)))
    }

    pub fn rid(&self, rid: RecordId, id: &str) -> Option<RecordId> {
        self.types.rid(rid, id)
    }

    pub fn set_rid(&mut self, rid: RecordId, id: &str, value: Option<RecordId>) -> PyResult<()> {
        let dirty = self.rid(rid, id) != value;
        self.types
            .set_rid(rid, id, value)
            .and_then(|_| {
                self.stores
                    .set_dirty_by_number(rid.store_number(), dirty, false)
            })
            .map_err(|err| PyException::new_err(format!("{:?}", err)))
    }

    pub fn set_items(&mut self, rid: RecordId, id: &str, value: Vec<RecordId>) -> PyResult<()> {
        let dirty = self.items(rid, id).unwrap_or_default() != value;
        self.types
            .set_items(rid, id, value)
            .and_then(|_| {
                self.stores
                    .set_dirty_by_number(rid.store_number(), dirty, false)
            })
            .map_err(|err| PyException::new_err(format!("{:?}", err)))
    }

    pub fn active_variant(&self, rid: RecordId, id: &str) -> Option<usize> {
        self.types.active_variant(rid, id)
    }

    pub fn set_active_variant(&mut self, rid: RecordId, id: &str, value: usize) -> PyResult<()> {
        let dirty = self.active_variant(rid, id).unwrap_or_default() != value;
        self.types
            .set_active_variant(rid, id, value)
            .and_then(|_| {
                self.stores
                    .set_dirty_by_number(rid.store_number(), dirty, false)
            })
            .map_err(|err| PyException::new_err(format!("{:?}", err)))
    }
}
