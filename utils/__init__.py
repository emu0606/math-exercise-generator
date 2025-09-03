#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - Utils 統一模組入口

提供完整的數學測驗生成功能，符合三個關鍵原則：
1. 完成當前架構：補完缺失的核心功能
2. 徹底移除舊API：刪除所有向後相容層  
3. 設計統一入口：建立清晰的utils/__init__.py

快速開始：
    # 三角形功能
    from utils import construct_triangle, get_centroid, get_incenter
    
    # 完整工作流
    triangle = construct_triangle("sss", side_a=3, side_b=4, side_c=5)
    centroid = get_centroid(triangle)
"""

# 核心幾何功能
from .geometry import (
    # 三角形構造
    construct_triangle,
    construct_triangle_sss,
    construct_triangle_sas,
    construct_triangle_asa,
    construct_triangle_aas,
    construct_triangle_coordinates,
    
    # 三角形特殊點
    get_centroid as get_triangle_centroid,
    get_incenter,
    get_circumcenter, 
    get_orthocenter,
    get_all_centers,
    
    # 基礎幾何運算
    distance,
    midpoint,
    centroid,
    area_of_triangle,
    angle_between_vectors,
    angle_at_vertex,
    rotate_point,
    reflect_point,
    
    # 數據類型
    Point,
    Triangle,
    Circle,
    Vector,
    Line,
    
    # 異常類
    GeometryError,
    TriangleDefinitionError,
    TriangleConstructionError,
    ValidationError
)

# TikZ 基礎功能
from .tikz import (
    tikz_coordinate,
    tikz_angle_degrees,
    ArcRenderer,
    LabelPositioner
)

# 核心功能
from .core import (
    global_config,
    registry,
    get_logger
)

# 版本資訊
__version__ = "2.0.0"
__author__ = "Math Exercise Generator Team"

# 統一導入別名 - 正確指向三角形質心函數
get_centroid = get_triangle_centroid

# 統一工作流便利函數
def create_simple_triangle_figure(mode: str, **triangle_params):
    """簡化的三角形圖形創建接口
    
    Args:
        mode: 三角形構造模式 ("sss", "sas", "asa", "aas", "coordinates")
        **triangle_params: 三角形構造參數
        
    Returns:
        包含三角形和特殊點的字典
    """
    # 構造三角形
    triangle = construct_triangle(mode, **triangle_params)
    
    # 計算特殊點
    centers = get_all_centers(triangle)
    
    # 生成基礎 TikZ 代碼
    tikz_lines = []
    tikz_lines.append(f"\\draw {tikz_coordinate(triangle.A)} -- {tikz_coordinate(triangle.B)} -- {tikz_coordinate(triangle.C)} -- cycle;")
    tikz_lines.append(f"\\node[below left] at {tikz_coordinate(triangle.A)} {{A}};")
    tikz_lines.append(f"\\node[below right] at {tikz_coordinate(triangle.B)} {{B}};")
    tikz_lines.append(f"\\node[above] at {tikz_coordinate(triangle.C)} {{C}};")
    
    return {
        'triangle': triangle,
        'centers': centers,
        'tikz_code': "\\n".join(tikz_lines)
    }

# 公開統一API
__all__ = [
    # === 核心幾何功能 ===
    # 三角形構造
    'construct_triangle',
    'construct_triangle_sss',
    'construct_triangle_sas', 
    'construct_triangle_asa',
    'construct_triangle_aas',
    'construct_triangle_coordinates',
    
    # 三角形特殊點
    'get_triangle_centroid',
    'get_centroid',  # 別名
    'get_incenter',
    'get_circumcenter',
    'get_orthocenter', 
    'get_all_centers',
    
    # 基礎幾何運算
    'distance',
    'midpoint',
    'centroid',
    'area_of_triangle',
    'angle_between_vectors',
    'angle_at_vertex',
    'rotate_point',
    'reflect_point',
    
    # === 基礎渲染 ===
    'tikz_coordinate',
    'tikz_angle_degrees',
    'ArcRenderer',
    'LabelPositioner',
    
    # === 數據類型 ===
    'Point',
    'Triangle',
    'Circle',
    'Vector',
    'Line',
    
    # === 異常類 ===
    'GeometryError',
    'TriangleDefinitionError',
    'TriangleConstructionError',
    'ValidationError',
    
    # === 核心功能 ===
    'global_config',
    'registry',
    'get_logger',
    
    # === 統一工作流 ===
    'create_simple_triangle_figure'
]