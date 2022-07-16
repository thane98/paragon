use std::collections::BTreeSet;

use crate::data::fields::field::Field;
use crate::data::Types;
use crate::model::id::{RecordId, StoreNumber};
use crate::model::read_state::ReadState;
use crate::model::write_state::WriteState;
use anyhow::anyhow;
use mila::{BinArchive, BinArchiveWriter};
use pyo3::types::PyDict;
use pyo3::{PyObject, PyResult, Python, ToPyObject};
use serde::Deserialize;

#[derive(Clone, Copy, Debug, Deserialize)]
#[serde(rename_all = "snake_case")]
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

        #[serde(default)]
        doubled: bool,
    },
    Static {
        count: usize,
    },
    PostfixCount {
        label: String,
    },
    LabelOrDestTerminated {
        step_size: usize,
        #[serde(default)]
        skip_first: bool,
    },
    FatesAi,
    NullTerminated {
        #[serde(default)]
        peak: Option<usize>,
        step_size: usize,
    },
    All {
        divisor: usize,
    },
    CountIncomingPointersUntilLabel {
        label: String,
    },
    Fake,
    FromLabels {
        label: String,
    },
    FromLabelsIndexed {
        start_index: usize,
    },
}

#[derive(Clone, Debug, Deserialize)]
pub struct ListField {
    pub id: String,

    #[serde(default)]
    pub name: Option<String>,

    #[serde(default)]
    pub table: Option<String>,

    #[serde(skip, default)]
    pub items: Vec<RecordId>,

    #[serde(default)]
    pub allocate_individual: bool,

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
    pub fn create_table_container(typename: String) -> Self {
        ListField {
            id: "table".to_string(),
            name: None,
            table: None,
            items: Vec::new(),
            allocate_individual: false,
            format: Format::Fake,
            typename,
        }
    }

    pub fn is_non_sequential_format(&self) -> bool {
        matches!(
            &self.format,
            Format::Fake
                | Format::FromLabels { label: _ }
                | Format::FromLabelsIndexed { start_index: _ }
        )
    }

    pub fn enumerate_item_addresses(&self, state: &ReadState) -> anyhow::Result<BTreeSet<usize>> {
        Ok(match &self.format {
            Format::Fake => match &self.table {
                Some(t) => state.references.pointers_to_table(t),
                None => {
                    return Err(anyhow!("Fake list type requires table to be set."));
                }
            },
            Format::FromLabels { label } => state
                .reader
                .archive()
                .all_labels()
                .into_iter()
                .filter(|(_, l)| l.starts_with(label))
                .map(|(a, _)| a)
                .collect(),
            Format::FromLabelsIndexed { start_index } => {
                let labels = state.reader.archive().all_labels();
                if labels.len() <= *start_index {
                    return Err(anyhow!("Start index for list '{}' out of bounds", self.id));
                } else {
                    labels[*start_index..labels.len()]
                        .iter()
                        .map(|a| a.0)
                        .collect()
                }
            }
            _ => BTreeSet::new(),
        })
    }

