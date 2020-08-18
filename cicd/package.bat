for /r %%v in (target\wheels\*.whl) do pip install --force-reinstall "%%v"
cd application
pyinstaller --noconsole --onefile --icon=paragon.ico --name=paragon main.py
copy paragon.ico dist
xcopy Assets dist\Assets\ /s /e /y
xcopy Modules dist\Modules\ /s /e /y
