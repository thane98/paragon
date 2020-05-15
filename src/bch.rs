use std::io::prelude::*;
use std::io::{self, Cursor, SeekFrom, Seek, Read, Result};
use std::fs::File;
use byteorder::{LittleEndian, ReadBytesExt};
use std::vec;

// Will look at optimized spica code when done
static COMMANDS: [u32; 0x10000];
static UNIFORM: vec![];
static CURRENTUNIFORM: u32;
static lookUpTable: [f32; 256];


pub struct Header {
    magic_ID: str,
    backward_compatibility: u8,
    forward_compatibility: u8,
    version: u16,
    contents_address: u32,
    strings_address: u32,
    commands_address: u32,
    raw_data_address: u32,
    raw_ext_address: u32,             // if BackwardCompatibility > 0x20
    relocation_address: u32,
    contents_length: u32,
    strings_length: u32,
    commands_length: u32,
    raw_data_length: u32,
    raw_ext_length: u32,              // if BackwardCompatibility > 0x20
    relocation_length: u32,
    unInit_data_length: u32,
    unInit_commands_length: u32,
}
pub struct ContentTable {
    models_ptr_table_offset: u32,
    models_ptr_table_entries: u32,
    textures_ptr_table_offset: u32,
    textures_ptr_table_entries: u32,
}
pub struct Texture {
    filename: str,
    bytes: [u8],
}

pub struct Size {
    height: u32,
    width: u32,
}

pub fn Read(file: &[u8]) -> Result<Vec<Texture>> {
    let mut reader = Cursor::new(file);

    let header = read_header(reader)?;

    reader.seek(SeekFrom::Start(header.contents_address));
    let content_table = read_content_table(reader, header.contents_address)?;

    // Textures; we know it's a tex bch, so no need to mess with flags 
    for index in 0..content_table.textures_ptr_table_entries {
        reader.seek(SeekFrom::Start(content_table.textures_ptr_table_offset + i * 4));
        reader.seek(SeekFrom::Start(reader.read_u32::<LittleEndian>()));

        let mut tex_unit0_commands_offset = reader.read_u32::<LittleEndian>()?;
        let mut tex_unit0_commands_word_count = reader.read_u32::<LittleEndian>()?;
        let mut tex_unit1_commands_offset = reader.read_u32::<LittleEndian>()?;
        let mut tex_unit1_commands_word_count = reader.read_u32::<LittleEndian>()?;
        let mut tex_unit2_commands_offset = reader.read_u32::<LittleEndian>()?;
        let mut tex_unit2_commands_word_count = reader.read_u32::<LittleEndian>()?;
        reader.read_u32::<LittleEndian>()?; // Don't know; might look at spica

        let mut texture_name = String::new();
        reader.read_to_string(&mut texture_name);    // prob could read exactly the number from Header.strings_length

        reader.seek(SeekFrom::Start(tex_unit0_commands_offset));
        let mut texture_commands = PICA_command_reader(reader, tex_unit0_commands_word_count);  // Incomplete
        
        reader.seek(SeekFrom::Start(get_tex_unit0_address()));  // Just pass 0x85 to get parameter ig

        let mut textureSize = get_tex_unit0_size()?;
        let mut buffer: [u8; textureSize.height * textureSize.width * 4];
        reader.read_exact(buffer);
        
        // The End
        // Just decode texture now and parse as bitmap
    }
}

fn read_header(reader: &mut Cursor<[u8]>) -> Result<Header> {
    let mut raw_ext_address = 0;
    let mut raw_ext_length = 0;

    let magic_ID: String = reader.read_u32::<LittleEndian>()?;
    if (magic_ID != "BCH") {
        Err("Invalid BCH file");
    }
    let backward_compatibility = reader.read_u32::<LittleEndian>()?;
    let forward_compatibility = reader.read_u32::<LittleEndian>()?;
    let version = reader.read_u16()?;
    let contents_address = reader.read_u32::<LittleEndian>()?;
    let strings_address = reader.read_u32::<LittleEndian>()?;
    let commands_address = reader.read_u32::<LittleEndian>()?;
    let raw_data_address = reader.read_u32::<LittleEndian>()?;
    if (backward_compatibility > 0x20) {
        raw_ext_address = reader.read_u32::<LittleEndian>()?;
    }
    let relocation_address = reader.read_u32::<LittleEndian>()?;
    let contents_length = reader.read_u32::<LittleEndian>()?;
    let strings_length = reader.read_u32::<LittleEndian>()?;
    let commands_length = reader.read_u32::<LittleEndian>()?;
    let raw_data_length = reader.read_u32::<LittleEndian>()?;
    if (backward_compatibility > 0x20){
        raw_ext_length = reader.read_u32::<LittleEndian>()?;
    }
    let relocation_length = reader.read_u32::<LittleEndian>()?;
    let unInit_data_length = reader.read_u32::<LittleEndian>()?;
    let unInit_commands_length = reader.read_u32::<LittleEndian>()?;

    Ok(Header{
        magic_ID,
        backward_compatibility,
        forward_compatibility,
        version,
        contents_address,
        strings_address,
        commands_address,
        raw_data_address,
        raw_ext_address,
        relocation_address,
        contents_length,
        strings_length,
        commands_length,
        raw_data_length,
        raw_ext_length,
        relocation_length,
        unInit_data_length,
        unInit_commands_length,
    })
}

