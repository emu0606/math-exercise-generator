#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 圖形生成器包
"""

from typing import Dict, Type, Any, Optional
import functools
import inspect
from .base import FigureGenerator

# 圖形生成器註冊表
_figure_generators: Dict[str, Type[FigureGenerator]] = {}

def register_figure_generator(cls=None, *, name: Optional[str] = None):
    """註冊圖形生成器裝飾器
    
    可以直接使用 @register_figure_generator 或指定名稱 @register_figure_generator(name='custom_name')
    
    Args:
        cls: 被裝飾的類
        name: 可選的自定義名稱，如果未提供則使用 cls.get_name()
    """
    def decorator(cls):
        # 獲取圖形類型名稱
        figure_name = name if name is not None else cls.get_name()
        
        # 檢查是否已註冊
        if figure_name in _figure_generators:
            raise ValueError(f"圖形生成器 '{figure_name}' 已經被註冊")
        
        # 檢查是否是 FigureGenerator 的子類
        if not issubclass(cls, FigureGenerator):
            raise TypeError(f"類 '{cls.__name__}' 必須繼承 FigureGenerator")
        
        # 註冊生成器
        _figure_generators[figure_name] = cls
        print(f"已註冊圖形生成器: {cls.__name__} (類型: '{figure_name}')")
        
        return cls
    
    # 處理直接使用 @register_figure_generator 的情況
    if cls is not None:
        return decorator(cls)
    
    # 處理使用 @register_figure_generator(name='custom_name') 的情況
    return decorator

def get_figure_generator(figure_type: str) -> Type[FigureGenerator]:
    """獲取指定類型的圖形生成器類
    
    Args:
        figure_type: 圖形類型名稱
        
    Returns:
        圖形生成器類
        
    Raises:
        ValueError: 如果找不到指定類型的圖形生成器
    """
    if figure_type not in _figure_generators:
        raise ValueError(f"找不到類型為 '{figure_type}' 的圖形生成器")
    
    return _figure_generators[figure_type]

def get_registered_figure_types() -> Dict[str, Type[FigureGenerator]]:
    """獲取所有已註冊的圖形類型
    
    Returns:
        圖形類型名稱到生成器類的映射
    """
    return _figure_generators.copy()

# 導入所有具體生成器模組，這將自動註冊它們
# 注意：這些導入語句應該放在文件的最後，以避免循環導入問題

# 基礎圖形生成器
from .unit_circle import UnitCircleGenerator
from .circle import CircleGenerator
from .coordinate_system import CoordinateSystemGenerator
from .point import PointGenerator
from .line import LineGenerator
from .angle import AngleGenerator
from .label import LabelGenerator
# from .triangle import TriangleGenerator # 舊的或待重構的
from .basic_triangle import BasicTriangleGenerator # 新增的基礎三角形
from .arc import ArcGenerator # 新增的圓弧生成器

# 複合圖形生成器
from .composite import CompositeFigureGenerator

# 預定義複合圖形生成器
from .predefined.standard_unit_circle import StandardUnitCircleGenerator
from .predefined.predefined_triangle import PredefinedTriangleGenerator