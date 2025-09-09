#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 三角函數題目生成器模組

本模組提供各種三角函數相關的數學題目生成器，涵蓋從基本三角函數值
計算到複雜三角恆等式的完整範圍。使用新架構的統一 API，整合配置管理
和日誌系統，提供高品質的三角函數教學內容。

可用的三角函數生成器：
- TrigonometricFunctionGenerator: 三角函數值計算題目生成器
- InverseTrigonometricFunctionGenerator: 反三角函數計算生成器  
- TrigAngleConversionGenerator: 三角函數角度轉換生成器
- TrigonometricFunctionGeneratorRadius: 弧度制三角函數生成器

主要特色：
- 完整的 Pydantic 參數驗證系統
- 精確的 sympy 符號運算支援
- 智能的定義域檢查和邊界處理
- 專業的 LaTeX 數學表達式格式化  
- 詳細的單位圓幾何解析
- 可配置的角度範圍和函數選擇
- 完整的 Sphinx 文檔標準

Example:
    >>> from generators.trigonometry import TrigonometricFunctionGenerator
    >>> 
    >>> # 使用預設設定創建生成器
    >>> generator = TrigonometricFunctionGenerator()
    >>> question = generator.generate_question()
    >>> print(question['question'])
    '求 $\\sin 60°$ 的值'
    >>> 
    >>> # 使用自訂設定創建生成器
    >>> custom_generator = TrigonometricFunctionGenerator({
    ...     'functions': ['sin', 'cos'],
    ...     'angles': [30, 45, 60],
    ...     'show_unit_circle': True
    ... })
    >>> custom_question = custom_generator.generate_question()
    
Note:
    所有三角函數生成器都遵循新架構的設計原則，使用 sympy 進行精確的
    符號運算，確保特殊角度的三角函數值以最簡根式形式呈現。每個生成器
    都包含完整的定義域檢查，避免產生數學上無意義的題目。
"""

from utils import get_logger

logger = get_logger(__name__)

# 導入所有三角函數生成器
from .TrigonometricFunctionGenerator import TrigonometricFunctionGenerator
from .InverseTrigonometricFunctionGenerator import InverseTrigonometricFunctionGenerator  
from .TrigAngleConversionGenerator import TrigAngleConversionGenerator
from .TrigonometricFunctionGenerator_radius import TrigonometricFunctionGeneratorRadius

# 記錄模組初始化
logger.info("三角函數生成器模組初始化完成：4 個生成器已加載")
logger.debug("可用生成器：度數制、反三角函數、角度轉換、弧度制")

# 公開 API
__all__ = [
    'TrigonometricFunctionGenerator',
    'InverseTrigonometricFunctionGenerator',
    'TrigAngleConversionGenerator',
    'TrigonometricFunctionGeneratorRadius'
]