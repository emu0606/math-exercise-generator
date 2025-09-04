#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
集成測試：predefined_triangle.py 與新 utils 架構的完整集成測試
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from figures.predefined.predefined_triangle import PredefinedTriangleGenerator
from utils import construct_triangle, get_centroid, distance, Point, Triangle
from utils.tikz import ArcRenderer


class TestPredefinedTriangleIntegration:
    """
    測試 predefined_triangle.py 與新 utils 架構的完整集成
    """
    
    def setup_method(self):
        """設置測試"""
        self.generator = PredefinedTriangleGenerator()
    
    def test_basic_sss_triangle_generation(self):
        """測試基本SSS三角形生成"""
        params = {
            'definition_mode': 'sss',
            'side_a': 3.0,
            'side_b': 4.0,
            'side_c': 5.0,
            'variant': 'standard',
            'vertex_p1_display_config': {
                'show_point': True,
                'show_label': True
            },
            'vertex_p2_display_config': {
                'show_point': True,
                'show_label': True
            },
            'vertex_p3_display_config': {
                'show_point': True,
                'show_label': True
            }
        }
        
        # 測試TikZ生成不報錯
        tikz_result = self.generator.generate_tikz(params)
        
        # 基本驗證
        assert isinstance(tikz_result, str)
        assert len(tikz_result) > 0
        assert "filldraw" in tikz_result  # 應該包含點繪製
        assert not tikz_result.startswith("% Error")  # 不應該有錯誤
        
        print("SUCCESS: SSS triangle generation")
        print(f"TikZ length: {len(tikz_result)} characters")
    
    def test_triangle_with_special_points(self):
        """測試包含特殊點的三角形生成"""
        params = {
            'definition_mode': 'sss',
            'side_a': 4.0,
            'side_b': 5.0,
            'side_c': 6.0,
            'variant': 'standard',
            'display_centroid': {
                'show_point': True,
                'show_label': True
            },
            'display_incenter': {
                'show_point': True,
                'show_label': True
            }
        }
        
        tikz_result = self.generator.generate_tikz(params)
        
        # 驗證特殊點被包含
        assert "darkgray" in tikz_result or "circle" in tikz_result  # 特殊點樣式
        assert not tikz_result.startswith("% Error")
        
        print("✅ 特殊點三角形生成成功")
    
    def test_triangle_with_labels_and_arcs(self):
        """測試包含標籤和角弧的完整三角形"""
        params = {
            'definition_mode': 'sss',
            'side_a': 3.0,
            'side_b': 4.0,
            'side_c': 5.0,
            'variant': 'standard',
            'side_p1p2_display_config': {
                'show_label': True,
                'label_text_type': 'length'
            },
            'side_p2p3_display_config': {
                'show_label': True,
                'label_text_type': 'default_name'
            },
            'angle_at_p1_display_config': {
                'show_arc': True,
                'show_label': True,
                'label_text_type': 'value'
            }
        }
        
        tikz_result = self.generator.generate_tikz(params)
        
        # 驗證包含標籤和弧線
        assert "node" in tikz_result  # 標籤
        assert "arc" in tikz_result   # 角弧
        assert not tikz_result.startswith("% Error")
        
        print("✅ 完整標籤和角弧三角形生成成功")
    
    def test_coordinate_mode_triangle(self):
        """測試坐標模式三角形"""
        params = {
            'definition_mode': 'coordinates',
            'p1': (0, 0),
            'p2': (3, 0),
            'p3': (1.5, 2),
            'variant': 'standard',
            'vertex_p1_display_config': {
                'show_point': True,
                'show_label': True
            }
        }
        
        tikz_result = self.generator.generate_tikz(params)
        
        assert not tikz_result.startswith("% Error")
        assert "filldraw" in tikz_result
        
        print("✅ 坐標模式三角形生成成功")
    
    def test_new_utils_api_direct_usage(self):
        """直接測試新utils API的使用"""
        # 測試三角形構造
        triangle = construct_triangle('sss', side_a=3, side_b=4, side_c=5)
        assert isinstance(triangle, Triangle)
        
        # 測試特殊點計算
        centroid = get_centroid(triangle)
        assert isinstance(centroid, Point)
        
        # 測試距離計算
        dist = distance((0, 0), (3, 4))
        assert abs(dist - 5.0) < 1e-10
        
        print("✅ 新utils API直接使用正常")
    
    def test_arc_renderer_integration(self):
        """測試弧線渲染器集成"""
        renderer = ArcRenderer()
        
        # 測試角度弧渲染
        arc_params = renderer.render_angle_arc(
            vertex=(0, 0),
            point1=(1, 0),
            point2=(0, 1),
            radius_config="auto"
        )
        
        # 驗證返回參數
        assert hasattr(arc_params, 'center')
        assert hasattr(arc_params, 'radius')
        assert hasattr(arc_params, 'start_angle')
        assert hasattr(arc_params, 'end_angle')
        
        print("✅ 弧線渲染器集成正常")
    
    def test_error_handling(self):
        """測試錯誤處理"""
        # 測試無效三角形參數
        params = {
            'definition_mode': 'sss',
            'side_a': 1.0,
            'side_b': 1.0,
            'side_c': 10.0,  # 違反三角形不等式
            'variant': 'standard'
        }
        
        tikz_result = self.generator.generate_tikz(params)
        
        # 應該包含錯誤信息而不是崩潰
        assert "Error generating triangle vertices" in tikz_result
        
        print("✅ 錯誤處理正常")
    
    def test_comprehensive_integration(self):
        """綜合集成測試：完整工作流程"""
        params = {
            'definition_mode': 'sss',
            'side_a': 5.0,
            'side_b': 12.0,
            'side_c': 13.0,  # 5-12-13直角三角形
            'variant': 'standard',
            
            # 頂點顯示
            'vertex_p1_display_config': {'show_point': True, 'show_label': True},
            'vertex_p2_display_config': {'show_point': True, 'show_label': True},
            'vertex_p3_display_config': {'show_point': True, 'show_label': True},
            
            # 邊標籤
            'side_p1p2_display_config': {'show_label': True, 'label_text_type': 'length'},
            'side_p2p3_display_config': {'show_label': True, 'label_text_type': 'length'},
            'side_p3p1_display_config': {'show_label': True, 'label_text_type': 'length'},
            
            # 角度標記
            'angle_at_p1_display_config': {'show_arc': True, 'show_label': True},
            'angle_at_p2_display_config': {'show_arc': True, 'show_label': True},
            'angle_at_p3_display_config': {'show_arc': True, 'show_label': True},
            
            # 特殊點
            'display_centroid': {'show_point': True, 'show_label': True},
            'display_incenter': {'show_point': True, 'show_label': True}
        }
        
        tikz_result = self.generator.generate_tikz(params)
        
        # 全面驗證
        assert not tikz_result.startswith("% Error")
        assert len(tikz_result) > 500  # 複雜圖形應該有足夠內容
        assert tikz_result.count("filldraw") >= 5  # 3個頂點 + 2個特殊點
        assert tikz_result.count("node") >= 8  # 多個標籤
        assert tikz_result.count("arc") >= 3  # 3個角弧
        
        print("✅ 綜合集成測試成功")
        print(f"完整TikZ內容: {len(tikz_result)} 字符")
        
        # 輸出部分內容供檢查
        lines = tikz_result.split('\n')[:10]
        print("TikZ前10行內容:")
        for i, line in enumerate(lines, 1):
            print(f"  {i:2d}: {line}")


if __name__ == "__main__":
    # 直接運行測試
    test_instance = TestPredefinedTriangleIntegration()
    test_instance.setup_method()
    
    try:
        test_instance.test_new_utils_api_direct_usage()
        test_instance.test_arc_renderer_integration()
        test_instance.test_basic_sss_triangle_generation()
        test_instance.test_triangle_with_special_points()
        test_instance.test_triangle_with_labels_and_arcs()
        test_instance.test_coordinate_mode_triangle()
        test_instance.test_error_handling()
        test_instance.test_comprehensive_integration()
        
        print("\n🎉 所有predefined_triangle.py集成測試通過！")
        
    except Exception as e:
        print(f"\n❌ 集成測試失敗: {e}")
        import traceback
        traceback.print_exc()