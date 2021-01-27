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
    LabelAppend { label: String },
}

#[derive(Clone, Debug, Deserialize)]
pub struct RecordField {
    pub id: String,

    #[serde(default)]
    pub name: Option<String>,

    #[serde(default)]
    pub value: Option<u64>,

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
        //println!("Name: {}, Address: 0x{:X}", self.id, state.reader.tell());
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
            Format::LabelAppend { label } => {
                let address = state
                    .reader
                    .archive()
                    .find_label_address(label)
                    .ok_or(anyhow!("Label {} not found", label))?;
                state.reader.seek(address);
                self.read_impl(state)?;
            }
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
                    let dest = state.writer.size();
                    state.writer.write_pointer(Some(dest))?;
                    let end_address = state.writer.tell();
                    state.writer.seek(dest);
                    v.write(state, self.value.unwrap())?;
                    state.writer.seek(end_address);
                }
                None => state.writer.write_pointer(None)?,
            },
            Format::LabelAppend { label: _ } => {
                verify_not_none(&record)?;
                let dest = state.writer.size();
                state.writer.allocate_at_end(size);
                state.writer.seek(dest);
                record.unwrap().write(state, self.value.unwrap())?;
            }
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
