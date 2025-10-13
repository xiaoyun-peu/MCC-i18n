# -*- coding: utf-8 -*-
"""
导航组件 - Navigation Widget
"""

import os
from typing import List, Dict

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QFrame,
    QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap


class NavigationWidget(QWidget):
    """导航组件"""
    
    page_changed = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # 创建按钮
        self.buttons = []
        for i, text in enumerate(["选择存档", "扫描文本", "翻译管理", "写入地图", "导出结果"]):
            button = QPushButton(text)
            button.setObjectName(f"nav_button_{i}")
            button.setEnabled(i == 0)  # 默认只启用第一个按钮
            button.setProperty("index", i)
            button.clicked.connect(lambda _, idx=i: self.on_button_clicked(idx))  # 修复信号连接
            layout.addWidget(button)
            self.buttons.append(button)
        
        layout.addStretch()
        
        # 设置样式
        self.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                border: none;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:disabled {
                background-color: #bdbdbd;
                color: #757575;
            }
        """)
    
    def on_button_clicked(self, index: int):
        """按钮点击处理"""
        self.page_changed.emit(index)  # 修复信号发出逻辑
    
    def set_page_enabled(self, index: int, enabled: bool):
        """设置页面按钮是否可用"""
        if 0 <= index < len(self.buttons):
            self.buttons[index].setEnabled(enabled)
