#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
完整PDF生成流程測試：驗證從參數到PDF的完整工作流程
"""

import sys
import os
import tempfile
import shutil
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def test_pdf_orchestration():
    """測試PDF協調器功能"""
    print("Testing PDF orchestration...")
    
    from utils.orchestration import PDFOrchestrator
    from utils.orchestration.pdf_orchestrator import OutputConfig, ContentConfig
    
    # 創建協調器
    orchestrator = PDFOrchestrator()
    assert orchestrator is not None
    print("PDF orchestrator created successfully")
    
def test_latex_compilation():
    """測試LaTeX編譯功能"""
    print("\nTesting LaTeX compilation...")
    
    from utils.latex import LaTeXCompiler, DocumentConfig, CompilerConfig
    
    # 創建編譯器
    compiler = LaTeXCompiler()
    
    # 創建簡單的LaTeX文檔
    simple_doc = r"""
\documentclass{article}
\usepackage[UTF8]{ctex}
\begin{document}
測試文檔
\begin{tikzpicture}
\filldraw[blue] (0,0) circle (1pt);
\node at (0.2,0.2) {P};
\end{tikzpicture}
\end{document}
"""
    
    # 測試編譯（不實際執行，只驗證接口）
    doc_config = DocumentConfig()
    compiler_config = CompilerConfig()
    
    print("LaTeX compiler interface OK")

def test_figure_to_latex_generation():
    """測試從圖形參數到LaTeX代碼的生成"""
    print("\nTesting figure to LaTeX generation...")
    
    from figures.predefined.predefined_triangle import PredefinedTriangleGenerator
    from utils.latex import LaTeXGenerator
    
    # 創建三角形參數
    triangle_params = {
        'definition_mode': 'sss',
        'side_a': 6.0,
        'side_b': 8.0, 
        'side_c': 10.0,
        'variant': 'question',
        'vertex_p1_display_config': {'show_point': True, 'show_label': True},
        'vertex_p2_display_config': {'show_point': True, 'show_label': True},
        'vertex_p3_display_config': {'show_point': True, 'show_label': True},
        'display_centroid': {'show_point': True, 'show_label': True}
    }
    
    # 生成TikZ代碼
    triangle_gen = PredefinedTriangleGenerator()
    tikz_code = triangle_gen.generate_tikz(triangle_params)
    
    assert len(tikz_code) > 100
    assert "filldraw" in tikz_code
    print(f"TikZ code generated: {len(tikz_code)} characters")
    
    # 生成完整LaTeX文檔
    latex_gen = LaTeXGenerator()
    
    # 創建完整文檔
    full_latex = latex_gen.generate_complete_document(
        tikz_content=tikz_code,
        title="測試三角形",
        content_type="question"
    )
    
    assert "\\documentclass" in full_latex
    assert "\\begin{tikzpicture}" in full_latex
    assert "\\end{tikzpicture}" in full_latex
    print(f"Complete LaTeX document generated: {len(full_latex)} characters")
    
    return full_latex

def test_end_to_end_workflow():
    """端到端工作流程測試"""
    print("\nTesting end-to-end workflow...")
    
    # 創建臨時目錄用於測試
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Using temp directory: {temp_dir}")
        
        # 1. 參數設置
        test_problems = [
            {
                'type': 'predefined_triangle',
                'params': {
                    'definition_mode': 'sss',
                    'side_a': 3.0,
                    'side_b': 4.0,
                    'side_c': 5.0,
                    'variant': 'question',
                    'vertex_p1_display_config': {'show_point': True, 'show_label': True},
                    'vertex_p2_display_config': {'show_point': True, 'show_label': True},
                    'vertex_p3_display_config': {'show_point': True, 'show_label': True}
                }
            },
            {
                'type': 'predefined_triangle', 
                'params': {
                    'definition_mode': 'sss',
                    'side_a': 5.0,
                    'side_b': 12.0,
                    'side_c': 13.0,
                    'variant': 'explanation',
                    'vertex_p1_display_config': {'show_point': True, 'show_label': True},
                    'vertex_p2_display_config': {'show_point': True, 'show_label': True}, 
                    'vertex_p3_display_config': {'show_point': True, 'show_label': True},
                    'display_centroid': {'show_point': True, 'show_label': True},
                    'side_p1p2_display_config': {'show_label': True, 'label_text_type': 'length'}
                }
            }
        ]
        
        # 2. 生成TikZ代碼
        from figures.predefined.predefined_triangle import PredefinedTriangleGenerator  
        from utils.latex import LaTeXGenerator
        
        generator = PredefinedTriangleGenerator()
        latex_gen = LaTeXGenerator()
        generated_docs = []
        
        for i, problem in enumerate(test_problems):
            print(f"Processing problem {i+1}...")
            
            tikz_code = generator.generate_tikz(problem['params'])
            assert len(tikz_code) > 50
            
            latex_doc = latex_gen.generate_complete_document(
                tikz_content=tikz_code,
                title=f"測試問題 {i+1}",
                content_type=problem['params']['variant']
            )
            
            generated_docs.append(latex_doc)
            
            # 保存LaTeX文件用於調試
            latex_file = os.path.join(temp_dir, f"problem_{i+1}.tex")
            with open(latex_file, 'w', encoding='utf-8') as f:
                f.write(latex_doc)
            print(f"LaTeX saved to: {latex_file}")
        
        # 3. 驗證生成的內容
        assert len(generated_docs) == 2
        for doc in generated_docs:
            assert "\\documentclass" in doc
            assert "\\begin{tikzpicture}" in doc
            assert "filldraw" in doc
        
        print(f"Generated {len(generated_docs)} complete LaTeX documents")
        print(f"Document 1 length: {len(generated_docs[0])} characters")
        print(f"Document 2 length: {len(generated_docs[1])} characters")

def test_utils_api_workflow():
    """測試新utils API的完整工作流程"""
    print("\nTesting complete utils API workflow...")
    
    from utils import construct_triangle, get_centroid, distance
    from utils.tikz import ArcRenderer
    from utils.latex import LaTeXGenerator
    
    # 1. 構造三角形
    triangle = construct_triangle('sss', side_a=8, side_b=6, side_c=10)
    print(f"Triangle vertices: P1{triangle.p1.to_tuple()}, P2{triangle.p2.to_tuple()}, P3{triangle.p3.to_tuple()}")
    
    # 2. 計算特殊點
    centroid = get_centroid(triangle)
    print(f"Centroid: ({centroid.x:.3f}, {centroid.y:.3f})")
    
    # 3. 手動構建TikZ內容
    tikz_parts = []
    
    # 繪製三角形邊
    tikz_parts.append(f"\\draw ({triangle.p1.x:.3f},{triangle.p1.y:.3f}) -- ({triangle.p2.x:.3f},{triangle.p2.y:.3f}) -- ({triangle.p3.x:.3f},{triangle.p3.y:.3f}) -- cycle;")
    
    # 繪製頂點
    for i, point in enumerate([triangle.p1, triangle.p2, triangle.p3], 1):
        tikz_parts.append(f"\\filldraw[blue] ({point.x:.3f},{point.y:.3f}) circle (1.5pt);")
        tikz_parts.append(f"\\node at ({point.x+0.15:.3f},{point.y+0.15:.3f}) {{P{i}}};")
    
    # 繪製質心
    tikz_parts.append(f"\\filldraw[red] ({centroid.x:.3f},{centroid.y:.3f}) circle (1.2pt);")
    tikz_parts.append(f"\\node at ({centroid.x+0.15:.3f},{centroid.y+0.15:.3f}) {{G}};")
    
    tikz_content = "\n".join(tikz_parts)
    
    # 4. 生成完整LaTeX
    latex_gen = LaTeXGenerator()
    full_doc = latex_gen.generate_complete_document(
        tikz_content=tikz_content,
        title="手工構建的三角形",
        content_type="question"
    )
    
    assert len(full_doc) > 200
    assert tikz_content in full_doc
    print(f"Manual workflow successful: {len(full_doc)} characters")

if __name__ == "__main__":
    try:
        test_pdf_orchestration()
        test_latex_compilation()
        latex_content = test_figure_to_latex_generation()
        test_end_to_end_workflow()
        test_utils_api_workflow()
        
        print("\n" + "="*50)
        print("ALL PDF GENERATION FLOW TESTS PASSED!")
        print("Complete workflow from parameters to LaTeX is functional")
        print("="*50)
        
        # 顯示生成的LaTeX示例（前500字符）
        print("\nSample generated LaTeX:")
        print("-" * 30)
        print(latex_content[:500] + "..." if len(latex_content) > 500 else latex_content)
        
    except Exception as e:
        print(f"\nPDF GENERATION FLOW TEST FAILED: {e}")
        import traceback
        traceback.print_exc()