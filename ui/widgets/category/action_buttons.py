#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 分類操作按鈕群組

負責分類選擇器的操作按鈕管理，從原始 category_widget.py 
中分離出的按鈕相關邏輯和操作功能。

從原始怪物檔案分離的功能：
- load_icons() - 圖示載入
- select_all_categories() - 全選操作
- deselect_all_categories() - 全取消操作
- expand_all_categories() - 全展開操作
- collapse_all_categories() - 全收折操作
- randomly_check_subcategories() - 隨機選擇
- distribute_evenly() - 平均分配

重構收益：
- 功能聚合: 所有按鈕相關邏輯集中管理
- UI 一致性: 統一的按鈕樣式和行為
- 可配置性: 按鈕顯示和功能可通過配置控制
- 新架構整合: 充分利用主題和配置系統
"""

import random
from typing import List, Dict, Any, Optional, Callable
from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QMessageBox
from PyQt5.QtCore import Qt, QSize, pyqtSignal

from utils import get_logger, global_config
from ui.components.base import BaseWidget
from ui.utils import load_icon

class ActionButtons(BaseWidget):
    """
    分類操作按鈕群組
    
    提供分類選擇器的所有操作按鈕，包括選擇控制、展開控制、
    隨機操作等。使用新架構設計確保一致的用戶體驗。
    
    主要功能：
    - 全選/全取消按鈕
    - 全展開/全收折按鈕
    - 隨機選擇功能
    - 平均分配功能
    - 可配置的按鈕組合
    - 統一的圖示和樣式管理
    
    Signals:
        select_all_requested: 請求全選操作
        deselect_all_requested: 請求全取消操作
        expand_all_requested: 請求全展開操作
        collapse_all_requested: 請求全收折操作
        random_select_requested: 請求隨機選擇 (count)
        distribute_evenly_requested: 請求平均分配 (total_questions)
    
    Example:
        >>> buttons = ActionButtons()
        >>> buttons.set_enabled_buttons(['select_all', 'expand_all', 'random'])
        >>> 
        >>> # 監聽操作請求
        >>> buttons.select_all_requested.connect(on_select_all)
        >>> buttons.random_select_requested.connect(on_random_select)
    """
    
    # 操作請求信號
    select_all_requested = pyqtSignal()
    deselect_all_requested = pyqtSignal()
    expand_all_requested = pyqtSignal()
    collapse_all_requested = pyqtSignal()
    random_select_requested = pyqtSignal(int)       # count
    distribute_evenly_requested = pyqtSignal(int)   # total_questions
    
    def __init__(self, parent=None, config=None):
        """
        初始化操作按鈕群組
        
        Args:
            parent: 父組件
            config: 配置字典，支援以下選項：
                - enabled_buttons: 啟用的按鈕列表 (預設: 全部)
                - button_height: 按鈕高度 (預設: 32)
                - show_icons: 是否顯示圖示 (預設: True)
                - show_tooltips: 是否顯示工具提示 (預設: True)
        """
        self._buttons = {}              # 按鈕字典 {name: button}
        self._button_configs = {}       # 按鈕配置
        self._random_count = 5          # 預設隨機選擇數量
        self._total_questions = 20      # 預設總題數
        
        super().__init__(parent, config)
        
        # 應用配置
        self.enabled_buttons = self.get_config_value('enabled_buttons', 
            ['select_all', 'deselect_all', 'expand_all', 'collapse_all', 'random', 'distribute'])
        self.button_height = self.get_config_value('button_height', 32)
        self.show_icons = self.get_config_value('show_icons', True)
        self.show_tooltips = self.get_config_value('show_tooltips', True)
        
        self.logger.info(f"操作按鈕群組初始化完成: {len(self.enabled_buttons)} 個按鈕")
    
    def _setup_ui(self):
        """建立按鈕群組UI"""
        try:
            # 主佈局
            self.layout = QHBoxLayout(self)
            self.layout.setContentsMargins(0, 0, 0, 0)
            self.layout.setSpacing(5)
            
            # 載入圖示
            self._load_icons()
            
            # 建立按鈕配置
            self._setup_button_configs()
            
            # 建立按鈕
            self._create_buttons()
            
            self.logger.debug("操作按鈕UI建立完成")
            
        except Exception as e:
            self.logger.error(f"建立按鈕群組UI失敗: {e}")
            raise
    
    def _connect_signals(self):
        """連接按鈕信號"""
        try:
            # 連接各按鈕的點擊信號
            button_handlers = {
                'select_all': self._on_select_all_clicked,
                'deselect_all': self._on_deselect_all_clicked,
                'expand_all': self._on_expand_all_clicked,
                'collapse_all': self._on_collapse_all_clicked,
                'random': self._on_random_clicked,
                'distribute': self._on_distribute_clicked
            }
            
            for button_name, handler in button_handlers.items():
                if button_name in self._buttons:
                    self._buttons[button_name].clicked.connect(handler)
            
            self.logger.debug("按鈕信號連接完成")
            
        except Exception as e:
            self.logger.error(f"連接按鈕信號失敗: {e}")
    
    def _load_icons(self):
        """載入所有需要的圖示"""
        try:
            self._icons = {
                'select_all': load_icon('check-square.svg'),
                'deselect_all': load_icon('square.svg'),
                'expand_all': load_icon('chevrons-down.svg'),
                'collapse_all': load_icon('chevrons-up.svg'),
                'random': load_icon('shuffle.svg'),
                'distribute': load_icon('bar-chart-2.svg')
            }
            self.logger.debug("按鈕圖示載入完成")
        except Exception as e:
            self.logger.warning(f"載入按鈕圖示失敗: {e}")
            self._icons = {}
    
    def _setup_button_configs(self):
        """設定按鈕配置"""
        self._button_configs = {
            'select_all': {
                'text': ' 全選',
                'tooltip': '選中所有分類和子分類',
                'icon_key': 'select_all'
            },
            'deselect_all': {
                'text': ' 全取消',
                'tooltip': '取消選中所有分類和子分類', 
                'icon_key': 'deselect_all'
            },
            'expand_all': {
                'text': ' 全展開',
                'tooltip': '展開所有分類',
                'icon_key': 'expand_all'
            },
            'collapse_all': {
                'text': ' 全收折',
                'tooltip': '收折所有分類',
                'icon_key': 'collapse_all'
            },
            'random': {
                'text': ' 隨機選擇',
                'tooltip': '隨機選擇指定數量的題型',
                'icon_key': 'random'
            },
            'distribute': {
                'text': ' 平均分配',
                'tooltip': '將總題數平均分配給已選題型',
                'icon_key': 'distribute'
            }
        }
    
    def _create_buttons(self):
        """建立所有啟用的按鈕"""
        try:
            for button_name in self.enabled_buttons:
                if button_name in self._button_configs:
                    button = self._create_single_button(button_name)
                    if button:
                        self._buttons[button_name] = button
                        self.layout.addWidget(button)
            
            # 添加彈性空間
            self.layout.addStretch()
            
            self.logger.info(f"建立了 {len(self._buttons)} 個操作按鈕")
            
        except Exception as e:
            self.logger.error(f"建立按鈕失敗: {e}")
    
    def _create_single_button(self, button_name: str) -> Optional[QPushButton]:
        """
        建立單個按鈕
        
        Args:
            button_name: 按鈕名稱
            
        Returns:
            建立的按鈕物件或None
        """
        try:
            config = self._button_configs[button_name]
            
            button = QPushButton(config['text'])
            button.setObjectName("controlButton")
            button.setFixedHeight(self.button_height)
            
            # 設定圖示
            if self.show_icons and config['icon_key'] in self._icons:
                button.setIcon(self._icons[config['icon_key']])
            
            # 設定工具提示
            if self.show_tooltips:
                button.setToolTip(config['tooltip'])
            
            return button
            
        except Exception as e:
            self.logger.error(f"建立按鈕 '{button_name}' 失敗: {e}")
            return None
    
    def _on_select_all_clicked(self):
        """處理全選按鈕點擊"""
        self.logger.debug("全選按鈕被點擊")
        self.select_all_requested.emit()
    
    def _on_deselect_all_clicked(self):
        """處理全取消按鈕點擊"""
        self.logger.debug("全取消按鈕被點擊")
        self.deselect_all_requested.emit()
    
    def _on_expand_all_clicked(self):
        """處理全展開按鈕點擊"""
        self.logger.debug("全展開按鈕被點擊")
        self.expand_all_requested.emit()
    
    def _on_collapse_all_clicked(self):
        """處理全收折按鈕點擊"""
        self.logger.debug("全收折按鈕被點擊")
        self.collapse_all_requested.emit()
    
    def _on_random_clicked(self):
        """處理隨機選擇按鈕點擊"""
        self.logger.debug(f"隨機選擇按鈕被點擊: {self._random_count} 個")
        self.random_select_requested.emit(self._random_count)
    
    def _on_distribute_clicked(self):
        """處理平均分配按鈕點擊"""
        self.logger.debug(f"平均分配按鈕被點擊: {self._total_questions} 題")
        self.distribute_evenly_requested.emit(self._total_questions)
    
    def set_random_count(self, count: int) -> bool:
        """
        設定隨機選擇數量
        
        Args:
            count: 隨機選擇數量
            
        Returns:
            設定是否成功
        """
        try:
            if count < 1:
                self.logger.warning(f"隨機選擇數量無效: {count}")
                return False
            
            self._random_count = count
            self.logger.debug(f"隨機選擇數量設定為: {count}")
            return True
            
        except Exception as e:
            self.logger.error(f"設定隨機選擇數量失敗: {e}")
            return False
    
    def set_total_questions(self, total: int) -> bool:
        """
        設定總題數
        
        Args:
            total: 總題數
            
        Returns:
            設定是否成功
        """
        try:
            if total < 1:
                self.logger.warning(f"總題數無效: {total}")
                return False
            
            self._total_questions = total
            self.logger.debug(f"總題數設定為: {total}")
            return True
            
        except Exception as e:
            self.logger.error(f"設定總題數失敗: {e}")
            return False
    
    def get_random_count(self) -> int:
        """
        獲取當前隨機選擇數量
        
        Returns:
            隨機選擇數量
        """
        return self._random_count
    
    def get_total_questions(self) -> int:
        """
        獲取當前總題數
        
        Returns:
            總題數
        """
        return self._total_questions
    
    def set_button_enabled(self, button_name: str, enabled: bool) -> bool:
        """
        設定按鈕啟用狀態
        
        Args:
            button_name: 按鈕名稱
            enabled: 是否啟用
            
        Returns:
            操作是否成功
        """
        try:
            if button_name in self._buttons:
                self._buttons[button_name].setEnabled(enabled)
                self.logger.debug(f"按鈕 '{button_name}' 啟用狀態: {enabled}")
                return True
            else:
                self.logger.warning(f"按鈕不存在: {button_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"設定按鈕啟用狀態失敗: {e}")
            return False
    
    def get_button_count(self) -> int:
        """
        獲取按鈕數量
        
        Returns:
            當前按鈕數量
        """
        return len(self._buttons)
    
    def get_enabled_buttons(self) -> List[str]:
        """
        獲取已啟用按鈕列表
        
        Returns:
            已啟用按鈕名稱列表
        """
        return [name for name, button in self._buttons.items() if button.isEnabled()]