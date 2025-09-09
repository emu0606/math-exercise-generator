#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - UI 應用層組件模組

本模組提供具體應用場景的複合組件，基於基礎組件構建，
實現完整的業務功能和用戶交互體驗。

組件分類：
- category/: 分類選擇相關組件 (重構自 category_widget.py 怪物檔案)
- settings/: 設定面板相關組件
- main/: 主視窗相關組件
- preview/: 預覽相關組件 (未來擴展)

架構特點：
- 模組化設計: 每個業務功能獨立成模組，避免單一檔案過大
- 組合模式: 使用基礎組件組合成複雜功能
- 事件驅動: 組件間通過統一事件系統通信
- 可配置性: 所有行為都可通過配置控制

Example:
    >>> from ui.widgets.category import CategoryWidget
    >>> from ui.widgets.settings import SettingsWidget
    >>> 
    >>> # 使用重構後的分類選擇器
    >>> category_widget = CategoryWidget()
    >>> 
    >>> # 使用模組化的設定面板
    >>> settings_widget = SettingsWidget()

Note:
    所有應用層組件都基於 ui.components 中的基礎組件構建，
    遵循統一的架構標準和最佳實踐。
"""

from utils import get_logger

logger = get_logger(__name__)

logger.info("UI應用層組件模組初始化完成")

# 應用層組件將逐步從重構中添加
__all__ = []