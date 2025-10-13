# -*- coding: utf-8 -*-
"""
扫描工作线程 - Scan Worker Thread
"""

import os
import re
import json
from typing import List, Dict, Any, Optional
from PyQt6.QtCore import QThread, pyqtSignal

import nbtlib
from nbtlib import File, Compound, List as NBTList

from utils.logger import get_logger
from utils.config import Config


class ScanWorker(QThread):
    """扫描工作线程"""
    
    progress_updated = pyqtSignal(int, int, str)
    scan_finished = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, world_path: str, scan_region: bool = True, 
                 scan_data: bool = True, scan_entities: bool = True,
                 scan_playerdata: bool = False):
        super().__init__()
        self.world_path = world_path
        self.scan_region = scan_region
        self.scan_data = scan_data
        self.scan_entities = scan_entities
        self.scan_playerdata = scan_playerdata
        self.logger = get_logger()
        self.config = Config()
        self.results = []
        self.stop_flag = False
    
    def run(self):
        """运行扫描"""
        try:
            self.results = []
            total_files = 0
            processed_files = 0
            
            # 统计总文件数
            if self.scan_region:
                region_path = os.path.join(self.world_path, "region")
                if os.path.exists(region_path):
                    total_files += len([f for f in os.listdir(region_path) if f.endswith('.mca')])
            
            if self.scan_data:
                data_path = os.path.join(self.world_path, "data")
                if os.path.exists(data_path):
                    total_files += len([f for f in os.listdir(data_path) if f.endswith('.dat')])
            
            if self.scan_entities:
                entities_path = os.path.join(self.world_path, "entities")
                if os.path.exists(entities_path):
                    total_files += len([f for f in os.listdir(entities_path) if f.endswith('.mca')])
            
            self.logger.info(f"开始扫描，总计 {total_files} 个文件")
            
            # 扫描各个区域
            if self.scan_region:
                processed_files = self.scan_region_files(processed_files, total_files)
            
            if self.scan_data:
                processed_files = self.scan_data_files(processed_files, total_files)
            
            if self.scan_entities:
                processed_files = self.scan_entity_files(processed_files, total_files)
            
            if self.scan_playerdata:
                processed_files = self.scan_playerdata_files(processed_files, total_files)
            
            # 完成信号
            self.scan_finished.emit(self.results)
            self.logger.info(f"扫描完成，找到 {len(self.results)} 条文本")
            
        except Exception as e:
            error_msg = f"扫描过程中发生错误: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
    
    def scan_region_files(self, current: int, total: int) -> int:
        """扫描region文件"""
        region_path = os.path.join(self.world_path, "region")
        if not os.path.exists(region_path):
            return current
        
        mca_files = [f for f in os.listdir(region_path) if f.endswith('.mca')]
        
        for mca_file in mca_files:
            if self.stop_flag:
                break
            
            file_path = os.path.join(region_path, mca_file)
            self.progress_updated.emit(current + 1, total, f"扫描: {mca_file}")
            
            try:
                self.scan_mca_file(file_path)
            except Exception as e:
                self.logger.warning(f"扫描文件 {mca_file} 失败: {e}")
            
            current += 1
        
        return current
    
    def scan_data_files(self, current: int, total: int) -> int:
        """扫描data文件"""
        data_path = os.path.join(self.world_path, "data")
        if not os.path.exists(data_path):
            return current
        
        dat_files = [f for f in os.listdir(data_path) if f.endswith('.dat')]
        
        for dat_file in dat_files:
            if self.stop_flag:
                break
            
            file_path = os.path.join(data_path, dat_file)
            self.progress_updated.emit(current + 1, total, f"扫描: {dat_file}")
            
            try:
                self.scan_dat_file(file_path)
            except Exception as e:
                self.logger.warning(f"扫描文件 {dat_file} 失败: {e}")
            
            current += 1
        
        return current
    
    def scan_playerdata_files(self, current: int, total: int) -> int:
        """扫描玩家数据文件"""
        playerdata_path = os.path.join(self.world_path, "playerdata")
        if not os.path.exists(playerdata_path):
            return current
        
        dat_files = [f for f in os.listdir(playerdata_path) if f.endswith('.dat')]
        
        for dat_file in dat_files:
            if self.stop_flag:
                break
            
            file_path = os.path.join(playerdata_path, dat_file)
            self.progress_updated.emit(current + 1, total, f"扫描玩家数据: {dat_file}")
            
            try:
                self.scan_dat_file(file_path)
            except Exception as e:
                self.logger.warning(f"扫描玩家数据文件 {dat_file} 失败: {e}")
            
            current += 1
        
        return current
    
    def scan_entity_files(self, current: int, total: int) -> int:
        """扫描实体文件"""
        entities_path = os.path.join(self.world_path, "entities")
        if not os.path.exists(entities_path):
            return current
        
        mca_files = [f for f in os.listdir(entities_path) if f.endswith('.mca')]
        
        for mca_file in mca_files:
            if self.stop_flag:
                break
            
            file_path = os.path.join(entities_path, mca_file)
            self.progress_updated.emit(current + 1, total, f"扫描实体: {mca_file}")
            
            try:
                self.scan_entity_file(file_path)
            except Exception as e:
                self.logger.warning(f"扫描实体文件 {mca_file} 失败: {e}")
            
            current += 1
        
        return current
    
    def scan_mca_file(self, file_path: str):
        """扫描MCA文件"""
        try:
            # 这里简化处理，实际应该解析MCA文件的chunk数据
            # 由于MCA解析较复杂，这里使用简化的方法
            with open(file_path, 'rb') as f:
                content = f.read()
                
            # 查找可能的文本内容
            text_patterns = [
                rb'Command:\s*"([^"]*)"',  # 命令方块命令
                rb'CustomName:\s*"([^"]*)"',  # 实体自定义名称
                rb'text:\s*"([^"]*)"',  # JSON文本
                rb'name:\s*"([^"]*)"',  # 名称字段
            ]
            
            for pattern in text_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    if isinstance(match, bytes):
                        text = match.decode('utf-8', errors='ignore')
                    else:
                        text = str(match)
                    
                    if self.is_translatable_text(text):
                        self.add_result(text, 'command_block', file_path)
        
        except Exception as e:
            self.logger.debug(f"扫描MCA文件 {file_path} 时出错: {e}")
    
    def scan_dat_file(self, file_path: str):
        """扫描DAT文件"""
        try:
            # 从配置中读取NBT加载选项
            ignore_data_version = self.config.get('nbt.ignore_data_version', False)
            
            # 使用nbtlib解析NBT文件，强制使用gzip=True
            nbt_file = File.load(file_path, gzipped=True)
            
            # 递归扫描NBT数据
            self.scan_nbt_data(nbt_file, file_path)
            
        except Exception as e:
            self.logger.debug(f"扫描DAT文件 {file_path} 时出错: {e}")
    
    def scan_entity_file(self, file_path: str):
        """扫描实体文件"""
        try:
            # 类似于MCA文件扫描，但专注于实体数据
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # 查找实体名称
            name_patterns = [
                rb'CustomName:\s*"([^"]*)"',
                rb'name:\s*"([^"]*)"',
            ]
            
            for pattern in name_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    if isinstance(match, bytes):
                        text = match.decode('utf-8', errors='ignore')
                    else:
                        text = str(match)
                    
                    if self.is_translatable_text(text):
                        self.add_result(text, 'entity_name', file_path)
        
        except Exception as e:
            self.logger.debug(f"扫描实体文件 {file_path} 时出错: {e}")
    
    def scan_nbt_data(self, data: Any, file_path: str, path: str = ""):
        """递归扫描NBT数据"""
        if isinstance(data, Compound):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                
                # 检查特定字段
                if key in ['Command', 'CustomName', 'Name']:
                    if isinstance(value, str) and self.is_translatable_text(value):
                        self.add_result(value, f'nbt_{key.lower()}', file_path)
                
                # 递归处理
                self.scan_nbt_data(value, file_path, current_path)
        
        elif isinstance(data, NBTList):
            for i, item in enumerate(data):
                current_path = f"{path}[{i}]"
                self.scan_nbt_data(item, file_path, current_path)
        
        elif isinstance(data, str):
            # 检查字符串内容
            if self.is_translatable_text(data):
                # 尝试解析JSON文本
                if data.startswith('{') or data.startswith('['):
                    try:
                        json_data = json.loads(data)
                        self.scan_json_text(json_data, file_path)
                    except:
                        # 如果不是有效的JSON，直接作为文本处理
                        self.add_result(data, 'text', file_path)
                else:
                    self.add_result(data, 'text', file_path)
    
    def scan_json_text(self, data: Any, file_path: str):
        """扫描JSON文本内容"""
        if isinstance(data, dict):
            # 查找text字段
            if 'text' in data and isinstance(data['text'], str):
                if self.is_translatable_text(data['text']):
                    self.add_result(data['text'], 'json_text', file_path)
            
            # 查找extra字段
            if 'extra' in data and isinstance(data['extra'], list):
                for item in data['extra']:
                    self.scan_json_text(item, file_path)
            
            # 递归处理其他字段
            for key, value in data.items():
                if key != 'text' and key != 'extra':
                    self.scan_json_text(value, file_path)
        
        elif isinstance(data, list):
            for item in data:
                self.scan_json_text(item, file_path)
    
    def is_translatable_text(self, text: str) -> bool:
        """判断是否为可翻译文本"""
        if not text or not isinstance(text, str):
            return False
        
        # 过滤掉太短或太长的文本
        if len(text.strip()) < 2 or len(text) > 1000:
            return False
        
        # 过滤掉纯数字、符号或代码
        if re.match(r'^[\d\s\W]+$', text):
            return False
        
        # 过滤掉明显的命令或代码
        if text.startswith('/') or text.startswith('@') or text.startswith('#'):
            return False
        
        # 过滤掉UUID等标识符
        if re.match(r'^[a-fA-F0-9-]{36}$', text):
            return False
        
        # 过滤掉坐标等数字
        if re.match(r'^-?\d+(?:\s+-?\d+){1,2}$', text.strip()):
            return False
        
        return True
    
    def add_result(self, text: str, text_type: str, location: str):
        """添加扫描结果"""
        if text and text.strip():
            self.results.append({
                'original': text.strip(),
                'type': text_type,
                'location': location,
                'file': os.path.basename(location)
            })
    
    def stop(self):
        """停止扫描"""
        self.stop_flag = True