use std::collections::HashMap;

use anyhow::{anyhow, Context};
use mila::{BinArchiveReader, BinArchiveWriter, LayeredFilesystem};
use serde::Deserialize;

use crate::data::serialization::inject_count_strategy::CountStrategy;
use crate::data::serialization::inject_location_strategy::LocationStrategy;
use crate::data::serialization::references::{ReadReferences, WriteReferences};
use crate::data::Types;
use crate::model::read_output::ReadOutput;
use crate::model::read_state::ReadState;
use crate::model::ui_node::UINode;
use crate::model::write_state::WriteState;

#[derive(Deserialize, Debug)]
pub struct TableInjectStore {
    pub id: String,

    pub typename: String,

    pub filename: String,

    pub node_name: String,

    pub location_strategy: LocationStrategy,

    pub count_strategy: CountStrategy,

    #[serde(skip, default)]
    pub rid: Option<u64>,

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
            node_name: String::new(),
            location_strategy,
            count_strategy,
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
        let mut records = Vec::new();
        let element_size = types
            .size_of(&self.typename)
            .ok_or_else(|| anyhow!("Type {} does not exist.", self.typename))?;
        for i in 0..count {
            // Read the next item.
            let reader = BinArchiveReader::new(&archive, table_address + i * element_size);
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

            // Add it to the table.
            let rid = state.types.peek_next_rid();
            record.post_register_read(rid, &mut state);
            records.push(types.register(record));
        }

        // Synthesize a type for the table.
        let table_typename = types.define_simple_table(self.typename.clone());

        // Wrap the fields in an instance of the type.
        // We do this so the UI doesn't need to treat this store like a special case.
        let mut instance = types
            .instantiate(&table_typename)
            .ok_or_else(|| anyhow!("Type system did not register the table type."))?;
        instance
            .field_mut("table")
            .ok_or_else(|| anyhow!("Malformed inject table type."))?
            .set_items(records)
            .context("Failed to set items on inject table type.")?;

        // Register the wrapper.
        let rid = types.register(instance);
        self.rid = Some(rid);

        // Create the read output.
        let ui_node = UINode {
            id: format!("{}__{}", self.id, table_typename),
            name: self.node_name.clone(),
            rid,
            store: self.id.clone(),
        };
        let mut read_output = ReadOutput::new();
        read_output.nodes.push(ui_node);
        Ok(read_output)
    }

    pub fn write(
        &self,
        types: &Types,
        tables: &HashMap<String, (u64, String)>,
        fs: &LayeredFilesystem,
    ) -> anyhow::Result<()> {
        // Read the file.
        let mut archive = fs.read_archive(&self.filename, false)?;

        // Get the location and old count.
        let table_address = self
            .location_strategy
            .apply(&archive)
            .context("Failed to locate table in the archive")?;
        let count = self
            .count_strategy
            .apply(&archive)
            .context("Failed to read table count.")?;

        // Retrieve info we need to perform the write.
        let items = self
            .rid
            .map(|rid| types.instance(rid))
            .ok_or_else(|| anyhow!("Bad RID in inject table store"))?
            .and_then(|r| r.field("table"))
            .and_then(|f| f.items())
            .ok_or_else(|| anyhow!("Malformed inject table type."))?;
        let element_size = types
            .size_of(&self.typename)
            .ok_or_else(|| anyhow!("Type {} does not exist.", self.typename))?;

        // Either deallocate unused items in the table or
        // allocate space for new items.
        if items.len() > count {
            // We have new items, need to make space.
            let diff_in_bytes = (items.len() - count) * element_size;
            let start_address = table_address + element_size * count;
            archive
                .allocate(start_address, diff_in_bytes, true)
                .context("Failed to allocate space for new items.")?;
        } else if items.len() < count {
            // Items have been removed, deallocate unused space.
            let diff_in_bytes = (count - items.len()) * element_size;
            let start_address = table_address + element_size * items.len();
            archive
                .deallocate(start_address, diff_in_bytes, true)
                .context("Failed to deallocate unused items.")?;
        }

        // Write the table contents.
        self.count_strategy.write(&mut archive, items.len())?;
        let references = WriteReferences::new(types, tables);
        let mut state = WriteState::new(
            types,
            references,
            BinArchiveWriter::new(&mut archive, table_address),
        );
        for rid in items {
            let record = types
                .instance(rid)
                .ok_or_else(|| anyhow!("Bad RID in inject store."))?;
            record.write(&mut state, rid)?;
        }

        // Write the archive.
        fs.write_archive(&self.filename, &archive, false)?;
        Ok(())
    }
}
