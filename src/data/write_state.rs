use super::{Types, WriteReferences};
use mila::BinArchiveWriter;

pub struct WriteState<'a> {
    // The type system.
    // Handles type information + instantiation.
    pub types: &'a Types,

    // The write head.
    pub writer: BinArchiveWriter<'a>,

    // Resolves references during writing.
    // Also holds on to pointer information so pointer references
    // can be resolved at the end of the operation.
    pub references: WriteReferences<'a>,

    // Tracks the RID of every record being written.
    // When a record write starts, its RID is pushed on to the stack.
    // When the record write finishes, the RID is popped off.
    pub rid_stack: Vec<u64>,

    // Tracks the starting address of every record being written.
    // When a record write starts, the address is pushed on top of the stack.
    // When the read write, it's popped off.
    // This is primarily used for writing counts for the Indirect list format.
    pub address_stack: Vec<usize>,

    // Tracks the index of the item being read in its parent list.
    // Necessary for FE13 growth encoding since it relies on the character's index.
    pub list_index: Vec<usize>,

    pub deferred: Vec<(usize, u64, String)>,
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
        }
    }
}
