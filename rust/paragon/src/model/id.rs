use pyo3::prelude::*;
use std::fmt::Debug;

/// Unique ID for a store.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, FromPyObject)]
pub struct StoreNumber(u32);

impl StoreNumber {
    pub fn increment(&mut self) {
        self.0 += 1;
    }
}

impl Default for StoreNumber {
    fn default() -> Self {
        Self(1)
    }
}

impl IntoPy<pyo3::PyObject> for StoreNumber {
    fn into_py(self, py: Python<'_>) -> pyo3::PyObject {
        self.0.into_py(py)
    }
}

/// Unique ID for a record within a store.
#[derive(Clone, Copy, Debug)]
pub struct RecordNumber(u32);

impl RecordNumber {
    pub fn increment(&mut self) {
        self.0 += 1;
    }
}

impl Default for RecordNumber {
    fn default() -> Self {
        Self(1)
    }
}

/// Unique ID for a record.
/// This is a combination of a [StoreNumber] and [RecordNumber].
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, FromPyObject)]
pub struct RecordId(pub(crate) u64);

impl RecordId {
    /// Create a RecordId from a store number and record number.
    pub fn new(store_number: StoreNumber, record_number: RecordNumber) -> Self {
        Self(((store_number.0 as u64) << 32) + record_number.0 as u64)
    }

    /// Retrieve the record ID's [StoreNumber].
    pub fn store_number(&self) -> StoreNumber {
        StoreNumber((self.0 >> 32) as u32)
    }

    /// Retrieve the record ID's [RecordNumber].
    pub fn record_number(&self) -> RecordNumber {
        RecordNumber((self.0 & 0xFFFFFFFF) as u32)
    }

    pub fn with_store_number(&self, store_number: StoreNumber) -> Self {
        Self::new(store_number, self.record_number())
    }
}

impl std::fmt::Display for RecordId {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        Debug::fmt(&self, f)
    }
}

impl IntoPy<pyo3::PyObject> for RecordId {
    fn into_py(self, py: Python<'_>) -> pyo3::PyObject {
        self.0.into_py(py)
    }
}
