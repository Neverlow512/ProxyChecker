# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['proxy_checker_gui.py'],  # Your main script file
    pathex=[],
    binaries=[],
    # Include both icons in the root directory
    datas=[  
        ('./Proxy Checker.jpg', '.'),  # Main icon in the root directory  
        ('./x.svg', '.'), # SVG icon in the root directory  
        ('./reddit.svg, '.')  # SVG icon in the root directory  
    ],
    hiddenimports=[
        'PyQt6.QtCore', 
        'PyQt6.QtGui', 
        'PyQt6.QtWidgets', 
        'PyQt6.QtNetwork',
        'PyQt6.QtSvgWidgets'  # Add this for handling SVGs
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
    icon='path/to/proxy checker.jpg',  # Main app icon
    bundle_identifier=None
)
