call venv\Scripts\activate.bat
maturin develop --release
pyinstaller paragon.spec
copy paragon.ico dist
copy LICENSE.txt dist
xcopy Data dist\Data\ /s /e /y
xcopy resources dist\resources\ /s /e /y
xcopy third-party-licenses dist\third-party-licenses\ /s /e /y
