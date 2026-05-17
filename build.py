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
        ('PyQt6', 'PyQt6'),
        ('qt_material', 'qt_material'),
        ('nbtlib', 'nbtlib'),
        ('openpyxl', 'openpyxl'),
        ('pyinstaller', 'PyInstaller')
    ]
    
    print("检查依赖包...")
    for display_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"✓ {display_name} 已安装")
        except ImportError:
            print(f"✗ {display_name} 未安装")
            return False
    
    return True


def create_icon():
    """创建应用程序图标"""
    icon_dir = Path('resources/icons')
    icon_dir.mkdir(parents=True, exist_ok=True)
    
    icon_path = icon_dir / 'app.ico'
    
    # 如果已存在真实的图标文件，跳过创建
    if icon_path.exists():
        # 检查是否是有效的 ICO 文件（不是文本占位符）
        with open(icon_path, 'rb') as f:
            header = f.read(4)
            if header[:2] == b'\x00\x00' and header[2:4] in [b'\x01\x00', b'\x02\x00']:
                print("✓ 使用现有的图标文件")
                return
    
    # 尝试使用 Pillow 创建简单图标
    try:
        from PIL import Image, ImageDraw
        
        # 创建 256x256 的图标
        img = Image.new('RGBA', (256, 256), (0, 120, 212, 255))
        draw = ImageDraw.Draw(img)
        
        # 绘制简单的图形（一个白色的 "M" 字母）
        draw.polygon([(80, 200), (80, 56), (128, 128), (176, 56), (176, 200)], 
                     fill=(255, 255, 255, 255))
        
        # 保存为多尺寸 ICO 文件
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        icons = [img.resize(size, Image.Resampling.LANCZOS) for size in sizes]
        icons[0].save(icon_path, format='ICO', sizes=sizes)
        
        print("✓ 使用 Pillow 创建图标文件")
        return
    except ImportError:
        pass
    
    # 如果没有 Pillow，复制一个默认的图标或使用空图标
    print("⚠ Pillow 未安装，尝试使用默认图标")
    
    # 创建一个最小的有效 ICO 文件（16x16, 1bpp）
    # ICO 文件头 + 图标目录 + 位图数据
    ico_data = bytes([
        0x00, 0x00,  # 保留
        0x01, 0x00,  # 图标类型 (1 = ICO)
        0x01, 0x00,  # 图标数量
        # 图标目录条目
        0x10,        # 宽度 (16)
        0x10,        # 高度 (16)
        0x00,        # 颜色数 (0 = 256+ colors)
        0x00,        # 保留
        0x01, 0x00,  # 颜色平面
        0x18, 0x00,  # 位深度 (24 bpp)
        0x28, 0x00, 0x00, 0x00,  # 数据大小
        0x16, 0x00, 0x00, 0x00,  # 数据偏移
        # BITMAPINFOHEADER
        0x28, 0x00, 0x00, 0x00,  # 头大小 (40)
        0x10, 0x00, 0x00, 0x00,  # 宽度 (16)
        0x20, 0x00, 0x00, 0x00,  # 高度 (32 = 16x2 for XOR and AND masks)
        0x01, 0x00,              # 平面
        0x18, 0x00,              # 位深度 (24 bpp)
        0x00, 0x00, 0x00, 0x00,  # 压缩
        0x00, 0x00, 0x00, 0x00,  # 图像大小
        0x00, 0x00, 0x00, 0x00,  # X ppm
        0x00, 0x00, 0x00, 0x00,  # Y ppm
        0x00, 0x00, 0x00, 0x00,  # 颜色使用
        0x00, 0x00, 0x00, 0x00,  # 重要颜色
    ])
    
    # 添加像素数据（简单的蓝色方块）
    # XOR mask (16x16, 24bpp = 768 bytes, 每行填充到4字节边界)
    row_size = 48  # 16 pixels * 3 bytes, padded to 48 (divisible by 4)
    pixel_data = bytearray()
    for y in range(16):
        row = bytearray(row_size)
        for x in range(16):
            # 蓝色 (BGR)
            row[x*3] = 0xFF      # B
            row[x*3 + 1] = 0x00  # G
            row[x*3 + 2] = 0x00  # R
        pixel_data.extend(row)
    
    # AND mask (1bpp, 16x16 = 32 bytes, 每行填充到4字节)
    and_mask = bytearray(32)  # 全透明
    
    ico_data = ico_data + bytes(pixel_data) + bytes(and_mask)
    
    with open(icon_path, 'wb') as f:
        f.write(ico_data)
    
    print("✓ 创建默认图标文件完成")


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
    
    # 创建图标（自动创建，不需要参数）
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