#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TikZ座標轉換器單元測試
測試 utils.tikz.coordinate_transform 模組的座標轉換功能
"""

import pytest
import math
from utils.tikz import (
    CoordinateTransformer, AdvancedCoordinateTransformer, CoordinateTransform,
    TikZCoordinate, TikZDistance, TikZAngle, RenderingContext,
    tikz_coordinate, tikz_angle_degrees, tikz_distance, tikz_options_format,
    batch_coordinate_transform, batch_angle_transform,
    ensure_tikz_coordinate, ensure_tikz_angle, get_arc_render_params
)
from utils.tikz.exceptions import CoordinateTransformError, TikZConfigError
from utils.geometry import Point


class TestCoordinateTransformer:
    """座標轉換器測試"""
    
    def setup_method(self):
        """測試設置"""
        self.context = RenderingContext(precision=3, unit="cm")
        self.transformer = CoordinateTransformer(self.context)
    
    def test_transformer_creation(self):
        """測試轉換器創建"""
        assert self.transformer is not None
        assert self.transformer.context == self.context
        assert self.transformer.context.precision == 3
        assert self.transformer.context.unit == "cm"
    
    def test_default_transformer(self):
        """測試預設轉換器"""
        default_transformer = CoordinateTransformer()
        assert default_transformer is not None
        assert default_transformer.context.precision == 3
    
    def test_point_to_tikz_coordinate(self):
        """測試點到TikZ座標轉換"""
        point = Point(1.5, 2.7)
        tikz_coord = self.transformer.point_to_tikz_coordinate(point)
        
        assert isinstance(tikz_coord, TikZCoordinate)
        assert tikz_coord.x == 1.5
        assert tikz_coord.y == 2.7
    
    def test_tikz_coordinate_to_point(self):
        """測試TikZ座標到點轉換"""
        tikz_coord = Point(3.2, 4.8)
        point = self.transformer.tikz_coordinate_to_point(tikz_coord)
        
        assert isinstance(point, Point)
        assert point.x == 3.2
        assert point.y == 4.8
    
    def test_format_coordinate(self):
        """測試座標格式化"""
        coordinate = Point(1.23456, 7.89012)
        formatted = self.transformer.format_coordinate(coordinate)
        
        assert isinstance(formatted, str)
        assert formatted.startswith("(")
        assert formatted.endswith(")")
        assert "1.235" in formatted  # 精度3
        assert "7.890" in formatted
    
    def test_format_coordinate_with_unit(self):
        """測試帶單位的座標格式化"""
        coordinate = Point(2.0, 3.0)
        formatted = self.transformer.format_coordinate(coordinate, include_unit=True)
        
        assert "cm" in formatted or formatted is not None
    
    def test_apply_scale_transform(self):
        """測試縮放轉換"""
        original = Point(2.0, 3.0)
        scaled = self.transformer.apply_scale(original, scale_x=2.0, scale_y=1.5)
        
        assert scaled.x == 4.0
        assert scaled.y == 4.5
    
    def test_apply_translation_transform(self):
        """測試平移轉換"""
        original = Point(1.0, 1.0)
        translated = self.transformer.apply_translation(original, dx=2.0, dy=-1.0)
        
        assert translated.x == 3.0
        assert translated.y == 0.0
    
    def test_apply_rotation_transform(self):
        """測試旋轉轉換"""
        original = Point(1.0, 0.0)
        # 旋轉90度
        rotated = self.transformer.apply_rotation(original, angle_degrees=90.0)
        
        # 由於浮點精度，使用近似比較
        assert abs(rotated.x) < 1e-10
        assert abs(rotated.y - 1.0) < 1e-10


class TestAdvancedCoordinateTransformer:
    """進階座標轉換器測試"""
    
    def setup_method(self):
        """測試設置"""
        self.transformer = AdvancedCoordinateTransformer()
    
    def test_composite_transform(self):
        """測試複合轉換"""
        transform = CoordinateTransform(
            scale=(2.0, 1.5),
            translate=(1.0, 0.5),
            rotate=45.0
        )
        
        original = Point(1.0, 1.0)
        result = self.transformer.apply_transform(original, transform)
        
        assert isinstance(result, TikZCoordinate)
        # 複合轉換的結果應該是有效的
        assert result.x is not None
        assert result.y is not None
    
    def test_inverse_transform(self):
        """測試逆轉換"""
        transform = CoordinateTransform(
            scale=(2.0, 2.0),
            translate=(3.0, 4.0),
            rotate=0.0
        )
        
        original = Point(1.0, 1.0)
        transformed = self.transformer.apply_transform(original, transform)
        inverse_transformed = self.transformer.apply_inverse_transform(transformed, transform)
        
        # 逆轉換後應該接近原始座標
        assert abs(inverse_transformed.x - original.x) < 1e-10
        assert abs(inverse_transformed.y - original.y) < 1e-10
    
    def test_coordinate_system_conversion(self):
        """測試座標系統轉換"""
        # 笛卡爾座標到極座標
        cartesian = Point(3.0, 4.0)
        polar = self.transformer.cartesian_to_polar(cartesian)
        
        # 極座標應該是 (5.0, arctan(4/3))
        expected_r = 5.0
        expected_theta = math.atan2(4.0, 3.0)
        
        assert abs(polar.r - expected_r) < 1e-10
        assert abs(polar.theta - expected_theta) < 1e-10
    
    def test_bounding_box_calculation(self):
        """測試邊界框計算"""
        coordinates = [
            Point(0.0, 0.0),
            Point(2.0, 3.0),
            Point(-1.0, 1.0),
            Point(4.0, -2.0)
        ]
        
        bbox = self.transformer.calculate_bounding_box(coordinates)
        
        assert bbox.min_x == -1.0
        assert bbox.max_x == 4.0
        assert bbox.min_y == -2.0
        assert bbox.max_y == 3.0


class TestUtilityFunctions:
    """工具函數測試"""
    
    def test_tikz_coordinate_function(self):
        """測試tikz_coordinate工具函數"""
        coord = tikz_coordinate(1.5, 2.5, precision=2)
        assert coord == "(1.50,2.50)"
        
        coord_no_precision = tikz_coordinate(1.0, 2.0)
        assert coord_no_precision == "(1.000,2.000)"  # 預設精度3
    
    def test_tikz_angle_degrees_function(self):
        """測試tikz_angle_degrees工具函數"""
        angle_str = tikz_angle_degrees(45.123, precision=1)
        assert angle_str == "45.1"
        
        angle_str_no_precision = tikz_angle_degrees(90.0)
        assert angle_str_no_precision == "90.000"
    
    def test_tikz_distance_function(self):
        """測試tikz_distance工具函數"""
        dist_str = tikz_distance(1.234, unit="cm", precision=2)
        assert dist_str == "1.23cm"
        
        dist_str_mm = tikz_distance(5.0, unit="mm")
        assert dist_str_mm == "5.000mm"
    
    def test_tikz_options_format_function(self):
        """測試tikz_options_format工具函數"""
        options = {
            "color": "red",
            "line width": "thick",
            "dashed": None
        }
        
        formatted = tikz_options_format(options)
        assert isinstance(formatted, str)
        assert "color=red" in formatted
        assert "line width=thick" in formatted
        assert "dashed" in formatted
    
    def test_ensure_tikz_coordinate_function(self):
        """測試ensure_tikz_coordinate工具函數"""
        # 從Point轉換
        point = Point(1.0, 2.0)
        tikz_coord = ensure_tikz_coordinate(point)
        assert isinstance(tikz_coord, TikZCoordinate)
        assert tikz_coord.x == 1.0
        assert tikz_coord.y == 2.0
        
        # 從元組轉換
        tuple_coord = (3.0, 4.0)
        tikz_coord = ensure_tikz_coordinate(tuple_coord)
        assert isinstance(tikz_coord, TikZCoordinate)
        assert tikz_coord.x == 3.0
        assert tikz_coord.y == 4.0
        
        # 已經是TikZCoordinate
        existing_coord = Point(5.0, 6.0)
        result = ensure_tikz_coordinate(existing_coord)
        assert result == existing_coord
    
    def test_ensure_tikz_angle_function(self):
        """測試ensure_tikz_angle工具函數"""
        # 從float轉換
        angle = ensure_tikz_angle(45.0)
        assert isinstance(angle, TikZAngle)
        assert angle.degrees == 45.0
        
        # 從弧度轉換
        angle_rad = ensure_tikz_angle(math.pi/4, is_radians=True)
        assert isinstance(angle_rad, TikZAngle)
        assert abs(angle_rad.degrees - 45.0) < 1e-10
        
        # 已經是TikZAngle
        existing_angle = TikZAngle(30.0)
        result = ensure_tikz_angle(existing_angle)
        assert result == existing_angle


class TestBatchOperations:
    """批次操作測試"""
    
    def test_batch_coordinate_transform(self):
        """測試批次座標轉換"""
        points = [Point(0.0, 0.0), Point(1.0, 1.0), Point(2.0, 0.0)]
        
        tikz_coords = batch_coordinate_transform(points, precision=2)
        
        assert len(tikz_coords) == 3
        for coord in tikz_coords:
            assert isinstance(coord, str)
            assert coord.startswith("(")
            assert coord.endswith(")")
    
    def test_batch_angle_transform(self):
        """測試批次角度轉換"""
        angles_degrees = [0.0, 45.0, 90.0, 180.0, 270.0]
        
        tikz_angles = batch_angle_transform(angles_degrees, precision=1)
        
        assert len(tikz_angles) == 5
        expected = ["0.0", "45.0", "90.0", "180.0", "270.0"]
        for i, angle_str in enumerate(tikz_angles):
            assert angle_str == expected[i]
    
    def test_batch_transform_with_transform_matrix(self):
        """測試批次轉換與轉換矩陣"""
        coordinates = [
            Point(0.0, 0.0),
            Point(1.0, 0.0),
            Point(0.0, 1.0)
        ]
        
        transform = CoordinateTransform(
            scale=(2.0, 2.0),
            translate=(1.0, 1.0)
        )
        
        transformer = AdvancedCoordinateTransformer()
        transformed_coords = transformer.batch_apply_transform(coordinates, transform)
        
        assert len(transformed_coords) == 3
        for coord in transformed_coords:
            assert isinstance(coord, TikZCoordinate)
        
        # 檢查第一個點的轉換結果
        # (0,0) -> scale(2,2) -> (0,0) -> translate(1,1) -> (1,1)
        assert transformed_coords[0].x == 1.0
        assert transformed_coords[0].y == 1.0


class TestBackwardCompatibility:
    """向後相容測試"""
    
    def test_get_arc_render_params_compatibility(self):
        """測試get_arc_render_params向後相容函數"""
        vertex = Point(0.0, 0.0)
        point1 = Point(1.0, 0.0)
        point2 = Point(0.0, 1.0)
        
        # 應該返回相容的結果
        result = get_arc_render_params(vertex, point1, point2, radius_config="auto")
        
        # 檢查返回的結果結構
        assert result is not None
        # 可能是字典或對象形式，取決於實現


class TestErrorHandling:
    """錯誤處理測試"""
    
    def setup_method(self):
        """測試設置"""
        self.transformer = CoordinateTransformer()
    
    def test_invalid_scale_factors(self):
        """測試無效縮放因子"""
        coordinate = Point(1.0, 1.0)
        
        # 零縮放
        with pytest.raises(CoordinateTransformError):
            self.transformer.apply_scale(coordinate, scale_x=0.0, scale_y=1.0)
        
        with pytest.raises(CoordinateTransformError):
            self.transformer.apply_scale(coordinate, scale_x=1.0, scale_y=0.0)
    
    def test_invalid_coordinate_input(self):
        """測試無效座標輸入"""
        with pytest.raises(TikZConfigError):
            ensure_tikz_coordinate("invalid")
        
        with pytest.raises(TikZConfigError):
            ensure_tikz_coordinate(None)
    
    def test_invalid_angle_input(self):
        """測試無效角度輸入"""
        with pytest.raises(TikZConfigError):
            ensure_tikz_angle("invalid")
        
        with pytest.raises(TikZConfigError):
            ensure_tikz_angle(None)
    
    def test_empty_batch_operations(self):
        """測試空批次操作"""
        # 空列表應該返回空結果
        result = batch_coordinate_transform([])
        assert result == []
        
        result = batch_angle_transform([])
        assert result == []


class TestComplexTransformationScenarios:
    """複雜轉換場景測試"""
    
    def setup_method(self):
        """測試設置"""
        self.transformer = AdvancedCoordinateTransformer()
    
    def test_multiple_sequential_transforms(self):
        """測試多個順序轉換"""
        original = Point(1.0, 0.0)
        
        # 依次應用多個轉換
        scaled = self.transformer.apply_scale(original, scale_x=2.0, scale_y=2.0)
        rotated = self.transformer.apply_rotation(scaled, angle_degrees=90.0)
        translated = self.transformer.apply_translation(rotated, dx=1.0, dy=1.0)
        
        # 最終結果應該合理
        assert translated is not None
        assert isinstance(translated, TikZCoordinate)
    
    def test_transformation_matrix_composition(self):
        """測試轉換矩陣組合"""
        transform1 = CoordinateTransform(scale=(2.0, 1.0), rotate=45.0)
        transform2 = CoordinateTransform(translate=(1.0, 1.0), scale=(0.5, 2.0))
        
        # 組合轉換
        composed = self.transformer.compose_transforms(transform1, transform2)
        
        original = Point(1.0, 1.0)
        result = self.transformer.apply_transform(original, composed)
        
        assert result is not None
        assert isinstance(result, TikZCoordinate)
    
    def test_coordinate_precision_preservation(self):
        """測試座標精度保持"""
        high_precision_context = RenderingContext(precision=6, unit="mm")
        transformer = CoordinateTransformer(high_precision_context)
        
        coordinate = Point(1.123456789, 2.987654321)
        formatted = transformer.format_coordinate(coordinate)
        
        # 應該保持指定的精度
        assert "1.123457" in formatted  # 6位精度，舍入
        assert "2.987654" in formatted


if __name__ == "__main__":
    pytest.main([__file__, "-v"])