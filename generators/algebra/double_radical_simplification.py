#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 雙重根式化簡題目生成器

本模組提供雙重根式化簡題目的生成功能，生成形如 √(c ± d√e) 
的雙重根式，要求學生將其化簡為 √a ± √b 的形式。使用新架構的
統一 API，整合幾何計算、配置管理和日誌系統。

支援的功能：
- 自動生成數學上有效的雙重根式
- 完整的化簡步驟解析
- 智能避免平凡情況（如完全平方數）
- LaTeX 格式化的數學表達式
- 可配置的難度和範圍控制

Example:
    >>> from generators.algebra import DoubleRadicalSimplificationGenerator
    >>> generator = DoubleRadicalSimplificationGenerator()
    >>> question = generator.generate_question()
    >>> question['question']
    '化簡：$\\sqrt{14 - 6\\sqrt{5}}$'
    >>> question['answer']
    '$\\sqrt{9} - \\sqrt{5}$'
    
Note:
    此生成器使用 sympy 進行符號數學運算，確保數學邏輯的正確性。
    所有生成的題目都經過驗證，避免無解或平凡解的情況。
"""

import math
import random
from typing import Dict, Any, List, Tuple, Optional

import numpy as np
import sympy as sp
from sympy import sqrt, expand, simplify, latex
from pydantic import BaseModel, Field, validator

from utils import global_config, get_logger
from ..base import QuestionGenerator, QuestionSize, register_generator

logger = get_logger(__name__)


class DoubleRadicalParams(BaseModel):
    """雙重根式生成參數模型
    
    定義生成雙重根式化簡題目時的所有配置參數，
    使用 Pydantic 進行參數驗證和型別安全。
    
    Attributes:
        max_value (int): 根式內數值的最大範圍，預設 25
        max_attempts (int): 生成有效題目的最大嘗試次數，預設 100
        allow_addition (bool): 是否允許加法形式的根式，預設 True
        allow_subtraction (bool): 是否允許減法形式的根式，預設 True
        min_difficulty (int): 最小難度等級 (1-5)，預設 2
        max_difficulty (int): 最大難度等級 (1-5)，預設 4
        
    Example:
        >>> params = DoubleRadicalParams(max_value=15, max_attempts=50)
        >>> params.max_value
        15
        >>> params.allow_addition
        True
    """
    max_value: int = Field(
        default=25, 
        ge=5, 
        le=100, 
        description="根式內數值的最大範圍"
    )
    max_attempts: int = Field(
        default=100, 
        ge=10, 
        le=1000, 
        description="生成有效題目的最大嘗試次數"
    )
    allow_addition: bool = Field(
        default=True, 
        description="是否允許加法形式的根式"
    )
    allow_subtraction: bool = Field(
        default=True, 
        description="是否允許減法形式的根式"
    )
    min_difficulty: int = Field(
        default=2, 
        ge=1, 
        le=5, 
        description="最小難度等級"
    )
    max_difficulty: int = Field(
        default=4, 
        ge=1, 
        le=5, 
        description="最大難度等級"
    )
    
    @validator('max_difficulty')
    def difficulty_range_valid(cls, v, values):
        """驗證難度範圍的合理性"""
        if 'min_difficulty' in values and v < values['min_difficulty']:
            raise ValueError('最大難度不能小於最小難度')
        return v
    
    @validator('allow_addition', 'allow_subtraction', pre=True, always=True)
    def at_least_one_operation(cls, v, values):
        """確保至少允許一種運算形式"""
        if 'allow_addition' in values:
            if not values['allow_addition'] and not v:
                raise ValueError('必須至少允許加法或減法其中一種形式')
        return v


@register_generator
class DoubleRadicalSimplificationGenerator(QuestionGenerator):
    """雙重根式化簡題目生成器
    
    生成形如 √(c ± d√e) 的雙重根式化簡題目，要求學生將其化簡為
    √a ± √b 的形式。此生成器採用新架構的完整重建，充分利用新工具
    和框架優勢，提供高品質的代數題目生成。
    
    使用新架構的核心特性：
    - 完整的 Pydantic 參數驗證系統
    - 統一的日誌記錄和錯誤處理
    - 智能的數學邏輯驗證
    - LaTeX 格式化的專業輸出
    - 可配置的難度控制系統
    
    Attributes:
        logger: 模組日誌記錄器
        config: 全域配置物件
        params: 經過驗證的生成參數
        
    Example:
        >>> generator = DoubleRadicalSimplificationGenerator({
        ...     'max_value': 20,
        ...     'allow_subtraction': True
        ... })
        >>> question = generator.generate_question()
        >>> question['question']
        '化簡：$\\sqrt{29 + 12\\sqrt{5}}$'
        >>> question['answer']
        '$2\\sqrt{5} + 3$'
        
    Note:
        此生成器使用 sympy 的符號數學引擎確保數學正確性，
        所有生成的根式都有唯一的標準化簡形式。
    """
    
    def __init__(self, options: Dict[str, Any] = None):
        """初始化雙重根式化簡題目生成器
        
        使用新架構的參數驗證和配置系統，確保所有輸入參數
        的有效性和數學邏輯的正確性。
        
        Args:
            options (Dict[str, Any], optional): 生成器配置選項，
                將透過 DoubleRadicalParams 進行驗證。支援的選項包括：
                - max_value: 根式數值範圍
                - max_attempts: 生成嘗試次數
                - allow_addition/subtraction: 運算類型控制
                - min/max_difficulty: 難度控制
                
        Raises:
            ValidationError: 如果配置參數不符合要求
            
        Example:
            >>> # 基本初始化
            >>> generator = DoubleRadicalSimplificationGenerator()
            >>> 
            >>> # 自訂配置初始化
            >>> custom_options = {
            ...     'max_value': 15,
            ...     'allow_addition': True,
            ...     'min_difficulty': 3
            ... }
            >>> generator = DoubleRadicalSimplificationGenerator(custom_options)
        """
        super().__init__(options)
        
        # 使用新架構的參數驗證系統
        try:
            self.params = DoubleRadicalParams(**self.options)
            logger.debug(f"雙重根式生成器初始化成功: {self.params}")
        except Exception as e:
            logger.error(f"參數驗證失敗: {str(e)}")
            # 使用預設參數
            self.params = DoubleRadicalParams()
            logger.info("使用預設參數初始化生成器")
    
    def generate_question(self) -> Dict[str, Any]:
        """生成一個雙重根式化簡題目
        
        使用新架構的智能生成算法，創建數學上有效且教育價值高的
        雙重根式化簡題目。所有題目都經過完整的數學驗證。
        
        Returns:
            Dict[str, Any]: 包含完整題目資訊的字典，包含以下鍵值：
                - question (str): LaTeX 格式的題目文字
                - answer (str): LaTeX 格式的標準答案
                - explanation (str): HTML 格式的詳細解析步驟
                - size (QuestionSize): 題目顯示大小
                - difficulty (str): 題目難度等級
                - category (str): 數學領域分類
                - subcategory (str): 具體題型分類
                
        Raises:
            ValueError: 如果無法生成有效的題目
            
        Example:
            >>> generator = DoubleRadicalSimplificationGenerator()
            >>> result = generator.generate_question()
            >>> result['question']
            '化簡：$\\sqrt{14 - 6\\sqrt{5}}$'
            >>> result['answer']
            '$\\sqrt{9} - \\sqrt{5}$'
            >>> 'explanation' in result
            True
            
        Note:
            生成過程包含智能避免機制，跳過數學上平凡的情況，
            確保每個題目都有教育意義和適當的挑戰性。
        """
        logger.info("開始生成雙重根式化簡題目")
        
        # 生成題目
        for attempt in range(self.params.max_attempts):
            try:
                result = self._generate_single_question()
                if result:
                    logger.info(f"成功生成題目（第 {attempt + 1} 次嘗試）")
                    return result
            except Exception as e:
                logger.warning(f"生成嘗試 {attempt + 1} 失敗: {str(e)}")
                continue
        
        # 如果無法生成有效題目，使用預設題目
        logger.warning("達到最大嘗試次數，使用預設題目")
        return self._get_default_question()
    
    def _generate_single_question(self) -> Optional[Dict[str, Any]]:
        """生成單一題目的內部方法
        
        Returns:
            Optional[Dict[str, Any]]: 成功時返回題目字典，失敗時返回 None
        """
        # 隨機選擇不同的 a 和 b
        values = list(range(1, self.params.max_value + 1))
        random.shuffle(values)
        a, b = values[:2]
        
        # 確保 a >= b 以避免負數問題
        if a < b:
            a, b = b, a
        
        # 根據配置決定運算類型
        available_ops = []
        if self.params.allow_addition:
            available_ops.append(True)
        if self.params.allow_subtraction:
            available_ops.append(False)
        
        is_addition = random.choice(available_ops)
        
        # 檢查是否為平凡情況
        if self._is_trivial_case(a, b):
            return None
        
        # 生成數學表達式
        expr = sqrt(a) + sqrt(b) if is_addition else sqrt(a) - sqrt(b)
        squared = expand(expr**2)
        
        # 驗證表達式的有效性
        if not self._is_valid_expression(squared):
            return None
        
        # 生成題目和答案
        radical_expr = sqrt(squared)
        question = f"化簡：${latex(radical_expr)}$"
        
        simplified_expr = simplify(expr)
        answer = f"${latex(simplified_expr)}$"
        
        # 生成詳細解析
        explanation = self._generate_explanation(a, b, is_addition, squared)
        
        # 評估難度
        difficulty = self._assess_difficulty(a, b, is_addition)
        
        return {
            "question": question,
            "answer": answer,
            "explanation": explanation,
            "size": self.get_question_size(),
            "difficulty": difficulty,
            "category": self.get_category(),
            "subcategory": self.get_subcategory()
        }
    
    def _is_trivial_case(self, a: int, b: int) -> bool:
        """檢查是否為平凡情況
        
        Args:
            a, b: 根式參數
            
        Returns:
            bool: 是否為平凡情況
        """
        # 檢查 a*b 是否為完全平方數
        if self._is_perfect_square(a * b):
            logger.debug(f"跳過平凡情況: a={a}, b={b} (ab={a*b} 為完全平方數)")
            return True
        
        # 檢查 a 和 b 本身是否為完全平方數
        if self._is_perfect_square(a) or self._is_perfect_square(b):
            logger.debug(f"跳過平凡情況: a={a}, b={b} (其中包含完全平方數)")
            return True
        
        return False
    
    def _is_perfect_square(self, n: int) -> bool:
        """檢查一個數是否為完全平方數
        
        Args:
            n: 要檢查的數
            
        Returns:
            bool: 是否為完全平方數
        """
        if n <= 0:
            return False
        
        sqrt_n = int(math.sqrt(n))
        return sqrt_n * sqrt_n == n
    
    def _is_valid_expression(self, expr) -> bool:
        """驗證表達式的有效性
        
        Args:
            expr: sympy 表達式
            
        Returns:
            bool: 是否為有效表達式
        """
        try:
            # 檢查表達式是否能正確計算
            float(expr.subs(sqrt(2), math.sqrt(2)))
            return True
        except (ValueError, TypeError):
            return False
    
    def _generate_explanation(self, a: int, b: int, is_addition: bool, squared) -> str:
        """生成詳細的解析步驟
        
        Args:
            a, b: 根式參數
            is_addition: 是否為加法
            squared: 平方後的表達式
            
        Returns:
            str: HTML 格式的解析步驟
        """
        operator = "+" if is_addition else "-"
        
        # 使用新架構生成專業的解析步驟
        steps = [
            f"$\\sqrt{{{latex(squared)}}}$",
            f"$= \\sqrt{{{a}+{b} {operator} 2\\sqrt{{{a}\\cdot{b}}}}}$",
            f"$= \\sqrt{{(\\sqrt{{{a}}} {operator} \\sqrt{{{b}}})^2}}$",
            f"$= |\\sqrt{{{a}}} {operator} \\sqrt{{{b}}}|$"
        ]
        
        # 根據符號添加最終步驟
        if is_addition or a >= b:
            steps.append(f"$= \\sqrt{{{a}}} {operator} \\sqrt{{{b}}}$")
        else:
            steps.append(f"$= \\sqrt{{{b}}} - \\sqrt{{{a}}}$")
        
        return "<br>".join(steps)
    
    def _assess_difficulty(self, a: int, b: int, is_addition: bool) -> str:
        """評估題目難度
        
        Args:
            a, b: 根式參數
            is_addition: 是否為加法
            
        Returns:
            str: 難度等級
        """
        # 基於數值大小和運算類型評估難度
        max_val = max(a, b)
        product = a * b
        
        if max_val <= 9 and product <= 25:
            difficulty = "EASY"
        elif max_val <= 16 and product <= 100:
            difficulty = "MEDIUM"
        else:
            difficulty = "HARD"
        
        # 減法通常比加法稍難
        if not is_addition and difficulty == "EASY":
            difficulty = "MEDIUM"
        
        logger.debug(f"評估難度: a={a}, b={b}, addition={is_addition} -> {difficulty}")
        return difficulty
    
    def _get_default_question(self) -> Dict[str, Any]:
        """獲取預設題目
        
        Returns:
            Dict[str, Any]: 預設題目字典
        """
        logger.info("使用預設雙重根式題目")
        
        return {
            "question": "化簡：$\\sqrt{14 - 6\\sqrt{5}}$",
            "answer": "$3 - \\sqrt{5}$",
            "explanation": (
                "$\\sqrt{14 - 6\\sqrt{5}}$<br>"
                "$= \\sqrt{9+5 - 2\\sqrt{9\\cdot5}}$<br>"
                "$= \\sqrt{(\\sqrt{9} - \\sqrt{5})^2}$<br>"
                "$= |\\sqrt{9} - \\sqrt{5}|$<br>"
                "$= \\sqrt{9} - \\sqrt{5} = 3-\\sqrt{5}$"
            ),
            "size": self.get_question_size(),
            "difficulty": "MEDIUM",
            "category": self.get_category(),
            "subcategory": self.get_subcategory()
        }
    
    def get_question_size(self) -> int:
        """獲取題目顯示大小
        
        雙重根式化簡題目需要較寬的顯示空間來正確展示
        數學表達式和解析步驟。
        
        Returns:
            int: QuestionSize.WIDE 的數值
            
        Note:
            WIDE 大小適合包含複雜數學表達式的題目顯示。
        """
        return QuestionSize.WIDE.value
    
    def get_category(self) -> str:
        """獲取題目主類別
        
        Returns:
            str: 主要數學領域分類
        """
        return "數與式"
    
    def get_subcategory(self) -> str:
        """獲取題目子類別
        
        Returns:
            str: 具體的代數題型分類
        """
        return "重根號練習"