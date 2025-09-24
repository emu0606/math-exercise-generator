#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""UI工具模組

提供動態配置UI生成和管理功能，支援自動化的配置界面創建。

主要模組：
- config_factory: 配置UI工廠，自動生成配置控件
"""

from .config_factory import ConfigUIFactory, ConfigValueCollector

__all__ = ['ConfigUIFactory', 'ConfigValueCollector']