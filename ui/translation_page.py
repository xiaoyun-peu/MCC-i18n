# -*- coding: utf-8 -*-
"""
翻译页面 - Translation Page
"""

import os
import csv
from typing import List, Dict, Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QLineEdit, QComboBox, QMessageBox, QFileDialog, QProgressBar,
    QTextEdit, QCheckBox
)
from PyQt6.QtCore import pyqtSignal, Qt, QThread
from PyQt6.QtGui import QFont, QColor

from workers.translate_worker import TranslateWorker
from utils.logger import get_logger


class TranslationPage(QWidget):
    """翻译页面"""
    
    translation_requested = pyqtSignal(list)
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger()
        self.translation_data = []
        self.filtered_data = []
        self.translate_worker = None
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # 标题
        title = QLabel("翻译管理")
        title.setObjectName("page_title")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # 工具栏
        toolbar = QFrame()
        toolbar.setObjectName("toolbar")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(10, 10, 10, 10)
        
        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setObjectName("search_input")
        self.search_input.setPlaceholderText("搜索文本...")
        self.search_input.textChanged.connect(self.filter_data)
        toolbar_layout.addWidget(self.search_input)
        
        # 语言选择
        self.lang_combo = QComboBox()
        self.lang_combo.setObjectName("lang_combo")
        self.lang_combo.addItems(["en → zh-cn", "zh-cn → en"])
        toolbar_layout.addWidget(self.lang_combo)
        
        # 机翻按钮
        self.translate_button = QPushButton("一键机翻")
        self.translate_button.setObjectName("translate_button")
        self.translate_button.clicked.connect(self.auto_translate)
        toolbar_layout.addWidget(self.translate_button)
        
        # 导入导出按钮
        self.import_button = QPushButton("导入")
        self.import_button.setObjectName("import_button")
        self.import_button.clicked.connect(self.import_translations)
        toolbar_layout.addWidget(self.import_button)
        
        self.export_button = QPushButton("导出")
        self.export_button.setObjectName("export_button")
        self.export_button.clicked.connect(self.export_translations)
        toolbar_layout.addWidget(self.export_button)
        
        layout.addWidget(toolbar)
        
        # 表格
        self.table = QTableWidget()
        self.table.setObjectName("translation_table")
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["原文", "译文", "出现次数", "状态"])
        
        # 设置表格属性
        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        self.table.setEditTriggers(QTableWidget.EditTrigger.DoubleClicked)
        self.table.cellChanged.connect(self.on_cell_changed)
        layout.addWidget(self.table)
        
        # 状态栏
        self.status_bar = QFrame()
        self.status_bar.setObjectName("status_bar")
        status_layout = QHBoxLayout(self.status_bar)
        status_layout.setContentsMargins(10, 10, 10, 10)
        
        self.status_label = QLabel("就绪")
        self.status_label.setObjectName("status_label")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progress_bar")
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)
        
        layout.addWidget(self.status_bar)
        
        # 设置样式
        self.setStyleSheet("""
            #page_title {
                color: #00695c;
                margin-bottom: 10px;
            }
            #toolbar, #status_bar {
                background-color: #f5f5f5;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
            }
            #search_input {
                padding: 8px;
                border: 1px solid #bdbdbd;
                border-radius: 4px;
                font-size: 14px;
            }
            #lang_combo, #translate_button, #import_button, #export_button {
                padding: 8px 15px;
                border: 1px solid #bdbdbd;
                border-radius: 4px;
                font-size: 14px;
                margin: 0 2px;
            }
            #translate_button {
                background-color: #00897b;
                color: white;
                border-color: #00897b;
            }
            #translate_button:hover {
                background-color: #00695c;
            }
            #translation_table {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
            }
            #translation_table QHeaderView::section {
                background-color: #f5f5f5;
                border: 1px solid #e0e0e0;
                padding: 8px;
                font-weight: bold;
            }
            #translation_table::item {
                padding: 8px;
                border-bottom: 1px solid #e0e0e0;
            }
            #translation_table::item:selected {
                background-color: #e8f5e8;
            }
            #status_label {
                color: #757575;
                font-size: 14px;
            }
            #progress_bar {
                height: 20px;
                border-radius: 10px;
            }
        """)
    
    def load_scan_results(self, results: List[Dict[str, Any]]):
        """加载扫描结果"""
        self.translation_data = []
        
        # 去重并统计出现次数
        text_count = {}
        for result in results:
            original = result.get('original', '')
            if original:
                if original not in text_count:
                    text_count[original] = {
                        'count': 0,
                        'locations': [],
                        'type': result.get('type', 'unknown')
                    }
                text_count[original]['count'] += 1
                text_count[original]['locations'].append(result.get('location', ''))
        
        # 转换为表格数据
        for original, info in text_count.items():
            self.translation_data.append({
                'original': original,
                'translation': '',
                'count': info['count'],
                'locations': info['locations'],
                'type': info['type'],
                'status': '未翻译'
            })
        
        self.update_table()
        self.update_status()
        self.logger.info(f"加载了 {len(self.translation_data)} 条待翻译文本")
    
    def update_table(self):
        """更新表格显示"""
        data_to_show = self.filtered_data if self.search_input.text() else self.translation_data
        
        self.table.setRowCount(len(data_to_show))
        
        for row, item in enumerate(data_to_show):
            # 原文
            original_item = QTableWidgetItem(item['original'])
            original_item.setData(Qt.ItemDataRole.UserRole, item)
            self.table.setItem(row, 0, original_item)
            
            # 译文
            translation_item = QTableWidgetItem(item['translation'])
            if item['translation']:
                translation_item.setBackground(QColor(200, 230, 200))  # 淡绿色
            self.table.setItem(row, 1, translation_item)
            
            # 出现次数
            count_item = QTableWidgetItem(str(item['count']))
            count_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 2, count_item)
            
            # 状态
            status_item = QTableWidgetItem(item['status'])
            if item['status'] == '未翻译':
                status_item.setBackground(QColor(255, 200, 200))  # 淡红色
            elif item['status'] == '已翻译':
                status_item.setBackground(QColor(200, 255, 200))  # 淡绿色
            elif item['status'] == '翻译中':
                status_item.setBackground(QColor(255, 255, 200))  # 淡黄色
            
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 3, status_item)
    
    def on_cell_changed(self, row: int, column: int):
        """单元格内容改变处理"""
        if column == 1:  # 译文列
            item = self.table.item(row, 0)
            if item:
                data = item.data(Qt.ItemDataRole.UserRole)
                translation = self.table.item(row, 1).text()
                
                # 更新数据
                data['translation'] = translation
                data['status'] = '已翻译' if translation else '未翻译'
                
                # 更新状态列
                status_item = self.table.item(row, 3)
                if status_item is None:  # 检查是否为 None
                    status_item = QTableWidgetItem()  # 创建新的 QTableWidgetItem
                    self.table.setItem(row, 3, status_item)  # 设置到表格中
                
                status_item.setText(data['status'])
                if translation:
                    status_item.setBackground(QColor(200, 255, 200))
                else:
                    status_item.setBackground(QColor(255, 200, 200))
                
                self.update_status()
    
    def filter_data(self):
        """过滤数据"""
        search_text = self.search_input.text().lower()
        
        if not search_text:
            self.filtered_data = []
        else:
            self.filtered_data = [
                item for item in self.translation_data
                if search_text in item['original'].lower() or 
                   search_text in item['translation'].lower()
            ]
        
        self.update_table()
    
    def auto_translate(self):
        """自动翻译"""
        if not self.translation_data:
            QMessageBox.warning(self, "警告", "没有需要翻译的文本")
            return
        
        # 获取未翻译的文本
        untranslated = [item for item in self.translation_data if not item['translation']]
        
        if not untranslated:
            QMessageBox.information(self, "提示", "所有文本都已翻译")
            return
        
        # 显示进度
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(untranslated))
        self.progress_bar.setValue(0)
        
        # 创建翻译工作线程
        self.translate_worker = TranslateWorker(
            texts=untranslated,
            target_lang=self.lang_combo.currentText()
        )
        
        # 连接信号
        self.translate_worker.translation_progress.connect(self.update_translation_progress)
        self.translate_worker.translation_finished.connect(self.on_translation_finished)
        self.translate_worker.translation_error.connect(self.on_translation_error)
        
        # 启动翻译
        self.translate_worker.start()
        self.status_label.setText("正在翻译...")
        
        # 更新状态
        for item in untranslated:
            item['status'] = '翻译中'
        self.update_table()
        
        self.logger.info(f"开始自动翻译 {len(untranslated)} 条文本")
    
    def update_translation_progress(self, current: int, total: int):
        """更新翻译进度"""
        self.progress_bar.setValue(current)
        self.status_label.setText(f"翻译进度: {current}/{total}")
    
    def on_translation_finished(self, results: List[Dict[str, Any]]):
        """翻译完成处理"""
        # 更新翻译结果
        for result in results:
            original = result['original']
            translation = result['translation']
            
            # 更新原始数据
            for item in self.translation_data:
                if item['original'] == original:
                    item['translation'] = translation
                    item['status'] = '已翻译'
                    break
        
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"翻译完成，共翻译 {len(results)} 条文本")
        self.update_table()
        self.update_status()
        
        self.logger.info(f"自动翻译完成，共翻译 {len(results)} 条文本")
        self.translation_requested.emit(results)
    
    def on_translation_error(self, error: str):
        """翻译错误处理"""
        self.progress_bar.setVisible(False)
        self.status_label.setText("翻译失败")
        
        QMessageBox.critical(self, "翻译错误", f"翻译过程中发生错误:\n{error}")
        self.logger.error(f"翻译错误: {error}")
    
    def import_translations(self):
        """导入翻译文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入翻译文件", "", 
            "CSV Files (*.csv);;Excel Files (*.xlsx);;All Files (*)"
        )
        
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    self.import_csv(file_path)
                else:
                    QMessageBox.warning(self, "提示", "目前只支持CSV格式导入")
            except Exception as e:
                QMessageBox.critical(self, "导入错误", f"导入失败:\n{str(e)}")
                self.logger.error(f"导入翻译文件失败: {e}")
    
    def import_csv(self, file_path: str):
        """导入CSV文件"""
        imported_count = 0
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # 跳过标题行
            
            for row in reader:
                if len(row) >= 2:
                    original, translation = row[0], row[1]
                    
                    # 查找匹配的原文
                    for item in self.translation_data:
                        if item['original'] == original:
                            item['translation'] = translation
                            item['status'] = '已翻译'
                            imported_count += 1
                            break
        
        self.update_table()
        self.update_status()
        
        QMessageBox.information(
            self, "导入完成", 
            f"成功导入 {imported_count} 条翻译记录"
        )
        self.logger.info(f"导入翻译文件完成，共导入 {imported_count} 条记录")
    
    def export_translations(self):
        """导出翻译文件"""
        if not self.translation_data:
            QMessageBox.warning(self, "警告", "没有数据可导出")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出翻译文件", "translations.csv",
            "CSV Files (*.csv);;Excel Files (*.xlsx);;All Files (*)"
        )
        
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    self.export_csv(file_path)
                else:
                    QMessageBox.warning(self, "提示", "目前只支持CSV格式导出")
            except Exception as e:
                QMessageBox.critical(self, "导出错误", f"导出失败:\n{str(e)}")
                self.logger.error(f"导出翻译文件失败: {e}")
    
    def export_csv(self, file_path: str):
        """导出CSV文件"""
        with open(file_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["原文", "译文", "出现次数", "类型", "位置"])
            
            for item in self.translation_data:
                locations = "; ".join(item.get('locations', [])[:3])  # 只显示前3个位置
                writer.writerow([
                    item['original'],
                    item['translation'],
                    item['count'],
                    item.get('type', ''),
                    locations
                ])
        
        QMessageBox.information(self, "导出完成", f"翻译文件已导出到:\n{file_path}")
        self.logger.info(f"导出翻译文件完成: {file_path}")
    
    def update_status(self):
        """更新状态信息"""
        total = len(self.translation_data)
        translated = len([item for item in self.translation_data if item['translation']])
        untranslated = total - translated
        
        self.status_label.setText(
            f"总计: {total} | 已翻译: {translated} | 未翻译: {untranslated}"
        )
    
    def get_translation_data(self) -> List[Dict[str, Any]]:
        """获取翻译数据"""
        return self.translation_data
    
    def proceed_to_translation(self):
        """进入翻译步骤"""
        if self.translation_data:
            self.logger.info("进入翻译页面")
            # 触发主窗口的页面切换逻辑
            self.parent().stack_widget.setCurrentIndex(2)  # 切换到翻译页面
