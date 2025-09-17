#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 坐標系圖形生成器

本模組提供笛卡爾坐標系的生成功能，支援自定義坐標軸範圍、
網格線顯示、刻度標記和樣式配置等多種功能。
"""

from typing import Dict, Any
from pydantic import ValidationError

from utils import Point, global_config, get_logger
from .base import FigureGenerator
from .params import CoordinateSystemParams
from . import register_figure_generator

logger = get_logger(__name__)


@register_figure_generator
class CoordinateSystemGenerator(FigureGenerator):
    """笛卡爾坐標系圖形生成器
    
    生成二維笛卡爾坐標系，支援自定義坐標軸範圍、網格線、刻度
    標記和箱頭樣式等多種配置選項。使用新架構的統一 API，
    整合幾何計算和日誌系統。
    
    支援的功能：
    - 自定義坐標軸範圍和刻度稀疏度
    - 網格線的顯示和樣式配置
    - 坐標軸標籤和刻度標記
    - 箱頭樣式和顏色自定義
    - 問題和說明變體模式
    
    Attributes:
        logger: 模組日誌記錄器
        config: 全域配置物件
        
    Example:
        >>> generator = CoordinateSystemGenerator()
        >>> params = {
        ...     'x_min': -3, 'x_max': 3,
        ...     'y_min': -3, 'y_max': 3,
        ...     'show_grid': True,
        ...     'show_labels': True
        ... }
        >>> tikz_code = generator.generate_tikz(params)
        >>> 'draw[-stealth' in tikz_code  # 箱頭樣式
        True
        >>> 'grid' in tikz_code  # 網格線
        True
        
    Note:
        此生成器使用 TikZ 的 arrows.meta 庫提供現代化箱頭樣式。
        坐標範圍和刻度計算使用新架構的 Point 類型確保精確度。
    """
    
    @classmethod
    def get_name(cls) -> str:
        """獲取圖形類型唯一標識符"""
        return 'coordinate_system'
    
    def generate_tikz(self, params: Dict[str, Any]) -> str:
        """生成坐標系 TikZ 圖形內容
        
        生成包含坐標軸、網格線、刻度標記和標籤的完整
        笛卡爾坐標系 TikZ 代碼。
        
        Args:
            params (Dict[str, Any]): 坐標系參數字典，支援的鍵值包括：
                - variant (str): 變體類型，'question' 或 'explanation'
                - x_min, x_max (float): X 軸範圍，預設 -5.0 到 5.0
                - y_min, y_max (float): Y 軸範圍，預設 -5.0 到 5.0
                - show_grid (bool): 是否顯示網格線，預設 False
                - show_labels (bool): 是否顯示軸標籤和刻度，預設 True
                - color (str): 坐標軸顏色，預設 'black'
                - grid_color (str): 網格線顏色，預設 'gray!30'
                - x_label, y_label (str): 軸標籤文字，預設 'x', 'y'
                - arrow_style (str): 箱頭樣式，預設 'stealth'
                
        Returns:
            str: TikZ 圖形內容（不包含 tikzpicture 環境），
                 包含完整的坐標系繪製命令
                
        Raises:
            ValidationError: 如果參數驗證失敗或包含無效值
            ValueError: 如果坐標範圍不合理（如 x_min >= x_max）
            
        Example:
            >>> generator = CoordinateSystemGenerator()
            >>> params = {'x_min': -2, 'x_max': 2, 'y_min': -2, 'y_max': 2}
            >>> result = generator.generate_tikz(params)
            >>> 'draw[-stealth, black]' in result
            True
            >>> 'node[right] {$x$}' in result
            True
            
            >>> # 帶網格線的範例
            >>> grid_params = {
            ...     'x_min': -3, 'x_max': 3,
            ...     'y_min': -3, 'y_max': 3,
            ...     'show_grid': True,
            ...     'grid_color': 'lightgray'
            ... }
            >>> result = generator.generate_tikz(grid_params)
            >>> 'grid' in result
            True
            
        Note:
            網格線的稀疏度固定為 1 單位，刻度標記只在整數位置顯示。
            使用 TikZ arrows.meta 庫提供現代化箱頭樣式。
        """
        # 使用新架構的參數模型驗證
        try:
            validated_params = CoordinateSystemParams(**params)
            logger.debug(f"坐標系參數驗證成功: 範圍{validated_params.x_range} x {validated_params.y_range}")
        except ValidationError as e:
            logger.error(f"坐標系參數驗證失敗: {str(e)}")
            raise ValidationError(f"坐標系參數驗證失敗: {str(e)}", e.raw_errors)
        
        # 提取參數並進行合理性檢查
        x_min, x_max = validated_params.x_range
        y_min, y_max = validated_params.y_range
        
        # 使用新架構驗證坐標範圍合理性
        if x_min >= x_max or y_min >= y_max:
            error_msg = f"坐標範圍不合理: X({x_min}, {x_max}), Y({y_min}, {y_max})"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        show_grid = validated_params.show_grid
        show_axes_labels = validated_params.show_axes_labels
        axes_color = validated_params.axes_color
        grid_color = validated_params.grid_color
        x_label = validated_params.x_label
        y_label = validated_params.y_label
        
        # 使用 Point 類型計算關鍵坐標
        origin = Point(0, 0)
        x_min_point = Point(x_min, 0)
        x_max_point = Point(x_max, 0)
        y_min_point = Point(0, y_min)
        y_max_point = Point(0, y_max)
        
        # 生成 TikZ 代碼
        tikz_content = "% 坐標系\n"
        
        # 添加 TikZ 庫
        tikz_content += "\\usetikzlibrary{arrows.meta}\n\n"
        
        # 繪製網格（如果需要）
        if show_grid:
            grid_min = Point(x_min, y_min)
            grid_max = Point(x_max, y_max)
            tikz_content += f"\\draw[{grid_color}, step=1] {grid_min.to_tikz()} grid {grid_max.to_tikz()};\n"
        
        # 繪製坐標軸（使用 Point 類型的座標）
        x_label_node = f" node[right] {{${x_label}$}}" if show_axes_labels else ""
        y_label_node = f" node[above] {{${y_label}$}}" if show_axes_labels else ""

        tikz_content += f"\\draw[-stealth, {axes_color}] {x_min_point.to_tikz()} -- {x_max_point.to_tikz()}{x_label_node};\n"
        tikz_content += f"\\draw[-stealth, {axes_color}] {y_min_point.to_tikz()} -- {y_max_point.to_tikz()}{y_label_node};\n"

        # 繪製刻度（如果需要）
        if show_axes_labels:
            # X 軸刻度（使用 Point 類型確保精確度）
            for i in range(int(x_min) + 1, int(x_max)):
                if i != 0:  # 跳過原點
                    tick_bottom = Point(i, -0.1)
                    tick_top = Point(i, 0.1)
                    tikz_content += f"\\draw[{axes_color}] {tick_bottom.to_tikz()} -- {tick_top.to_tikz()} node[below] {{${i}$}};\n"
            
            # Y 軸刻度（使用 Point 類型確保精確度）
            for i in range(int(y_min) + 1, int(y_max)):
                if i != 0:  # 跳過原點
                    tick_left = Point(-0.1, i)
                    tick_right = Point(0.1, i)
                    tikz_content += f"\\draw[{axes_color}] {tick_left.to_tikz()} -- {tick_right.to_tikz()} node[left] {{${i}$}};\n"
        
        logger.debug(f"生成坐標系 TikZ 代碼: 範圍({x_min},{y_min})-({x_max},{y_max}), 網格={show_grid}")
        
        return tikz_content