fn read_content_table(reader: &mut Cursor<[u8]>, contents_address: u32) -> Result<ContentTable> {
    let models_ptr_table_offset = reader.read_u32::<LittleEndian>() + contents_address?;
    let models_ptr_table_entries = reader.read_u32::<LittleEndian>()?;

    reader.seek(SeekFrom::Start(contents_address + 0x24));
    let textures_ptr_table_offset = reader.read_u32::<LittleEndian>() + contents_address?;
    let textures_ptr_table_entries = reader.read_u32::<LittleEndian>()?;
    
    Ok(ContentTable{
        models_ptr_table_offset,
        models_ptr_table_entries,
        textures_ptr_table_offset,
        textures_ptr_table_entries,
    })
}

fn PICA_command_reader(reader: &mut Cursor<[u8]>, word_count: u32) {
    let mut words_read = 0;
    while words_read < word_count {
        let mut parameter = reader.read_u32::<LittleEndian>()?;
        let mut header = reader.read_u32::<LittleEndian>()?;
        words_read += 2;

        let mut id: u16 = header & 0xffff;
        let mut mask = (header >> 16) & 0xf;
        let mut extra_parameters = (header >> 20) & 0x7ff;
        let mut consecutive_writing  = (header & 0x80000000) > 0;
        
        /*
        I have to ignore this for now :(
        COMMANDS[id] = (get_parameter(id) & (-mask & 0xf) | (reader.read_u32::<LittleEndian>() & (0xfffffff0 | mask)));
        if (id == PICARegister::GPUREG_CMDBUF_JUMP1) {
            break;  // ?? Gonna question redudancy later
        }
        else if (id == PICARegister::GPUREG_VSH_FLOATUNIFORM_INDEX) {
            CURRENTUNIFORM = parameter & 0x7fffffff;
        }
        else if (id == PICARegister::GPUREG_VSH_FLOATUNIFORM_DATA0) {
            UNIFORM
        }
        else if (id == PICARegister::GPUREG_LIGHTING_LUT_DATA0) {

        }

        for i in 0..extraParameters {
            if (consecutive_writing) {
                id += 1;  // ??
        }
        COMMANDS[id] = (get_parameter(id) & (-mask & 0xf) | (reader.read_u32::<LittleEndian>() & (0xfffffff0 | mask)));
        words_read += 1;

        if (id > PICARegister::GPUREG_VSH_FLOATUNIFORM_INDEX && id < PICARegister::GPUREG_VSH_FLOATUNIFORM_DATA0 + 8) {
            // I NEED A LIST
        }
        else if (id == PICARegister::GPUREG_LIGHTING_LUT_DATA0)
        {
            // I NEED A LIST
        }
        */
        if (!false) {
            while ((reader.position() & 7) != 0) {
                reader.ReadUInt32();
            }
        }
    }
    
}

fn get_parameter(command_ID: &u16) -> Result<u32> {
    OK(COMMANDS[command_ID]);
}

fn get_tex_unit0_address() -> Result<u32> {
    OK(get_parameter(PICARegister::GPUREG_TEXUNIT0_ADDR1 as u16));
    
} 

