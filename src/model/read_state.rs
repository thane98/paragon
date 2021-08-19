use crate::data::serialization::references::ReadReferences;
use crate::data::Types;
use crate::model::ui_node::{NodeStoreContext, UINode};
use mila::BinArchiveReader;
use std::collections::{HashMap, HashSet};

pub struct ReadState<'a> {
    // The type system.
    // Handles type information + instantiation.
    pub types: &'a mut Types,

    // Tracks references to tables.
    // Since the tables may not have been read when the reference is encountered,
    // this will handle resolving references when all reads have finished.
    pub references: &'a mut ReadReferences,

    // The read head.
    pub reader: BinArchiveReader<'a>,

    // Tracks every UI node encountered during this read operation.
    pub nodes: Vec<UINode>,

    // Tracks every table encountered during this read operation.
    pub tables: HashMap<String, (u64, String)>,

    // Tracks the starting address of every record being read.
    // When a record read starts, the address is pushed on top of the stack.
    // When the read finishes, it's popped off.
    // This is primarily used for reading counts for the Indirect list format.
    pub address_stack: Vec<usize>,

    // The store which is managing this read operation.
    pub store_id: String,

    // Tracks the index of the item being read in its parent list.
    // Necessary for FE13 growth decoding since it relies on the character's index.
    pub list_index: Vec<usize>,

    // Information for use during node generation.
    // This is used to make unique UI nodes from the same type.
    pub node_context: Vec<NodeStoreContext>,

    // Caching info from the archive to avoid redundant
    // lookups during reading. The archive is already
    // immutable during this time, so we don't have to
    // worry about updates.
    pub pointer_destinations: HashSet<usize>,

    // Cache of known shared pointers and their RIDs.
    pub shared_pointers: HashMap<usize, u64>,

    // Conditions cache. Used to store flags for whether or not specific fields are present.
    pub conditions_stack: Vec<HashSet<String>>,
}

impl<'a> ReadState<'a> {
    pub fn new(
        types: &'a mut Types,
        references: &'a mut ReadReferences,
        reader: BinArchiveReader<'a>,
        store_id: String,
        node_context: Vec<NodeStoreContext>,
    ) -> Self {
        let pointer_destinations = reader.archive().pointer_destinations();
        ReadState {
            types,
            references,
            reader,
            nodes: Vec::new(),
            tables: HashMap::new(),
            address_stack: Vec::new(),
            store_id,
            pointer_destinations,
            list_index: Vec::new(),
            node_context,
            shared_pointers: HashMap::new(),
            conditions_stack: Vec::new(),
        }
    }
}
