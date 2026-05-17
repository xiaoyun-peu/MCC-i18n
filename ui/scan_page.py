# -*- coding: utf-8 -*-
"""
扫描页面 - Scan Page
"""
import os
from typing import List, Dict, Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QProgressBar, QTextEdit, QMessageBox, QCheckBox
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont

from workers.scan_worker import ScanWorker
from utils.logger import get_logger
from utils.config import Config


class ScanPage(QWidget):
    """扫描页面"""
    
    scan_started = pyqtSignal()
    scan_finished = pyqtSignal(list)
    proceed_to_translation_signal = pyqtSignal()  # 新增信号

    def __init__(self):
        super().__init__()
        self.logger = get_logger()
        self.config = Config()
        self.scan_worker = None
        self.world_path = ""
        self.scan_results = []
        self.init_ui()
        self.load_config()

        
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        
        # 标题
        title = QLabel("扫描文本内容")
        title.setObjectName("page_title")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # 说明文字
        description = QLabel(
            "系统将扫描世界文件中的所有可翻译文本，包括命令方块、实体名称、\n"
            "Boss栏名称等。扫描过程可能需要一些时间，请耐心等待。"
        )
        description.setObjectName("description")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(description)
        
        layout.addSpacing(20)
        
        # 扫描配置区域
        config_frame = QFrame()
        config_frame.setObjectName("config_frame")
        config_layout = QVBoxLayout(config_frame)
        config_layout.setContentsMargins(20, 20, 20, 20)
        
        config_title = QLabel("扫描配置")
        config_title.setObjectName("config_title")
        config_layout.addWidget(config_title)
        
        # 扫描选项
        self.scan_region = QCheckBox("扫描Region文件")
        self.scan_region.setObjectName("scan_option")
        self.scan_region.setChecked(True)
        config_layout.addWidget(self.scan_region)
        
        self.scan_data = QCheckBox("扫描Data文件")
        self.scan_data.setObjectName("scan_option")
        self.scan_data.setChecked(True)
        config_layout.addWidget(self.scan_data)
        
        self.scan_entities = QCheckBox("扫描实体名称")
        self.scan_entities.setObjectName("scan_option")
        self.scan_entities.setChecked(True)
        config_layout.addWidget(self.scan_entities)
        
        self.scan_playerdata = QCheckBox("扫描玩家数据")
        self.scan_playerdata.setObjectName("scan_option")
        self.scan_playerdata.setChecked(False)
        config_layout.addWidget(self.scan_playerdata)
        
        layout.addWidget(config_frame)
        
        # 进度区域
        self.progress_frame = QFrame()
        self.progress_frame.setObjectName("progress_frame")
        self.progress_frame.setVisible(False)
        progress_layout = QVBoxLayout(self.progress_frame)
        progress_layout.setContentsMargins(20, 20, 20, 20)
        
        self.progress_label = QLabel("准备扫描...")
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
        
        # 结果区域
        self.result_frame = QFrame()
        self.result_frame.setObjectName("result_frame")
        self.result_frame.setVisible(False)
        result_layout = QVBoxLayout(self.result_frame)
        result_layout.setContentsMargins(20, 20, 20, 20)
        
        result_title = QLabel("扫描结果")
        result_title.setObjectName("result_title")
        result_layout.addWidget(result_title)
        
        self.result_summary = QTextEdit()
        self.result_summary.setObjectName("result_summary")
        self.result_summary.setReadOnly(True)
        self.result_summary.setMaximumHeight(100)
        result_layout.addWidget(self.result_summary)
        
        layout.addWidget(self.result_frame)
        
        layout.addStretch()
        
        # 操作按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.scan_button = QPushButton("开始扫描")
        self.scan_button.setObjectName("scan_button")
        self.scan_button.clicked.connect(self.start_scan)
        button_layout.addWidget(self.scan_button)
        
        self.stop_button = QPushButton("停止")
        self.stop_button.setObjectName("stop_button")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_scan)
        button_layout.addWidget(self.stop_button)
        
        self.next_button = QPushButton("下一步")
        self.next_button.setObjectName("next_button")
        self.next_button.setEnabled(False)
        self.next_button.clicked.connect(self.proceed_to_translation)
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
            #config_frame, #progress_frame, #result_frame {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
            #config_title, #progress_label, #result_title {
                font-weight: bold;
                color: #424242;
                margin-bottom: 10px;
            }
            #scan_option {
                background-color: #f5f5f5;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 10px;
                text-align: left;
                font-size: 14px;
                margin: 5px 0;
            }
            #scan_option:checked {
                background-color: #e8f5e8;
                border-color: #4caf50;
                color: #2e7d32;
                font-weight: bold;
            }
            #progress_bar {
                height: 20px;
                border-radius: 10px;
                text-align: center;
            }
            #progress_detail, #result_summary {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: #fafafa;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
            }
            #scan_button, #next_button {
                background-color: #00897b;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 30px;
                font-size: 16px;
                font-weight: bold;
                margin: 0 5px;
            }
            #scan_button:hover, #next_button:hover, #stop_button:hover {
                background-color: #00695c;
            }
            #scan_button:disabled, #next_button:disabled, #stop_button:disabled {
                background-color: #bdbdbd;
                color: #757575;
            }
            #stop_button {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 30px;
                font-size: 16px;
                font-weight: bold;
                margin: 0 5px;
            }
            #stop_button:hover {
                background-color: #d32f2f;
            }
        """)
    
    def load_config(self):
        """加载配置"""
        try:
            scan_region = self.config.get('scan.scan_region', True)
            self.scan_region.setChecked(scan_region)
            
            scan_data = self.config.get('scan.scan_data', True)
            self.scan_data.setChecked(scan_data)
            
            scan_entities = self.config.get('scan.scan_entities', True)
            self.scan_entities.setChecked(scan_entities)
            
            scan_playerdata = self.config.get('scan.scan_playerdata', False)
            self.scan_playerdata.setChecked(scan_playerdata)
            
        except Exception as e:
            self.logger.error(f"加载扫描配置失败: {e}")
    
    def set_world_path(self, world_path: str):
        """设置世界路径"""
        self.world_path = world_path
        self.logger.info(f"设置扫描世界路径: {world_path}")
    
    def start_scan(self):
        """开始扫描"""
        if not self.world_path or not os.path.exists(self.world_path):  # 增加路径存在性检查
            QMessageBox.warning(self, "警告", "请先选择有效的世界文件夹")
            return
        
        # 保存当前配置
        self.config.set('scan.scan_region', self.scan_region.isChecked())
        self.config.set('scan.scan_data', self.scan_data.isChecked())
        self.config.set('scan.scan_entities', self.scan_entities.isChecked())
        self.config.set('scan.scan_playerdata', self.scan_playerdata.isChecked())
        
        # 显示进度界面
        self.progress_frame.setVisible(True)
        self.scan_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        
        # 创建扫描工作线程
        self.scan_worker = ScanWorker(
            world_path=self.world_path,
            scan_region=self.scan_region.isChecked(),
            scan_data=self.scan_data.isChecked(),
            scan_entities=self.scan_entities.isChecked(),
            scan_playerdata=self.scan_playerdata.isChecked()
        )
        
        # 连接信号
        self.scan_worker.progress_updated.connect(self.update_progress)
        self.scan_worker.scan_finished.connect(self.on_scan_finished)
        self.scan_worker.error_occurred.connect(self.on_scan_error)
        
        # 启动扫描
        self.scan_worker.start()
        self.scan_started.emit()
        self.logger.info("开始扫描世界文本")
    
    def update_progress(self, current: int, total: int, message: str):
        """更新进度"""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.progress_label.setText(f"扫描进度: {current}/{total}")
        
        # 添加详细日志
        self.progress_detail.append(message)
        self.progress_detail.verticalScrollBar().setValue(
            self.progress_detail.verticalScrollBar().maximum()
        )
    
    def on_scan_finished(self, results: List[Dict[str, Any]]):
        """扫描完成处理"""
        self.scan_results = results
        self.progress_frame.setVisible(False)
        self.result_frame.setVisible(True)
        
        # 显示结果摘要
        total_texts = len(results)
        unique_texts = len(set(result['original'] for result in results))
        
        summary = f"扫描完成！\n"
        summary += f"总文本数量: {total_texts}\n"
        summary += f"唯一文本数量: {unique_texts}\n"
        summary += f"扫描位置: {self.world_path}\n"
        
        self.result_summary.setPlainText(summary)
        
        # 启用下一步按钮，禁用停止按钮
        self.next_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.scan_button.setText("重新扫描")
        self.scan_button.setEnabled(True)
        
        self.logger.info(f"扫描完成，找到 {total_texts} 条文本，其中 {unique_texts} 条唯一")
        self.scan_finished.emit(results)
    
    def on_scan_error(self, error: str):
        """扫描错误处理"""
        self.progress_frame.setVisible(False)
        self.scan_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        QMessageBox.critical(self, "扫描错误", f"扫描过程中发生错误:\n{error}")
        self.logger.error(f"扫描错误: {error}")
    
    def stop_scan(self):
        """停止扫描"""
        if self.scan_worker and self.scan_worker.isRunning():
            self.scan_worker.stop()
            self.logger.info("正在停止扫描...")
            self.stop_button.setEnabled(False)
            self.stop_button.setText("停止中...")
    
    def proceed_to_translation(self):
        self.proceed_to_translation_signal.emit()
