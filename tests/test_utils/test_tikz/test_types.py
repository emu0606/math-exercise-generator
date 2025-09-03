#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TikZ類型系統單元測試
測試 utils.tikz.types 模組的所有數據類型和工具函數
"""

import pytest
import math
from utils.tikz.types import (
    TikZPosition, ArcType, LabelType, CoordinateSystem,
    ArcConfig, LabelConfig, RenderingContext, 
    TikZCoordinate, TikZDistance, TikZAngle,
    format_tikz_coordinate, format_tikz_angle
)
from utils.geometry import Point


class TestTikZCoordinate:
    """TikZ座標測試"""
    
    def test_coordinate_creation(self):
        """測試座標創建 - 使用Point類"""
        point = Point(1.5, 2.0)
        coord_str = format_tikz_coordinate(point)
        assert "1.500" in coord_str and "2.000" in coord_str
    
    def test_coordinate_from_tuple(self):
        """測試從元組創建座標"""
        point = Point(3.0, 4.0)
        coord_str = format_tikz_coordinate(point)
        assert "3.000" in coord_str and "4.000" in coord_str
    
    def test_coordinate_format(self):
        """測試座標格式化"""
        coord = Point(1.234, 5.678)
        formatted = coord.format(precision=2)
        assert formatted == "(1.23,5.68)"
    
    def test_coordinate_arithmetic(self):
        """測試座標運算"""
        coord1 = Point(1.0, 2.0)
        coord2 = Point(3.0, 4.0)
        
        result_add = coord1 + coord2
        assert result_add.x == 4.0
        assert result_add.y == 6.0
        
        result_sub = coord2 - coord1
        assert result_sub.x == 2.0
        assert result_sub.y == 2.0


class TestTikZDistance:
    """TikZ距離測試"""
    
    def test_distance_creation(self):
        """測試距離創建"""
        dist = TikZDistance(2.5, "cm")
        assert dist.value == 2.5
        assert dist.unit == "cm"
    
    def test_distance_format(self):
        """測試距離格式化"""
        dist = TikZDistance(1.234, "mm")
        formatted = dist.format(precision=2)
        assert formatted == "1.23mm"
    
    def test_distance_conversion(self):
        """測試距離單位轉換"""
        dist_cm = TikZDistance(1.0, "cm")
        dist_mm = dist_cm.convert_to("mm")
        assert dist_mm.value == 10.0
        assert dist_mm.unit == "mm"


class TestTikZAngle:
    """TikZ角度測試"""
    
    def test_angle_creation(self):
        """測試角度創建"""
        angle = TikZAngle(45.0)
        assert angle.degrees == 45.0
        assert abs(angle.radians - math.pi/4) < 1e-10
    
    def test_angle_normalization(self):
        """測試角度標準化"""
        angle = TikZAngle(390.0)
        normalized = angle.normalize()
        assert normalized.degrees == 30.0
    
    def test_angle_format(self):
        """測試角度格式化"""
        angle = TikZAngle(45.5)
        formatted = angle.format(precision=1)
        assert formatted == "45.5"


class TestConfigurationTypes:
    """配置類型測試"""
    
    def test_arc_config(self):
        """測試弧線配置"""
        config = ArcConfig(
            radius=1.0,
            start_angle=0.0,
            end_angle=90.0,
            color="blue"
        )
        assert config.radius == 1.0
        assert config.start_angle == 0.0
        assert config.end_angle == 90.0
        assert config.color == "blue"
    
    def test_label_config(self):
        """測試標籤配置"""
        config = LabelConfig(
            text="A",
            position=TikZPosition.ABOVE,
            offset=TikZDistance(0.1, "cm")
        )
        assert config.text == "A"
        assert config.position == TikZPosition.ABOVE
        assert config.offset.value == 0.1
    
    def test_rendering_context(self):
        """測試渲染上下文"""
        context = RenderingContext(
            precision=2,
            unit="mm",
            debug_mode=True
        )
        assert context.precision == 2
        assert context.unit == "mm"
        assert context.debug_mode is True


class TestParameterTypes:
    """參數類型測試"""
    
    def test_arc_parameters(self):
        """測試弧線參數"""
        params = ArcParameters(
            center=Point(0.0, 0.0),
            radius=1.0,
            start_angle=0.0,
            end_angle=90.0,
            tikz_code="\\arc[radius=1cm] (0:90)"
        )
        assert params.center.x == 0.0
        assert params.center.y == 0.0
        assert params.radius == 1.0
        assert params.tikz_code == "\\arc[radius=1cm] (0:90)"
    
    def test_label_parameters(self):
        """測試標籤參數"""
        params = LabelParameters(
            position=Point(1.0, 1.0),
            text="Label",
            anchor=TikZAnchor.CENTER,
            tikz_code="\\node at (1,1) {Label};"
        )
        assert params.position.x == 1.0
        assert params.position.y == 1.0
        assert params.text == "Label"
        assert params.anchor == TikZAnchor.CENTER


class TestUtilityFunctions:
    """工具函數測試"""
    
    def test_normalize_tikz_position(self):
        """測試TikZ位置標準化"""
        # 字符串到枚舉
        pos = normalize_tikz_position("above")
        assert pos == TikZPosition.ABOVE
        
        # 枚舉保持不變
        pos = normalize_tikz_position(TikZPosition.BELOW)
        assert pos == TikZPosition.BELOW
    
    def test_normalize_tikz_anchor(self):
        """測試TikZ錨點標準化"""
        # 字符串到枚舉
        anchor = normalize_tikz_anchor("center")
        assert anchor == TikZAnchor.CENTER
        
        # 枚舉保持不變
        anchor = normalize_tikz_anchor(TikZAnchor.NORTH)
        assert anchor == TikZAnchor.NORTH
    
    def test_format_tikz_coordinate(self):
        """測試座標格式化"""
        formatted = format_tikz_coordinate(1.234, 5.678, precision=2)
        assert formatted == "(1.23,5.68)"
        
        formatted = format_tikz_coordinate(0.0, -1.5, precision=1)
        assert formatted == "(0.0,-1.5)"
    
    def test_format_tikz_angle(self):
        """測試角度格式化"""
        formatted = format_tikz_angle(45.123, precision=1)
        assert formatted == "45.1"
        
        formatted = format_tikz_angle(0.0, precision=0)
        assert formatted == "0"


class TestEnumerations:
    """枚舉類型測試"""
    
    def test_tikz_position_enum(self):
        """測試TikZ位置枚舉"""
        assert TikZPosition.ABOVE.value == "above"
        assert TikZPosition.BELOW.value == "below"
        assert TikZPosition.LEFT.value == "left"
        assert TikZPosition.RIGHT.value == "right"
    
    def test_tikz_anchor_enum(self):
        """測試TikZ錨點枚舉"""
        assert TikZAnchor.CENTER.value == "center"
        assert TikZAnchor.NORTH.value == "north"
        assert TikZAnchor.SOUTH.value == "south"
        assert TikZAnchor.EAST.value == "east"
        assert TikZAnchor.WEST.value == "west"
    
    def test_arc_type_enum(self):
        """測試弧線類型枚舉"""
        assert ArcType.ANGLE.value == "angle"
        assert ArcType.CIRCLE.value == "circle"
        assert ArcType.ARC.value == "arc"


class TestErrorHandling:
    """錯誤處理測試"""
    
    def test_invalid_position_normalization(self):
        """測試無效位置標準化"""
        with pytest.raises(TikZConfigError):
            normalize_tikz_position("invalid_position")
    
    def test_invalid_anchor_normalization(self):
        """測試無效錨點標準化"""
        with pytest.raises(TikZConfigError):
            normalize_tikz_anchor("invalid_anchor")
    
    def test_invalid_distance_unit(self):
        """測試無效距離單位"""
        dist = TikZDistance(1.0, "cm")
        with pytest.raises(TikZConfigError):
            dist.convert_to("invalid_unit")


class TestComplexOperations:
    """複雜操作測試"""
    
    def test_coordinate_transform_chain(self):
        """測試座標轉換鏈"""
        transform = CoordinateTransform(
            scale=(2.0, 1.5),
            translate=(1.0, 0.5),
            rotate=45.0
        )
        
        original = Point(1.0, 1.0)
        transformed = transform.apply(original)
        
        # 驗證轉換結果
        assert transformed is not None
        assert isinstance(transformed, TikZCoordinate)
    
    def test_rendering_context_validation(self):
        """測試渲染上下文驗證"""
        # 有效配置
        context = RenderingContext(precision=3, unit="cm", debug_mode=False)
        assert context.is_valid()
        
        # 無效精度
        with pytest.raises(TikZConfigError):
            RenderingContext(precision=-1, unit="cm")
        
        # 無效單位
        with pytest.raises(TikZConfigError):
            RenderingContext(precision=3, unit="invalid")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])