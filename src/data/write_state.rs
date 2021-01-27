use super::{Types, WriteReferences};
use mila::BinArchiveWriter;

pub struct WriteState<'a> {
    pub types: &'a Types,
    pub writer: BinArchiveWriter<'a>,
    pub references: WriteReferences<'a>,
    pub rid_stack: Vec<u64>,
    pub address_stack: Vec<usize>,
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
        }
    }
}
