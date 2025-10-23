# -*- mode: python ; coding: utf-8 -*-
# PhyloForester PyInstaller spec file
# Generated: 2025-10-23

block_cipher = None

a = Analysis(
    ['PhyloForester.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('icons/*.png', 'icons'),
        ('data/*.*', 'data'),
        ('translations/*.qm', 'translations'),
        ('migrations/*', 'migrations'),
    ],
    hiddenimports=[
        'peewee',
        'peewee_migrate',
        'PIL',
        'Bio',
        'matplotlib',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'pytest',
        'pytest-qt',
        'pytest-cov',
        'pytest-mock',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PhyloForester',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Windowed application (no console)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icons/PhyloForester.png',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PhyloForester',
)
