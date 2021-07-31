use crate::data::Types;
use anyhow::{anyhow, Context};
use mila::BinArchiveWriter;
use std::collections::{BTreeSet, HashMap};
use crate::data::fields::field::Field;

#[derive(Debug)]
struct IndexReference {
    index: usize,
    table: String,
    rid: u64,
    id: String,
}

#[derive(Debug)]
struct FieldReference {
    value: i64,
    table: String,
    target_field: String,
    rid: u64,
    id: String,
}

#[derive(Debug)]
struct KeyReference {
    key: String,
    table: String,
    rid: u64,
    id: String,
}

#[derive(Debug)]
struct PointerReference {
    address: usize,
    table: String,
    rid: u64,
    id: String,
}

pub struct ReadReferences {
    index_refs: Vec<IndexReference>,
    field_refs: Vec<FieldReference>,
    key_refs: Vec<KeyReference>,
    pointer_refs: Vec<PointerReference>,
    known_records: HashMap<(usize, String), u64>,
}

pub struct WriteReferences<'a> {
    tables: &'a HashMap<String, (u64, String)>,
    types: &'a Types,
    known_pointers: Vec<(u64, usize)>,
    known_records: HashMap<u64, usize>,
}

impl ReadReferences {
    pub fn new() -> Self {
        ReadReferences {
            index_refs: Vec::new(),
            field_refs: Vec::new(),
            key_refs: Vec::new(),
            pointer_refs: Vec::new(),
            known_records: HashMap::new(),
        }
    }

    pub fn pointers_to_table(&self, table: &str) -> BTreeSet<usize> {
        self.pointer_refs
            .iter()
            .filter(|r| r.table == table)
            .map(|r| r.address)
            .collect()
    }

    pub fn add_id(&mut self, index: usize, table: String, rid: u64, id: String) {
        self.index_refs.push(IndexReference {
            index,
            table,
            rid,
            id,
        });
    }

    pub fn add_field(
        &mut self,
        value: i64,
        table: String,
        target_field: String,
        rid: u64,
        id: String,
    ) {
        self.field_refs.push(FieldReference {
            value,
            table,
            target_field,
            rid,
            id,
        })
    }

    pub fn add_key(&mut self, key: String, table: String, rid: u64, id: String) {
        self.key_refs.push(KeyReference {
            key,
            table,
            rid,
            id,
        });
    }

    pub fn add_pointer(&mut self, address: usize, table: String, rid: u64, id: String) {
        self.pointer_refs.push(PointerReference {
            address,
            table,
            rid,
            id,
        });
    }

    pub fn add_known_record(&mut self, address: usize, table: String, rid: u64) {
        self.known_records.insert((address, table), rid);
    }

    pub fn resolve(
        &self,
        tables: &HashMap<String, (u64, String)>,
        types: &mut Types,
    ) -> anyhow::Result<()> {
        for index_ref in &self.index_refs {
            // Find the item's rid.
            let table = tables
                .get(&index_ref.table)
                .ok_or(anyhow!("Undefined table {}.", index_ref.table))?;
            let field = types
                .field(table.0, &table.1)
                .ok_or(anyhow!("Bad table entry {}.", index_ref.table))?;
            let rid = if let Field::List(list) = field {
                list.rid_from_index(index_ref.index)
            } else {
                None
            };

            // Write the rid to the reference.
            types
                .set_rid(index_ref.rid, &index_ref.id, rid)
                .context(format!("Bad reference {:?}", index_ref))?;
        }
        for key_ref in &self.key_refs {
            // Find the item's rid.
            let table = tables
                .get(&key_ref.table)
                .ok_or(anyhow!("Undefined table {}.", key_ref.table))?;
            let field = types
                .field(table.0, &table.1)
                .ok_or(anyhow!("Bad table entry {}.", key_ref.table))?;
            let rid = if let Field::List(list) = field {
                list.rid_from_key(&key_ref.key, types)
            } else {
                None
            };

            // Write the rid to the reference.
            types
                .set_rid(key_ref.rid, &key_ref.id, rid)
                .context(format!("Bad reference {:?}", key_ref))?;
            if types.rid(key_ref.rid, &key_ref.id).is_none() {
                println!("{:?}", key_ref);
            }
        }
        for field_ref in &self.field_refs {
            // Find the item's rid.
            let table = tables
                .get(&field_ref.table)
                .ok_or(anyhow!("Undefined table {}.", field_ref.table))?;
            let field = types
                .field(table.0, &table.1)
                .ok_or(anyhow!("Bad table entry {}.", field_ref.table))?;
            let rid = if let Field::List(list) = field {
                list.rid_from_int_field(field_ref.value, &field_ref.target_field, types)
            } else {
                None
            };

            // Write the rid to the reference.
            types
                .set_rid(field_ref.rid, &field_ref.id, rid)
                .context(format!("Bad reference {:?}", field_ref))?;
        }
        for pointer_ref in &self.pointer_refs {
            // Find the item's rid.
            let key = (pointer_ref.address, pointer_ref.table.clone());
            let rid = if let Some(rid) = self.known_records.get(&key) {
                Some(*rid)
            } else {
                None
            };

            // Write the rid to the reference.
            types
                .set_rid(pointer_ref.rid, &pointer_ref.id, rid)
                .context(format!("Bad reference {:?}", pointer_ref))?;
        }
        Ok(())
    }
}

impl<'a> WriteReferences<'a> {
    pub fn new(types: &'a Types, tables: &'a HashMap<String, (u64, String)>) -> Self {
        WriteReferences {
            types,
            tables,
            known_pointers: Vec::new(),
            known_records: HashMap::new(),
        }
    }

    pub fn resolve_index(&self, rid: u64, table: &str) -> Option<usize> {
        match self.tables.get(table) {
            Some((list_rid, id)) => {
                if let Some(Field::List(f)) = self.types.field(*list_rid, id) {
                    f.index_from_rid(rid)
                } else {
                    None
                }
            }
            None => None,
        }
    }

    pub fn resolve_field(&self, rid: u64, field: &str) -> Option<i64> {
        self.types.int(rid, field)
    }

    pub fn resolve_key(&self, rid: u64) -> Option<String> {
        self.types.key(rid)
    }

    pub fn add_known_pointer(&mut self, rid: u64, address: usize) {
        self.known_pointers.push((rid, address));
    }

    pub fn add_known_record(&mut self, rid: u64, address: usize) {
        self.known_records.insert(rid, address);
    }

    pub fn resolve_pointers(&self, writer: &mut BinArchiveWriter) -> anyhow::Result<()> {
        for (rid, source) in &self.known_pointers {
            match self.known_records.get(rid) {
                Some(dest) => {
                    writer.seek(*source);
                    writer.write_pointer(Some(*dest))?;
                }
                None => {}
            }
        }
        Ok(())
    }
}
