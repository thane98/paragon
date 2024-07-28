use std::cmp::Ordering;
use std::fmt::Display;

use pyo3::prelude::*;

fn normalize_slashes(path: &str) -> String {
    if cfg!(windows) {
        path.replace('/', "\\")
    } else {
        path.to_string()
    }
}

#[pyclass(eq, hash, frozen)]
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct ScriptNode {
    #[pyo3(get)]
    pub path: String,
    pub kind: ScriptNodeKind,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub enum ScriptNodeKind {
    CompileTarget,
    UserLibrary,
    StandardLibrary,
}

impl Display for ScriptNodeKind {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.write_str(match self {
            ScriptNodeKind::CompileTarget => "compile_target",
            ScriptNodeKind::UserLibrary => "user_library",
            ScriptNodeKind::StandardLibrary => "standard_library",
        })
    }
}

impl ScriptNode {
    pub fn standard_library(path_from_category_root: String) -> Self {
        ScriptNode {
            path: normalize_slashes(&path_from_category_root),
            kind: ScriptNodeKind::StandardLibrary,
        }
    }

    pub fn user_library(path_from_category_root: String) -> Self {
        ScriptNode {
            path: normalize_slashes(&path_from_category_root),
            kind: ScriptNodeKind::UserLibrary,
        }
    }

    pub fn compiled(path_from_category_root: String) -> Self {
        ScriptNode {
            path: normalize_slashes(&path_from_category_root),
            kind: ScriptNodeKind::CompileTarget,
        }
    }
}

#[pymethods]
impl ScriptNode {
    pub fn kind(&self) -> String {
        self.kind.to_string()
    }
}

impl PartialOrd for ScriptNode {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl Ord for ScriptNode {
    fn cmp(&self, other: &Self) -> Ordering {
        match self.kind.cmp(&other.kind) {
            Ordering::Equal => self.path.cmp(&other.path),
            ord => ord,
        }
    }
}
