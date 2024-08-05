# -*- mode: python ; coding: utf-8 -*-

import os
import sys

def recursive_files(path, root= None, exclude_dirs=['__pycache__']):
    files = []
    path = os.path.normpath(path)
    split = os.path.split(path)
    if root:
        outputRoot = os.path.join(root,*split[1:])
    else:
        outputRoot = os.path.join(*split[1:])
    for item in os.listdir(path):
        itemPath = os.path.join(path,item)
        if os.path.isdir(itemPath):
            if item not in exclude_dirs:
                files.extend(recursive_files(itemPath,split[1]))
                continue
        # not dir
        files.append((itemPath,outputRoot))
    return files

datas = []
datas += recursive_files('src/data/')
datas += recursive_files('src/resources/')

a = Analysis(
    ['src/main/app/application.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=['runtime_hook.py'],
    excludes=[],
    hooksconfig={
        "matplotlib": {
            "backends": "QtAgg",
        },
    },
    noarchive= False,
    optimize=0,
    win_no_prefer_redirects=False,
    win_private_assemblies=False
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='phototransductsim',
    debug=False, # True for dev
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True, # True for dev
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='src/resources/icons/psim.ico'
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


app = BUNDLE(
    coll,
    name='phototransductsim.app',
    icon='src/resources/icons/psim.icns',
    bundle_identifier='com.khrisgriffis.phototransductsim',
    info_plist={
            'CFBundleName': 'PhototransductSim',
            'CFBundleDisplayName': 'PhototransductSim',
            'CFBundleVersion': '0.1.0',
            'CFBundleShortVersionString': '0.1.2',
            'CFBundleIdentifier': 'com.example.phototransductsim',
            'LSUIElement': True,
        }
)