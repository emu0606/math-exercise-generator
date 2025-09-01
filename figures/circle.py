#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 圓形圖形生成器
"""

from typing import Dict, Any
from pydantic import ValidationError, BaseModel, Field

from .base import FigureGenerator
from . import register_figure_generator

class CircleParams(BaseModel):
    """圓形參數模型"""
    variant: str = 'question'
    radius: float = 1.0
    center_x: float = 0.0
    center_y: float = 0.0
    fill: bool = False
    fill_color: str = 'white'
    line_color: str = 'black'
    line_style: str = 'solid'
    line_width: str = 'thin'

@register_figure_generator
class CircleGenerator(FigureGenerator):
    """圓形圖形生成器
    
    生成一個圓形。
    """
    
    @classmethod
    def get_name(cls) -> str:
        """獲取圖形類型唯一標識符"""
        return 'circle'
    
    def generate_tikz(self, params: Dict[str, Any]) -> str:
        """生成圓形 TikZ 圖形內容
        
        Args:
            params: 圓形參數字典，應符合 CircleParams 模型
            
        Returns:
            TikZ 圖形內容（不包含 tikzpicture 環境）
            
        Raises:
            ValidationError: 如果參數驗證失敗
        """
        # 使用 Pydantic 模型驗證參數
        try:
            validated_params = CircleParams(**params)
        except ValidationError as e:
            raise ValidationError(f"圓形參數驗證失敗: {str(e)}", e.raw_errors)
        
        # 提取參數
        radius = validated_params.radius
        center_x = validated_params.center_x
        center_y = validated_params.center_y
        fill = validated_params.fill
        fill_color = validated_params.fill_color
        line_color = validated_params.line_color
        line_style = validated_params.line_style
        line_width = validated_params.line_width
        
        # 生成 TikZ 代碼
        tikz_content = "% 圓形\n"
        
        # 設置樣式
        style = f"{line_width}, {line_style}, {line_color}"
        if fill:
            style += f", fill={fill_color}"
        
        # 繪製圓形
        tikz_content += f"\\draw[{style}] ({center_x}, {center_y}) circle ({radius});\n"
        
        return tikz_content