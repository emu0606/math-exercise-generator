#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 樣式模組

此模組統一導出所有樣式相關的配置類別和預設選項。
提供標籤樣式和顯示效果的完整配置體系。

主要模組：
1. **labels**: 標籤和文字樣式配置
2. **display**: 顯示效果和視覺樣式配置

使用方式：
    導入特定樣式配置::
    
        from figures.params.styles import LabelStyleConfig, ArcStyleConfig
        
    導入樣式預設::
    
        from figures.params.styles import TextStylePresets, StylePresets
        
    組合使用樣式配置::
    
        from figures.params.styles import (
            VertexDisplayConfig, 
            FillStyleConfig,
            ColorSchemeConfig
        )

Note:
    - 樣式配置獨立於具體圖形參數
    - 支援樣式的組合和重用
    - 提供豐富的預設選項
    - 與 TikZ 系統深度整合
"""

# 從 labels 模組導出標籤樣式相關類別
from .labels import (
    LabelStyleConfig,
    PointStyleConfig,
    VertexDisplayConfig,
    SideDisplayConfig,
    AngleLabelConfig,
    TextStylePresets
)

# 從 display 模組導出顯示效果相關類別
from .display import (
    ArcStyleConfig,
    FillStyleConfig,
    LineStyleConfig,
    DisplayControlConfig,
    ColorSchemeConfig,
    RenderingConfig,
    StylePresets
)

# 定義模組的公開接口
__all__ = [
    # 標籤樣式類別
    'LabelStyleConfig',
    'PointStyleConfig', 
    'VertexDisplayConfig',
    'SideDisplayConfig',
    'AngleLabelConfig',
    
    # 顯示效果類別
    'ArcStyleConfig',
    'FillStyleConfig',
    'LineStyleConfig',
    'DisplayControlConfig',
    'ColorSchemeConfig',
    'RenderingConfig',
    
    # 預設樣式集合
    'TextStylePresets',
    'StylePresets'
]

# 版本資訊
__version__ = '1.0.0'
__author__ = 'Math Exercise Generator Team'
__description__ = 'Style configuration models for mathematical figure generation'