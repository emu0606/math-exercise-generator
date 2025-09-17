#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 三角函數值計算題生成器（改進的詳解）
"""

import sympy
from sympy import sin, cos, tan, cot, csc, sec, pi, simplify, latex
import random
from typing import Dict, Any, List, Tuple, Union, Callable

from ..base import QuestionGenerator, QuestionSize, register_generator

@register_generator
class TrigonometricFunctionGenerator(QuestionGenerator):
    """三角函數值計算題生成器
    
    生成計算三角函數值的題目，使用新的圖形架構並提供簡潔明瞭的詳解。
    """
    
    def __init__(self, options: Dict[str, Any] = None):
        super().__init__(options)
        self.options = options or {}
        
        # 設定可用的三角函數
        #self.functions = [sin, cos, tan, cot, sec, csc]
        self.functions = [sin, cos, tan]
        if self.options.get("functions"):
            self.functions = self.options.get("functions")
        
        # 設定可用的角度
        self.angles = [0, 30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 240, 270, 300, 315, 330, 360]
        if self.options.get("angles"):
            self.angles = self.options.get("angles")
        
        self.difficulty = self.options.get("difficulty", "MEDIUM")
        
        # 創建三角函數值查詢表
        self.trig_values = self._build_trig_value_table()
        
        # 函數定義與幾何意義
        self.definitions = {
            "sin": "\\frac{y}{r}",
            "cos": "\\frac{x}{r}",
            "tan": "\\frac{y}{x}",
            "cot": "\\frac{1}{\\tan \\theta} = \\frac{x}{y}",
            "sec": "\\frac{1}{\\cos \\theta} = \\frac{r}{x}",
            "csc": "\\frac{1}{\\sin \\theta} = \\frac{r}{y}"
        }
        
        self.geometric_meanings = {
            "sin": "單位圓上點的y座標值",
            "cos": "單位圓上點的x座標值",
            "tan": "y座標除以x座標",
            "cot": "x座標除以y座標", 
            "sec": "半徑除以x座標",
            "csc": "半徑除以y座標"
        }
    
    def _build_trig_value_table(self) -> Dict[Tuple[Callable, int], Union[str, sympy.Expr]]:
        """構建三角函數值查詢表，包含所有角度的所有函數值和對應的坐標"""
        table = {}
        
        # 填充表格
        for func in self.functions:
            for angle in self.angles:
                key = (func, angle)
                
                # 計算角度對應的弧度
                angle_rad = angle * pi / 180
                
                try:
                    # 嘗試使用sympy計算值
                    value = simplify(func(angle_rad))
                    table[key] = value
                except Exception:
                    # 標記為錯誤
                    table[key] = "ERROR"
        
        return table
    
    def _get_unit_circle_coordinates(self, angle: int) -> Tuple[sympy.Expr, sympy.Expr]:
        """獲取單位圓上指定角度的坐標點
        
        Args:
            angle: 角度值（度）
            
        Returns:
            (x, y): 坐標點的x和y值
        """
        angle_rad = angle * pi / 180
        x = simplify(cos(angle_rad))
        y = simplify(sin(angle_rad))
        return (x, y)
    
    def generate_question(self) -> Dict[str, Any]:
        """生成一個題目"""
        # 隨機選擇角度和函數
        angle = random.choice(self.angles)
        func = random.choice(self.functions)
        func_name = func.__name__
        
        # 從查詢表獲取值
        value = self.trig_values.get((func, angle))
        
        # 如果值是錯誤標記，重新選擇一組
        while value == "ERROR":
            angle = random.choice(self.angles)
            func = random.choice(self.functions)
            func_name = func.__name__
            value = self.trig_values.get((func, angle))
        
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
                'scale': 1.0
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
                'scale': 1.2 # 'width' is removed as per refactoring plan
            }
        }
        
        # 生成題目文字
        question_text = f"${func_name}({angle}^\\circ)$ \\\\ $= $"

        # 生成答案（使用latex輸出）
        answer = f"${latex(value)}$"
        
        # 生成解析
        explanation = self._generate_explanation(func_name, angle, value)
        
        return {
            "question": question_text,
            "answer": answer,
            "explanation": explanation,
            "size": self.get_question_size(),
            "difficulty": self.difficulty,
            "figure_data_question": figure_data_question,
            "figure_data_explanation": figure_data_explanation,
            "figure_position": "right", # Controls question figure position
            "explanation_figure_position": "right" # Controls explanation figure position
        }
    
    def _generate_explanation(self, func_name: str, angle: int, value: Union[sympy.Expr, str]) -> str:
        """生成三角函數值計算的詳解，添加更清晰的換行符號
        
        Args:
            func_name: 三角函數名稱
            angle: 角度值（度）
            value: 函數值（sympy表達式）
            
        Returns:
            詳解文字，含有適當的LaTeX換行符號
        """
        # 獲取單位圓上的坐標
        x, y = self._get_unit_circle_coordinates(angle)
        
        # 函數定義和幾何意義
        definition = self.definitions.get(func_name, "")
        meaning = self.geometric_meanings.get(func_name, "")
        
        # 生成坐標說明
        coords = f"當 $\\theta = {angle}^\\circ$ 時，\\\\ 點的座標為 $({latex(x)}, {latex(y)})$"
        
        # 根據函數類型生成計算過程
        is_infinity = isinstance(value, sympy.core.numbers.Infinity) or isinstance(value, sympy.core.numbers.NegativeInfinity)
        
        if is_infinity:
            # 對於無窮大的情況，提供更詳細的說明
            if func_name == "tan" and (angle == 90 or angle == 270):
                reason = f"因為 $\\cos({angle}^\\circ) = {latex(x)} = 0$，\\\\ 所以分母為零"
                calc = f"\\frac{{{latex(y)}}}{{0}} = {latex(value)}"
            elif func_name == "cot" and (angle == 0 or angle == 180 or angle == 360):
                reason = f"因為 $\\sin({angle}^\\circ) = {latex(y)} = 0$，\\\\ 所以分母為零"
                calc = f"\\frac{{{latex(x)}}}{{0}} = {latex(value)}"
            elif func_name == "sec" and (angle == 90 or angle == 270):
                reason = f"因為 $\\cos({angle}^\\circ) = {latex(x)} = 0$，\\\\ 所以分母為零"
                calc = f"\\frac{{1}}{{0}} = {latex(value)}"
            elif func_name == "csc" and (angle == 0 or angle == 180 or angle == 360):
                reason = f"因為 $\\sin({angle}^\\circ) = {latex(y)} = 0$，\\\\ 所以分母為零"
                calc = f"\\frac{{1}}{{0}} = {latex(value)}"
            else:
                reason = "分母為零"
                calc = f"{latex(value)}"
            
            explanation = f"""因為 ${func_name} \\theta = {definition}$，\\\\ 即{meaning} \\\\ {coords} \\\\ {reason} \\\\ 所以 ${func_name}({angle}^\\circ) = {calc}$"""
        else:
            # 對於一般值，顯示計算過程
            if func_name == "sin":
                calc = f"{latex(y)}"
            elif func_name == "cos":
                calc = f"{latex(x)}"
            elif func_name == "tan":
                calc = f"\\frac{{{latex(y)}}}{{{latex(x)}}} = {latex(value)}"
            elif func_name == "cot":
                calc = f"\\frac{{{latex(x)}}}{{{latex(y)}}} = {latex(value)}"
            elif func_name == "sec":
                calc = f"\\frac{{1}}{{{latex(x)}}} = {latex(value)}"
            elif func_name == "csc":
                calc = f"\\frac{{1}}{{{latex(y)}}} = {latex(value)}"
            else:
                calc = f"{latex(value)}"
            
            explanation = f"""因為 ${func_name} \\theta = {definition}$，\\\\ 即{meaning} \\\\ {coords} \\\\ 所以 ${func_name}({angle}^\\circ) = {calc}$"""
        
        return explanation

    
    def get_question_size(self) -> int:
        """獲取題目大小"""
        return QuestionSize.SMALL
    
    def get_category(self) -> str:
        """獲取題目類別"""
        return "三角比"
    
    def get_subcategory(self) -> str:
        """獲取題目子類別"""
        return "三角函數值計算"	