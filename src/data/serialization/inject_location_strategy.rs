use mila::BinArchive;
use serde::Deserialize;

#[derive(Debug, Clone, Deserialize)]
pub struct StaticLocationStrategy {
    address: usize,
}

#[derive(Debug, Clone, Deserialize)]
pub struct LabelLocationStrategy {
    label: String,
    offset: usize,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(rename_all = "snake_case", tag = "type")]
pub enum LocationStrategy {
    Label(LabelLocationStrategy),
    Static(StaticLocationStrategy),
}

macro_rules! on_location_strategy {
    ($on:ident, $with:ident, $body:tt) => {
        match $on {
            LocationStrategy::Label($with) => $body,
            LocationStrategy::Static($with) => $body,
        }
    };
}

impl StaticLocationStrategy {
    pub fn apply(&self, _archive: &BinArchive) -> anyhow::Result<usize> {
        Ok(self.address)
    }
}

impl LabelLocationStrategy {
    pub fn apply(&self, archive: &BinArchive) -> anyhow::Result<usize> {
        Ok(archive
            .find_label_address(&self.label)
            .ok_or_else(|| anyhow::anyhow!(
                "Label '{}' does not exist in the archive.",
                self.label
            ))?
            + self.offset)
    }
}

impl LocationStrategy {
    pub fn apply(&self, archive: &BinArchive) -> anyhow::Result<usize> {
        on_location_strategy!(self, ls, { ls.apply(archive) })
    }
}
