use std::collections::{HashMap, HashSet};

use crate::data::serialization::references::WriteReferences;
use crate::data::Types;
use mila::BinArchiveWriter;

use super::id::RecordId;

pub struct WriteState<'a> {
    /// The type system.
    /// Handles type information + instantiation.
    pub types: &'a Types,

    /// The write head.
    pub writer: BinArchiveWriter<'a>,

    /// Resolves references during writing.
    /// Also holds on to pointer information so pointer references
    /// can be resolved at the end of the operation.
    pub references: WriteReferences<'a>,

    /// Tracks the [RecordId] of every record being written.
    /// When a record write starts, its [RecordId] is pushed on to the stack.
    /// When the record write finishes, the [RecordId] is popped off.
    pub rid_stack: Vec<RecordId>,

    /// Tracks the starting address of every record being written.
    /// When a record write starts, the address is pushed on top of the stack.
    /// When the read write, it's popped off.
    /// This is primarily used for writing counts for the Indirect list format.
    pub address_stack: Vec<usize>,

    /// Tracks the index of the item being read in its parent list.
    /// Necessary for FE13 growth encoding since it relies on the character's index.
    pub list_index: Vec<usize>,

    pub deferred: Vec<(usize, RecordId, String)>,

    /// Cache that stores where shared pointers were written.
    pub shared_pointers: HashMap<RecordId, usize>,

    /// Cache of conditional flags to determine whether or not certain fields are present.
    pub conditions_stack: Vec<HashSet<String>>,
}

impl<'a> WriteState<'a> {
    pub fn new(
        types: &'a Types,
        references: WriteReferences<'a>,
        writer: BinArchiveWriter<'a>,
    ) -> Self {
        WriteState {
            types,
            writer,
            references,
            rid_stack: Vec::new(),
            address_stack: Vec::new(),
            list_index: Vec::new(),
            deferred: Vec::new(),
            shared_pointers: HashMap::new(),
            conditions_stack: Vec::new(),
        }
    }
}
