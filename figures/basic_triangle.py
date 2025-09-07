#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 基礎三角形生成器
"""

from typing import Dict, Any
from pydantic import ValidationError

from utils import (
    Point, Triangle, distance, midpoint,
    area_of_triangle, get_centroid,
    global_config, get_logger
)
from .base import FigureGenerator
from . import register_figure_generator
from .params import BasicTriangleParams

@register_figure_generator
class BasicTriangleGenerator(FigureGenerator):
    """基礎三角形圖形生成器
    
    在二維平面上生成基礎三角形圖形，支援多種樣式和顯示選項。
    使用新架構的統一幾何 API 進行三角形的創建和渲染。
    
    此生成器提供完整的三角形繪製功能，適用於：
    - 基本幾何圖形教學
    - 三角形性質演示
    - 幾何問題的圖形表示
    - 數學測驗的輔助圖形
    
    支援功能：
    - 精確的頂點座標定位
    - 多種填充和邊框樣式
    - 幾何屬性計算（面積、重心等）
    - 智能樣式配置和顏色管理
    - 統一的 TikZ 渲染輸出
    
    Example:
        生成帶填充的彩色三角形::
        
            generator = BasicTriangleGenerator()
            tikz_code = generator.generate_tikz({
                'p1': (0, 0),
                'p2': (3, 0), 
                'p3': (1.5, 2.6),
                'fill_color': 'lightblue',
                'draw_options': 'thick,blue',
                'variant': 'explanation'
            })
            
    Note:
        - 使用新架構的 Point、Triangle 和幾何計算 API
        - 參數通過重構後的 BasicTriangleParams 模型驗證
        - 支援全局配置和日誌系統
        - 整合先進的三角形幾何計算功能
    """

    @classmethod
    def get_name(cls) -> str:
        """獲取圖形類型唯一標識符
        
        Returns:
            str: 固定返回 'basic_triangle'，用於圖形生成器註冊系統
        """
        return "basic_triangle"

    def generate_tikz(self, params: Dict[str, Any]) -> str:
        """生成基礎三角形的 TikZ 圖形內容
        
        使用新架構的統一 API 生成精確定位的三角形圖形，支援完整的
        樣式控制和先進的幾何計算功能。
        
        Args:
            params (Dict[str, Any]): 三角形參數字典，包含以下鍵值：
                - p1 (tuple): 第一個頂點座標 (x, y)
                - p2 (tuple): 第二個頂點座標 (x, y)
                - p3 (tuple): 第三個頂點座標 (x, y)
                - draw_options (str, optional): TikZ 繪製選項，如 'thick,blue'
                - fill_color (str, optional): 填充顏色，如 'blue!30'
                - variant (str): 變體類型，'question' 或 'explanation'
                
        Returns:
            str: TikZ 圖形內容（不包含 tikzpicture 環境），包含三角形的繪製指令
            
        Raises:
            ValidationError: 當參數驗證失敗時拋出，包含具體錯誤信息
            
        Example:
            >>> generator = BasicTriangleGenerator()
            >>> tikz = generator.generate_tikz({
            ...     'p1': (0, 0), 'p2': (2, 0), 'p3': (1, 1.732),
            ...     'fill_color': 'red!20', 'variant': 'question'
            ... })
            >>> print(tikz)
            % 基礎三角形圖形
            \\draw[fill=red!20] (0,0) -- (2,0) -- (1,1.732) -- cycle;
            
        Note:
            - 使用重構後的 BasicTriangleParams 進行參數驗證
            - 整合新架構的 Point、Triangle 和幾何計算 API
            - 支援面積、重心等幾何屬性的自動計算
            - 智能格式化座標以處理浮點精度問題
        """
        # 獲取日誌記錄器
        logger = get_logger(__name__)
        logger.debug(f"生成基礎三角形圖形，參數: {params}")
        
        # 使用重構後的 BasicTriangleParams 進行參數驗證
        try:
            validated_params = BasicTriangleParams(**params)
        except ValidationError as e:
            logger.error(f"三角形參數驗證失敗: {str(e)}")
            raise
        
        # 使用新架構創建 Point 和 Triangle 對象
        p1 = Point(validated_params.p1[0], validated_params.p1[1])
        p2 = Point(validated_params.p2[0], validated_params.p2[1])
        p3 = Point(validated_params.p3[0], validated_params.p3[1])
        
        # 創建 Triangle 對象進行幾何計算
        triangle = Triangle(p1, p2, p3)
        
        # 計算三角形的基本屬性（用於日誌和可能的擴展功能）
        area = area_of_triangle(triangle)
        centroid = get_centroid(triangle)
        
        logger.debug(f"三角形面積: {area:.3f}, 重心: ({centroid.x:.3f}, {centroid.y:.3f})")
        
        # 構建繪製選項
        draw_options_list = []
        if validated_params.draw_options:
            draw_options_list.append(validated_params.draw_options)
        
        if validated_params.fill_color:
            draw_options_list.append(f"fill={validated_params.fill_color}")

        final_draw_options = ", ".join(filter(None, draw_options_list))
        if final_draw_options:
            final_draw_options = f"[{final_draw_options}]"
        
        # 生成 TikZ 代碼
        tikz_content = "% 基礎三角形圖形\n"
        
        # TikZ 座標格式 (x,y), 使用 .7g 進行格式化以處理浮點精度
        tikz_p1 = f"({p1.x:.7g},{p1.y:.7g})"
        tikz_p2 = f"({p2.x:.7g},{p2.y:.7g})" 
        tikz_p3 = f"({p3.x:.7g},{p3.y:.7g})"

        # 繪製三角形：\draw[options] (x1,y1) -- (x2,y2) -- (x3,y3) -- cycle;
        tikz_content += f"\\draw{final_draw_options} {tikz_p1} -- {tikz_p2} -- {tikz_p3} -- cycle;\n"
        
        # 根據 variant 的擴展處理（為未來功能預留）
        if validated_params.variant == 'explanation':
            # 可在詳解模式下添加額外的幾何信息標註
            logger.debug("詳解模式：可添加面積、角度等額外信息")
        
        logger.debug(f"生成的 TikZ 內容: {tikz_content.strip()}")
        return tikz_content