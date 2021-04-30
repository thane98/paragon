use super::{Field, Record, TextData, TypeDefinition};
use anyhow::{anyhow, Context};
use pyo3::{PyObject, PyResult, Python};
use std::collections::HashMap;
use std::path::PathBuf;

#[derive(Debug)]
pub struct Types {
    types: HashMap<String, TypeDefinition>,
    next_rid: u64,
    instances: HashMap<u64, Record>,
}

impl Types {
    pub fn load(dir: &PathBuf) -> anyhow::Result<Self> {
        // Walk the directory.
        let mut complete_types: HashMap<String, TypeDefinition> = HashMap::new();
        if dir.exists() {
            let paths = std::fs::read_dir(dir)
                .with_context(|| format!("Error walking directory {} in Types.", dir.display()))?;
            for path in paths {
                match path {
                    Ok(p) => {
                        // Parse type definitions from every file we encounter.
                        let metadata = p.metadata()?;
                        if metadata.is_file() {
                            let types = Types::read_definitions(p.path())?;
                            complete_types.extend(types);
                        }
                    }
                    Err(_) => {}
                }
            }
            for td in complete_types.values_mut() {
                td.post_init();
            }
        }
        Ok(Types {
            types: complete_types,
            next_rid: 0,
            instances: HashMap::new(),
        })
    }

    fn read_definitions(path: PathBuf) -> anyhow::Result<HashMap<String, TypeDefinition>> {
        let raw_types = std::fs::read_to_string(&path).with_context(|| {
            format!(
                "Failed to read type definitions from path '{}'",
                path.display()
            )
        })?;
        let types: HashMap<String, TypeDefinition> = serde_yaml::from_str(&raw_types)
            .with_context(|| {
                format!(
                    "Failed to parse type definitions from path '{}'",
                    path.display()
                )
            })?;
        Ok(types)
    }

    pub fn peek_next_rid(&self) -> u64 {
        self.next_rid
    }

    pub fn instantiate_and_register(&mut self, name: &str) -> Option<u64> {
        match self.instantiate(name) {
            Some(record) => Some(self.register(record)),
            None => None,
        }
    }

    pub fn instantiate(&self, name: &str) -> Option<Record> {
        match self.types.get(name) {
            Some(t) => Some(Record::new(name.to_string(), t)),
            None => None,
        }
    }

    pub fn register(&mut self, record: Record) -> u64 {
        let rid = self.next_rid;
        self.instances.insert(rid, record);
        self.next_rid += 1;
        rid
    }

    pub fn get(&self, name: &str) -> Option<&TypeDefinition> {
        self.types.get(name)
    }

    pub fn instance(&self, rid: u64) -> Option<&Record> {
        self.instances.get(&rid)
    }

    pub fn instance_mut(&mut self, rid: u64) -> Option<&mut Record> {
        self.instances.get_mut(&rid)
    }

    pub fn field(&self, rid: u64, id: &str) -> Option<&Field> {
        match self.instance(rid) {
            Some(instance) => instance.field(id),
            None => None,
        }
    }

    pub fn field_mut(&mut self, rid: u64, id: &str) -> Option<&mut Field> {
        match self.instance_mut(rid) {
            Some(instance) => instance.field_mut(id),
            None => None,
        }
    }

    pub fn type_metadata(&self, py: Python, typename: &str) -> PyResult<Option<PyObject>> {
        match self.get(typename) {
            Some(t) => match t.type_metadata(py) {
                Ok(obj) => Ok(Some(obj)),
                Err(err) => Err(err),
            },
            None => Ok(None),
        }
    }

    pub fn field_metadata(&self, py: Python, typename: &str) -> PyResult<Option<PyObject>> {
        match self.get(typename) {
            Some(t) => match t.field_metadata(py) {
                Ok(obj) => Ok(Some(obj)),
                Err(err) => Err(err),
            },
            None => Ok(None),
        }
    }

    pub fn metadata_from_field_id(
        &self,
        py: Python,
        typename: &str,
        field_id: &str,
    ) -> PyResult<Option<PyObject>> {
        match self.get(typename) {
            Some(t) => match t.get_field(field_id) {
                Some(f) => match f.metadata(py) {
                    Ok(obj) => Ok(Some(obj)),
                    Err(err) => Err(err),
                },
                None => Ok(None),
            },
            None => Ok(None),
        }
    }

