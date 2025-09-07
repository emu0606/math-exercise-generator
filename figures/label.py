#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 標籤圖形生成器

本模組提供文字標籤的生成功能，支援數學模式、自定義位置、
旋轉角度、字體大小和顏色等多種樣式配置。
"""

from typing import Dict, Any, Optional
from pydantic import ValidationError
import math

from utils import Point, global_config, get_logger
from .base import FigureGenerator
from .params import LabelParams
from . import register_figure_generator

logger = get_logger(__name__)

@register_figure_generator
class LabelGenerator(FigureGenerator):
    """文字標籤圖形生成器
    
    生成可自定義位置和樣式的文字標籤，支援數學模式、旋轉、
    字體設定和特殊字符處理。使用新架構的統一 API，
    整合幾何計算和日誌系統。
    
    支援的功能：
    - 數學模式和一般文本模式
    - 自定義位置和錨點設定
    - 旋轉角度和字體大小控制
    - 顏色和附加 TikZ 選項
    - LaTeX 特殊字符的自動轉義
    
    Attributes:
        logger: 模組日誌記錄器
        config: 全域配置物件
        
    Example:
        >>> generator = LabelGenerator()
        >>> params = {
        ...     'x': 1.0, 'y': 2.0,
        ...     'text': 'A',
        ...     'math_mode': False
        ... }
        >>> tikz_code = generator.generate_tikz(params)
        >>> 'node' in tikz_code
        True
        >>> 'at (1,2)' in tikz_code
        True
        
        >>> # 數學模式範例
        >>> math_params = {
        ...     'x': 0, 'y': 0,
        ...     'text': 'x^2 + y^2 = r^2',
        ...     'math_mode': True,
        ...     'color': 'red'
        ... }
        >>> result = generator.generate_tikz(math_params)
        >>> '$x^2 + y^2 = r^2$' in result
        True
        
    Note:
        此生成器自動處理 LaTeX 特殊字符的轉義，確保文本正確顯示。
        坐標計算使用新架構的 Point 類型確保精確度。
    """
    
    @classmethod
    def get_name(cls) -> str:
        """獲取圖形類型唯一標識符"""
        return 'label'
    
    def generate_tikz(self, params: Dict[str, Any]) -> str:
        """生成文字標籤 TikZ 圖形內容
        
        生成包含文字內容、位置設定和樣式配置的完整
        TikZ node 命令。
        
        Args:
            params (Dict[str, Any]): 標籤參數字典，支援的鍵值包括：
                - x, y (float): 標籤位置座標
                - text (str): 標籤文字內容
                - math_mode (bool): 是否使用數學模式，預設 False
                - position_modifiers (str, optional): 位置修飾符（如 'above', 'right'）
                - anchor (str, optional): 節點錨點設定
                - rotate (float, optional): 旋轉角度
                - color (str): 文字顏色，預設 'black'
                - font_size (str, optional): 字體大小設定
                - additional_node_options (str, optional): 附加 TikZ 節點選項
                
        Returns:
            str: TikZ 圖形內容（不包含 tikzpicture 環境），
                 包含完整的 \\node 命令
                
        Raises:
            ValidationError: 如果參數驗證失敗或包含無效值
            ValueError: 如果文字內容為空且未允許空標籤
            
        Example:
            >>> generator = LabelGenerator()
            >>> params = {'x': 1.5, 'y': 2.5, 'text': 'Point A'}
            >>> result = generator.generate_tikz(params)
            >>> '\\node[color=black] at (1.5,2.5) {Point A};' in result
            True
            
            >>> # 數學模式和樣式範例
            >>> styled_params = {
            ...     'x': 0, 'y': 1,
            ...     'text': '\\alpha + \\beta',
            ...     'math_mode': True,
            ...     'position_modifiers': 'above',
            ...     'color': 'blue',
            ...     'rotate': 45
            ... }
            >>> result = generator.generate_tikz(styled_params)
            >>> '$\\alpha + \\beta$' in result
            True
            >>> 'above' in result
            True
            >>> 'rotate=45' in result
            True
            
        Note:
            非數學模式下的特殊字符會自動轉義為 LaTeX 安全字符。
            坐標使用 .7g 格式化避免不必要的小數位。
        """
        # 使用新架構的參數模型驗證
        try:
            validated_params = LabelParams(**params)
            logger.debug(f"標籤參數驗證成功: 位置({validated_params.x},{validated_params.y}), 文字='{validated_params.text}'")
        except ValidationError as e:
            logger.error(f"標籤參數驗證失敗: {str(e)}")
            raise
        
        # 使用新架構的 Point 類型處理坐標
        position = Point(validated_params.x, validated_params.y)
        text = validated_params.text
        math_mode = validated_params.math_mode
        
        # 生成 TikZ 代碼
        # tikz_content = "% 標籤\n" # 移除註釋行，生成器只返回命令
        
        # 構建 TikZ node options
        options_list = []
        if validated_params.position_modifiers:
            options_list.append(validated_params.position_modifiers)
        if validated_params.anchor:
            options_list.append(f"anchor={validated_params.anchor}")
        if validated_params.rotate is not None: # rotate=0 is a valid rotation
            options_list.append(f"rotate={validated_params.rotate:.7g}")
        
        # Color is always present, use the one from params (default 'black')
        options_list.append(f"color={validated_params.color}")
            
        if validated_params.font_size:
            options_list.append(f"font={validated_params.font_size}")
        
        if validated_params.additional_node_options:
            options_list.append(validated_params.additional_node_options)
        
        style_str = ", ".join(filter(None, options_list))
        if style_str:
            style_str = f"[{style_str}]"
        
        # 處理文字
        if math_mode:
            # 如果是數學模式，用 $ 包裹文本
            # 假設傳入的 text 是原始文本，不包含 $
            formatted_text = f"${text}$" if text else ""
        else:
            # 如果不是數學模式，直接使用文本
            # TikZ 的 node 文本已經在 {} 中，大多數特殊字符不需要額外轉義
            # 但某些字符如 % 和 \ 仍需要特別處理
            formatted_text = text if text else ""
            
            # 處理可能需要特別注意的字符
            if formatted_text:
                # 處理反斜杠 \
                formatted_text = formatted_text.replace('\\', '\\textbackslash{}')
                # 處理其他特殊字符
                formatted_text = formatted_text.replace('&', '\\&')
                formatted_text = formatted_text.replace('%', '\\%')
                formatted_text = formatted_text.replace('$', '\\$')
                formatted_text = formatted_text.replace('#', '\\#')
                formatted_text = formatted_text.replace('_', '\\_')
                formatted_text = formatted_text.replace('{', '\\{')
                formatted_text = formatted_text.replace('}', '\\}')
                formatted_text = formatted_text.replace('~', '\\textasciitilde{}')
                formatted_text = formatted_text.replace('^', '\\textasciicircum{}')
        
        # 繪製標籤，使用 Point 類型的 to_tikz() 方法
        tikz_content = f"\\node{style_str} at {position.to_tikz()} {{{formatted_text}}};\n"
        
        logger.debug(f"生成標籤 TikZ 代碼: 位置{position.to_tikz()}, 數學模式={math_mode}")
        
        return tikz_content.strip()