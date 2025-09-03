#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 基礎生成器類別
"""

import random
from abc import ABC, abstractmethod
from enum import IntEnum
from typing import Dict, List, Any, Tuple, Optional, Union, Type, ClassVar



class QuestionSize(IntEnum):
    """題目大小枚舉
    
    定義六種不同的大小空間：
    SMALL: 一單位大小
    WIDE: 左右兩單位，上下一單位
    SQUARE: 左右一單位，上下兩單位
    MEDIUM: 左右兩單位，上下兩單位
    LARGE: 左右三單位，上下兩單位
    EXTRA: 左右四單位，上下兩單位
    """
    SMALL = 1        # 一單位大小
    WIDE = 2  # 左右兩單位，上下一單位
    SQUARE = 3  # 左右一單位，上下兩單位
    MEDIUM = 4       # 左右兩單位，上下兩單位
    LARGE = 5        # 左右三單位，上下兩單位
    EXTRA = 6  # 左右四單位，上下兩單位




class QuestionGenerator(ABC):
    """題目生成器基礎類別
    
    所有具體題目生成器都應該繼承此類別並實現其抽象方法。
    """
    
    # 類別屬性，用於自動註冊
    auto_register: ClassVar[bool] = True
    
    def __init__(self, options: Dict[str, Any] = None):
        """初始化生成器
        
        Args:
            options: 其他選項，如特定範圍、特定運算符等
        """
        self.options = options or {}
        
    @abstractmethod
    def generate_question(self) -> Dict[str, Any]:
        """生成一個題目
        
        Returns:
            包含題目資訊的字典，至少應包含以下鍵：
            - 'question': 題目文字
            - 'answer': 答案
            - 'explanation': 解析
            - 'size': 題目大小（QuestionSize 枚舉值）
        """
        pass
    
    @abstractmethod
    def get_question_size(self) -> int:
        """獲取題目大小
        
        Returns:
            題目大小（使用 QuestionSize 枚舉值）
        """
        pass
    
    @abstractmethod
    def get_category(self) -> str:
        """獲取題目類別
        
        Returns:
            題目類別名稱
        """
        pass
    
    @abstractmethod
    def get_subcategory(self) -> str:
        """獲取題目子類別
        
        Returns:
            題目子類別名稱
        """
        pass
    
    def generate_batch(self, count: int) -> List[Dict[str, Any]]:
        """生成一批題目
        
        Args:
            count: 題目數量
            
        Returns:
            題目列表
        """
        return [self.generate_question() for _ in range(count)]
    
    def set_options(self, options: Dict[str, Any]) -> None:
        """設置選項
        
        Args:
            options: 選項字典
        """
        self.options = options
        
    def get_param_range(self, param_name: str, default_range: Tuple[int, int]) -> Tuple[int, int]:
        """獲取參數範圍
        
        Args:
            param_name: 參數名稱，用於從 options 中查找
            default_range: 預設範圍
            
        Returns:
            參數範圍 (最小值, 最大值)
        """
        # 檢查 options 中是否有指定範圍
        if param_name in self.options:
            return self.options[param_name]
        
        # 使用預設範圍
        return default_range
    
    def format_question(self, template: str, **kwargs) -> str:
        """格式化題目文字
        
        Args:
            template: 題目模板
            **kwargs: 模板參數
            
        Returns:
            格式化後的題目文字
        """
        return template.format(**kwargs)
    
    def format_latex(self, expression: str) -> str:
        """格式化 LaTeX 表達式
        
        Args:
            expression: LaTeX 表達式
            
        Returns:
            格式化後的 LaTeX 表達式
        """
        return f"${expression}$"
    
    def random_int(self, min_val: int, max_val: int, exclude: List[int] = None) -> int:
        """生成隨機整數
        
        Args:
            min_val: 最小值
            max_val: 最大值
            exclude: 排除的值列表
            
        Returns:
            隨機整數
        """
        if exclude is None:
            exclude = []
            
        if min_val > max_val:
            min_val, max_val = max_val, min_val
            
        if max_val - min_val + 1 <= len(exclude):
            raise ValueError("排除的值太多，無法生成隨機數")
            
        while True:
            num = random.randint(min_val, max_val)
            if num not in exclude:
                return num
                
    def random_float(self, min_val: float, max_val: float, precision: int = 2, exclude: List[float] = None) -> float:
        """生成隨機浮點數
        
        Args:
            min_val: 最小值
            max_val: 最大值
            precision: 精度（小數位數）
            exclude: 排除的值列表
            
        Returns:
            隨機浮點數
        """
        if exclude is None:
            exclude = []
            
        if min_val > max_val:
            min_val, max_val = max_val, min_val
            
        while True:
            num = round(random.uniform(min_val, max_val), precision)
            if num not in exclude:
                return num
    
    @classmethod
    def register(cls) -> None:
        """註冊生成器到中央系統"""
        from utils.core.registry import registry
        
        print(f"正在註冊生成器: {cls.__name__}")
        
        # 創建一個臨時實例以獲取類別和子類別
        temp_instance = cls()
        category = temp_instance.get_category()
        subcategory = temp_instance.get_subcategory()
        
        print(f"生成器 {cls.__name__} 的類別: '{category}', 子類別: '{subcategory}'")
        
        # 註冊到中央系統
        registry.register(cls, category, subcategory)


# 裝飾器：用於註冊生成器
def register_generator(cls):
    """註冊生成器裝飾器
    
    用法：
    @register_generator
    class MyGenerator(QuestionGenerator):
        ...
    """
    print(f"裝飾器被調用: {cls.__name__}")
    
    # 如果設置了自動註冊，則註冊生成器
    if getattr(cls, 'auto_register', True):
        print(f"自動註冊已啟用，正在註冊 {cls.__name__}")
        cls.register()
    else:
        print(f"自動註冊已禁用，不註冊 {cls.__name__}")
    
    return cls
