#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 標籤圖形生成器
"""

from typing import Dict, Any, Optional
from pydantic import ValidationError
import math # For potential use in future, or if formatting numbers

from .base import FigureGenerator
from . import register_figure_generator
from .params_models import LabelParams # Import from central params_models

@register_figure_generator
class LabelGenerator(FigureGenerator):
    """標籤圖形生成器
    
    生成一個文字標籤。
    """
    
    @classmethod
    def get_name(cls) -> str:
        """獲取圖形類型唯一標識符"""
        return 'label'
    
    def generate_tikz(self, params: Dict[str, Any]) -> str:
        """生成標籤 TikZ 圖形內容
        
        Args:
            params: 標籤參數字典，應符合 LabelParams 模型
            
        Returns:
            TikZ 圖形內容（不包含 tikzpicture 環境）
            
        Raises:
            ValidationError: 如果參數驗證失敗
        """
        # 使用 Pydantic 模型驗證參數
        try:
            validated_params = LabelParams(**params)
        except ValidationError as e:
            # Pydantic V2 uses e.errors() instead of e.raw_errors
            # Simply re-raise the original Pydantic ValidationError
            raise
        
        # 提取參數
        x = validated_params.x
        y = validated_params.y
        text = validated_params.text
        # position = validated_params.position # Old param
        # color = validated_params.color       # Old param
        # font_size = validated_params.font_size # Old param
        math_mode = validated_params.math_mode
        
        # 生成 TikZ 代碼
        # tikz_content = "% 標籤\n" # 移除註釋行，生成器只返回命令
        
        # 構建 TikZ node options
        options_list = []
        if validated_params.position_modifiers:
            options_list.append(validated_params.position_modifiers)
        if validated_params.anchor:
            options_list.append(f"anchor={validated_params.anchor}")
        if validated_params.rotate is not None: # rotate=0 is a valid rotation
            options_list.append(f"rotate={validated_params.rotate:.7g}")
        
        # Color is always present, use the one from params (default 'black')
        options_list.append(f"color={validated_params.color}")
            
        if validated_params.font_size:
            options_list.append(f"font={validated_params.font_size}")
        
        if validated_params.additional_node_options:
            options_list.append(validated_params.additional_node_options)
        
        style_str = ", ".join(filter(None, options_list))
        if style_str:
            style_str = f"[{style_str}]"
        
        # 處理文字
        if math_mode:
            # 如果是數學模式，用 $ 包裹文本
            # 假設傳入的 text 是原始文本，不包含 $
            formatted_text = f"${text}$" if text else ""
        else:
            # 如果不是數學模式，直接使用文本
            # TikZ 的 node 文本已經在 {} 中，大多數特殊字符不需要額外轉義
            # 但某些字符如 % 和 \ 仍需要特別處理
            formatted_text = text if text else ""
            
            # 處理可能需要特別注意的字符
            if formatted_text:
                # 處理反斜杠 \
                formatted_text = formatted_text.replace('\\', '\\textbackslash{}')
                # 處理其他特殊字符
                formatted_text = formatted_text.replace('&', '\\&')
                formatted_text = formatted_text.replace('%', '\\%')
                formatted_text = formatted_text.replace('$', '\\$')
                formatted_text = formatted_text.replace('#', '\\#')
                formatted_text = formatted_text.replace('_', '\\_')
                formatted_text = formatted_text.replace('{', '\\{')
                formatted_text = formatted_text.replace('}', '\\}')
                formatted_text = formatted_text.replace('~', '\\textasciitilde{}')
                formatted_text = formatted_text.replace('^', '\\textasciicircum{}')
        
        # 繪製標籤，使用 .7g 格式化座標
        tikz_x = f"{x:.7g}"
        tikz_y = f"{y:.7g}"
        # Initialize tikz_content here if the leading comment is removed
        tikz_content = f"\\node{style_str} at ({tikz_x},{tikz_y}) {{{formatted_text}}};\n"
        
        return tikz_content.strip() # Use strip() to remove potential leading/trailing newlines if any