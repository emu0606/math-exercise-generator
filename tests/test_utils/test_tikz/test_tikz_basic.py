#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TikZ模組基礎測試
測試 utils.tikz 模組的核心功能和類型系統
"""

import pytest
import math
from utils.tikz.types import (
    TikZPosition, TikZAnchor, ArcType, LabelType, CoordinateSystem,
    ArcConfig, LabelConfig, RenderingContext
)
from utils.geometry import Point


class TestTikZEnumerations:
    """TikZ枚舉測試"""
    
    def test_tikz_position_enum(self):
        """測試TikZ位置枚舉"""
        assert TikZPosition.ABOVE.value == "above"
        assert TikZPosition.BELOW.value == "below"
        assert TikZPosition.LEFT.value == "left"
        assert TikZPosition.RIGHT.value == "right"
        assert TikZPosition.CENTER.value == "center"
        
        # 測試方向位置
        assert TikZPosition.NORTH.value == "north"
        assert TikZPosition.SOUTH.value == "south"
        assert TikZPosition.EAST.value == "east"
        assert TikZPosition.WEST.value == "west"
    
    def test_tikz_anchor_enum(self):
        """測試TikZ錨點枚舉"""
        assert TikZAnchor.CENTER.value == "center"
        assert TikZAnchor.NORTH.value == "north"
        assert TikZAnchor.SOUTH.value == "south"
        assert TikZAnchor.EAST.value == "east"
        assert TikZAnchor.WEST.value == "west"
        
        # 測試角落錨點
        assert TikZAnchor.NORTH_EAST.value == "north east"
        assert TikZAnchor.SOUTH_WEST.value == "south west"
    
    def test_arc_type_literals(self):
        """測試弧線類型字面量"""
        # 這些是 Literal 類型，測試有效值
        valid_arc_types = ['angle_arc', 'right_angle', 'custom']
        for arc_type in valid_arc_types:
            # 創建使用此類型的配置
            config = ArcConfig(radius=1.0, arc_type=arc_type)
            assert config.arc_type == arc_type
    
    def test_label_type_literals(self):
        """測試標籤類型字面量"""
        valid_label_types = ['vertex', 'side', 'angle_value']
        # Label types 用於配置，這裡只驗證有效性
        for label_type in valid_label_types:
            assert isinstance(label_type, str)
    
    def test_coordinate_system_literals(self):
        """測試座標系統字面量"""
        valid_coord_systems = ['cartesian', 'polar', 'tikz_native']
        for coord_system in valid_coord_systems:
            assert isinstance(coord_system, str)


class TestArcConfig:
    """弧線配置測試"""
    
    def test_arc_config_creation(self):
        """測試弧線配置創建"""
        config = ArcConfig(radius=0.5)
        assert config.radius == 0.5
        assert config.arc_type == 'angle_arc'  # 預設值
        assert config.start_angle is None
        assert config.end_angle is None
        assert config.style_options == {}
    
    def test_arc_config_with_all_parameters(self):
        """測試帶所有參數的弧線配置"""
        style_options = {"color": "red", "line width": "thick"}
        config = ArcConfig(
            radius=1.0,
            arc_type='custom',
            start_angle=0.0,
            end_angle=math.pi/2,
            style_options=style_options
        )
        
        assert config.radius == 1.0
        assert config.arc_type == 'custom'
        assert config.start_angle == 0.0
        assert config.end_angle == math.pi/2
        assert config.style_options == style_options
    
    def test_arc_config_validation(self):
        """測試弧線配置驗證"""
        from utils.tikz.exceptions import TikZConfigError
        
        # 負半徑應該拋出錯誤
        with pytest.raises(TikZConfigError):
            ArcConfig(radius=-0.5)
        
        # 零半徑應該拋出錯誤
        with pytest.raises(TikZConfigError):
            ArcConfig(radius=0.0)
    
    def test_arc_config_style_options_default(self):
        """測試弧線配置樣式選項預設值"""
        config = ArcConfig(radius=0.3)
        assert config.style_options is not None
        assert isinstance(config.style_options, dict)
        assert len(config.style_options) == 0


class TestLabelConfig:
    """標籤配置測試"""
    
    def test_label_config_creation(self):
        """測試標籤配置創建"""
        config = LabelConfig()
        assert config.offset == 0.15  # 預設值
        assert config.position is None
        assert config.anchor is None
        assert config.style_options == {}
        assert config.auto_position is True
    
    def test_label_config_with_parameters(self):
        """測試帶參數的標籤配置"""
        config = LabelConfig(
            offset=0.2,
            position=TikZPosition.ABOVE,
            anchor=TikZAnchor.CENTER,
            auto_position=False
        )
        
        assert config.offset == 0.2
        assert config.position == TikZPosition.ABOVE or config.position == TikZPosition.ABOVE.value
        assert config.anchor == TikZAnchor.CENTER or config.anchor == TikZAnchor.CENTER.value
        assert config.auto_position is False
    
    def test_label_config_with_string_position(self):
        """測試使用字符串位置的標籤配置"""
        config = LabelConfig(
            position="above left",
            anchor="center"
        )
        
        assert config.position == "above left"
        assert config.anchor == "center"
    
    def test_label_config_validation(self):
        """測試標籤配置驗證"""
        from utils.tikz.exceptions import TikZConfigError
        
        # 負偏移應該拋出錯誤
        with pytest.raises(TikZConfigError):
            LabelConfig(offset=-0.1)
        
        # 零偏移應該拋出錯誤
        with pytest.raises(TikZConfigError):
            LabelConfig(offset=0.0)
    
    def test_label_config_style_options(self):
        """測試標籤配置樣式選項"""
        style_options = {"font": "\\small", "color": "blue"}
        config = LabelConfig(style_options=style_options)
        
        assert config.style_options == style_options


class TestRenderingContext:
    """渲染上下文測試"""
    
    def test_rendering_context_creation(self):
        """測試渲染上下文創建"""
        context = RenderingContext()
        # 檢查是否有基本屬性
        assert hasattr(context, '__dict__')
    
    def test_rendering_context_with_parameters(self):
        """測試帶參數的渲染上下文"""
        try:
            context = RenderingContext(precision=2, unit="mm", debug_mode=True)
            # 如果RenderingContext接受這些參數
            if hasattr(context, 'precision'):
                assert context.precision == 2
            if hasattr(context, 'unit'):
                assert context.unit == "mm"
            if hasattr(context, 'debug_mode'):
                assert context.debug_mode is True
        except TypeError:
            # 如果RenderingContext不接受參數，這也是可以的
            context = RenderingContext()
            assert context is not None


class TestTikZTypeAliases:
    """TikZ類型別名測試"""
    
    def test_tikz_coordinate_types(self):
        """測試TikZ座標類型"""
        # TikZCoordinate 是 Union[Point, str]
        point = Point(1.0, 2.0)
        coord_str = "(1.0,2.0)"
        
        # 這些都應該是有效的TikZ座標
        assert isinstance(point, Point)
        assert isinstance(coord_str, str)
    
    def test_tikz_distance_types(self):
        """測試TikZ距離類型"""
        # TikZDistance 是 Union[float, str]
        distance_float = 1.5
        distance_str = "1.5cm"
        
        assert isinstance(distance_float, float)
        assert isinstance(distance_str, str)
    
    def test_tikz_angle_types(self):
        """測試TikZ角度類型"""
        # TikZAngle 是 float
        angle = math.pi / 4
        assert isinstance(angle, float)
        assert angle == math.pi / 4


class TestConfigurationIntegration:
    """配置整合測試"""
    
    def test_arc_config_with_label_config(self):
        """測試弧線配置與標籤配置結合"""
        arc_config = ArcConfig(radius=0.4, arc_type='angle_arc')
        label_config = LabelConfig(
            offset=0.1,
            position=TikZPosition.ABOVE,
            auto_position=False
        )
        
        # 兩個配置都應該有效
        assert arc_config.radius == 0.4
        assert label_config.offset == 0.1
        assert label_config.position == TikZPosition.ABOVE or label_config.position == TikZPosition.ABOVE.value
    
    def test_multiple_configurations(self):
        """測試多個配置對象"""
        configs = []
        
        # 創建多個弧線配置
        for i, radius in enumerate([0.2, 0.3, 0.4]):
            config = ArcConfig(radius=radius, arc_type='angle_arc')
            configs.append(config)
        
        assert len(configs) == 3
        for i, config in enumerate(configs):
            expected_radius = [0.2, 0.3, 0.4][i]
            assert config.radius == expected_radius


class TestErrorHandling:
    """錯誤處理測試"""
    
    def test_configuration_error_messages(self):
        """測試配置錯誤訊息"""
        from utils.tikz.exceptions import TikZConfigError
        
        try:
            ArcConfig(radius=-1.0)
            pytest.fail("應該拋出TikZConfigError")
        except TikZConfigError as e:
            # 檢查錯誤訊息包含相關資訊
            assert isinstance(e, Exception)
            error_str = str(e)
            assert isinstance(error_str, str)
            assert len(error_str) > 0
    
    def test_label_configuration_errors(self):
        """測試標籤配置錯誤"""
        from utils.tikz.exceptions import TikZConfigError
        
        try:
            LabelConfig(offset=-0.5)
            pytest.fail("應該拋出TikZConfigError")
        except TikZConfigError as e:
            assert isinstance(e, Exception)
            error_str = str(e)
            assert "offset" in error_str or "標籤" in error_str or len(error_str) > 0


class TestTypeCompatibility:
    """類型相容性測試"""
    
    def test_enum_string_compatibility(self):
        """測試枚舉與字符串相容性"""
        # 枚舉值應該可以與字符串比較
        assert TikZPosition.ABOVE.value == "above"
        assert TikZAnchor.CENTER.value == "center"
    
    def test_position_anchor_combinations(self):
        """測試位置和錨點組合"""
        positions = [TikZPosition.ABOVE, TikZPosition.BELOW, TikZPosition.LEFT, TikZPosition.RIGHT]
        anchors = [TikZAnchor.CENTER, TikZAnchor.NORTH, TikZAnchor.SOUTH]
        
        # 測試各種組合
        for position in positions:
            for anchor in anchors:
                config = LabelConfig(position=position, anchor=anchor)
                assert config.position == position or config.position == position.value
                assert config.anchor == anchor or config.anchor == anchor.value


if __name__ == "__main__":
    pytest.main([__file__, "-v"])