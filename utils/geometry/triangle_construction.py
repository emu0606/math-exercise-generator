#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 三角形構造模組
提供各種三角形構造方法：SSS, SAS, ASA, AAS, 坐標構造
"""

import math
from typing import Dict, List, Any, Optional, Tuple, Union
from .types import Point, Triangle
from .exceptions import TriangleConstructionError, ValidationError
from .basic_ops import distance, angle_between_vectors, normalize_angle
from .math_backend import get_math_backend

class TriangleConstructor:
    """三角形構造器
    
    提供多種三角形構造方法，支援不同的輸入參數組合。
    所有構造方法都會驗證輸入的有效性，確保能構造出有效的三角形。
    """
    
    def __init__(self, backend: str = "numpy"):
        """初始化三角形構造器
        
        Args:
            backend: 數學後端選擇 ("numpy", "sympy", "python")
        """
        self.backend = get_math_backend(backend)
    
    def construct_sss(self, side_a: float, side_b: float, side_c: float) -> Triangle:
        """使用三邊長構造三角形 (SSS)
        
        Args:
            side_a: 第一邊長
            side_b: 第二邊長  
            side_c: 第三邊長
            
        Returns:
            構造的三角形對象
            
        Raises:
            TriangleConstructionError: 邊長不滿足三角形不等式
            ValidationError: 輸入參數無效
        """
        # 輸入驗證
        if any(side <= 0 for side in [side_a, side_b, side_c]):
            invalid_sides = [s for s in [side_a, side_b, side_c] if s <= 0]
            raise ValidationError("side_lengths", invalid_sides, "所有邊長必須為正數")
        
        # 三角形不等式檢查
        if not self._check_triangle_inequality(side_a, side_b, side_c):
            raise TriangleConstructionError(
                f"邊長 ({side_a}, {side_b}, {side_c}) 不滿足三角形不等式"
            )
        
        # 使用餘弦定理計算角度和坐標
        # 放置第一個頂點在原點，第二個頂點在 x 軸上
        A = Point(0.0, 0.0)
        B = Point(side_c, 0.0)
        
        # 使用餘弦定理計算角 A
        cos_A = (side_b**2 + side_c**2 - side_a**2) / (2 * side_b * side_c)
        cos_A = max(-1.0, min(1.0, cos_A))  # 防止數值誤差
        angle_A = math.acos(cos_A)
        
        # 計算第三個頂點的坐標
        C_x = side_b * math.cos(angle_A)
        C_y = side_b * math.sin(angle_A)
        C = Point(C_x, C_y)
        
        return Triangle(A, B, C)
    
    def construct_sas(self, side1: float, angle_rad: float, side2: float) -> Triangle:
        """使用兩邊夾角構造三角形 (SAS)
        
        Args:
            side1: 第一邊長
            angle_rad: 夾角（弧度）
            side2: 第二邊長
            
        Returns:
            構造的三角形對象
            
        Raises:
            TriangleConstructionError: 角度無效或邊長無效
            ValidationError: 輸入參數無效
        """
        # 輸入驗證
        if side1 <= 0 or side2 <= 0:
            invalid_sides = [s for s in [side1, side2] if s <= 0]
            raise ValidationError("side_lengths", invalid_sides, "邊長必須為正數")
        
        if angle_rad <= 0 or angle_rad >= math.pi:
            raise ValidationError("angle_rad", angle_rad, "角度必須在 0 到 π 之間")
        
        # 構造三角形
        A = Point(0.0, 0.0)
        B = Point(side1, 0.0)
        
        # 根據夾角計算第三個頂點
        C_x = side2 * math.cos(angle_rad)
        C_y = side2 * math.sin(angle_rad)
        C = Point(C_x, C_y)
        
        return Triangle(A, B, C)
    
    def construct_asa(self, angle1_rad: float, side_length: float, angle2_rad: float) -> Triangle:
        """使用角邊角構造三角形 (ASA)
        
        Args:
            angle1_rad: 第一個角（弧度）
            side_length: 已知邊長
            angle2_rad: 第二個角（弧度）
            
        Returns:
            構造的三角形對象
            
        Raises:
            TriangleConstructionError: 角度和超過 π 或其他無效情況
            ValidationError: 輸入參數無效
        """
        # 輸入驗證
        if side_length <= 0:
            raise ValidationError("side_length", side_opposite_angle1, "邊長必須為正數")
        
        if angle1_rad <= 0 or angle1_rad >= math.pi:
            raise ValidationError("angle1_rad", angle1_rad, "第一個角度必須在 0 到 π 之間")
        
        if angle2_rad <= 0 or angle2_rad >= math.pi:
            raise ValidationError("angle2_rad", angle2_rad, "第二個角度必須在 0 到 π 之間")
        
        # 計算第三個角
        angle3_rad = math.pi - angle1_rad - angle2_rad
        if angle3_rad <= 0:
            raise TriangleConstructionError("角度和不能大於或等於 π")
        
        # 使用正弦定理計算其他邊長
        # sin(A)/a = sin(B)/b = sin(C)/c
        sin_ratio = side_length / math.sin(angle1_rad)
        side2 = sin_ratio * math.sin(angle2_rad)
        side3 = sin_ratio * math.sin(angle3_rad)
        
        # 使用 SAS 方法構造
        return self.construct_sas(side_length, angle2_rad, side2)
    
    def construct_aas(self, angle1_rad: float, angle2_rad: float, 
                     side_opposite_angle1: float) -> Triangle:
        """使用角角邊構造三角形 (AAS)
        
        Args:
            angle1_rad: 第一個角（弧度）
            angle2_rad: 第二個角（弧度）
            side_opposite_angle1: 第一個角的對邊長
            
        Returns:
            構造的三角形對象
            
        Raises:
            TriangleConstructionError: 角度和超過 π 或其他無效情況
            ValidationError: 輸入參數無效
        """
        # 輸入驗證
        if side_opposite_angle1 <= 0:
            raise ValidationError("side_length", side_opposite_angle1, "邊長必須為正數")
        
        if angle1_rad <= 0 or angle1_rad >= math.pi:
            raise ValidationError("angle1_rad", angle1_rad, "第一個角度必須在 0 到 π 之間")
        
        if angle2_rad <= 0 or angle2_rad >= math.pi:
            raise ValidationError("angle2_rad", angle2_rad, "第二個角度必須在 0 到 π 之間")
        
        # 計算第三個角
        angle3_rad = math.pi - angle1_rad - angle2_rad
        if angle3_rad <= 0:
            raise TriangleConstructionError("角度和不能大於或等於 π")
        
        # 使用正弦定理計算已知邊的鄰邊
        sin_ratio = side_opposite_angle1 / math.sin(angle1_rad)
        side_opposite_angle2 = sin_ratio * math.sin(angle2_rad)
        
        # 使用 ASA 方法構造（已知邊在第一個角和第三個角之間）
        return self.construct_asa(angle3_rad, side_opposite_angle1, angle1_rad)
    
    def construct_coordinates(self, p1: Point, p2: Point, p3: Point) -> Triangle:
        """使用三個頂點坐標構造三角形
        
        Args:
            p1, p2, p3: 三個頂點坐標
            
        Returns:
            構造的三角形對象
            
        Raises:
            TriangleConstructionError: 三點共線或重複
        """
        # 檢查三點是否重複
        if p1 == p2 or p2 == p3 or p1 == p3:
            raise TriangleConstructionError("三角形的頂點不能重複")
        
        # 檢查三點是否共線
        if self._are_collinear(p1, p2, p3):
            raise TriangleConstructionError("三點不能共線")
        
        return Triangle(p1, p2, p3)
    
    def _check_triangle_inequality(self, a: float, b: float, c: float) -> bool:
        """檢查三角形不等式"""
        return (a + b > c) and (b + c > a) and (a + c > b)
    
    def _are_collinear(self, p1: Point, p2: Point, p3: Point, tolerance: float = 1e-10) -> bool:
        """檢查三點是否共線"""
        # 使用叉積判斷，如果叉積為0則共線
        v1 = (p2.x - p1.x, p2.y - p1.y)
        v2 = (p3.x - p1.x, p3.y - p1.y)
        cross_product = v1[0] * v2[1] - v1[1] * v2[0]
        return abs(cross_product) < tolerance

# 統一的構造函數接口
def construct_triangle(mode: str, **kwargs) -> Triangle:
    """統一的三角形構造接口
    
    Args:
        mode: 構造模式 ("sss", "sas", "asa", "aas", "coordinates")
        **kwargs: 對應模式的參數
        
    Returns:
        構造的三角形對象
        
    Raises:
        ValueError: 未知的構造模式
        TriangleConstructionError: 構造失敗
        
    Examples:
        # SSS構造
        triangle = construct_triangle("sss", side_a=3, side_b=4, side_c=5)
        
        # SAS構造
        triangle = construct_triangle("sas", side1=3, angle_rad=math.pi/2, side2=4)
        
        # 坐標構造
        triangle = construct_triangle("coordinates", p1=(0,0), p2=(3,0), p3=(0,4))
    """
    constructor = TriangleConstructor()
    
    if mode == "sss":
        required_params = ["side_a", "side_b", "side_c"]
        if not all(param in kwargs for param in required_params):
            raise ValueError(f"SSS模式需要參數: {required_params}")
        return constructor.construct_sss(kwargs["side_a"], kwargs["side_b"], kwargs["side_c"])
    
    elif mode == "sas":
        required_params = ["side1", "angle_rad", "side2"]
        if not all(param in kwargs for param in required_params):
            raise ValueError(f"SAS模式需要參數: {required_params}")
        return constructor.construct_sas(kwargs["side1"], kwargs["angle_rad"], kwargs["side2"])
    
    elif mode == "asa":
        required_params = ["angle1_rad", "side_length", "angle2_rad"]
        if not all(param in kwargs for param in required_params):
            raise ValueError(f"ASA模式需要參數: {required_params}")
        return constructor.construct_asa(kwargs["angle1_rad"], kwargs["side_length"], kwargs["angle2_rad"])
    
    elif mode == "aas":
        required_params = ["angle1_rad", "angle2_rad", "side_opposite_angle1"]
        if not all(param in kwargs for param in required_params):
            raise ValueError(f"AAS模式需要參數: {required_params}")
        return constructor.construct_aas(kwargs["angle1_rad"], kwargs["angle2_rad"], kwargs["side_opposite_angle1"])
    
    elif mode == "coordinates":
        required_params = ["p1", "p2", "p3"]
        if not all(param in kwargs for param in required_params):
            raise ValueError(f"坐標模式需要參數: {required_params}")
        
        # 轉換為 Point 對象
        p1 = Point(*kwargs["p1"]) if not isinstance(kwargs["p1"], Point) else kwargs["p1"]
        p2 = Point(*kwargs["p2"]) if not isinstance(kwargs["p2"], Point) else kwargs["p2"]
        p3 = Point(*kwargs["p3"]) if not isinstance(kwargs["p3"], Point) else kwargs["p3"]
        
        return constructor.construct_coordinates(p1, p2, p3)
    
    else:
        raise ValueError(f"未知的構造模式: {mode}，支援的模式: sss, sas, asa, aas, coordinates")

# 便利函數（取代舊的 get_vertices）
def construct_triangle_sss(side_a: float, side_b: float, side_c: float) -> Triangle:
    """三邊構造三角形"""
    return construct_triangle("sss", side_a=side_a, side_b=side_b, side_c=side_c)

def construct_triangle_sas(side1: float, angle_rad: float, side2: float) -> Triangle:
    """兩邊夾角構造三角形"""
    return construct_triangle("sas", side1=side1, angle_rad=angle_rad, side2=side2)

def construct_triangle_asa(angle1_rad: float, side_length: float, angle2_rad: float) -> Triangle:
    """角邊角構造三角形"""
    return construct_triangle("asa", angle1_rad=angle1_rad, side_length=side_length, angle2_rad=angle2_rad)

def construct_triangle_aas(angle1_rad: float, angle2_rad: float, side_opposite_angle1: float) -> Triangle:
    """角角邊構造三角形"""
    return construct_triangle("aas", angle1_rad=angle1_rad, angle2_rad=angle2_rad, 
                             side_opposite_angle1=side_opposite_angle1)

def construct_triangle_coordinates(p1: Union[Point, Tuple[float, float]], 
                                  p2: Union[Point, Tuple[float, float]], 
                                  p3: Union[Point, Tuple[float, float]]) -> Triangle:
    """坐標構造三角形"""
    return construct_triangle("coordinates", p1=p1, p2=p2, p3=p3)