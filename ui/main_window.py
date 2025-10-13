# -*- coding: utf-8 -*-
"""
主窗口类 - Main Window Class
"""

import os
from typing import Optional, Dict, Any
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFrame,
    QPushButton, QLabel, QTextEdit, QStackedWidget, QFileDialog,
    QMessageBox, QMenuBar, QMenu, QStatusBar, QSplitter,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QComboBox, QCheckBox, QProgressBar, QDialog, QDialogButtonBox,
    QTextBrowser, QToolBar, QToolButton, QStyle, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer, QSize, QPoint
from PyQt6.QtGui import QIcon, QPixmap, QFont, QPalette, QColor, QMouseEvent

from qt_material import apply_stylesheet, list_themes

# 添加相对导入以解决 ModuleNotFoundError
from .navigation_widget import NavigationWidget
from .world_select_page import WorldSelectPage
from .scan_page import ScanPage
from .translation_page import TranslationPage
from .write_page import WritePage
from .export_page import ExportPage
from .settings_dialog import SettingsDialog
from workers.scan_worker import ScanWorker
from workers.write_worker import WriteWorker
from workers.translate_worker import TranslateWorker
from workers.export_worker import ExportWorker
from utils.logger import get_logger
from utils.config import Config
from utils.exceptions import MCCError


