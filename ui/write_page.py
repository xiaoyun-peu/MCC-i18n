# -*- coding: utf-8 -*-
"""
写入页面 - Write Page
"""

import os
import shutil
import zipfile
from datetime import datetime
from typing import List, Dict, Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTextEdit, QMessageBox, QProgressBar, QCheckBox
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont

from workers.write_worker import WriteWorker
from utils.logger import get_logger


class WritePage(QWidget):
    """写入页面"""
    
    write_requested = pyqtSignal(str, dict)
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger()
        self.world_path = ""
        self.translation_data = []
        self.write_worker = None
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # 标题
        title = QLabel("写入地图")
        title.setObjectName("page_title")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # 说明文字
        description = QLabel(
            "将翻译后的文本写回到Minecraft世界文件中。\n"
            "系统会自动创建备份，确保数据安全。"
        )
        description.setObjectName("description")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(description)
        
        layout.addSpacing(20)
        
        # 写入配置
        config_frame = QFrame()
        config_frame.setObjectName("config_frame")
        config_layout = QVBoxLayout(config_frame)
        config_layout.setContentsMargins(20, 20, 20, 20)
        
        config_title = QLabel("写入配置")
        config_title.setObjectName("config_title")
        config_layout.addWidget(config_title)
        
        # 备份选项
        self.backup_checkbox = QCheckBox("自动创建备份")
        self.backup_checkbox.setObjectName("backup_checkbox")
        self.backup_checkbox.setChecked(True)
        config_layout.addWidget(self.backup_checkbox)
        
        # 验证JSON选项
        self.validate_checkbox = QCheckBox("验证JSON格式")
        self.validate_checkbox.setObjectName("validate_checkbox")
        self.validate_checkbox.setChecked(True)
        config_layout.addWidget(self.validate_checkbox)
        
        # 覆盖现有翻译
        self.overwrite_checkbox = QCheckBox("覆盖现有翻译")
        self.overwrite_checkbox.setObjectName("overwrite_checkbox")
        self.overwrite_checkbox.setChecked(False)
        config_layout.addWidget(self.overwrite_checkbox)
        
        layout.addWidget(config_frame)
        
        # 统计信息
        self.stats_frame = QFrame()
        self.stats_frame.setObjectName("stats_frame")
        self.stats_frame.setVisible(False)
        stats_layout = QVBoxLayout(self.stats_frame)
        stats_layout.setContentsMargins(20, 20, 20, 20)
        
        stats_title = QLabel("翻译统计")
        stats_title.setObjectName("stats_title")
        stats_layout.addWidget(stats_title)
        
        self.stats_text = QTextEdit()
        self.stats_text.setObjectName("stats_text")
        self.stats_text.setReadOnly(True)
        self.stats_text.setMaximumHeight(100)
        stats_layout.addWidget(self.stats_text)
        
        layout.addWidget(self.stats_frame)
        
        # 进度区域
        self.progress_frame = QFrame()
        self.progress_frame.setObjectName("progress_frame")
        self.progress_frame.setVisible(False)
        progress_layout = QVBoxLayout(self.progress_frame)
        progress_layout.setContentsMargins(20, 20, 20, 20)
        
        self.progress_label = QLabel("准备写入...")
        self.progress_label.setObjectName("progress_label")
        progress_layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progress_bar")
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_detail = QTextEdit()
        self.progress_detail.setObjectName("progress_detail")
        self.progress_detail.setReadOnly(True)
        self.progress_detail.setMaximumHeight(150)
        progress_layout.addWidget(self.progress_detail)
        
        layout.addWidget(self.progress_frame)
        
        layout.addStretch()
        
        # 操作按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.write_button = QPushButton("开始写入")
        self.write_button.setObjectName("write_button")
        self.write_button.clicked.connect(self.start_write)
        button_layout.addWidget(self.write_button)
        
        self.open_dir_button = QPushButton("打开世界目录")
        self.open_dir_button.setObjectName("open_dir_button")
        self.open_dir_button.setVisible(False)
        self.open_dir_button.clicked.connect(self.open_world_directory)
        button_layout.addWidget(self.open_dir_button)
        
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
            #config_frame, #stats_frame, #progress_frame {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
            #config_title, #stats_title, #progress_label {
                font-weight: bold;
                color: #424242;
                margin-bottom: 10px;
            }
            #backup_checkbox, #validate_checkbox, #overwrite_checkbox {
                font-size: 14px;
                margin: 5px 0;
            }
            #stats_text, #progress_detail {
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
            #write_button, #open_dir_button {
                background-color: #00897b;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 30px;
                font-size: 16px;
                font-weight: bold;
                margin: 0 5px;
            }
            #write_button:hover, #open_dir_button:hover {
                background-color: #00695c;
            }
            #write_button:disabled {
                background-color: #bdbdbd;
                color: #757575;
            }
        """)
    
    def set_world_path(self, world_path: str):
        """设置世界路径"""
        self.world_path = world_path
    
    def set_translation_data(self, translation_data: List[Dict[str, Any]]):
        """设置翻译数据"""
        self.translation_data = translation_data
        self.update_stats()
        self.stats_frame.setVisible(True)
    
    def update_stats(self):
        """更新统计信息"""
        if not self.translation_data:
            return
        
        total = len(self.translation_data)
        translated = len([item for item in self.translation_data if item.get('translation')])
        untranslated = total - translated
        
        stats_text = f"翻译统计信息:\n"
        stats_text += f"总文本数量: {total}\n"
        stats_text += f"已翻译: {translated}\n"
        stats_text += f"未翻译: {untranslated}\n"
        stats_text += f"翻译完成度: {translated/total*100:.1f}%\n"
        
        self.stats_text.setPlainText(stats_text)
    
    def create_backup(self) -> str:
        """创建备份"""
        if not self.backup_checkbox.isChecked():
            return ""
        
        try:
            # 生成备份文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            world_name = os.path.basename(self.world_path)
            backup_name = f"{world_name}_{timestamp}_backup.zip"
            backup_path = os.path.join(os.path.dirname(self.world_path), backup_name)
            
            # 创建ZIP备份
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(self.world_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, self.world_path)
                        zipf.write(file_path, arcname)
            
            self.logger.info(f"备份创建完成: {backup_path}")
            return backup_path
            
        except Exception as e:
            self.logger.error(f"创建备份失败: {e}")
            raise Exception(f"备份创建失败: {e}")
    
    def start_write(self):
        """开始写入"""
        if not self.world_path:
            QMessageBox.warning(self, "警告", "世界路径未设置")
            return
        
        if not self.translation_data:
            QMessageBox.warning(self, "警告", "没有翻译数据可写入")
            return
        
        # 获取已翻译的数据
        translated_data = [
            item for item in self.translation_data 
            if item.get('translation')
        ]
        
        if not translated_data:
            QMessageBox.warning(self, "警告", "没有已翻译的文本可写入")
            return
        
        # 确认对话框
        reply = QMessageBox.question(
            self, "确认写入",
            f"确定要将 {len(translated_data)} 条翻译写入到世界文件中吗？\n"
            "此操作将修改原始文件，建议确保已创建备份。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        try:
            # 创建备份
            if self.backup_checkbox.isChecked():
                backup_path = self.create_backup()
                self.progress_detail.append(f"备份创建完成: {backup_path}")
            
            # 显示进度界面
            self.progress_frame.setVisible(True)
            self.write_button.setEnabled(False)
            
            # 创建写入工作线程
            self.write_worker = WriteWorker(
                world_path=self.world_path,
                translations=translated_data,
                validate_json=self.validate_checkbox.isChecked(),
                overwrite_existing=self.overwrite_checkbox.isChecked()
            )
            
            # 连接信号
            self.write_worker.progress_updated.connect(self.update_write_progress)
            self.write_worker.write_finished.connect(self.on_write_finished)
            self.write_worker.write_error.connect(self.on_write_error)
            
            # 启动写入
            self.write_worker.start()
            self.logger.info(f"开始写入翻译到世界文件，共 {len(translated_data)} 条")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"写入启动失败:\n{str(e)}")
            self.logger.error(f"写入启动失败: {e}")
    
    def update_write_progress(self, current: int, total: int, message: str):
        """更新写入进度"""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.progress_label.setText(f"写入进度: {current}/{total}")
        
        # 添加详细日志
        self.progress_detail.append(message)
        self.progress_detail.verticalScrollBar().setValue(
            self.progress_detail.verticalScrollBar().maximum()
        )
    
    def on_write_finished(self, results: Dict[str, Any]):
        """写入完成处理"""
        self.progress_frame.setVisible(True)
        self.write_button.setEnabled(True)
        self.open_dir_button.setVisible(True)
        
        # 显示结果
        success_count = results.get('success_count', 0)
        error_count = results.get('error_count', 0)
        total_count = results.get('total_count', 0)
        
        summary = f"写入完成！\n"
        summary += f"成功: {success_count}\n"
        summary += f"失败: {error_count}\n"
        summary += f"总计: {total_count}\n"
        
        if error_count > 0:
            summary += f"\n错误详情:\n"
            for error in results.get('errors', []):
                summary += f"- {error}\n"
        
        self.progress_detail.append("\n" + "="*50)
        self.progress_detail.append(summary)
        
        # 显示成功对话框
        if error_count == 0:
            QMessageBox.information(
                self, "写入成功",
                f"所有翻译已成功写入世界文件！\n"
                f"共写入 {success_count} 条翻译记录。"
            )
        else:
            QMessageBox.warning(
                self, "写入完成",
                f"写入完成，但有 {error_count} 条记录失败。\n"
                f"请查看日志了解详细信息。"
            )
        
        self.logger.info(f"写入完成，成功: {success_count}, 失败: {error_count}")
        self.write_requested.emit(self.world_path, results)
    
    def on_write_error(self, error: str):
        """写入错误处理"""
        self.progress_frame.setVisible(False)
        self.write_button.setEnabled(True)
        
        QMessageBox.critical(self, "写入错误", f"写入过程中发生错误:\n{error}")
        self.logger.error(f"写入错误: {error}")
    
    def open_world_directory(self):
        """打开世界目录"""
        if self.world_path and os.path.exists(self.world_path):
            import platform
            import subprocess
            
            if platform.system() == "Windows":
                os.startfile(self.world_path)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", self.world_path])
            else:
                subprocess.Popen(["xdg-open", self.world_path])
        else:
            QMessageBox.warning(self, "警告", "世界目录不存在")