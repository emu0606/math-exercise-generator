#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
简化集成测试：predefined_triangle.py 与新 utils 架构集成
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def test_new_utils_api():
    """测试新utils API的使用"""
    print("Testing new utils API...")
    
    from utils import construct_triangle, get_centroid, distance, Point, Triangle
    
    # 测试三角形构造
    triangle = construct_triangle('sss', side_a=3, side_b=4, side_c=5)
    assert isinstance(triangle, Triangle)
    print("Triangle construction OK")
    
    # 测试特殊点计算
    centroid = get_centroid(triangle)
    assert isinstance(centroid, Point)
    print(f"Centroid: ({centroid.x:.3f}, {centroid.y:.3f})")
    
    # 测试距离计算
    dist = distance((0, 0), (3, 4))
    assert abs(dist - 5.0) < 1e-10
    print(f"Distance calculation: {dist}")
    
    print("New utils API test PASSED")

def test_arc_renderer():
    """测试弧线渲染器"""
    print("\nTesting arc renderer...")
    
    from utils.tikz import ArcRenderer
    
    renderer = ArcRenderer()
    arc_params = renderer.render_angle_arc(
        vertex=(0, 0),
        point1=(1, 0),
        point2=(0, 1),
        radius_config="auto"
    )
    
    assert hasattr(arc_params, 'center')
    assert hasattr(arc_params, 'radius')
    print(f"Arc center: {arc_params.center}, radius: {arc_params.radius}")
    
    print("Arc renderer test PASSED")

def test_predefined_triangle_basic():
    """测试predefined_triangle基本功能"""
    print("\nTesting predefined_triangle basic generation...")
    
    from figures.predefined.predefined_triangle import PredefinedTriangleGenerator
    
    generator = PredefinedTriangleGenerator()
    
    params = {
        'definition_mode': 'sss',
        'side_a': 3.0,
        'side_b': 4.0,
        'side_c': 5.0,
        'variant': 'question',
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
    
    tikz_result = generator.generate_tikz(params)
    
    assert isinstance(tikz_result, str)
    assert len(tikz_result) > 0
    assert "filldraw" in tikz_result
    assert not tikz_result.startswith("% Error")
    
    print(f"TikZ generation successful: {len(tikz_result)} characters")
    print("Predefined triangle test PASSED")

def test_comprehensive_integration():
    """综合集成测试"""
    print("\nTesting comprehensive integration...")
    
    from figures.predefined.predefined_triangle import PredefinedTriangleGenerator
    
    generator = PredefinedTriangleGenerator()
    
    params = {
        'definition_mode': 'sss',
        'side_a': 5.0,
        'side_b': 12.0,
        'side_c': 13.0,
        'variant': 'question',
        
        'vertex_p1_display_config': {'show_point': True, 'show_label': True},
        'vertex_p2_display_config': {'show_point': True, 'show_label': True},
        'vertex_p3_display_config': {'show_point': True, 'show_label': True},
        
        'side_p1p2_display_config': {'show_label': True, 'label_text_type': 'length'},
        'side_p2p3_display_config': {'show_label': True, 'label_text_type': 'length'},
        
        'angle_at_p1_display_config': {'show_arc': True, 'show_label': True},
        
        'display_centroid': {'show_point': True, 'show_label': True}
    }
    
    tikz_result = generator.generate_tikz(params)
    
    assert not tikz_result.startswith("% Error")
    assert len(tikz_result) > 200
    assert tikz_result.count("filldraw") >= 4  # 3 vertices + 1 special point
    
    print(f"Comprehensive test successful: {len(tikz_result)} characters")
    print("Generated content includes:")
    print(f"  - Points (filldraw): {tikz_result.count('filldraw')}")
    print(f"  - Labels (node): {tikz_result.count('node')}")
    print(f"  - Arcs: {tikz_result.count('arc')}")
    
    print("Comprehensive integration test PASSED")

if __name__ == "__main__":
    try:
        test_new_utils_api()
        test_arc_renderer()
        test_predefined_triangle_basic()
        test_comprehensive_integration()
        
        print("\n" + "="*50)
        print("ALL INTEGRATION TESTS PASSED!")
        print("predefined_triangle.py works correctly with new architecture")
        print("="*50)
        
    except Exception as e:
        print(f"\nINTEGRATION TEST FAILED: {e}")
        import traceback
        traceback.print_exc()