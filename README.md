# Paragon
Paragon is a toolkit for editing and creating editors for FE13, FE14, and FE15. Unlike its predecessor, FEFNightmare, Paragon operates on an entire ROM instead of individual files so that it can see common data between files, tables, etc. This leads to a more streamlined editing process.

Users can define their own editors using a simple, human-readable (JSON) format. Paragon will take the editor specification and generate a UI which can be used to make changes.

## Installation
Paragon releases should require no dependencies. Download the release for your operating system and run.

## Building
Paragon requires Rust Nightly and Python 3.7.x. You will also need to install the Maturin, pillow, and PySide2 Python packages. If you want to build a standalone executable, you should also install PyInstaller.

1. To build, run *maturin build --release* from the root directory of the project. This will produce a "target" folder.
2. Navigate to "target/wheels" in your terminal.
3. Run *pip install {name of the file Maturin produced}*. The file name will vary by version. If you are repeating these instructions, you might need to run *pip uninstall fefeditor2* first.
4. If the install succeeds, you can run Paragon by running the "main.py" script in the application directory.
5. To create a standalone executable, run *pyinstaller main.py --noconsole --onefile* from the application directory.

## Credits
* Moonling for writing most of the modules.
* RainThunder for the original FE14 Nightmare modules.
* Einstein95 for DSDecmp.
* Hextator for Nightmare 2 which was a major inspiration for Paragon.
* lazy for bch and arc parsing

* [3dstools](https://github.com/ObsidianX/3dstools) and xDaniel for etc1a4 decompression.
* [FEAT](https://github.com/SciresM/FEAT) and [Ohana3DS](https://github.com/gdkchan/Ohana3DS-Rebirth) for bch parsing references.

## License
Unless explicitly stated in a file, this project is licensed under the GNU General Public License 3.0.

BCH parsing code (stored under src/bch.rs) was created by referencing code from FEAT and Ohana. This portion is licensed under the GNU General Public License 3.0.
