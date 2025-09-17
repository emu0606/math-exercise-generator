#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 圓弧生成器
"""

import math
from typing import Dict, Any
from pydantic import ValidationError

from .base import FigureGenerator
from . import register_figure_generator # 假設 __init__.py 中已定義並導出
from .params_models import ArcParams

@register_figure_generator
class ArcGenerator(FigureGenerator):
    """
    圓弧生成器。
    根據中心點、半徑、起始和結束角度繪製圓弧。
    """

    @classmethod
    def get_name(cls) -> str:
        """獲取圖形類型唯一標識符"""
        return "arc"

    def generate_tikz(self, params: Dict[str, Any]) -> str:
        """
        生成 TikZ 圖形內容。

        Args:
            params: 圖形參數字典，應符合 ArcParams 模型。
                    包含 center, radius, start_angle_rad, end_angle_rad, draw_options。

        Returns:
            TikZ 圖形內容（不包含 tikzpicture 環境）。

        Raises:
            ValidationError: 如果參數驗證失敗。
        """
        try:
            validated_params = ArcParams(**params)
        except ValidationError as e:
            # Simply re-raise the original Pydantic ValidationError
            raise

        center = validated_params.center
        radius = validated_params.radius
        start_angle_rad = validated_params.start_angle_rad
        end_angle_rad = validated_params.end_angle_rad
        
        # 將弧度轉換為度數供 TikZ 使用
        start_deg = math.degrees(start_angle_rad)
        end_deg = math.degrees(end_angle_rad)

        # TikZ 的 arc 命令 (start angle:end angle:radius)
        # 角度的順序和範圍由 get_arc_render_params 函數初步處理。
        # ArcGenerator 忠實地使用這些角度。
        # 例如，如果 end_deg < start_deg 且差異小於 360，TikZ 會畫一個大於180度的弧。
        # 如果差異大於 360，TikZ 的行為可能需要注意。
        # 我們假設 get_arc_render_params 提供的角度已經考慮了期望的掃描方向和範圍。
        # （例如，對於 test_arc_angle_wraparound，start=pi/2, end=2pi -> 90deg to 360deg）

        draw_options_str = validated_params.draw_options or ""
        if draw_options_str:
            draw_options_str = f"[{draw_options_str}]"
        
        # TikZ 繪製圓弧的標準語法之一：
        # \draw[options] (start_point_x,start_point_y) arc (start_angle_deg:end_angle_deg:radius);
        # 計算弧的起點
        start_point_x = center[0] + radius * math.cos(start_angle_rad)
        start_point_y = center[1] + radius * math.sin(start_angle_rad)
        
        tikz_p_start = f"({start_point_x:.7g},{start_point_y:.7g})" # 使用 .7g 避免過多小數位
        
        # 使用 :.7g 格式化度數，避免不必要的 .0
        tikz_start_deg = f"{start_deg:.7g}"
        tikz_end_deg = f"{end_deg:.7g}"
        tikz_radius = f"{radius:.7g}"

        tikz_code = f"\\draw{draw_options_str} {tikz_p_start} arc ({tikz_start_deg}:{tikz_end_deg}:{tikz_radius});"
        
        return tikz_code