# phototransductsim.spec
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main/app/application.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('src/main/data/*', 'data'),
        ('src/resources/fonts/*', 'resources/fonts'),
        ('src/resources/icons/*', 'resources/icons'),
        ('src/resources/img/*', 'resources/img'),
        ('src/resources/styles/*', 'resources/styles')
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='phototransductsim',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='phototransductsim'
)
