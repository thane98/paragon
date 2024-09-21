poetry run maturin develop --release
poetry run pyinstaller paragon.spec
copy paragon.ico dist
copy LICENSE.txt dist
:: TODO: Add command to copy Exalt's standard library
xcopy Data dist\Data\ /s /e /y
xcopy resources dist\resources\ /s /e /y
xcopy third-party-licenses dist\third-party-licenses\ /s /e /y
