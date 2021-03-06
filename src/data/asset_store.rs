use super::{Field, ReadOutput, Record, Types, UINode};
use anyhow::{anyhow, Context};
use mila::{AssetBinary, AssetSpec, LayeredFilesystem};
use serde::Deserialize;

fn default_typename() -> String {
    "Asset".to_owned()
}

fn vec_to_array(v: Vec<u8>) -> [u8; 4] {
    [v[0], v[1], v[2], v[3]]
}

fn to_record(types: &mut Types, spec: &AssetSpec) -> anyhow::Result<Record> {
    let mut record = types
        .instantiate("AssetSpec")
        .ok_or(anyhow!("Type 'AssetSpec' does not exist."))?;
    record
        .field_mut("name")
        .ok_or(anyhow!("Missing field."))?
        .set_string(spec.name.to_owned())?;
    record
        .field_mut("conditional1")
        .ok_or(anyhow!("Missing field."))?
        .set_string(spec.conditional1.to_owned())?;
    record
        .field_mut("conditional2")
        .ok_or(anyhow!("Missing field."))?
        .set_string(spec.conditional2.to_owned())?;
    record
        .field_mut("body_model")
        .ok_or(anyhow!("Missing field."))?
        .set_string(spec.body_model.to_owned())?;
    record
        .field_mut("body_texture")
        .ok_or(anyhow!("Missing field."))?
        .set_string(spec.body_texture.to_owned())?;
    record
        .field_mut("head_model")
        .ok_or(anyhow!("Missing field."))?
        .set_string(spec.head_model.to_owned())?;
    record
        .field_mut("head_texture")
        .ok_or(anyhow!("Missing field."))?
        .set_string(spec.head_texture.to_owned())?;
    record
        .field_mut("hair_model")
        .ok_or(anyhow!("Missing field."))?
        .set_string(spec.hair_model.to_owned())?;
    record
        .field_mut("hair_texture")
        .ok_or(anyhow!("Missing field."))?
        .set_string(spec.hair_texture.to_owned())?;
    record
        .field_mut("outer_clothing_model")
        .ok_or(anyhow!("Missing field."))?
        .set_string(spec.outer_clothing_model.to_owned())?;
    record
        .field_mut("outer_clothing_texture")
        .ok_or(anyhow!("Missing field."))?
        .set_string(spec.outer_clothing_texture.to_owned())?;
    record
        .field_mut("underwear_model")
        .ok_or(anyhow!("Missing field."))?
        .set_string(spec.underwear_model.to_owned())?;
    record
        .field_mut("underwear_texture")
        .ok_or(anyhow!("Missing field."))?
        .set_string(spec.underwear_texture.to_owned())?;
    record
        .field_mut("mount_model")
        .ok_or(anyhow!("Missing field."))?
        .set_string(spec.mount_model.to_owned())?;
    record
        .field_mut("mount_texture")
        .ok_or(anyhow!("Missing field."))?
        .set_string(spec.mount_texture.to_owned())?;
    record
        .field_mut("mount_outer_clothing_model")
        .ok_or(anyhow!("Missing field."))?
        .set_string(spec.mount_outer_clothing_model.to_owned())?;
    record
        .field_mut("mount_outer_clothing_texture")
        .ok_or(anyhow!("Missing field."))?
        .set_string(spec.mount_outer_clothing_texture.to_owned())?;
    record
        .field_mut("weapon_model_dual")
        .ok_or(anyhow!("Missing field."))?
        .set_string(spec.weapon_model_dual.to_owned())?;
    record
        .field_mut("weapon_model")
        .ok_or(anyhow!("Missing field."))?
        .set_string(spec.weapon_model.to_owned())?;
    record
        .field_mut("skeleton")
        .ok_or(anyhow!("Missing field."))?
        .set_string(spec.skeleton.to_owned())?;
    record
        .field_mut("mount_skeleton")
        .ok_or(anyhow!("Missing field."))?
        .set_string(spec.mount_skeleton.to_owned())?;
    record
        .field_mut("accessory1_model")
        .ok_or(anyhow!("Missing field."))?
        .set_string(spec.accessory1_model.to_owned())?;
    record
        .field_mut("accessory1_texture")
        .ok_or(anyhow!("Missing field."))?
        .set_string(spec.accessory1_texture.to_owned())?;
    record
        .field_mut("accessory2_model")
        .ok_or(anyhow!("Missing field."))?
        .set_string(spec.accessory2_model.to_owned())?;
    record
        .field_mut("accessory2_texture")
        .ok_or(anyhow!("Missing field."))?
        .set_string(spec.accessory2_texture.to_owned())?;
    record
        .field_mut("accessory3_model")
        .ok_or(anyhow!("Missing field."))?
        .set_string(spec.accessory3_model.to_owned())?;
    record
        .field_mut("accessory3_texture")
        .ok_or(anyhow!("Missing field."))?
        .set_string(spec.accessory3_texture.to_owned())?;
    record
        .field_mut("attack_animation")
        .ok_or(anyhow!("Missing field."))?
        .set_string(spec.attack_animation.to_owned())?;
    record
        .field_mut("attack_animation2")
        .ok_or(anyhow!("Missing field."))?
        .set_string(spec.attack_animation2.to_owned())?;
    record
        .field_mut("visual_effect")
        .ok_or(anyhow!("Missing field."))?
        .set_string(spec.visual_effect.to_owned())?;
    record
        .field_mut("hid")
        .ok_or(anyhow!("Missing field."))?
        .set_string(spec.hid.to_owned())?;
    record
        .field_mut("footstep_sound")
        .ok_or(anyhow!("Missing field."))?
        .set_string(spec.footstep_sound.to_owned())?;
    record
        .field_mut("clothing_sound")
        .ok_or(anyhow!("Missing field."))?
        .set_string(spec.clothing_sound.to_owned())?;
    record
        .field_mut("voice")
        .ok_or(anyhow!("Missing field."))?
        .set_string(spec.voice.to_owned())?;
    record
        .field_mut("hair_color")
        .ok_or(anyhow!("Missing field."))?
        .set_bytes(spec.hair_color.iter().cloned().collect())?;
    record
        .field_mut("use_hair_color")
        .ok_or(anyhow!("Missing field."))?
        .set_bool(spec.use_hair_color)?;
    record
        .field_mut("skin_color")
        .ok_or(anyhow!("Missing field."))?
        .set_bytes(spec.skin_color.iter().cloned().collect())?;
    record
        .field_mut("use_skin_color")
        .ok_or(anyhow!("Missing field."))?
        .set_bool(spec.use_skin_color)?;
    record
        .field_mut("weapon_trail_color")
        .ok_or(anyhow!("Missing field."))?
        .set_bytes(spec.weapon_trail_color.iter().cloned().collect())?;
    record
        .field_mut("use_weapon_trail_color")
        .ok_or(anyhow!("Missing field."))?
        .set_bool(spec.use_weapon_trail_color)?;
    record
        .field_mut("model_size")
        .ok_or(anyhow!("Missing field."))?
        .set_float(spec.model_size)?;
    record
        .field_mut("use_model_size")
        .ok_or(anyhow!("Missing field."))?
        .set_bool(spec.use_model_size)?;
    record
        .field_mut("head_size")
        .ok_or(anyhow!("Missing field."))?
        .set_float(spec.head_size)?;
    record
        .field_mut("use_head_size")
        .ok_or(anyhow!("Missing field."))?
        .set_bool(spec.use_head_size)?;
    record
        .field_mut("pupil_y")
        .ok_or(anyhow!("Missing field."))?
        .set_float(spec.pupil_y)?;
    record
        .field_mut("use_pupil_y")
        .ok_or(anyhow!("Missing field."))?
        .set_bool(spec.use_pupil_y)?;
    record
        .field_mut("unk3")
        .ok_or(anyhow!("Missing field."))?
        .set_int(spec.unk3 as i64)?;
    record
        .field_mut("use_unk3")
        .ok_or(anyhow!("Missing field."))?
        .set_bool(spec.use_unk3)?;
    record
        .field_mut("unk4")
        .ok_or(anyhow!("Missing field."))?
        .set_int(spec.unk4 as i64)?;
    record
        .field_mut("use_unk4")
        .ok_or(anyhow!("Missing field."))?
        .set_bool(spec.use_unk4)?;
    record
        .field_mut("unk5")
        .ok_or(anyhow!("Missing field."))?
        .set_int(spec.unk5 as i64)?;
    record
        .field_mut("use_unk5")
        .ok_or(anyhow!("Missing field."))?
        .set_bool(spec.use_unk5)?;
    record
        .field_mut("unk6")
        .ok_or(anyhow!("Missing field."))?
        .set_int(spec.unk6 as i64)?;
    record
        .field_mut("use_unk6")
        .ok_or(anyhow!("Missing field."))?
        .set_bool(spec.use_unk6)?;
    record
        .field_mut("on_hit_effect")
        .ok_or(anyhow!("Missing field."))?
        .set_int(spec.on_hit_effect as i64)?;
    record
        .field_mut("use_on_hit_effect")
        .ok_or(anyhow!("Missing field."))?
        .set_bool(spec.use_on_hit_effect)?;
    record
        .field_mut("unk7")
        .ok_or(anyhow!("Missing field."))?
        .set_int(spec.unk7 as i64)?;
    record
        .field_mut("use_unk7")
        .ok_or(anyhow!("Missing field."))?
        .set_bool(spec.use_unk7)?;
    record
        .field_mut("unk8")
        .ok_or(anyhow!("Missing field."))?
        .set_int(spec.unk8 as i64)?;
    record
        .field_mut("use_unk8")
        .ok_or(anyhow!("Missing field."))?
        .set_bool(spec.use_unk8)?;
    record
        .field_mut("unk9")
        .ok_or(anyhow!("Missing field."))?
        .set_int(spec.unk9 as i64)?;
    record
        .field_mut("use_unk9")
        .ok_or(anyhow!("Missing field."))?
        .set_bool(spec.use_unk9)?;
    record
        .field_mut("unk10")
        .ok_or(anyhow!("Missing field."))?
        .set_int(spec.unk10 as i64)?;
    record
        .field_mut("use_unk10")
        .ok_or(anyhow!("Missing field."))?
        .set_bool(spec.use_unk10)?;
    record
        .field_mut("unk11")
        .ok_or(anyhow!("Missing field."))?
        .set_int(spec.unk11 as i64)?;
    record
        .field_mut("use_unk11")
        .ok_or(anyhow!("Missing field."))?
        .set_bool(spec.use_unk11)?;
    record
        .field_mut("unk12")
        .ok_or(anyhow!("Missing field."))?
        .set_int(spec.unk12 as i64)?;
    record
        .field_mut("use_unk12")
        .ok_or(anyhow!("Missing field."))?
        .set_bool(spec.use_unk12)?;
    record
        .field_mut("unk13")
        .ok_or(anyhow!("Missing field."))?
        .set_int(spec.unk13 as i64)?;
    record
        .field_mut("use_unk13")
        .ok_or(anyhow!("Missing field."))?
        .set_bool(spec.use_unk13)?;
    Ok(record)
}

