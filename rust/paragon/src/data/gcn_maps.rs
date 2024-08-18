use anyhow::{anyhow, bail, Result};
use mila::{BinArchive, BinArchiveReader, Endian, Game, LayeredFilesystem};
use std::collections::HashMap;

use crate::model::gcn_map_data::GcnMapData;

use super::archives::Archives;

pub struct GcnMaps {
    game: Game,
    maps: HashMap<String, GcnMapData>,
}

impl GcnMaps {
    pub fn new(game: Game) -> Self {
        Self {
            game,
            maps: Default::default(),
        }
    }

    pub fn load(
        &mut self,
        fs: &LayeredFilesystem,
        archives: &mut Archives,
        map: &str,
    ) -> Result<GcnMapData> {
        if let Some(data) = self.maps.get(map).cloned() {
            return Ok(data);
        }

        let cmp_path = format!("zmap/{}/map.cmp", map);
        let raw = archives.load_file(fs, &cmp_path, "map.bin")?;
        let bin_archive = BinArchive::from_bytes(raw, Endian::Big)?;

        let data = match self.game {
            Game::FE9 => self.load_fe9(&bin_archive)?,
            Game::FE10 => self.load_fe10(&bin_archive, map)?,
            _ => bail!("unsupported game {:?}", self.game),
        };

        self.maps.insert(map.to_string(), data.clone());
        Ok(data)
    }

    fn load_fe9(&self, bin_archive: &BinArchive) -> Result<GcnMapData> {
        let mut reader = BinArchiveReader::new(bin_archive, 0);
        let width = reader.read_u16()? as usize;
        let height = reader.read_u16()? as usize;
        let margin = reader.read_u16()? as usize;
        let label_address = bin_archive
            .find_label_address("panelindex")
            .ok_or_else(|| anyhow!("Could not locate panelindex section"))?;
        reader.seek(label_address);
        let mut tiles = vec![];
        for _ in 0..(width * height) {
            tiles.push(reader.read_u16()?);
        }

        let unique_panel_address = bin_archive
            .find_label_address("uniquepanel")
            .ok_or_else(|| anyhow!("Could not locate uniquepanel section"))?;
        reader.seek(unique_panel_address);
        let mut tile_info = vec![];
        loop {
            reader.skip(8);
            tile_info.push(reader.read_c_string()?);
            if reader.read_labels()?.is_some() {
                break;
            }
        }

        Ok(GcnMapData {
            width,
            height,
            margin,
            tiles: tiles
                .into_iter()
                .map(|tile_index| tile_info.get(tile_index as usize).cloned())
                .map(|tile_name| tile_name.flatten())
                .collect(),
        })
    }

    fn load_fe10(&self, bin_archive: &BinArchive, map: &str) -> Result<GcnMapData> {
        let mut reader = BinArchiveReader::new(bin_archive, 2);
        let width = reader.read_u8()? as usize;
        let height = reader.read_u8()? as usize;
        reader.seek(17);
        let margin = reader.read_u8()? as usize;
        let label_address = bin_archive
            .find_label_address(&format!("{}:panelindex", map))
            .ok_or_else(|| anyhow!("Could not locate panelindex section"))?;
        reader.seek(label_address);
        let mut tiles = vec![];
        for _ in 0..(width * height) {
            tiles.push(reader.read_u16()?);
        }

        let unique_panel_address = bin_archive
        .find_label_address(&format!("{}:uniquepanel", map))
            .ok_or_else(|| anyhow!("Could not locate uniquepanel section"))?;
        reader.seek(unique_panel_address);
        let mut tile_info = vec![];
        loop {
            reader.skip(8);
            tile_info.push(reader.read_c_string()?);
            if reader.read_labels()?.is_some() {
                break;
            }
        }

        Ok(GcnMapData {
            width,
            height,
            margin,
            tiles: tiles
                .into_iter()
                .map(|tile_index| tile_info.get(tile_index as usize).cloned())
                .map(|tile_name| tile_name.flatten())
                .collect(),
        })
    }
}
