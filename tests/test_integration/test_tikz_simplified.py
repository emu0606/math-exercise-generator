#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
簡化的TikZ測試：只測試實際存在的API和核心功能
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# 編碼安全設置
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8') 
    except:
        pass

def test_tikz_core_functionality():
    """測試TikZ核心功能"""
    print("Testing TikZ core functionality...")
    
    from utils.tikz import ArcRenderer
    from utils.geometry.types import Point
    
    # 創建弧線渲染器
    renderer = ArcRenderer()
    assert renderer is not None
    print("ArcRenderer created successfully")
    
    # 測試基本角度弧線渲染
    vertex = Point(0.0, 0.0)
    point1 = Point(1.0, 0.0) 
    point2 = Point(0.0, 1.0)
    
    result = renderer.render_angle_arc(
        vertex=vertex,
        point1=point1,
        point2=point2,
        radius_config=0.3
    )
    
    assert result is not None
    assert hasattr(result, 'center')
    assert hasattr(result, 'radius') 
    assert hasattr(result, 'tikz_code')
    assert result.radius == 0.3
    print(f"Angle arc rendered: radius={result.radius}, code_length={len(result.tikz_code)}")

def test_tikz_coordinate_functions():
    """測試TikZ座標轉換函數"""
    print("\nTesting TikZ coordinate functions...")
    
    from utils.tikz import tikz_coordinate, tikz_angle_degrees
    from utils.geometry.types import Point
    
    # 測試座標格式化
    point = Point(1.234, 5.678)
    tikz_coord = tikz_coordinate(point, precision=2)
    assert isinstance(tikz_coord, str)
    print(f"Point {point} -> TikZ: {tikz_coord}")
    
    # 測試角度轉換
    angle_rad = 1.5708  # π/2
    angle_deg = tikz_angle_degrees(angle_rad)
    assert abs(angle_deg - 90.0) < 0.1
    print(f"Angle {angle_rad} rad -> {angle_deg} degrees")

def test_tikz_types_and_configs():
    """測試TikZ類型和配置"""
    print("\nTesting TikZ types and configurations...")
    
    from utils.tikz.types import ArcConfig, ArcType
    
    # 測試基本配置
    config1 = ArcConfig(radius=0.5)
    assert config1.radius == 0.5
    print("Basic ArcConfig created")
    
    # 測試帶樣式選項的配置
    config2 = ArcConfig(
        radius=0.8,
        style_options={"color": "blue", "line_width": "thick"}
    )
    assert config2.radius == 0.8
    assert config2.style_options["color"] == "blue"
    print("ArcConfig with style options created")

def test_tikz_label_positioning():
    """測試TikZ標籤定位功能"""
    print("\nTesting TikZ label positioning...")
    
    from utils.tikz import position_vertex_label_auto, position_side_label_auto
    from utils.geometry.types import Point
    
    # 測試頂點標籤定位
    vertex = Point(1.0, 1.0)
    adjacent_vertices = [Point(0.0, 0.0), Point(2.0, 0.0)]
    
    label_params = position_vertex_label_auto(vertex, adjacent_vertices, offset=0.2)
    
    assert hasattr(label_params, 'position')
    assert hasattr(label_params, 'tikz_anchor')
    assert hasattr(label_params, 'rotation_angle')
    print(f"Vertex label positioned at: {label_params.position}")
    
    # 測試邊標籤定位
    side_start = Point(0.0, 0.0)
    side_end = Point(2.0, 0.0)
    all_vertices = (Point(0.0, 0.0), Point(2.0, 0.0), Point(1.0, 1.0))
    
    side_label_params = position_side_label_auto(side_start, side_end, all_vertices, offset=0.2)
    
    assert hasattr(side_label_params, 'position')
    print(f"Side label positioned at: {side_label_params.position}")

def test_tikz_integration_with_geometry():
    """測試TikZ與幾何模組的集成"""
    print("\nTesting TikZ integration with geometry...")
    
    from utils import construct_triangle, get_centroid
    from utils.tikz import ArcRenderer
    
    # 構造三角形
    triangle = construct_triangle('sss', side_a=3, side_b=4, side_c=5)
    vertices = [triangle.p1, triangle.p2, triangle.p3]
    
    # 計算質心
    centroid = get_centroid(triangle)
    print(f"Triangle centroid: ({centroid.x:.3f}, {centroid.y:.3f})")
    
    # 為每個角渲染弧線
    renderer = ArcRenderer()
    
    for i in range(3):
        vertex = vertices[i]
        point1 = vertices[(i+1) % 3] 
        point2 = vertices[(i+2) % 3]
        
        arc_result = renderer.render_angle_arc(
            vertex=vertex,
            point1=point1, 
            point2=point2,
            radius_config=0.2
        )
        
        assert arc_result is not None
        print(f"  Angle {i+1}: radius={arc_result.radius:.3f}, TikZ length={len(arc_result.tikz_code)}")

def main():
    """主測試函數"""
    print("=" * 50)
    print("SIMPLIFIED TIKZ FUNCTIONALITY TESTS")
    print("=" * 50)
    
    try:
        test_tikz_core_functionality()
        test_tikz_coordinate_functions() 
        test_tikz_types_and_configs()
        test_tikz_label_positioning()
        test_tikz_integration_with_geometry()
        
        print("\n" + "=" * 50)
        print("ALL SIMPLIFIED TIKZ TESTS PASSED!")
        print("Core TikZ functionality is working correctly:")
        print("  ✓ Arc rendering")
        print("  ✓ Coordinate transformation") 
        print("  ✓ Configuration management")
        print("  ✓ Label positioning")
        print("  ✓ Integration with geometry module")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"\nSIMPLIFIED TIKZ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)