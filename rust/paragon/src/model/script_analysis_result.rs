use pyo3::prelude::*;

#[pyclass(hash, eq, frozen)]
#[derive(Debug, Clone, Hash, PartialEq, Eq)]
pub struct DiagnosticLocation {
    #[pyo3(get)]
    pub file: Option<String>,

    #[pyo3(get)]
    pub span: (usize, usize),

    #[pyo3(get)]
    pub line_number: usize,

    #[pyo3(get)]
    pub index_in_line: usize,
}

#[pyclass(hash, eq, frozen)]
#[derive(Debug, Clone, Hash, PartialEq, Eq)]
pub struct Diagnostic {
    #[pyo3(get)]
    pub message: String,
    #[pyo3(get)]
    pub location: Option<DiagnosticLocation>,
}

#[pyclass]
#[derive(Default, Debug, Clone)]
pub struct ScriptAnalysisResult {
    pub errors: Vec<Diagnostic>,
    pub warnings: Vec<Diagnostic>,
}

#[pymethods]
impl ScriptAnalysisResult {
    pub fn get_errors(&self) -> Vec<Diagnostic> {
        self.errors.clone()
    }

    pub fn get_warnings(&self) -> Vec<Diagnostic> {
        self.warnings.clone()
    }
}