fn get_tex_unit0_size() -> Result<Size> {
    let value: u32 = get_parameter(PICARegister::GPUREG_TEXUNIT0_DIM as u16);
    let height = value >> 16;
    let width = value & 0xffff;
    Ok(Size {
        height,
        width,
    })
    
}
enum PICARegister {
    GPUREG_DUMMY = 0x0000,
    GPUREG_FINALIZE = 0x0010,
    GPUREG_FACECULLING_CONFIG = 0x0040,
    GPUREG_VIEWPORT_WIDTH = 0x0041,
    GPUREG_VIEWPORT_INVW = 0x0042,
    GPUREG_VIEWPORT_HEIGHT = 0x0043,
    GPUREG_VIEWPORT_INVH = 0x0044,
    GPUREG_FRAGOP_CLIP = 0x0047,
    GPUREG_FRAGOP_CLIP_DATA0 = 0x0048,
    GPUREG_FRAGOP_CLIP_DATA1 = 0x0049,
    GPUREG_FRAGOP_CLIP_DATA2 = 0x004A,
    GPUREG_FRAGOP_CLIP_DATA3 = 0x004B,
    GPUREG_DEPTHMAP_SCALE = 0x004D,
    GPUREG_DEPTHMAP_OFFSET = 0x004E,
    GPUREG_SH_OUTMAP_TOTAL = 0x004F,
    GPUREG_SH_OUTMAP_O0 = 0x0050,
    GPUREG_SH_OUTMAP_O1 = 0x0051,
    GPUREG_SH_OUTMAP_O2 = 0x0052,
    GPUREG_SH_OUTMAP_O3 = 0x0053,
    GPUREG_SH_OUTMAP_O4 = 0x0054,
    GPUREG_SH_OUTMAP_O5 = 0x0055,
    GPUREG_SH_OUTMAP_O6 = 0x0056,
    GPUREG_EARLYDEPTH_FUNC = 0x0061,
    GPUREG_EARLYDEPTH_TEST1 = 0x0062,
    GPUREG_EARLYDEPTH_CLEAR = 0x0063,
    GPUREG_SH_OUTATTR_MODE = 0x0064,
    GPUREG_SCISSORTEST_MODE = 0x0065,
    GPUREG_SCISSORTEST_POS = 0x0066,
    GPUREG_SCISSORTEST_DIM = 0x0067,
    GPUREG_VIEWPORT_XY = 0x0068,
    GPUREG_EARLYDEPTH_DATA = 0x006A,
    GPUREG_DEPTHMAP_ENABLE = 0x006D,
    GPUREG_RENDERBUF_DIM = 0x006E,
    GPUREG_SH_OUTATTR_CLOCK = 0x006F,
    GPUREG_TEXUNIT_CONFIG = 0x0080,
    GPUREG_TEXUNIT0_BORDER_COLOR = 0x0081,
    GPUREG_TEXUNIT0_DIM = 0x0082,
    GPUREG_TEXUNIT0_PARAM = 0x0083,
    GPUREG_TEXUNIT0_LOD = 0x0084,
    GPUREG_TEXUNIT0_ADDR1 = 0x0085,
    GPUREG_TEXUNIT0_ADDR2 = 0x0086,
    GPUREG_TEXUNIT0_ADDR3 = 0x0087,
    GPUREG_TEXUNIT0_ADDR4 = 0x0088,
    GPUREG_TEXUNIT0_ADDR5 = 0x0089,
    GPUREG_TEXUNIT0_ADDR6 = 0x008A,
    GPUREG_TEXUNIT0_SHADOW = 0x008B,
    GPUREG_TEXUNIT0_TYPE = 0x008E,
    GPUREG_LIGHTING_ENABLE0 = 0x008F,
    GPUREG_TEXUNIT1_BORDER_COLOR = 0x0091,
    GPUREG_TEXUNIT1_DIM = 0x0092,
    GPUREG_TEXUNIT1_PARAM = 0x0093,
    GPUREG_TEXUNIT1_LOD = 0x0094,
    GPUREG_TEXUNIT1_ADDR = 0x0095,
    GPUREG_TEXUNIT1_TYPE = 0x0096,
    GPUREG_TEXUNIT2_BORDER_COLOR = 0x0099,
    GPUREG_TEXUNIT2_DIM = 0x009A,
    GPUREG_TEXUNIT2_PARAM = 0x009B,
    GPUREG_TEXUNIT2_LOD = 0x009C,
    GPUREG_TEXUNIT2_ADDR = 0x009D,
    GPUREG_TEXUNIT2_TYPE = 0x009E,
    GPUREG_TEXUNIT3_PROCTEX0 = 0x00A8,
    GPUREG_TEXUNIT3_PROCTEX1 = 0x00A9,
    GPUREG_TEXUNIT3_PROCTEX2 = 0x00AA,
    GPUREG_TEXUNIT3_PROCTEX3 = 0x00AB,
    GPUREG_TEXUNIT3_PROCTEX4 = 0x00AC,
    GPUREG_TEXUNIT3_PROCTEX5 = 0x00AD,
    GPUREG_PROCTEX_LUT = 0x00AF,
    GPUREG_PROCTEX_LUT_DATA0 = 0x00B0,
    GPUREG_PROCTEX_LUT_DATA1 = 0x00B1,
    GPUREG_PROCTEX_LUT_DATA2 = 0x00B2,
    GPUREG_PROCTEX_LUT_DATA3 = 0x00B3,
    GPUREG_PROCTEX_LUT_DATA4 = 0x00B4,
    GPUREG_PROCTEX_LUT_DATA5 = 0x00B5,
    GPUREG_PROCTEX_LUT_DATA6 = 0x00B6,
    GPUREG_PROCTEX_LUT_DATA7 = 0x00B7,
    GPUREG_TEXENV0_SOURCE = 0x00C0,
    GPUREG_TEXENV0_OPERAND = 0x00C1,
    GPUREG_TEXENV0_COMBINER = 0x00C2,
    GPUREG_TEXENV0_COLOR = 0x00C3,
    GPUREG_TEXENV0_SCALE = 0x00C4,
    GPUREG_TEXENV1_SOURCE = 0x00C8,
    GPUREG_TEXENV1_OPERAND = 0x00C9,
    GPUREG_TEXENV1_COMBINER = 0x00CA,
    GPUREG_TEXENV1_COLOR = 0x00CB,
    GPUREG_TEXENV1_SCALE = 0x00CC,
    GPUREG_TEXENV2_SOURCE = 0x00D0,
    GPUREG_TEXENV2_OPERAND = 0x00D1,
    GPUREG_TEXENV2_COMBINER = 0x00D2,
    GPUREG_TEXENV2_COLOR = 0x00D3,
    GPUREG_TEXENV2_SCALE = 0x00D4,
    GPUREG_TEXENV3_SOURCE = 0x00D8,
    GPUREG_TEXENV3_OPERAND = 0x00D9,
    GPUREG_TEXENV3_COMBINER = 0x00DA,
    GPUREG_TEXENV3_COLOR = 0x00DB,
    GPUREG_TEXENV3_SCALE = 0x00DC,
    GPUREG_TEXENV_UPDATE_BUFFER = 0x00E0,
    GPUREG_FOG_COLOR = 0x00E1,
    GPUREG_GAS_ATTENUATION = 0x00E4,
    GPUREG_GAS_ACCMAX = 0x00E5,
    GPUREG_FOG_LUT_INDEX = 0x00E6,
    GPUREG_FOG_LUT_DATA0 = 0x00E8,
    GPUREG_FOG_LUT_DATA1 = 0x00E9,
    GPUREG_FOG_LUT_DATA2 = 0x00EA,
    GPUREG_FOG_LUT_DATA3 = 0x00EB,
    GPUREG_FOG_LUT_DATA4 = 0x00EC,
    GPUREG_FOG_LUT_DATA5 = 0x00ED,
    GPUREG_FOG_LUT_DATA6 = 0x00EE,
    GPUREG_FOG_LUT_DATA7 = 0x00EF,
    GPUREG_TEXENV4_SOURCE = 0x00F0,
    GPUREG_TEXENV4_OPERAND = 0x00F1,
    GPUREG_TEXENV4_COMBINER = 0x00F2,
    GPUREG_TEXENV4_COLOR = 0x00F3,
    GPUREG_TEXENV4_SCALE = 0x00F4,
    GPUREG_TEXENV5_SOURCE = 0x00F8,
    GPUREG_TEXENV5_OPERAND = 0x00F9,
    GPUREG_TEXENV5_COMBINER = 0x00FA,
    GPUREG_TEXENV5_COLOR = 0x00FB,
    GPUREG_TEXENV5_SCALE = 0x00FC,
    GPUREG_TEXENV_BUFFER_COLOR = 0x00FD,
    GPUREG_COLOR_OPERATION = 0x0100,
    GPUREG_BLEND_FUNC = 0x0101,
    GPUREG_LOGIC_OP = 0x0102,
    GPUREG_BLEND_COLOR = 0x0103,
    GPUREG_FRAGOP_ALPHA_TEST = 0x0104,
    GPUREG_STENCIL_TEST = 0x0105,
    GPUREG_STENCIL_OP = 0x0106,
    GPUREG_DEPTH_COLOR_MASK = 0x0107,
    GPUREG_FRAMEBUFFER_INVALIDATE = 0x0110,
    GPUREG_FRAMEBUFFER_FLUSH = 0x0111,
    GPUREG_COLORBUFFER_READ = 0x0112,
    GPUREG_COLORBUFFER_WRITE = 0x0113,
    GPUREG_DEPTHBUFFER_READ = 0x0114,
    GPUREG_DEPTHBUFFER_WRITE = 0x0115,
    GPUREG_DEPTHBUFFER_FORMAT = 0x0116,
    GPUREG_COLORBUFFER_FORMAT = 0x0117,
    GPUREG_EARLYDEPTH_TEST2 = 0x0118,
    GPUREG_FRAMEBUFFER_BLOCK32 = 0x011B,
    GPUREG_DEPTHBUFFER_LOC = 0x011C,
    GPUREG_COLORBUFFER_LOC = 0x011D,
    GPUREG_FRAMEBUFFER_DIM = 0x011E,
    GPUREG_GAS_LIGHT_XY = 0x0120,
    GPUREG_GAS_LIGHT_Z = 0x0121,
    GPUREG_GAS_LIGHT_Z_COLOR = 0x0122,
    GPUREG_GAS_LUT_INDEX = 0x0123,
    GPUREG_GAS_LUT_DATA = 0x0124,
    GPUREG_GAS_DELTAZ_DEPTH = 0x0126,
    GPUREG_FRAGOP_SHADOW = 0x0130,
    GPUREG_LIGHT0_SPECULAR0 = 0x0140,
    GPUREG_LIGHT0_SPECULAR1 = 0x0141,
    GPUREG_LIGHT0_DIFFUSE = 0x0142,
    GPUREG_LIGHT0_AMBIENT = 0x0143,
    GPUREG_LIGHT0_XY = 0x0144,
    GPUREG_LIGHT0_Z = 0x0145,
    GPUREG_LIGHT0_SPOTDIR_XY = 0x0146,
    GPUREG_LIGHT0_SPOTDIR_Z = 0x0147,
    GPUREG_LIGHT0_CONFIG = 0x0149,
    GPUREG_LIGHT0_ATTENUATION_BIAS = 0x014A,
    GPUREG_LIGHT0_ATTENUATION_SCALE = 0x014B,
    GPUREG_LIGHT1_SPECULAR0 = 0x0150,
    GPUREG_LIGHT1_SPECULAR1 = 0x0151,
    GPUREG_LIGHT1_DIFFUSE = 0x0152,
    GPUREG_LIGHT1_AMBIENT = 0x0153,
    GPUREG_LIGHT1_XY = 0x0154,
    GPUREG_LIGHT1_Z = 0x0155,
    GPUREG_LIGHT1_SPOTDIR_XY = 0x0156,
    GPUREG_LIGHT1_SPOTDIR_Z = 0x0157,
    GPUREG_LIGHT1_CONFIG = 0x0159,
    GPUREG_LIGHT1_ATTENUATION_BIAS = 0x015A,
    GPUREG_LIGHT1_ATTENUATION_SCALE = 0x015B,
    GPUREG_LIGHT2_SPECULAR0 = 0x0160,
    GPUREG_LIGHT2_SPECULAR1 = 0x0161,
    GPUREG_LIGHT2_DIFFUSE = 0x0162,
    GPUREG_LIGHT2_AMBIENT = 0x0163,
    GPUREG_LIGHT2_XY = 0x0164,
    GPUREG_LIGHT2_Z = 0x0165,
    GPUREG_LIGHT2_SPOTDIR_XY = 0x0166,
    GPUREG_LIGHT2_SPOTDIR_Z = 0x0167,
    GPUREG_LIGHT2_CONFIG = 0x0169,
    GPUREG_LIGHT2_ATTENUATION_BIAS = 0x016A,
    GPUREG_LIGHT2_ATTENUATION_SCALE = 0x016B,
    GPUREG_LIGHT3_SPECULAR0 = 0x0170,
    GPUREG_LIGHT3_SPECULAR1 = 0x0171,
    GPUREG_LIGHT3_DIFFUSE = 0x0172,
    GPUREG_LIGHT3_AMBIENT = 0x0173,
    GPUREG_LIGHT3_XY = 0x0174,
    GPUREG_LIGHT3_Z = 0x0175,
    GPUREG_LIGHT3_SPOTDIR_XY = 0x0176,
    GPUREG_LIGHT3_SPOTDIR_Z = 0x0177,
    GPUREG_LIGHT3_CONFIG = 0x0179,
    GPUREG_LIGHT3_ATTENUATION_BIAS = 0x017A,
    GPUREG_LIGHT3_ATTENUATION_SCALE = 0x017B,
    GPUREG_LIGHT4_SPECULAR0 = 0x0180,
    GPUREG_LIGHT4_SPECULAR1 = 0x0181,
    GPUREG_LIGHT4_DIFFUSE = 0x0182,
    GPUREG_LIGHT4_AMBIENT = 0x0183,
    GPUREG_LIGHT4_XY = 0x0184,
    GPUREG_LIGHT4_Z = 0x0185,
    GPUREG_LIGHT4_SPOTDIR_XY = 0x0186,
    GPUREG_LIGHT4_SPOTDIR_Z = 0x0187,
    GPUREG_LIGHT4_CONFIG = 0x0189,
    GPUREG_LIGHT4_ATTENUATION_BIAS = 0x018A,
    GPUREG_LIGHT4_ATTENUATION_SCALE = 0x018B,
    GPUREG_LIGHT5_SPECULAR0 = 0x0190,
    GPUREG_LIGHT5_SPECULAR1 = 0x0191,
    GPUREG_LIGHT5_DIFFUSE = 0x0192,
    GPUREG_LIGHT5_AMBIENT = 0x0193,
    GPUREG_LIGHT5_XY = 0x0194,
    GPUREG_LIGHT5_Z = 0x0195,
    GPUREG_LIGHT5_SPOTDIR_XY = 0x0196,
    GPUREG_LIGHT5_SPOTDIR_Z = 0x0197,
    GPUREG_LIGHT5_CONFIG = 0x0199,
    GPUREG_LIGHT5_ATTENUATION_BIAS = 0x019A,
    GPUREG_LIGHT5_ATTENUATION_SCALE = 0x019B,
    GPUREG_LIGHT6_SPECULAR0 = 0x01A0,
    GPUREG_LIGHT6_SPECULAR1 = 0x01A1,
    GPUREG_LIGHT6_DIFFUSE = 0x01A2,
    GPUREG_LIGHT6_AMBIENT = 0x01A3,
    GPUREG_LIGHT6_XY = 0x01A4,
    GPUREG_LIGHT6_Z = 0x01A5,
    GPUREG_LIGHT6_SPOTDIR_XY = 0x01A6,
    GPUREG_LIGHT6_SPOTDIR_Z = 0x01A7,
    GPUREG_LIGHT6_CONFIG = 0x01A9,
    GPUREG_LIGHT6_ATTENUATION_BIAS = 0x01AA,
    GPUREG_LIGHT6_ATTENUATION_SCALE = 0x01AB,
    GPUREG_LIGHT7_SPECULAR0 = 0x01B0,
    GPUREG_LIGHT7_SPECULAR1 = 0x01B1,
    GPUREG_LIGHT7_DIFFUSE = 0x01B2,
    GPUREG_LIGHT7_AMBIENT = 0x01B3,
    GPUREG_LIGHT7_XY = 0x01B4,
    GPUREG_LIGHT7_Z = 0x01B5,
    GPUREG_LIGHT7_SPOTDIR_XY = 0x01B6,
    GPUREG_LIGHT7_SPOTDIR_Z = 0x01B7,
    GPUREG_LIGHT7_CONFIG = 0x01B9,
    GPUREG_LIGHT7_ATTENUATION_BIAS = 0x01BA,
    GPUREG_LIGHT7_ATTENUATION_SCALE = 0x01BB,
    GPUREG_LIGHTING_AMBIENT = 0x01C0,
    GPUREG_LIGHTING_NUM_LIGHTS = 0x01C2,
    GPUREG_LIGHTING_CONFIG0 = 0x01C3,
    GPUREG_LIGHTING_CONFIG1 = 0x01C4,
    GPUREG_LIGHTING_LUT_INDEX = 0x01C5,
    GPUREG_LIGHTING_ENABLE1 = 0x01C6,
    GPUREG_LIGHTING_LUT_DATA0 = 0x01C8,
    GPUREG_LIGHTING_LUT_DATA1 = 0x01C9,
    GPUREG_LIGHTING_LUT_DATA2 = 0x01CA,
    GPUREG_LIGHTING_LUT_DATA3 = 0x01CB,
    GPUREG_LIGHTING_LUT_DATA4 = 0x01CC,
    GPUREG_LIGHTING_LUT_DATA5 = 0x01CD,
    GPUREG_LIGHTING_LUT_DATA6 = 0x01CE,
    GPUREG_LIGHTING_LUT_DATA7 = 0x01CF,
    GPUREG_LIGHTING_LUTINPUT_ABS = 0x01D0,
    GPUREG_LIGHTING_LUTINPUT_SELECT = 0x01D1,
    GPUREG_LIGHTING_LUTINPUT_SCALE = 0x01D2,
    GPUREG_LIGHTING_LIGHT_PERMUTATION = 0x01D9,
    GPUREG_ATTRIBBUFFERS_LOC = 0x0200,
    GPUREG_ATTRIBBUFFERS_FORMAT_LOW = 0x0201,
    GPUREG_ATTRIBBUFFERS_FORMAT_HIGH = 0x0202,
    GPUREG_ATTRIBBUFFER0_OFFSET = 0x0203,
    GPUREG_ATTRIBBUFFER0_CONFIG1 = 0x0204,
    GPUREG_ATTRIBBUFFER0_CONFIG2 = 0x0205,
    GPUREG_ATTRIBBUFFER1_OFFSET = 0x0206,
    GPUREG_ATTRIBBUFFER1_CONFIG1 = 0x0207,
    GPUREG_ATTRIBBUFFER1_CONFIG2 = 0x0208,
    GPUREG_ATTRIBBUFFER2_OFFSET = 0x0209,
    GPUREG_ATTRIBBUFFER2_CONFIG1 = 0x020A,
    GPUREG_ATTRIBBUFFER2_CONFIG2 = 0x020B,
    GPUREG_ATTRIBBUFFER3_OFFSET = 0x020C,
    GPUREG_ATTRIBBUFFER3_CONFIG1 = 0x020D,
    GPUREG_ATTRIBBUFFER3_CONFIG2 = 0x020E,
    GPUREG_ATTRIBBUFFER4_OFFSET = 0x020F,
    GPUREG_ATTRIBBUFFER4_CONFIG1 = 0x0210,
    GPUREG_ATTRIBBUFFER4_CONFIG2 = 0x0211,
    GPUREG_ATTRIBBUFFER5_OFFSET = 0x0212,
    GPUREG_ATTRIBBUFFER5_CONFIG1 = 0x0213,
    GPUREG_ATTRIBBUFFER5_CONFIG2 = 0x0214,
    GPUREG_ATTRIBBUFFER6_OFFSET = 0x0215,
    GPUREG_ATTRIBBUFFER6_CONFIG1 = 0x0216,
    GPUREG_ATTRIBBUFFER6_CONFIG2 = 0x0217,
    GPUREG_ATTRIBBUFFER7_OFFSET = 0x0218,
    GPUREG_ATTRIBBUFFER7_CONFIG1 = 0x0219,
    GPUREG_ATTRIBBUFFER7_CONFIG2 = 0x021A,
    GPUREG_ATTRIBBUFFER8_OFFSET = 0x021B,
    GPUREG_ATTRIBBUFFER8_CONFIG1 = 0x021C,
    GPUREG_ATTRIBBUFFER8_CONFIG2 = 0x021D,
    GPUREG_ATTRIBBUFFER9_OFFSET = 0x021E,
    GPUREG_ATTRIBBUFFER9_CONFIG1 = 0x021F,
    GPUREG_ATTRIBBUFFER9_CONFIG2 = 0x0220,
    GPUREG_ATTRIBBUFFER10_OFFSET = 0x0221,
    GPUREG_ATTRIBBUFFER10_CONFIG1 = 0x0222,
    GPUREG_ATTRIBBUFFER10_CONFIG2 = 0x0223,
    GPUREG_ATTRIBBUFFER11_OFFSET = 0x0224,
    GPUREG_ATTRIBBUFFER11_CONFIG1 = 0x0225,
    GPUREG_ATTRIBBUFFER11_CONFIG2 = 0x0226,
    GPUREG_INDEXBUFFER_CONFIG = 0x0227,
    GPUREG_NUMVERTICES = 0x0228,
    GPUREG_GEOSTAGE_CONFIG = 0x0229,
    GPUREG_VERTEX_OFFSET = 0x022A,
    GPUREG_POST_VERTEX_CACHE_NUM = 0x022D,
    GPUREG_DRAWARRAYS = 0x022E,
    GPUREG_DRAWELEMENTS = 0x022F,
    GPUREG_VTX_FUNC = 0x0231,
    GPUREG_FIXEDATTRIB_INDEX = 0x0232,
    GPUREG_FIXEDATTRIB_DATA0 = 0x0233,
    GPUREG_FIXEDATTRIB_DATA1 = 0x0234,
    GPUREG_FIXEDATTRIB_DATA2 = 0x0235,
    GPUREG_CMDBUF_SIZE0 = 0x0238,
    GPUREG_CMDBUF_SIZE1 = 0x0239,
    GPUREG_CMDBUF_ADDR0 = 0x023A,
    GPUREG_CMDBUF_ADDR1 = 0x023B,
    GPUREG_CMDBUF_JUMP0 = 0x023C,
    GPUREG_CMDBUF_JUMP1 = 0x023D,
    GPUREG_VSH_NUM_ATTR = 0x0242,
    GPUREG_VSH_COM_MODE = 0x0244,
    GPUREG_START_DRAW_FUNC0 = 0x0245,
    GPUREG_VSH_OUTMAP_TOTAL1 = 0x024A,
    GPUREG_VSH_OUTMAP_TOTAL2 = 0x0251,
    GPUREG_GSH_MISC0 = 0x0252,
    GPUREG_GEOSTAGE_CONFIG2 = 0x0253,
    GPUREG_GSH_MISC1 = 0x0254,
    GPUREG_PRIMITIVE_CONFIG = 0x025E,
    GPUREG_RESTART_PRIMITIVE = 0x025F,
    GPUREG_GSH_BOOLUNIFORM = 0x0280,
    GPUREG_GSH_INTUNIFORM_I0 = 0x0281,
    GPUREG_GSH_INTUNIFORM_I1 = 0x0282,
    GPUREG_GSH_INTUNIFORM_I2 = 0x0283,
    GPUREG_GSH_INTUNIFORM_I3 = 0x0284,
    GPUREG_GSH_INPUTBUFFER_CONFIG = 0x0289,
    GPUREG_GSH_ENTRYPOINT = 0x028A,
    GPUREG_GSH_ATTRIBUTES_PERMUTATION_LOW = 0x028B,
    GPUREG_GSH_ATTRIBUTES_PERMUTATION_HIGH = 0x028C,
    GPUREG_GSH_OUTMAP_MASK = 0x028D,
    GPUREG_GSH_CODETRANSFER_END = 0x028F,
    GPUREG_GSH_FLOATUNIFORM_INDEX = 0x0290,
    GPUREG_GSH_FLOATUNIFORM_DATA0 = 0x0291,
    GPUREG_GSH_FLOATUNIFORM_DATA1 = 0x0292,
    GPUREG_GSH_FLOATUNIFORM_DATA2 = 0x0293,
    GPUREG_GSH_FLOATUNIFORM_DATA3 = 0x0294,
    GPUREG_GSH_FLOATUNIFORM_DATA4 = 0x0295,
    GPUREG_GSH_FLOATUNIFORM_DATA5 = 0x0296,
    GPUREG_GSH_FLOATUNIFORM_DATA6 = 0x0297,
    GPUREG_GSH_FLOATUNIFORM_DATA7 = 0x0298,
    GPUREG_GSH_CODETRANSFER_INDEX = 0x029B,
    GPUREG_GSH_CODETRANSFER_DATA0 = 0x029C,
    GPUREG_GSH_CODETRANSFER_DATA1 = 0x029D,
    GPUREG_GSH_CODETRANSFER_DATA2 = 0x029E,
    GPUREG_GSH_CODETRANSFER_DATA3 = 0x029F,
    GPUREG_GSH_CODETRANSFER_DATA4 = 0x02A0,
    GPUREG_GSH_CODETRANSFER_DATA5 = 0x02A1,
    GPUREG_GSH_CODETRANSFER_DATA6 = 0x02A2,
    GPUREG_GSH_CODETRANSFER_DATA7 = 0x02A3,
    GPUREG_GSH_OPDESCS_INDEX = 0x02A5,
    GPUREG_GSH_OPDESCS_DATA0 = 0x02A6,
    GPUREG_GSH_OPDESCS_DATA1 = 0x02A7,
    GPUREG_GSH_OPDESCS_DATA2 = 0x02A8,
    GPUREG_GSH_OPDESCS_DATA3 = 0x02A9,
    GPUREG_GSH_OPDESCS_DATA4 = 0x02AA,
    GPUREG_GSH_OPDESCS_DATA5 = 0x02AB,
    GPUREG_GSH_OPDESCS_DATA6 = 0x02AC,
    GPUREG_GSH_OPDESCS_DATA7 = 0x02AD,
    GPUREG_VSH_BOOLUNIFORM = 0x02B0,
    GPUREG_VSH_INTUNIFORM_I0 = 0x02B1,
    GPUREG_VSH_INTUNIFORM_I1 = 0x02B2,
    GPUREG_VSH_INTUNIFORM_I2 = 0x02B3,
    GPUREG_VSH_INTUNIFORM_I3 = 0x02B4,
    GPUREG_VSH_INPUTBUFFER_CONFIG = 0x02B9,
    GPUREG_VSH_ENTRYPOINT = 0x02BA,
    GPUREG_VSH_ATTRIBUTES_PERMUTATION_LOW = 0x02BB,
    GPUREG_VSH_ATTRIBUTES_PERMUTATION_HIGH = 0x02BC,
    GPUREG_VSH_OUTMAP_MASK = 0x02BD,
    GPUREG_VSH_CODETRANSFER_END = 0x02BF,
    GPUREG_VSH_FLOATUNIFORM_INDEX = 0x02C0,
    GPUREG_VSH_FLOATUNIFORM_DATA0 = 0x02C1,
    GPUREG_VSH_FLOATUNIFORM_DATA1 = 0x02C2,
    GPUREG_VSH_FLOATUNIFORM_DATA2 = 0x02C3,
    GPUREG_VSH_FLOATUNIFORM_DATA3 = 0x02C4,
    GPUREG_VSH_FLOATUNIFORM_DATA4 = 0x02C5,
    GPUREG_VSH_FLOATUNIFORM_DATA5 = 0x02C6,
    GPUREG_VSH_FLOATUNIFORM_DATA6 = 0x02C7,
    GPUREG_VSH_FLOATUNIFORM_DATA7 = 0x02C8,
    GPUREG_VSH_CODETRANSFER_INDEX = 0x02CB,
    GPUREG_VSH_CODETRANSFER_DATA0 = 0x02CC,
    GPUREG_VSH_CODETRANSFER_DATA1 = 0x02CD,
    GPUREG_VSH_CODETRANSFER_DATA2 = 0x02CE,
    GPUREG_VSH_CODETRANSFER_DATA3 = 0x02CF,
    GPUREG_VSH_CODETRANSFER_DATA4 = 0x02D0,
    GPUREG_VSH_CODETRANSFER_DATA5 = 0x02D1,
    GPUREG_VSH_CODETRANSFER_DATA6 = 0x02D2,
    GPUREG_VSH_CODETRANSFER_DATA7 = 0x02D3,
    GPUREG_VSH_OPDESCS_INDEX = 0x02D5,
    GPUREG_VSH_OPDESCS_DATA0 = 0x02D6,
    GPUREG_VSH_OPDESCS_DATA1 = 0x02D7,
    GPUREG_VSH_OPDESCS_DATA2 = 0x02D8,
    GPUREG_VSH_OPDESCS_DATA3 = 0x02D9,
    GPUREG_VSH_OPDESCS_DATA4 = 0x02DA,
    GPUREG_VSH_OPDESCS_DATA5 = 0x02DB,
    GPUREG_VSH_OPDESCS_DATA6 = 0x02DC,
    GPUREG_VSH_OPDESCS_DATA7 = 0x02DD
}