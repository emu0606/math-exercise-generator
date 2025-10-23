#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - LaTeX 配置類別
集中管理 LaTeX 生成相關的配置參數
"""

from typing import Dict, Any, Optional
from datetime import datetime

class LaTeXConfig:
    """LaTeX 配置類別
    
    集中管理 LaTeX 生成相關的配置參數，包括頁面尺寸、網格定義、間距等。
    提供計算派生屬性的功能，如可用寬度、單元格尺寸等。
    """
    
    def __init__(self,
                 page_width: float = 21.0,  # A4 紙寬度（厘米）
                 page_height: float = 29.7,  # A4 紙高度（厘米）
                 margin: float = 1.8,  # 邊距（厘米）
                 grid_width: int = 4,  # 網格列數
                 grid_height: int = 10,  # 網格行數（從 8 改為 10）
                 gap: float = 0.3,  # 網格間隔（厘米，從 0.5 改為 0.3）
                 font_path: str = "./assets/fonts/"):  # 字體路徑
        """初始化 LaTeX 配置

        Args:
            page_width: 頁面寬度（厘米），預設為 A4 紙寬度 21.0 厘米
            page_height: 頁面高度（厘米），預設為 A4 紙高度 29.7 厘米
            margin: 頁面邊距（厘米），預設為 1.8 厘米
            grid_width: 網格列數，預設為 4
            grid_height: 網格行數，預設為 10（4x10 網格）
            gap: 網格間隔（厘米），預設為 0.3 厘米
            font_path: 字體路徑，預設為 "./assets/fonts/"
        """
        # 基本參數
        self.page_width = page_width
        self.page_height = page_height
        self.margin = margin
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.gap = gap
        self.font_path = font_path

        # 計算派生屬性 - 寬度
        self.usable_width = self.page_width - 2 * self.margin  # 可用寬度（厘米）
        self.total_gap_width = (self.grid_width - 1) * self.gap  # 總間隔寬度（厘米）
        self.unit_width = round((self.usable_width - self.total_gap_width) / self.grid_width, 3)  # 單元格寬度（厘米）

        # 新增：定義結構高度常數
        self.header_height = 1.5  # 頁首固定高度（cm）
        self.footer_height = 1.0  # 頁尾固定高度（cm）

        # 新增：計算可用垂直空間
        self.usable_height = self.page_height - (2 * self.margin) - self.header_height - self.footer_height

        # 修正：基於可用空間計算單元格高度
        self.total_gap_height = (self.grid_height - 1) * self.gap
        self.unit_height = round((self.usable_height - self.total_gap_height) / self.grid_height, 3)

    def get_current_date(self) -> str:
        """獲取當前日期字符串
        
        Returns:
            格式化的當前日期字符串（YYYY-MM-DD）
        """
        return datetime.now().strftime("%Y-%m-%d")