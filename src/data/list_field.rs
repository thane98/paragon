use super::{Field, ReadState, Types, WriteState};
use anyhow::anyhow;
use mila::{BinArchive, BinArchiveWriter};
use pyo3::types::PyDict;
use pyo3::{PyObject, PyResult, Python, ToPyObject};
use serde::Deserialize;

#[derive(Clone, Copy, Debug, Deserialize)]
#[serde(rename_all = "snake_case", tag = "type")]
enum CountFormat {
    U8,
    U16,
    U32,
}

#[derive(Clone, Debug, Deserialize)]
#[serde(rename_all = "snake_case", tag = "type")]
enum Format {
    Indirect {
        index: i64,
        offset: usize,
        format: CountFormat,
    },
    Static {
        count: usize,
    },
    PostfixCount {
        label: String,
    },
    AwakeningBMap,
}

#[derive(Clone, Debug, Deserialize)]
pub struct ListField {
    pub id: String,

    #[serde(default)]
    pub name: Option<String>,

    #[serde(default)]
    pub table: Option<String>,

    #[serde(default)]
    pub items: Vec<u64>,

    format: Format,

    pub typename: String,
}

fn read_count(archive: &BinArchive, address: usize, format: CountFormat) -> anyhow::Result<usize> {
    Ok(match format {
        CountFormat::U8 => archive.read_u8(address)? as usize,
        CountFormat::U16 => archive.read_u16(address)? as usize,
        CountFormat::U32 => archive.read_u32(address)? as usize,
    })
}

fn write_count(
    writer: &mut BinArchiveWriter,
    address: usize,
    count: usize,
    format: CountFormat,
) -> anyhow::Result<()> {
    let end_address = writer.tell();
    writer.seek(address);
    match format {
        CountFormat::U8 => writer.write_u8(count as u8)?,
        CountFormat::U16 => writer.write_u16(count as u16)?,
        CountFormat::U32 => writer.write_u32(count as u32)?,
    }
    writer.seek(end_address);
    Ok(())
}

fn align(operand: usize, alignment: usize) -> usize {
    (operand + (alignment - 1)) & !(alignment - 1)
}

impl ListField {
    pub fn read(&mut self, state: &mut ReadState) -> anyhow::Result<()> {
        // Read the count.
        let count = match &self.format {
            Format::Indirect {
                index,
                offset,
                format,
            } => {
                let index = ((state.address_stack.len() as i64) + index) as usize;
                let address = state.address_stack[index] + offset;
                read_count(state.reader.archive(), address, *format)?
            }
            Format::Static { count } => *count,
            Format::PostfixCount { label } => {
                let archive = state.reader.archive();
                let address = archive
                    .find_label_address(label)
                    .ok_or(anyhow!("Unable to find label '{}' in archive.", label))?;
                archive.read_u32(address)? as usize
            }
            Format::AwakeningBMap => {
                // TODO: This looks like a list, but I haven't been able to find out
                // where the count for it is stored. For now, this will "read" the count
                // by looking ahead until it hits either a pointer destination or a label.
                let archive = state.reader.archive();
                let dests = &state.pointer_destinations;
                let mut count = 0;
                let mut addr = state.reader.tell();
                while !dests.contains(&addr) && archive.read_labels(addr)?.is_none() {
                    count += 1;
                    addr += 4;
                }
                count
            }
        };

        // Read items.
        state.list_index.push(0);
        for _ in 0..count {
            let cur_list_index = state.list_index.len() - 1;
            state.list_index[cur_list_index] = self.items.len();

            let address = state.reader.tell();
            let mut record = state
                .types
                .instantiate(&self.typename)
                .ok_or(anyhow!("Type {} is not defined.", self.typename))?;
            record.read(state)?;

            let rid = state.types.peek_next_rid();
            record.post_register_read(rid, state);
            self.items.push(state.types.register(record));

            if let Some(table) = &self.table {
                state
                    .references
                    .add_known_record(address, table.clone(), rid);
            }
        }
        state.list_index.pop();
        Ok(())
    }

