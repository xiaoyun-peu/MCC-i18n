#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建脚本 - Build Script
用于生成可执行文件
"""

import os
import sys
import subprocess
import shutil
import argparse
from pathlib import Path


def check_requirements():
    """检查必要的依赖是否安装"""
    required_packages = [
        'PyQt6',
        'qt_material',
        'nbtlib',
        'openpyxl',
        'pyinstaller'
    ]
    
    print("检查依赖包...")
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} 已安装")
        except ImportError:
            print(f"✗ {package} 未安装")
            return False
    
    return True


def create_icon():
    """创建应用程序图标"""
    icon_dir = Path('resources/icons')
    icon_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建简单的图标文件（实际项目中应该使用真实的图标文件）
    icon_content = """
    # 这是一个占位符图标文件
    # 实际项目中应该替换为真实的 .ico 文件
    """
    
    with open(icon_dir / 'app.ico', 'w') as f:
        f.write(icon_content)
    
    print("创建图标文件完成")


def create_main_spec():
    """创建PyInstaller spec文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

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
'''
    
    with open('main.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("创建spec文件完成")


def build_executable():
    """构建可执行文件"""
    print("开始构建可执行文件...")
    
    # 清理之前的构建
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')
    
    # 运行PyInstaller
    try:
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            'main.spec',
            '--clean',
            '--noconfirm'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ 构建成功完成!")
            print(f"可执行文件位于: {os.path.join('dist', 'mcc_i18n.exe' if os.name == 'nt' else 'mcc_i18n')}")
            return True
        else:
            print("✗ 构建失败!")
            print("错误输出:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"✗ 构建过程中发生错误: {e}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='MCC i18n 构建脚本')
    parser.add_argument('--check-only', action='store_true', 
                       help='仅检查依赖，不构建')
    parser.add_argument('--create-icon', action='store_true',
                       help='创建图标文件')
    
    args = parser.parse_args()
    
    print("Minecraft地图汉化工具 - 构建脚本")
    print("=" * 50)
    
    # 检查依赖
    if not check_requirements():
        print("\n请先安装所有必需的依赖包:")
        print("pip install -r requirements.txt")
        return 1
    
    if args.check_only:
        print("\n所有依赖包已安装，可以开始构建!")
        return 0
    
    # 创建图标
    if args.create_icon:
        create_icon()
    
    # 创建spec文件
    create_main_spec()
    
    # 构建可执行文件
    if build_executable():
        print("\n构建完成!")
        return 0
    else:
        print("\n构建失败!")
        return 1


if __name__ == '__main__':
    sys.exit(main())