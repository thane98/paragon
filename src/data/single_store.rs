use super::{
    Field, NodeStoreContext, ReadOutput, ReadReferences, ReadState, Types, WriteReferences,
    WriteState,
};
use anyhow::{anyhow, Context};
use mila::{BinArchive, BinArchiveReader, BinArchiveWriter, LayeredFilesystem};
use serde::Deserialize;
use std::collections::HashMap;
use std::str::FromStr;

#[derive(Deserialize, Debug)]
pub struct SingleStore {
    pub id: String,

    pub typename: String,

    pub filename: String,

    #[serde(default)]
    pub truncate_to: Option<String>,

    #[serde(default)]
    pub language: Option<String>,

    #[serde(default)]
    pub node_context: Option<NodeStoreContext>,

    #[serde(skip, default)]
    pub rid: Option<u64>,

    #[serde(skip, default)]
    pub dirty: bool,
}

impl SingleStore {
    pub fn create_instance_for_multi(typename: String, filename: String, dirty: bool) -> Self {
        SingleStore {
            id: String::new(),
            typename,
            filename,
            truncate_to: None,
            language: None,
            node_context: None,
            rid: None,
            dirty,
        }
    }

    pub fn set_filename(&mut self, filename: String) {
        self.filename = filename;
    }

    pub fn dirty_files(&self) -> Vec<String> {
        if self.dirty {
            vec![self.filename.clone()]
        } else {
            Vec::new()
        }
    }

    pub fn read(
        &mut self,
        types: &mut Types,
        references: &mut ReadReferences,
        fs: &LayeredFilesystem,
    ) -> anyhow::Result<ReadOutput> {
        // Check if this store is language-specific.
        // Exit early if it is.
        if let Some(language) = &self.language {
            let language = mila::Language::from_str(language)?;
            if fs.language() != language {
                return Ok(ReadOutput::new());
            }
        }

        // Read the file.
        let archive = fs.read_archive(&self.filename, false)?;

        // Instantiate the type and try parsing it from the file.
        let mut record = types
            .instantiate(&self.typename)
            .ok_or(anyhow!("Type {} does not exist.", self.typename))?;
        let node_context: Vec<NodeStoreContext> = if let Some(context) = &self.node_context {
            vec![context.clone()]
        } else {
            Vec::new()
        };

        // Create the reader. seek forward if truncating.
        let mut reader = BinArchiveReader::new(&archive, 0);
        if let Some(label) = &self.truncate_to {
            let address = archive.find_label_address(label).ok_or(anyhow!(
                "Cannot truncate because label {} does not exist.",
                label
            ))?;
            reader.seek(address);
        }

        let mut state = ReadState::new(types, references, reader, self.id.clone(), node_context);
        record.read(&mut state).with_context(|| {
            format!(
                "Failed to parse type {} from file {}",
                self.typename, self.filename
            )
        })?;

        // Post read: register the type with the type system.
        // Need to wait until after reading for this due to
        // borrow checker constraints.
        let rid = state.types.peek_next_rid();
        record.post_register_read(rid, &mut state);

        // Forward all nodes and tables we found to the caller.
        let mut result = ReadOutput::new();
        result.nodes = state.nodes;
        result.tables = state.tables;
        self.rid = Some(types.register(record));
        Ok(result)
    }

    pub fn write(
        &self,
        types: &Types,
        tables: &HashMap<String, (u64, String)>,
        fs: &LayeredFilesystem,
    ) -> anyhow::Result<()> {
        match self.rid {
            Some(rid) => {
                let mut archive = if let Some(label) = &self.truncate_to {
                    let mut archive = fs.read_archive(&self.filename, false)?;
                    let address = archive.find_label_address(label).ok_or(anyhow!(
                        "Cannot truncate because label {} does not exist.",
                        label
                    ))?;
                    archive.truncate(address)?;
                    archive
                } else {
                    BinArchive::new(fs.endian())
                };
                let start_address = archive.size();
                match types.get(&self.typename) {
                    Some(td) => archive.allocate_at_end(td.size),
                    None => return Err(anyhow!("Undefined type {}.", self.typename)),
                }

                let references = WriteReferences::new(types, tables);
                let mut state = WriteState::new(
                    types,
                    references,
                    BinArchiveWriter::new(&mut archive, start_address),
                );
                if let Some(record) = types.instance(rid) {
                    record.write(&mut state, rid)?;
                    state
                        .references
                        .resolve_pointers(&mut state.writer)
                        .context("Failed to resolve pointers during writing.")?;

                    // Might have pointers that are queued to write. Handle them here.
                    while !state.deferred.is_empty() {
                        let cpy = state.deferred.clone();
                        for (address, rid, id) in &cpy {
                            match state.types.field(*rid, &id) {
                                Some(i) => match i {
                                    Field::Record(r) => {
                                        r.write_deferred_pointer(*address, &mut state)
                                    }
                                    _ => Err(anyhow!("None-record field in deferred pointers.")),
                                },
                                None => Err(anyhow!("Bad rid/id combo in deferred pointer.")),
                            }?;
                        }
                        state.deferred.drain(0..cpy.len());
                    }

                    fs.write_archive(&self.filename, &archive, false)?;
                }
            }
            None => {}
        }
        Ok(())
    }
}
