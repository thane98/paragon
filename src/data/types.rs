use crate::data::fields::field::Field;
use crate::data::fields::list_field::ListField;
use crate::data::{Record, TextData, TypeDefinition};
use crate::model::id::{RecordId, RecordNumber, StoreNumber};
use anyhow::{anyhow, Context};
use pyo3::{PyObject, PyResult, Python};
use rustc_hash::FxHashMap;
use std::collections::HashMap;
use std::path::{Path, PathBuf};

#[derive(Debug)]
pub struct Types {
    types: FxHashMap<String, TypeDefinition>,
    next_record_numbers: FxHashMap<StoreNumber, RecordNumber>,
    instances: FxHashMap<RecordId, Record>,
}

impl Types {
    pub fn load(dir: &PathBuf, language: &str) -> anyhow::Result<Self> {
        // Walk the directory.
        let mut complete_types: FxHashMap<String, TypeDefinition> = FxHashMap::default();
        let generated_dir = dir.join(Path::new("Generated"));
        let language_dir = dir.join(Path::new(language));
        Types::load_types_from_dir(&mut complete_types, dir)?;
        Types::load_types_from_dir(&mut complete_types, &generated_dir)?;
        Types::load_types_from_dir(&mut complete_types, &language_dir)?;
        Ok(Types {
            types: complete_types,
            next_record_numbers: FxHashMap::default(),
            instances: FxHashMap::default(),
        })
    }

    fn load_types_from_dir(
        types: &mut FxHashMap<String, TypeDefinition>,
        dir: &PathBuf,
    ) -> anyhow::Result<()> {
        if dir.is_dir() {
            for entry in std::fs::read_dir(dir)? {
                let entry = entry?;
                let path = entry.path();
                if !path.is_dir() {
                    let types_in_dir = Types::read_definitions(&path)?;
                    types.extend(types_in_dir);
                }
            }
        }
        Ok(())
    }

    fn read_definitions(path: &PathBuf) -> anyhow::Result<HashMap<String, TypeDefinition>> {
        let raw_types = std::fs::read_to_string(path).with_context(|| {
            format!(
                "Failed to read type definitions from path '{}'",
                path.display()
            )
        })?;
        let mut types: HashMap<String, TypeDefinition> = serde_yaml::from_str(&raw_types)
            .with_context(|| {
                format!(
                    "Failed to parse type definitions from path '{}'",
                    path.display()
                )
            })?;
        for td in types.values_mut() {
            td.post_init();
        }
        Ok(types)
    }

    pub fn register_type(&mut self, name: String, td: TypeDefinition) {
        self.types.insert(name, td);
    }

    pub fn define_simple_table(&mut self, stored_type: String) -> String {
        let table_typename = format!("__table_inject__{}", stored_type);
        let container = ListField::create_table_container(stored_type);
        let td = TypeDefinition::with_fields(vec![Field::List(container)]);
        self.types.insert(table_typename.clone(), td);
        table_typename
    }

    pub fn peek_next_rid(&self, store_number: StoreNumber) -> RecordId {
        RecordId::new(
            store_number,
            self.next_record_numbers
                .get(&store_number)
                .cloned()
                .unwrap_or_default(),
        )
    }

    pub fn instantiate_and_register(
        &mut self,
        name: &str,
        store_number: StoreNumber,
    ) -> Option<RecordId> {
        self.instantiate(name)
            .map(|record| self.register(record, store_number))
    }

    pub fn instantiate(&self, name: &str) -> Option<Record> {
        self.types
            .get(name)
            .map(|t| Record::new(name.to_string(), t))
    }

    pub fn register(&mut self, record: Record, store_number: StoreNumber) -> RecordId {
        let rid = self.allocate_record_id(store_number);
        self.instances.insert(rid, record);
        rid
    }

    fn allocate_record_id(&mut self, store_number: StoreNumber) -> RecordId {
        let record_number_entry = self
            .next_record_numbers
            .entry(store_number)
            .or_default();
        let rid = RecordId::new(store_number, *record_number_entry);
        record_number_entry.increment();
        rid
    }

    pub fn get(&self, name: &str) -> Option<&TypeDefinition> {
        self.types.get(name)
    }

    pub fn instance(&self, rid: RecordId) -> Option<&Record> {
        self.instances.get(&rid)
    }

