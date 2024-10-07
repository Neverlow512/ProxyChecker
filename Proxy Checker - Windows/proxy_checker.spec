# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['proxy_checker_gui.py'],  
    pathex=[],
    binaries=[],
    datas=[
        (os.path.abspath('./proxychecker.jpg'), '.'),  # Use absolute path
        (os.path.abspath('./twitter.svg'), '.'),
        (os.path.abspath('./reddit.svg'), '.'),
    ],
    hiddenimports=[
        'PyQt6.QtCore', 
        'PyQt6.QtGui', 
        'PyQt6.QtWidgets', 
        'PyQt6.QtNetwork',
        'PyQt6.QtSvgWidgets'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ProxyChecker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None
)

app = BUNDLE(
    exe,
    name='ProxyChecker.app',
    icon=os.path.abspath('./proxychecker.jpg'),  # Use absolute path
    bundle_identifier=None
)
