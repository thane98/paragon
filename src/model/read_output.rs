use crate::model::ui_node::UINode;
use std::collections::HashMap;

use super::id::RecordId;

#[derive(Debug)]
pub struct ReadOutput {
    pub nodes: Vec<UINode>,
    pub tables: HashMap<String, (RecordId, String)>,
}

impl ReadOutput {
    pub fn new() -> Self {
        ReadOutput {
            nodes: Vec::new(),
            tables: HashMap::new(),
        }
    }

    pub fn merge(&mut self, other: ReadOutput) {
        self.nodes.extend(other.nodes);
        self.tables.extend(other.tables);
    }
}
