#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 線段圖形生成器
"""

from typing import Dict, Any, Optional
from pydantic import ValidationError, BaseModel, Field

from .base import FigureGenerator
from . import register_figure_generator

class LineParams(BaseModel):
    """線段參數模型"""
    variant: str = 'question'
    x1: float = 0.0
    y1: float = 0.0
    x2: float = 1.0
    y2: float = 0.0
    color: str = 'black'
    style: str = 'solid'
    width: str = 'thin'
    arrow: bool = False
    arrow_style: str = 'stealth'
    label: Optional[str] = None
    label_position: str = 'above'

@register_figure_generator
class LineGenerator(FigureGenerator):
    """線段圖形生成器
    
    生成一個線段。
    """
    
    @classmethod
    def get_name(cls) -> str:
        """獲取圖形類型唯一標識符"""
        return 'line'
    
    def generate_tikz(self, params: Dict[str, Any]) -> str:
        """生成線段 TikZ 圖形內容
        
        Args:
            params: 線段參數字典，應符合 LineParams 模型
            
        Returns:
            TikZ 圖形內容（不包含 tikzpicture 環境）
            
        Raises:
            ValidationError: 如果參數驗證失敗
        """
        # 使用 Pydantic 模型驗證參數
        try:
            validated_params = LineParams(**params)
        except ValidationError as e:
            raise ValidationError(f"線段參數驗證失敗: {str(e)}", e.raw_errors)
        
        # 提取參數
        x1 = validated_params.x1
        y1 = validated_params.y1
        x2 = validated_params.x2
        y2 = validated_params.y2
        color = validated_params.color
        style = validated_params.style
        width = validated_params.width
        arrow = validated_params.arrow
        arrow_style = validated_params.arrow_style
        label = validated_params.label
        label_position = validated_params.label_position
        
        # 生成 TikZ 代碼
        tikz_content = "% 線段\n"
        
        # 添加 TikZ 庫（如果需要箭頭）
        if arrow:
            tikz_content += "\\usetikzlibrary{arrows.meta}\n\n"
        
        # 設置樣式
        line_style = f"{width}, {style}, {color}"
        if arrow:
            line_style += f", -{arrow_style}"
        
        # 繪製線段
        tikz_content += f"\\draw[{line_style}] ({x1}, {y1}) -- ({x2}, {y2})"
        
        # 添加標籤（如果有）
        if label is not None:
            tikz_content += f" node[{label_position}] {{${label}$}}"
        
        tikz_content += ";\n"
        
        return tikz_content