fn to_records(types: &mut Types, specs: &[AssetSpec]) -> anyhow::Result<Vec<u64>> {
    let mut items: Vec<u64> = Vec::new();
    for spec in specs {
        let record = to_record(types, spec).context("Failed to convert AssetSpec to record.")?;
        items.push(types.register(record));
    }
    Ok(items)
}

fn to_spec(record: &Record) -> anyhow::Result<AssetSpec> {
    let mut spec = AssetSpec::new();
    spec.name = record
        .field("name")
        .ok_or(anyhow!("Missing field."))?
        .string_value()
        .map(|x| x.to_string());
    spec.conditional1 = record
        .field("conditional1")
        .ok_or(anyhow!("Missing field."))?
        .string_value()
        .map(|x| x.to_string());
    spec.conditional2 = record
        .field("conditional2")
        .ok_or(anyhow!("Missing field."))?
        .string_value()
        .map(|x| x.to_string());
    spec.body_model = record
        .field("body_model")
        .ok_or(anyhow!("Missing field."))?
        .string_value()
        .map(|x| x.to_string());
    spec.body_texture = record
        .field("body_texture")
        .ok_or(anyhow!("Missing field."))?
        .string_value()
        .map(|x| x.to_string());
    spec.head_model = record
        .field("head_model")
        .ok_or(anyhow!("Missing field."))?
        .string_value()
        .map(|x| x.to_string());
    spec.head_texture = record
        .field("head_texture")
        .ok_or(anyhow!("Missing field."))?
        .string_value()
        .map(|x| x.to_string());
    spec.hair_model = record
        .field("hair_model")
        .ok_or(anyhow!("Missing field."))?
        .string_value()
        .map(|x| x.to_string());
    spec.hair_texture = record
        .field("hair_texture")
        .ok_or(anyhow!("Missing field."))?
        .string_value()
        .map(|x| x.to_string());
    spec.outer_clothing_model = record
        .field("outer_clothing_model")
        .ok_or(anyhow!("Missing field."))?
        .string_value()
        .map(|x| x.to_string());
    spec.outer_clothing_texture = record
        .field("outer_clothing_texture")
        .ok_or(anyhow!("Missing field."))?
        .string_value()
        .map(|x| x.to_string());
    spec.underwear_model = record
        .field("underwear_model")
        .ok_or(anyhow!("Missing field."))?
        .string_value()
        .map(|x| x.to_string());
    spec.underwear_texture = record
        .field("underwear_texture")
        .ok_or(anyhow!("Missing field."))?
        .string_value()
        .map(|x| x.to_string());
    spec.mount_model = record
        .field("mount_model")
        .ok_or(anyhow!("Missing field."))?
        .string_value()
        .map(|x| x.to_string());
    spec.mount_texture = record
        .field("mount_texture")
        .ok_or(anyhow!("Missing field."))?
        .string_value()
        .map(|x| x.to_string());
    spec.mount_outer_clothing_model = record
        .field("mount_outer_clothing_model")
        .ok_or(anyhow!("Missing field."))?
        .string_value()
        .map(|x| x.to_string());
    spec.mount_outer_clothing_texture = record
        .field("mount_outer_clothing_texture")
        .ok_or(anyhow!("Missing field."))?
        .string_value()
        .map(|x| x.to_string());
    spec.weapon_model_dual = record
        .field("weapon_model_dual")
        .ok_or(anyhow!("Missing field."))?
        .string_value()
        .map(|x| x.to_string());
    spec.weapon_model = record
        .field("weapon_model")
        .ok_or(anyhow!("Missing field."))?
        .string_value()
        .map(|x| x.to_string());
    spec.skeleton = record
        .field("skeleton")
        .ok_or(anyhow!("Missing field."))?
        .string_value()
        .map(|x| x.to_string());
    spec.mount_skeleton = record
        .field("mount_skeleton")
        .ok_or(anyhow!("Missing field."))?
        .string_value()
        .map(|x| x.to_string());
    spec.accessory1_model = record
        .field("accessory1_model")
        .ok_or(anyhow!("Missing field."))?
        .string_value()
        .map(|x| x.to_string());
    spec.accessory1_texture = record
        .field("accessory1_texture")
        .ok_or(anyhow!("Missing field."))?
        .string_value()
        .map(|x| x.to_string());
    spec.accessory2_model = record
        .field("accessory2_model")
        .ok_or(anyhow!("Missing field."))?
        .string_value()
        .map(|x| x.to_string());
    spec.accessory2_texture = record
        .field("accessory2_texture")
        .ok_or(anyhow!("Missing field."))?
        .string_value()
        .map(|x| x.to_string());
    spec.accessory3_model = record
        .field("accessory3_model")
        .ok_or(anyhow!("Missing field."))?
        .string_value()
        .map(|x| x.to_string());
    spec.accessory3_texture = record
        .field("accessory3_texture")
        .ok_or(anyhow!("Missing field."))?
        .string_value()
        .map(|x| x.to_string());
    spec.attack_animation = record
        .field("attack_animation")
        .ok_or(anyhow!("Missing field."))?
        .string_value()
        .map(|x| x.to_string());
    spec.attack_animation2 = record
        .field("attack_animation2")
        .ok_or(anyhow!("Missing field."))?
        .string_value()
        .map(|x| x.to_string());
    spec.visual_effect = record
        .field("visual_effect")
        .ok_or(anyhow!("Missing field."))?
        .string_value()
        .map(|x| x.to_string());
    spec.hid = record
        .field("hid")
        .ok_or(anyhow!("Missing field."))?
        .string_value()
        .map(|x| x.to_string());
    spec.footstep_sound = record
        .field("footstep_sound")
        .ok_or(anyhow!("Missing field."))?
        .string_value()
        .map(|x| x.to_string());
    spec.clothing_sound = record
        .field("clothing_sound")
        .ok_or(anyhow!("Missing field."))?
        .string_value()
        .map(|x| x.to_string());
    spec.voice = record
        .field("voice")
        .ok_or(anyhow!("Missing field."))?
        .string_value()
        .map(|x| x.to_string());
    spec.hair_color = vec_to_array(
        record
            .field("hair_color")
            .ok_or(anyhow!("Missing field."))?
            .bytes_value()
            .unwrap(),
    );
    spec.use_hair_color = record
        .field("use_hair_color")
        .ok_or(anyhow!("Missing field."))?
        .bool_value()
        .unwrap();
    spec.skin_color = vec_to_array(
        record
            .field("skin_color")
            .ok_or(anyhow!("Missing field."))?
            .bytes_value()
            .unwrap(),
    );
    spec.use_skin_color = record
        .field("use_skin_color")
        .ok_or(anyhow!("Missing field."))?
        .bool_value()
        .unwrap();
    spec.weapon_trail_color = vec_to_array(
        record
            .field("weapon_trail_color")
            .ok_or(anyhow!("Missing field."))?
            .bytes_value()
            .unwrap(),
    );
    spec.use_weapon_trail_color = record
        .field("use_weapon_trail_color")
        .ok_or(anyhow!("Missing field."))?
        .bool_value()
        .unwrap();
    spec.model_size = record
        .field("model_size")
        .ok_or(anyhow!("Missing field."))?
        .float_value()
        .unwrap();
    spec.use_model_size = record
        .field("use_model_size")
        .ok_or(anyhow!("Missing field."))?
        .bool_value()
        .unwrap();
    spec.head_size = record
        .field("head_size")
        .ok_or(anyhow!("Missing field."))?
        .float_value()
        .unwrap();
    spec.use_head_size = record
        .field("use_head_size")
        .ok_or(anyhow!("Missing field."))?
        .bool_value()
        .unwrap();
    spec.pupil_y = record
        .field("pupil_y")
        .ok_or(anyhow!("Missing field."))?
        .float_value()
        .unwrap();
    spec.use_pupil_y = record
        .field("use_pupil_y")
        .ok_or(anyhow!("Missing field."))?
        .bool_value()
        .unwrap();
    spec.unk3 = record
        .field("unk3")
        .ok_or(anyhow!("Missing field."))?
        .int_value()
        .unwrap() as u32;
    spec.use_unk3 = record
        .field("use_unk3")
        .ok_or(anyhow!("Missing field."))?
        .bool_value()
        .unwrap();
    spec.unk4 = record
        .field("unk4")
        .ok_or(anyhow!("Missing field."))?
        .int_value()
        .unwrap() as u32;
    spec.use_unk4 = record
        .field("use_unk4")
        .ok_or(anyhow!("Missing field."))?
        .bool_value()
        .unwrap();
    spec.unk5 = record
        .field("unk5")
        .ok_or(anyhow!("Missing field."))?
        .int_value()
        .unwrap() as u32;
    spec.use_unk5 = record
        .field("use_unk5")
        .ok_or(anyhow!("Missing field."))?
        .bool_value()
        .unwrap();
    spec.unk6 = record
        .field("unk6")
        .ok_or(anyhow!("Missing field."))?
        .int_value()
        .unwrap() as u32;
    spec.use_unk6 = record
        .field("use_unk6")
        .ok_or(anyhow!("Missing field."))?
        .bool_value()
        .unwrap();
    spec.on_hit_effect = record
        .field("on_hit_effect")
        .ok_or(anyhow!("Missing field."))?
        .int_value()
        .unwrap() as u32;
    spec.use_on_hit_effect = record
        .field("use_on_hit_effect")
        .ok_or(anyhow!("Missing field."))?
        .bool_value()
        .unwrap();
    spec.unk7 = record
        .field("unk7")
        .ok_or(anyhow!("Missing field."))?
        .int_value()
        .unwrap() as u32;
    spec.use_unk7 = record
        .field("use_unk7")
        .ok_or(anyhow!("Missing field."))?
        .bool_value()
        .unwrap();
    spec.unk8 = record
        .field("unk8")
        .ok_or(anyhow!("Missing field."))?
        .int_value()
        .unwrap() as u32;
    spec.use_unk8 = record
        .field("use_unk8")
        .ok_or(anyhow!("Missing field."))?
        .bool_value()
        .unwrap();
    spec.unk9 = record
        .field("unk9")
        .ok_or(anyhow!("Missing field."))?
        .int_value()
        .unwrap() as u32;
    spec.use_unk9 = record
        .field("use_unk9")
        .ok_or(anyhow!("Missing field."))?
        .bool_value()
        .unwrap();
    spec.unk10 = record
        .field("unk10")
        .ok_or(anyhow!("Missing field."))?
        .int_value()
        .unwrap() as u32;
    spec.use_unk10 = record
        .field("use_unk10")
        .ok_or(anyhow!("Missing field."))?
        .bool_value()
        .unwrap();
    spec.unk11 = record
        .field("unk11")
        .ok_or(anyhow!("Missing field."))?
        .int_value()
        .unwrap() as u32;
    spec.use_unk11 = record
        .field("use_unk11")
        .ok_or(anyhow!("Missing field."))?
        .bool_value()
        .unwrap();
    spec.unk12 = record
        .field("unk12")
        .ok_or(anyhow!("Missing field."))?
        .int_value()
        .unwrap() as u32;
    spec.use_unk12 = record
        .field("use_unk12")
        .ok_or(anyhow!("Missing field."))?
        .bool_value()
        .unwrap();
    spec.unk13 = record
        .field("unk13")
        .ok_or(anyhow!("Missing field."))?
        .int_value()
        .unwrap() as u32;
    spec.use_unk13 = record
        .field("use_unk13")
        .ok_or(anyhow!("Missing field."))?
        .bool_value()
        .unwrap();
    Ok(spec)
}

