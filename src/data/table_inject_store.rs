use super::{CountStrategy, LocationStrategy, ReadOutput, ReadReferences, ReadState, Types};
use anyhow::{anyhow, Context};
use mila::{BinArchiveReader, LayeredFilesystem};
use serde::Deserialize;
use std::collections::HashMap;

#[derive(Deserialize)]
pub struct TableInjectStore {
    pub id: String,

    pub typename: String,

    pub filename: String,

    pub location_strategy: LocationStrategy,

    pub count_strategy: CountStrategy,

    #[serde(skip, default)]
    pub records: Vec<u64>,

    #[serde(skip, default)]
    pub dirty: bool,
}

impl TableInjectStore {
    pub fn create_instance_for_multi(
        typename: String,
        filename: String,
        dirty: bool,
        location_strategy: LocationStrategy,
        count_strategy: CountStrategy,
    ) -> Self {
        TableInjectStore {
            id: String::new(),
            typename,
            filename,
            location_strategy,
            count_strategy,
            records: Vec::new(),
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
        // Read the file.
        let archive = fs.read_archive(&self.filename, false)?;

        // Get the location and count.
        let table_address = self
            .location_strategy
            .apply(&archive)
            .context("Failed to locate table in the archive")?;
        let count = self
            .count_strategy
            .apply(&archive)
            .context("Failed to read table count.")?;

        // Read the table.
        self.records = Vec::new();
        let element_size = types
            .size_of(&self.typename)
            .ok_or(anyhow!("Type {} does not exist.", self.typename))?;
        for i in 0..count {
            // Read the next item.
            let reader = BinArchiveReader::new(&archive, table_address + i * element_size);
            let mut record = types
                .instantiate(&self.typename)
                .ok_or(anyhow!("Type {} does not exist.", self.typename))?;
            let mut state = ReadState::new(types, references, reader, self.id.clone(), Vec::new());
            record.read(&mut state).with_context(|| {
                format!(
                    "Failed to parse type {} from file {}",
                    self.typename, self.filename
                )
            })?;

            // Add it to the table.
            let rid = state.types.peek_next_rid();
            record.post_register_read(rid, &mut state);
            self.records.push(rid);
        }
        todo!()
    }

    pub fn write(
        &self,
        types: &Types,
        tables: &HashMap<String, (u64, String)>,
        fs: &LayeredFilesystem,
    ) -> anyhow::Result<()> {
        todo!()
    }
}
