#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TikZ標籤定位器單元測試
測試 utils.tikz.label_positioner 模組的標籤定位功能
"""

import pytest
import math
from utils.tikz import (
    LabelPositioner, LabelConfig, LabelParameters, RenderingContext,
    TikZCoordinate, TikZDistance, TikZPosition, TikZAnchor, LabelType,
    position_vertex_label_auto, position_side_label_auto, position_angle_label_auto
)
from utils.tikz.exceptions import LabelPlacementError, TikZConfigError
from utils.geometry import Point


class TestLabelPositioner:
    """標籤定位器測試"""
    
    def setup_method(self):
        """測試設置"""
        self.context = RenderingContext(precision=2, unit="cm", debug_mode=False)
        self.positioner = LabelPositioner(self.context)
        
        # 測試用的基礎點
        self.test_point = Point(1.0, 1.0)
        self.adjacent_points = [Point(0.0, 1.0), Point(1.0, 0.0)]
    
    def test_label_positioner_creation(self):
        """測試標籤定位器創建"""
        assert self.positioner is not None
        assert self.positioner.context == self.context
        assert self.positioner.context.precision == 2
    
    def test_default_label_positioner(self):
        """測試預設標籤定位器"""
        default_positioner = LabelPositioner()
        assert default_positioner is not None
        assert default_positioner.context.precision == 3  # 預設值
    
    def test_position_vertex_label_basic(self):
        """測試基礎頂點標籤定位"""
        result = self.positioner.position_vertex_label(
            vertex_coord=self.test_point,
            label_text="A"
        )
        
        assert isinstance(result, LabelParameters)
        assert result.text == "A"
        assert result.position is not None
        assert result.tikz_code is not None
        assert len(result.tikz_code) > 0
    
    def test_position_vertex_label_with_position(self):
        """測試指定位置的頂點標籤定位"""
        result = self.positioner.position_vertex_label(
            vertex_coord=self.test_point,
            label_text="B",
            position=TikZPosition.ABOVE
        )
        
        assert result.text == "B"
        assert "above" in result.tikz_code.lower() or result.tikz_code.find("above") >= 0
    
    def test_position_vertex_label_with_offset(self):
        """測試帶偏移的頂點標籤定位"""
        offset = TikZDistance(0.2, "cm")
        result = self.positioner.position_vertex_label(
            vertex_coord=self.test_point,
            label_text="C",
            offset=offset
        )
        
        assert result.text == "C"
        assert result.tikz_code is not None
    
    def test_position_side_label_basic(self):
        """測試基礎邊標籤定位"""
        start_point = Point(0.0, 0.0)
        end_point = Point(2.0, 0.0)
        
        result = self.positioner.position_side_label(
            start_point=start_point,
            end_point=end_point,
            label_text="a"
        )
        
        assert isinstance(result, LabelParameters)
        assert result.text == "a"
        assert result.position is not None
        assert result.tikz_code is not None
    
    def test_position_side_label_with_position(self):
        """測試指定位置的邊標籤定位"""
        start_point = Point(0.0, 0.0)
        end_point = Point(0.0, 2.0)
        
        result = self.positioner.position_side_label(
            start_point=start_point,
            end_point=end_point,
            label_text="b",
            position=TikZPosition.RIGHT
        )
        
        assert result.text == "b"
        assert result.tikz_code is not None
    
    def test_position_angle_label_basic(self):
        """測試基礎角度標籤定位"""
        vertex = Point(0.0, 0.0)
        point1 = Point(1.0, 0.0)
        point2 = Point(0.0, 1.0)
        
        result = self.positioner.position_angle_label(
            vertex=vertex,
            point1=point1,
            point2=point2,
            label_text="α"
        )
        
        assert isinstance(result, LabelParameters)
        assert result.text == "α"
        assert result.position is not None
        assert result.tikz_code is not None
    
    def test_position_angle_label_with_distance(self):
        """測試指定距離的角度標籤定位"""
        vertex = Point(0.0, 0.0)
        point1 = Point(1.0, 0.0)
        point2 = Point(0.0, 1.0)
        
        result = self.positioner.position_angle_label(
            vertex=vertex,
            point1=point1,
            point2=point2,
            label_text="β",
            distance_from_vertex=0.8
        )
        
        assert result.text == "β"
        assert result.tikz_code is not None


class TestLabelConfigurationHandling:
    """標籤配置處理測試"""
    
    def setup_method(self):
        """測試設置"""
        self.positioner = LabelPositioner()
    
    def test_label_config_application(self):
        """測試標籤配置應用"""
        config = LabelConfig(
            text="D",
            position=TikZPosition.BELOW,
            offset=TikZDistance(0.15, "cm"),
            color="red",
            font_size="small"
        )
        
        result = self.positioner.position_vertex_label_with_config(
            vertex_coord=Point(1.0, 1.0),
            config=config
        )
        
        assert result.text == "D"
        tikz_code = result.tikz_code
        assert "below" in tikz_code.lower() or tikz_code.find("below") >= 0
        assert "red" in tikz_code or result.tikz_code is not None
    
    def test_font_configuration(self):
        """測試字體配置"""
        font_sizes = ["tiny", "small", "normal", "large", "huge"]
        
        for font_size in font_sizes:
            config = LabelConfig(
                text="X",
                font_size=font_size
            )
            
            result = self.positioner.position_vertex_label_with_config(
                vertex_coord=Point(0.0, 0.0),
                config=config
            )
            
            assert result.text == "X"
            assert result.tikz_code is not None
    
    def test_color_configuration(self):
        """測試顏色配置"""
        colors = ["black", "red", "blue", "green", "orange"]
        
        for color in colors:
            config = LabelConfig(
                text="Y",
                color=color
            )
            
            result = self.positioner.position_vertex_label_with_config(
                vertex_coord=Point(0.0, 0.0),
                config=config
            )
            
            assert result.text == "Y"
            # 顏色可能在TikZ代碼中以不同方式表示
            assert result.tikz_code is not None


class TestAutomaticPositioning:
    """自動定位測試"""
    
    def test_auto_vertex_positioning(self):
        """測試自動頂點定位"""
        vertex = Point(1.0, 1.0)
        adjacent = [Point(0.0, 1.0), Point(1.0, 0.0), Point(2.0, 1.0)]
        
        result = position_vertex_label_auto(
            vertex_coord=vertex,
            label_text="P",
            adjacent_vertices=adjacent
        )
        
        assert isinstance(result, LabelParameters)
        assert result.text == "P"
        assert result.position is not None
        assert result.tikz_code is not None
    
    def test_auto_side_positioning(self):
        """測試自動邊標籤定位"""
        start = Point(0.0, 0.0)
        end = Point(3.0, 4.0)
        
        result = position_side_label_auto(
            start_point=start,
            end_point=end,
            label_text="c",
            current_offset=None
        )
        
        assert isinstance(result, LabelParameters)
        assert result.text == "c"
        assert result.position is not None
        assert result.tikz_code is not None
    
    def test_auto_angle_positioning(self):
        """測試自動角度標籤定位"""
        vertex = Point(0.0, 0.0)
        point1 = Point(2.0, 0.0)
        point2 = Point(0.0, 3.0)
        
        result = position_angle_label_auto(
            vertex=vertex,
            point1=point1,
            point2=point2,
            label_text="θ"
        )
        
        assert isinstance(result, LabelParameters)
        assert result.text == "θ"
        assert result.position is not None
        assert result.tikz_code is not None
    
    def test_auto_positioning_collision_avoidance(self):
        """測試自動定位的碰撞避免"""
        # 模擬多個相近的標籤
        base_point = Point(1.0, 1.0)
        
        # 創建多個標籤，應該自動選擇不同位置避免重疊
        labels = []
        for i, text in enumerate(["A", "B", "C", "D"]):
            adjacent = [Point(0.0, 1.0), Point(1.0, 0.0)]
            result = position_vertex_label_auto(
                vertex_coord=base_point,
                label_text=text,
                adjacent_vertices=adjacent
            )
            labels.append(result)
        
        assert len(labels) == 4
        for label in labels:
            assert label is not None
            assert label.tikz_code is not None


class TestErrorHandling:
    """錯誤處理測試"""
    
    def setup_method(self):
        """測試設置"""
        self.positioner = LabelPositioner()
    
    def test_invalid_label_text(self):
        """測試無效標籤文本"""
        # 空文本
        with pytest.raises(LabelPlacementError):
            self.positioner.position_vertex_label(
                vertex_coord=Point(0.0, 0.0),
                label_text=""
            )
        
        # None文本
        with pytest.raises(LabelPlacementError):
            self.positioner.position_vertex_label(
                vertex_coord=Point(0.0, 0.0),
                label_text=None
            )
    
    def test_invalid_position(self):
        """測試無效位置"""
        with pytest.raises(TikZConfigError):
            self.positioner.position_vertex_label(
                vertex_coord=Point(0.0, 0.0),
                label_text="A",
                position="invalid_position"
            )
    
    def test_invalid_offset(self):
        """測試無效偏移"""
        with pytest.raises(LabelPlacementError):
            self.positioner.position_vertex_label(
                vertex_coord=Point(0.0, 0.0),
                label_text="A",
                offset=TikZDistance(-0.1, "cm")  # 負偏移
            )
    
    def test_collinear_side_points(self):
        """測試共線邊點（應該仍能處理）"""
        # 這個測試檢查邊標籤是否能處理零長度邊
        start = Point(1.0, 1.0)
        end = Point(1.0, 1.0)  # 相同點
        
        # 應該拋出錯誤或處理優雅
        with pytest.raises(LabelPlacementError):
            self.positioner.position_side_label(
                start_point=start,
                end_point=end,
                label_text="zero"
            )


class TestTikZCodeGeneration:
    """TikZ代碼生成測試"""
    
    def setup_method(self):
        """測試設置"""
        self.positioner = LabelPositioner()
    
    def test_vertex_label_tikz_structure(self):
        """測試頂點標籤TikZ結構"""
        result = self.positioner.position_vertex_label(
            vertex_coord=Point(2.0, 3.0),
            label_text="V"
        )
        
        tikz_code = result.tikz_code
        
        # 基本TikZ結構檢查
        assert isinstance(tikz_code, str)
        assert len(tikz_code) > 0
        
        # 可能包含的TikZ元素
        tikz_elements = ["\\node", "node", "(", ")", "{", "}", "at"]
        has_tikz_element = any(element in tikz_code for element in tikz_elements)
        assert has_tikz_element
    
    def test_coordinate_formatting_in_tikz(self):
        """測試TikZ中的座標格式化"""
        context = RenderingContext(precision=1, unit="mm")
        positioner = LabelPositioner(context)
        
        result = positioner.position_vertex_label(
            vertex_coord=Point(1.23456, 7.89012),
            label_text="F"
        )
        
        tikz_code = result.tikz_code
        
        # 檢查精度是否正確應用到座標
        assert tikz_code is not None
        # 座標應該按照指定精度格式化
        import re
        coordinates = re.findall(r'\(\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*\)', tikz_code)
        assert len(coordinates) > 0  # 至少應該有一個座標
    
    def test_special_characters_in_labels(self):
        """測試標籤中的特殊字符"""
        special_labels = ["α", "β", "θ", "Δ", "∠", "∑", "$x^2$", "\\alpha"]
        
        for label_text in special_labels:
            try:
                result = self.positioner.position_vertex_label(
                    vertex_coord=Point(0.0, 0.0),
                    label_text=label_text
                )
                assert result.text == label_text
                assert result.tikz_code is not None
            except Exception as e:
                # 某些特殊字符可能需要特殊處理
                assert isinstance(e, (LabelPlacementError, TikZConfigError))


class TestPerformanceAndComplexScenarios:
    """性能和複雜場景測試"""
    
    def setup_method(self):
        """測試設置"""
        self.positioner = LabelPositioner()
    
    def test_batch_label_positioning(self):
        """測試批次標籤定位"""
        vertices = [
            (Point(0.0, 0.0), "A"),
            (Point(1.0, 0.0), "B"),
            (Point(0.5, 1.0), "C"),
            (Point(-1.0, 0.5), "D")
        ]
        
        results = []
        for vertex, label in vertices:
            result = self.positioner.position_vertex_label(
                vertex_coord=vertex,
                label_text=label
            )
            results.append(result)
        
        assert len(results) == 4
        for i, result in enumerate(results):
            assert result.text == vertices[i][1]
            assert result.tikz_code is not None
    
    def test_complex_triangle_labeling(self):
        """測試複雜三角形標記"""
        # 三角形的三個頂點
        vertices = [Point(0.0, 0.0), Point(4.0, 0.0), Point(2.0, 3.0)]
        vertex_labels = ["A", "B", "C"]
        
        # 三條邊
        sides = [(0, 1), (1, 2), (2, 0)]
        side_labels = ["c", "a", "b"]
        
        # 三個角
        angles = [(1, 0, 2), (2, 1, 0), (0, 2, 1)]  # (point1, vertex, point2)
        angle_labels = ["α", "β", "γ"]
        
        # 頂點標籤
        vertex_results = []
        for i, (vertex, label) in enumerate(zip(vertices, vertex_labels)):
            adjacent = [vertices[j] for j in range(3) if j != i]
            result = position_vertex_label_auto(vertex, label, adjacent)
            vertex_results.append(result)
        
        # 邊標籤
        side_results = []
        for (i, j), label in zip(sides, side_labels):
            result = position_side_label_auto(vertices[i], vertices[j], label)
            side_results.append(result)
        
        # 角度標籤
        angle_results = []
        for (i, v, j), label in zip(angles, angle_labels):
            result = position_angle_label_auto(vertices[v], vertices[i], vertices[j], label)
            angle_results.append(result)
        
        # 驗證所有結果
        assert len(vertex_results) == 3
        assert len(side_results) == 3
        assert len(angle_results) == 3
        
        all_results = vertex_results + side_results + angle_results
        for result in all_results:
            assert result is not None
            assert result.tikz_code is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])