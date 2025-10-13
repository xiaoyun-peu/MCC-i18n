#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目测试脚本 - Project Test Script
用于验证项目结构和基本功能
"""

import os
import sys
import importlib.util
from pathlib import Path


def check_file_exists(filepath):
    """检查文件是否存在"""
    if os.path.exists(filepath):
        print(f"✓ {filepath} 存在")
        return True
    else:
        print(f"✗ {filepath} 不存在")
        return False


def check_directory_structure():
    """检查目录结构"""
    print("检查项目目录结构...")
    
    required_dirs = [
        'ui',
        'workers', 
        'utils',
        'resources',
        'resources/icons',
        'resources/styles'
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        if os.path.isdir(dir_path):
            print(f"✓ {dir_path}/ 目录存在")
        else:
            print(f"✗ {dir_path}/ 目录不存在")
            all_exist = False
    
    return all_exist


def check_required_files():
    """检查必需文件"""
    print("\n检查必需文件...")
    
    required_files = [
        'main.py',
        'build.py',
        'requirements.txt',
        'README.md',
        'PROJECT_OVERVIEW.md',
        'ui/main_window.py',
        'ui/navigation_widget.py',
        'ui/world_select_page.py',
        'ui/scan_page.py',
        'ui/translation_page.py',
        'ui/write_page.py',
        'ui/export_page.py',
        'ui/__init__.py',
        'workers/scan_worker.py',
        'workers/translate_worker.py',
        'workers/write_worker.py',
        'workers/export_worker.py',
        'workers/__init__.py',
        'utils/logger.py',
        'utils/config.py',
        'utils/nbt_helper.py',
        'utils/json_validator.py',
        'utils/exceptions.py',
        'utils/mock_translator.py',
        'utils/__init__.py',
        'resources/styles.qrc',
        'resources/styles/light_theme.qss',
        'resources/styles/dark_theme.qss',
        'resources/icons/app.png',
        'resources/icons/logo.png'
    ]
    
    all_exist = True
    for file_path in required_files:
        if not check_file_exists(file_path):
            all_exist = False
    
    return all_exist


def check_python_syntax():
    """检查Python语法"""
    print("\n检查Python语法...")
    
    python_files = [
        'main.py',
        'build.py',
        'ui/main_window.py',
        'workers/scan_worker.py',
        'utils/logger.py'
    ]
    
    all_valid = True
    for file_path in python_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                compile(content, file_path, 'exec')
                print(f"✓ {file_path} 语法正确")
            except SyntaxError as e:
                print(f"✗ {file_path} 语法错误: {e}")
                all_valid = False
            except Exception as e:
                print(f"✗ {file_path} 检查失败: {e}")
                all_valid = False
    
    return all_valid


def check_imports():
    """检查导入"""
    print("\n检查模块导入...")
    
    test_imports = [
        ('PyQt6.QtWidgets', 'PyQt6'),
        ('PyQt6.QtCore', 'PyQt6'),
        ('PyQt6.QtGui', 'PyQt6'),
        ('nbtlib', 'nbtlib'),
        ('openpyxl', 'openpyxl')
    ]
    
    all_importable = True
    for module_name, package_name in test_imports:
        try:
            __import__(module_name)
            print(f"✓ {package_name} 可正常导入")
        except ImportError:
            print(f"✗ {package_name} 导入失败")
            all_importable = False
    
    return all_importable


def main():
    """主测试函数"""
    print("Minecraft地图汉化工具 - 项目测试")
    print("=" * 50)
    
    # 检查目录结构
    dirs_ok = check_directory_structure()
    
    # 检查必需文件
    files_ok = check_required_files()
    
    # 检查Python语法
    syntax_ok = check_python_syntax()
    
    # 检查导入
    imports_ok = check_imports()
    
    # 总结
    print("\n" + "=" * 50)
    print("测试结果总结:")
    print(f"目录结构: {'✓ 通过' if dirs_ok else '✗ 失败'}")
    print(f"必需文件: {'✓ 通过' if files_ok else '✗ 失败'}")
    print(f"Python语法: {'✓ 通过' if syntax_ok else '✗ 失败'}")
    print(f"模块导入: {'✓ 通过' if imports_ok else '✗ 失败'}")
    
    overall_ok = dirs_ok and files_ok and syntax_ok and imports_ok
    
    if overall_ok:
        print("\n🎉 项目结构完整，可以正常开发和构建！")
        return 0
    else:
        print("\n❌ 项目存在问题，请检查上述错误信息！")
        return 1


if __name__ == '__main__':
    sys.exit(main())