    pub fn delete_instance(&mut self, rid: u64) -> anyhow::Result<()> {
        if !self.instances.contains_key(&rid) {
            Err(anyhow!("Cannot delete invalid RID {}.", rid))
        } else {
            self.instances.remove(&rid);
            Ok(())
        }
    }

    pub fn copy(&mut self, source: u64, destination: u64, fields: &[String]) -> anyhow::Result<()> {
        let source = self
            .instance(source)
            .ok_or(anyhow!("Bad source RID {} in copy.", source))?
            .clone();
        let mut dest = self
            .instance(destination)
            .ok_or(anyhow!("Bad destination RID {} in copy.", destination))?
            .to_owned();
        source.copy_to(&mut dest, fields, self)?;
        self.instances.insert(destination, dest);
        Ok(())
    }

    pub fn type_of(&self, rid: u64) -> Option<String> {
        self.instance(rid).map(|r| r.typename().to_string())
    }

    pub fn icon_category(&self, rid: u64) -> Option<String> {
        match self.instance(rid) {
            Some(r) => self.get(&r.typename()).map(|t| t.icon.clone()).flatten(),
            None => None,
        }
    }

    pub fn items(&self, rid: u64, id: &str) -> Option<Vec<u64>> {
        self.field(rid, id).map(|f| f.items()).flatten()
    }

    pub fn stored_type(&self, rid: u64, id: &str) -> Option<String> {
        match self.field(rid, id) {
            Some(f) => f.stored_type(),
            None => None,
        }
    }

    pub fn range(&self, rid: u64, id: &str) -> Option<(i64, i64)> {
        match self.field(rid, id) {
            Some(f) => f.range(),
            None => None,
        }
    }

    pub fn length(&self, rid: u64, id: &str) -> Option<usize> {
        match self.field(rid, id) {
            Some(f) => f.length(),
            None => None,
        }
    }

    pub fn size_of(&self, typename: &str) -> Option<usize> {
        self.get(typename).map(|td| td.size)
    }

    pub fn display(&self, text_data: &TextData, rid: u64) -> Option<String> {
        // TODO: Maybe a functional approach would work better here?
        match self.instance(rid) {
            Some(r) => match self.get(&r.typename()) {
                Some(td) => match &td.display {
                    Some(display) => match r.field(display) {
                        Some(f) => match f.display_text(self, text_data) {
                            Some(v) => Some(v),
                            None => None,
                        },
                        None => None,
                    },
                    None => None,
                },
                None => None,
            },
            None => None,
        }
    }

    pub fn key(&self, rid: u64) -> Option<String> {
        // TODO: Maybe a functional approach would work better here?
        match self.instance(rid) {
            Some(r) => match self.get(&r.typename()) {
                Some(td) => match &td.key {
                    Some(key) => match r.field(key) {
                        Some(f) => match f.key(self) {
                            Some(v) => Some(v),
                            None => None,
                        },
                        None => None,
                    },
                    None => None,
                },
                None => None,
            },
            None => None,
        }
    }

    pub fn list_size(&self, rid: u64, id: &str) -> anyhow::Result<usize> {
        match self.field(rid, id) {
            Some(f) => f.list_size(),
            None => Err(anyhow!("Bad rid/id combo: {} {}", rid, id)),
        }
    }

    pub fn list_get(&self, rid: u64, id: &str, index: usize) -> anyhow::Result<u64> {
        match self.field(rid, id) {
            Some(f) => f.list_get(index),
            None => Err(anyhow!("Bad rid/id combo: {} {}", rid, id)),
        }
    }

    pub fn list_get_by_field_value(
        &self,
        rid: u64,
        id: &str,
        field: &str,
        value: i64,
    ) -> Option<u64> {
        match self.field(rid, id) {
            Some(list) => match list {
                Field::List(l) => l.rid_from_int_field(value, field, self),
                _ => None,
            },
            None => None,
        }
    }

