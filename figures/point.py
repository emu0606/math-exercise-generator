#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 點圖形生成器

生成二維平面上的點圖形，支援標籤顯示和樣式自定義。
使用新架構的統一 API 進行幾何計算和渲染。

主要功能：
1. **精確定位**: 在指定座標生成點
2. **標籤支援**: 可選的數學標籤和位置控制
3. **樣式控制**: 顏色、大小、填充/描邊選項
4. **統一 API**: 使用新架構的幾何和渲染系統

Example:
    生成標記點::

        from figures import get_figure_generator
        
        generator = get_figure_generator('point')
        tikz_code = generator.generate_tikz({
            'x': 1.0, 'y': 2.0,
            'label': 'A',
            'label_position': 'above right',
            'variant': 'explanation'
        })

Note:
    此生成器已遷移到新架構 API，使用統一的導入和配置系統。
"""

from typing import Dict, Any
from pydantic import ValidationError

from utils import Point, global_config, get_logger
from .base import FigureGenerator
from . import register_figure_generator
from .params import PointParams

# 使用重構後的參數模型
# 已遷移到新架構: from .params import PointParams

@register_figure_generator
class PointGenerator(FigureGenerator):
    """點圖形生成器
    
    在二維平面上生成精確定位的點圖形，支援標籤顯示和完整的樣式控制。
    使用新架構的統一幾何 API 進行點的創建和渲染。
    
    此生成器提供基礎的點圖形功能，適用於：
    - 標記重要座標位置
    - 作為其他圖形的參考點
    - 幾何圖形的頂點標記
    - 函數圖像上的特殊點
    
    支援功能：
    - 精確的座標定位 (x, y)
    - 可選的數學標籤顯示
    - 靈活的標籤位置控制
    - 多種顏色和樣式選項
    - 可調整的點大小
    
    Example:
        生成帶標籤的點::
        
            generator = PointGenerator()
            tikz_code = generator.generate_tikz({
                'x': 2.5, 'y': 1.8,
                'label': 'P',
                'label_position': 'below left',
                'color': 'blue',
                'size': 0.05,
                'variant': 'explanation'
            })
            
    Note:
        - 使用新架構的 Point 和幾何 API
        - 參數通過重構後的 PointParams 模型驗證
        - 支援全局配置和日誌系統
    """
    
    @classmethod
    def get_name(cls) -> str:
        """獲取圖形類型唯一標識符
        
        Returns:
            str: 固定返回 'point'，用於圖形生成器註冊系統
        """
        return 'point'
    
    def generate_tikz(self, params: Dict[str, Any]) -> str:
        """生成點的 TikZ 圖形內容
        
        使用新架構的統一 API 生成精確定位的點圖形，支援完整的
        標籤和樣式控制。
        
        Args:
            params (Dict[str, Any]): 點參數字典，包含以下鍵值：
                - x (float): 點的 x 座標
                - y (float): 點的 y 座標  
                - label (str, optional): 點的標籤文字
                - label_position (str): 標籤相對位置，如 'above', 'below left'
                - color (str): 點的顏色，預設 'black'
                - size (float): 點的大小半徑，預設 0.03
                - style (str): 繪製樣式，'fill' 或 'draw'
                - variant (str): 變體類型，'question' 或 'explanation'
                
        Returns:
            str: TikZ 圖形內容（不包含 tikzpicture 環境），包含點的繪製指令
            
        Raises:
            ValidationError: 當參數驗證失敗時拋出，包含具體錯誤信息
            
        Example:
            >>> generator = PointGenerator()
            >>> tikz = generator.generate_tikz({
            ...     'x': 1.0, 'y': 2.0, 
            ...     'label': 'A', 
            ...     'color': 'red',
            ...     'variant': 'question'
            ... })
            >>> print(tikz)
            % 點\n\\fill[red] (1.0, 2.0) circle (0.03) node[above] {$A$};\n
            
        Note:
            - 使用重構後的 PointParams 進行參數驗證
            - 整合新架構的 Point 和全局配置系統
            - 支援數學模式的標籤渲染
        """
        # 獲取日誌記錄器
        logger = get_logger(__name__)
        logger.debug(f"生成點圖形，參數: {params}")
        
        # 使用重構後的 PointParams 進行參數驗證
        try:
            validated_params = PointParams(**params)
        except ValidationError as e:
            logger.error(f"點參數驗證失敗: {str(e)}")
            raise ValidationError(f"點參數驗證失敗: {str(e)}", e.raw_errors)
        
        # 使用新架構創建 Point 對象
        point = Point(validated_params.x, validated_params.y)
        
        # 提取樣式參數
        label = validated_params.label
        color = validated_params.color
        size = validated_params.size
        shape = validated_params.shape
        # 預設標籤位置
        label_position = 'above'
        
        # 生成 TikZ 代碼
        tikz_content = "% 點圖形\n"
        
        # 根據形狀和顏色生成繪製指令
        if shape == 'circle':
            tikz_content += f"\\fill[{color}] ({point.x}, {point.y}) circle ({size})"
        elif shape == 'square':
            tikz_content += f"\\fill[{color}] ({point.x}, {point.y}) rectangle ++({size}, {size})"
        else:  # triangle or other
            tikz_content += f"\\fill[{color}] ({point.x}, {point.y}) circle ({size})"
        
        # 添加標籤（如果有）
        if label is not None:
            tikz_content += f" node[{label_position}] {{${label}$}}"
        
        tikz_content += ";\n"
        
        logger.debug(f"生成的 TikZ 內容: {tikz_content.strip()}")
        return tikz_content