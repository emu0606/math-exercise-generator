#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 圖形渲染器
負責渲染 TikZ 圖形，與 figures 模組交互
"""

from typing import Dict, List, Any, Optional
import figures
from utils.latex_config import LaTeXConfig

class FigureRenderer:
    """圖形渲染器
    
    負責渲染 TikZ 圖形，與 figures 模組交互。
    處理圖形生成過程中的錯誤，並返回適當的錯誤信息。
    """
    
    def __init__(self, config: Optional[LaTeXConfig] = None):
        """初始化圖形渲染器
        
        Args:
            config: LaTeX 配置對象，如果為 None，則創建一個新的配置對象
        """
        self.config = config or LaTeXConfig()
    
    def render(self, figure_data: Dict[str, Any]) -> str:
        """渲染圖形
        
        根據 figure_data 生成 TikZ 圖形代碼，處理所有可能的錯誤並返回結果或錯誤信息。
        
        Args:
            figure_data: 圖形數據字典，包含 'type', 'params' 和 'options'
            
        Returns:
            TikZ 圖形代碼（包含 tikzpicture 環境）或錯誤信息
        """
        try:
            # 檢查圖形數據
            if not figure_data:
                return ""
            
            # 提取圖形類型和參數
            figure_type = figure_data.get('type')
            params = figure_data.get('params', {})
            options = figure_data.get('options', {})
            
            if not figure_type:
                return "\\textbf{圖形數據缺少 'type' 字段}"
            
            try:
                # 獲取圖形生成器
                generator_cls = figures.get_figure_generator(figure_type)
                generator = generator_cls()
                
                # 生成 TikZ 圖形內容
                tikz_content = generator.generate_tikz(params)
                
                # 處理 scale 選項
                scale = options.get('scale', 1.0)
                
                # 構建 tikzpicture 環境選項
                tikz_options = []
                if scale != 1.0:
                    tikz_options.append(f"scale={scale}")
                
                # 構建 tikzpicture 環境
                if tikz_options:
                    options_str = ", ".join(tikz_options)
                    tikz_code = f"\\begin{{tikzpicture}}[{options_str}]\n{tikz_content}\n\\end{{tikzpicture}}"
                else:
                    tikz_code = f"\\begin{{tikzpicture}}\n{tikz_content}\n\\end{{tikzpicture}}"
                
                return tikz_code
                
            except Exception as e:
                return f"\\textbf{{渲染圖形時出錯 (類型: {figure_type}): {str(e)}}}"
                
        except Exception as e:
            return f"\\textbf{{Unexpected error in render: {str(e)}}}"