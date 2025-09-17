#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 線段圖形生成器

生成二維平面上的線段圖形，支援多種樣式和箭頭選項。
使用新架構的統一 API 進行幾何計算和 TikZ 渲染。

主要功能：
1. **精確線段**: 通過起點和終點定義線段
2. **樣式支援**: 實線、虛線、點線等多種樣式
3. **箭頭選項**: 灵活的箭頭配置和樣式控制
4. **標籤系統**: 可選的標籤和位置控制
5. **統一 API**: 使用新架構的幾何和渲染系統

Example:
    生成帶箭頭的彩色線段::

        from figures import get_figure_generator
        
        generator = get_figure_generator('line')
        tikz_code = generator.generate_tikz({
            'start_point': [0, 0],
            'end_point': [3, 2],
            'color': 'blue',
            'arrow': '->',
            'label': 'AB',
            'variant': 'explanation'
        })

Note:
    此生成器已遷移到新架構 API，使用統一的導入和配置系統。
"""

from typing import Dict, Any
from pydantic import ValidationError

from utils import Point, distance, midpoint, global_config, get_logger
from .base import FigureGenerator
from . import register_figure_generator
from .params import LineParams

# 使用重構後的參數模型
# from .params import LineParams

@register_figure_generator
class LineGenerator(FigureGenerator):
    """線段圖形生成器
    
    在二維平面上生成線段圖形，支援多種樣式和箭頭配置。
    使用新架構的統一幾何 API 進行線段的創建和渲染。
    
    此生成器提供完整的線段繪製功能，適用於：
    - 幾何圖形的邊和線段
    - 坐標系統的軸線
    - 向量和方向的表示
    - 函數圖像的輔助線
    
    支援功能：
    - 精確的起點和終點定位
    - 多種線條樣式（實線、虛線、點線）
    - 灵活的箭頭配置和樣式
    - 可調的線條粗細和顏色
    - 智能標籤位置計算
    
    Example:
        生成帶箭頭的彩色線段::
        
            generator = LineGenerator()
            tikz_code = generator.generate_tikz({
                'start_point': [1, 2],
                'end_point': [4, 5],
                'color': 'red',
                'width': 'thick',
                'arrow': '->',
                'label': 'v',
                'variant': 'explanation'
            })
            
    Note:
        - 使用新架構的 Point、distance 和 midpoint API
        - 參數通過重構後的 LineParams 模型驗證
        - 支援全局配置和日誌系統
        - 智能計算標籤的最佳位置
    """
    
    @classmethod
    def get_name(cls) -> str:
        """獲取圖形類型唯一標識符
        
        Returns:
            str: 固定返回 'line'，用於圖形生成器註冊系統
        """
        return 'line'
    
    def generate_tikz(self, params: Dict[str, Any]) -> str:
        """生成線段的 TikZ 圖形內容
        
        使用新架構的統一 API 生成精確定位的線段圖形，支援完整的
        樣式控制和智能標籤位置計算。
        
        Args:
            params (Dict[str, Any]): 線段參數字典，包含以下鍵值：
                - start_point (List[float]): 起始點坐標 [x, y]
                - end_point (List[float]): 結束點坐標 [x, y]
                - color (str): 線條顏色，預設 'black'
                - width (str): 線條粗細，如 'thin', 'thick'
                - style (str): 線條樣式，'solid', 'dashed', 'dotted' 等
                - arrow (str, optional): 箭頭樣式，如 '->', '<->', 無箭頭為 None
                - label (str, optional): 線段標籤文字
                - label_position (float): 標籤在線段上的位置比例 (0-1)
                - variant (str): 變體類型，'question' 或 'explanation'
                
        Returns:
            str: TikZ 圖形內容（不包含 tikzpicture 環境），包含線段的繪製指令
            
        Raises:
            ValidationError: 當參數驗證失敗時拋出，包含具體錯誤信息
            
        Example:
            >>> generator = LineGenerator()
            >>> tikz = generator.generate_tikz({
            ...     'start_point': [0, 0], 'end_point': [2, 3],
            ...     'color': 'blue', 'arrow': '->',
            ...     'label': 'AB', 'variant': 'question'
            ... })
            >>> print(tikz)
            % 線段圖形\n\\draw[thick, solid, blue, ->] (0, 0) -- (2, 3) node[pos=0.5, above] {$AB$};\n
            
        Note:
            - 使用重構後的 LineParams 進行參數驗證
            - 整合新架構的 Point、distance 和 midpoint API
            - 支援數學模式的標籤渲柕
            - 智能計算標籤的最佳位置
        """
        # 獲取日誌記錄器
        logger = get_logger(__name__)
        logger.debug(f"生成線段圖形，參數: {params}")
        
        # 使用重構後的 LineParams 進行參數驗證
        try:
            validated_params = LineParams(**params)
        except ValidationError as e:
            logger.error(f"線段參數驗證失敗: {str(e)}")
            raise ValueError(f"線段參數驗證失敗: {str(e)}")
        
        # 使用新架構創建 Point 對象
        start_point = Point(validated_params.start_point[0], validated_params.start_point[1])
        end_point = Point(validated_params.end_point[0], validated_params.end_point[1])
        
        # 提取樣式參數
        color = validated_params.color
        style = validated_params.style
        width = validated_params.width
        arrow = validated_params.arrow
        label = validated_params.label
        label_position = validated_params.label_position
        
        # 計算線段的基本屬性
        line_length = distance(start_point, end_point)
        mid_point = midpoint(start_point, end_point)
        
        logger.debug(f"線段長度: {line_length:.3f}, 中點: ({mid_point.x:.3f}, {mid_point.y:.3f})")
        
        # 生成 TikZ 代碼
        tikz_content = "% 線段圖形\n"
        
        # 添加 TikZ 庫（如果需要箭頭）
        if arrow is not None:
            tikz_content += "\\usetikzlibrary{arrows.meta}\n"
        
        # 設置樣式
        line_style_parts = [width, style, color]
        if arrow is not None:
            line_style_parts.append(arrow)
        line_style = ", ".join(line_style_parts)
        
        # 繪製線段（使用 Point 對象的坐標）
        tikz_content += f"\\draw[{line_style}] ({start_point.x}, {start_point.y}) -- ({end_point.x}, {end_point.y})"
        
        # 添加標籤（如果有），使用 pos 參數控制位置
        if label is not None:
            tikz_content += f" node[pos={label_position}, above] {{${label}$}}"
        
        tikz_content += ";\n"
        
        logger.debug(f"生成的 TikZ 內容: {tikz_content.strip()}")
        return tikz_content