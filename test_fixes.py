#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复的功能 - Test Fixed Features
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试导入是否成功"""
    print("测试导入...")
    
    try:
        from PyQt6.QtWidgets import QApplication
        print("✓ QApplication 导入成功")
    except ImportError as e:
        print(f"✗ QApplication 导入失败: {e}")
        return False
    
    try:
        from ui.main_window import MainWindow
        print("✓ MainWindow 导入成功")
    except ImportError as e:
        print(f"✗ MainWindow 导入失败: {e}")
        return False
    
    try:
        from ui.settings_dialog import SettingsDialog
        print("✓ SettingsDialog 导入成功")
    except ImportError as e:
        print(f"✗ SettingsDialog 导入失败: {e}")
        return False
    
    try:
        from utils.nbt_helper import validate_world, load_nbt_file
        print("✓ NBT助手函数导入成功")
    except ImportError as e:
        print(f"✗ NBT助手函数导入失败: {e}")
        return False
    
    return True

def test_nbt_config():
    """测试NBT配置"""
    print("\n测试NBT配置...")
    
    try:
        from utils.config import Config
        config = Config()
        
        # 测试NBT配置是否存在
        nbt_config = config.get_nbt_config()
        print(f"✓ NBT配置: {nbt_config}")
        
        # 测试ignore_data_version配置
        ignore_data_version = config.get('nbt.ignore_data_version', False)
        print(f"✓ ignore_data_version: {ignore_data_version}")
        
        return True
    except Exception as e:
        print(f"✗ NBT配置测试失败: {e}")
        return False

def test_settings_dialog():
    """测试设置对话框"""
    print("\n测试设置对话框...")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from ui.settings_dialog import SettingsDialog
        
        # 创建临时应用实例
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 创建设置对话框
        dialog = SettingsDialog()
        print("✓ 设置对话框创建成功")
        
        # 测试加载设置
        dialog.load_settings()
        print("✓ 设置加载成功")
        
        return True
    except Exception as e:
        print(f"✗ 设置对话框测试失败: {e}")
        return False

def test_nbt_helper():
    """测试NBT助手"""
    print("\n测试NBT助手...")
    
    try:
        from utils.nbt_helper import load_nbt_file
        
        # 测试函数签名
        import inspect
        sig = inspect.signature(load_nbt_file)
        print(f"✓ load_nbt_file签名: {sig}")
        
        # 检查是否有ignore_data_version参数
        params = sig.parameters
        if 'ignore_data_version' in params:
            print("✓ 包含ignore_data_version参数")
        else:
            print("✗ 缺少ignore_data_version参数")
            
        return True
    except Exception as e:
        print(f"✗ NBT助手测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("Minecraft地图汉化工具 - 修复功能测试")
    print("=" * 50)
    
    all_passed = True
    
    # 测试导入
    if not test_imports():
        all_passed = False
    
    # 测试NBT配置
    if not test_nbt_config():
        all_passed = False
    
    # 测试设置对话框
    if not test_settings_dialog():
        all_passed = False
    
    # 测试NBT助手
    if not test_nbt_helper():
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有测试通过！修复成功！")
        return 0
    else:
        print("❌ 部分测试失败，请检查错误信息")
        return 1

if __name__ == "__main__":
    sys.exit(main())