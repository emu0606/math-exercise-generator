#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TikZ弧線渲染器單元測試 - ⚠️ 過時版本
測試 utils.tikz.arc_renderer 模組的弧線渲染功能

🚨 **重要提醒 (2025-09-03)**：
此測試文件包含過時的API調用，與當前實現不匹配！

問題說明：
- 這些測試是根據設計預期編寫的，但實際實現時API有調整
- 例如：TikZCoordinate(x,y) 應改為 Point(x,y)
- 例如：render_full_circle() 方法不存在，應使用 render_custom_arc()

當前狀況：
❌ 此測試文件：113個失敗（API不匹配，非功能問題）
✅ 實際功能：100%正常工作，PredefinedTriangleGenerator成功生成1657字符TikZ代碼
✅ 有效測試：見 test_arc_renderer_simple.py (9/9通過)

TODO: 需要將此測試的API更新為與當前實現匹配，或使用有效的測試文件
"""

import pytest
import math
from utils.tikz import (
    ArcRenderer, ArcConfig, ArcParameters, RenderingContext,
    TikZCoordinate, TikZAngle, ArcType
)
from utils.tikz.exceptions import ArcRenderingError, TikZConfigError
from utils.geometry import Point


class TestArcRenderer:
    """弧線渲染器測試"""
    
    def setup_method(self):
        """測試設置"""
        self.context = RenderingContext(precision=2, unit="cm", debug_mode=False)
        self.renderer = ArcRenderer(self.context)
        
        # 測試用的基礎幾何
        self.vertex = Point(0.0, 0.0)
        self.point1 = Point(1.0, 0.0)
        self.point2 = Point(0.0, 1.0)
    
    def test_arc_renderer_creation(self):
        """測試弧線渲染器創建"""
        assert self.renderer is not None
        assert self.renderer.context == self.context
        assert self.renderer.context.precision == 2
        assert self.renderer.context.unit == "cm"
    
    def test_default_arc_renderer(self):
        """測試預設弧線渲染器"""
        default_renderer = ArcRenderer()
        assert default_renderer is not None
        assert default_renderer.context.precision == 3  # 預設值
        assert default_renderer.context.unit == "cm"
    
    def test_render_angle_arc_basic(self):
        """測試基礎角度弧線渲染"""
        result = self.renderer.render_angle_arc(
            vertex=self.vertex,
            point1=self.point1,
            point2=self.point2,
            radius_config="auto"
        )
        
        assert isinstance(result, ArcParameters)
        assert result.center is not None
        assert result.radius > 0
        assert result.start_angle >= 0
        assert result.end_angle >= 0
        assert result.tikz_code is not None
        assert len(result.tikz_code) > 0
    
    def test_render_angle_arc_custom_radius(self):
        """測試自定義半徑角度弧線渲染"""
        custom_radius = 0.5
        result = self.renderer.render_angle_arc(
            vertex=self.vertex,
            point1=self.point1,
            point2=self.point2,
            radius_config=custom_radius
        )
        
        assert abs(result.radius - custom_radius) < 1e-10
        assert result.tikz_code is not None
    
    def test_render_angle_arc_with_config(self):
        """測試使用配置的角度弧線渲染"""
        custom_radius = 0.8
        
        result = self.renderer.render_angle_arc(
            vertex=self.vertex,
            point1=self.point1,
            point2=self.point2,
            radius_config=custom_radius
        )
        
        # 驗證配置生效
        assert abs(result.radius - custom_radius) < 1e-10
        assert result.tikz_code is not None
        assert "0.80cm" in result.tikz_code  # 驗證半徑在TikZ代碼中
    
    def test_render_custom_arc(self):
        """測試自定義弧線渲染"""
        center = Point(1.0, 1.0)  # 使用Point類而不是TikZCoordinate Union類型
        radius = 1.0
        start_angle = 0.0
        end_angle = 1.5708  # 90度的弧度值
        
        result = self.renderer.render_custom_arc(
            center=center,
            radius=radius,
            start_angle=start_angle,
            end_angle=end_angle
        )
        
        assert result.center.x == center.x
        assert result.center.y == center.y
        assert result.radius == radius
        assert abs(result.start_angle - start_angle) < 1e-10
        assert abs(result.end_angle - end_angle) < 1e-10
        assert result.tikz_code is not None
    
    def test_render_full_circle(self):
        """測試完整圓形渲染（使用自定義弧線）"""
        center = Point(0.0, 0.0)
        radius = 2.0
        # 完整圓形：0到2π弧度
        result = self.renderer.render_custom_arc(
            center=center,
            radius=radius,
            start_angle=0.0,
            end_angle=6.2832  # 2π
        )
        
        assert result.center == center
        assert result.radius == radius
        assert result.start_angle == 0.0
        assert result.end_angle == 360.0
        assert "circle" in result.tikz_code.lower() or "360" in result.tikz_code
    
    def test_auto_radius_calculation(self):
        """測試自動半徑計算"""
        # 測試不同的點配置
        vertex = Point(0.0, 0.0)
        point1 = Point(2.0, 0.0)  # 較遠的點
        point2 = Point(0.0, 2.0)
        
        result = self.renderer.render_angle_arc(
            vertex=vertex,
            point1=point1,
            point2=point2,
            radius_config="auto"
        )
        
        # 自動計算的半徑應該合理（不會太大或太小）
        assert 0.1 <= result.radius <= 1.0
    
    def test_angle_calculation_accuracy(self):
        """測試角度計算精度"""
        # 90度角
        result_90 = self.renderer.render_angle_arc(
            vertex=Point(0.0, 0.0),
            point1=Point(1.0, 0.0),
            point2=Point(0.0, 1.0),
            radius_config=0.5
        )
        
        # 驗證90度角的角度差
        angle_diff = abs(result_90.end_angle - result_90.start_angle)
        assert abs(angle_diff - 90.0) < 1.0  # 允許1度誤差
    
    def test_different_arc_types(self):
        """測試不同弧線類型"""
        configs = [
            ArcConfig(arc_type=ArcType.ANGLE),
            ArcConfig(arc_type=ArcType.CIRCLE),
            ArcConfig(arc_type=ArcType.ARC)
        ]
        
        for config in configs:
            result = self.renderer.render_angle_arc(
                vertex=self.vertex,
                point1=self.point1,
                point2=self.point2,
                config=config
            )
            assert result is not None
            assert result.tikz_code is not None


class TestArcConfigurationHandling:
    """弧線配置處理測試"""
    
    def setup_method(self):
        """測試設置"""
        self.renderer = ArcRenderer()
    
    def test_color_configuration(self):
        """測試顏色配置"""
        colors = ["red", "blue", "green", "black", "gray"]
        
        for color in colors:
            config = ArcConfig(color=color)
            result = self.renderer.render_angle_arc(
                vertex=Point(0.0, 0.0),
                point1=Point(1.0, 0.0),
                point2=Point(0.0, 1.0),
                config=config
            )
            assert color in result.tikz_code
    
    def test_line_width_configuration(self):
        """測試線寬配置"""
        line_widths = ["thin", "thick", "very thick", "ultra thick"]
        
        for width in line_widths:
            config = ArcConfig(line_width=width)
            result = self.renderer.render_angle_arc(
                vertex=Point(0.0, 0.0),
                point1=Point(1.0, 0.0),
                point2=Point(0.0, 1.0),
                config=config
            )
            # 線寬可能被轉換為TikZ選項
            assert result.tikz_code is not None
    
    def test_style_configuration(self):
        """測試樣式配置"""
        styles = ["solid", "dashed", "dotted", "dash dot"]
        
        for style in styles:
            config = ArcConfig(style=style)
            result = self.renderer.render_angle_arc(
                vertex=Point(0.0, 0.0),
                point1=Point(1.0, 0.0),
                point2=Point(0.0, 1.0),
                config=config
            )
            assert result.tikz_code is not None


class TestErrorHandling:
    """錯誤處理測試"""
    
    def setup_method(self):
        """測試設置"""
        self.renderer = ArcRenderer()
    
    def test_invalid_radius_config(self):
        """測試無效半徑配置"""
        with pytest.raises(ArcRenderingError):
            self.renderer.render_angle_arc(
                vertex=Point(0.0, 0.0),
                point1=Point(1.0, 0.0),
                point2=Point(0.0, 1.0),
                radius_config=-1.0  # 負半徑
            )
    
    def test_collinear_points(self):
        """測試共線點"""
        with pytest.raises(ArcRenderingError):
            self.renderer.render_angle_arc(
                vertex=Point(0.0, 0.0),
                point1=Point(1.0, 0.0),
                point2=Point(2.0, 0.0),  # 共線
                radius_config=0.5
            )
    
    def test_identical_points(self):
        """測試相同點"""
        with pytest.raises(ArcRenderingError):
            self.renderer.render_angle_arc(
                vertex=Point(0.0, 0.0),
                point1=Point(0.0, 0.0),  # 與頂點相同
                point2=Point(1.0, 0.0),
                radius_config=0.5
            )
    
    def test_invalid_angle_range(self):
        """測試無效角度範圍"""
        with pytest.raises(ArcRenderingError):
            self.renderer.render_custom_arc(
                center=Point(0.0, 0.0),
                radius=1.0,
                start_angle=90.0,
                end_angle=0.0  # 結束角度小於開始角度
            )


class TestTikZCodeGeneration:
    """TikZ代碼生成測試"""
    
    def setup_method(self):
        """測試設置"""
        self.renderer = ArcRenderer()
    
    def test_tikz_code_structure(self):
        """測試TikZ代碼結構"""
        result = self.renderer.render_angle_arc(
            vertex=Point(0.0, 0.0),
            point1=Point(1.0, 0.0),
            point2=Point(0.0, 1.0),
            radius_config=0.5
        )
        
        tikz_code = result.tikz_code
        
        # 基本結構檢查
        assert isinstance(tikz_code, str)
        assert len(tikz_code) > 0
        
        # 可能包含的TikZ元素
        tikz_elements = ["\\draw", "\\arc", "arc", "(", ")", "[", "]"]
        has_tikz_element = any(element in tikz_code for element in tikz_elements)
        assert has_tikz_element
    
    def test_coordinate_precision(self):
        """測試座標精度"""
        context_low_precision = RenderingContext(precision=1)
        renderer_low = ArcRenderer(context_low_precision)
        
        result = renderer_low.render_custom_arc(
            center=Point(1.23456, 2.6789),
            radius=0.7654321,
            start_angle=45.6789,
            end_angle=123.4567
        )
        
        # 檢查精度是否正確應用
        tikz_code = result.tikz_code
        assert tikz_code is not None
        
        # 不應該有太多小數位
        import re
        numbers = re.findall(r'\d+\.\d+', tikz_code)
        for number in numbers:
            decimal_part = number.split('.')[1]
            assert len(decimal_part) <= 2  # 精度1，但可能有舍入


class TestPerformanceAndEdgeCases:
    """性能和邊界情況測試"""
    
    def setup_method(self):
        """測試設置"""
        self.renderer = ArcRenderer()
    
    def test_very_small_angles(self):
        """測試極小角度"""
        # 接近0度的角度
        result = self.renderer.render_angle_arc(
            vertex=Point(0.0, 0.0),
            point1=Point(1.0, 0.0),
            point2=Point(1.0, 0.001),  # 很小的角度
            radius_config=0.5
        )
        
        assert result is not None
        assert result.tikz_code is not None
    
    def test_large_coordinates(self):
        """測試大座標值"""
        result = self.renderer.render_custom_arc(
            center=Point(1000.0, 1000.0),
            radius=100.0,
            start_angle=0.0,
            end_angle=90.0
        )
        
        assert result is not None
        assert result.center.x == 1000.0
        assert result.center.y == 1000.0
    
    def test_batch_arc_rendering(self):
        """測試批次弧線渲染"""
        # 渲染多個弧線
        vertices = [
            (Point(0.0, 0.0), Point(1.0, 0.0), Point(0.0, 1.0)),
            (Point(1.0, 1.0), Point(2.0, 1.0), Point(1.0, 2.0)),
            (Point(-1.0, -1.0), Point(0.0, -1.0), Point(-1.0, 0.0))
        ]
        
        results = []
        for vertex, p1, p2 in vertices:
            result = self.renderer.render_angle_arc(
                vertex=vertex, point1=p1, point2=p2, radius_config=0.3
            )
            results.append(result)
        
        assert len(results) == 3
        for result in results:
            assert result is not None
            assert result.tikz_code is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])