class MainWindow(QMainWindow):
    """主窗口类"""
    
    # 自定义信号
    theme_changed = pyqtSignal(str)
    
    def __init__(self, config: Config):
        super().__init__()
        self.config = config
        self.logger = get_logger()
        self.current_theme = "light_teal.xml"
        
        # 初始化UI
        self.init_ui()
        self.setup_connections()
        
        # 应用初始主题
        self.apply_theme(self.current_theme)
        
        self.logger.info("主窗口初始化完成")
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("Minecraft地图汉化工具 v1.0.0")
        self.setGeometry(100, 100, 1400, 900)
        
        # 创建无边框窗口
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 创建中心部件
        central_widget = QWidget()
        central_widget.setObjectName("central_widget")
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建导航栏
        self.navigation = NavigationWidget()
        main_layout.addWidget(self.navigation)
        
        # 创建内容区域
        content_widget = QWidget()
        content_widget.setObjectName("content_widget")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # 创建自定义标题栏
        self.create_title_bar()
        content_layout.addWidget(self.title_bar)

        # 标题栏样式
        self.title_bar.setStyleSheet("""
            #title_bar {
                background-color: #00897b;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }
            #title_label {
                color: white;
                font-weight: bold;
                font-size: 14px;
            }
            #theme_button, #min_button, #max_button, #close_button {
                background-color: transparent;
                border: none;
                color: white;
                font-size: 18px;  /* 调整字体大小 */
                padding: 5px;     /* 增加内边距 */
                border-radius: 15px;
            }
            #theme_button:hover, #min_button:hover, #max_button:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
            #close_button:hover {
                background-color: #f44336;
            }
        """)
        
        # 创建主工作区
        self.create_work_area()
        content_layout.addWidget(self.work_splitter)
        
        main_layout.addWidget(content_widget)
        
        # 设置样式
        self.setStyleSheet("""
            #central_widget {
                background-color: transparent;
            }
            #content_widget {
                background-color: #fafafa;
                border-radius: 10px;
            }
            MainWindow {
                background-color: #e0e0e0;
            }
        """)
    
    def create_title_bar(self):
        """创建自定义标题栏"""
        self.title_bar = QFrame()
        self.title_bar.setObjectName("title_bar")
        self.title_bar.setFixedHeight(40)
        
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)
        title_layout.setSpacing(10)
        
        # 应用图标
        icon_label = QLabel()
        icon_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons', 'app.png')
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio)
            icon_label.setPixmap(pixmap)
        title_layout.addWidget(icon_label)
        
        # 标题
        title_label = QLabel("Minecraft地图汉化工具")
        title_label.setObjectName("title_label")
        title_layout.addWidget(title_label)
        
        title_layout.addStretch()
        
        # 设置按钮：增加图标和样式调整
        self.settings_button = QPushButton()
        settings_icon_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons', 'settings.png')
        if os.path.exists(settings_icon_path):
            self.settings_button.setIcon(QIcon(settings_icon_path))
            self.settings_button.setIconSize(QSize(24, 24))
        self.settings_button.setObjectName("settings_button")
        self.settings_button.setFixedSize(30, 30)
        self.settings_button.setToolTip("设置")
        self.settings_button.clicked.connect(self.show_settings)
        title_layout.addWidget(self.settings_button)
        
        # 主题切换按钮
        self.theme_button = QPushButton("🌙")
        self.theme_button.setObjectName("theme_button")
        self.theme_button.setFixedSize(30, 30)
        self.theme_button.setToolTip("切换主题")
        title_layout.addWidget(self.theme_button)
        
        # 最小化按钮
        self.min_button = QPushButton("🗕")
        self.min_button.setObjectName("min_button")
        self.min_button.setFixedSize(30, 30)
        title_layout.addWidget(self.min_button)
        
        # 最大化/还原按钮
        self.max_button = QPushButton("🗖")
        self.max_button.setObjectName("max_button")
        self.max_button.setFixedSize(30, 30)
        title_layout.addWidget(self.max_button)
        
        # 关闭按钮
        self.close_button = QPushButton("✕")
        self.close_button.setObjectName("close_button")
        self.close_button.setFixedSize(30, 30)
        title_layout.addWidget(self.close_button)
        
    def create_work_area(self):
        """创建工作区域"""
        self.work_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 创建堆叠窗口
        self.stack_widget = QStackedWidget()
        
        # 创建各个页面
        self.world_select_page = WorldSelectPage()
        self.scan_page = ScanPage()
        self.translation_page = TranslationPage()
        self.write_page = WritePage()
        self.export_page = ExportPage()
        
        # 添加页面到堆叠窗口
        self.stack_widget.addWidget(self.world_select_page)
        self.stack_widget.addWidget(self.scan_page)
        self.stack_widget.addWidget(self.translation_page)
        self.stack_widget.addWidget(self.write_page)
        self.stack_widget.addWidget(self.export_page)
        
        # 创建日志区域
        self.log_widget = self.create_log_widget()
        
        # 添加到分割器
        self.work_splitter.addWidget(self.stack_widget)
        self.work_splitter.addWidget(self.log_widget)
        self.work_splitter.setStretchFactor(0, 3)
        self.work_splitter.setStretchFactor(1, 1)
        self.work_splitter.setHandleWidth(2)
    
    def create_log_widget(self):
        """创建日志组件"""
        log_frame = QFrame()
        log_frame.setObjectName("log_frame")
        log_layout = QVBoxLayout(log_frame)
        log_layout.setContentsMargins(5, 5, 5, 5)
        
        # 日志标题
        log_title = QLabel("日志输出")
        log_title.setObjectName("log_title")
        log_layout.addWidget(log_title)
        
        # 日志文本区域
        self.log_text = QTextEdit()
        self.log_text.setObjectName("log_text")
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        log_layout.addWidget(self.log_text)
        
        # 日志控制按钮
        log_controls = QHBoxLayout()
        
        self.clear_log_button = QPushButton("清屏")
        self.clear_log_button.setObjectName("clear_log_button")
        log_controls.addWidget(self.clear_log_button)
        
        self.copy_log_button = QPushButton("复制")
        self.copy_log_button.setObjectName("copy_log_button")
        log_controls.addWidget(self.copy_log_button)
        
        self.save_log_button = QPushButton("保存")
        self.save_log_button.setObjectName("save_log_button")
        log_controls.addWidget(self.save_log_button)
        
        log_layout.addLayout(log_controls)
        
        # 日志样式
        log_frame.setStyleSheet("""
            #log_frame {
                background-color: #f5f5f5;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
            }
            #log_title {
                font-weight: bold;
                color: #424242;
                margin-bottom: 5px;
            }
            #log_text {
                background-color: #263238;
                color: #eeffff;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                border: none;
                border-radius: 3px;
            }
            #clear_log_button, #copy_log_button, #save_log_button {
                background-color: #00897b;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
                font-size: 12px;
            }
            #clear_log_button:hover, #copy_log_button:hover, #save_log_button:hover {
                background-color: #00695c;
            }
        """)
        
        return log_frame
    
    def setup_connections(self):
        """设置信号连接"""
        # 导航连接
        self.navigation.page_changed.connect(self.stack_widget.setCurrentIndex)
        
        # ② → ③ 扫描完成后自动跳转
        self.scan_page.proceed_to_translation_signal.connect(
            lambda: (
                self.stack_widget.setCurrentIndex(2)
            )
        )
        # ③ → ④ 翻译请求后跳转
        self.write_page.write_requested.connect(
            lambda _, __: (
                self.stack_widget.setCurrentIndex(4)
            )
        )


        # 标题栏按钮连接
        self.min_button.clicked.connect(self.showMinimized)
        self.max_button.clicked.connect(self.toggle_maximized)
        self.close_button.clicked.connect(self.close)
        self.theme_button.clicked.connect(self.toggle_theme)
        
        # 日志按钮连接
        self.clear_log_button.clicked.connect(self.log_text.clear)
        self.copy_log_button.clicked.connect(self.copy_log)
        self.save_log_button.clicked.connect(self.save_log)
        
        # 页面间信号连接
        self.world_select_page.world_selected.connect(self.on_world_selected)
        self.scan_page.scan_started.connect(self.on_scan_started)
        self.scan_page.scan_finished.connect(self.on_scan_finished)
        self.translation_page.translation_requested.connect(self.on_translation_requested)
        self.write_page.write_requested.connect(self.on_write_requested)
        self.export_page.export_requested.connect(self.on_export_requested)
    
    def apply_theme(self, theme_name: str):
        """应用主题"""
        try:
            if theme_name.endswith('.xml'):
                apply_stylesheet(self, theme=theme_name, invert_secondary=False)
            else:
                apply_stylesheet(self, theme=f"{theme_name}.xml", invert_secondary=False)
            
            self.current_theme = theme_name
            self.logger.info(f"主题已切换为: {theme_name}")
            
            # 更新主题按钮
            if "dark" in theme_name.lower():
                self.theme_button.setText("☀️")
            else:
                self.theme_button.setText("🌙")
                
        except Exception as e:
            self.logger.error(f"应用主题失败: {e}")
    
    def toggle_theme(self):
        """切换主题"""
        if "dark" in self.current_theme.lower():
            new_theme = "light_teal.xml"
        else:
            new_theme = "dark_teal.xml"
        
        self.apply_theme(new_theme)
        self.theme_changed.emit(new_theme)
    
    def toggle_maximized(self):
        """切换最大化状态"""
        if self.isMaximized():
            self.showNormal()
            self.max_button.setText("🗖")
        else:
            self.showMaximized()
            self.max_button.setText("🗗")
    
    def on_world_selected(self, world_path: str):
        """世界选择完成处理"""
        self.logger.info(f"已选择世界: {world_path}")
        self.config.set('last_world', world_path)
        self.navigation.set_page_enabled(1, True)  # 启用扫描页面
        self.stack_widget.setCurrentIndex(1)
        # 确保将世界路径传递给扫描页面
        self.scan_page.set_world_path(world_path)

    def on_scan_started(self):
        """扫描开始处理"""
        self.logger.info("开始扫描文本...")
    
    def on_scan_finished(self, results: list):
        """扫描完成处理"""
        self.logger.info(f"扫描完成，找到 {len(results)} 条文本")
        self.translation_page.load_scan_results(results)
        self.navigation.set_page_enabled(2, True)  # 启用翻译页面
    
    def on_translation_requested(self, texts: list):
        """翻译请求处理"""
        self.logger.info(f"请求翻译 {len(texts)} 条文本")
    
    def on_write_requested(self, world_path: str, translations: dict):
        """写入请求处理"""
        self.logger.info("开始写入地图...")
    
    def on_export_requested(self, world_path: str, output_path: str):
        """导出请求处理"""
        self.logger.info(f"开始导出到: {output_path}")
    
    def copy_log(self):
        """复制日志内容"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.log_text.toPlainText())
        self.logger.info("日志已复制到剪贴板")
    
    def save_log(self):
        """保存日志到文件"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存日志", "mcc_i18n.log", "Log Files (*.log);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.toPlainText())
                self.logger.info(f"日志已保存到: {file_path}")
            except Exception as e:
                self.logger.error(f"保存日志失败: {e}")
    
    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下事件 - 用于窗口拖拽"""
        if event.button() == Qt.MouseButton.LeftButton:
            if event.position().y() <= 40:  # 标题栏高度
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标移动事件 - 用于窗口拖拽"""
        if event.buttons() & Qt.MouseButton.LeftButton:
            if hasattr(self, 'drag_position'):
                self.move(event.globalPosition().toPoint() - self.drag_position)
                event.accept()
    
    def show_settings(self):
        """显示设置对话框"""
        try:
            dialog = SettingsDialog(self)
            dialog.settings_changed.connect(self.on_settings_changed)
            dialog.exec()
        except Exception as e:
            self.logger.error(f"显示设置对话框失败: {e}")
            QMessageBox.critical(self, "错误", f"无法打开设置对话框: {e}")
    
    def on_settings_changed(self):
        """设置变更处理"""
        try:
            # 重新应用主题
            self.apply_theme(self.config.get_theme())
            self.logger.info("设置已更新")
        except Exception as e:
            self.logger.error(f"应用设置变更失败: {e}")
    
    def closeEvent(self, event):
        """关闭事件"""
        self.logger.info("应用程序关闭")
        event.accept()