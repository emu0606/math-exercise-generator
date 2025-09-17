#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 角度圖形生成器
"""

from typing import Dict, Any, Optional
from pydantic import ValidationError, BaseModel, Field

from .base import FigureGenerator
from . import register_figure_generator

class AngleParams(BaseModel):
    """角度參數模型"""
    variant: str = 'question'
    start_angle: float = 0.0
    end_angle: float = 90.0
    radius: float = 1.0
    center_x: float = 0.0
    center_y: float = 0.0
    color: str = 'blue'
    style: str = 'solid'
    width: str = 'thin'
    show_arrow: bool = True
    arrow_style: str = 'stealth'
    label: Optional[str] = None
    label_position: str = 'above right'
    label_distance: float = 0.5  # 標籤距離圓心的比例

@register_figure_generator
class AngleGenerator(FigureGenerator):
    """角度圖形生成器
    
    生成一個角度弧。
    """
    
    @classmethod
    def get_name(cls) -> str:
        """獲取圖形類型唯一標識符"""
        return 'angle'
    
    def generate_tikz(self, params: Dict[str, Any]) -> str:
        """生成角度 TikZ 圖形內容
        
        Args:
            params: 角度參數字典，應符合 AngleParams 模型
            
        Returns:
            TikZ 圖形內容（不包含 tikzpicture 環境）
            
        Raises:
            ValidationError: 如果參數驗證失敗
        """
        # 使用 Pydantic 模型驗證參數
        try:
            validated_params = AngleParams(**params)
        except ValidationError as e:
            raise ValidationError(f"角度參數驗證失敗: {str(e)}", e.raw_errors)
        
        # 提取參數
        start_angle = validated_params.start_angle
        end_angle = validated_params.end_angle
        radius = validated_params.radius
        center_x = validated_params.center_x
        center_y = validated_params.center_y
        color = validated_params.color
        style = validated_params.style
        width = validated_params.width
        show_arrow = validated_params.show_arrow
        arrow_style = validated_params.arrow_style
        label = validated_params.label
        label_position = validated_params.label_position
        label_distance = validated_params.label_distance
        
        # 生成 TikZ 代碼
        tikz_content = "% 角度\n"
        
        # 添加 TikZ 庫（如果需要箭頭）
        if show_arrow:
            tikz_content += "\\usetikzlibrary{arrows.meta}\n\n"
        
        # 設置樣式
        arc_style = f"{width}, {style}, {color}"
        if show_arrow:
            arc_style += f", -{arrow_style}"
        
        # 繪製角度弧
        tikz_content += f"\\draw[{arc_style}] ({center_x}, {center_y}) +({start_angle}:{radius}) arc ({start_angle}:{end_angle}:{radius})"
        
        # 添加標籤（如果有）
        if label is not None:
            # 計算標籤位置（在弧的中間）
            mid_angle = (start_angle + end_angle) / 2
            # Use midway placement on the arc path itself
            tikz_content += f" node[midway, {label_position}] {{${label}$}}"
        
        tikz_content += ";\n"
        
        return tikz_content