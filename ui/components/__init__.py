#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - UI 基礎組件模組

本模組提供可復用的 UI 基礎組件，採用現代化架構設計，
整合日誌系統和配置管理，為應用層組件提供穩固的技術基礎。

組件分類：
- base/: 基礎組件類別和接口定義
- inputs/: 輸入組件 (搜尋框、下拉選單、數字選擇器)
- displays/: 顯示組件 (樹狀檢視、表格、進度條)
- controls/: 控制組件 (按鈕群組、工具列、狀態列)

設計原則：
- 單一職責原則: 每個組件只負責一個明確功能
- 配置驅動設計: 組件行為由配置控制，而非硬編碼
- 事件驅動架構: 使用統一的事件系統進行組件間通信
- 新架構整合: 充分利用 get_logger, global_config 等工具

Example:
    >>> from ui.components.base import BaseWidget
    >>> from ui.components.inputs import SearchBox
    >>> from ui.components.displays import TreeView
    >>> 
    >>> # 建立搜尋框組件
    >>> search = SearchBox(placeholder="搜尋題型...")
    >>> 
    >>> # 建立樹狀檢視組件
    >>> tree = TreeView(auto_expand=True)

Note:
    所有基礎組件都遵循新架構設計標準，包含完整的錯誤處理、
    日誌記錄和配置管理。每個組件都可獨立測試和復用。
"""

from utils import get_logger

logger = get_logger(__name__)

logger.info("UI基礎組件模組初始化完成")

# 組件類別將在後續實施中逐步添加
__all__ = []