#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 圖形生成器基礎類別

此模組定義了所有圖形生成器必須實現的抽象基礎類別。
圖形生成器負責將數學參數轉換為 TikZ 圖形代碼，用於 LaTeX 文檔中的圖形渲染。

所有具體的圖形生成器都應該繼承 `FigureGenerator` 並實現其抽象方法。
這確保了統一的接口和一致的行為模式。

Example:
    創建自定義圖形生成器::

        from figures.base import FigureGenerator
        from figures import register_figure_generator

        @register_figure_generator
        class MyCustomGenerator(FigureGenerator):
            @classmethod
            def get_name(cls) -> str:
                return "my_custom_figure"
            
            def generate_tikz(self, params: Dict[str, Any]) -> str:
                # 實現具體的圖形生成邏輯
                return "\\draw (0,0) circle (1);"

Note:
    此模組是圖形生成系統的核心，所有圖形生成器都必須遵循此接口。
    新架構鼓勵使用 `from utils import` 統一 API 進行幾何計算。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, ClassVar


class FigureGenerator(ABC):
    """圖形生成器抽象基類
    
    定義了所有圖形生成器必須實現的統一接口。每個具體的圖形生成器
    都應該繼承此類別並實現 `generate_tikz` 和 `get_name` 方法。
    
    此基類確保了：
    1. 統一的圖形生成接口
    2. 一致的命名規範
    3. 標準化的參數處理流程
    4. 與註冊系統的兼容性
    
    Attributes:
        此抽象基類不包含實例屬性，所有屬性由具體實現定義。
        
    Example:
        實現自定義圖形生成器::
        
            class CircleGenerator(FigureGenerator):
                @classmethod
                def get_name(cls) -> str:
                    return "circle"
                
                def generate_tikz(self, params: Dict[str, Any]) -> str:
                    radius = params.get('radius', 1.0)
                    return f"\\draw (0,0) circle ({radius});"
    
    Note:
        - 此類使用 ABC (Abstract Base Class) 確保方法必須被實現
        - 生成的 TikZ 代碼不應包含 tikzpicture 環境
        - 推薦使用 Pydantic 模型驗證輸入參數
        - 新架構鼓勵使用統一的 `utils` API 進行計算
    """
    
    @abstractmethod
    def generate_tikz(self, params: Dict[str, Any]) -> str:
        """生成 TikZ 圖形內容
        
        這是圖形生成器的核心方法，負責將輸入參數轉換為對應的 TikZ 代碼。
        生成的代碼將用於 LaTeX 文檔中的圖形渲染。
        
        實現此方法時應該：
        1. 使用 Pydantic 模型驗證輸入參數
        2. 執行必要的數學計算（推薦使用 `utils` API）
        3. 生成符合 TikZ 語法的代碼
        4. 確保代碼不包含 tikzpicture 環境本身
        
        Args:
            params (Dict[str, Any]): 圖形參數字典，包含生成圖形所需的所有資訊。
                具體參數根據不同的圖形類型而異，但通常包含：
                - 'variant': 圖形變體 ('question' 或 'explanation')
                - 幾何參數（座標、長度、角度等）
                - 樣式參數（顏色、線型等）
                
        Returns:
            str: TikZ 圖形內容，不包含 \\begin{tikzpicture} 和 \\end{tikzpicture} 環境。
                返回的字符串應該是有效的 TikZ 命令序列。
                
        Raises:
            ValidationError: 當輸入參數驗證失敗時
            ValueError: 當參數值無效或無法生成有效圖形時
            GeometryError: 當幾何計算失敗時（使用新架構 API 時）
            
        Example:
            典型的實現模式::
            
                def generate_tikz(self, params: Dict[str, Any]) -> str:
                    # 1. 參數驗證
                    validated = MyParams(**params)
                    
                    # 2. 數學計算
                    from utils import construct_triangle
                    triangle = construct_triangle("sss", ...)
                    
                    # 3. 生成 TikZ 代碼
                    tikz_lines = []
                    tikz_lines.append("\\draw (0,0) -- (1,0) -- (0.5,0.866) -- cycle;")
                    return "\\n".join(tikz_lines)
        
        Note:
            - 此方法是抽象方法，必須在子類中實現
            - 建議使用新架構的統一 API 進行數學計算
            - 生成的 TikZ 代碼應該相對座標，由外部系統處理絕對定位
        """
        pass
    
    @classmethod
    @abstractmethod
    def get_name(cls) -> str:
        """獲取圖形類型唯一標識符
        
        返回此圖形生成器的唯一標識符，用於註冊系統中的識別和查找。
        此標識符必須在整個系統中唯一，並且應該具有描述性。
        
        命名規範：
        - 使用小寫字母和下底線
        - 描述性且簡潔
        - 避免與現有生成器衝突
        
        Returns:
            str: 圖形類型的唯一標識符，如 "unit_circle"、"basic_triangle"、
                "coordinate_system" 等。
                
        Example:
            典型的實現::
            
                @classmethod
                def get_name(cls) -> str:
                    return "my_custom_figure"
        
        Note:
            - 此方法是類方法和抽象方法，必須在子類中實現
            - 返回的名稱用於 `@register_figure_generator` 註冊系統
            - 名稱一旦確定後不應輕易更改，以免破壞現有配置
        """
        pass