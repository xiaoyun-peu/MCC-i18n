#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minecraft地图文本汉化工具 - 主程序入口
Minecraft Map Text Localization Tool - Main Entry Point

作者: AI Assistant
版本: 1.0.0
"""

import sys
import os
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTranslator, QLocale
from PyQt6.QtGui import QIcon

from ui.main_window import MainWindow
from utils.logger import setup_logger
from utils.config import Config


def main():
    """主函数 - Main function"""
    # 创建QApplication实例
    app = QApplication(sys.argv)
    app.setApplicationName("MCC i18n")
    app.setApplicationDisplayName("Minecraft地图汉化工具")
    app.setOrganizationName("MCCi18n")
    
    # 设置应用程序图标
    icon_path = os.path.join(os.path.dirname(__file__), 'resources', 'icons', 'app.ico')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # 初始化配置
    config = Config()
    
    # 设置日志
    logger = setup_logger()
    logger.info("应用程序启动 - Application started")
    
    # 创建并显示主窗口
    window = MainWindow(config)
    window.show()
    
    # 运行应用程序
    try:
        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"应用程序异常退出: {e}")
        raise


if __name__ == "__main__":
    main()