    pub fn read(&mut self, state: &mut ReadState) -> anyhow::Result<()> {
        // Read the count.
        let count = match &self.format {
            Format::Indirect {
                index,
                offset,
                format,
                doubled: _,
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
                    .ok_or_else(|| anyhow!("Unable to find label '{}' in archive.", label))?;
                archive.read_u32(address)? as usize
            }
            Format::LabelOrDestTerminated {
                step_size,
                skip_first,
            } => {
                // This is used for formats where the count cannot be determined conventionally.
                // Usually means we're missing something about the format, so this is a hack.
                // Determine count by walking until we hit a label or pointer dest.
                let archive = state.reader.archive();
                let dests = &state.pointer_destinations;
                let mut count = if *skip_first { 1 } else { 0 };
                let mut addr = if *skip_first {
                    state.reader.tell() + step_size
                } else {
                    state.reader.tell()
                };
                while !dests.contains(&addr) && archive.read_labels(addr)?.is_none() {
                    count += 1;
                    addr += step_size;
                }
                count
            }
            Format::FatesAi => {
                // TODO: Another weird setup where the count hasn't been found yet.
                //       Walk forward until we find a terminating sequence.
                let end = state.reader.tell();
                let mut count = 1;
                let mut next = state.reader.read_u32()?;
                while next != 0x80000000 {
                    count += 1;
                    state.reader.skip(8);
                    next = state.reader.read_u32()?;
                }
                state.reader.seek(end);
                count
            }
            Format::NullTerminated { peak, step_size } => {
                let end = state.reader.tell();
                let mut count = 0;
                loop {
                    let bytes = if let Some(size) = peak {
                        state.reader.read_bytes(*size)?
                    } else {
                        state.reader.read_bytes(*step_size)?
                    };
                    if bytes.into_iter().filter(|b| *b != 0).count() == 0 {
                        break;
                    }
                    count += 1;
                    if let Some(size) = peak {
                        state.reader.skip(*step_size - *size);
                    }
                }
                state.reader.seek(end);
                count
            }
            Format::All { divisor } => state.reader.archive().size() / divisor,
            Format::CountIncomingPointersUntilLabel { label } => {
                if let Some(end) = state.reader.archive().find_label_address(label) {
                    let dests = &state.pointer_destinations;
                    let start = state.reader.tell();
                    dests.iter().filter(|a| (start..end).contains(*a)).count()
                } else {
                    return Err(anyhow!(
                        "List format requires label '{}' which isn't present.",
                        label
                    ));
                }
            }
            Format::Fake => {
                if let Some(table) = &self.table {
                    state.references.pointers_to_table(table).len()
                } else {
                    return Err(anyhow!("Fake list type requires table to be set."));
                }
            }
            Format::FromLabels { label } => state
                .reader
                .archive()
                .all_labels()
                .into_iter()
                .filter(|(_, l)| l.starts_with(label))
                .count(),
            Format::FromLabelsIndexed { start_index } => {
                state.reader.archive().all_labels().len() - start_index
            }
        };

        // Read items.
        state.list_index.push(0);
        let mut item_addresses = self.enumerate_item_addresses(state)?.into_iter();
        for _ in 0..count {
            let cur_list_index = state.list_index.len() - 1;
            state.list_index[cur_list_index] = self.items.len();

            // For non-sequential lists, the items could be scattered throughout the archive.
            // So, we need to seek to each one individually.
            if self.is_non_sequential_format() {
                state.reader.seek(item_addresses.next().ok_or_else(|| {
                    anyhow::anyhow!("Ran out of addresses while reading non-sequential list.")
                })?);
            }

            // Read the item.
            let address = state.reader.tell();
            let mut record = state
                .types
                .instantiate(&self.typename)
                .ok_or_else(|| anyhow!("Type {} is not defined.", self.typename))?;
            record.read(state)?;

            // Register the item with the type system.
            let rid = state.types.peek_next_rid(state.store_number);
            record.post_register_read(rid, state);
            self.items.push(state.types.register(record, state.store_number));

            // If we're a table, make sure references know where
            // to find the current item.
            if let Some(table) = &self.table {
                state
                    .references
                    .add_known_record(address, table.clone(), rid);
            }
        }
        if let Format::NullTerminated { peak, step_size } = &self.format {
            state.reader.skip(match peak {
                Some(size) => *size,
                None => *step_size,
            });
        }
        state.list_index.pop();
        Ok(())
    }

