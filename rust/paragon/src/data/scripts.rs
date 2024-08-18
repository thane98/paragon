use std::collections::{BTreeSet, HashMap, HashSet};
use std::path::{Path, PathBuf};

use anyhow::{anyhow, bail, Result};
use exalt_completions::CompletionServer;
use normpath::PathExt;

use exalt_ast::{FileId, Literal, Location};
use exalt_compiler::{CompileRequest, CompilerError, CompilerLog, ParseRequest};
use exalt_decompiler::IrTransform;
use mila::Game;
use mila::LayeredFilesystem;

use crate::model::script_analysis_result::{Diagnostic, ScriptAnalysisResult};
use crate::model::script_node::{ScriptNode, ScriptNodeKind};
use crate::util::utf16_diagnostic_map::Utf16DiagnosticMap;

const MIRROR_FOLDER: &str = "exalt/scripts";
const USER_LIBRARY_FOLDER: &str = "exalt/libs";
const STANDARD_LIBRARY_FOLDER: &str = "resources/exalt";

fn get_standard_library_prelude(game: exalt_lir::Game) -> Option<PathBuf> {
    let path = Path::new(STANDARD_LIBRARY_FOLDER)
        .join("std")
        .join(format!("{:?}", game).to_lowercase())
        .join("prelude.exl");
    path.is_file().then_some(path)
}

fn load_decompiler_transform(game: exalt_lir::Game) -> Result<Option<IrTransform>> {
    if let Some(target) = get_standard_library_prelude(game) {
        // Load std lib files
        if !target.is_file() {
            println!(
                "WARNING: could not find std library at path '{}'",
                target.display()
            );
            return Ok(None);
        }
        let parse_result = exalt_compiler::parse(&ParseRequest {
            game,
            target,
            source: None,
            additional_includes: Default::default(),
        })?;
        let symbol_table = parse_result.symbol_table;

        // Populate the transform from the symbol table
        let mut transform = IrTransform::default();
        for constant in symbol_table.constants() {
            let c = constant.borrow();
            if let Literal::Str(s) = &c.value {
                transform.strings.insert(s.clone(), c.name.clone());
            }
        }
        for (k, v) in symbol_table.aliases() {
            // Flip because aliases are key=friendly name, value=internal name
            transform.functions.insert(v, k);
        }
        if let Some(symbol) = symbol_table.lookup_enum("Event") {
            let e = symbol.borrow();
            for (name, variant) in &e.variants {
                if let Literal::Int(i) = &variant.value {
                    transform
                        .events
                        .insert(*i as usize, format!("Event.{}", name));
                }
            }
        }
        Ok(Some(transform))
    } else {
        Ok(None)
    }
}

fn get_index_mapping<'a>(
    cache: &'a mut HashMap<FileId, Utf16DiagnosticMap>,
    log: &'a CompilerLog,
    file_id: FileId,
) -> &'a Utf16DiagnosticMap {
    cache.entry(file_id).or_insert_with(|| {
        log.files
            .get(file_id)
            .ok()
            .map(|file| Utf16DiagnosticMap::from_source(file.source()))
            .unwrap_or_default()
    })
}

fn extract_log(log: &CompilerLog) -> ScriptAnalysisResult {
    let mut index_conversions: HashMap<FileId, Utf16DiagnosticMap> = HashMap::new();
    ScriptAnalysisResult {
        errors: log
            .errors
            .iter()
            .map(|e| Diagnostic {
                message: e.message().to_string(),
                location: e.location().and_then(|l| match l {
                    Location::Source(file_id, r) => get_index_mapping(
                        &mut index_conversions,
                        log,
                        *file_id,
                    )
                    .get_location(log.file(*file_id)?, r.start, r.end),
                    Location::Generated => None,
                    _ => None,
                }),
            })
            .collect(),
        warnings: log
            .warnings
            .iter()
            .map(|e| Diagnostic {
                message: e.message().to_string(),
                location: Some(e.location()).and_then(|l| match l {
                    Location::Source(file_id, r) => get_index_mapping(
                        &mut index_conversions,
                        log,
                        *file_id,
                    )
                    .get_location(log.file(*file_id)?, r.start, r.end),
                    Location::Generated => None,
                    _ => None,
                }),
            })
            .collect(),
    }
}

