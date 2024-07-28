use pyo3::prelude::*;

use super::script_analysis_result::ScriptAnalysisResult;

#[pyclass]
pub struct SaveResult {
    #[pyo3(get)]
    pub script_compile_result: ScriptAnalysisResult,
}
