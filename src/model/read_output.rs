use std::collections::HashMap;
use crate::model::ui_node::UINode;

#[derive(Debug)]
pub struct ReadOutput {
    pub nodes: Vec<UINode>,
    pub tables: HashMap<String, (u64, String)>,
}

impl ReadOutput {
    pub fn new() -> Self {
        ReadOutput {
            nodes: Vec::new(),
            tables: HashMap::new(),
        }
    }

    pub fn merge(&mut self, other: ReadOutput) {
        self.nodes.extend(other.nodes.into_iter());
        self.tables.extend(other.tables.into_iter());
    }
}
