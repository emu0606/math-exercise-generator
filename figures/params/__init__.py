#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 圖形參數模型統一接口

本模組提供所有圖形生成器所需的參數模型，採用模組化設計
以提高可維護性和可擴展性。重構自原本 562 行的單一文件，
現已模組化為清晰的職責分離結構，同時保持完整的向後兼容性。

模組結構：
- **types**: 基礎類型定義（TikzAnchor, TikzPlacement, PointTuple）
- **base**: 基礎參數類別（BaseFigureParams, 定位系統）
- **geometry**: 基礎幾何圖形參數（點、線、圓、三角形、弧）
- **shapes**: 標準形狀參數（單位圓、座標系統、標籤）
- **composite**: 複合圖形參數（子圖形組合、相對定位）
- **styles**: 樣式和顯示配置（標籤樣式、顯示效果）

使用方式：
    基礎幾何圖形::
    
        from figures.params import PointParams, CircleParams, TriangleParams
        
        point = PointParams(x=1, y=2, label='A', variant="question")
        circle = CircleParams(center=[0, 0], radius=2.0, color='blue')
        
    複合圖形系統::
    
        from figures.params import CompositeParams, SubFigureParams
        from figures.params import AbsolutePosition, RelativePosition
        
        composite = CompositeParams(
            sub_figures=[...],  # 子圖形列表
            variant='explanation'
        )
        
    樣式配置::
    
        from figures.params.styles import LabelStyleConfig, ColorSchemeConfig
        
        label_style = LabelStyleConfig(color='blue', font_size=r'\\large')

統一架構：
    所有生成器使用統一的新架構::

        # 統一導入方式
        from figures.params import UnitCircleParams, CircleParams, CoordinateSystemParams

        # 舊架構已移除（2025-09-16）
        # from figures.params_models import UnitCircleParams  # 已不可用

Note:
    - Day 2 重構完成：基礎架構、幾何參數、樣式系統已就緒
    - 完整的 Sphinx docstring 文檔覆蓋
    - 所有參數模型支援 variant='question'/'explanation' 雙模式
    - 新增強大的複合圖形和樣式配置系統
"""

# 從各個模組導出核心參數類別
from .types import TikzAnchor, TikzPlacement, PointTuple
from .base import BaseFigureParams, AbsolutePosition, RelativePosition

# 基礎幾何圖形參數
from .geometry import (
    PointParams,
    LineParams, 
    AngleParams,
    TriangleParams,
    CircleParams,
    UnitCircleParams,
    ArcParams
)

# 標準形狀參數
from .shapes import (
    StandardUnitCircleParams,
    CoordinateSystemParams,
    LabelParams,
    GridParams
)

# 複合圖形參數
from .composite import (
    SubFigureParams,
    CompositeParams,
    LayoutParams,
    GroupParams
)

# 三角形模組 (新增)
from .triangle import (
    BasicTriangleParams,
    TriangleParams as DetailedTriangleParams,  # 避免與 geometry 的 TriangleParams 衝突
    PredefinedTriangleParams,
    LabelStyleConfig,
    PointStyleConfig,
    VertexDisplayConfig,
    SideDisplayConfig,
    ArcStyleConfig,
    AngleDisplayConfig,
    SpecialPointDisplayConfig
)

# 樣式配置（可選導入）
from .styles import (
    FillStyleConfig,
    ColorSchemeConfig
)

# 定義模組的公開接口
__all__ = [
    # 基礎類型
    'TikzAnchor',
    'TikzPlacement', 
    'PointTuple',
    
    # 基礎參數類別
    'BaseFigureParams',
    'AbsolutePosition',
    'RelativePosition',
    
    # 基礎幾何參數
    'PointParams',
    'LineParams',
    'AngleParams', 
    'TriangleParams',
    'CircleParams',
    'UnitCircleParams',
    'ArcParams',
    
    # 標準形狀參數
    'StandardUnitCircleParams',
    'CoordinateSystemParams',
    'LabelParams',
    'GridParams',
    
    # 複合圖形參數
    'SubFigureParams',
    'CompositeParams',
    'LayoutParams',
    'GroupParams',
    
    # 三角形模組 (Day 3 新增)
    'BasicTriangleParams',
    'DetailedTriangleParams',
    'PredefinedTriangleParams',
    'PointStyleConfig',
    'SideDisplayConfig',
    'AngleDisplayConfig',
    'SpecialPointDisplayConfig',
    
    # 樣式配置
    'LabelStyleConfig',
    'VertexDisplayConfig',
    'ArcStyleConfig',
    'FillStyleConfig',
    'ColorSchemeConfig'
]

# 版本資訊
__version__ = '2.0.0'  # 重構版本
__author__ = 'Math Exercise Generator Team'
__description__ = 'Modular parameter models for mathematical figure generation'

# 重構完成狀態
__refactoring_status__ = 'Day 3 Complete'
__modules_ready__ = [
    'types', 'base', 'geometry', 'shapes', 
    'composite', 'styles.labels', 'styles.display',
    'triangle.basic', 'triangle.advanced'  # Day 3 新增
]