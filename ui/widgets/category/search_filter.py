#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 分類搜尋過濾器

負責分類選擇器的搜尋和過濾功能，從原始 category_widget.py 
中分離出的 filter_topics() 方法相關邏輯。

從原始怪物檔案分離的功能：
- filter_topics() - 主題過濾邏輯
- 搜尋查詢解析和處理
- 結果過濾和高亮顯示
- 搜尋狀態維護

重構收益：
- 職責單一: 只負責搜尋過濾相關邏輯
- 可復用性: 可被其他需要搜尋功能的組件使用
- 可擴展性: 易於添加進階搜尋功能
- 新架構整合: 充分利用配置和日誌系統
"""

import re
from typing import List, Dict, Any, Optional, Set, Tuple
from PyQt5.QtWidgets import QWidget, QFrame, QCheckBox
from PyQt5.QtCore import pyqtSignal

from utils import get_logger, global_config
from ui.components.base import BaseWidget

class SearchFilter(BaseWidget):
    """
    分類搜尋過濾器
    
    提供強大的搜尋和過濾功能，支援多種搜尋模式和結果高亮。
    使用新架構工具確保高效率和高品質的搜尋體驗。
    
    主要功能：
    - 即時搜尋過濾
    - 模糊匹配和精確匹配
    - 搜尋結果高亮顯示
    - 搜尋歷史管理
    - 多語言搜尋支援
    
    Signals:
        search_started: 搜尋開始時發出
        search_completed: 搜尋完成時發出 (query, result_count)
        filter_applied: 過濾器應用時發出 (visible_items, hidden_items)
        search_cleared: 搜尋清空時發出
    
    Example:
        >>> filter = SearchFilter()
        >>> filter.set_search_data(categories_data)
        >>> 
        >>> # 執行搜尋
        >>> results = filter.apply_filter("三角形")
        >>> 
        >>> # 監聽搜尋事件
        >>> filter.search_completed.connect(on_search_done)
    """
    
    # 搜尋相關信號
    search_started = pyqtSignal(str)                    # query
    search_completed = pyqtSignal(str, int)             # query, result_count
    filter_applied = pyqtSignal(list, list)             # visible_items, hidden_items
    search_cleared = pyqtSignal()
    
    def __init__(self, parent=None, config=None):
        """
        初始化搜尋過濾器
        
        Args:
            parent: 父組件
            config: 配置字典，支援以下選項：
                - case_sensitive: 是否區分大小寫 (預設: False)
                - fuzzy_search: 是否啟用模糊搜尋 (預設: True)
                - highlight_results: 是否高亮搜尋結果 (預設: True)
                - search_history_size: 搜尋歷史大小 (預設: 10)
                - min_search_length: 最小搜尋長度 (預設: 1)
        """
        self._search_data = {}           # 搜尋數據 {item_id: searchable_text}
        self._search_history = []        # 搜尋歷史
        self._last_query = ""           # 最後搜尋查詢
        self._visible_items = set()     # 可見項目集合
        self._hidden_items = set()      # 隱藏項目集合
        
        super().__init__(parent, config)
        
        # 應用配置
        self.case_sensitive = self.get_config_value('case_sensitive', False)
        self.fuzzy_search = self.get_config_value('fuzzy_search', True)
        self.highlight_results = self.get_config_value('highlight_results', True)
        self.history_size = self.get_config_value('search_history_size', 10)
        self.min_length = self.get_config_value('min_search_length', 1)
        
        self.logger.info("搜尋過濾器初始化完成")
    
    def _setup_ui(self):
        """建立UI結構 - 過濾器不需要可視UI"""
        pass
    
    def _connect_signals(self):
        """連接信號 - 過濾器主要提供API，不需要內部信號連接"""
        pass
    
    def set_search_data(self, data: Dict[str, str]) -> None:
        """
        設定可搜尋數據
        
        Args:
            data: 搜尋數據字典 {item_id: searchable_text}
            
        Example:
            >>> data = {
            ...     "cat_0_代數": "代數 一次方程式 二次方程式",
            ...     "cat_1_幾何": "幾何 三角形 圓形 面積",
            ...     "subcat_0_0_一次方程式": "一次方程式 linear equation"
            ... }
            >>> filter.set_search_data(data)
        """
        try:
            self._search_data = dict(data)  # 複製字典避免外部修改
            
            # 初始化時所有項目都可見
            self._visible_items = set(data.keys())
            self._hidden_items.clear()
            
            self.logger.info(f"搜尋數據更新: {len(data)} 個項目")
            self.logger.debug(f"可搜尋項目: {list(data.keys())[:5]}...")  # 只記錄前5個
            
        except Exception as e:
            self.logger.error(f"設定搜尋數據失敗: {e}")
    
    def apply_filter(self, query: str) -> Dict[str, Any]:
        """
        應用搜尋過濾器
        
        Args:
            query: 搜尋查詢字串
            
        Returns:
            過濾結果字典，包含：
            - visible_items: 可見項目列表
            - hidden_items: 隱藏項目列表
            - match_count: 匹配數量
            - query: 處理後的查詢字串
            
        Example:
            >>> result = filter.apply_filter("三角形")
            >>> print(f"找到 {result['match_count']} 個結果")
            >>> for item in result['visible_items']:
            ...     print(f"匹配項目: {item}")
        """
        try:
            self.search_started.emit(query)
            self.logger.debug(f"開始搜尋: '{query}'")
            
            # 處理空查詢 - 顯示所有項目
            if not query or len(query.strip()) < self.min_length:
                return self._show_all_items()
            
            processed_query = self._preprocess_query(query.strip())
            
            # 執行搜尋
            visible_items = []
            hidden_items = []
            
            for item_id, searchable_text in self._search_data.items():
                if self._is_match(processed_query, searchable_text):
                    visible_items.append(item_id)
                else:
                    hidden_items.append(item_id)
            
            # 更新內部狀態
            self._visible_items = set(visible_items)
            self._hidden_items = set(hidden_items)
            self._last_query = query
            
            # 更新搜尋歷史
            self._update_search_history(query)
            
            # 準備結果
            result = {
                'visible_items': visible_items,
                'hidden_items': hidden_items,
                'match_count': len(visible_items),
                'query': query,
                'processed_query': processed_query
            }
            
            # 發送信號
            self.filter_applied.emit(visible_items, hidden_items)
            self.search_completed.emit(query, len(visible_items))
            
            self.logger.info(f"搜尋完成: '{query}' -> {len(visible_items)} 個結果")
            return result
            
        except Exception as e:
            self.logger.error(f"搜尋過濾失敗: {e}")
            return self._get_error_result(query)
    
    def clear_filter(self) -> bool:
        """
        清空過濾器，顯示所有項目
        
        Returns:
            操作是否成功
        """
        try:
            self.logger.debug("清空搜尋過濾器")
            
            result = self._show_all_items()
            self._last_query = ""
            
            self.search_cleared.emit()
            self.logger.info("搜尋過濾器已清空")
            return True
            
        except Exception as e:
            self.logger.error(f"清空過濾器失敗: {e}")
            return False
    
    def get_visible_items(self) -> List[str]:
        """
        獲取當前可見項目列表
        
        Returns:
            可見項目ID列表
        """
        return list(self._visible_items)
    
    def get_hidden_items(self) -> List[str]:
        """
        獲取當前隱藏項目列表
        
        Returns:
            隱藏項目ID列表
        """
        return list(self._hidden_items)
    
    def get_search_history(self) -> List[str]:
        """
        獲取搜尋歷史
        
        Returns:
            搜尋歷史列表，按時間倒序排列
        """
        return list(self._search_history)
    
    def is_item_visible(self, item_id: str) -> bool:
        """
        檢查項目是否可見
        
        Args:
            item_id: 項目ID
            
        Returns:
            項目是否可見
        """
        return item_id in self._visible_items
    
    def get_match_statistics(self) -> Dict[str, int]:
        """
        獲取匹配統計資訊
        
        Returns:
            統計字典，包含總項目數、可見項目數、隱藏項目數
        """
        total = len(self._search_data)
        visible = len(self._visible_items)
        hidden = len(self._hidden_items)
        
        return {
            'total_items': total,
            'visible_items': visible,
            'hidden_items': hidden,
            'match_rate': visible / total if total > 0 else 0
        }
    
    def _preprocess_query(self, query: str) -> str:
        """
        預處理搜尋查詢
        
        Args:
            query: 原始查詢字串
            
        Returns:
            處理後的查詢字串
        """
        processed = query
        
        # 大小寫處理
        if not self.case_sensitive:
            processed = processed.lower()
        
        # 移除多餘空白
        processed = re.sub(r'\s+', ' ', processed)
        
        return processed
    
    def _is_match(self, query: str, text: str) -> bool:
        """
        判斷文本是否匹配查詢
        
        Args:
            query: 處理後的查詢字串
            text: 要搜尋的文本
            
        Returns:
            是否匹配
        """
        # 大小寫處理
        search_text = text.lower() if not self.case_sensitive else text
        
        if self.fuzzy_search:
            # 模糊搜尋：查詢中的每個詞都要在文本中找到
            query_words = query.split()
            return all(word in search_text for word in query_words)
        else:
            # 精確搜尋：完整查詢字串要在文本中
            return query in search_text
    
    def _show_all_items(self) -> Dict[str, Any]:
        """
        顯示所有項目
        
        Returns:
            顯示所有項目的結果字典
        """
        all_items = list(self._search_data.keys())
        self._visible_items = set(all_items)
        self._hidden_items.clear()
        
        result = {
            'visible_items': all_items,
            'hidden_items': [],
            'match_count': len(all_items),
            'query': '',
            'processed_query': ''
        }
        
        self.filter_applied.emit(all_items, [])
        return result
    
    def _update_search_history(self, query: str) -> None:
        """
        更新搜尋歷史
        
        Args:
            query: 搜尋查詢
        """
        try:
            # 移除重複項目
            if query in self._search_history:
                self._search_history.remove(query)
            
            # 添加到開頭
            self._search_history.insert(0, query)
            
            # 限制歷史大小
            if len(self._search_history) > self.history_size:
                self._search_history = self._search_history[:self.history_size]
                
        except Exception as e:
            self.logger.warning(f"更新搜尋歷史失敗: {e}")
    
    def _get_error_result(self, query: str) -> Dict[str, Any]:
        """
        獲取錯誤情況下的結果
        
        Args:
            query: 原始查詢
            
        Returns:
            錯誤結果字典
        """
        return {
            'visible_items': [],
            'hidden_items': list(self._search_data.keys()),
            'match_count': 0,
            'query': query,
            'processed_query': '',
            'error': True
        }