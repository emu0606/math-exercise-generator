#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 圓弧生成器

本模組提供圓弧的生成功能，支援指定中心、半徑、起始角度
和結束角度的圓弧繪製，支援多種樣式和繪製選項。
"""

import math
from typing import Dict, Any
from pydantic import ValidationError

from utils import Point, global_config, get_logger
from .base import FigureGenerator
from .params import ArcParams
from . import register_figure_generator

logger = get_logger(__name__)

@register_figure_generator
class ArcGenerator(FigureGenerator):
    """
    圓弧生成器
    
    根據指定的中心點、半徑、起始和結束角度繪製圓弧。
    使用新架構的統一 API，整合幾何計算和日誌系統。
    
    支援的功能：
    - 自定義中心點和半徑
    - 弧度和度數角度支援
    - 多種 TikZ 繪製選項和樣式
    - 精確的幾何計算和座標轉換
    
    Attributes:
        logger: 模組日誌記錄器
        config: 全域配置物件
        
    Example:
        >>> generator = ArcGenerator()
        >>> params = {
        ...     'center': (0, 0),
        ...     'radius': 1.0,
        ...     'start_angle_rad': 0,
        ...     'end_angle_rad': math.pi/2,
        ...     'draw_options': 'thick,red'
        ... }
        >>> tikz_code = generator.generate_tikz(params)
        >>> 'arc (0:90:1)' in tikz_code
        True
        
    Note:
        此生成器使用 TikZ 的 arc 命令語法，支援弧度和度數輸入。
        角度轉換和座標計算使用新架構的 Point 類型確保精確度。
    """

    @classmethod
    def get_name(cls) -> str:
        """獲取圖形類型唯一標識符"""
        return "arc"

    def generate_tikz(self, params: Dict[str, Any]) -> str:
        """
        生成圓弧 TikZ 圖形內容

        根據提供的參數生成圓弧的 TikZ 代碼，支援精確的角度計算
        和彈性的繪製選項配置。

        Args:
            params (Dict[str, Any]): 圓弧參數字典，支援的鍵值包括：
                - center (Tuple[float, float]): 圓弧中心點座標
                - radius (float): 圓弧半徑
                - start_angle_rad (float): 起始角度（弧度）
                - end_angle_rad (float): 結束角度（弧度）
                - draw_options (str, optional): TikZ 繪製選項字串
                - variant (str, optional): 變體類型，預設為 'question'

        Returns:
            str: TikZ 圖形內容（不包含 tikzpicture 環境），
                 使用 TikZ arc 命令語法繪製圓弧

        Raises:
            ValidationError: 如果參數驗證失敗或包含無效值
            ValueError: 如果角度值或半徑不合理
            
        Example:
            >>> generator = ArcGenerator()
            >>> params = {
            ...     'center': (0, 0),
            ...     'radius': 2.0,
            ...     'start_angle_rad': 0,
            ...     'end_angle_rad': math.pi/2
            ... }
            >>> result = generator.generate_tikz(params)
            >>> 'arc (0:90:2)' in result
            True
            
            >>> # 帶樣式選項的範例
            >>> styled_params = {
            ...     'center': (1, 1),
            ...     'radius': 1.5,
            ...     'start_angle_rad': math.pi/4,
            ...     'end_angle_rad': 3*math.pi/4,
            ...     'draw_options': 'thick,blue,->'
            ... }
            >>> result = generator.generate_tikz(styled_params)
            >>> 'draw[thick,blue,->]' in result
            True
            
        Note:
            角度轉換使用 math.degrees() 確保精確度。
            TikZ arc 命令使用 (start_deg:end_deg:radius) 語法。
            生成的座標使用 .7g 格式化避免不必要的小數位。
        """
        try:
            validated_params = ArcParams(**params)
            logger.debug(f"圓弧參數驗證成功: center={validated_params.center}, radius={validated_params.radius}")
        except ValidationError as e:
            logger.error(f"圓弧參數驗證失敗: {str(e)}")
            raise

        # 使用新架構的幾何計算功能
        center = Point(*validated_params.center)
        radius = validated_params.radius
        start_angle_deg = validated_params.start_angle
        end_angle_deg = validated_params.end_angle

        # 將度數轉換為弧度供計算使用
        start_angle_rad = math.radians(start_angle_deg)
        end_angle_rad = math.radians(end_angle_deg)

        # 繪製選項處理
        color = validated_params.color
        line_width = validated_params.line_width
        arrow = validated_params.arrow

        # 構建draw選項
        draw_options = [color, line_width]
        if arrow:
            draw_options.append(arrow)
        draw_options_str = f"[{', '.join(draw_options)}]"
        
        # 使用 Point 類型計算弧的起點座標
        start_point_x = center.x + radius * math.cos(start_angle_rad)
        start_point_y = center.y + radius * math.sin(start_angle_rad)
        start_point = Point(start_point_x, start_point_y)
        
        # 使用 Point 類型的 to_tikz() 方法獲取座標字串
        tikz_p_start = start_point.to_tikz()
        
        # 使用 :.7g 格式化度數和半徑，避免不必要的小數位
        tikz_start_deg = f"{start_angle_deg:.7g}"
        tikz_end_deg = f"{end_angle_deg:.7g}"
        tikz_radius = f"{radius:.7g}"

        # 生成 TikZ arc 命令
        tikz_code = f"\\draw{draw_options_str} {tikz_p_start} arc ({tikz_start_deg}:{tikz_end_deg}:{tikz_radius});"

        logger.debug(f"生成圓弧 TikZ 代碼: 中心{center.to_tikz()}, 角度{tikz_start_deg}°-{tikz_end_deg}°")
        
        return tikz_code