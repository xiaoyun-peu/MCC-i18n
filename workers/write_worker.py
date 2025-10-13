# -*- coding: utf-8 -*-
"""
写入工作线程 - Write Worker Thread
"""

import os
import json
import shutil
from typing import List, Dict, Any, Optional
from PyQt6.QtCore import QThread, pyqtSignal

import nbtlib
from nbtlib import File, Compound, List as NBTList, String

from utils.logger import get_logger
from utils.json_validator import validate_json_text
from utils.config import Config


class WriteWorker(QThread):
    """写入工作线程"""
    
    progress_updated = pyqtSignal(int, int, str)
    write_finished = pyqtSignal(dict)
    write_error = pyqtSignal(str)
    
    def __init__(self, world_path: str, translations: List[Dict[str, Any]],
                 validate_json: bool = True, overwrite_existing: bool = False):
        super().__init__()
        self.world_path = world_path
        self.translations = translations
        self.validate_json = validate_json
        self.overwrite_existing = overwrite_existing
        self.logger = get_logger()
        self.config = Config()
        self.stop_flag = False
    
    def run(self):
        """运行写入"""
        try:
            results = {
                'success_count': 0,
                'error_count': 0,
                'total_count': len(self.translations),
                'errors': [],
                'world_path': self.world_path
            }
            
            self.logger.info(f"开始写入 {len(self.translations)} 条翻译到世界文件")
            
            # 创建写入映射
            write_map = self.create_write_map()
            
            # 处理每个文件
            total_files = len(write_map)
            processed_files = 0
            
            for file_path, translations in write_map.items():
                if self.stop_flag:
                    break
                
                processed_files += 1
                self.progress_updated.emit(
                    processed_files, total_files, 
                    f"处理文件: {os.path.basename(file_path)}"
                )
                
                try:
                    success_count, errors = self.write_to_file(file_path, translations)
                    results['success_count'] += success_count
                    results['error_count'] += len(errors)
                    results['errors'].extend(errors)
                    
                except Exception as e:
                    error_msg = f"处理文件 {file_path} 失败: {str(e)}"
                    self.logger.error(error_msg)
                    results['error_count'] += len(translations)
                    results['errors'].append(error_msg)
            
            # 发送完成信号
            self.write_finished.emit(results)
            self.logger.info(f"写入完成，成功: {results['success_count']}, 失败: {results['error_count']}")
            
        except Exception as e:
            error_msg = f"写入过程中发生错误: {str(e)}"
            self.logger.error(error_msg)
            self.write_error.emit(error_msg)
    
    def create_write_map(self) -> Dict[str, List[Dict[str, Any]]]:
        """创建写入映射"""
        write_map = {}
        
        for translation in self.translations:
            original = translation.get('original', '')
            translated = translation.get('translation', original)
            location = translation.get('location', '')
            
            if not location or not os.path.exists(location):
                continue
            
            if location not in write_map:
                write_map[location] = []
            
            write_map[location].append({
                'original': original,
                'translated': translated,
                'type': translation.get('type', 'text')
            })
        
        return write_map
    
    def write_to_file(self, file_path: str, translations: List[Dict[str, Any]]) -> tuple:
        """写入单个文件"""
        success_count = 0
        errors = []
        
        try:
            # 检查文件类型
            if file_path.endswith('.dat'):
                # NBT文件
                # 从配置中读取NBT加载选项
                ignore_data_version = self.config.get('nbt.ignore_data_version', False)
                nbt_file = File.load(file_path, gzipped=True)
                success_count, errors = self.write_to_nbt(nbt_file, translations)
                
                # 保存文件
                backup_path = file_path + '.bak'
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                shutil.move(file_path, backup_path)
                nbt_file.save(file_path)
                
            elif file_path.endswith('.mca'):
                # MCA文件（简化处理）
                success_count, errors = self.write_to_mca(file_path, translations)
            
            else:
                errors.append(f"不支持的文件类型: {file_path}")
        
        except Exception as e:
            errors.append(f"写入文件 {file_path} 失败: {str(e)}")
        
        return success_count, errors
    
    def write_to_nbt(self, nbt_data: Compound, translations: List[Dict[str, Any]]) -> tuple:
        """写入NBT数据"""
        success_count = 0
        errors = []
        
        for translation in translations:
            try:
                original = translation['original']
                translated = translation['translated']
                text_type = translation['type']
                
                # 根据类型写入不同位置
                if text_type == 'command_block' or 'Command' in str(nbt_data):
                    self.replace_in_nbt(nbt_data, original, translated, 'Command')
                
                elif text_type == 'entity_name' or 'CustomName' in str(nbt_data):
                    self.replace_in_nbt(nbt_data, original, translated, 'CustomName')
                
                elif text_type == 'json_text':
                    self.replace_json_in_nbt(nbt_data, original, translated)
                
                else:
                    # 通用替换
                    self.replace_in_nbt(nbt_data, original, translated)
                
                success_count += 1
                
            except Exception as e:
                errors.append(f"写入翻译 '{original}' 失败: {str(e)}")
        
        return success_count, errors
    
    def replace_in_nbt(self, data: Any, original: str, translated: str, target_key: str = None):
        """在NBT数据中替换文本"""
        if isinstance(data, Compound):
            for key, value in data.items():
                if target_key and key != target_key:
                    continue
                
                if isinstance(value, String) and original in str(value):
                    new_value = str(value).replace(original, translated)
                    data[key] = String(new_value)
                
                elif isinstance(value, (Compound, NBTList)):
                    self.replace_in_nbt(value, original, translated, target_key)
        
        elif isinstance(data, NBTList):
            for i, item in enumerate(data):
                if isinstance(item, (Compound, NBTList)):
                    self.replace_in_nbt(item, original, translated, target_key)
    
    def replace_json_in_nbt(self, data: Any, original: str, translated: str):
        """替换NBT中的JSON文本"""
        if isinstance(data, Compound):
            for key, value in data.items():
                if isinstance(value, String):
                    try:
                        # 尝试解析为JSON
                        json_str = str(value)
                        if json_str.startswith('{') or json_str.startswith('['):
                            json_data = json.loads(json_str)
                            modified = self.replace_in_json(json_data, original, translated)
                            if modified and (self.validate_json and validate_json_text(json_data)):
                                data[key] = String(json.dumps(json_data, ensure_ascii=False))
                    except:
                        # 如果不是有效的JSON，直接替换
                        if original in str(value):
                            new_value = str(value).replace(original, translated)
                            data[key] = String(new_value)
                
                elif isinstance(value, (Compound, NBTList)):
                    self.replace_json_in_nbt(value, original, translated)
        
        elif isinstance(data, NBTList):
            for i, item in enumerate(data):
                if isinstance(item, (Compound, NBTList)):
                    self.replace_json_in_nbt(item, original, translated)
    
    def replace_in_json(self, data: Any, original: str, translated: str) -> bool:
        """在JSON数据中替换文本"""
        modified = False
        
        if isinstance(data, dict):
            for key, value in data.items():
                if key == 'text' and isinstance(value, str) and original in value:
                    data[key] = value.replace(original, translated)
                    modified = True
                
                elif isinstance(value, (dict, list)):
                    if self.replace_in_json(value, original, translated):
                        modified = True
        
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, str) and original in item:
                    data[i] = item.replace(original, translated)
                    modified = True
                
                elif isinstance(item, (dict, list)):
                    if self.replace_in_json(item, original, translated):
                        modified = True
        
        return modified
    
    def write_to_mca(self, file_path: str, translations: List[Dict[str, Any]]) -> tuple:
        """写入MCA文件（简化处理）"""
        success_count = 0
        errors = []
        
        try:
            # 读取文件内容
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # 转换为字符串进行处理
            content_str = content.decode('utf-8', errors='ignore')
            modified = False
            
            for translation in translations:
                original = translation['original']
                translated = translation['translated']
                
                if original in content_str:
                    content_str = content_str.replace(original, translated)
                    modified = True
                    success_count += 1
            
            # 如果有修改，写回文件
            if modified:
                # 创建备份
                backup_path = file_path + '.bak'
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                shutil.move(file_path, backup_path)
                
                # 写回修改后的内容
                with open(file_path, 'wb') as f:
                    f.write(content_str.encode('utf-8', errors='ignore'))
            
        except Exception as e:
            errors.append(f"处理MCA文件失败: {str(e)}")
        
        return success_count, errors
    
    def stop(self):
        """停止写入"""
        self.stop_flag = True