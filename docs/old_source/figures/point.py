#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 點圖形生成器
"""

from typing import Dict, Any, Optional
from pydantic import ValidationError, BaseModel, Field

from .base import FigureGenerator
from . import register_figure_generator

class PointParams(BaseModel):
    """點參數模型"""
    variant: str = 'question'
    x: float = 0.0
    y: float = 0.0
    label: Optional[str] = None
    label_position: str = 'above'
    color: str = 'black'
    size: float = 0.03
    style: str = 'fill'

@register_figure_generator
class PointGenerator(FigureGenerator):
    """點圖形生成器
    
    生成一個點。
    """
    
    @classmethod
    def get_name(cls) -> str:
        """獲取圖形類型唯一標識符"""
        return 'point'
    
    def generate_tikz(self, params: Dict[str, Any]) -> str:
        """生成點 TikZ 圖形內容
        
        Args:
            params: 點參數字典，應符合 PointParams 模型
            
        Returns:
            TikZ 圖形內容（不包含 tikzpicture 環境）
            
        Raises:
            ValidationError: 如果參數驗證失敗
        """
        # 使用 Pydantic 模型驗證參數
        try:
            validated_params = PointParams(**params)
        except ValidationError as e:
            raise ValidationError(f"點參數驗證失敗: {str(e)}", e.raw_errors)
        
        # 提取參數
        x = validated_params.x
        y = validated_params.y
        label = validated_params.label
        label_position = validated_params.label_position
        color = validated_params.color
        size = validated_params.size
        style = validated_params.style
        
        # 生成 TikZ 代碼
        tikz_content = "% 點\n"
        
        # 繪製點
        if style == 'fill':
            tikz_content += f"\\fill[{color}] ({x}, {y}) circle ({size})"
        else:
            tikz_content += f"\\draw[{color}] ({x}, {y}) circle ({size})"
        
        # 添加標籤（如果有）
        if label is not None:
            tikz_content += f" node[{label_position}] {{${label}$}}"
        
        tikz_content += ";\n"
        
        return tikz_content