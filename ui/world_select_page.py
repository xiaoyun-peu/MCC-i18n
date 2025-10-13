# -*- coding: utf-8 -*-
"""
世界选择页面 - World Selection Page
"""

import os
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFrame, QFileDialog, QMessageBox, QTextEdit
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont

from utils.nbt_helper import validate_world
from utils.logger import get_logger


class WorldSelectPage(QWidget):
    """世界选择页面"""
    
    world_selected = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger()
        self.selected_world_path = ""
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # 标题
        title = QLabel("选择Minecraft世界")
        title.setObjectName("page_title")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # 说明文字
        description = QLabel(
            "请选择包含level.dat文件的Minecraft世界文件夹。\n"
            "通常位于 .minecraft/saves/ 目录下。"
        )
        description.setObjectName("description")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(description)
        
        layout.addSpacing(20)
        
        # 世界路径选择区域
        path_frame = QFrame()
        path_frame.setObjectName("path_frame")
        path_layout = QVBoxLayout(path_frame)
        path_layout.setContentsMargins(20, 20, 20, 20)
        
        # 路径标签
        path_label = QLabel("世界文件夹路径:")
        path_label.setObjectName("path_label")
        path_layout.addWidget(path_label)
        
        # 路径输入区域
        path_input_layout = QHBoxLayout()
        
        self.path_input = QLineEdit()
        self.path_input.setObjectName("path_input")
        self.path_input.setPlaceholderText("点击右侧按钮选择世界文件夹...")
        self.path_input.textChanged.connect(self.on_path_changed)
        path_input_layout.addWidget(self.path_input)
        
        self.browse_button = QPushButton("浏览...")
        self.browse_button.setObjectName("browse_button")
        self.browse_button.clicked.connect(self.browse_world)
        path_input_layout.addWidget(self.browse_button)
        
        path_layout.addLayout(path_input_layout)
        
        # 路径状态指示
        self.path_status = QLabel("未选择世界")
        self.path_status.setObjectName("path_status")
        path_layout.addWidget(self.path_status)
        
        layout.addWidget(path_frame)
        
        # 世界信息区域
        self.info_frame = QFrame()
        self.info_frame.setObjectName("info_frame")
        self.info_frame.setVisible(False)
        info_layout = QVBoxLayout(self.info_frame)
        info_layout.setContentsMargins(20, 20, 20, 20)
        
        info_title = QLabel("世界信息")
        info_title.setObjectName("info_title")
        info_layout.addWidget(info_title)
        
        self.world_info = QTextEdit()
        self.world_info.setObjectName("world_info")
        self.world_info.setReadOnly(True)
        self.world_info.setMaximumHeight(150)
        info_layout.addWidget(self.world_info)
        
        layout.addWidget(self.info_frame)
        
        layout.addStretch()
        
        # 操作按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.next_button = QPushButton("下一步")
        self.next_button.setObjectName("next_button")
        self.next_button.setEnabled(False)
        self.next_button.clicked.connect(self.proceed_to_scan)
        button_layout.addWidget(self.next_button)
        
        layout.addLayout(button_layout)
        
        # 设置样式
        self.setStyleSheet("""
            #page_title {
                color: #00695c;
                margin-bottom: 10px;
            }
            #description {
                color: #757575;
                font-size: 14px;
                margin-bottom: 20px;
            }
            #path_frame, #info_frame {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
            #path_label, #info_title {
                font-weight: bold;
                color: #424242;
                margin-bottom: 8px;
            }
            #path_input {
                padding: 10px;
                border: 1px solid #bdbdbd;
                border-radius: 4px;
                font-size: 14px;
            }
            #path_input:focus {
                border-color: #00897b;
                outline: none;
            }
            #browse_button {
                background-color: #00897b;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: 14px;
            }
            #browse_button:hover {
                background-color: #00695c;
            }
            #path_status {
                color: #757575;
                font-size: 12px;
                margin-top: 5px;
            }
            #world_info {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: #fafafa;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
            }
            #next_button {
                background-color: #00897b;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 30px;
                font-size: 16px;
                font-weight: bold;
            }
            #next_button:hover {
                background-color: #00695c;
            }
            #next_button:disabled {
                background-color: #bdbdbd;
                color: #757575;
            }
        """)
    
    def browse_world(self):
        """浏览选择世界文件夹"""
        world_dir = QFileDialog.getExistingDirectory(
            self, 
            "选择Minecraft世界文件夹",
            os.path.expanduser("~"),
            QFileDialog.Option.ShowDirsOnly
        )
        
        if world_dir:
            self.path_input.setText(world_dir)
    
    def on_path_changed(self, path: str):
        """路径改变处理"""
        if not path:
            self.path_status.setText("未选择世界")
            self.path_status.setStyleSheet("color: #757575;")
            self.next_button.setEnabled(False)
            self.info_frame.setVisible(False)
            return
        
        # 验证世界文件夹
        is_valid, message = validate_world(path)
        
        if is_valid:
            self.path_status.setText("✓ 有效的Minecraft世界")
            self.path_status.setStyleSheet("color: #4caf50; font-weight: bold;")
            self.next_button.setEnabled(True)
            self.selected_world_path = path
            self.show_world_info(path)
            self.info_frame.setVisible(True)
        else:
            self.path_status.setText(f"✗ {message}")
            self.path_status.setStyleSheet("color: #f44336; font-weight: bold;")
            self.next_button.setEnabled(False)
            self.info_frame.setVisible(False)
    
    def show_world_info(self, world_path: str):
        """显示世界信息"""
        try:
            world_name = os.path.basename(world_path)
            level_dat_path = os.path.join(world_path, "level.dat")
            
            info_text = f"世界名称: {world_name}\n"
            info_text += f"世界路径: {world_path}\n"
            
            if os.path.exists(level_dat_path):
                file_size = os.path.getsize(level_dat_path)
                info_text += f"level.dat 大小: {file_size:,} 字节\n"
                info_text += "状态: 世界文件存在且有效\n"
            else:
                info_text += "状态: level.dat 文件不存在\n"
            
            # 检查region文件夹
            region_path = os.path.join(world_path, "region")
            if os.path.exists(region_path):
                mca_files = [f for f in os.listdir(region_path) if f.endswith('.mca')]
                info_text += f"Region文件: {len(mca_files)} 个\n"
            
            # 检查data文件夹
            data_path = os.path.join(world_path, "data")
            if os.path.exists(data_path):
                dat_files = [f for f in os.listdir(data_path) if f.endswith('.dat')]
                info_text += f"Data文件: {len(dat_files)} 个\n"
            
            self.world_info.setPlainText(info_text)
            
        except Exception as e:
            self.logger.error(f"获取世界信息失败: {e}")
            self.world_info.setPlainText(f"获取世界信息失败: {e}")
    
    def proceed_to_scan(self):
        """进入扫描步骤"""
        if self.selected_world_path:
            self.world_selected.emit(self.selected_world_path)
            self.logger.info(f"选择世界完成: {self.selected_world_path}")