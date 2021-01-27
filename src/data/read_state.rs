use super::{ReadReferences, Types, UINode};
use mila::BinArchiveReader;
use std::collections::HashMap;

pub struct ReadState<'a> {
    pub types: &'a mut Types,
    pub references: &'a mut ReadReferences,
    pub reader: BinArchiveReader<'a>,
    pub nodes: Vec<UINode>,
    pub tables: HashMap<String, (u64, String)>,
    pub address_stack: Vec<usize>,
    pub store_id: String,
}

impl<'a> ReadState<'a> {
    pub fn new(
        types: &'a mut Types,
        references: &'a mut ReadReferences,
        reader: BinArchiveReader<'a>,
        store_id: String,
    ) -> Self {
        ReadState {
            types,
            references,
            reader,
            nodes: Vec::new(),
            tables: HashMap::new(),
            address_stack: Vec::new(),
            store_id,
        }
    }
}
