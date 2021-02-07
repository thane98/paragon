use super::{Field, ReadState, TypeDefinition, Types, WriteState};
use anyhow::{anyhow, Context};
use linked_hash_map::LinkedHashMap;

#[derive(Debug, Clone)]
pub struct Record {
    typename: String,
    fields: LinkedHashMap<String, Field>,
}

impl Record {
    pub fn new(name: String, definition: &TypeDefinition) -> Self {
        let mut fields: LinkedHashMap<String, Field> = LinkedHashMap::new();
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
    ) -> anyhow::Result<()> {
        if self.typename != other.typename {
            return Err(anyhow!(
                "Cannot copy between different types: {} {}.",
                self.typename,
                other.typename
            ));
        }
        let fields: Vec<String> = if fields.len() > 0 {
            fields.iter().cloned().collect()
        } else {
            self.fields.keys().map(|k| k.clone()).collect()
        };
        for field in fields {
            let field_clone = self
                .fields
                .get(&field)
                .unwrap()
                .clone_with_allocations(types)?;
            other.fields.insert(field, field_clone);
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
        Ok(())
    }

    pub fn post_register_read(&self, rid: u64, state: &mut ReadState) {
        if let Some(td) = state.types.get(self.typename()) {
            if let Some(node) = &td.node {
                let mut node = node.clone();
                if let Some(context) = &state.node_context {
                    node.id = format!("{}{}", node.id, context.id_suffix);
                    node.name = format!("{}{}", node.name, context.name_suffix);
                }
                node.rid = rid;
                node.store = state.store_id.clone();
                state.nodes.push(node);
            }
        }
        for (_, v) in &self.fields {
            v.post_register_read(rid, state);
        }
    }

    pub fn write(&self, state: &mut WriteState, rid: u64) -> anyhow::Result<()> {
        state.address_stack.push(state.writer.tell());
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
        state.rid_stack.pop();
        Ok(())
    }

    pub fn string(&self, id: &str) -> Option<String> {
        match self.field(id) {
            Some(field) => field.string_value().map(String::from),
            None => None,
        }
    }

    pub fn key(&self, types: &Types) -> Option<String> {
        match types.get(&self.typename) {
            Some(typedef) => match &typedef.key {
                Some(id) => self.string(id),
                None => None,
            },
            None => None,
        }
    }
}
