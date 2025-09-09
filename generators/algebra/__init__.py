#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 代數題目生成器模組

本模組提供各種代數相關的數學題目生成器，涵蓋從基礎代數運算
到高等代數概念的完整範圍。使用新架構的統一 API，整合配置管理
和日誌系統，提供高品質的代數教學內容。

可用的代數生成器：
- DoubleRadicalSimplificationGenerator: 雙重根式化簡題目生成器

主要特色：
- 完整的 Pydantic 參數驗證系統
- 智能的數學邏輯驗證和錯誤避免
- 專業的 LaTeX 數學表達式格式化
- 詳細的解題步驟解析
- 可配置的難度和範圍控制
- 完整的 Sphinx 文檔標準

Example:
    >>> from generators.algebra import DoubleRadicalSimplificationGenerator
    >>> 
    >>> # 使用預設設定創建生成器
    >>> generator = DoubleRadicalSimplificationGenerator()
    >>> question = generator.generate_question()
    >>> print(question['question'])
    '化簡：$\\sqrt{14 - 6\\sqrt{5}}$'
    >>> 
    >>> # 使用自訂設定創建生成器
    >>> custom_generator = DoubleRadicalSimplificationGenerator({
    ...     'max_value': 20,
    ...     'allow_subtraction': True
    ... })
    >>> custom_question = custom_generator.generate_question()
    
Note:
    所有代數生成器都遵循新架構的設計原則，使用 sympy 等專業數學庫
    確保數學正確性，並提供完整的教學價值。每個生成器都包含智能的
    邊界條件處理，避免產生數學上無意義或過於簡單的題目。
"""

from utils import get_logger

logger = get_logger(__name__)

# 導入所有代數生成器
from .double_radical_simplification import DoubleRadicalSimplificationGenerator

# 記錄模組初始化
logger.debug("代數生成器模組初始化完成")

# 公開 API
__all__ = [
    'DoubleRadicalSimplificationGenerator'
]
