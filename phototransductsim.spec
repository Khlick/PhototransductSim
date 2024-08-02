# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# Collect all data files in the specified directories
datas = [
    ('src/main/data/*', 'data'),
    ('src/resources/fonts/*', 'resources/fonts'),
    ('src/resources/icons/*', 'resources/icons'),
    ('src/resources/img/*', 'resources/img'),
    ('src/resources/styles/*', 'resources/styles')
]

# Collect all hidden imports
hiddenimports = []
for module in ['your_module_1', 'your_module_2']:
    hiddenimports += collect_all(module)[0]

a = Analysis(
    ['src/main/app/application.py'],
    pathex=[os.getcwd()],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
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
    console=False,
    icon='src/resources/icons/psim.ico'  # specify your icon file
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

# Additional configurations for creating .dmg (macOS) and .exe (Windows) packages
if os.name == 'nt':
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
        console=False,
        icon='src/resources/icons/psim.ico'  # specify your icon file
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

elif os.name == 'posix':
    app = BUNDLE(
        coll,
        name='PhototransductSim.app',
        icon='src/resources/icons/psim.icns',  # specify your icon file
        bundle_identifier='com.example.phototransductsim'  # specify your bundle identifier
    )

    dmg = DMG(
        app,
        name='PhototransductSim',
        volume_label='PhototransductSim'
    )
