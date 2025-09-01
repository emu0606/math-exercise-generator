#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 圖形生成器基礎類別
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, ClassVar


class FigureGenerator(ABC):
    """圖形生成器抽象基類
    
    所有具體圖形生成器都應該繼承此類別並實現其抽象方法。
    """
    
    @abstractmethod
    def generate_tikz(self, params: Dict[str, Any]) -> str:
        """生成 TikZ 圖形內容
        
        注意：此方法應該只生成 TikZ 圖形的內容，不包含 \\begin{tikzpicture} 和 \\end{tikzpicture}。
        應首先使用 Pydantic 模型驗證 params，然後根據驗證後的參數生成圖形。
        
        Args:
            params: 圖形參數字典
            
        Returns:
            TikZ 圖形內容（不包含 tikzpicture 環境）
        """
        pass
    
    @classmethod
    @abstractmethod
    def get_name(cls) -> str:
        """獲取圖形類型唯一標識符
        
        Returns:
            圖形類型唯一標識符
        """
        pass