pub struct Scripts {
    exalt_game: exalt_lir::Game,
    scripts_to_compile: HashSet<ScriptNode>,
    completion_server: CompletionServer,
}

impl Scripts {
    pub fn new(game: Game) -> Self {
        Scripts {
            exalt_game: match game {
                Game::FE9 => exalt_lir::Game::FE9,
                Game::FE10 => exalt_lir::Game::FE10,
                Game::FE11 => exalt_lir::Game::FE11,
                Game::FE12 => exalt_lir::Game::FE12,
                Game::FE13 => exalt_lir::Game::FE13,
                Game::FE14 => exalt_lir::Game::FE14,
                Game::FE15 => exalt_lir::Game::FE15,
            },
            scripts_to_compile: Default::default(),
            completion_server: CompletionServer::default(),
        }
    }

    fn get_compiled_script_root(&self) -> &str {
        "Scripts"
    }

    pub fn get_nodes(&self, fs: &LayeredFilesystem) -> BTreeSet<ScriptNode> {
        let standard_libary_glob = Path::new(STANDARD_LIBRARY_FOLDER)
            .join("**/*.exl")
            .to_string_lossy()
            .to_string();
        let mut nodes: BTreeSet<ScriptNode> = glob::glob(&standard_libary_glob)
            .into_iter()
            .flat_map(|paths| paths.into_iter())
            .flat_map(|result| result.into_iter())
            .flat_map(|path| {
                path.strip_prefix(STANDARD_LIBRARY_FOLDER)
                    .map(|p| p.to_path_buf())
            })
            .map(|p| ScriptNode::standard_library(p.to_string_lossy().to_string()))
            .collect();
        nodes.extend(
            fs.write_layer()
                .list(USER_LIBRARY_FOLDER, Some("**/*.exl"))
                .unwrap_or_default()
                .into_iter()
                .flat_map(|path| {
                    Path::new(&path)
                        .strip_prefix(USER_LIBRARY_FOLDER)
                        .map(|p| p.to_path_buf())
                })
                .map(|path| ScriptNode::user_library(self.source_path(&path.to_string_lossy()))),
        );
        nodes.extend(
            fs.list(self.get_compiled_script_root(), Some("**/*.cmb"), false)
                .unwrap_or_default()
                .into_iter()
                .flat_map(|path| {
                    Path::new(&path)
                        .strip_prefix(self.get_compiled_script_root())
                        .map(|p| p.to_path_buf())
                })
                .map(|path| ScriptNode::compiled(self.mirror_path(&path.to_string_lossy()))),
        );
        nodes.extend(
            fs.write_layer()
                .list(MIRROR_FOLDER, Some("**/*.exl"))
                .unwrap_or_default()
                .into_iter()
                .flat_map(|path| {
                    Path::new(&path)
                        .strip_prefix(MIRROR_FOLDER)
                        .map(|p| p.to_path_buf())
                })
                .map(|path| ScriptNode::compiled(self.mirror_path(&path.to_string_lossy()))),
        );
        nodes
    }

    fn get_source_template(&self) -> &str {
        match self.exalt_game {
            exalt_lir::Game::FE10 => "include std:fe10:prelude;\n",
            exalt_lir::Game::FE14 => "include std:fe14:prelude;\n",
            _ => Default::default(),
        }
    }

    fn source_path(&self, path: &str) -> String {
        Path::new(USER_LIBRARY_FOLDER)
            .join(path)
            .to_string_lossy()
            .to_string()
    }

    fn mirror_path(&self, path: &str) -> String {
        Path::new(MIRROR_FOLDER)
            .join(path)
            .with_extension("exl")
            .to_string_lossy()
            .to_string()
    }

