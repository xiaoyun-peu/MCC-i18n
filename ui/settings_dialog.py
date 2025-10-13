# -*- coding: utf-8 -*-
"""
设置对话框 - Settings Dialog
"""

from typing import Dict, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QWidget, QCheckBox, QLineEdit, QSpinBox,
    QDoubleSpinBox, QComboBox, QGroupBox, QMessageBox
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont

from utils.config import Config
from utils.logger import get_logger


class SettingsDialog(QDialog):
    """设置对话框"""
    
    settings_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = Config()
        self.logger = get_logger()
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("设置")
        self.setModal(True)
        self.resize(600, 500)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建标签页
        self.tabs = QTabWidget()
        
        # 一般设置
        self.general_tab = self.create_general_tab()
        self.tabs.addTab(self.general_tab, "一般")
        
        # NBT设置
        self.nbt_tab = self.create_nbt_tab()
        self.tabs.addTab(self.nbt_tab, "NBT")
        
        # 扫描设置
        self.scan_tab = self.create_scan_tab()
        self.tabs.addTab(self.scan_tab, "扫描")
        
        # 翻译设置
        self.translation_tab = self.create_translation_tab()
        self.tabs.addTab(self.translation_tab, "翻译")
        
        # 导出设置
        self.export_tab = self.create_export_tab()
        self.tabs.addTab(self.export_tab, "导出")
        
        layout.addWidget(self.tabs)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.save_button = QPushButton("保存")
        self.save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_button)
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.apply_button = QPushButton("应用")
        self.apply_button.clicked.connect(self.apply_settings)
        button_layout.addWidget(self.apply_button)
        
        layout.addLayout(button_layout)
        
        # 设置样式
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QTabWidget::pane {
                border: 1px solid #e0e0e0;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f5f5f5;
                border: 1px solid #e0e0e0;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #00897b;
                color: white;
                border-color: #00897b;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e0e0e0;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #00897b;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00695c;
            }
            QPushButton:pressed {
                background-color: #004d40;
            }
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                padding: 6px;
                border: 1px solid #bdbdbd;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
                border-color: #00897b;
                outline: none;
            }
            QCheckBox {
                font-size: 14px;
                spacing: 8px;
            }
            QLabel {
                font-size: 14px;
            }
        """)
    
    def create_general_tab(self) -> QWidget:
        """创建一般设置标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # 界面设置
        ui_group = QGroupBox("界面设置")
        ui_layout = QVBoxLayout(ui_group)
        
        # 主题选择
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("主题:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["浅色主题", "深色主题"])
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        ui_layout.addLayout(theme_layout)
        
        # 语言选择
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("语言:"))
        self.language_combo = QComboBox()
        self.language_combo.addItems(["中文", "English"])
        lang_layout.addWidget(self.language_combo)
        lang_layout.addStretch()
        ui_layout.addLayout(lang_layout)
        
        layout.addWidget(ui_group)
        
        # 日志设置
        log_group = QGroupBox("日志设置")
        log_layout = QVBoxLayout(log_group)
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        log_layout.addWidget(QLabel("日志级别:"))
        log_layout.addWidget(self.log_level_combo)
        
        self.log_file_input = QLineEdit()
        self.log_file_input.setPlaceholderText("日志文件路径")
        log_layout.addWidget(QLabel("日志文件:"))
        log_layout.addWidget(self.log_file_input)
        
        layout.addWidget(log_group)
        
        layout.addStretch()
        return tab
    
    def create_nbt_tab(self) -> QWidget:
        """创建NBT设置标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # NBT读取设置
        read_group = QGroupBox("NBT读取设置")
        read_layout = QVBoxLayout(read_group)
        
        self.ignore_data_version = QCheckBox("忽略DataVersion检查")
        self.ignore_data_version.setToolTip("加载NBT文件时忽略DataVersion版本检查")
        read_layout.addWidget(self.ignore_data_version)
        
        self.force_gzip = QCheckBox("强制使用GZIP压缩")
        self.force_gzip.setToolTip("始终使用gzip=True参数加载NBT文件")
        self.force_gzip.setChecked(True)
        self.force_gzip.setEnabled(False)  # 默认启用，不可禁用
        read_layout.addWidget(self.force_gzip)
        
        self.strict_mode = QCheckBox("严格模式")
        self.strict_mode.setToolTip("对NBT文件格式要求更严格")
        read_layout.addWidget(self.strict_mode)
        
        layout.addWidget(read_group)
        
        # NBT写入设置
        write_group = QGroupBox("NBT写入设置")
        write_layout = QVBoxLayout(write_group)
        
        self.backup_before_write = QCheckBox("写入前自动备份")
        self.backup_before_write.setToolTip("在修改NBT文件前自动创建备份")
        write_layout.addWidget(self.backup_before_write)
        
        self.validate_json = QCheckBox("验证JSON格式")
        self.validate_json.setToolTip("写入前验证JSON文本格式")
        write_layout.addWidget(self.validate_json)
        
        layout.addWidget(write_group)
        
        layout.addStretch()
        return tab
    
    def create_scan_tab(self) -> QWidget:
        """创建扫描设置标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # 扫描选项
        scan_group = QGroupBox("扫描选项")
        scan_layout = QVBoxLayout(scan_group)
        
        self.scan_region = QCheckBox("扫描Region文件")
        scan_layout.addWidget(self.scan_region)
        
        self.scan_data = QCheckBox("扫描Data文件")
        scan_layout.addWidget(self.scan_data)
        
        self.scan_entities = QCheckBox("扫描实体名称")
        scan_layout.addWidget(self.scan_entities)
        
        self.scan_playerdata = QCheckBox("扫描玩家数据")
        scan_layout.addWidget(self.scan_playerdata)
        
        layout.addWidget(scan_group)
        
        # 扫描限制
        limit_group = QGroupBox("扫描限制")
        limit_layout = QVBoxLayout(limit_group)
        
        self.max_file_size = QSpinBox()
        self.max_file_size.setRange(1, 1000)
        self.max_file_size.setSuffix(" MB")
        self.max_file_size.setToolTip("跳过大于此大小的文件")
        
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("最大文件大小:"))
        size_layout.addWidget(self.max_file_size)
        size_layout.addStretch()
        limit_layout.addLayout(size_layout)
        
        self.max_text_length = QSpinBox()
        self.max_text_length.setRange(10, 10000)
        self.max_text_length.setSuffix(" 字符")
        self.max_text_length.setToolTip("忽略长度超过此限制的文本")
        
        length_layout = QHBoxLayout()
        length_layout.addWidget(QLabel("最大文本长度:"))
        length_layout.addWidget(self.max_text_length)
        length_layout.addStretch()
        limit_layout.addLayout(length_layout)
        
        layout.addWidget(limit_group)
        
        layout.addStretch()
        return tab
    
    def create_translation_tab(self) -> QWidget:
        """创建翻译设置标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # 翻译服务
        service_group = QGroupBox("翻译服务")
        service_layout = QVBoxLayout(service_group)
        
        self.translation_service = QComboBox()
        self.translation_service.addItems(["Google Translate", "Mock Translator (离线)"])
        service_layout.addWidget(QLabel("翻译服务:"))
        service_layout.addWidget(self.translation_service)
        
        self.batch_size = QSpinBox()
        self.batch_size.setRange(1, 100)
        self.batch_size.setToolTip("每次翻译的文本数量")
        
        batch_layout = QHBoxLayout()
        batch_layout.addWidget(QLabel("批量大小:"))
        batch_layout.addWidget(self.batch_size)
        batch_layout.addStretch()
        service_layout.addLayout(batch_layout)
        
        self.request_delay = QDoubleSpinBox()
        self.request_delay.setRange(0.1, 10.0)
        self.request_delay.setSingleStep(0.1)
        self.request_delay.setSuffix(" 秒")
        self.request_delay.setToolTip("翻译请求之间的延迟")
        
        delay_layout = QHBoxLayout()
        delay_layout.addWidget(QLabel("请求延迟:"))
        delay_layout.addWidget(self.request_delay)
        delay_layout.addStretch()
        service_layout.addLayout(delay_layout)
        
        layout.addWidget(service_group)
        
        # 翻译选项
        option_group = QGroupBox("翻译选项")
        option_layout = QVBoxLayout(option_group)
        
        self.auto_translate = QCheckBox("启用自动翻译")
        option_layout.addWidget(self.auto_translate)
        
        self.overwrite_existing = QCheckBox("覆盖现有翻译")
        option_layout.addWidget(self.overwrite_existing)
        
        self.save_translation_cache = QCheckBox("保存翻译缓存")
        option_layout.addWidget(self.save_translation_cache)
        
        layout.addWidget(option_group)
        
        layout.addStretch()
        return tab
    
    def create_export_tab(self) -> QWidget:
        """创建导出设置标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # 导出选项
        export_group = QGroupBox("导出选项")
        export_layout = QVBoxLayout(export_group)
        
        self.include_world = QCheckBox("包含世界文件")
        export_layout.addWidget(self.include_world)
        
        self.include_lang_file = QCheckBox("包含语言文件")
        export_layout.addWidget(self.include_lang_file)
        
        self.compress_export = QCheckBox("压缩导出文件")
        export_layout.addWidget(self.compress_export)
        
        self.add_timestamp = QCheckBox("添加时间戳")
        export_layout.addWidget(self.add_timestamp)
        
        layout.addWidget(export_group)
        
        # 文件格式
        format_group = QGroupBox("文件格式")
        format_layout = QVBoxLayout(format_group)
        
        self.export_format = QComboBox()
        self.export_format.addItems([".mcworld", ".zip", ".mcpack"])
        format_layout.addWidget(QLabel("导出格式:"))
        format_layout.addWidget(self.export_format)
        
        layout.addWidget(format_group)
        
        layout.addStretch()
        return tab
    
    def load_settings(self):
        """加载设置"""
        try:
            # 一般设置
            theme = self.config.get('theme', 'light_teal.xml')
            if 'dark' in theme.lower():
                self.theme_combo.setCurrentText("深色主题")
            else:
                self.theme_combo.setCurrentText("浅色主题")
            
            language = self.config.get('language', 'zh-CN')
            if language.startswith('zh'):
                self.language_combo.setCurrentText("中文")
            else:
                self.language_combo.setCurrentText("English")
            
            log_level = self.config.get('logging.level', 'INFO')
            self.log_level_combo.setCurrentText(log_level)
            
            log_file = self.config.get('logging.file', 'mcc_i18n.log')
            self.log_file_input.setText(log_file)
            
            # NBT设置
            ignore_data_version = self.config.get('nbt.ignore_data_version', False)
            self.ignore_data_version.setChecked(ignore_data_version)
            
            strict_mode = self.config.get('nbt.strict_mode', False)
            self.strict_mode.setChecked(strict_mode)
            
            backup_before_write = self.config.get('backup.auto_backup', True)
            self.backup_before_write.setChecked(backup_before_write)
            
            validate_json = self.config.get('nbt.validate_json', True)
            self.validate_json.setChecked(validate_json)
            
            # 扫描设置
            scan_region = self.config.get('scan.scan_region', True)
            self.scan_region.setChecked(scan_region)
            
            scan_data = self.config.get('scan.scan_data', True)
            self.scan_data.setChecked(scan_data)
            
            scan_entities = self.config.get('scan.scan_entities', True)
            self.scan_entities.setChecked(scan_entities)
            
            scan_playerdata = self.config.get('scan.scan_playerdata', False)
            self.scan_playerdata.setChecked(scan_playerdata)
            
            max_file_size = self.config.get('scan.max_file_size', 100)
            self.max_file_size.setValue(max_file_size)
            
            max_text_length = self.config.get('scan.max_text_length', 1000)
            self.max_text_length.setValue(max_text_length)
            
            # 翻译设置
            auto_translate = self.config.get('translation.auto_translate', False)
            self.auto_translate.setChecked(auto_translate)
            
            overwrite_existing = self.config.get('translation.overwrite_existing', False)
            self.overwrite_existing.setChecked(overwrite_existing)
            
            save_cache = self.config.get('translation.save_cache', True)
            self.save_translation_cache.setChecked(save_cache)
            
            batch_size = self.config.get('translation.batch_size', 10)
            self.batch_size.setValue(batch_size)
            
            request_delay = self.config.get('translation.delay_between_requests', 1.0)
            self.request_delay.setValue(request_delay)
            
            # 导出设置
            include_world = self.config.get('export.include_world', True)
            self.include_world.setChecked(include_world)
            
            include_lang_file = self.config.get('export.include_lang_file', True)
            self.include_lang_file.setChecked(include_lang_file)
            
            compress_export = self.config.get('export.compress_files', True)
            self.compress_export.setChecked(compress_export)
            
            add_timestamp = self.config.get('export.add_timestamp', True)
            self.add_timestamp.setChecked(add_timestamp)
            
            export_format = self.config.get('export.default_format', '.mcworld')
            self.export_format.setCurrentText(export_format)
            
        except Exception as e:
            self.logger.error(f"加载设置失败: {e}")
    
    def save_settings(self):
        """保存设置"""
        try:
            # 一般设置
            theme_text = self.theme_combo.currentText()
            if theme_text == "深色主题":
                self.config.set('theme', 'dark_teal.xml')
            else:
                self.config.set('theme', 'light_teal.xml')
            
            language_text = self.language_combo.currentText()
            if language_text == "中文":
                self.config.set('language', 'zh-CN')
            else:
                self.config.set('language', 'en-US')
            
            self.config.set('logging.level', self.log_level_combo.currentText())
            self.config.set('logging.file', self.log_file_input.text())
            
            # NBT设置
            self.config.set('nbt.ignore_data_version', self.ignore_data_version.isChecked())
            self.config.set('nbt.strict_mode', self.strict_mode.isChecked())
            self.config.set('backup.auto_backup', self.backup_before_write.isChecked())
            self.config.set('nbt.validate_json', self.validate_json.isChecked())
            
            # 扫描设置
            self.config.set('scan.scan_region', self.scan_region.isChecked())
            self.config.set('scan.scan_data', self.scan_data.isChecked())
            self.config.set('scan.scan_entities', self.scan_entities.isChecked())
            self.config.set('scan.scan_playerdata', self.scan_playerdata.isChecked())
            self.config.set('scan.max_file_size', self.max_file_size.value())
            self.config.set('scan.max_text_length', self.max_text_length.value())
            
            # 翻译设置
            self.config.set('translation.auto_translate', self.auto_translate.isChecked())
            self.config.set('translation.overwrite_existing', self.overwrite_existing.isChecked())
            self.config.set('translation.save_cache', self.save_translation_cache.isChecked())
            self.config.set('translation.batch_size', self.batch_size.value())
            self.config.set('translation.delay_between_requests', self.request_delay.value())
            
            # 导出设置
            self.config.set('export.include_world', self.include_world.isChecked())
            self.config.set('export.include_lang_file', self.include_lang_file.isChecked())
            self.config.set('export.compress_files', self.compress_export.isChecked())
            self.config.set('export.add_timestamp', self.add_timestamp.isChecked())
            self.config.set('export.default_format', self.export_format.currentText())
            
            self.logger.info("设置已保存")
            self.settings_changed.emit()
            self.accept()
            
        except Exception as e:
            self.logger.error(f"保存设置失败: {e}")
            QMessageBox.critical(self, "错误", f"保存设置失败: {e}")
    
    def apply_settings(self):
        """应用设置但不关闭对话框"""
        try:
            # 只应用一些立即生效的设置
            theme_text = self.theme_combo.currentText()
            if theme_text == "深色主题":
                self.config.set('theme', 'dark_teal.xml')
            else:
                self.config.set('theme', 'light_teal.xml')
            
            self.config.set('nbt.ignore_data_version', self.ignore_data_version.isChecked())
            
            self.logger.info("设置已应用")
            self.settings_changed.emit()
            
        except Exception as e:
            self.logger.error(f"应用设置失败: {e}")
            QMessageBox.critical(self, "错误", f"应用设置失败: {e}")
    
    def showEvent(self, event):
        """显示事件"""
        super().showEvent(event)
        self.load_settings()  # 重新加载设置以确保最新