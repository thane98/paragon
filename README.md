# Paragon
Paragon is a toolkit for editing and creating editors for FE13, FE14, and FE15.

## Installation
Paragon releases should require no dependencies. Download the release for your operating system and run.

## Building
Paragon requires Rust and Python 3.8.x. You will also need to install the python packages this project depends on. More on this below. If you want to build a standalone executable, you should also install PyInstaller.

1. Install [Poetry](https://python-poetry.org/) - this is used for managing the Python side of the build.
1. Install dependencies into the Python environment by running `poetry install`.
1. Render module templates by running `poetry run python scripts/render_templates.py`.
1. Build the Rust code by running `poetry run maturin develop --release`.
1. If everything succeeded, you can run the main script with the command `poetry run paragon/ui/main.py`.

## Tools Using Paragon
The following tools use Paragon features like import/export to edit FE13, FE14, and FE15. Take a look at the if you're interested!

### Fire Emblem Echoes Random Class Generator
Randomize classes for characters in Fire Emblem Echoes: Shadows of Valentia. Outputs JSON which can be used to apply changes to your ROM.

[https://evinjaff.github.io/FESOV-randomizer/](https://evinjaff.github.io/FESOV-randomizer/)

## Credits
* lazy for texture parsing as well as completion support for dialogue.
* Moonling for writing most of the modules.
* RainThunder for the original FE14 Nightmare modules.
* Einstein95 for DSDecmp.
* Hextator for Nightmare 2 which was a major inspiration for Paragon.

* [FontAwesome](https://fontawesome.com/) for icons. NOTE: Most icons were colorized to work better with light and dark modes.

* [3dstools](https://github.com/ObsidianX/3dstools) and xDaniel for etc1a4 decompression.
* [FEAT](https://github.com/SciresM/FEAT) and [Ohana3DS](https://github.com/gdkchan/Ohana3DS-Rebirth) for bch parsing references.

## License
Unless explicitly stated in a file, this project is licensed under the GNU General Public License 3.0.

BCH parsing code (stored under src/bch.rs) was created by referencing code from FEAT and Ohana. This portion is licensed under the GNU General Public License 3.0.