    fn build_includes(&self, fs: &LayeredFilesystem, node: &ScriptNode) -> Vec<PathBuf> {
        let mut includes = vec![PathBuf::from(STANDARD_LIBRARY_FOLDER)];
        match node.kind {
            ScriptNodeKind::CompileTarget | ScriptNodeKind::UserLibrary => {
                if let Some(path) = fs.resolve(USER_LIBRARY_FOLDER, false) {
                    includes.push(path);
                }
            }
            _ => {}
        }
        includes
    }

    pub fn new_source_only_script(
        &mut self,
        fs: &LayeredFilesystem,
        path: &str,
    ) -> Result<ScriptNode> {
        let path = self.source_path(path);
        if fs.exists(&path, false)? {
            bail!("file already exists at path '{}'", path);
        }
        fs.write(&path, self.get_source_template().as_bytes(), false)?;
        let node = ScriptNode::user_library(path);
        Ok(node)
    }

    pub fn new_compiled_script(
        &mut self,
        fs: &LayeredFilesystem,
        path: &str,
    ) -> Result<ScriptNode> {
        let path = self.mirror_path(path);
        if fs.exists(&path, false)? {
            bail!("file already exists at path '{}'", path);
        }
        fs.write(&path, self.get_source_template().as_bytes(), false)?;
        let node = ScriptNode::compiled(path);
        self.scripts_to_compile.insert(node.clone());
        Ok(node)
    }

    pub fn compiled_script_path(&self, mirror_path: &str) -> Result<PathBuf> {
        Ok(Path::new(self.get_compiled_script_root())
            .join(Path::new(&mirror_path).strip_prefix(MIRROR_FOLDER)?))
    }

    pub fn save(&mut self, fs: &LayeredFilesystem) -> Result<ScriptAnalysisResult> {
        let mut all_errors = HashSet::new();
        let mut all_warnings = HashSet::new();
        for script_node in std::mem::take(&mut self.scripts_to_compile) {
            if let ScriptNodeKind::CompileTarget = script_node.kind {
                let path = Path::new(fs.write_layer().root())
                    .join(Path::new(self.get_compiled_script_root()))
                    .join(
                        Path::new(&script_node.path)
                            .strip_prefix(MIRROR_FOLDER)?
                            .with_extension("cmb"),
                    );
                let full_path = Path::new(fs.write_layer().root()).join(&script_node.path);
                let normalized = full_path
                    .normalize()
                    .ok()
                    .map(|p| p.as_path().to_path_buf())
                    .ok_or_else(|| anyhow!("bad path"))?;
                let request = CompileRequest {
                    game: self.exalt_game,
                    target: normalized,
                    output: Some(path),
                    text_data: None,
                    additional_includes: self.build_includes(fs, &script_node),
                };
                if let Err(CompilerError::ParseError(log)) = exalt_compiler::compile(&request) {
                    let result = extract_log(&log);
                    all_errors.extend(result.errors);
                    all_warnings.extend(result.warnings);
                    self.scripts_to_compile.insert(script_node);
                }
            }
        }
        Ok(ScriptAnalysisResult {
            errors: all_errors.into_iter().collect(),
            warnings: all_warnings.into_iter().collect(),
        })
    }

    pub fn open(&mut self, fs: &LayeredFilesystem, script_node: &ScriptNode) -> Result<String> {
        match script_node.kind {
            ScriptNodeKind::UserLibrary => {
                let text = String::from_utf8(fs.read(&script_node.path, false)?)?;
                Ok(text)
            }
            ScriptNodeKind::StandardLibrary => {
                let path = Path::new(STANDARD_LIBRARY_FOLDER).join(&script_node.path);
                let text = std::fs::read_to_string(path)?;
                Ok(text)
            }
            ScriptNodeKind::CompileTarget => {
                if fs.file_exists(&script_node.path, false)? {
                    let text = String::from_utf8(fs.read(&script_node.path, false)?)?;
                    return Ok(text);
                }
                let path = Path::new(self.get_compiled_script_root()).join(
                    Path::new(&script_node.path)
                        .strip_prefix(MIRROR_FOLDER)?
                        .with_extension("cmb"),
                );
                let raw = fs.read(&path.to_string_lossy(), false)?;
                let script = exalt_disassembler::disassemble(&raw, self.exalt_game)?;
                let transform = load_decompiler_transform(self.exalt_game)?;
                let includes = match self.exalt_game {
                    exalt_lir::Game::FE10 => vec!["std:fe10:prelude".to_owned()],
                    exalt_lir::Game::FE14 => vec!["std:fe14:prelude".to_owned()],
                    _ => Vec::new(),
                };
                let script = exalt_decompiler::decompile(
                    &script,
                    transform,
                    includes,
                    self.exalt_game,
                    false,
                )?;
                fs.write(&script_node.path, script.as_bytes(), false)?;
                Ok(script)
            }
        }
    }

