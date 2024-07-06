use crate::data::fields::field::Field;
use crate::data::{TypeDefinition, Types};
use crate::model::id::{RecordId, StoreNumber};
use crate::model::read_state::ReadState;
use crate::model::write_state::WriteState;
use anyhow::{anyhow, Context};
use indexmap::IndexMap;
use std::collections::HashSet;

#[derive(Debug, Clone)]
pub struct Record {
    typename: String,
    fields: IndexMap<String, Field>,
}

impl Record {
    pub fn new(name: String, definition: &TypeDefinition) -> Self {
        let mut fields = IndexMap::new();
        for field in definition.get_fields() {
            fields.insert(field.id().to_string(), field.clone());
        }
        Record {
            typename: name,
            fields,
        }
    }

    pub fn copy_to(
        &self,
        other: &mut Record,
        fields: &[String],
        types: &mut Types,
        destination_store_number: StoreNumber,
    ) -> anyhow::Result<()> {
        if self.typename != other.typename {
            return Err(anyhow!(
                "Cannot copy between different types: {} {}.",
                self.typename,
                other.typename
            ));
        }
        let typedef = types
            .get(self.typename())
            .ok_or_else(|| anyhow!("Type '{}' does not exist.", self.typename()))?;
        let mut fields: HashSet<String> = if !fields.is_empty() {
            fields.iter().cloned().collect()
        } else {
            self.fields
                .keys()
                .filter(|s| !typedef.ignore_for_copy.contains(*s))
                .cloned()
                .collect()
        };
        if let Some(id) = &typedef.index {
            fields.remove(id);
        }

        let old_fields = other.fields.clone();
        other.fields.clear();
        for (k, v) in old_fields.into_iter() {
            if fields.contains(&k) {
                let field_clone = self
                    .fields
                    .get(&k)
                    .unwrap()
                    .clone_with_allocations(types, destination_store_number)?;
                other.fields.insert(k, field_clone);
            } else {
                other.fields.insert(k, v);
            }
        }
        Ok(())
    }

    pub fn typename(&self) -> &str {
        &self.typename
    }

    pub fn field(&self, id: &str) -> Option<&Field> {
        self.fields.get(id)
    }

    pub fn field_mut(&mut self, id: &str) -> Option<&mut Field> {
        self.fields.get_mut(id)
    }

    pub fn read(&mut self, state: &mut ReadState) -> anyhow::Result<()> {
        let typename = self.typename.clone();
        state.address_stack.push(state.reader.tell());
        state.conditions_stack.push(HashSet::new());
        for (k, v) in &mut self.fields {
            v.read(state).with_context(|| {
                format!(
                    "Failed to read typename '{}' field '{}' at address '0x{:X}",
                    typename,
                    k,
                    state.reader.tell()
                )
            })?;
        }
        state.address_stack.pop();
        state.conditions_stack.pop();
        Ok(())
    }

    pub fn post_register_read(&self, rid: RecordId, state: &mut ReadState) {
        if let Some(td) = state.types.get(self.typename()) {
            if let Some(node) = &td.node {
                let mut node = node.clone();
                if let Some(context) = &state.node_context.last() {
                    node.id = format!("{}{}", node.id, context.id_suffix);
                    node.name = format!("{}{}", node.name, context.name_suffix);
                }
                node.rid = Some(rid);
                node.store.clone_from(&state.store_id);
                state.nodes.push(node);
            }
        }
        for (_, v) in &self.fields {
            v.post_register_read(rid, state);
        }
    }

    pub fn write(&self, state: &mut WriteState, rid: RecordId) -> anyhow::Result<()> {
        state.address_stack.push(state.writer.tell());
        state.conditions_stack.push(HashSet::new());
        state.rid_stack.push(rid);
        state.references.add_known_record(rid, state.writer.tell());
        for (k, v) in &self.fields {
            v.write(state).with_context(|| {
                format!(
                    "Failed to write typename '{}' field '{}' at address '0x{:X}'",
                    self.typename,
                    k,
                    state.writer.tell()
                )
            })?;
        }
        state.address_stack.pop();
        state.conditions_stack.pop();
        state.rid_stack.pop();
        Ok(())
    }

    pub fn string(&self, id: &str) -> Option<String> {
        match self.field(id) {
            Some(field) => field.string_value().map(String::from),
            None => None,
        }
    }
}
