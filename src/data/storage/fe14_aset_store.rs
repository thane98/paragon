use crate::data::fields::field::Field;
use crate::data::fields::list_field::ListField;
use crate::data::fields::string_field::StringField;
use crate::data::{Record, TypeDefinition, Types};
use crate::model::id::{RecordId, StoreNumber};
use crate::model::read_output::ReadOutput;
use crate::model::ui_node::UINode;
use anyhow::{anyhow, Context};
use mila::fe14_aset::ANIMATION_NAMES;
use mila::{FE14ASet, LayeredFilesystem};
use serde::Deserialize;

#[derive(Deserialize, Debug)]
pub struct FE14ASetStore {
    pub id: String,

    pub node: UINode,

    pub filename: String,

    #[serde(skip, default)]
    pub store_number: Option<StoreNumber>,

    #[serde(skip, default)]
    pub rid: Option<RecordId>,

    #[serde(skip, default)]
    pub dirty: bool,

    #[serde(skip, default)]
    pub force_dirty: bool,
}

fn to_records(types: &mut Types, sets: &[Vec<Option<String>>], store_number: StoreNumber) -> anyhow::Result<Vec<RecordId>> {
    let mut sets_table = Vec::new();
    for set in sets {
        let mut set_record = types
            .instantiate("AnimationSet")
            .ok_or_else(|| anyhow::anyhow!("Undefined type 'AnimationSet'"))?;
        for i in 0..set.len() {
            match set_record.field_mut(ANIMATION_NAMES[i]) {
                Some(f) => f.set_string(set[i].clone())?,
                None => return Err(anyhow::anyhow!("Unknown field '{}'", ANIMATION_NAMES[i])),
            }
        }
        sets_table.push(types.register(set_record, store_number));
    }
    Ok(sets_table)
}

fn to_set(record: &Record) -> Vec<Option<String>> {
    let mut set = Vec::new();
    for v in ANIMATION_NAMES {
        match record.string(v) {
            Some(v) => set.push(Some(v)),
            None => set.push(None),
        }
    }
    set
}

fn build_animation_set_type_definition() -> TypeDefinition {
    let mut fields = Vec::new();
    for v in ANIMATION_NAMES {
        fields.push(Field::String(StringField::new(v.to_string())));
    }
    let mut td = TypeDefinition::with_fields(fields);
    td.key = Some("label".to_string());
    td.display = Some("label".to_string());
    td
}

fn build_table_type_definition() -> TypeDefinition {
    let field = ListField::create_table_container("AnimationSet".to_string());
    TypeDefinition::with_fields(vec![Field::List(field)])
}

fn register_types(types: &mut Types) {
    types.register_type(
        "AnimationSet".to_string(),
        build_animation_set_type_definition(),
    );
    types.register_type(
        "AnimationSetTable".to_string(),
        build_table_type_definition(),
    );
}

impl FE14ASetStore {
    pub fn create_instance_for_multi(
        filename: String,
        store_number: StoreNumber,
        dirty: bool,
    ) -> Self {
        FE14ASetStore {
            id: String::new(),
            node: UINode::new(),
            filename,
            store_number: Some(store_number),
            rid: None,
            dirty,
            force_dirty: false,
        }
    }

    pub fn dirty_files(&self) -> Vec<String> {
        if self.dirty {
            vec![self.filename.clone()]
        } else {
            Vec::new()
        }
    }

    pub fn filename(&self) -> String {
        self.filename.clone()
    }

    pub fn set_filename(&mut self, filename: String) {
        self.filename = filename;
    }

    pub fn read(
        &mut self,
        types: &mut Types,
        fs: &LayeredFilesystem,
    ) -> anyhow::Result<ReadOutput> {
        let store_number = self.store_number.unwrap();
        let archive = fs.read_archive(&self.filename, false)?;
        let aset = FE14ASet::from_archive(&archive)
            .with_context(|| format!("Failed to parse FE14ASet from '{}'.", self.filename))?;

        // ASet type definitions are tedious to do by hand, but easy to do programmatically.
        // Handle it here to make things easy.
        register_types(types);

        let mut table = types
            .instantiate("AnimationSetTable")
            .ok_or_else(|| anyhow!("Type 'AnimationSetTable' does not exist."))?;
        match table.field_mut("table") {
            Some(f) => match f {
                Field::List(l) => {
                    l.items.extend(to_records(types, &aset.sets, store_number)?);
                    let rid = types.register(table, store_number);
                    self.rid = Some(rid);
                    let mut output = ReadOutput::new();
                    let mut node = self.node.clone();
                    node.rid = Some(self.rid.unwrap());
                    node.store = self.id.clone();
                    output.nodes.push(node);
                    output
                        .tables
                        .insert(self.id.clone(), (rid, "table".to_string()));
                    Ok(output)
                }
                _ => Err(anyhow!(
                    "Expected field 'table' in AnimationSetTable to be a list."
                )),
            },
            None => Err(anyhow!("Expected field 'table' in AnimationSetTable")),
        }
    }

    pub fn write(&self, types: &Types, fs: &LayeredFilesystem) -> anyhow::Result<()> {
        match self.rid {
            Some(rid) => {
                let archive = fs.read_archive(&self.filename, false)?;
                let mut aset = FE14ASet::from_archive(&archive).with_context(|| {
                    format!("Failed to parse FE14ASet from '{}'.", self.filename)
                })?;
                aset.sets.clear();
                let sets = types
                    .items(rid, "table")
                    .ok_or_else(|| anyhow!("AnimationSetTable has no 'table' field."))?;
                for rid in sets {
                    let instance = types
                        .instance(rid)
                        .ok_or_else(|| anyhow!("Bad RID in AssetTable."))?;
                    let set = to_set(instance);
                    aset.sets.push(set);
                }

                let bytes = aset.serialize().context("Failed to serialize FE14ASet.")?;
                fs.write(&self.filename, &bytes, false)?;
                Ok(())
            }
            None => Ok(()),
        }
    }
}
