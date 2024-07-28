use std::collections::{BTreeMap, HashMap};

use crate::model::script_analysis_result::DiagnosticLocation;

#[derive(Default)]
pub struct Utf16DiagnosticMap {
    line_start_indices: BTreeMap<usize, usize>,
    utf8_to_utf16_indices: HashMap<usize, usize>,
}

impl Utf16DiagnosticMap {
    pub fn from_source(source: &str) -> Self {
        let mut current_line_number = 1;
        let mut line_start_indices = BTreeMap::new();
        line_start_indices.insert(0, current_line_number);
        let mut utf8_to_utf16_indices = HashMap::new();
        utf8_to_utf16_indices.reserve(source.len());
        for (utf16_index, (utf8_index, character)) in source.char_indices().enumerate() {
            utf8_to_utf16_indices.insert(utf8_index, utf16_index);
            if character == '\n' {
                // Line starts AFTER the newline
                current_line_number += 1;
                line_start_indices.insert(utf8_index + 1, current_line_number);
            }
        }
        Self {
            line_start_indices,
            utf8_to_utf16_indices,
        }
    }

    pub fn get_location(
        &self,
        file: String,
        start: usize,
        end: usize,
    ) -> Option<DiagnosticLocation> {
        // TODO: Does this work if the start index is a key in the map?
        let (line_start_index, line_number) =
            self.line_start_indices
                .range(..=start)
                .next_back()
                .map(|(line_start_index, line)| (*line_start_index, *line))?;
        let start_index = *self.utf8_to_utf16_indices.get(&start)?;
        let end_index = *self.utf8_to_utf16_indices.get(&end)?;
        Some(DiagnosticLocation {
            file: Some(file),
            span: (start_index, end_index),
            line_number,
            index_in_line: self
                .utf8_to_utf16_indices
                .get(&start.saturating_sub(line_start_index))
                .copied()
                .unwrap_or(0),
        })
    }
}
