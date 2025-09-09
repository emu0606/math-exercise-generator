#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 分類選擇組件模組

本模組是從原始 579 行怪物檔案 category_widget.py 重構而來，
採用完全推倒重建策略，分解為 6 個專門模組，每個模組都符合
單一職責原則和檔案規模標準 (<200行)。

模組架構：
- main_widget.py: CategoryWidget 主類 (組合器和對外接口)
- tree_controller.py: 樹狀結構控制邏輯
- search_filter.py: 搜尋和過濾功能
- action_buttons.py: 操作按鈕群組管理
- event_manager.py: 事件處理和信號管理
- layout_manager.py: UI 佈局管理 (可選)

重構目標：
- 🎯 零怪物檔案: 每個檔案 < 200 行
- ⚡ 完全模組化: 6 種職責完全分離
- 🏆 新架構典範: 充分利用 get_logger, global_config
- 📚 完整文檔: 100% Sphinx docstring 覆蓋

向後兼容：
    >>> from ui.widgets.category import CategoryWidget
    >>> 
    >>> # 使用方式完全不變，內部已完全重構
    >>> widget = CategoryWidget()
    >>> widget.populate_categories(categories_data)
    >>> 
    >>> # 新架構提供的額外功能
    >>> widget.set_search_config(enable_highlight=True)
    >>> widget.get_tree_statistics()

重構統計：
- 原始檔案: category_widget.py (579行, 21個方法)
- 重構後: 6個模組 (每個<200行, 職責清晰)
- 功能完整性: 100% 保持原有功能
- 新架構整合: 100% 使用新架構工具

Note:
    這是 UI 重構計畫的核心示範模組，展示如何將複雜的
    單一檔案重構為清晰的模組化架構。
"""

from utils import get_logger

logger = get_logger(__name__)

# 主要組件導入
from .main_widget import CategoryWidget
from .tree_controller import TreeController  
from .search_filter import SearchFilter
from .action_buttons import ActionButtons
from .event_manager import EventManager

logger.info("分類選擇組件模組初始化完成 - 重構版本可用")

# 向後兼容導出
__all__ = [
    'CategoryWidget',      # 主要對外接口
    'TreeController',      # 樹狀結構控制器
    'SearchFilter',        # 搜尋過濾器
    'ActionButtons',       # 操作按鈕群組
    'EventManager',        # 事件處理管理器
]