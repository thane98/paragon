use std::collections::HashMap;

use super::{ReadOutput, ReadReferences, ReadState, Types, WriteReferences, WriteState};
use anyhow::anyhow;
use mila::{BinArchive, BinArchiveReader, BinArchiveWriter, LayeredFilesystem};
use serde::Deserialize;

#[derive(Deserialize)]
pub struct SingleStore {
    pub id: String,

    pub typename: String,

    pub filename: String,

    #[serde(skip, default)]
    pub rid: Option<u64>,

    #[serde(skip, default)]
    pub dirty: bool,
}

impl SingleStore {
    pub fn read(
        &mut self,
        types: &mut Types,
        references: &mut ReadReferences,
        fs: &LayeredFilesystem,
    ) -> anyhow::Result<ReadOutput> {
        let archive = fs.read_archive(&self.filename, false)?;
        let mut record = types
            .instantiate(&self.typename)
            .ok_or(anyhow!("Type does not exist."))?;
        let mut state = ReadState::new(
            types,
            references,
            BinArchiveReader::new(&archive, 0),
            self.id.clone(),
        );
        record.read(&mut state)?;

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
        fs: &LayeredFilesystem,
    ) -> anyhow::Result<()> {
        match self.rid {
            Some(rid) => {
                let mut archive = BinArchive::new();
                match types.get(&self.typename) {
                    Some(td) => archive.allocate_at_end(td.size),
                    None => return Err(anyhow!("Undefined type {}.", self.typename)),
                }

                let references = WriteReferences::new(types, tables);
                let mut state =
                    WriteState::new(types, references, BinArchiveWriter::new(&mut archive, 0));
                if let Some(record) = types.instance(rid) {
                    record.write(&mut state, rid)?;
                    state.references.resolve_pointers(&mut state.writer)?;
                    fs.write_archive(&self.filename, &archive, false)?;
                }
            }
            None => {}
        }
        Ok(())
    }
}
