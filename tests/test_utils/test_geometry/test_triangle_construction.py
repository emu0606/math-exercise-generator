#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
三角形構造模組單元測試
測試 utils.geometry.triangle_construction 模組的三角形構造功能
"""

import pytest
import math
from utils.geometry import (
    construct_triangle, construct_triangle_sss, construct_triangle_sas,
    construct_triangle_asa, construct_triangle_aas, construct_triangle_coordinates,
    TriangleConstructor, Point, Triangle,
    TriangleConstructionError, ValidationError
)


class TestTriangleConstructor:
    """三角形構造器測試"""
    
    def setup_method(self):
        """測試設置"""
        self.constructor = TriangleConstructor()
    
    def test_sss_construction(self):
        """測試SSS構造（三邊長）"""
        # 3-4-5 直角三角形
        triangle = self.constructor.construct_sss(3, 4, 5)
        
        # 驗證頂點
        assert triangle.p1.x == 0.0
        assert triangle.p1.y == 0.0
        assert triangle.p2.x == 5.0
        assert triangle.p2.y == 0.0
        
        # 驗證邊長 (a=|p2p3|, b=|p1p3|, c=|p1p2|)
        side_lengths = triangle.side_lengths()
        assert abs(side_lengths[0] - 3.0) < 1e-10  # a = p2-p3 = 3
        assert abs(side_lengths[1] - 4.0) < 1e-10  # b = p1-p3 = 4
        assert abs(side_lengths[2] - 5.0) < 1e-10  # c = p1-p2 = 5
    
    def test_sss_invalid_triangle(self):
        """測試SSS構造無效三角形"""
        # 不滿足三角形不等式
        with pytest.raises(TriangleConstructionError):
            self.constructor.construct_sss(1, 2, 5)
        
        # 負邊長
        with pytest.raises(ValidationError):
            self.constructor.construct_sss(-1, 2, 3)
        
        # 零邊長
        with pytest.raises(ValidationError):
            self.constructor.construct_sss(0, 2, 3)
    
    def test_sas_construction(self):
        """測試SAS構造（兩邊夾角）"""
        # 直角三角形：邊長3和4，夾角90度
        triangle = self.constructor.construct_sas(3, math.pi/2, 4)
        
        # 驗證基本結構
        assert triangle.p1.x == 0.0
        assert triangle.p1.y == 0.0
        assert triangle.p2.x == 3.0
        assert triangle.p2.y == 0.0
        
        # 第三個頂點應該在(0, 4)
        assert abs(triangle.p3.x) < 1e-10
        assert abs(triangle.p3.y - 4.0) < 1e-10
    
    def test_sas_invalid_angle(self):
        """測試SAS構造無效角度"""
        # 角度為0
        with pytest.raises(ValidationError):
            self.constructor.construct_sas(3, 0, 4)
        
        # 角度為π
        with pytest.raises(ValidationError):
            self.constructor.construct_sas(3, math.pi, 4)
        
        # 角度超過π
        with pytest.raises(ValidationError):
            self.constructor.construct_sas(3, math.pi + 0.1, 4)
    
    def test_asa_construction(self):
        """測試ASA構造（角邊角）"""
        # 45-45-90三角形
        triangle = self.constructor.construct_asa(
            math.pi/4, 2*math.sqrt(2), math.pi/4
        )
        
        # 驗證是等腰直角三角形
        side_lengths = triangle.side_lengths()
        # 兩條直角邊應該相等
        assert abs(side_lengths[1] - side_lengths[2]) < 1e-10
    
    def test_asa_invalid_angles(self):
        """測試ASA構造無效角度"""
        # 角度和超過π
        with pytest.raises(TriangleConstructionError):
            self.constructor.construct_asa(math.pi/2, 5, math.pi/2 + 0.1)
        
        # 負角度
        with pytest.raises(ValidationError):
            self.constructor.construct_asa(-0.1, 5, math.pi/4)
    
    def test_aas_construction(self):
        """測試AAS構造（角角邊）"""
        # 30-60-90三角形
        triangle = self.constructor.construct_aas(
            math.pi/6, math.pi/3, 1.0  # 30度角對邊長為1
        )
        
        # 驗證構造成功且生成有效三角形
        assert triangle is not None
        side_lengths = triangle.side_lengths()
        assert len(side_lengths) == 3
        assert all(length > 0 for length in side_lengths)
        
        # 驗證角度約束（第三個角應該是90度）
        assert abs(sum([math.pi/6, math.pi/3, math.pi/2]) - math.pi) < 1e-10
    
    def test_coordinates_construction(self):
        """測試坐標構造"""
        p1 = Point(0, 0)
        p2 = Point(3, 0)
        p3 = Point(0, 4)
        
        triangle = self.constructor.construct_coordinates(p1, p2, p3)
        
        assert triangle.p1 == p1
        assert triangle.p2 == p2
        assert triangle.p3 == p3
    
    def test_coordinates_invalid_points(self):
        """測試坐標構造無效點"""
        # 重複點
        p1 = Point(0, 0)
        p2 = Point(0, 0)
        p3 = Point(1, 1)
        
        with pytest.raises(TriangleConstructionError):
            self.constructor.construct_coordinates(p1, p2, p3)
        
        # 共線點
        p4 = Point(0, 0)
        p5 = Point(1, 0)
        p6 = Point(2, 0)
        
        with pytest.raises(TriangleConstructionError):
            self.constructor.construct_coordinates(p4, p5, p6)


class TestUnifiedInterface:
    """統一接口測試"""
    
    def test_construct_triangle_sss(self):
        """測試統一接口SSS模式"""
        triangle = construct_triangle("sss", side_a=3, side_b=4, side_c=5)
        
        # 驗證是3-4-5直角三角形
        side_lengths = triangle.side_lengths()
        sorted_lengths = sorted(side_lengths)
        assert abs(sorted_lengths[0] - 3.0) < 1e-10
        assert abs(sorted_lengths[1] - 4.0) < 1e-10
        assert abs(sorted_lengths[2] - 5.0) < 1e-10
    
    def test_construct_triangle_sas(self):
        """測試統一接口SAS模式"""
        triangle = construct_triangle("sas", side1=3, angle_rad=math.pi/2, side2=4)
        
        # 驗證直角三角形
        # 斜邊長度應該是5
        side_lengths = triangle.side_lengths()
        max_side = max(side_lengths)
        assert abs(max_side - 5.0) < 1e-10
    
    def test_construct_triangle_coordinates(self):
        """測試統一接口坐標模式"""
        triangle = construct_triangle(
            "coordinates", 
            p1=(0, 0), p2=(3, 0), p3=(0, 4)
        )
        
        assert triangle.p1.x == 0.0
        assert triangle.p1.y == 0.0
        assert triangle.p2.x == 3.0
        assert triangle.p2.y == 0.0
        assert triangle.p3.x == 0.0
        assert triangle.p3.y == 4.0
    
    def test_construct_triangle_invalid_mode(self):
        """測試無效構造模式"""
        with pytest.raises(ValueError):
            construct_triangle("invalid_mode", side_a=3, side_b=4, side_c=5)
    
    def test_construct_triangle_missing_params(self):
        """測試缺少必要參數"""
        # SSS模式缺少參數
        with pytest.raises(ValueError):
            construct_triangle("sss", side_a=3, side_b=4)  # 缺少side_c


class TestConvenienceFunctions:
    """便利函數測試"""
    
    def test_individual_construction_functions(self):
        """測試各個便利構造函數"""
        # SSS
        triangle_sss = construct_triangle_sss(3, 4, 5)
        assert triangle_sss is not None
        
        # SAS
        triangle_sas = construct_triangle_sas(3, math.pi/2, 4)
        assert triangle_sas is not None
        
        # ASA
        triangle_asa = construct_triangle_asa(math.pi/4, 2*math.sqrt(2), math.pi/4)
        assert triangle_asa is not None
        
        # AAS
        triangle_aas = construct_triangle_aas(math.pi/6, math.pi/3, 1.0)
        assert triangle_aas is not None
        
        # Coordinates
        triangle_coords = construct_triangle_coordinates(
            Point(0, 0), Point(3, 0), Point(0, 4)
        )
        assert triangle_coords is not None
    
    def test_coordinates_with_tuples(self):
        """測試坐標函數接受元組"""
        triangle = construct_triangle_coordinates((0, 0), (3, 0), (0, 4))
        
        assert triangle.p1.x == 0.0
        assert triangle.p1.y == 0.0
        assert triangle.p2.x == 3.0
        assert triangle.p2.y == 0.0


class TestEdgeCases:
    """邊界情況測試"""
    
    def test_very_small_triangles(self):
        """測試小三角形"""
        triangle = construct_triangle_sss(1e-4, 1e-4, 1e-4)
        assert triangle is not None
        assert triangle.area() > 0
    
    def test_very_large_triangles(self):
        """測試極大三角形"""
        triangle = construct_triangle_sss(1e6, 1e6, 1e6)
        assert triangle is not None
        assert triangle.area() > 0
    
    def test_nearly_degenerate_triangles(self):
        """測試接近退化的三角形"""
        # 非常細長的三角形
        triangle = construct_triangle_sss(1000, 1000, 1)
        assert triangle is not None
        assert triangle.area() > 0
    
    def test_precision_edge_cases(self):
        """測試精度邊界情況"""
        # 邊長幾乎相等的三角形
        triangle = construct_triangle_sss(1.0, 1.0, 1.0000000001)
        assert triangle is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])