#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 三角形特殊點計算模組
提供質心、內心、外心、垂心等特殊點的計算功能
"""

import math
from typing import Dict, Union, Tuple
from .types import Point, Triangle
from .exceptions import TriangleDefinitionError, ValidationError, GeometryError
from .basic_ops import distance
from .math_backend import get_math_backend


class TriangleCenterCalculator:
    """三角形特殊點計算器
    
    提供各種三角形特殊點的精確計算，支援多種數學後端。
    """
    
    def __init__(self, backend: str = "numpy"):
        """初始化計算器
        
        Args:
            backend: 數學後端選擇 ("numpy", "sympy", "python")
        """
        self.backend = get_math_backend(backend)
    
    def get_centroid(self, triangle: Triangle) -> Point:
        """計算三角形的質心 (重心)
        
        質心是三條中線的交點，也是三個頂點的算術平均點。
        
        Args:
            triangle: 三角形對象
            
        Returns:
            質心座標
            
        Raises:
            ValidationError: 三角形無效
        """
        self._validate_triangle(triangle)
        
        # 質心公式: G = (p1 + p2 + p3) / 3
        centroid_x = (triangle.p1.x + triangle.p2.x + triangle.p3.x) / 3.0
        centroid_y = (triangle.p1.y + triangle.p2.y + triangle.p3.y) / 3.0
        
        return Point(centroid_x, centroid_y)
    
    def get_incenter(self, triangle: Triangle) -> Point:
        """計算三角形的內心 (三個內角平分線的交點)
        
        內心是內切圓的圓心，到三邊的距離相等。
        
        Args:
            triangle: 三角形對象
            
        Returns:
            內心座標
            
        Raises:
            TriangleDefinitionError: 三角形退化無法計算內心
        """
        self._validate_triangle(triangle)
        
        # 計算三邊長度
        a = distance(triangle.p2, triangle.p3)  # p1的對邊
        b = distance(triangle.p1, triangle.p3)  # p2的對邊  
        c = distance(triangle.p1, triangle.p2)  # p3的對邊
        
        perimeter = a + b + c
        if perimeter < 1e-9:
            raise TriangleDefinitionError("頂點幾乎重合，無法計算內心")
        
        # 檢查三角形不等式
        epsilon = 1e-9
        if not (a + b > c + epsilon and a + c > b + epsilon and b + c > a + epsilon):
            raise TriangleDefinitionError("三點共線或無法構成非退化三角形，無法計算內心")
        
        # 內心公式: I = (a*p1 + b*p2 + c*p3) / (a + b + c)
        incenter_x = (a * triangle.p1.x + b * triangle.p2.x + c * triangle.p3.x) / perimeter
        incenter_y = (a * triangle.p1.y + b * triangle.p2.y + c * triangle.p3.y) / perimeter
        
        return Point(incenter_x, incenter_y)
    
    def get_circumcenter(self, triangle: Triangle) -> Point:
        """計算三角形的外心 (三邊垂直平分線的交點)
        
        外心是外接圓的圓心，到三個頂點的距離相等。
        
        Args:
            triangle: 三角形對象
            
        Returns:
            外心座標
            
        Raises:
            TriangleDefinitionError: 三點共線，外心無定義
        """
        self._validate_triangle(triangle)
        
        x1, y1 = triangle.p1.x, triangle.p1.y
        x2, y2 = triangle.p2.x, triangle.p2.y
        x3, y3 = triangle.p3.x, triangle.p3.y
        
        # D = 2 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
        # 如果 D == 0, 三點共線
        D_val = 2 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
        
        if abs(D_val) < 1e-9:
            raise TriangleDefinitionError("三點共線，無法計算外心")
        
        p1_sq = x1**2 + y1**2
        p2_sq = x2**2 + y2**2
        p3_sq = x3**2 + y3**2
        
        circumcenter_x = (p1_sq * (y2 - y3) + p2_sq * (y3 - y1) + p3_sq * (y1 - y2)) / D_val
        circumcenter_y = (p1_sq * (x3 - x2) + p2_sq * (x1 - x3) + p3_sq * (x2 - x1)) / D_val
        
        return Point(circumcenter_x, circumcenter_y)
    
    def get_orthocenter(self, triangle: Triangle) -> Point:
        """計算三角形的垂心 (三條高的交點)
        
        垂心是三條高線的交點。對於直角三角形，垂心是直角頂點。
        
        Args:
            triangle: 三角形對象
            
        Returns:
            垂心座標
            
        Raises:
            TriangleDefinitionError: 三點共線，垂心無定義
        """
        self._validate_triangle(triangle)
        
        x1, y1 = triangle.p1.x, triangle.p1.y
        x2, y2 = triangle.p2.x, triangle.p2.y
        x3, y3 = triangle.p3.x, triangle.p3.y
        
        # 檢查共線性
        D_val = 2 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
        if abs(D_val) < 1e-9:
            raise TriangleDefinitionError("三點共線，無法計算垂心")
        
        # 特殊情況：直角三角形，垂心是直角頂點
        # 檢查 p1 是否為直角頂點
        dot_p1 = (x2 - x1) * (x3 - x1) + (y2 - y1) * (y3 - y1)
        if abs(dot_p1) < 1e-9:
            return triangle.p1
        
        # 檢查 p2 是否為直角頂點
        dot_p2 = (x1 - x2) * (x3 - x2) + (y1 - y2) * (y3 - y2)
        if abs(dot_p2) < 1e-9:
            return triangle.p2
        
        # 檢查 p3 是否為直角頂點
        dot_p3 = (x1 - x3) * (x2 - x3) + (y1 - y3) * (y2 - y3)
        if abs(dot_p3) < 1e-9:
            return triangle.p3
        
        # 通用情況：解兩條高線的方程
        # 高線 h1: 從 A 到邊 BC
        # 高線 h2: 從 B 到邊 AC
        
        # 處理邊 BC 平行於 x 軸
        if abs(y2 - y3) < 1e-9:  # 邊 BC 水平，高線 h1 垂直
            ortho_x = x1
            if abs(x1 - x3) < 1e-9:  # 邊 AC 垂直，高線 h2 水平
                ortho_y = y2
            else:  # 邊 AC 是斜線
                m_h2 = -(x1 - x3) / (y1 - y3)
                ortho_y = m_h2 * (ortho_x - x2) + y2
            return Point(ortho_x, ortho_y)
        
        # 處理邊 AC 平行於 x 軸
        if abs(y1 - y3) < 1e-9:  # 邊 AC 水平，高線 h2 垂直
            ortho_x = x2
            if abs(x2 - x3) < 1e-9:  # 邊 BC 垂直，高線 h1 水平
                ortho_y = y1
            else:  # 邊 BC 是斜線
                m_h1 = -(x2 - x3) / (y2 - y3)
                ortho_y = m_h1 * (ortho_x - x1) + y1
            return Point(ortho_x, ortho_y)
        
        # 一般情況：兩條邊都不是水平的
        # 處理邊 BC 垂直於 x 軸
        if abs(x2 - x3) < 1e-9:  # 邊 BC 垂直
            m_h1 = 0.0  # 高線 h1 水平
            # 處理邊 AC 垂直於 x 軸
            if abs(x1 - x3) < 1e-9:  # 邊 AC 垂直
                raise TriangleDefinitionError("計算垂心時出現異常情況 (兩邊垂直)")
            
            m_h2 = -(x1 - x3) / (y1 - y3)
            ortho_y = y1
            ortho_x = (ortho_y - y2 + m_h2 * x2) / m_h2
            return Point(ortho_x, ortho_y)
        
        # 處理邊 AC 垂直於 x 軸
        if abs(x1 - x3) < 1e-9:  # 邊 AC 垂直
            m_h2 = 0.0  # 高線 h2 水平
            m_h1 = -(x2 - x3) / (y2 - y3)
            ortho_y = y2
            ortho_x = (ortho_y - y1 + m_h1 * x1) / m_h1
            return Point(ortho_x, ortho_y)
        
        # 最一般情況：兩條邊都是斜線
        m_h1 = -(x2 - x3) / (y2 - y3)  # 高線 h1 的斜率
        m_h2 = -(x1 - x3) / (y1 - y3)  # 高線 h2 的斜率
        
        # 高線方程:
        # h1: y - y1 = m_h1 * (x - x1)  =>  y = m_h1*x + (y1 - m_h1*x1)
        # h2: y - y2 = m_h2 * (x - x2)  =>  y = m_h2*x + (y2 - m_h2*x2)
        
        c_h1 = y1 - m_h1 * x1
        c_h2 = y2 - m_h2 * x2
        
        # 解交點: m_h1*x + c_h1 = m_h2*x + c_h2
        if abs(m_h1 - m_h2) < 1e-9:
            raise TriangleDefinitionError("高線平行，無法計算垂心")
        
        ortho_x = (c_h2 - c_h1) / (m_h1 - m_h2)
        ortho_y = m_h1 * ortho_x + c_h1
        
        return Point(ortho_x, ortho_y)
    
    def get_all_centers(self, triangle: Triangle) -> Dict[str, Point]:
        """計算三角形的所有特殊點
        
        Args:
            triangle: 三角形對象
            
        Returns:
            包含所有特殊點的字典
            
        Example:
            centers = calculator.get_all_centers(triangle)
            centroid = centers['centroid']
            incenter = centers['incenter']
        """
        try:
            return {
                'centroid': self.get_centroid(triangle),
                'incenter': self.get_incenter(triangle),
                'circumcenter': self.get_circumcenter(triangle),
                'orthocenter': self.get_orthocenter(triangle)
            }
        except (TriangleDefinitionError, ValidationError) as e:
            raise GeometryError(f"無法計算特殊點: {e}")
    
    def _validate_triangle(self, triangle: Triangle) -> None:
        """驗證三角形的有效性"""
        if not isinstance(triangle, Triangle):
            raise ValidationError("輸入必須是 Triangle 對象")


# 便利函數 - 提供簡潔的函數式接口
def get_centroid(triangle: Triangle, backend: str = "numpy") -> Point:
    """計算三角形質心"""
    calculator = TriangleCenterCalculator(backend)
    return calculator.get_centroid(triangle)


def get_incenter(triangle: Triangle, backend: str = "numpy") -> Point:
    """計算三角形內心"""
    calculator = TriangleCenterCalculator(backend)
    return calculator.get_incenter(triangle)


def get_circumcenter(triangle: Triangle, backend: str = "numpy") -> Point:
    """計算三角形外心"""
    calculator = TriangleCenterCalculator(backend)
    return calculator.get_circumcenter(triangle)


def get_orthocenter(triangle: Triangle, backend: str = "numpy") -> Point:
    """計算三角形垂心"""
    calculator = TriangleCenterCalculator(backend)
    return calculator.get_orthocenter(triangle)


def get_all_centers(triangle: Triangle, backend: str = "numpy") -> Dict[str, Point]:
    """計算三角形的所有特殊點"""
    calculator = TriangleCenterCalculator(backend)
    return calculator.get_all_centers(triangle)


# 向後相容函數 - 支援舊的 (x,y) 元組格式
def get_centroid_legacy(p1: Tuple[float, float], p2: Tuple[float, float], 
                       p3: Tuple[float, float]) -> Tuple[float, float]:
    """向後相容的質心計算函數"""
    triangle = Triangle(Point(*p1), Point(*p2), Point(*p3))
    result = get_centroid(triangle)
    return (result.x, result.y)


def get_incenter_legacy(p1: Tuple[float, float], p2: Tuple[float, float], 
                       p3: Tuple[float, float]) -> Tuple[float, float]:
    """向後相容的內心計算函數"""
    triangle = Triangle(Point(*p1), Point(*p2), Point(*p3))
    result = get_incenter(triangle)
    return (result.x, result.y)


def get_circumcenter_legacy(p1: Tuple[float, float], p2: Tuple[float, float], 
                           p3: Tuple[float, float]) -> Tuple[float, float]:
    """向後相容的外心計算函數"""
    triangle = Triangle(Point(*p1), Point(*p2), Point(*p3))
    result = get_circumcenter(triangle)
    return (result.x, result.y)


def get_orthocenter_legacy(p1: Tuple[float, float], p2: Tuple[float, float], 
                          p3: Tuple[float, float]) -> Tuple[float, float]:
    """向後相容的垂心計算函數"""
    triangle = Triangle(Point(*p1), Point(*p2), Point(*p3))
    result = get_orthocenter(triangle)
    return (result.x, result.y)