use crate::data::archives::Archives;
use crate::data::fields::field::Field;
use crate::data::serialization::references::{ReadReferences, WriteReferences};
use crate::data::Types;
use crate::model::read_output::ReadOutput;
use crate::model::read_state::ReadState;
use crate::model::write_state::WriteState;
use anyhow::{anyhow, Context};
use mila::{BinArchive, BinArchiveReader, BinArchiveWriter, LayeredFilesystem};
use serde::Deserialize;
use std::collections::HashMap;

#[derive(Deserialize, Debug)]
pub struct CmpStore {
    pub id: String,

    pub typename: String,

    pub archive: String,

    pub filename: String,

    #[serde(skip, default)]
    pub rid: Option<u64>,

    #[serde(skip, default)]
    pub dirty: bool,
}

impl CmpStore {
    pub fn create_instance_for_multi(
        typename: String,
        archive: String,
        filename: String,
        dirty: bool,
    ) -> Self {
        CmpStore {
            id: String::new(),
            typename,
            archive,
            filename,
            rid: None,
            dirty,
        }
    }

    pub fn set_archive(&mut self, archive: String) {
        self.archive = archive;
    }

    pub fn dirty_files(&self) -> Vec<String> {
        if self.dirty {
            vec![self.archive.clone()]
        } else {
            Vec::new()
        }
    }

    pub fn read(
        &mut self,
        types: &mut Types,
        references: &mut ReadReferences,
        archives: &mut Archives,
        fs: &LayeredFilesystem,
    ) -> anyhow::Result<ReadOutput> {
        let raw_archive = archives.load_file(fs, &self.archive, &self.filename)?;
        let archive =
            mila::BinArchive::from_bytes(raw_archive, fs.endian()).with_context(|| {
                format!(
                    "Failed to deserialize bin archive from cmp '{}' file '{}'",
                    self.archive, self.filename
                )
            })?;
        let reader = BinArchiveReader::new(&archive, 0);

        let mut record = types
            .instantiate(&self.typename)
            .ok_or_else(|| anyhow!("Type {} does not exist.", self.typename))?;
        let mut state = ReadState::new(types, references, reader, self.id.clone(), Vec::new());
        record.read(&mut state).with_context(|| {
            format!(
                "Failed to parse type {} from file {}",
                self.typename, self.filename
            )
        })?;
        let rid = state.types.peek_next_rid();
        record.post_register_read(rid, &mut state);

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
        archives: &mut Archives,
        fs: &LayeredFilesystem,
    ) -> anyhow::Result<()> {
        if let Some(rid) = self.rid {
            let mut archive = BinArchive::new(fs.endian());
            if let Some(td) = types.get(&self.typename) {
                archive.allocate_at_end(td.size);
            }

            let references = WriteReferences::new(types, tables);
            let mut state =
                WriteState::new(types, references, BinArchiveWriter::new(&mut archive, 0));

            if let Some(record) = types.instance(rid) {
                record.write(&mut state, rid)?;
                state
                    .references
                    .resolve_pointers(&mut state.writer)
                    .context("Failed to resolve pointers during writing.")?;

                while !state.deferred.is_empty() {
                    let cpy = state.deferred.clone();
                    for (address, rid, id) in &cpy {
                        match state.types.field(*rid, id) {
                            Some(i) => match i {
                                Field::Record(r) => r.write_deferred_pointer(*address, &mut state),
                                _ => Err(anyhow!("None-record field in deferred pointers.")),
                            },
                            None => Err(anyhow!("Bad rid/id combo in deferred pointer.")),
                        }?;
                    }
                    state.deferred.drain(0..cpy.len());
                }

                let raw = archive
                    .serialize()
                    .context("Failed to serialize CMP archive.")?;
                archives.overwrite(&self.archive, &self.filename, raw)?;
            }
        }
        Ok(())
    }
}