#[derive(Deserialize)]
pub struct AssetStore {
    pub id: String,

    pub node: UINode,

    pub filename: String,

    #[serde(skip, default = "default_typename")]
    pub typename: String,

    #[serde(skip, default)]
    pub rid: Option<u64>,

    #[serde(skip, default)]
    pub dirty: bool,
}

impl AssetStore {
    pub fn dirty_files(&self) -> Vec<String> {
        if self.dirty {
            vec![self.filename.clone()]
        } else {
            Vec::new()
        }
    }

    pub fn read(
        &mut self,
        types: &mut Types,
        fs: &LayeredFilesystem,
    ) -> anyhow::Result<ReadOutput> {
        let archive = fs.read_archive(&self.filename, false)?;
        let asset_binary = mila::AssetBinary::from_archive(&archive)
            .with_context(|| format!("Failed to parse Asset from '{}'.", self.filename))?;

        let mut table = types
            .instantiate("AssetTable")
            .ok_or(anyhow!("Type 'AssetTable' does not exist."))?;
        table
            .field_mut("flags")
            .ok_or(anyhow!("AssetTable is missing 'flags' field."))?
            .set_int(asset_binary.flags as i64)?;
        match table.field_mut("specs") {
            Some(f) => match f {
                Field::List(l) => {
                    l.items.extend(to_records(types, &asset_binary.specs)?);
                    let rid = types.register(table);
                    self.rid = Some(rid);
                    let mut output = ReadOutput::new();
                    let mut node = self.node.clone();
                    node.rid = self.rid.unwrap();
                    node.store = self.id.clone();
                    output.nodes.push(node);
                    output
                        .tables
                        .insert(self.id.clone(), (rid, "specs".to_owned()));
                    Ok(output)
                }
                _ => Err(anyhow!(
                    "Expected field 'specs' in AssetTable to be a list."
                )),
            },
            None => Err(anyhow!("Expected field 'specs' in AssetTable")),
        }
    }

    pub fn write(&self, types: &Types, fs: &LayeredFilesystem) -> anyhow::Result<()> {
        match self.rid {
            Some(rid) => {
                let mut binary = AssetBinary::new();
                binary.flags = types
                    .int(rid, "flags")
                    .ok_or(anyhow!("AssetTable has no 'flags' field."))?
                    as u32;
                let specs = types
                    .items(rid, "specs")
                    .ok_or(anyhow!("AssetTable has no 'specs' field."))?;
                for rid in specs {
                    let instance = types
                        .instance(rid)
                        .ok_or(anyhow!("Bad RID in AssetTable."))?;
                    let spec = to_spec(instance)?;
                    binary.specs.push(spec);
                }

                let bytes = binary
                    .serialize()
                    .context("Failed to serialize AssetBinary.")?;
                fs.write(&self.filename, &bytes, false)?;
                Ok(())
            }
            None => Ok(()),
        }
    }
}