    pub fn instance_mut(&mut self, rid: RecordId) -> Option<&mut Record> {
        self.instances.get_mut(&rid)
    }

    pub fn field(&self, rid: RecordId, id: &str) -> Option<&Field> {
        match self.instance(rid) {
            Some(instance) => instance.field(id),
            None => None,
        }
    }

    pub fn field_mut(&mut self, rid: RecordId, id: &str) -> Option<&mut Field> {
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

    pub fn delete_instance(&mut self, rid: RecordId) -> anyhow::Result<()> {
        if !self.instances.contains_key(&rid) {
            Err(anyhow!("Cannot delete invalid RID {}.", rid))
        } else {
            self.instances.remove(&rid);
            Ok(())
        }
    }

    pub fn copy(
        &mut self,
        source: RecordId,
        destination: RecordId,
        fields: &[String],
    ) -> anyhow::Result<()> {
        let source = self
            .instance(source)
            .ok_or_else(|| anyhow!("Bad source RID {} in copy.", source))?
            .clone();
        let mut dest = self
            .instance(destination)
            .ok_or_else(|| anyhow!("Bad destination RID {} in copy.", destination))?
            .to_owned();
        source.copy_to(&mut dest, fields, self, destination.store_number())?;
        self.instances.insert(destination, dest);
        Ok(())
    }

    pub fn type_of(&self, rid: RecordId) -> Option<String> {
        self.instance(rid).map(|r| r.typename().to_string())
    }

    pub fn icon_category(&self, rid: RecordId) -> Option<String> {
        match self.instance(rid) {
            Some(r) => self.get(r.typename()).and_then(|t| t.icon.clone()),
            None => None,
        }
    }

    pub fn items(&self, rid: RecordId, id: &str) -> Option<Vec<RecordId>> {
        self.field(rid, id).and_then(|f| f.items())
    }

    pub fn stored_type(&self, rid: RecordId, id: &str) -> Option<String> {
        match self.field(rid, id) {
            Some(f) => f.stored_type(),
            None => None,
        }
    }

    pub fn range(&self, rid: RecordId, id: &str) -> Option<(i64, i64)> {
        match self.field(rid, id) {
            Some(f) => f.range(),
            None => None,
        }
    }

    pub fn length(&self, rid: RecordId, id: &str) -> Option<usize> {
        match self.field(rid, id) {
            Some(f) => f.length(),
            None => None,
        }
    }

    pub fn size_of(&self, typename: &str) -> Option<usize> {
        self.get(typename).map(|td| td.size)
    }

    pub fn display(&self, text_data: &TextData, rid: RecordId) -> Option<String> {
        // TODO: Maybe a functional approach would work better here?
        match self.instance(rid) {
            Some(r) => match self.get(r.typename()) {
                Some(td) => match &td.display {
                    Some(display) => match r.field(display) {
                        Some(f) => f.display_text(self, text_data),
                        None => None,
                    },
                    None => None,
                },
                None => None,
            },
            None => None,
        }
    }

    pub fn key(&self, rid: RecordId) -> Option<String> {
        // TODO: Maybe a functional approach would work better here?
        match self.instance(rid) {
            Some(r) => match self.get(r.typename()) {
                Some(td) => match &td.key {
                    Some(key) => match r.field(key) {
                        Some(f) => f.key(self),
                        None => None,
                    },
                    None => None,
                },
                None => None,
            },
            None => None,
        }
    }

    pub fn list_size(&self, rid: RecordId, id: &str) -> anyhow::Result<usize> {
        match self.field(rid, id) {
            Some(f) => f.list_size(),
            None => Err(anyhow!("Bad rid/id combo: {} {}", rid, id)),
        }
    }

    pub fn list_get(&self, rid: RecordId, id: &str, index: usize) -> anyhow::Result<RecordId> {
        match self.field(rid, id) {
            Some(f) => f.list_get(index),
            None => Err(anyhow!("Bad rid/id combo: {} {}", rid, id)),
        }
    }

    pub fn list_get_by_field_value(
        &self,
        rid: RecordId,
        id: &str,
        field: &str,
        value: i64,
    ) -> Option<RecordId> {
        match self.field(rid, id) {
            Some(Field::List(l)) => l.rid_from_int_field(value, field, self),
            _ => None,
        }
    }

    pub fn list_insert(
        &mut self,
        rid: RecordId,
        id: &str,
        index: usize,
    ) -> anyhow::Result<RecordId> {
        // Hold on to the base ID for ID generation.
        let base_id = self.list_base_id(rid, id);

        // Allocate an instance of the list's stored type.
        let stored_type = self
            .stored_type(rid, id)
            .ok_or_else(|| anyhow!("Field is not a list."))?;
        let new_rid = self
            .instantiate_and_register(&stored_type, rid.store_number())
            .ok_or_else(|| anyhow!("Instantiation failed."))?;

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
        list_rid: RecordId,
        id: &str,
        rid: RecordId,
        index: usize,
    ) -> anyhow::Result<()> {
        match self.field_mut(list_rid, id) {
            Some(f) => f.list_insert(rid, index),
            None => Err(anyhow!("Bad rid/id combo: {} {}", rid, id)),
        }
    }

    pub fn list_add(&mut self, rid: RecordId, id: &str) -> anyhow::Result<RecordId> {
        let length = self
            .length(rid, id)
            .ok_or_else(|| anyhow!("Field is not a list."))?;
        self.list_insert(rid, id, length)
    }

    pub fn list_remove(&mut self, rid: RecordId, id: &str, index: usize) -> anyhow::Result<()> {
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

    pub fn list_swap(&mut self, rid: RecordId, id: &str, a: usize, b: usize) -> anyhow::Result<()> {
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
    pub fn list_base_id(&self, rid: RecordId, id: &str) -> Option<usize> {
        match self.stored_type(rid, id) {
            Some(typename) => match self.list_index_field_id(&typename) {
                Some(index_id) => {
                    if self.list_size(rid, id).ok().unwrap_or_default() > 0 {
                        self.list_get(rid, id, 0)
                            .ok()
                            .and_then(|rid| self.int(rid, &index_id))
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
        rid: RecordId,
        id: &str,
        base_id: usize,
    ) -> anyhow::Result<()> {
        let stored_type = self
            .stored_type(rid, id)
            .ok_or_else(|| anyhow!("Field is not a list."))?;
        match self.list_index_field_id(&stored_type) {
            Some(index_id) => {
                let items = self
                    .items(rid, id)
                    .ok_or_else(|| anyhow!("Field is not a list."))?;
                for (i, item) in items.iter().enumerate() {
                    let id = base_id + i;
                    self.set_int(*item, &index_id, id as i64)?;
                }
                Ok(())
            }
            None => Ok(()),
        }
    }

    pub fn key_to_rid_mapping(
        &self,
        rid: RecordId,
        id: &str,
    ) -> anyhow::Result<HashMap<String, RecordId>> {
        match self.items(rid, id) {
            Some(items) => {
                let mut mapping: HashMap<String, RecordId> = HashMap::new();
                for rid in items {
                    if let Some(key) = self.key(rid) {
                        mapping.insert(key, rid);
                    }
                }
                Ok(mapping)
            }
            None => Err(anyhow!("rid/id combo is not a valid list: {} {}", rid, id)),
        }
    }

    pub fn string(&self, rid: RecordId, id: &str) -> Option<String> {
        match self.instance(rid) {
            Some(r) => r.string(id),
            None => None,
        }
    }

    pub fn set_string(
        &mut self,
        rid: RecordId,
        id: &str,
        value: Option<String>,
    ) -> anyhow::Result<()> {
        match self.field_mut(rid, id) {
            Some(f) => f.set_string(value),
            None => Err(anyhow!("Bad rid/id combo: {} {}", rid, id)),
        }
    }

    pub fn int(&self, rid: RecordId, id: &str) -> Option<i64> {
        match self.field(rid, id) {
            Some(f) => f.int_value(),
            None => None,
        }
    }

    pub fn set_int(&mut self, rid: RecordId, id: &str, value: i64) -> anyhow::Result<()> {
        match self.field_mut(rid, id) {
            Some(f) => f.set_int(value),
            None => Err(anyhow!("Bad rid/id combo: {} {}", rid, id)),
        }
    }

    pub fn float(&self, rid: RecordId, id: &str) -> Option<f32> {
        match self.field(rid, id) {
            Some(f) => f.float_value(),
            None => None,
        }
    }

    pub fn set_float(&mut self, rid: RecordId, id: &str, value: f32) -> anyhow::Result<()> {
        match self.field_mut(rid, id) {
            Some(f) => f.set_float(value),
            None => Err(anyhow!("Bad rid/id combo: {} {}", rid, id)),
        }
    }

    pub fn bool(&self, rid: RecordId, id: &str) -> Option<bool> {
        match self.field(rid, id) {
            Some(f) => f.bool_value(),
            None => None,
        }
    }

    pub fn set_bool(&mut self, rid: RecordId, id: &str, value: bool) -> anyhow::Result<()> {
        match self.field_mut(rid, id) {
            Some(f) => f.set_bool(value),
            None => Err(anyhow!("Bad rid/id combo: {} {}", rid, id)),
        }
    }

    pub fn bytes(&self, rid: RecordId, id: &str) -> Option<Vec<u8>> {
        match self.field(rid, id) {
            Some(f) => f.bytes_value(),
            None => None,
        }
    }

    pub fn set_bytes(&mut self, rid: RecordId, id: &str, value: Vec<u8>) -> anyhow::Result<()> {
        match self.field_mut(rid, id) {
            Some(f) => f.set_bytes(value),
            None => Err(anyhow!("Bad rid/id combo: {} {}", rid, id)),
        }
    }

    pub fn get_byte(&self, rid: RecordId, id: &str, index: usize) -> anyhow::Result<u8> {
        match self.field(rid, id) {
            Some(f) => f.get_byte(index),
            None => Err(anyhow!("Bad rid/id combo: {} {}", rid, id)),
        }
    }

    pub fn set_byte(
        &mut self,
        rid: RecordId,
        id: &str,
        index: usize,
        value: u8,
    ) -> anyhow::Result<()> {
        match self.field_mut(rid, id) {
            Some(f) => f.set_byte(index, value),
            None => Err(anyhow!("Bad rid/id combo: {} {}", rid, id)),
        }
    }

    pub fn rid(&self, rid: RecordId, id: &str) -> Option<RecordId> {
        match self.field(rid, id) {
            Some(f) => f.rid_value(),
            None => None,
        }
    }

    pub fn set_rid(
        &mut self,
        rid: RecordId,
        id: &str,
        value: Option<RecordId>,
    ) -> anyhow::Result<Option<RecordId>> {
        // Cases that change a record's ownership need special handling.
        // These cases DON'T require anything special:
        // - Nulling a reference.
        // - Updates within the same store.
        // - Updates to fields that don't take ownership of the value (ex. references)
        if value.is_none()
            || value.unwrap().store_number() == rid.store_number()
            || self
                .field(rid, id)
                .map(|f| !f.is_rid_owner())
                .unwrap_or_default()
        {
            return match self.field_mut(rid, id) {
                Some(f) => {
                    f.set_rid(value)?;
                    Ok(value)
                }
                None => Err(anyhow!("Bad rid/id combo: {} {}", rid, id)),
            };
        }

        // We have an ownership change.
        // For this to work, we have to take out the record and register it under a different key for the new store.
        let old_value_rid = value.unwrap();
        let record = self
            .instances
            .remove(&old_value_rid)
            .ok_or_else(|| anyhow!("Bad record number '{}'", old_value_rid))?;
        let new_value_rid = self.register(record, rid.store_number());
        self.set_rid(rid, id, Some(new_value_rid))
    }

    pub fn set_items(
        &mut self,
        rid: RecordId,
        id: &str,
        value: Vec<RecordId>,
    ) -> anyhow::Result<()> {
        match self.field_mut(rid, id) {
            Some(f) => f.set_items(
                value
                    .into_iter()
                    .map(|item_rid| item_rid.with_store_number(rid.store_number()))
                    .collect(),
            ),
            None => Err(anyhow!("Bad rid/id combo: {} {}", rid, id)),
        }
    }

    pub fn active_variant(&self, rid: RecordId, id: &str) -> Option<usize> {
        self.field(rid, id).and_then(|f| f.active_variant())
    }

    pub fn set_active_variant(
        &mut self,
        rid: RecordId,
        id: &str,
        value: usize,
    ) -> anyhow::Result<()> {
        match self.field_mut(rid, id) {
            Some(f) => f.set_active_variant(value),
            None => Err(anyhow!("Bad rid/id combo: {} {}", rid, id)),
        }
    }
}
