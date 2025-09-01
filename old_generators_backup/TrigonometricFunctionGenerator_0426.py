#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 三角函數值計算題生成器（使用新的圖形架構）
"""

import sympy
from sympy import sin, cos, tan, cot, csc, sec, pi, simplify, latex
import random
from typing import Dict, Any, List, Tuple, Union, Callable

from ..base import QuestionGenerator, QuestionSize, register_generator

@register_generator
class TrigonometricFunctionGenerator(QuestionGenerator):
    """三角函數值計算題生成器
    
    生成計算三角函數值的題目，使用新的圖形架構。
    """
    
    def __init__(self, options: Dict[str, Any] = None):
        super().__init__(options)
        self.options = options or {}
        
        # 設定可用的三角函數
        self.functions = [sin, cos, tan, cot, sec, csc]
        if self.options.get("functions"):
            self.functions = self.options.get("functions")
        
        # 設定可用的角度
        self.angles = [0, 30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 240, 270, 300, 315, 330, 360]
        if self.options.get("angles"):
            self.angles = self.options.get("angles")
        
        self.difficulty = self.options.get("difficulty", "MEDIUM")
        
        # 創建三角函數值查詢表
        self.trig_values = self._build_trig_value_table()
    
    def _build_trig_value_table(self) -> Dict[Tuple[Callable, int], Union[str, sympy.Expr]]:
        """構建三角函數值查詢表，包含所有角度的所有函數值"""
        table = {}
        
        # 特殊無窮大情況
        special_cases = {
            (tan, 90): "\\infty",
            (tan, 270): "-\\infty",
            (cot, 0): "\\infty",
            (cot, 180): "-\\infty",
            (cot, 360): "\\infty",
            (sec, 90): "\\infty",
            (sec, 270): "-\\infty",
            (csc, 0): "\\infty",
            (csc, 180): "-\\infty",
            (csc, 360): "\\infty"
        }
        
        # 填充表格
        for func in self.functions:
            for angle in self.angles:
                key = (func, angle)
                
                # 檢查是否是特殊情況
                if key in special_cases:
                    table[key] = special_cases[key]
                else:
                    # 計算正常值
                    angle_rad = angle * pi / 180
                    try:
                        value = simplify(func(angle_rad))
                        table[key] = value
                    except Exception:
                        # 標記為錯誤，而不是默認到固定角度
                        table[key] = "ERROR"
        
        return table
    
    def generate_question(self) -> Dict[str, Any]:
        """生成一個題目"""
        # 隨機選擇角度和函數
        angle = random.choice(self.angles)
        func = random.choice(self.functions)
        func_name = func.__name__
        angle_rad = angle * pi / 180
        
        # 從查詢表獲取值
        value = self.trig_values.get((func, angle))
        
        # 如果值是錯誤標記，重新選擇一組
        while value == "ERROR":
            angle = random.choice(self.angles)
            func = random.choice(self.functions)
            value = self.trig_values.get((func, angle))
        
        # 判斷是否特殊值（無窮大）
        is_special = isinstance(value, str) and "\\infty" in value
        
        # 創建圖形數據
        figure_data_question = {
            'type': 'standard_unit_circle',
            'params': {
                'variant': 'question',
                'angle': angle,
                'show_coordinates': True,
                'show_angle': True,
                'show_point': True,
                'label_point': False,
                'show_radius': True
            },
            'options': {
                'scale': 0.5
                
            }
        }
        
        figure_data_explanation = {
            'type': 'standard_unit_circle',
            'params': {
                'variant': 'explanation',
                'angle': angle,
                'show_coordinates': True,
                'show_angle': True,
                'show_point': True,
                'show_radius': True
            },
            'options': {
                'scale': 1.2,
                'width': '2cm'
            }
        }
        
        # 生成題目文字
        question_text = f"${func_name}({angle}^\\circ) = $"
        
        # 生成答案
        answer = f"${latex(value)}$" if not is_special else f"${value}$"
        
        # 生成解析
        if is_special:
            explanation = self._generate_special_explanation(func_name, angle, value)
        else:
            explanation = self._generate_normal_explanation(func_name, angle, angle_rad, latex(value))
        
        return {
            "question": question_text,
            "answer": answer,
            "explanation": explanation,
            "size": self.get_question_size(),
            "difficulty": self.difficulty,
            "figure_data_question": figure_data_question,
            "figure_data_explanation": figure_data_explanation,
            "figure_position": "right"  # (可選) 題目圖形位置 ('right', 'left', 'bottom', 'none')
        }
    
    def _generate_special_explanation(self, func_name, angle, value):
        """生成特殊值的解釋"""
        return f"""
        計算 ${func_name}({angle}^\\circ)$ 的值：

        ${func_name}({angle}^\\circ)$ 是未定義的值，但可以表示為 ${value}$

        在數學上，當 ${func_name}({angle}^\\circ)$ 趨近於無限大時，我們記作 ${value}$
        """
    
    def _generate_normal_explanation(self, func_name, angle, angle_rad, value_latex):
        """生成一般值的解釋"""
        return f"""
        計算 ${func_name}({angle}^\\circ)$ 的值：

        將角度轉換為弧度：${angle}^\\circ = {latex(angle_rad)} \\text{{ rad}}$

        利用特殊角公式計算 ${func_name}({latex(angle_rad)}) = {value_latex}$
        """
    
    def get_question_size(self) -> int:
        """獲取題目大小"""
        return QuestionSize.SMALL  # 改為 WIDE 以適應圖形
    
    def get_category(self) -> str:
        """獲取題目類別"""
        return "三角比"
    
    def get_subcategory(self) -> str:
        """獲取題目子類別"""
        return "三角函數值計算"