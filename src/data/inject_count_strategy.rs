use super::inject_location_strategy::LocationStrategy;
use anyhow::Context;
use mila::BinArchive;
use serde::Deserialize;

#[derive(Debug, Clone, Copy, Deserialize)]
#[serde(rename_all = "snake_case")]
enum CountFormat {
    U8,
    U16,
    U32,
}

#[derive(Debug, Clone, Deserialize)]
pub struct StandardCountStrategy {
    location: LocationStrategy,
    format: CountFormat,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(rename_all = "snake_case", tag = "type")]
pub enum CountStrategy {
    Standard(StandardCountStrategy),
}

macro_rules! on_count_strategy {
    ($on:ident, $with:ident, $body:tt) => {
        match $on {
            CountStrategy::Standard($with) => $body,
        }
    };
}

impl StandardCountStrategy {
    pub fn apply(&self, archive: &BinArchive) -> anyhow::Result<usize> {
        let address = self.location.apply(archive)?;
        let address = match self.format {
            CountFormat::U8 => archive.read_u8(address).map(|v| v as usize),
            CountFormat::U16 => archive.read_u16(address).map(|v| v as usize),
            CountFormat::U32 => archive.read_u32(address).map(|v| v as usize),
        }?;
        Ok(address)
    }

    pub fn write(&self, archive: &mut BinArchive, count: usize) -> anyhow::Result<()> {
        let address = self.location.apply(archive)?;
        match self.format {
            CountFormat::U8 => archive.write_u8(address, count as u8)?,
            CountFormat::U16 => archive.write_u16(address, count as u16)?,
            CountFormat::U32 => archive.write_u32(address, count as u32)?,
        }
        Ok(())
    }
}

impl CountStrategy {
    pub fn apply(&self, archive: &BinArchive) -> anyhow::Result<usize> {
        on_count_strategy!(self, cs, { cs.apply(archive) })
            .context("Failed to apply count strategy to archive.")
    }

    pub fn write(&self, archive: &mut BinArchive, count: usize) -> anyhow::Result<()> {
        on_count_strategy!(self, cs, { cs.write(archive, count) })
            .context("Failed to write count to archive.")
    }
}
