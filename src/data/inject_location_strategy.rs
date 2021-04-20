use serde::Deserialize;

#[derive(Debug, Clone, Deserialize)]
pub struct StaticLocationStrategy {
    address: usize,
}

#[derive(Debug, Clone, Deserialize)]
pub struct LabelLocationStrategy {
    label: String,
}

#[derive(Debug, Clone, Deserialize)]
pub enum LocationStrategy {
    Label(LabelLocationStrategy),
    Static(StaticLocationStrategy),
}