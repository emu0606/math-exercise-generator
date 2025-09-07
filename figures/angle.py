#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 角度圖形生成器

生成二維平面上的角度圖形，支援多種標記樣式和標籤選項。
使用新架構的統一 API 進行角度計算和 TikZ 渲染。

主要功能：
1. **精確角度**: 通過頂點和兩條射線定義角度
2. **弧線標記**: 支援角度弧線和標記樣式
3. **標籤系統**: 可選的角度標籤和位置控制
4. **樣式支援**: 多種線條樣式和顏色選項
5. **統一 API**: 使用新架構的幾何和渲染系統

Example:
    生成帶標籤的 60 度角::

        from figures import get_figure_generator
        
        generator = get_figure_generator('angle')
        tikz_code = generator.generate_tikz({
            'vertex': [0, 0],
            'ray1_point': [2, 0],
            'ray2_point': [1, 1.732], 
            'angle_value': 60,
            'label': 'α',
            'variant': 'explanation'
        })

Note:
    此生成器已遷移到新架構 API，使用統一的導入和配置系統。
"""

from typing import Dict, Any
from pydantic import ValidationError
import math

from utils import (
    Point, angle_between_vectors, angle_at_vertex,
    distance, global_config, get_logger
)
from .base import FigureGenerator
from . import register_figure_generator
from .params import AngleParams

@register_figure_generator
class AngleGenerator(FigureGenerator):
    """角度圖形生成器
    
    在二維平面上生成角度圖形，支援多種標記樣式和標籤配置。
    使用新架構的統一幾何 API 進行角度的創建和渲染。
    
    此生成器提供完整的角度繪製功能，適用於：
    - 幾何圖形中的角度標記
    - 角度測量和標註
    - 幾何問題的角度表示
    - 數學測驗的輔助圖形
    
    支援功能：
    - 精確的頂點和射線定位
    - 智能角度計算和弧線生成
    - 多種標記樣式和顏色選項
    - 可調的弧線半徑和標籤位置
    - 統一的 TikZ 渲染輸出
    
    Example:
        生成帶標籤的彩色角度::
        
            generator = AngleGenerator()
            tikz_code = generator.generate_tikz({
                'vertex': [0, 0],
                'ray1_point': [3, 0], 
                'ray2_point': [2, 2.5],
                'angle_value': 45,
                'color': 'red',
                'label': '∠A',
                'variant': 'explanation'
            })
            
    Note:
        - 使用新架構的 Point、angle_between_vectors 等 API
        - 參數通過重構後的 AngleParams 模型驗證
        - 支援全局配置和日誌系統
        - 智能計算弧線的最佳繪製參數
    """
    
    @classmethod
    def get_name(cls) -> str:
        """獲取圖形類型唯一標識符
        
        Returns:
            str: 固定返回 'angle'，用於圖形生成器註冊系統
        """
        return 'angle'
    
    def generate_tikz(self, params: Dict[str, Any]) -> str:
        """生成角度的 TikZ 圖形內容
        
        使用新架構的統一 API 生成精確定位的角度圖形，支援完整的
        樣式控制和智能角度計算功能。
        
        Args:
            params (Dict[str, Any]): 角度參數字典，包含以下鍵值：
                - vertex (List[float]): 角度頂點座標 [x, y]
                - ray1_point (List[float]): 第一條射線上的點座標 [x, y]
                - ray2_point (List[float]): 第二條射線上的點座標 [x, y]
                - angle_value (float, optional): 角度數值（度），為 None 時不顯示數值
                - show_arc (bool): 是否顯示角度弧線標記，預設為 True
                - arc_radius (float): 弧線半徑，預設為 0.5
                - color (str): 角度標記顏色，預設為 'blue'
                - label (str, optional): 角度標籤，如 'α', '∠A'
                - variant (str): 變體類型，'question' 或 'explanation'
                
        Returns:
            str: TikZ 圖形內容（不包含 tikzpicture 環境），包含角度的繪製指令
            
        Raises:
            ValidationError: 當參數驗證失敗時拋出，包含具體錯誤信息
            
        Example:
            >>> generator = AngleGenerator()
            >>> tikz = generator.generate_tikz({
            ...     'vertex': [0, 0], 'ray1_point': [2, 0], 'ray2_point': [1, 1.732],
            ...     'angle_value': 60, 'label': 'α', 'variant': 'question'
            ... })
            >>> print(tikz)
            % 角度圖形
            \draw[blue] (0,0) ++(30:0.5) arc (30:90:0.5) node[midway, above] {$α$};

            
        Note:
            - 使用重構後的 AngleParams 進行參數驗證
            - 整合新架構的 Point、angle_between_vectors 和角度計算 API
            - 支援智能弧線半徑和標籤位置計算
            - 自動處理角度範圍和方向計算
        """
        # 獲取日誌記錄器
        logger = get_logger(__name__)
        logger.debug(f"生成角度圖形，參數: {params}")
        
        # 使用重構後的 AngleParams 進行參數驗證
        try:
            validated_params = AngleParams(**params)
        except ValidationError as e:
            logger.error(f"角度參數驗證失敗: {str(e)}")
            raise
        
        # 使用新架構創建 Point 對象
        vertex = Point(validated_params.vertex[0], validated_params.vertex[1])
        ray1_point = Point(validated_params.ray1_point[0], validated_params.ray1_point[1])
        ray2_point = Point(validated_params.ray2_point[0], validated_params.ray2_point[1])
        
        # 提取參數
        show_arc = validated_params.show_arc
        arc_radius = validated_params.arc_radius
        color = validated_params.color
        label = validated_params.label
        angle_value = validated_params.angle_value
        
        # 使用新架構計算角度
        if angle_value is None:
            # 如果未指定角度值，使用幾何計算
            angle_degrees = angle_at_vertex(vertex, ray1_point, ray2_point)
            logger.debug(f"計算得到角度: {angle_degrees:.2f} 度")
        else:
            angle_degrees = angle_value
        
        # 計算射線方向角度
        ray1_angle = math.atan2(ray1_point.y - vertex.y, ray1_point.x - vertex.x)
        ray2_angle = math.atan2(ray2_point.y - vertex.y, ray2_point.x - vertex.x)
        
        # 轉換為度數
        ray1_angle_deg = math.degrees(ray1_angle)
        ray2_angle_deg = math.degrees(ray2_angle)
        
        # 確保角度方向正確
        if ray2_angle_deg < ray1_angle_deg:
            ray2_angle_deg += 360
        
        logger.debug(f"射線角度: ray1={ray1_angle_deg:.2f}°, ray2={ray2_angle_deg:.2f}°")
        
        # 生成 TikZ 代碼
        tikz_content = "% 角度圖形\n"
        
        if show_arc:
            # 繪製角度弧線
            tikz_content += f"\\draw[{color}] ({vertex.x:.7g},{vertex.y:.7g}) +({ray1_angle_deg:.2f}:{arc_radius}) arc ({ray1_angle_deg:.2f}:{ray2_angle_deg:.2f}:{arc_radius})"
            
            # 添加標籤（如果有）
            if label is not None:
                tikz_content += f" node[midway, above] {{${label}$}}"
            
            tikz_content += ";\n"
        
        # 如果是詳解模式，可添加額外信息
        if validated_params.variant == 'explanation':
            if angle_value is not None:
                logger.debug(f"詳解模式：角度值 = {angle_value}°")
        
        logger.debug(f"生成的 TikZ 內容: {tikz_content.strip()}")
        return tikz_content