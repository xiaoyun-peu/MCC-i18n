# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_all

# 收集PyQt6数据文件
datas = []
binaries = []
hiddenimports = []

# 收集PyQt6数据
tmp_ret = collect_all('PyQt6')
datas += tmp_ret[0]
binaries += tmp_ret[1]
hiddenimports += tmp_ret[2]

# 收集qt-material数据
tmp_ret = collect_all('qt_material')
datas += tmp_ret[0]
binaries += tmp_ret[1]
hiddenimports += tmp_ret[2]

# 添加资源文件
resources_dir = os.path.join(os.getcwd(), 'resources')
if os.path.exists(resources_dir):
    for root, dirs, files in os.walk(resources_dir):
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, os.getcwd())
            datas.append((rel_path, os.path.dirname(rel_path)))

# 添加样式文件
styles_dir = os.path.join(os.getcwd(), 'resources', 'styles')
if os.path.exists(styles_dir):
    for root, dirs, files in os.walk(styles_dir):
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, os.getcwd())
            datas.append((rel_path, os.path.dirname(rel_path)))

# 添加图标文件
icons_dir = os.path.join(os.getcwd(), 'resources', 'icons')
if os.path.exists(icons_dir):
    for root, dirs, files in os.walk(icons_dir):
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, os.getcwd())
            datas.append((rel_path, os.path.dirname(rel_path)))

# 隐藏导入
hiddenimports += [
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'PyQt6.QtPrintSupport',
    'nbtlib',
    'nbtlib.tag',
    'nbtlib.schema',
    'openpyxl',
    'openpyxl.workbook',
    'openpyxl.worksheet',
    'openpyxl.cell',
    'openpyxl.styles',
    'googletrans',
    'googletrans.constants',
    'googletrans.models',
    'googletrans.gtoken',
    'googletrans.client',
]

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='mcc_i18n',
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
    entitlements_file=None,
    icon=['resources/icons/app.ico'],
)
