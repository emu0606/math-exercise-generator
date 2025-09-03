#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
三角形特殊點計算單元測試
測試 utils.geometry.triangle_centers 模組的特殊點計算功能
"""

import pytest
import math
from utils.geometry import (
    get_centroid, get_incenter, get_circumcenter, get_orthocenter, get_all_centers,
    TriangleCenterCalculator, construct_triangle, construct_triangle_coordinates, Point, Triangle,
    TriangleDefinitionError
)


class TestTriangleCenterCalculator:
    """三角形特殊點計算器測試"""
    
    def setup_method(self):
        """測試設置"""
        self.calculator = TriangleCenterCalculator()
        # 標準3-4-5直角三角形
        self.right_triangle = construct_triangle("sss", side_a=3, side_b=4, side_c=5)
        # 等邊三角形
        self.equilateral_triangle = construct_triangle("sss", side_a=2, side_b=2, side_c=2)
    
    def test_centroid_calculation(self):
        """測試質心計算"""
        centroid = self.calculator.get_centroid(self.right_triangle)
        
        # 3-4-5三角形的質心應該是三個頂點的平均
        # 頂點: (0,0), (5,0), (3.2, 2.4) (大約)
        # 質心: (8.2/3, 2.4/3) = (2.733, 0.8)
        assert abs(centroid.x - 8.2/3) < 1e-2
        assert abs(centroid.y - 2.4/3) < 1e-2
        
        # 等邊三角形的質心
        eq_centroid = self.calculator.get_centroid(self.equilateral_triangle)
        assert eq_centroid is not None
        assert eq_centroid.x > 0
        assert eq_centroid.y > 0
    
    def test_incenter_calculation(self):
        """測試內心計算"""
        incenter = self.calculator.get_incenter(self.right_triangle)
        
        # 內心應該在三角形內部
        assert incenter.x >= 0
        assert incenter.y >= 0
        
        # 3-4-5直角三角形的內心計算
        # 對於此構造的三角形，內心約在 (3.0, 1.0)
        assert abs(incenter.x - 3.0) < 1e-1
        assert abs(incenter.y - 1.0) < 1e-1
        
        # 等邊三角形的內心應該在重心位置
        eq_incenter = self.calculator.get_incenter(self.equilateral_triangle)
        eq_centroid = self.calculator.get_centroid(self.equilateral_triangle)
        
        # 等邊三角形，內心=重心=外心=垂心
        assert abs(eq_incenter.x - eq_centroid.x) < 1e-10
        assert abs(eq_incenter.y - eq_centroid.y) < 1e-10
    
    def test_circumcenter_calculation(self):
        """測試外心計算"""
        circumcenter = self.calculator.get_circumcenter(self.right_triangle)
        
        # 直角三角形的外心應該在斜邊中點
        # 斜邊是從(0,0)到(5,0)，中點是(2.5, 0)
        assert abs(circumcenter.x - 2.5) < 1e-1
        assert abs(circumcenter.y - 0) < 1e-1
        
        # 驗證外心到三個頂點的距離相等（外接圓半徑）
        from utils.geometry import distance
        p1, p2, p3 = self.right_triangle.p1, self.right_triangle.p2, self.right_triangle.p3
        dist1 = distance(circumcenter, p1)
        dist2 = distance(circumcenter, p2) 
        dist3 = distance(circumcenter, p3)
        
        assert abs(dist1 - dist2) < 1e-10
        assert abs(dist2 - dist3) < 1e-10
    
    def test_orthocenter_calculation(self):
        """測試垂心計算"""
        orthocenter = self.calculator.get_orthocenter(self.right_triangle)
        
        # 直角三角形的垂心應該在直角頂點
        # 3-4-5三角形的直角頂點大約在 (3.2, 2.4)
        assert orthocenter.x >= 0
        assert orthocenter.y >= 0
        
        # 等邊三角形的垂心=重心
        eq_orthocenter = self.calculator.get_orthocenter(self.equilateral_triangle)
        eq_centroid = self.calculator.get_centroid(self.equilateral_triangle)
        
        assert abs(eq_orthocenter.x - eq_centroid.x) < 1e-10
        assert abs(eq_orthocenter.y - eq_centroid.y) < 1e-10
    
    def test_degenerate_triangles(self):
        """測試退化三角形"""
        # 共線三角形應該拋出異常
        with pytest.raises(TriangleDefinitionError):
            degenerate = Triangle(Point(0, 0), Point(1, 0), Point(2, 0))
            self.calculator.get_circumcenter(degenerate)


class TestUnifiedInterface:
    """統一接口測試"""
    
    def setup_method(self):
        """測試設置"""
        self.triangle = construct_triangle("sss", side_a=3, side_b=4, side_c=5)
    
    def test_get_centroid_function(self):
        """測試get_centroid函數"""
        centroid = get_centroid(self.triangle)
        assert centroid is not None
        assert isinstance(centroid, Point)
    
    def test_get_incenter_function(self):
        """測試get_incenter函數"""
        incenter = get_incenter(self.triangle)
        assert incenter is not None
        assert isinstance(incenter, Point)
    
    def test_get_circumcenter_function(self):
        """測試get_circumcenter函數"""
        circumcenter = get_circumcenter(self.triangle)
        assert circumcenter is not None
        assert isinstance(circumcenter, Point)
    
    def test_get_orthocenter_function(self):
        """測試get_orthocenter函數"""
        orthocenter = get_orthocenter(self.triangle)
        assert orthocenter is not None
        assert isinstance(orthocenter, Point)
    
    def test_get_all_centers_function(self):
        """測試get_all_centers函數"""
        centers = get_all_centers(self.triangle)
        
        assert isinstance(centers, dict)
        assert 'centroid' in centers
        assert 'incenter' in centers
        assert 'circumcenter' in centers
        assert 'orthocenter' in centers
        
        # 所有特殊點都應該是Point對象
        for center_name, center_point in centers.items():
            assert isinstance(center_point, Point)
    
    def test_backend_selection(self):
        """測試不同數學後端"""
        # NumPy後端
        centroid_numpy = get_centroid(self.triangle, backend="numpy")
        assert centroid_numpy is not None
        
        # SymPy後端（如果可用）
        try:
            centroid_sympy = get_centroid(self.triangle, backend="sympy")
            assert centroid_sympy is not None
            
            # 不同後端結果應該相近
            assert abs(centroid_numpy.x - centroid_sympy.x) < 1e-6
            assert abs(centroid_numpy.y - centroid_sympy.y) < 1e-6
        except ImportError:
            # SymPy不可用時跳過
            pass
        
        # Python後端
        centroid_python = get_centroid(self.triangle, backend="python")
        assert centroid_python is not None


class TestSpecialTriangles:
    """特殊三角形測試"""
    
    def test_right_triangle_properties(self):
        """測試直角三角形特性"""
        triangle = construct_triangle("sss", side_a=3, side_b=4, side_c=5)
        
        # 外心應該在斜邊中點
        circumcenter = get_circumcenter(triangle)
        
        # 外接圓半徑應該是斜邊長度的一半
        from utils.geometry import distance
        radius = distance(circumcenter, triangle.p1)
        assert abs(radius - 2.5) < 1e-1  # 5/2 = 2.5
    
    def test_equilateral_triangle_properties(self):
        """測試等邊三角形特性"""
        triangle = construct_triangle("sss", side_a=2, side_b=2, side_c=2)
        
        centroid = get_centroid(triangle)
        incenter = get_incenter(triangle)
        circumcenter = get_circumcenter(triangle)
        orthocenter = get_orthocenter(triangle)
        
        # 等邊三角形的四個特殊點應該重合
        tolerance = 1e-10
        assert abs(centroid.x - incenter.x) < tolerance
        assert abs(centroid.y - incenter.y) < tolerance
        assert abs(centroid.x - circumcenter.x) < tolerance
        assert abs(centroid.y - circumcenter.y) < tolerance
        assert abs(centroid.x - orthocenter.x) < tolerance
        assert abs(centroid.y - orthocenter.y) < tolerance
    
    def test_isosceles_triangle_properties(self):
        """測試等腰三角形特性"""
        triangle = construct_triangle("sss", side_a=3, side_b=3, side_c=4)
        
        centroid = get_centroid(triangle)
        circumcenter = get_circumcenter(triangle)
        
        # 等腰三角形的重心和外心應該在對稱軸上
        # 此處我們主要檢查計算不會出錯
        assert centroid is not None
        assert circumcenter is not None


class TestPerformanceAndAccuracy:
    """性能和精度測試"""
    
    def test_calculation_accuracy(self):
        """測試計算精度"""
        # 使用已知精確值的三角形
        triangle = construct_triangle_coordinates(
            Point(0, 0), Point(6, 0), Point(0, 8)
        )
        
        # 6-8-10直角三角形
        centroid = get_centroid(triangle)
        
        # 重心坐標應該是 (2, 8/3)
        assert abs(centroid.x - 2.0) < 1e-10
        assert abs(centroid.y - 8.0/3) < 1e-10
    
    def test_center_calculation_performance(self, benchmark):
        """測試特殊點計算性能"""
        triangle = construct_triangle("sss", side_a=3, side_b=4, side_c=5)
        
        # 基準測試重心計算
        result = benchmark(get_centroid, triangle)
        assert result is not None
    
    def test_all_centers_performance(self, benchmark):
        """測試所有特殊點計算性能"""
        triangle = construct_triangle("sss", side_a=3, side_b=4, side_c=5)
        
        # 基準測試所有特殊點計算
        results = benchmark(get_all_centers, triangle)
        assert len(results) == 4


class TestBackwardCompatibility:
    """向後兼容性測試"""
    
    def test_legacy_interface_support(self):
        """測試傳統接口支援"""
        triangle = construct_triangle("sss", side_a=3, side_b=4, side_c=5)
        
        # 測試是否支援舊格式調用
        try:
            from utils.geometry import get_centroid_legacy
            legacy_result = get_centroid_legacy(
                (triangle.p1.x, triangle.p1.y),
                (triangle.p2.x, triangle.p2.y), 
                (triangle.p3.x, triangle.p3.y)
            )
            assert legacy_result is not None
        except ImportError:
            # 如果沒有legacy函數則跳過
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])