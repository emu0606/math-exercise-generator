#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 生成器註冊系統
"""

from typing import Dict, Type, Optional, Any

# 生成器基類的前向聲明
QuestionGeneratorType = Any

class GeneratorRegistry:
    """生成器註冊系統
    
    用於管理所有題目生成器的中央系統。
    """
    
    _instance = None
    
    def __new__(cls):
        """單例模式實現"""
        if cls._instance is None:
            cls._instance = super(GeneratorRegistry, cls).__new__(cls)
            cls._instance._generators = {}
            cls._instance._category_map = {}
        return cls._instance
    
    def register(self, generator_class: Type[QuestionGeneratorType], 
                 category: str, subcategory: str) -> None:
        """註冊一個生成器
        
        Args:
            generator_class: 生成器類
            category: 題目類別
            subcategory: 題目子類別
        """
        key = (category, subcategory)
        self._generators[key] = generator_class
        
        # 調試輸出
        print(f"註冊生成器: {generator_class.__name__}, 類別: '{category}', 子類別: '{subcategory}'")
        
        # 更新類別映射
        if category not in self._category_map:
            self._category_map[category] = []
        if subcategory not in self._category_map[category]:
            self._category_map[category].append(subcategory)
    
    def get_generator(self, category: str, subcategory: str) -> Optional[Type[QuestionGeneratorType]]:
        """獲取生成器
        
        Args:
            category: 題目類別
            subcategory: 題目子類別
            
        Returns:
            生成器類，如果找不到則返回 None
        """
        key = (category, subcategory)
        generator = self._generators.get(key)
        
        # 調試輸出
        if generator:
            print(f"找到生成器: {generator.__name__}, 類別: '{category}', 子類別: '{subcategory}'")
        else:
            print(f"未找到生成器, 類別: '{category}', 子類別: '{subcategory}'")
            print(f"已註冊的生成器: {list(self._generators.keys())}")
        
        return generator
    
    def get_categories(self) -> Dict[str, list]:
        """獲取所有類別和子類別
        
        Returns:
            類別映射，格式為 {類別: [子類別1, 子類別2, ...]}
        """
        return self._category_map
    
    def get_subcategories(self, category: str) -> list:
        """獲取指定類別的所有子類別
        
        Args:
            category: 題目類別
            
        Returns:
            子類別列表
        """
        return self._category_map.get(category, [])


# 全局註冊表實例
registry = GeneratorRegistry()
