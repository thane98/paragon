use std::collections::HashMap;

type RecordDiff = HashMap<String, DiffValue>;

pub enum DiffValue {
    Bool(bool),
    Bytes(Vec<u8>),
    Float(f32),
    Int(i64),
    Str(Option<String>),
    Record(RecordDiff),
    ListItemsByIndices {
        indices: Vec<usize>,
        items: Vec<RecordDiff>,
    },
    ListItemsByKeys {
        keys: Vec<String>,
        items: Vec<RecordDiff>,
    },
}