    pub fn update(
        &mut self,
        fs: &LayeredFilesystem,
        script_node: &ScriptNode,
        contents: &str,
    ) -> Result<()> {
        match script_node.kind {
            ScriptNodeKind::CompileTarget | ScriptNodeKind::UserLibrary => {
                fs.write(&script_node.path, contents.as_bytes(), false)?;
                if let ScriptNodeKind::CompileTarget = script_node.kind {
                    self.scripts_to_compile.insert(script_node.to_owned());
                }
            }
            ScriptNodeKind::StandardLibrary => {
                std::fs::write(
                    Path::new(STANDARD_LIBRARY_FOLDER).join(&script_node.path),
                    contents,
                )?;
            }
        }
        Ok(())
    }

    pub fn analyze(
        &mut self,
        fs: &LayeredFilesystem,
        script_node: &ScriptNode,
        script: String,
    ) -> ScriptAnalysisResult {
        let target = match script_node.kind {
            ScriptNodeKind::CompileTarget | ScriptNodeKind::UserLibrary => {
                fs.resolve(&script_node.path, false)
            }
            ScriptNodeKind::StandardLibrary => {
                Some(Path::new(STANDARD_LIBRARY_FOLDER).join(&script_node.path))
            }
        };

        let normalized = target
            .and_then(|p| p.normalize().ok())
            .map(|p| p.as_path().to_path_buf());

        if let Some(target) = normalized {
            match exalt_compiler::parse(&ParseRequest {
                game: self.exalt_game,
                target,
                source: Some(script.clone()),
                additional_includes: self.build_includes(fs, script_node),
            }) {
                Ok(parse_result) => {
                    self.completion_server =
                        CompletionServer::from_symbol_table(&parse_result.symbol_table);
                    extract_log(&parse_result.log)
                }
                Err(CompilerError::ParseError(log)) => extract_log(&log),
                Err(err) => {
                    println!("{:?}", err);
                    ScriptAnalysisResult::default()
                }
            }
        } else {
            ScriptAnalysisResult::default()
        }
    }

    pub fn suggest_completions(&self, prefix: &str) -> Vec<&str> {
        self.completion_server.suggest_completions(prefix)
    }

    pub fn get_node(&self, fs: &LayeredFilesystem, path: &str) -> Option<ScriptNode> {
        let exalt_root: PathBuf = Path::new(path)
            .iter()
            .rev()
            .take_while(|p| *p != "exalt")
            .collect();
        let path_from_exalt_root =
            Path::new("exalt").join(exalt_root.iter().rev().collect::<PathBuf>());
        let path_string = path_from_exalt_root.to_string_lossy().to_string();
        let next_is_libs = path_from_exalt_root
            .iter()
            .skip(1)
            .take(1)
            .any(|t| t == "libs");
        if next_is_libs && fs.exists(&path_string, false).ok()? {
            return Some(ScriptNode::user_library(path_string));
        }
        let next_is_scripts = path_from_exalt_root
            .iter()
            .skip(1)
            .take(1)
            .any(|t| t == "scripts");
        if next_is_scripts && fs.exists(&path_string, false).ok()? {
            return Some(ScriptNode::compiled(path_string));
        }

        let path_string = path_from_exalt_root
            .iter()
            .skip(1)
            .collect::<PathBuf>()
            .to_string_lossy()
            .to_string();
        Some(ScriptNode::standard_library(path_string))
    }

    pub fn get_dirty_script_nodes(&self) -> HashSet<ScriptNode> {
        self.scripts_to_compile.clone()
    }
}