    pub fn post_register_read(&self, rid: u64, state: &mut ReadState) {
        if let Some(table) = &self.table {
            state.tables.insert(table.clone(), (rid, self.id.clone()));
        }
    }

    pub fn write(&self, state: &mut WriteState) -> anyhow::Result<()> {
        // Write count (for standard formats)
        match &self.format {
            Format::Indirect {
                index,
                offset,
                format,
            } => {
                let index = ((state.address_stack.len() as i64) + index) as usize;
                let address = state.address_stack[index] + offset;
                write_count(&mut state.writer, address, self.items.len(), *format)?;
            }
            _ => {}
        }

        let typedef = state
            .types
            .get(&self.typename)
            .ok_or(anyhow!("Type {} is not defined.", self.typename))?;
        let binary_count = align(self.items.len() * typedef.size, 4);
        state.writer.allocate(binary_count)?;
        state.list_index.push(0);
        for i in 0..self.items.len() {
            let cur_list_index = state.list_index.len() - 1;
            state.list_index[cur_list_index] = i;

            let rid = self.items[i];
            let item = state
                .types
                .instance(rid)
                .ok_or(anyhow!("Bad RID {}.", rid))?;
            item.write(state, rid)?;
        }
        state.list_index.pop();

        // Write count (for postfix)
        match &self.format {
            Format::PostfixCount { label } => {
                state.writer.seek(state.writer.length());
                state.writer.allocate_at_end(4);
                state.writer.write_label(label)?;
                state.writer.write_u32(self.items.len() as u32)?;
            }
            _ => {}
        }
        Ok(())
    }

    pub fn rid_from_index(&self, index: usize) -> Option<u64> {
        if index < self.items.len() {
            Some(self.items[index])
        } else {
            None
        }
    }

    pub fn rid_from_key(&self, key: &str, types: &Types) -> Option<u64> {
        for rid in &self.items {
            if let Some(record) = types.instance(*rid) {
                match record.key(types) {
                    Some(item_key) => {
                        if item_key == key {
                            return Some(*rid);
                        }
                    }
                    None => {}
                }
            }
        }
        None
    }

    pub fn index_from_rid(&self, rid: u64) -> Option<usize> {
        self.items.iter().position(|r| *r == rid)
    }

    pub fn insert(&mut self, rid: u64, index: usize) -> anyhow::Result<()> {
        if index > self.items.len() {
            return Err(anyhow!("Index {} is out of bounds.", index));
        }
        self.items.insert(index, rid);
        Ok(())
    }

    pub fn remove(&mut self, index: usize) -> anyhow::Result<()> {
        if index >= self.items.len() {
            return Err(anyhow!("Index {} is out of bounds.", index));
        }
        self.items.remove(index);
        Ok(())
    }

    pub fn swap(&mut self, a: usize, b: usize) -> anyhow::Result<()> {
        if a >= self.items.len() || b >= self.items.len() {
            return Err(anyhow!("Index {} {} is out of bounds.", a, b));
        }
        let tmp = self.items[a];
        self.items[a] = self.items[b];
        self.items[b] = tmp;
        Ok(())
    }

    pub fn metadata(&self, py: Python) -> PyResult<PyObject> {
        let dict = PyDict::new(py);
        dict.set_item("type", "list")?;
        dict.set_item("id", self.id.clone())?;
        dict.set_item("name", self.name.clone())?;
        dict.set_item("stored_type", self.typename.clone())?;
        Ok(dict.to_object(py))
    }

    pub fn clone_with_allocations(&self, types: &mut Types) -> anyhow::Result<Field> {
        let mut clone = self.clone();
        clone.items.clear();
        for rid in &self.items {
            let new_rid = types
                .instantiate_and_register(&self.typename)
                .ok_or(anyhow!("Type {} is not defined.", self.typename))?;
            types.copy(*rid, new_rid, &Vec::new())?;
            clone.items.push(new_rid);
        }
        Ok(Field::List(clone))
    }
}
