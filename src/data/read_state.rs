use super::{NodeStoreContext, ReadReferences, Types, UINode};
use mila::BinArchiveReader;
use std::collections::{HashMap, HashSet};

pub struct ReadState<'a> {
    pub types: &'a mut Types,
    pub references: &'a mut ReadReferences,
    pub reader: BinArchiveReader<'a>,
    pub nodes: Vec<UINode>,
    pub tables: HashMap<String, (u64, String)>,
    pub address_stack: Vec<usize>,
    pub store_id: String,
    pub list_index: Vec<usize>,
    pub node_context: Option<NodeStoreContext>,

    // Caching info from the archive to avoid redundant
    // lookups during reading. The archive is already
    // immutable during this time, so we don't have to
    // worry about updates.
    pub pointer_destinations: HashSet<usize>,
}

impl<'a> ReadState<'a> {
    pub fn new(
        types: &'a mut Types,
        references: &'a mut ReadReferences,
        reader: BinArchiveReader<'a>,
        store_id: String,
        node_context: Option<NodeStoreContext>,
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
        }
    }
}
