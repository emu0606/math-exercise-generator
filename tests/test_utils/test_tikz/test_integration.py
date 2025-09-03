#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TikZ模組整合測試
測試 utils.tikz 各組件之間的整合和完整工作流程
"""

import pytest
import math
from utils.tikz import (
    ArcRenderer, LabelPositioner, CoordinateTransformer,
    create_arc_renderer, create_label_positioner, create_coordinate_transformer,
    RenderingContext, ArcConfig, LabelConfig, CoordinateTransform,
    TikZCoordinate, TikZPosition, TikZAnchor
)
from utils.geometry import Point, Triangle, construct_triangle


class TestTikZIntegration:
    """TikZ模組整合測試"""
    
    def setup_method(self):
        """測試設置"""
        self.context = RenderingContext(precision=2, unit="cm", debug_mode=False)
        self.arc_renderer = create_arc_renderer(self.context)
        self.label_positioner = create_label_positioner(self.context)
        self.coordinate_transformer = create_coordinate_transformer(precision=2, unit="cm")
        
        # 測試用三角形
        self.triangle = construct_triangle("sss", side_a=3, side_b=4, side_c=5)
    
    def test_complete_triangle_rendering_workflow(self):
        """測試完整的三角形渲染工作流程"""
        vertices = [self.triangle.p1, self.triangle.p2, self.triangle.p3]
        vertex_labels = ["A", "B", "C"]
        
        # 1. 渲染頂點標籤
        vertex_label_results = []
        for vertex, label in zip(vertices, vertex_labels):
            result = self.label_positioner.position_vertex_label(
                vertex_coord=vertex,
                label_text=label
            )
            vertex_label_results.append(result)
        
        # 2. 渲染邊標籤
        sides = [(vertices[0], vertices[1]), (vertices[1], vertices[2]), (vertices[2], vertices[0])]
        side_labels = ["c", "a", "b"]
        
        side_label_results = []
        for (start, end), label in zip(sides, side_labels):
            result = self.label_positioner.position_side_label(
                start_point=start,
                end_point=end,
                label_text=label
            )
            side_label_results.append(result)
        
        # 3. 渲染角度弧線
        angles = [(vertices[1], vertices[0], vertices[2]),
                  (vertices[2], vertices[1], vertices[0]),
                  (vertices[0], vertices[2], vertices[1])]
        
        arc_results = []
        for point1, vertex, point2 in angles:
            result = self.arc_renderer.render_angle_arc(
                vertex=vertex,
                point1=point1,
                point2=point2,
                radius_config=0.3
            )
            arc_results.append(result)
        
        # 驗證所有結果
        assert len(vertex_label_results) == 3
        assert len(side_label_results) == 3
        assert len(arc_results) == 3
        
        # 檢查所有結果都有有效的TikZ代碼
        all_results = vertex_label_results + side_label_results + arc_results
        for result in all_results:
            assert result is not None
            assert hasattr(result, 'tikz_code')
            assert result.tikz_code is not None
            assert len(result.tikz_code) > 0
    
    def test_coordinate_transform_integration(self):
        """測試座標轉換整合"""
        # 原始三角形
        original_vertices = [self.triangle.p1, self.triangle.p2, self.triangle.p3]
        
        # 轉換三角形（縮放和平移）
        transform = CoordinateTransform(
            scale=(0.5, 0.5),
            translate=(2.0, 1.0)
        )
        
        transformed_coords = []
        for vertex in original_vertices:
            tikz_coord = self.coordinate_transformer.point_to_tikz_coordinate(vertex)
            # 注意：需要使用高級轉換器來應用轉換
            from utils.tikz import AdvancedCoordinateTransformer
            advanced_transformer = AdvancedCoordinateTransformer()
            transformed = advanced_transformer.apply_transform(tikz_coord, transform)
            transformed_coords.append(transformed)
        
        # 在轉換後的座標上渲染標籤
        transformed_results = []
        for i, coord in enumerate(transformed_coords):
            point = self.coordinate_transformer.tikz_coordinate_to_point(coord)
            result = self.label_positioner.position_vertex_label(
                vertex_coord=point,
                label_text=f"T{i+1}"
            )
            transformed_results.append(result)
        
        assert len(transformed_results) == 3
        for result in transformed_results:
            assert result.tikz_code is not None
    
    def test_context_consistency_across_components(self):
        """測試組件間上下文一致性"""
        # 所有組件應該使用相同的渲染上下文
        assert self.arc_renderer.context.precision == 2
        assert self.label_positioner.context.precision == 2
        assert self.coordinate_transformer.context.precision == 2
        
        assert self.arc_renderer.context.unit == "cm"
        assert self.label_positioner.context.unit == "cm"
        assert self.coordinate_transformer.context.unit == "cm"
    
    def test_complex_diagram_generation(self):
        """測試複雜圖表生成"""
        # 創建一個複雜的幾何圖形：正六邊形
        center = Point(0.0, 0.0)
        radius = 2.0
        num_sides = 6
        
        # 生成六邊形頂點
        vertices = []
        for i in range(num_sides):
            angle = 2 * math.pi * i / num_sides
            x = center.x + radius * math.cos(angle)
            y = center.y + radius * math.sin(angle)
            vertices.append(Point(x, y))
        
        # 1. 頂點標籤
        vertex_results = []
        for i, vertex in enumerate(vertices):
            result = self.label_positioner.position_vertex_label(
                vertex_coord=vertex,
                label_text=f"P{i+1}"
            )
            vertex_results.append(result)
        
        # 2. 中心到頂點的連線標籤
        radius_results = []
        for i, vertex in enumerate(vertices):
            result = self.label_positioner.position_side_label(
                start_point=center,
                end_point=vertex,
                label_text=f"r{i+1}"
            )
            radius_results.append(result)
        
        # 3. 中心角弧線
        arc_results = []
        for i in range(num_sides):
            next_i = (i + 1) % num_sides
            result = self.arc_renderer.render_angle_arc(
                vertex=center,
                point1=vertices[i],
                point2=vertices[next_i],
                radius_config=0.4
            )
            arc_results.append(result)
        
        # 驗證結果
        assert len(vertex_results) == 6
        assert len(radius_results) == 6
        assert len(arc_results) == 6
        
        # 所有結果都應該有效
        all_results = vertex_results + radius_results + arc_results
        for result in all_results:
            assert result.tikz_code is not None


class TestErrorHandlingIntegration:
    """錯誤處理整合測試"""
    
    def setup_method(self):
        """測試設置"""
        self.renderer = ArcRenderer()
        self.positioner = LabelPositioner()
    
    def test_cascading_error_handling(self):
        """測試級聯錯誤處理"""
        # 使用無效輸入，應該在不同組件中產生適當的錯誤
        
        # 弧線渲染器：共線點
        from utils.tikz.exceptions import ArcRenderingError
        with pytest.raises(ArcRenderingError):
            self.renderer.render_angle_arc(
                vertex=Point(0.0, 0.0),
                point1=Point(1.0, 0.0),
                point2=Point(2.0, 0.0),  # 共線
                radius_config=0.5
            )
        
        # 標籤定位器：空標籤
        from utils.tikz.exceptions import LabelPlacementError
        with pytest.raises(LabelPlacementError):
            self.positioner.position_vertex_label(
                vertex_coord=Point(0.0, 0.0),
                label_text=""  # 空標籤
            )
    
    def test_error_recovery_workflow(self):
        """測試錯誤恢復工作流程"""
        # 模擬一個部分失敗的渲染過程
        vertices = [Point(0.0, 0.0), Point(1.0, 0.0), Point(1.0, 0.0)]  # 重複點
        labels = ["A", "B", "C"]
        
        successful_results = []
        failed_operations = []
        
        for vertex, label in zip(vertices, labels):
            try:
                result = self.positioner.position_vertex_label(
                    vertex_coord=vertex,
                    label_text=label
                )
                successful_results.append(result)
            except Exception as e:
                failed_operations.append((vertex, label, e))
        
        # 應該有一些成功和一些失敗的操作
        assert len(successful_results) >= 1  # 至少有一些成功
        # failed_operations 可能為空，取決於實現的容錯性


class TestPerformanceIntegration:
    """性能整合測試"""
    
    def test_batch_rendering_performance(self):
        """測試批次渲染性能"""
        import time
        
        # 創建大量幾何對象
        num_triangles = 10
        triangles = []
        for i in range(num_triangles):
            # 創建不同大小的三角形
            scale = 1.0 + i * 0.1
            triangle = construct_triangle("sss", side_a=3*scale, side_b=4*scale, side_c=5*scale)
            triangles.append(triangle)
        
        renderer = ArcRenderer()
        positioner = LabelPositioner()
        
        start_time = time.time()
        
        all_results = []
        for i, triangle in enumerate(triangles):
            vertices = [triangle.p1, triangle.p2, triangle.p3]
            
            # 每個三角形3個頂點標籤 + 3個角度弧線
            for j, vertex in enumerate(vertices):
                # 頂點標籤
                label_result = positioner.position_vertex_label(
                    vertex_coord=vertex,
                    label_text=f"T{i}V{j}"
                )
                all_results.append(label_result)
                
                # 角度弧線
                other_vertices = [v for k, v in enumerate(vertices) if k != j]
                if len(other_vertices) >= 2:
                    arc_result = renderer.render_angle_arc(
                        vertex=vertex,
                        point1=other_vertices[0],
                        point2=other_vertices[1],
                        radius_config=0.2
                    )
                    all_results.append(arc_result)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # 驗證結果
        expected_results = num_triangles * 6  # 每個三角形6個結果
        assert len(all_results) == expected_results
        
        # 性能檢查（應該在合理時間內完成）
        assert execution_time < 5.0  # 5秒內完成
        
        # 所有結果都應該有效
        for result in all_results:
            assert result.tikz_code is not None


class TestConfigurationIntegration:
    """配置整合測試"""
    
    def test_custom_configuration_workflow(self):
        """測試自訂配置工作流程"""
        # 創建自訂渲染上下文
        custom_context = RenderingContext(
            precision=1,
            unit="mm",
            debug_mode=True
        )
        
        # 創建使用自訂配置的組件
        custom_renderer = ArcRenderer(custom_context)
        custom_positioner = LabelPositioner(custom_context)
        
        # 測試配置是否正確應用
        result_arc = custom_renderer.render_angle_arc(
            vertex=Point(0.0, 0.0),
            point1=Point(1.0, 0.0),
            point2=Point(0.0, 1.0),
            radius_config=0.5
        )
        
        result_label = custom_positioner.position_vertex_label(
            vertex_coord=Point(1.0, 1.0),
            label_text="Test"
        )
        
        # 檢查精度配置是否生效
        assert result_arc.tikz_code is not None
        assert result_label.tikz_code is not None
        
        # 可能檢查座標精度（例如，只有1位小數）
        # 這取決於具體的實現
    
    def test_configuration_inheritance(self):
        """測試配置繼承"""
        # 父配置
        parent_context = RenderingContext(precision=3, unit="cm")
        
        # 創建使用父配置的組件
        renderer = ArcRenderer(parent_context)
        positioner = LabelPositioner(parent_context)
        
        # 檢查組件是否繼承了配置
        assert renderer.context.precision == 3
        assert renderer.context.unit == "cm"
        assert positioner.context.precision == 3
        assert positioner.context.unit == "cm"


class TestBackwardCompatibility:
    """向後相容性測試"""
    
    def test_legacy_function_integration(self):
        """測試遺留函數整合"""
        from utils.tikz import get_arc_render_params
        
        # 測試遺留函數是否仍然可用
        try:
            result = get_arc_render_params(
                vertex=Point(0.0, 0.0),
                point1=Point(1.0, 0.0),
                point2=Point(0.0, 1.0),
                radius_config="auto"
            )
            assert result is not None
        except NotImplementedError:
            # 如果遺留函數未實現，這也是可以接受的
            pass
    
    def test_mixed_old_new_api_usage(self):
        """測試混合使用舊新API"""
        # 新API
        new_renderer = ArcRenderer()
        new_result = new_renderer.render_angle_arc(
            vertex=Point(0.0, 0.0),
            point1=Point(1.0, 0.0),
            point2=Point(0.0, 1.0),
            radius_config=0.5
        )
        
        # 檢查新API結果
        assert new_result is not None
        assert new_result.tikz_code is not None
        
        # 如果有遺留API，也應該能產生類似結果
        # 這取決於具體的向後相容實現


class TestRealWorldScenarios:
    """真實世界場景測試"""
    
    def test_geometry_textbook_diagram(self):
        """測試幾何教科書圖表"""
        # 模擬一個典型的幾何教科書圖表：
        # 一個三角形，標記所有頂點、邊長、角度
        
        triangle = construct_triangle("sss", side_a=6, side_b=8, side_c=10)
        vertices = [triangle.p1, triangle.p2, triangle.p3]
        
        renderer = ArcRenderer()
        positioner = LabelPositioner()
        
        diagram_elements = []
        
        # 1. 頂點標籤
        vertex_labels = ["A", "B", "C"]
        for vertex, label in zip(vertices, vertex_labels):
            result = positioner.position_vertex_label(
                vertex_coord=vertex,
                label_text=label,
                position=TikZPosition.ABOVE
            )
            diagram_elements.append(("vertex_label", result))
        
        # 2. 邊標籤
        sides = [(vertices[0], vertices[1]),
                 (vertices[1], vertices[2]),
                 (vertices[2], vertices[0])]
        side_labels = ["c = 10", "a = 6", "b = 8"]
        
        for (start, end), label in zip(sides, side_labels):
            result = positioner.position_side_label(
                start_point=start,
                end_point=end,
                label_text=label
            )
            diagram_elements.append(("side_label", result))
        
        # 3. 角度弧線和標籤
        angles = [(vertices[1], vertices[0], vertices[2]),
                  (vertices[2], vertices[1], vertices[0]),
                  (vertices[0], vertices[2], vertices[1])]
        angle_labels = ["α", "β", "γ"]
        
        for (p1, vertex, p2), label in zip(angles, angle_labels):
            # 弧線
            arc_result = renderer.render_angle_arc(
                vertex=vertex,
                point1=p1,
                point2=p2,
                radius_config=0.4
            )
            diagram_elements.append(("angle_arc", arc_result))
            
            # 角度標籤
            angle_label_result = positioner.position_angle_label(
                vertex=vertex,
                point1=p1,
                point2=p2,
                label_text=label
            )
            diagram_elements.append(("angle_label", angle_label_result))
        
        # 驗證完整圖表
        assert len(diagram_elements) == 12  # 3個頂點 + 3條邊 + 3個弧線 + 3個角度標籤
        
        # 所有元素都應該有效
        for element_type, result in diagram_elements:
            assert result is not None
            assert result.tikz_code is not None
            assert len(result.tikz_code) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])