    pub fn list_insert(&mut self, rid: u64, id: &str, index: usize) -> anyhow::Result<u64> {
        // Hold on to the base ID for ID generation.
        let base_id = self.list_base_id(rid, id);

        // Allocate an instance of the list's stored type.
        let stored_type = self
            .stored_type(rid, id)
            .ok_or(anyhow!("Field is not a list."))?;
        let new_rid = self
            .instantiate_and_register(&stored_type)
            .ok_or(anyhow!("Instantiation failed."))?;

        // Insert the instance into the list.
        // Deallocate it if the operation fails to avoid a memory leak.
        let new_rid = match self.field_mut(rid, id) {
            Some(f) => match f.list_insert(new_rid, index) {
                Ok(_) => Ok(new_rid),
                Err(err) => {
                    self.instances.remove(&new_rid);
                    Err(err)
                }
            },
            None => {
                self.instances.remove(&new_rid);
                Err(anyhow!("Bad rid/id combo: {} {}", rid, id))
            }
        }?;

        // Inserted the element. Now we need to regenerate IDs for list items.
        if let Some(base_id) = base_id {
            self.list_regenerate_ids(rid, id, base_id)?;
        }

        Ok(new_rid)
    }

    pub fn list_insert_existing(
        &mut self,
        list_rid: u64,
        id: &str,
        rid: u64,
        index: usize,
    ) -> anyhow::Result<()> {
        match self.field_mut(list_rid, id) {
            Some(f) => f.list_insert(rid, index),
            None => Err(anyhow!("Bad rid/id combo: {} {}", rid, id)),
        }
    }

    pub fn list_add(&mut self, rid: u64, id: &str) -> anyhow::Result<u64> {
        let length = self
            .length(rid, id)
            .ok_or(anyhow!("Field is not a list."))?;
        self.list_insert(rid, id, length)
    }

    pub fn list_remove(&mut self, rid: u64, id: &str, index: usize) -> anyhow::Result<()> {
        // Get the base ID now in case we need to regenerate these after removing.
        let base_id = self.list_base_id(rid, id);

        // TODO: Note that some parts of the frontend (undo/redo) rely on this NOT
        //       garbage collecting the element immediately.
        match self.field_mut(rid, id) {
            Some(f) => f.list_remove(index),
            None => Err(anyhow!("Bad rid/id combo: {} {}", rid, id)),
        }?;

        // Regenerate IDs.
        if let Some(base_id) = base_id {
            self.list_regenerate_ids(rid, id, base_id)?;
        }

        Ok(())
    }

    pub fn list_swap(&mut self, rid: u64, id: &str, a: usize, b: usize) -> anyhow::Result<()> {
        // Get the base ID now in case we need to regenerate these after swapping.
        let base_id = self.list_base_id(rid, id);

        // Perform the swap.
        match self.field_mut(rid, id) {
            Some(f) => f.list_swap(a, b),
            None => Err(anyhow!("Bad rid/id combo: {} {}", rid, id)),
        }?;

        // Regenerate IDs.
        if let Some(base_id) = base_id {
            self.list_regenerate_ids(rid, id, base_id)?;
        }

        Ok(())
    }

    fn list_index_field_id(&self, typename: &str) -> Option<String> {
        match self.get(typename) {
            Some(td) => td.index.clone(),
            None => None,
        }
    }

    // Automatically determine the base ID for the list.
    pub fn list_base_id(&self, rid: u64, id: &str) -> Option<usize> {
        match self.stored_type(rid, id) {
            Some(typename) => match self.list_index_field_id(&typename) {
                Some(index_id) => {
                    if self.list_size(rid, id).ok().unwrap_or_default() > 0 {
                        self.list_get(rid, id, 0)
                            .ok()
                            .map(|rid| self.int(rid, &index_id))
                            .flatten()
                            .map(|id| id as usize)
                    } else {
                        Some(0)
                    }
                }
                None => None,
            },
            None => None,
        }
    }

    // TODO: This isn't optimized - it will likely go over several elements
    //       whose IDs don't need to be updated.
    pub fn list_regenerate_ids(
        &mut self,
        rid: u64,
        id: &str,
        base_id: usize,
    ) -> anyhow::Result<()> {
        let stored_type = self
            .stored_type(rid, id)
            .ok_or(anyhow!("Field is not a list."))?;
        match self.list_index_field_id(&stored_type) {
            Some(index_id) => {
                let items = self.items(rid, id).ok_or(anyhow!("Field is not a list."))?;
                for i in 0..items.len() {
                    let id = base_id + i;
                    self.set_int(items[i], &index_id, id as i64)?;
                }
                Ok(())
            }
            None => Ok(()),
        }
    }

