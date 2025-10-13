# -*- coding: utf-8 -*-
"""
导出工作线程 - Export Worker Thread
"""

import os
import json
import zipfile
import shutil
from typing import List, Dict, Any, Optional
from PyQt6.QtCore import QThread, pyqtSignal

from utils.logger import get_logger


class ExportWorker(QThread):
    """导出工作线程"""
    
    progress_updated = pyqtSignal(int, int, str)
    export_finished = pyqtSignal(dict)
    export_error = pyqtSignal(str)
    
    def __init__(self, world_path: str, translation_data: List[Dict[str, Any]],
                 output_path: str, include_world: bool = True,
                 include_lang_file: bool = True, compress: bool = True):
        super().__init__()
        self.world_path = world_path
        self.translation_data = translation_data
        self.output_path = output_path
        self.include_world = include_world
        self.include_lang_file = include_lang_file
        self.compress = compress
        self.logger = get_logger()
        self.stop_flag = False
    
    def run(self):
        """运行导出"""
        try:
            results = {
                'output_file': self.output_path,
                'file_size': 0,
                'files_included': [],
                'world_path': self.world_path
            }
            
            self.logger.info(f"开始导出世界到: {self.output_path}")
            
            # 创建临时工作目录
            temp_dir = self.create_temp_directory()
            
            try:
                # 复制世界文件
                if self.include_world:
                    self.copy_world_files(temp_dir)
                
                # 生成语言文件
                if self.include_lang_file:
                    self.generate_language_files(temp_dir)
                
                # 创建压缩包
                self.create_archive(temp_dir, results)
                
                # 获取文件大小
                if os.path.exists(self.output_path):
                    results['file_size'] = os.path.getsize(self.output_path)
                
                # 发送完成信号
                self.export_finished.emit(results)
                self.logger.info(f"导出完成: {self.output_path}")
                
            finally:
                # 清理临时目录
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
            
        except Exception as e:
            error_msg = f"导出过程中发生错误: {str(e)}"
            self.logger.error(error_msg)
            self.export_error.emit(error_msg)
    
    def create_temp_directory(self) -> str:
        """创建临时工作目录"""
        import tempfile
        temp_dir = tempfile.mkdtemp(prefix='mcc_i18n_export_')
        self.logger.info(f"创建临时目录: {temp_dir}")
        return temp_dir
    
    def copy_world_files(self, temp_dir: str):
        """复制世界文件到临时目录"""
        self.progress_updated.emit(1, 3, "复制世界文件...")
        
        world_name = os.path.basename(self.world_path)
        target_dir = os.path.join(temp_dir, world_name)
        
        # 复制整个世界目录
        shutil.copytree(self.world_path, target_dir)
        
        self.logger.info(f"复制世界文件完成: {world_name}")
    
    def generate_language_files(self, temp_dir: str):
        """生成语言文件"""
        self.progress_updated.emit(2, 3, "生成语言文件...")
        
        # 创建语言文件目录
        lang_dir = os.path.join(temp_dir, 'lang')
        os.makedirs(lang_dir, exist_ok=True)
        
        # 生成中文语言文件
        zh_cn_data = {}
        en_us_data = {}
        
        for translation in self.translation_data:
            original = translation.get('original', '')
            translated = translation.get('translation', original)
            
            if translated and translated != original:
                # 创建唯一的key
                key = f"text.{hash(original) & 0xFFFFFFFF:08x}"
                zh_cn_data[key] = translated
                en_us_data[key] = original
        
        # 写入语言文件
        zh_cn_path = os.path.join(lang_dir, 'zh_cn.json')
        with open(zh_cn_path, 'w', encoding='utf-8') as f:
            json.dump(zh_cn_data, f, ensure_ascii=False, indent=2)
        
        en_us_path = os.path.join(lang_dir, 'en_us.json')
        with open(en_us_path, 'w', encoding='utf-8') as f:
            json.dump(en_us_data, f, ensure_ascii=False, indent=2)
        
        # 生成pack.mcmeta文件
        pack_data = {
            "pack": {
                "pack_format": 15,
                "description": f"Translation pack for {os.path.basename(self.world_path)}"
            }
        }
        
        pack_path = os.path.join(temp_dir, 'pack.mcmeta')
        with open(pack_path, 'w', encoding='utf-8') as f:
            json.dump(pack_data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"生成语言文件完成: {len(zh_cn_data)} 条翻译")
    
    def create_archive(self, temp_dir: str, results: Dict[str, Any]):
        """创建压缩包"""
        self.progress_updated.emit(3, 3, "创建压缩包...")
        
        # 确保输出目录存在
        output_dir = os.path.dirname(self.output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 创建ZIP文件
        with zipfile.ZipFile(self.output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)
                    results['files_included'].append(arcname)
        
        self.logger.info(f"创建压缩包完成: {len(results['files_included'])} 个文件")
    
    def stop(self):
        """停止导出"""
        self.stop_flag = True