    pub fn post_register_read(&self, rid: RecordId, state: &mut ReadState) {
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
                doubled,
            } => {
                let index = ((state.address_stack.len() as i64) + index) as usize;
                let address = state.address_stack[index] + offset;
                write_count(&mut state.writer, address, self.items.len(), *format)?;
                if *doubled {
                    let address = address
                        + match *format {
                            CountFormat::U8 => 1,
                            CountFormat::U16 => 2,
                            CountFormat::U32 => 4,
                        };
                    write_count(&mut state.writer, address, self.items.len(), *format)?;
                }
            }
            _ => {}
        }

        // Allocate space for the list.
        // For null terminated lists, also allocate a null element at the end.
        let typedef = state
            .types
            .get(&self.typename)
            .ok_or_else(|| anyhow!("Type {} is not defined.", self.typename))?;

        // By default, allocate space for the entire list at once.
        // This is the only method available for null terminated lists.
        if !self.allocate_individual {
            let mut binary_count = align(self.items.len() * typedef.size, 4);
            if let Format::NullTerminated { peak, step_size } = &self.format {
                binary_count += if let Some(size) = peak {
                    *size
                } else {
                    *step_size
                };
            }
            state.writer.allocate(binary_count, false)?;
        }

        state.list_index.push(0);
        let length = if let Format::Static { count } = self.format.clone() {
            count
        } else {
            self.items.len()
        };
        for i in 0..length {
            if i > self.items.len() {
                return Err(anyhow!(
                    "List is of size {} expected {}",
                    length,
                    self.items.len()
                ));
            }

            // If using allocate individual, we allocate space for
            // each item when we write.
            // This is useful if the list contains fields with
            // lists to avoid expensive shifting.
            if self.allocate_individual {
                let binary_count = align(typedef.size, 4);
                state.writer.allocate(binary_count, false)?;
            }

            // Write the item.
            let cur_list_index = state.list_index.len() - 1;
            state.list_index[cur_list_index] = i;

            let rid = self.items[i];
            let item = state
                .types
                .instance(rid)
                .ok_or_else(|| anyhow!("Bad RID {}.", rid))?;
            item.write(state, rid)?;
        }
        state.list_index.pop();

        // Post-write operations based on list format.
        match &self.format {
            Format::PostfixCount { label } => {
                // Write the count.
                state.writer.seek(state.writer.length());
                state.writer.allocate_at_end(4);
                state.writer.write_label(label)?;
                state.writer.write_u32(self.items.len() as u32)?;
            }
            Format::NullTerminated { peak, step_size } => {
                // Skip to the end of the list.
                if let Some(size) = peak {
                    state.writer.skip(*size);
                } else {
                    state.writer.skip(*step_size);
                }
            }
            _ => {}
        }
        Ok(())
    }

    pub fn rid_from_index(&self, index: usize) -> Option<RecordId> {
        if index < self.items.len() {
            Some(self.items[index])
        } else {
            None
        }
    }

    pub fn rid_from_key(&self, key: &str, types: &Types) -> Option<RecordId> {
        for rid in &self.items {
            match types.key(*rid) {
                Some(item_key) => {
                    if item_key == key {
                        return Some(*rid);
                    }
                }
                None => {}
            }
        }
        None
    }

    pub fn rid_from_int_field(&self, target: i64, id: &str, types: &Types) -> Option<RecordId> {
        for rid in &self.items {
            if let Some(value) = types.int(*rid, id) {
                if value == target {
                    return Some(*rid);
                }
            }
        }
        None
    }

    pub fn index_from_rid(&self, rid: RecordId) -> Option<usize> {
        self.items.iter().position(|r| *r == rid)
    }

    pub fn get(&self, index: usize) -> anyhow::Result<RecordId> {
        if index > self.items.len() {
            return Err(anyhow!("Index {} is out of bounds.", index));
        }
        Ok(self.items[index])
    }

    pub fn insert(&mut self, rid: RecordId, index: usize) -> anyhow::Result<()> {
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
        self.items.swap(a, b);
        Ok(())
    }

    pub fn metadata(&self, py: Python) -> PyResult<PyObject> {
        let dict = PyDict::new(py);
        dict.set_item("type", "list")?;
        dict.set_item("id", self.id.clone())?;
        dict.set_item("name", self.name.clone())?;
        dict.set_item("stored_type", self.typename.clone())?;
        if let Format::Static { count } = self.format.clone() {
            dict.set_item("fixed_size", count)?;
        }
        Ok(dict.to_object(py))
    }

    pub fn clone_with_allocations(&self, types: &mut Types, store_number: StoreNumber) -> anyhow::Result<Field> {
        let mut clone = self.clone();
        clone.items.clear();
        for rid in &self.items {
            let new_rid = types
                .instantiate_and_register(&self.typename, store_number)
                .ok_or_else(|| anyhow!("Type {} is not defined.", self.typename))?;
            types.copy(*rid, new_rid, &Vec::new())?;
            clone.items.push(new_rid);
        }
        Ok(Field::List(clone))
    }
}
