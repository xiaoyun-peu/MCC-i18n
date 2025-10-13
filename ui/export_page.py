# -*- coding: utf-8 -*-
"""
导出页面 - Export Page
"""

import os
import json
import zipfile
from datetime import datetime
from typing import List, Dict, Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTextEdit, QMessageBox, QProgressBar, QLineEdit,
    QCheckBox, QFileDialog
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont

from workers.export_worker import ExportWorker
from utils.logger import get_logger


class ExportPage(QWidget):
    """导出页面"""
    
    export_requested = pyqtSignal(str, str)
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger()
        self.world_path = ""
        self.translation_data = []
        self.export_worker = None
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # 标题
        title = QLabel("打包导出")
        title.setObjectName("page_title")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # 说明文字
        description = QLabel(
            "将翻译后的世界打包成mcworld格式，方便分享和分发。\n"
            "同时会生成语言文件，支持多语言切换。"
        )
        description.setObjectName("description")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(description)
        
        layout.addSpacing(20)
        
        # 导出配置
        config_frame = QFrame()
        config_frame.setObjectName("config_frame")
        config_layout = QVBoxLayout(config_frame)
        config_layout.setContentsMargins(20, 20, 20, 20)
        
        config_title = QLabel("导出配置")
        config_title.setObjectName("config_title")
        config_layout.addWidget(config_title)
        
        # 输出路径
        path_layout = QHBoxLayout()
        
        path_label = QLabel("输出路径:")
        path_label.setObjectName("path_label")
        path_layout.addWidget(path_label)
        
        self.output_path_input = QLineEdit()
        self.output_path_input.setObjectName("output_path_input")
        self.output_path_input.setPlaceholderText("选择导出文件保存位置...")
        path_layout.addWidget(self.output_path_input)
        
        self.browse_button = QPushButton("浏览...")
        self.browse_button.setObjectName("browse_button")
        self.browse_button.clicked.connect(self.browse_output_path)
        path_layout.addWidget(self.browse_button)
        
        config_layout.addLayout(path_layout)
        
        # 导出选项
        self.include_world = QCheckBox("包含世界文件")
        self.include_world.setObjectName("include_world")
        self.include_world.setChecked(True)
        config_layout.addWidget(self.include_world)
        
        self.include_lang_file = QCheckBox("生成语言文件")
        self.include_lang_file.setObjectName("include_lang_file")
        self.include_lang_file.setChecked(True)
        config_layout.addWidget(self.include_lang_file)
        
        self.compress_files = QCheckBox("压缩文件")
        self.compress_files.setObjectName("compress_files")
        self.compress_files.setChecked(True)
        config_layout.addWidget(self.compress_files)
        
        layout.addWidget(config_frame)
        
        # 信息预览
        preview_frame = QFrame()
        preview_frame.setObjectName("preview_frame")
        preview_layout = QVBoxLayout(preview_frame)
        preview_layout.setContentsMargins(20, 20, 20, 20)
        
        preview_title = QLabel("导出预览")
        preview_title.setObjectName("preview_title")
        preview_layout.addWidget(preview_title)
        
        self.preview_text = QTextEdit()
        self.preview_text.setObjectName("preview_text")
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(150)
        preview_layout.addWidget(self.preview_text)
        
        layout.addWidget(preview_frame)
        
        # 进度区域
        self.progress_frame = QFrame()
        self.progress_frame.setObjectName("progress_frame")
        self.progress_frame.setVisible(False)
        progress_layout = QVBoxLayout(self.progress_frame)
        progress_layout.setContentsMargins(20, 20, 20, 20)
        
        self.progress_label = QLabel("准备导出...")
        self.progress_label.setObjectName("progress_label")
        progress_layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progress_bar")
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_detail = QTextEdit()
        self.progress_detail.setObjectName("progress_detail")
        self.progress_detail.setReadOnly(True)
        self.progress_detail.setMaximumHeight(100)
        progress_layout.addWidget(self.progress_detail)
        
        layout.addWidget(self.progress_frame)
        
        layout.addStretch()
        
        # 操作按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.export_button = QPushButton("开始导出")
        self.export_button.setObjectName("export_button")
        self.export_button.clicked.connect(self.start_export)
        button_layout.addWidget(self.export_button)
        
        self.open_file_button = QPushButton("打开文件")
        self.open_file_button.setObjectName("open_file_button")
        self.open_file_button.setVisible(False)
        self.open_file_button.clicked.connect(self.open_exported_file)
        button_layout.addWidget(self.open_file_button)
        
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
            #config_frame, #preview_frame, #progress_frame {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
            #config_title, #preview_title, #progress_label {
                font-weight: bold;
                color: #424242;
                margin-bottom: 10px;
            }
            #path_label {
                font-weight: bold;
                color: #424242;
                margin-right: 10px;
            }
            #output_path_input {
                padding: 8px;
                border: 1px solid #bdbdbd;
                border-radius: 4px;
                font-size: 14px;
            }
            #browse_button {
                background-color: #00897b;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
                font-size: 14px;
            }
            #browse_button:hover {
                background-color: #00695c;
            }
            #include_world, #include_lang_file, #compress_files {
                font-size: 14px;
                margin: 5px 0;
            }
            #preview_text, #progress_detail {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: #fafafa;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
            }
            #progress_bar {
                height: 20px;
                border-radius: 10px;
            }
            #export_button, #open_file_button {
                background-color: #00897b;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 30px;
                font-size: 16px;
                font-weight: bold;
                margin: 0 5px;
            }
            #export_button:hover, #open_file_button:hover {
                background-color: #00695c;
            }
            #export_button:disabled {
                background-color: #bdbdbd;
                color: #757575;
            }
        """)
    
    def set_world_path(self, world_path: str):
        """设置世界路径"""
        self.world_path = world_path
        self.update_preview()
    
    def set_translation_data(self, translation_data: List[Dict[str, Any]]):
        """设置翻译数据"""
        self.translation_data = translation_data
        self.update_preview()
    
    def browse_output_path(self):
        """浏览输出路径"""
        if not self.world_path:
            QMessageBox.warning(self, "警告", "请先选择要导出的世界")
            return
        
        world_name = os.path.basename(self.world_path)
        default_name = f"{world_name}_translated.mcworld"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "选择导出位置", default_name,
            "Minecraft World (*.mcworld);;ZIP Files (*.zip);;All Files (*)"
        )
        
        if file_path:
            self.output_path_input.setText(file_path)
            self.update_preview()
    
    def update_preview(self):
        """更新预览信息"""
        if not self.output_path_input.text() or not self.world_path:
            return
        
        world_name = os.path.basename(self.world_path)
        translated_count = len([
            item for item in self.translation_data 
            if item.get('translation')
        ])
        
        preview_text = f"导出预览:\n"
        preview_text += f"世界名称: {world_name}\n"
        preview_text += f"输出文件: {os.path.basename(self.output_path_input.text())}\n"
        preview_text += f"已翻译文本: {translated_count} 条\n"
        preview_text += f"包含世界文件: {'是' if self.include_world.isChecked() else '否'}\n"
        preview_text += f"包含语言文件: {'是' if self.include_lang_file.isChecked() else '否'}\n"
        preview_text += f"压缩文件: {'是' if self.compress_files.isChecked() else '否'}\n"
        
        self.preview_text.setPlainText(preview_text)
    
    def generate_lang_file(self, output_path: str):
        """生成语言文件"""
        if not self.include_lang_file.isChecked():
            return
        
        lang_data = {}
        for item in self.translation_data:
            if item.get('translation'):
                # 创建唯一的key
                key = f"text.{hash(item['original']) & 0xFFFFFFFF:08x}"
                lang_data[key] = item['translation']
        
        # 写入JSON语言文件
        lang_file_path = os.path.join(output_path, "zh_cn.lang")
        with open(lang_file_path, 'w', encoding='utf-8') as f:
            json.dump(lang_data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"生成语言文件: {lang_file_path}")
    
    def start_export(self):
        """开始导出"""
        if not self.world_path:
            QMessageBox.warning(self, "警告", "世界路径未设置")
            return
        
        if not self.output_path_input.text():
            QMessageBox.warning(self, "警告", "请选择导出文件保存位置")
            return
        
        output_path = self.output_path_input.text()
        
        # 检查输出目录是否存在
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法创建输出目录:\n{str(e)}")
                return
        
        # 确认对话框
        reply = QMessageBox.question(
            self, "确认导出",
            f"确定要将世界导出到:\n{output_path}\n\n"
            f"这将创建一个包含翻译后世界的压缩包。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        try:
            # 显示进度界面
            self.progress_frame.setVisible(True)
            self.export_button.setEnabled(False)
            
            # 创建导出工作线程
            self.export_worker = ExportWorker(
                world_path=self.world_path,
                translation_data=self.translation_data,
                output_path=output_path,
                include_world=self.include_world.isChecked(),
                include_lang_file=self.include_lang_file.isChecked(),
                compress=self.compress_files.isChecked()
            )
            
            # 连接信号
            self.export_worker.progress_updated.connect(self.update_export_progress)
            self.export_worker.export_finished.connect(self.on_export_finished)
            self.export_worker.export_error.connect(self.on_export_error)
            
            # 启动导出
            self.export_worker.start()
            self.logger.info(f"开始导出世界到: {output_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出启动失败:\n{str(e)}")
            self.logger.error(f"导出启动失败: {e}")
    
    def update_export_progress(self, current: int, total: int, message: str):
        """更新导出进度"""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.progress_label.setText(f"导出进度: {current}/{total}")
        
        # 添加详细日志
        self.progress_detail.append(message)
        self.progress_detail.verticalScrollBar().setValue(
            self.progress_detail.verticalScrollBar().maximum()
        )
    
    def on_export_finished(self, results: Dict[str, Any]):
        """导出完成处理"""
        self.progress_frame.setVisible(True)
        self.export_button.setEnabled(True)
        self.open_file_button.setVisible(True)
        
        # 显示结果
        output_file = results.get('output_file', '')
        file_size = results.get('file_size', 0)
        files_included = results.get('files_included', [])
        
        summary = f"导出完成！\n"
        summary += f"输出文件: {os.path.basename(output_file)}\n"
        summary += f"文件大小: {file_size:,} 字节\n"
        summary += f"包含文件: {len(files_included)} 个\n"
        
        self.progress_detail.append("\n" + "="*50)
        self.progress_detail.append(summary)
        
        # 显示成功对话框
        QMessageBox.information(
            self, "导出成功",
            f"世界导出完成！\n\n"
            f"文件: {os.path.basename(output_file)}\n"
            f"大小: {file_size:,} 字节\n\n"
            f"可以使用\"打开文件\"按钮查看导出的文件。"
        )
        
        self.logger.info(f"导出完成: {output_file}")
        self.export_requested.emit(self.world_path, output_file)
    
    def on_export_error(self, error: str):
        """导出错误处理"""
        self.progress_frame.setVisible(False)
        self.export_button.setEnabled(True)
        
        QMessageBox.critical(self, "导出错误", f"导出过程中发生错误:\n{error}")
        self.logger.error(f"导出错误: {error}")
    
    def open_exported_file(self):
        """打开导出的文件"""
        output_path = self.output_path_input.text()
        if output_path and os.path.exists(output_path):
            import platform
            import subprocess
            
            if platform.system() == "Windows":
                os.startfile(output_path)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", output_path])
            else:
                subprocess.Popen(["xdg-open", output_path])
        else:
            QMessageBox.warning(self, "警告", "导出文件不存在")