    pub fn string(&self, rid: u64, id: &str) -> Option<String> {
        match self.instance(rid) {
            Some(r) => r.string(id),
            None => None,
        }
    }

    pub fn set_string(&mut self, rid: u64, id: &str, value: Option<String>) -> anyhow::Result<()> {
        match self.field_mut(rid, id) {
            Some(f) => f.set_string(value),
            None => Err(anyhow!("Bad rid/id combo: {} {}", rid, id)),
        }
    }

    pub fn int(&self, rid: u64, id: &str) -> Option<i64> {
        match self.field(rid, id) {
            Some(f) => f.int_value(),
            None => None,
        }
    }

    pub fn set_int(&mut self, rid: u64, id: &str, value: i64) -> anyhow::Result<()> {
        match self.field_mut(rid, id) {
            Some(f) => f.set_int(value),
            None => Err(anyhow!("Bad rid/id combo: {} {}", rid, id)),
        }
    }

    pub fn float(&self, rid: u64, id: &str) -> Option<f32> {
        match self.field(rid, id) {
            Some(f) => f.float_value(),
            None => None,
        }
    }

    pub fn set_float(&mut self, rid: u64, id: &str, value: f32) -> anyhow::Result<()> {
        match self.field_mut(rid, id) {
            Some(f) => f.set_float(value),
            None => Err(anyhow!("Bad rid/id combo: {} {}", rid, id)),
        }
    }

    pub fn bool(&self, rid: u64, id: &str) -> Option<bool> {
        match self.field(rid, id) {
            Some(f) => f.bool_value(),
            None => None,
        }
    }

    pub fn set_bool(&mut self, rid: u64, id: &str, value: bool) -> anyhow::Result<()> {
        match self.field_mut(rid, id) {
            Some(f) => f.set_bool(value),
            None => Err(anyhow!("Bad rid/id combo: {} {}", rid, id)),
        }
    }

    pub fn bytes(&self, rid: u64, id: &str) -> Option<Vec<u8>> {
        match self.field(rid, id) {
            Some(f) => f.bytes_value(),
            None => None,
        }
    }

    pub fn set_bytes(&mut self, rid: u64, id: &str, value: Vec<u8>) -> anyhow::Result<()> {
        match self.field_mut(rid, id) {
            Some(f) => f.set_bytes(value),
            None => Err(anyhow!("Bad rid/id combo: {} {}", rid, id)),
        }
    }

    pub fn get_byte(&self, rid: u64, id: &str, index: usize) -> anyhow::Result<u8> {
        match self.field(rid, id) {
            Some(f) => f.get_byte(index),
            None => Err(anyhow!("Bad rid/id combo: {} {}", rid, id)),
        }
    }

    pub fn set_byte(&mut self, rid: u64, id: &str, index: usize, value: u8) -> anyhow::Result<()> {
        match self.field_mut(rid, id) {
            Some(f) => f.set_byte(index, value),
            None => Err(anyhow!("Bad rid/id combo: {} {}", rid, id)),
        }
    }

    pub fn rid(&self, rid: u64, id: &str) -> Option<u64> {
        match self.field(rid, id) {
            Some(f) => f.rid_value(),
            None => None,
        }
    }

    pub fn set_rid(&mut self, rid: u64, id: &str, value: Option<u64>) -> anyhow::Result<()> {
        match self.field_mut(rid, id) {
            Some(f) => f.set_rid(value),
            None => Err(anyhow!("Bad rid/id combo: {} {}", rid, id)),
        }
    }

    pub fn active_variant(&self, rid: u64, id: &str) -> Option<usize> {
        self.field(rid, id).map(|f| f.active_variant()).flatten()
    }

    pub fn set_active_variant(&mut self, rid: u64, id: &str, value: usize) -> anyhow::Result<()> {
        match self.field_mut(rid, id) {
            Some(f) => f.set_active_variant(value),
            None => Err(anyhow!("Bad rid/id combo: {} {}", rid, id)),
        }
    }
}
