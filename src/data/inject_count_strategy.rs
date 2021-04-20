use serde::Deserialize;
use super::inject_location_strategy::LocationStrategy;

#[derive(Debug, Clone, Deserialize)]
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
pub enum CountStrategy {
    Standard(StandardCountStrategy),
}