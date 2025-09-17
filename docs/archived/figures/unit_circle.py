#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 單位圓圖形生成器
"""

import math
from typing import Dict, Any
from pydantic import ValidationError

from .base import FigureGenerator
from .params_models import UnitCircleParams
from . import register_figure_generator

@register_figure_generator
class UnitCircleGenerator(FigureGenerator):
    """單位圓圖形生成器
    
    生成單位圓及其上的點、角度等。
    """
    
    @classmethod
    def get_name(cls) -> str:
        """獲取圖形類型唯一標識符"""
        return 'unit_circle'
    
    def generate_tikz(self, params: Dict[str, Any]) -> str:
        """生成單位圓 TikZ 圖形內容
        
        Args:
            params: 單位圓參數字典，應符合 UnitCircleParams 模型
            
        Returns:
            TikZ 圖形內容（不包含 tikzpicture 環境）
            
        Raises:
            ValidationError: 如果參數驗證失敗
        """
        # 使用 Pydantic 模型驗證參數
        try:
            validated_params = UnitCircleParams(**params)
        except ValidationError as e:
            raise ValidationError(f"單位圓參數驗證失敗: {str(e)}", e.raw_errors)
        
        # 提取參數
        angle = validated_params.angle
        show_coordinates = validated_params.show_coordinates
        line_color = validated_params.line_color
        point_color = validated_params.point_color
        angle_color = validated_params.angle_color
        radius = validated_params.radius
        variant = validated_params.variant
        
        # 計算角度（弧度）
        angle_rad = math.radians(angle)
        
        # 計算點的坐標
        cos_value = radius * math.cos(angle_rad)
        sin_value = radius * math.sin(angle_rad)
        
        # 確定點標籤的位置
        label_position = self._get_label_position(angle)
        
        # 確定角度標籤的位置
        angle_label_position = self._get_angle_label_position(angle)
        
        # 生成 TikZ 代碼
        tikz_content = "% 單位圓\n"
        
        # 坐標軸（如果需要顯示）
        if show_coordinates:
            tikz_content += f"\\draw[->] (-{radius*1.2},0) -- ({radius*1.2},0) node[right] {{$x$}};\n"
            tikz_content += f"\\draw[->] (0,-{radius*1.2}) -- (0,{radius*1.2}) node[above] {{$y$}};\n"
        
        # 單位圓
        tikz_content += f"\\draw[{line_color}] (0,0) circle ({radius});\n"
        
        # 原點
        tikz_content += f"\\fill (0,0) circle (0.03) node[below left] {{$O$}};\n"
        
        # 點 P
        tikz_content += f"\\fill[{point_color}] ({cos_value},{sin_value}) circle (0.03) node[{label_position}] {{$P$}};\n"
        
        # 半徑線段
        tikz_content += f"\\draw[thick,{point_color}] (0,0) -- ({cos_value},{sin_value});\n"
        
        # 角度弧
        tikz_content += f"\\draw[{angle_color},->] (0.3,0) arc (0:{angle}:0.3) node[midway,{angle_label_position}] {{${angle}^\\circ$}};\n"
        
        # 如果是詳解變體，添加更多信息
        if variant == 'explanation':
            # 計算 cos 和 sin 值（精確值）
            exact_cos = math.cos(angle_rad)
            exact_sin = math.sin(angle_rad)
            
            # 格式化為 LaTeX
            if angle in [0, 30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 240, 270, 300, 315, 330, 360]:
                # 特殊角度使用精確表示
                cos_latex, sin_latex = self._get_exact_trig_values(angle)
            else:
                # 其他角度使用小數表示
                cos_latex = f"{exact_cos:.4f}"
                sin_latex = f"{exact_sin:.4f}"
            
            # 添加坐標標籤
            tikz_content += f"\\node[below] at ({cos_value},{sin_value-0.2}) {{$({cos_latex},{sin_latex})$}};\n"
            
            # 添加 x 和 y 投影線
            tikz_content += f"\\draw[dashed,gray] ({cos_value},{sin_value}) -- ({cos_value},0) node[below] {{${cos_latex}$}};\n"
            tikz_content += f"\\draw[dashed,gray] ({cos_value},{sin_value}) -- (0,{sin_value}) node[left] {{${sin_latex}$}};\n"
        
        return tikz_content
    
    def _get_label_position(self, angle: float) -> str:
        """確定點標籤的位置"""
        if 0 <= angle < 45 or 315 <= angle <= 360:
            return "above right"
        elif 45 <= angle < 135:
            return "above"
        elif 135 <= angle < 225:
            return "above left"
        elif 225 <= angle < 315:
            return "below"
        else:
            return "right"
    
    def _get_angle_label_position(self, angle: float) -> str:
        """確定角度標籤的位置"""
        if 0 <= angle < 90:
            return "above right"
        elif 90 <= angle < 180:
            return "above left"
        elif 180 <= angle < 270:
            return "below left"
        else:
            return "below right"
    
    def _get_exact_trig_values(self, angle: float) -> tuple:
        """獲取特殊角度的精確三角函數值"""
        special_values = {
            0: ("1", "0"),
            30: ("\\frac{\\sqrt{3}}{2}", "\\frac{1}{2}"),
            45: ("\\frac{\\sqrt{2}}{2}", "\\frac{\\sqrt{2}}{2}"),
            60: ("\\frac{1}{2}", "\\frac{\\sqrt{3}}{2}"),
            90: ("0", "1"),
            120: ("-\\frac{1}{2}", "\\frac{\\sqrt{3}}{2}"),
            135: ("-\\frac{\\sqrt{2}}{2}", "\\frac{\\sqrt{2}}{2}"),
            150: ("-\\frac{\\sqrt{3}}{2}", "\\frac{1}{2}"),
            180: ("-1", "0"),
            210: ("-\\frac{\\sqrt{3}}{2}", "-\\frac{1}{2}"),
            225: ("-\\frac{\\sqrt{2}}{2}", "-\\frac{\\sqrt{2}}{2}"),
            240: ("-\\frac{1}{2}", "-\\frac{\\sqrt{3}}{2}"),
            270: ("0", "-1"),
            300: ("\\frac{1}{2}", "-\\frac{\\sqrt{3}}{2}"),
            315: ("\\frac{\\sqrt{2}}{2}", "-\\frac{\\sqrt{2}}{2}"),
            330: ("\\frac{\\sqrt{3}}{2}", "-\\frac{1}{2}"),
            360: ("1", "0")
        }
        
        return special_values.get(angle, (f"{math.cos(math.radians(angle)):.4f}", f"{math.sin(math.radians(angle)):.4f}"))