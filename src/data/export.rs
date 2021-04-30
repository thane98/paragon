use pyo3::prelude::*;

use crate::GameData;

#[pyclass]
pub struct ExportNodeWrapper {
    node: ExportNode,
}

pub enum ExportNode {
    RecordNode(u64),
    FieldNode(u64, String),
    SingleStoreNode(String),
    MultiStoreNode(String, String),
}

impl Into<ExportNodeWrapper> for ExportNode {
    fn into(self) -> ExportNodeWrapper {
        ExportNodeWrapper {
            node: self
        }
    }
}

impl ExportNode {
    pub fn get_children(&self, gd: GameData) -> Vec<ExportNodeWrapper> {
        todo!()
    }
}
