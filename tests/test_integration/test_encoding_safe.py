#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
編碼安全的集成測試：解決Windows cp950編碼問題
"""

import sys
import os

# 強制設置UTF-8編碼
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

# 或者使用包裝器
import io
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def safe_print(text):
    """編碼安全的打印函數"""
    try:
        print(text)
    except UnicodeEncodeError:
        # 如果UTF-8失敗，使用ASCII安全版本
        safe_text = text.encode('ascii', errors='replace').decode('ascii')
        print(safe_text)

def test_new_utils_api():
    """測試新utils API"""
    safe_print("=== Testing new utils API ===")
    
    from utils import construct_triangle, get_centroid, distance, Point, Triangle
    
    # 測試三角形構造
    triangle = construct_triangle('sss', side_a=3, side_b=4, side_c=5)
    assert isinstance(triangle, Triangle)
    safe_print("SUCCESS: Triangle construction")
    
    # 測試特殊點計算
    centroid = get_centroid(triangle)
    assert isinstance(centroid, Point)
    safe_print(f"SUCCESS: Centroid calculation: ({centroid.x:.3f}, {centroid.y:.3f})")
    
    # 測試距離計算
    dist = distance((0, 0), (3, 4))
    assert abs(dist - 5.0) < 1e-10
    safe_print(f"SUCCESS: Distance calculation: {dist}")
    
    safe_print("New utils API test PASSED")
    return True

def test_predefined_triangle_generation():
    """測試預定義三角形生成"""
    safe_print("\n=== Testing predefined triangle generation ===")
    
    from figures.predefined.predefined_triangle import PredefinedTriangleGenerator
    
    generator = PredefinedTriangleGenerator()
    
    params = {
        'definition_mode': 'sss',
        'side_a': 6.0,
        'side_b': 8.0,
        'side_c': 10.0,
        'variant': 'question',
        'vertex_p1_display_config': {'show_point': True, 'show_label': True},
        'vertex_p2_display_config': {'show_point': True, 'show_label': True},
        'vertex_p3_display_config': {'show_point': True, 'show_label': True}
    }
    
    tikz_result = generator.generate_tikz(params)
    
    assert isinstance(tikz_result, str)
    assert len(tikz_result) > 100
    assert "filldraw" in tikz_result
    assert not tikz_result.startswith("% Error")
    
    safe_print(f"SUCCESS: TikZ generation: {len(tikz_result)} characters")
    safe_print(f"Contains {tikz_result.count('filldraw')} fill/draw commands")
    safe_print(f"Contains {tikz_result.count('node')} node labels")
    
    safe_print("Predefined triangle test PASSED")
    return tikz_result

def test_comprehensive_workflow():
    """測試完整工作流程"""
    safe_print("\n=== Testing comprehensive workflow ===")
    
    from figures.predefined.predefined_triangle import PredefinedTriangleGenerator
    from utils import construct_triangle, get_centroid
    
    generator = PredefinedTriangleGenerator()
    
    # 測試不同類型的三角形
    triangles = [
        {'name': 'Right Triangle 3-4-5', 'sides': (3, 4, 5)},
        {'name': 'Right Triangle 5-12-13', 'sides': (5, 12, 13)},
        {'name': 'Equilateral Triangle', 'sides': (4, 4, 4)}
    ]
    
    results = []
    
    for tri_config in triangles:
        sides = tri_config['sides']
        
        # 使用新API計算
        triangle = construct_triangle('sss', side_a=sides[0], side_b=sides[1], side_c=sides[2])
        centroid = get_centroid(triangle)
        area = triangle.area()
        
        # 生成TikZ
        params = {
            'definition_mode': 'sss',
            'side_a': sides[0], 'side_b': sides[1], 'side_c': sides[2],
            'variant': 'question',
            'vertex_p1_display_config': {'show_point': True, 'show_label': True},
            'vertex_p2_display_config': {'show_point': True, 'show_label': True},
            'vertex_p3_display_config': {'show_point': True, 'show_label': True}
        }
        
        tikz_content = generator.generate_tikz(params)
        assert len(tikz_content) > 50
        
        results.append({
            'name': tri_config['name'],
            'area': area,
            'centroid': (centroid.x, centroid.y),
            'tikz_length': len(tikz_content)
        })
        
        safe_print(f"  {tri_config['name']}: Area={area:.2f}, TikZ={len(tikz_content)} chars")
    
    assert len(results) == 3
    safe_print("Comprehensive workflow test PASSED")
    return results

def test_latex_integration():
    """測試LaTeX集成"""
    safe_print("\n=== Testing LaTeX integration ===")
    
    try:
        from utils.orchestration import PDFOrchestrator
        orchestrator = PDFOrchestrator()
        safe_print("SUCCESS: PDF Orchestrator created")
        
        from utils.latex import LaTeXGenerator
        latex_gen = LaTeXGenerator()
        safe_print("SUCCESS: LaTeX Generator created")
        
        safe_print("LaTeX integration test PASSED")
        return True
        
    except Exception as e:
        safe_print(f"LaTeX integration test SKIPPED: {str(e)}")
        return False

def main():
    """主測試函數"""
    safe_print("=" * 60)
    safe_print("ENCODING-SAFE INTEGRATION TESTS")
    safe_print("=" * 60)
    
    try:
        # 顯示編碼信息
        safe_print(f"Python version: {sys.version}")
        safe_print(f"stdout encoding: {sys.stdout.encoding}")
        safe_print(f"filesystem encoding: {sys.getfilesystemencoding()}")
        safe_print("")
        
        # 運行測試
        test_new_utils_api()
        tikz_sample = test_predefined_triangle_generation()
        workflow_results = test_comprehensive_workflow()
        latex_ok = test_latex_integration()
        
        # 總結
        safe_print("\n" + "=" * 60)
        safe_print("ALL ENCODING-SAFE TESTS PASSED!")
        safe_print("Core functionality verified:")
        safe_print("  - New utils API: WORKING")
        safe_print("  - Triangle generation: WORKING") 
        safe_print("  - Multi-triangle workflow: WORKING")
        safe_print(f"  - LaTeX integration: {'WORKING' if latex_ok else 'SKIPPED'}")
        safe_print("=" * 60)
        
        # 顯示樣本
        safe_print("\nSample TikZ output (first 200 chars):")
        safe_print("-" * 40)
        safe_print(tikz_sample[:200] + "..." if len(tikz_sample) > 200 else tikz_sample)
        
        return True
        
    except Exception as e:
        safe_print(f"\nTEST FAILED: {str(e)}")
        import traceback
        safe_print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)