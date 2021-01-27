use super::{Field, Record, TypeDefinition, TextData};
use anyhow::anyhow;
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
        let mut complete_types: HashMap<String, TypeDefinition> = HashMap::new();
        let paths = std::fs::read_dir(dir)?;
        for path in paths {
            match path {
                Ok(p) => {
                    let metadata = p.metadata()?;
                    if metadata.is_file() {
                        let raw_types = std::fs::read_to_string(p.path())?;
                        let types: HashMap<String, TypeDefinition> =
                            serde_yaml::from_str(&raw_types)?;
                        complete_types.extend(types.into_iter());
                    }
                }
                Err(_) => {}
            }
        }
        for td in complete_types.values_mut() {
            td.post_init();
        }
        Ok(Types {
            types: complete_types,
            next_rid: 0,
            instances: HashMap::new(),
        })
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
            .clone();
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
                    }
                    None => None,
                },
                None => None,
            }
            None => None,
        }
    }

    pub fn list_insert(&mut self, rid: u64, id: &str, index: usize) -> anyhow::Result<u64> {
        // Allocate an instance of the list's stored type.
        let stored_type = self
            .stored_type(rid, id)
            .ok_or(anyhow!("Field is not a list."))?;
        let new_rid = self
            .instantiate_and_register(&stored_type)
            .ok_or(anyhow!("Instantiation failed."))?;

        // Insert the instance into the list.
        // Deallocate it if the operation fails to avoid a memory leak.
        match self.field_mut(rid, id) {
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
        }
    }

    pub fn list_add(&mut self, rid: u64, id: &str) -> anyhow::Result<u64> {
        let length = self
            .length(rid, id)
            .ok_or(anyhow!("Field is not a list."))?;
        self.list_insert(rid, id, length)
    }

    pub fn list_remove(&mut self, rid: u64, id: &str, index: usize) -> anyhow::Result<()> {
        match self.field_mut(rid, id) {
            Some(f) => f.list_remove(index),
            None => Err(anyhow!("Bad rid/id combo: {} {}", rid, id)),
        }
    }

    pub fn list_swap(&mut self, rid: u64, id: &str, a: usize, b: usize) -> anyhow::Result<()> {
        match self.field_mut(rid, id) {
            Some(f) => f.list_swap(a, b),
            None => Err(anyhow!("Bad rid/id combo: {} {}", rid, id)),
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
}
