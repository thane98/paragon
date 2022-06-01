use std::collections::HashMap;
use std::path::Path;

use mila::Game;
use mila::LayeredFilesystem;

pub struct Scripts {
    game: Game,
    scripts: HashMap<String, String>,
}

impl Scripts {
    pub fn new(game: Game) -> Self {
        Scripts {
            game,
            scripts: HashMap::new(),
        }
    }

    pub fn save(&self, fs: &LayeredFilesystem) -> anyhow::Result<()> {
        for (path, script) in &self.scripts {
            let script_name = Path::new(path)
                .file_name()
                .ok_or_else(|| anyhow::anyhow!("Bad path."))?
                .to_string_lossy()
                .to_string();
            let raw = match self.game {
                Game::FE10 => exalt::pretty_assemble_vgcn(&script_name, script),
                _ => Err(anyhow::anyhow!("Unsupported game.")),
            }?;
            fs.write(path, &raw, false)?;
        }
        Ok(())
    }

    pub fn open(&mut self, fs: &LayeredFilesystem, path: String) -> anyhow::Result<String> {
        if let Some(script) = self.scripts.get(&path) {
            Ok(script.clone())
        } else {
            let raw = fs.read(&path, false)?;
            let script = match self.game {
                Game::FE10 => exalt::pretty_disassemble_vgcn(&raw),
                _ => Err(anyhow::anyhow!("Unsupported game.")),
            }?;
            self.scripts.insert(path, script.clone());
            Ok(script)
        }
    }

    pub fn set_script(&mut self, path: String, script: String) {
        self.scripts.insert(path, script);
    }
}
