# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None

excluded_binaries = [
	'Qt5Pdf.dll',
	'Qt5Quick.dll',
	'libGLESv2.dll',
	'd3dcompiler_47.dll',
	'opengl32sw.dll',
    'Qt5Pdf.so',
	'Qt5Quick.so',
	'libGLESv2.so',
	'd3dcompiler_47.so',
	'opengl32sw.so',
]

a = Analysis(['paragon\\ui\\main.py'],
             pathex=['.'],
             binaries=None,
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
a.binaries = [b for b in a.binaries if os.path.basename(b[0]) not in excluded_binaries]
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='paragon',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True,
		  icon="paragon.ico")
