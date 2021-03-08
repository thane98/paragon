use super::{
    BoolField, BytesField, FloatField, IntField, LabelField, ListField, MessageField, ReadState,
    RecordField, ReferenceField, StringField, TextData, Types, UnionField, WriteState,
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
    Union(UnionField),
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
            Field::Union($with) => $body,
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
            Field::Union(f) => f.variant().post_register_read(rid, state),
            _ => {}
        }
    }

    pub fn union_read_succeeded(&self) -> anyhow::Result<bool> {
        match self {
            Field::Label(f) => Ok(f.value.is_some()),
            Field::Message(f) => Ok(f.value.is_some()),
            Field::Record(f) => Ok(f.value.is_some()),
            Field::Reference(f) => Ok(f.read_reference_info.is_some()),
            Field::String(f) => Ok(f.value.is_some()),
            Field::Union(_) => Err(anyhow!("Unions cannot be nested.")),
            _ => Ok(true),
        }
    }

    pub fn key(&self, types: &Types) -> Option<String> {
        match self {
            Field::Label(f) => f.value.clone().map(|v| v.to_string()),
            Field::Message(f) => f.value.clone().map(|v| v.to_string()),
            Field::Record(f) => f.value.as_ref().map(|rid| types.key(*rid)).flatten(),
            Field::Reference(f) => f.value.as_ref().map(|rid| types.key(*rid)).flatten(),
            Field::String(f) => f.value.clone().map(|v| v.to_string()),
            _ => None,
        }
    }

    pub fn display_text(&self, types: &Types, text_data: &TextData) -> Option<String> {
        match self {
            Field::Label(f) => f.value.clone().map(|v| v.to_string()),
            Field::Message(f) => match &f.value {
                Some(k) => {
                    for path in &f.paths {
                        if text_data.has_message(path, f.localized, k) {
                            return text_data.message(path, f.localized, k);
                        }
                    }
                    None
                }
                None => None,
            },
            Field::Record(f) => f
                .value
                .as_ref()
                .map(|rid| types.display(text_data, *rid))
                .flatten(),
            Field::Reference(f) => f
                .value
                .as_ref()
                .map(|rid| types.display(text_data, *rid))
                .flatten(),
            Field::String(f) => f.value.clone().map(|v| v.to_string()),
            _ => None,
        }
    }

    pub fn active_variant(&self) -> Option<usize> {
        match self {
            Field::Union(f) => Some(f.active_variant),
            _ => None,
        }
    }

    pub fn set_active_variant(&mut self, variant: usize) -> anyhow::Result<()> {
        match self {
            Field::Union(f) => f.active_variant = variant,
            _ => {
                return Err(anyhow!("Field is not a list."));
            }
        }
        Ok(())
    }

    pub fn items(&self) -> Option<Vec<u64>> {
        match self {
            Field::List(f) => Some(f.items.clone()),
            Field::Union(f) => f.variant().items(),
            _ => None,
        }
    }

    pub fn length(&self) -> Option<usize> {
        match self {
            Field::List(f) => Some(f.items.len()),
            Field::Bytes(f) => Some(f.value.len()),
            Field::Union(f) => f.variant().length(),
            _ => None,
        }
    }

    pub fn stored_type(&self) -> Option<String> {
        match self {
            Field::List(f) => Some(f.typename.clone()),
            Field::Record(f) => Some(f.typename.clone()),
            Field::Union(f) => f.variant().stored_type(),
            _ => None,
        }
    }

    pub fn range(&self) -> Option<(i64, i64)> {
        match self {
            Field::Int(f) => Some(f.range()),
            Field::Union(f) => f.variant().range(),
            _ => None,
        }
    }

    pub fn list_size(&self) -> anyhow::Result<usize> {
        match self {
            Field::List(f) => Ok(f.items.len()),
            Field::Union(f) => f.variant().list_size(),
            _ => Err(anyhow!("Field is not a list.")),
        }
    }

    pub fn list_get(&self, index: usize) -> anyhow::Result<u64> {
        match self {
            Field::List(f) => f.get(index),
            Field::Union(f) => f.variant().list_get(index),
            _ => Err(anyhow!("Field is not a list.")),
        }
    }

    pub fn list_insert(&mut self, rid: u64, index: usize) -> anyhow::Result<()> {
        match self {
            Field::List(f) => f.insert(rid, index),
            Field::Union(f) => f.variant_mut().list_insert(rid, index),
            _ => Err(anyhow!("Field is not a list.")),
        }
    }

    pub fn list_remove(&mut self, index: usize) -> anyhow::Result<()> {
        match self {
            Field::List(f) => f.remove(index),
            Field::Union(f) => f.variant_mut().list_remove(index),
            _ => Err(anyhow!("Field is not a list.")),
        }
    }

    pub fn list_swap(&mut self, a: usize, b: usize) -> anyhow::Result<()> {
        match self {
            Field::List(f) => f.swap(a, b),
            Field::Union(f) => f.variant_mut().list_swap(a, b),
            _ => Err(anyhow!("Field is not a list.")),
        }
    }

    pub fn string_value(&self) -> Option<&str> {
        match self {
            Field::Label(f) => f.value.as_deref(),
            Field::Message(f) => f.value.as_deref(),
            Field::String(f) => f.value.as_deref(),
            Field::Union(f) => f.variant().string_value(),
            _ => None,
        }
    }

    pub fn set_string(&mut self, value: Option<String>) -> anyhow::Result<()> {
        match self {
            Field::Label(f) => f.value = value,
            Field::Message(f) => f.value = value,
            Field::String(f) => f.value = value,
            Field::Union(f) => {
                f.variant_mut().set_string(value)?;
            }
            _ => return Err(anyhow!("Field is not a string.")),
        }
        Ok(())
    }

    pub fn int_value(&self) -> Option<i64> {
        match self {
            Field::Int(f) => Some(f.value),
            Field::Union(f) => f.variant().int_value(),
            _ => None,
        }
    }

    pub fn set_int(&mut self, value: i64) -> anyhow::Result<()> {
        match self {
            Field::Int(f) => f.value = value,
            Field::Union(f) => {
                f.variant_mut().set_int(value)?;
            }
            _ => return Err(anyhow!("Field is not an int.")),
        }
        Ok(())
    }

    pub fn float_value(&self) -> Option<f32> {
        match self {
            Field::Float(f) => Some(f.value),
            Field::Union(f) => f.variant().float_value(),
            _ => None,
        }
    }

    pub fn set_float(&mut self, value: f32) -> anyhow::Result<()> {
        match self {
            Field::Float(f) => f.value = value,
            Field::Union(f) => {
                f.variant_mut().set_float(value)?;
            }
            _ => return Err(anyhow!("Field is not a float.")),
        }
        Ok(())
    }

    pub fn bool_value(&self) -> Option<bool> {
        match self {
            Field::Bool(f) => Some(f.value),
            Field::Union(f) => f.variant().bool_value(),
            _ => None,
        }
    }

    pub fn set_bool(&mut self, value: bool) -> anyhow::Result<()> {
        match self {
            Field::Bool(f) => f.value = value,
            Field::Union(f) => {
                f.variant_mut().set_bool(value)?;
            }
            _ => return Err(anyhow!("Field is not a bool.")),
        }
        Ok(())
    }

    pub fn bytes_value(&self) -> Option<Vec<u8>> {
        match self {
            Field::Bytes(f) => Some(f.value.clone()),
            Field::Union(f) => f.variant().bytes_value(),
            _ => None,
        }
    }

    pub fn set_bytes(&mut self, value: Vec<u8>) -> anyhow::Result<()> {
        match self {
            Field::Bytes(f) => f.value = value,
            Field::Union(f) => {
                f.variant_mut().set_bytes(value)?;
            }
            _ => return Err(anyhow!("Field is not a bytes.")),
        }
        Ok(())
    }

    pub fn get_byte(&self, index: usize) -> anyhow::Result<u8> {
        match self {
            Field::Bytes(f) => f.get(index),
            Field::Union(f) => f.variant().get_byte(index),
            _ => Err(anyhow!("Field is not a bytes.")),
        }
    }

    pub fn set_byte(&mut self, index: usize, byte: u8) -> anyhow::Result<()> {
        match self {
            Field::Bytes(f) => f.set_byte(index, byte),
            Field::Union(f) => f.variant_mut().set_byte(index, byte),
            _ => Err(anyhow!("Field is not a bytes.")),
        }
    }

    pub fn rid_value(&self) -> Option<u64> {
        match self {
            Field::Record(f) => f.value.clone(),
            Field::Reference(f) => f.value.clone(),
            Field::Union(f) => f.variant().rid_value(),
            _ => None,
        }
    }

    pub fn set_rid(&mut self, rid: Option<u64>) -> anyhow::Result<()> {
        match self {
            Field::Record(f) => f.value = rid,
            Field::Reference(f) => f.value = rid,
            Field::Union(f) => {
                f.variant_mut().set_rid(rid)?;
            }
            _ => return Err(anyhow!("Field is not a bytes.")),
        }
        Ok(())
    }

    pub fn clone_with_allocations(&self, types: &mut Types) -> anyhow::Result<Field> {
        on_field!(self, f, { f.clone_with_allocations(types) })
    }
}
