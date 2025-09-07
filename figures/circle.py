#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 圓形圖形生成器

本模組提供圓形圖形的生成功能，支援自定義圓心、半徑、填充
和線條樣式等多種參數配置。
"""

from typing import Dict, Any
from pydantic import ValidationError

from utils import Point, global_config, get_logger
from .base import FigureGenerator
from .params import CircleParams
from . import register_figure_generator

logger = get_logger(__name__)


@register_figure_generator
class CircleGenerator(FigureGenerator):
    """圓形圖形生成器
    
    生成指定圓心和半徑的圓形，支援多種樣式配置和填充選項。
    使用新架構的統一 API，整合幾何計算和配置管理功能。
    
    支援的功能：
    - 自定義圓心座標和半徑
    - 多種線條樣式和顏色
    - 填充顏色和透明度控制
    - 問題和說明變體模式
    
    Attributes:
        logger: 模組日誌記錄器
        config: 全域配置物件
        
    Example:
        >>> generator = CircleGenerator()
        >>> params = {
        ...     'variant': 'question',
        ...     'radius': 2.0,
        ...     'center': (1, 1),
        ...     'fill': True,
        ...     'fill_color': 'lightblue'
        ... }
        >>> tikz_code = generator.generate_tikz(params)
        >>> print(tikz_code)
        % 圓形
        \draw[thin, solid, black, fill=lightblue] (1, 1) circle (2);
        
    Note:
        此生成器使用新架構的統一 API，依賴 utils 模組的幾何計算功能。
        所有參數驗證通過 CircleParams 模型進行，確保類型安全。
    """
    
    @classmethod
    def get_name(cls) -> str:
        """獲取圖形類型唯一標識符"""
        return 'circle'
    
    def generate_tikz(self, params: Dict[str, Any]) -> str:
        """生成圓形 TikZ 圖形內容
        
        根據提供的參數生成圓形的 TikZ 代碼，支援自定義圓心、
        半徑、樣式和填充等配置選項。
        
        Args:
            params (Dict[str, Any]): 圓形參數字典，支援的鍵值包括：
                - variant (str): 變體類型，'question' 或 'explanation'
                - radius (float): 圓形半徑，預設為 1.0
                - center (Tuple[float, float]): 圓心座標，預設為 (0, 0)
                - fill (bool): 是否填充，預設為 False
                - fill_color (str): 填充顏色，預設為 'white'
                - line_color (str): 線條顏色，預設為 'black'
                - line_style (str): 線條樣式，預設為 'solid'
                - line_width (str): 線條寬度，預設為 'thin'
                
        Returns:
            str: TikZ 圖形內容（不包含 tikzpicture 環境），
                 包含繪製圓形所需的完整 \draw 命令
                
        Raises:
            ValidationError: 如果參數驗證失敗或包含無效值
            TypeError: 如果參數類型不正確
            
        Example:
            >>> generator = CircleGenerator()
            >>> params = {'radius': 1.5, 'center': (0, 0), 'fill': True}
            >>> result = generator.generate_tikz(params)
            >>> '\\draw[thin, solid, black, fill=white] (0, 0) circle (1.5);' in result
            True
            
            >>> # 自定義樣式範例
            >>> styled_params = {
            ...     'radius': 2.0,
            ...     'center': (1, -1),
            ...     'line_color': 'red',
            ...     'line_width': 'thick',
            ...     'fill': True,
            ...     'fill_color': 'lightgray'
            ... }
            >>> result = generator.generate_tikz(styled_params)
            >>> 'circle (2)' in result
            True
            
        Note:
            生成的 TikZ 代碼使用標準的 circle 命令語法。
            圓心座標支援浮點數精度，樣式參數遵循 TikZ 標準。
        """
        # 使用新架構的參數模型驗證
        try:
            validated_params = CircleParams(**params)
            logger.debug(f"圓形參數驗證成功: radius={validated_params.radius}, center={validated_params.center}")
        except ValidationError as e:
            logger.error(f"圓形參數驗證失敗: {str(e)}")
            raise ValidationError(f"圓形參數驗證失敗: {str(e)}", e.raw_errors)
        
        # 提取參數並使用新架構的幾何類型
        radius = validated_params.radius
        center = Point(*validated_params.center) if hasattr(validated_params, 'center') else Point(0, 0)
        center_x, center_y = center.x, center.y
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
        
        # 使用新架構的幾何計算確保精確度
        center_str = f"({center_x}, {center_y})"
        
        # 繪製圓形
        tikz_content += f"\\draw[{style}] {center_str} circle ({radius});\n"
        
        logger.debug(f"生成圓形 TikZ 代碼: 圓心{center_str}, 半徑{radius}")
        
        return tikz_content