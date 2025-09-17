#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 單位圓圖形生成器
"""

import math
from typing import Dict, Any
from pydantic import ValidationError

from utils import Point, get_logger
from .base import FigureGenerator
from .params import UnitCircleParams
from . import register_figure_generator

logger = get_logger(__name__)

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
            logger.error(f"單位圓參數驗證失敗: {str(e)}")
            raise ValueError(f"單位圓參數驗證失敗: {str(e)}")
        
        # 提取參數
        angle = validated_params.angle
        show_coordinates = validated_params.show_coordinates
        line_color = validated_params.line_color
        point_color = validated_params.point_color
        angle_color = validated_params.angle_color
        radius = validated_params.radius
        variant = validated_params.variant
        
        # 使用新架構的幾何計算功能
        angle_rad = math.radians(angle)
        
        # 計算圓上點的座標，使用 Point 類型
        cos_value = radius * math.cos(angle_rad)
        sin_value = radius * math.sin(angle_rad)
        point_on_circle = Point(cos_value, sin_value)
        origin = Point(0, 0)
        
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
        tikz_content += f"\\fill {origin.to_tikz()} circle (0.03) node[below left] {{$O$}};\n"
        
        # 點 P
        tikz_content += f"\\fill[{point_color}] {point_on_circle.to_tikz()} circle (0.03) node[{label_position}] {{$P$}};\n"
        
        # 半徑線段（使用 Point 類型的座標）
        tikz_content += f"\\draw[thick,{point_color}] {origin.to_tikz()} -- {point_on_circle.to_tikz()};\n"
        
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
            
            # 使用 Point 類型的座標表示
            coord_label_point = Point(cos_value, sin_value - 0.2)
            x_projection = Point(cos_value, 0)
            y_projection = Point(0, sin_value)
            
            # 添加坐標標籤
            tikz_content += f"\\node[below] at {coord_label_point.to_tikz()} {{$({cos_latex},{sin_latex})$}};\n"
            
            # 添加 x 和 y 投影線
            tikz_content += f"\\draw[dashed,gray] {point_on_circle.to_tikz()} -- {x_projection.to_tikz()} node[below] {{${cos_latex}$}};\n"
            tikz_content += f"\\draw[dashed,gray] {point_on_circle.to_tikz()} -- {y_projection.to_tikz()} node[left] {{${sin_latex}$}};\n"
        
        logger.debug(f"生成單位圓 TikZ 代碼: 角度{angle}°, 點{point_on_circle.to_tikz()}")
        
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
        
        result = special_values.get(angle, (f"{math.cos(math.radians(angle)):.4f}", f"{math.sin(math.radians(angle)):.4f}"))
        logger.debug(f"獲取角度 {angle}° 的三角函數值: cos={result[0]}, sin={result[1]}")
        return result