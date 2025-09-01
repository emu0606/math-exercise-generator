#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 雙重根式化簡題目生成器
"""

import math
import random
import numpy as np
import sympy as sp
from sympy import sqrt, expand, simplify, latex
from typing import Dict, Any, List

from ..base import QuestionGenerator, QuestionSize, register_generator


@register_generator
class DoubleRadicalSimplificationGenerator(QuestionGenerator):
    """雙重根式化簡題目生成器
    
    生成形如 √(c ± d√e) 的雙重根式，要求學生將其化簡為 √a ± √b 的形式
    """
    
    def __init__(self, options: Dict[str, Any] = None):
        """初始化生成器
        
        Args:
            options: 其他選項，如特定範圍、特定運算符等
        """
        super().__init__(options)

    
    def generate_question(self) -> Dict[str, Any]:
        """生成一個雙重根式化簡題目
        
        Returns:
            包含題目資訊的字典，包含以下鍵：
            - 'question': 題目文字
            - 'answer': 答案
            - 'explanation': 解析
            - 'size': 題目大小
            - 'difficulty': 題目難度
        """
        # 設定參數
        max_value = self.options.get('max_value', 25)
        max_attempts = self.options.get('max_attempts', 100)
        
        # 生成題目
        for _ in range(max_attempts):
            # 隨機選擇不同的 a 和 b
            values = list(range(1, max_value + 1))
            random.shuffle(values)
            a, b = values[:2]
            
            # 對於減法，確保 a > b
            if a < b:
                a, b = b, a
            
            # 隨機決定加法或減法
            is_addition = random.choice([True, False])
            
            # 檢查 a*b 是否為完全平方數（如果是則跳過）
            if self._is_square(a * b):
                continue
            
            # 生成表達式並平方
            expr = sqrt(a) + sqrt(b) if is_addition else sqrt(a) - sqrt(b)
            squared = expand(expr**2)
            
            # 使用 sympy 生成題目表達式
            radical_expr = sqrt(squared)
            question = f"化簡：${latex(radical_expr)}$"
            
            # 使用 sympy 化簡答案
            simplified_expr = simplify(expr)
            answer = f"${latex(simplified_expr)}$"
            
            # 構建求解過程的每個步驟
            # 獲取運算符，用於顯示
            operator = "+" if is_addition else "-"
            
            # 解析步驟，精簡優雅的格式
            explanation = [
                f"$\\sqrt{{{latex(squared)}}}$",
                f"$= \\sqrt{{{a}+{b} {operator} 2\\sqrt{{{a}\\cdot{b}}}}}$",
                f"$= \\sqrt{{(\\sqrt{{{a}}} {operator} \\sqrt{{{b}}})^2}}$",
                f"$= |\\sqrt{{{a}}} {operator} \\sqrt{{{b}}}|$",
                f"$= \\sqrt{{{a}}} {operator} \\sqrt{{{b}}}$",
            ]
            
            # 構建完整的解析
            full_explanation = "<br>".join(explanation)
            
            # 確定難度
            difficulty = "MEDIUM"
            
            # 返回結果
            return {
                "question": question,
                "answer": answer,
                "explanation": full_explanation,
                "size": self.get_question_size(),
                "difficulty": difficulty
            }
        
        # 如果無法生成有效題目，返回一個預設題目
        default_expr = sqrt(9) - sqrt(5)
        default_squared = expand(default_expr**2)
        default_radical = sqrt(default_squared)
        
        return {
            "question": f"化簡：${latex(default_radical)}$",
            "answer": "$3 - \\sqrt{5}$",
            "explanation": "$\\sqrt{14 - 6\\sqrt{5}}$<br>$= \\sqrt{9+5 - 2\\sqrt{9\\cdot5}}$<br>$= \\sqrt{(\\sqrt{9} - \\sqrt{5})^2}$<br>$= |\\sqrt{9} - \\sqrt{5}|$<br>$= \\sqrt{9} - \\sqrt{5} = 3-\\sqrt{5}$",
            "size": self.get_question_size(),
            "difficulty": "MEDIUM"
        }




    def get_question_size(self) -> int:
        """獲取題目大小
        
        Returns:
            題目大小（使用 QuestionSize 枚舉值）
        """
        return QuestionSize.WIDE
    
    def get_category(self) -> str:
        """獲取題目類別
        
        Returns:
            題目類別名稱
        """
        return "數與式"
    
    def get_subcategory(self) -> str:
        """獲取題目子類別
        
        Returns:
            題目子類別名稱
        """
        return "重根式的化簡"
    
    def _is_square(self, n: int) -> bool:
        """檢查一個數是否為完全平方數
        
        Args:
            n: 要檢查的數
            
        Returns:
            是否為完全平方數
        """
        if n <= 0:
            return False
        
        sqrt_n = int(math.sqrt(n))
        return sqrt_n * sqrt_n == n
