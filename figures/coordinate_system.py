#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 坐標系圖形生成器
"""

from typing import Dict, Any
from pydantic import ValidationError, BaseModel, Field

from .base import FigureGenerator
from . import register_figure_generator

class CoordinateSystemParams(BaseModel):
    """坐標系參數模型"""
    variant: str = 'question'
    x_min: float = -5.0
    x_max: float = 5.0
    y_min: float = -5.0
    y_max: float = 5.0
    show_grid: bool = False
    show_labels: bool = True
    color: str = 'black'
    grid_color: str = 'gray!30'
    x_label: str = 'x'
    y_label: str = 'y'
    arrow_style: str = 'stealth'

@register_figure_generator
class CoordinateSystemGenerator(FigureGenerator):
    """坐標系圖形生成器
    
    生成一個坐標系。
    """
    
    @classmethod
    def get_name(cls) -> str:
        """獲取圖形類型唯一標識符"""
        return 'coordinate_system'
    
    def generate_tikz(self, params: Dict[str, Any]) -> str:
        """生成坐標系 TikZ 圖形內容
        
        Args:
            params: 坐標系參數字典，應符合 CoordinateSystemParams 模型
            
        Returns:
            TikZ 圖形內容（不包含 tikzpicture 環境）
            
        Raises:
            ValidationError: 如果參數驗證失敗
        """
        # 使用 Pydantic 模型驗證參數
        try:
            validated_params = CoordinateSystemParams(**params)
        except ValidationError as e:
            raise ValidationError(f"坐標系參數驗證失敗: {str(e)}", e.raw_errors)
        
        # 提取參數
        x_min = validated_params.x_min
        x_max = validated_params.x_max
        y_min = validated_params.y_min
        y_max = validated_params.y_max
        show_grid = validated_params.show_grid
        show_labels = validated_params.show_labels
        color = validated_params.color
        grid_color = validated_params.grid_color
        x_label = validated_params.x_label
        y_label = validated_params.y_label
        arrow_style = validated_params.arrow_style
        
        # 生成 TikZ 代碼
        tikz_content = "% 坐標系\n"
        
        # 添加 TikZ 庫
        tikz_content += "\\usetikzlibrary{arrows.meta}\n\n"
        
        # 繪製網格（如果需要）
        if show_grid:
            tikz_content += f"\\draw[{grid_color}, step=1] ({x_min}, {y_min}) grid ({x_max}, {y_max});\n"
        
        # 繪製坐標軸
        x_label_node = f" node[right] {{${x_label}$}}" if show_labels else ""
        y_label_node = f" node[above] {{${y_label}$}}" if show_labels else ""
        
        tikz_content += f"\\draw[-{arrow_style}, {color}] ({x_min}, 0) -- ({x_max}, 0){x_label_node};\n"
        tikz_content += f"\\draw[-{arrow_style}, {color}] (0, {y_min}) -- (0, {y_max}){y_label_node};\n"
        
        # 繪製刻度（如果需要）
        if show_labels:
            # X 軸刻度
            for i in range(int(x_min) + 1, int(x_max)):
                if i != 0:  # 跳過原點
                    tikz_content += f"\\draw[{color}] ({i}, -0.1) -- ({i}, 0.1) node[below] {{${i}$}};\n"
            
            # Y 軸刻度
            for i in range(int(y_min) + 1, int(y_max)):
                if i != 0:  # 跳過原點
                    tikz_content += f"\\draw[{color}] (-0.1, {i}) -- (0.1, {i}) node[left] {{${i}$}};\n"
        
        return tikz_content