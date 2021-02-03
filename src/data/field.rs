use super::{
    BoolField, BytesField, FloatField, IntField, LabelField, ListField, MessageField, ReadState,
    RecordField, ReferenceField, StringField, TextData, Types, WriteState,
};
use anyhow::anyhow;
use pyo3::{PyObject, PyResult, Python};
use serde::Deserialize;

#[derive(Clone, Debug, Deserialize)]
#[serde(rename_all = "snake_case", tag = "type")]
pub enum Field {
    Bool(BoolField),
    Bytes(BytesField),
    Float(FloatField),
    Int(IntField),
    Label(LabelField),
    List(ListField),
    Message(MessageField),
    Record(RecordField),
    Reference(ReferenceField),
    String(StringField),
}

macro_rules! on_field {
    ($on:ident, $with:ident, $body:tt) => {
        match $on {
            Field::Bool($with) => $body,
            Field::Bytes($with) => $body,
            Field::Float($with) => $body,
            Field::Int($with) => $body,
            Field::Label($with) => $body,
            Field::List($with) => $body,
            Field::Message($with) => $body,
            Field::Record($with) => $body,
            Field::Reference($with) => $body,
            Field::String($with) => $body,
        }
    };
}

impl Field {
    pub fn id(&self) -> &str {
        on_field!(self, f, { &f.id })
    }

    pub fn read(&mut self, state: &mut ReadState) -> anyhow::Result<()> {
        on_field!(self, f, { f.read(state) })
    }

    pub fn write(&self, state: &mut WriteState) -> anyhow::Result<()> {
        on_field!(self, f, { f.write(state) })
    }

    pub fn metadata(&self, py: Python) -> PyResult<PyObject> {
        on_field!(self, f, { f.metadata(py) })
    }

    pub fn post_register_read(&self, rid: u64, state: &mut ReadState) {
        match self {
            Field::List(f) => f.post_register_read(rid, state),
            Field::Reference(f) => f.post_register_read(rid, state),
            _ => {}
        }
    }

    pub fn display_text(&self, types: &Types, text_data: &TextData) -> Option<String> {
        match self {
            Field::Label(f) => f.value.clone().map(|v| v.to_string()),
            Field::Message(f) => match &f.value {
                Some(k) => {
                    for path in &f.paths {
                        if text_data.has_message(path.clone(), f.localized, k) {
                            return text_data.message(path.clone(), f.localized, k);
                        }
                    }
                    None
                }
                None => None,
            },
            Field::Reference(f) => f
                .value
                .as_ref()
                .map(|rid| types.display(text_data, *rid))
                .flatten(),
            Field::String(f) => f.value.clone().map(|v| v.to_string()),
            _ => None,
        }
    }

    pub fn items(&self) -> Option<Vec<u64>> {
        match self {
            Field::List(f) => Some(f.items.clone()),
            _ => None,
        }
    }

    pub fn length(&self) -> Option<usize> {
        match self {
            Field::List(f) => Some(f.items.len()),
            Field::Bytes(f) => Some(f.value.len()),
            _ => None,
        }
    }

    pub fn stored_type(&self) -> Option<String> {
        match self {
            Field::List(f) => Some(f.typename.clone()),
            Field::Record(f) => Some(f.typename.clone()),
            _ => None,
        }
    }

    pub fn range(&self) -> Option<(i64, i64)> {
        match self {
            Field::Int(f) => Some(f.range()),
            _ => None,
        }
    }

    pub fn list_insert(&mut self, rid: u64, index: usize) -> anyhow::Result<()> {
        match self {
            Field::List(f) => f.insert(rid, index),
            _ => Err(anyhow!("Field is not a list.")),
        }
    }

    pub fn list_remove(&mut self, index: usize) -> anyhow::Result<()> {
        match self {
            Field::List(f) => f.remove(index),
            _ => Err(anyhow!("Field is not a list.")),
        }
    }

    pub fn list_swap(&mut self, a: usize, b: usize) -> anyhow::Result<()> {
        match self {
            Field::List(f) => f.swap(a, b),
            _ => Err(anyhow!("Field is not a list.")),
        }
    }

    pub fn string_value(&self) -> Option<&str> {
        match self {
            Field::Label(f) => f.value.as_deref(),
            Field::Message(f) => f.value.as_deref(),
            Field::String(f) => f.value.as_deref(),
            _ => None,
        }
    }

    pub fn set_string(&mut self, value: Option<String>) -> anyhow::Result<()> {
        match self {
            Field::Label(f) => f.value = value,
            Field::Message(f) => f.value = value,
            Field::String(f) => f.value = value,
            _ => return Err(anyhow!("Field is not a string.")),
        }
        Ok(())
    }

    pub fn int_value(&self) -> Option<i64> {
        match self {
            Field::Int(f) => Some(f.value),
            _ => None,
        }
    }

    pub fn set_int(&mut self, value: i64) -> anyhow::Result<()> {
        match self {
            Field::Int(f) => f.value = value,
            _ => return Err(anyhow!("Field is not an int.")),
        }
        Ok(())
    }

    pub fn float_value(&self) -> Option<f32> {
        match self {
            Field::Float(f) => Some(f.value),
            _ => None,
        }
    }

    pub fn set_float(&mut self, value: f32) -> anyhow::Result<()> {
        match self {
            Field::Float(f) => f.value = value,
            _ => return Err(anyhow!("Field is not a float.")),
        }
        Ok(())
    }

    pub fn bool_value(&self) -> Option<bool> {
        match self {
            Field::Bool(f) => Some(f.value),
            _ => None,
        }
    }

    pub fn set_bool(&mut self, value: bool) -> anyhow::Result<()> {
        match self {
            Field::Bool(f) => f.value = value,
            _ => return Err(anyhow!("Field is not a bool.")),
        }
        Ok(())
    }

    pub fn bytes_value(&self) -> Option<Vec<u8>> {
        match self {
            Field::Bytes(f) => Some(f.value.clone()),
            _ => None,
        }
    }

    pub fn set_bytes(&mut self, value: Vec<u8>) -> anyhow::Result<()> {
        match self {
            Field::Bytes(f) => f.value = value,
            _ => return Err(anyhow!("Field is not a bytes.")),
        }
        Ok(())
    }

    pub fn rid_value(&self) -> Option<u64> {
        match self {
            Field::Record(f) => f.value.clone(),
            Field::Reference(f) => f.value.clone(),
            _ => None,
        }
    }

    pub fn set_rid(&mut self, rid: Option<u64>) -> anyhow::Result<()> {
        match self {
            Field::Record(f) => f.value = rid,
            Field::Reference(f) => f.value = rid,
            _ => return Err(anyhow!("Field is not a bytes.")),
        }
        Ok(())
    }

    pub fn clone_with_allocations(&self, types: &mut Types) -> anyhow::Result<Field> {
        on_field!(self, f, { f.clone_with_allocations(types) })
    }
}
