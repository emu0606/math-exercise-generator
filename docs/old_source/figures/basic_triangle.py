#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 基礎三角形生成器
"""

from typing import Dict, Any, Tuple
from pydantic import ValidationError

from .base import FigureGenerator
from . import register_figure_generator
from .params_models import BasicTriangleParams, PointTuple

@register_figure_generator
class BasicTriangleGenerator(FigureGenerator):
    """
    基礎三角形生成器。
    根據三個頂點座標繪製一個三角形。
    """

    @classmethod
    def get_name(cls) -> str:
        """獲取圖形類型唯一標識符"""
        return "basic_triangle"

    def generate_tikz(self, params: Dict[str, Any]) -> str:
        """
        生成 TikZ 圖形內容。

        Args:
            params: 圖形參數字典，應符合 BasicTriangleParams 模型。

        Returns:
            TikZ 圖形內容（不包含 tikzpicture 環境）。

        Raises:
            ValidationError: 如果參數驗證失敗。
        """
        try:
            validated_params = BasicTriangleParams(**params)
        except ValidationError as e:
            # Simply re-raise the original Pydantic ValidationError
            raise

        p1: PointTuple = validated_params.p1
        p2: PointTuple = validated_params.p2
        p3: PointTuple = validated_params.p3
        
        draw_options_list = []
        if validated_params.draw_options:
            draw_options_list.append(validated_params.draw_options)
        
        if validated_params.fill_color:
            draw_options_list.append(f"fill={validated_params.fill_color}")

        final_draw_options = ", ".join(filter(None, draw_options_list))
        if final_draw_options:
            final_draw_options = f"[{final_draw_options}]"
        
        # TikZ 座標格式 (x,y), 使用 .7g 進行格式化以處理浮點精度
        tikz_p1 = f"({p1[0]:.7g},{p1[1]:.7g})"
        tikz_p2 = f"({p2[0]:.7g},{p2[1]:.7g})"
        tikz_p3 = f"({p3[0]:.7g},{p3[1]:.7g})"

        # \draw[options] (x1,y1) -- (x2,y2) -- (x3,y3) -- cycle;
        tikz_code = f"\\draw{final_draw_options} {tikz_p1} -- {tikz_p2} -- {tikz_p3} -- cycle;"
        
        # 根據 variant 的處理 (如果需要)
        # if validated_params.variant == 'explanation':
        #     # 例如，在詳解中添加額外標註
        #     pass

        return tikz_code