use super::{Field, ReadState, Record, Types, WriteState};
use anyhow::anyhow;
use pyo3::types::PyDict;
use pyo3::{PyObject, PyResult, Python, ToPyObject};
use serde::Deserialize;

#[derive(Clone, Debug, Deserialize)]
#[serde(rename_all = "snake_case")]
enum Format {
    Inline,
    InlinePointer,
    Pointer,
    LabelAppend {
        label: String,

        #[serde(default)]
        offset: usize,
    },
    Append,
}

#[derive(Clone, Debug, Deserialize)]
pub struct RecordField {
    pub id: String,

    #[serde(default)]
    pub name: Option<String>,

    #[serde(default)]
    pub value: Option<u64>,

    #[serde(default)]
    pub defer_write: bool,

    format: Format,

    pub typename: String,
}

fn verify_not_none(record: &Option<&Record>) -> anyhow::Result<()> {
    match record {
        Some(_) => Ok(()),
        None => Err(anyhow!("Cannot write a none record for current format.")),
    }
}

impl RecordField {
    fn read_impl(&mut self, state: &mut ReadState) -> anyhow::Result<()> {
        // Read the record.
        let mut record = state
            .types
            .instantiate(&self.typename)
            .ok_or(anyhow!("Type {} is not defined.", self.typename))?;
        record.read(state)?;

        // Register the record with Types.
        let rid = state.types.peek_next_rid();
        record.post_register_read(rid, state);
        self.value = Some(state.types.register(record));
        Ok(())
    }

    pub fn read(&mut self, state: &mut ReadState) -> anyhow::Result<()> {
        match &self.format {
            Format::Inline => self.read_impl(state)?,
            Format::Pointer | Format::InlinePointer => match state.reader.read_pointer()? {
                Some(addr) => {
                    let end_address = state.reader.tell();
                    state.reader.seek(addr);
                    self.read_impl(state)?;
                    if let Format::Pointer = self.format {
                        state.reader.seek(end_address);
                    }
                }
                None => self.value = None,
            },
            Format::LabelAppend { label, offset } => {
                let address = state
                    .reader
                    .archive()
                    .find_label_address(label)
                    .ok_or(anyhow!("Label {} not found", label))?;
                state.reader.seek(address - offset);
                self.read_impl(state)?;
            }
            Format::Append => {
                // This format is only used for adding spacers.
                // Use default values to get all zeroes.
                let instance = state
                    .types
                    .instantiate(&self.typename)
                    .ok_or(anyhow!("Type {} is not defined.", self.typename))?;
                self.value = Some(state.types.register(instance));
            }
        }
        Ok(())
    }

    pub fn write_deferred_pointer(
        &self,
        address: usize,
        state: &mut WriteState,
    ) -> anyhow::Result<()> {
        // Get the type definition.
        let typedef = state
            .types
            .get(&self.typename)
            .ok_or(anyhow!("Type {} does not exist.", self.typename))?;

        match state.types.instance(self.value.unwrap()) {
            Some(v) => {
                // Write the pointer.
                let end_address = state.writer.tell();
                let dest = state.writer.size();
                state.writer.seek(address);
                state.writer.write_pointer(Some(dest))?;

                // Write the pointer data.
                state.writer.allocate_at_end(typedef.size);
                state.writer.seek(dest);
                v.write(state, self.value.unwrap())?;
                state.writer.seek(end_address);
            }
            None => {}
        }
        Ok(())
    }

    pub fn write(&self, state: &mut WriteState) -> anyhow::Result<()> {
        // Extract the record and type info from Types.
        let typedef = state
            .types
            .get(&self.typename)
            .ok_or(anyhow!("Type {} does not exist.", self.typename))?;
        let size = typedef.size;
        let record = if let Some(rid) = self.value {
            state.types.instance(rid)
        } else {
            None
        };

        // Note the amount of deferred pointers now so we know
        // which ones are associated with this record.
        let old_defer_count = state.deferred.len();

        // Write based on the format.
        match &self.format {
            Format::Inline => {
                verify_not_none(&record)?;
                state.writer.allocate(size)?;
                record.unwrap().write(state, self.value.unwrap())?;
            }
            Format::InlinePointer => {
                verify_not_none(&record)?;
                state.writer.allocate(size + 4)?; // Space for the record + the pointer.
                state.writer.write_pointer(Some(state.writer.tell() + 4))?; // Pointer to the space immediately after the pointer.
                record.unwrap().write(state, self.value.unwrap())?;
            }
            Format::Pointer => match record {
                Some(v) => {
                    if self.defer_write {
                        // Hit an exception where we need to wait for the record to finish writing
                        // the current record before allocating space for the pointer data.
                        state.deferred.push((
                            state.writer.tell(),
                            *state.rid_stack.last().unwrap(),
                            self.id.clone(),
                        ));
                        state.writer.skip(4);
                        return Ok(());
                    } else {
                        let dest = state.writer.size();
                        state.writer.allocate_at_end(typedef.size);
                        state.writer.write_pointer(Some(dest))?;
                        let end_address = state.writer.tell();
                        state.writer.seek(dest);
                        v.write(state, self.value.unwrap())?;
                        state.writer.seek(end_address);
                    }
                }
                None => state.writer.write_pointer(None)?,
            },
            Format::LabelAppend {
                label: _,
                offset: _,
            } => {
                verify_not_none(&record)?;
                let dest = state.writer.size();
                state.writer.allocate_at_end(size);
                state.writer.seek(dest);
                record.unwrap().write(state, self.value.unwrap())?;
            }
            Format::Append => {
                verify_not_none(&record)?;
                let dest = state.writer.size();
                state.writer.allocate_at_end(size);
                state.writer.seek(dest);
                record.unwrap().write(state, self.value.unwrap())?;
            }
        }

        // Write deferred pointers.
        let new_defer_count = state.deferred.len();
        for _ in old_defer_count..new_defer_count {
            let (address, rid, id) = state.deferred.remove(old_defer_count);
            match state.types.field(rid, &id) {
                Some(i) => match i {
                    Field::Record(r) => r.write_deferred_pointer(address, state),
                    _ => Err(anyhow!("None-record field in deferred pointers.")),
                },
                None => Err(anyhow!("Bad rid/id combo in deferred pointer.")),
            }?;
        }
        Ok(())
    }

    pub fn metadata(&self, py: Python) -> PyResult<PyObject> {
        let dict = PyDict::new(py);
        dict.set_item("type", "record")?;
        dict.set_item("id", self.id.clone())?;
        dict.set_item("name", self.name.clone())?;
        dict.set_item("stored_type", self.typename.clone())?;
        Ok(dict.to_object(py))
    }

    pub fn clone_with_allocations(&self, types: &mut Types) -> anyhow::Result<Field> {
        let mut clone = self.clone();
        match self.value {
            Some(rid) => {
                // For most record formats, the record it holds is unique.
                // Thus, we cannot produce a clone with an identical RID.
                // To fix this, we need to copy the record and give it a new
                // RID as well.
                let new_rid = types
                    .instantiate_and_register(&self.typename)
                    .ok_or(anyhow!("Type {} does not exist.", self.typename))?;
                types.copy(rid, new_rid, &Vec::new())?;
                clone.value = Some(new_rid);
            }
            None => {}
        }
        Ok(Field::Record(clone))
    }
}
