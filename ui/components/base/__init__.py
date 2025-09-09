#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - UI 基礎組件類別

本模組定義所有 UI 組件的基礎類別和接口，建立統一的
組件開發標準和最佳實踐範例。

主要類別：
- BaseWidget: 所有UI組件的抽象基類
- ConfigurableWidget: 可配置組件的基類  
- EventAwareWidget: 事件感知組件的基類

Example:
    >>> from ui.components.base import BaseWidget
    >>> 
    >>> class MyWidget(BaseWidget):
    ...     def _setup_ui(self):
    ...         # 實現UI建置邏輯
    ...         pass
    ...         
    ...     def _connect_signals(self):
    ...         # 實現信號連接邏輯  
    ...         pass
"""

from .base_widget import BaseWidget
from .configurable import ConfigurableWidget

__all__ = [
    'BaseWidget',
    'ConfigurableWidget'
]