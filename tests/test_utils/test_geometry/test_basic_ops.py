#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
幾何基礎運算單元測試
測試 utils.geometry.basic_ops 模組的所有基礎運算功能
"""

import pytest
import math
from utils.geometry import (
    distance, midpoint, centroid, area_of_triangle, signed_area_of_triangle,
    angle_between_vectors, angle_at_vertex, normalize_angle, angle_difference,
    rotate_point, reflect_point, is_point_on_segment, is_clockwise,
    perpendicular_distance, distances_from_point, find_closest_point,
    Point, ValidationError
)


class TestBasicOperations:
    """基礎幾何運算測試"""
    
    def test_distance_calculation(self):
        """測試距離計算"""
        # 3-4-5 直角三角形
        p1 = Point(0, 0)
        p2 = Point(3, 4)
        assert abs(distance(p1, p2) - 5.0) < 1e-10
        
        # 同一點
        assert distance(p1, p1) == 0.0
        
        # 軸對齊距離
        assert distance(Point(0, 0), Point(5, 0)) == 5.0
        assert distance(Point(0, 0), Point(0, 3)) == 3.0
    
    def test_midpoint_calculation(self):
        """測試中點計算"""
        p1 = Point(0, 0)
        p2 = Point(4, 6)
        mid = midpoint(p1, p2)
        assert mid.x == 2.0
        assert mid.y == 3.0
        
        # 負坐標
        p3 = Point(-2, -4)
        p4 = Point(2, 4)
        mid2 = midpoint(p3, p4)
        assert mid2.x == 0.0
        assert mid2.y == 0.0
    
    def test_centroid_calculation(self):
        """測試質心計算"""
        center = centroid(Point(0, 0), Point(3, 0), Point(0, 3))
        assert abs(center.x - 1.0) < 1e-10
        assert abs(center.y - 1.0) < 1e-10
        
        # 單個點
        center_single = centroid(Point(5, 7))
        assert center_single.x == 5.0
        assert center_single.y == 7.0
    
    def test_triangle_area_calculation(self):
        """測試三角形面積計算"""
        # 3-4-5 直角三角形，面積 = 6
        from utils.geometry import Triangle
        triangle1 = Triangle(Point(0, 0), Point(3, 0), Point(0, 4))
        area = area_of_triangle(triangle1)
        assert abs(area - 6.0) < 1e-10
        
        # 小三角形
        triangle2 = Triangle(Point(1, 0), Point(2, 0), Point(1.5, 0.1))
        area_small = area_of_triangle(triangle2)
        assert area_small > 0
    
    def test_signed_area_calculation(self):
        """測試帶符號面積計算"""
        
        # 逆時針為正
        signed_area_ccw = signed_area_of_triangle(Point(0, 0), Point(3, 0), Point(0, 4))
        assert signed_area_ccw > 0
        
        # 順時針為負
        signed_area_cw = signed_area_of_triangle(Point(0, 0), Point(0, 4), Point(3, 0))
        assert signed_area_cw < 0
        
        # 絕對值相等
        assert abs(signed_area_ccw + signed_area_cw) < 1e-10
    
    def test_angle_calculations(self):
        """測試角度計算"""
        # 90度角
        v1 = (1, 0)
        v2 = (0, 1)
        angle = angle_between_vectors(v1, v2)
        assert abs(angle - math.pi/2) < 1e-10
        
        # 180度角
        v3 = (1, 0)
        v4 = (-1, 0)
        angle2 = angle_between_vectors(v3, v4)
        assert abs(angle2 - math.pi) < 1e-10
        
        # 頂點角度計算
        vertex = Point(0, 0)
        arm1 = Point(1, 0)
        arm2 = Point(0, 1)
        vertex_angle = angle_at_vertex(vertex, arm1, arm2)
        assert abs(vertex_angle - math.pi/2) < 1e-10
    
    def test_angle_normalization(self):
        """測試角度標準化"""
        # 超過2π的角度
        angle1 = 3 * math.pi
        normalized1 = normalize_angle(angle1)
        assert abs(normalized1 - math.pi) < 1e-10
        
        # 負角度
        angle2 = -math.pi/2
        normalized2 = normalize_angle(angle2)
        assert abs(normalized2 - 3*math.pi/2) < 1e-10
        
        # 角度差計算
        diff = angle_difference(math.pi/4, 3*math.pi/4)
        assert abs(abs(diff) - math.pi/2) < 1e-10
    
    def test_point_transformations(self):
        """測試點變換"""
        p = Point(1, 0)
        
        # 90度旋轉
        rotated = rotate_point(p, Point(0, 0), math.pi/2)
        assert abs(rotated.x) < 1e-10
        assert abs(rotated.y - 1.0) < 1e-10
        
        # 反射（關於x軸）
        reflected = reflect_point(p, Point(0, 0), Point(1, 0))
        assert abs(reflected.x - 1.0) < 1e-10
        assert abs(reflected.y) < 1e-10
    
    def test_geometric_queries(self):
        """測試幾何查詢"""
        # 點是否在線段上
        p1 = Point(0, 0)
        p2 = Point(4, 0)
        test_point = Point(2, 0)
        assert is_point_on_segment(test_point, p1, p2)
        
        outside_point = Point(5, 0)
        assert not is_point_on_segment(outside_point, p1, p2)
        
        # 順時針檢查
        assert not is_clockwise(Point(0, 0), Point(1, 0), Point(0, 1))
        assert is_clockwise(Point(0, 0), Point(0, 1), Point(1, 0))
    
    def test_distance_operations(self):
        """測試距離相關操作"""
        line_start = Point(0, 0)
        line_end = Point(3, 4)
        test_point = Point(3, 0)
        
        # 點到線距離
        perp_dist = perpendicular_distance(test_point, line_start, line_end)
        assert perp_dist > 0
        
        # 多點距離計算
        points = [Point(0, 0), Point(1, 1), Point(2, 2)]
        reference = Point(0, 0)
        distances = distances_from_point(reference, points)
        assert len(distances) == 3
        assert distances[0] == 0.0
        assert abs(distances[1] - math.sqrt(2)) < 1e-10
        
        # 最近點查找
        closest_point, closest_distance, closest_index = find_closest_point(reference, points)
        assert closest_point == Point(0, 0)
        assert closest_distance == 0.0
        assert closest_index == 0
    
    def test_error_handling(self):
        """測試錯誤處理"""
        # 沒有提供點
        with pytest.raises(ValidationError):
            centroid()
        
        # 無效的角度向量（零向量）
        from utils.geometry import ComputationError
        with pytest.raises(ComputationError):
            angle_between_vectors((0, 0), (1, 0))


class TestPerformance:
    """性能測試"""
    
    def test_distance_performance(self, benchmark):
        """測試距離計算性能"""
        p1 = Point(0, 0)
        p2 = Point(1000, 1000)
        result = benchmark(distance, p1, p2)
        assert result > 0
    
    def test_batch_operations_performance(self, benchmark):
        """測試批次操作性能"""
        points = [Point(i, i*2) for i in range(1000)]
        reference = Point(0, 0)
        results = benchmark(distances_from_point, reference, points)
        assert len(results) == 1000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])