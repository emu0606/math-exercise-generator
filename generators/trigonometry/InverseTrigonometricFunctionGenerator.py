#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 反三角函數值計算題生成器
"""

import sympy
from sympy import sin, cos, tan, pi, sqrt, simplify, latex, rad, deg
import random
import math
from typing import Dict, Any

from ..base import QuestionGenerator, QuestionSize, register_generator

@register_generator
class InverseTrigonometricFunctionGenerator(QuestionGenerator):
    """反三角函數值計算題生成器
    
    生成計算反三角函數值的題目，主要針對特殊角的反三角函數值。
    """
    
    def __init__(self, options: Dict[str, Any] = None):
        super().__init__(options)
        self.options = options or {}
        
        # 設定可用的三角函數及其對應的反三角函數
        self.functions = ["sin", "cos", "tan"]
        if self.options.get("functions"):
            self.functions = self.options.get("functions")
        
        # 設定反三角函數名稱映射
        self.func_name_map = {
            "sin": "\\sin^{-1}",
            "cos": "\\cos^{-1}",
            "tan": "\\tan^{-1}"
        }
        
        # 設定特殊角（以度數表示）
        self.special_angles = [-90, -60, -45, -30, 0, 30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 240, 270]
        
        # 函數值域範圍，確保數學符號被$包裹
        self.value_ranges = {
            "sin": "$[-90^\\circ, 90^\\circ]$",
            "cos": "$[0^\\circ, 180^\\circ]$",
            "tan": "$(-90^\\circ, 90^\\circ)$"
        }
        
        self.difficulty = self.options.get("difficulty", "MEDIUM")
    
    def generate_question(self) -> Dict[str, Any]:
        """生成一個題目"""
        try:
            # 1. 先選擇函數
            func_name = random.choice(self.functions)
            
            # 2. 根據函數選擇合適的角度
            if func_name == "tan":
                # 排除tan不存在的角度
                valid_angles = [a for a in self.special_angles if a % 180 != 90]
                angle_deg = random.choice(valid_angles)
            else:
                angle_deg = random.choice(self.special_angles)
            
            # 3. 將角度轉為弧度，並計算對應的三角函數值
            angle_rad = sympy.rad(angle_deg)
            
            # 使用getattr獲取sympy中對應的函數
            trig_func = getattr(sympy, func_name)
            value = trig_func(angle_rad)
            
            # 4. 調整角度到反三角函數的值域內
            adjusted_angle = self._adjust_angle_to_range(angle_deg, func_name)
            
            # 格式化值的顯示
            value_latex = latex(value)
            
            # 5. 生成題目文字
            question_text = f"${self.func_name_map[func_name]}({value_latex}) = $"
            
            # 6. 生成答案
            answer = f"${adjusted_angle}^\\circ$"
            
            # 7. 生成解析
            explanation = self._generate_explanation(func_name, value_latex, adjusted_angle)
            
            return {
                "question": question_text,
                "answer": answer,
                "explanation": explanation,
                "size": self.get_question_size(),
                "difficulty": self.difficulty
            }
        except Exception as e:
            # 增強錯誤處理，提供詳細錯誤信息
            error_msg = f"生成反三角函數題目時出錯: {str(e)}"
            print(error_msg)  # 輸出錯誤日誌
            
            # 返回一個預設題目
            return {
                "question": "$\\sin^{-1}(\\frac{1}{2}) = $",
                "answer": "$30^\\circ$",
                "explanation": "預設題目：$\\sin^{-1}(\\frac{1}{2}) = 30^\\circ$，因為 $\\sin(30^\\circ) = \\sin(150^\\circ) = \\frac{1}{2}$ 但 $\\sin^{-1}$ 的值域為 $[-90^\\circ, 90^\\circ]$，所以答案是 $30^\\circ$。",
                "size": self.get_question_size(),
                "difficulty": self.difficulty
            }

    def _adjust_angle_to_range(self, angle_deg, func_name):
        """將角度調整到對應反三角函數的標準值域範圍內"""
        if func_name == "sin":
            # arcsin值域為[-90°, 90°]
            if -90 <= angle_deg <= 90:
                return angle_deg
            elif 90 < angle_deg <= 270:
                return 180 - angle_deg  # 取補角
            else:  # 270 < angle_deg
                return angle_deg - 360  # 轉為負角
        
        elif func_name == "cos":
            # arccos值域為[0°, 180°]
            if 0 <= angle_deg <= 180:
                return angle_deg
            elif -90 <= angle_deg < 0:
                return abs(angle_deg)  # 取絕對值
            else:  # 180 < angle_deg <= 270
                return 360 - angle_deg
        
        else:  # func_name == "tan"
            # arctan值域為(-90°, 90°)
            if -90 < angle_deg <= 90:
                return angle_deg
            else:  # 90 < angle_deg <= 270，不包含-90和90
                return angle_deg - 180

    def _generate_explanation(self, func_name, value_latex, adjusted_angle):
        """生成詳解，包含其他可能的角度
        
        Args:
            func_name: 三角函數名稱
            value_latex: LaTeX格式的函數輸入值
            adjusted_angle: 調整後的角度（度數）
            
        Returns:
            str: 格式化的解釋文本
        """
        inv_func_name = self.func_name_map[func_name]
        
        # 共同的解釋模板
        explanation_template = """
        ${orig_func}({angle}^\\circ) = {orig_func}({other_angle}^\\circ) = {val}$
        
        但 ${func}$ 的值域為 {domain}
        
        因此 ${func}({val}) = {angle}^\\circ$
        """
        
        # 根據函數類型確定其他角度
        if func_name == "sin":
            other_angle = 180 - adjusted_angle  # 補角
        elif func_name == "cos":
            other_angle = -adjusted_angle  # 負角
            if other_angle < 0:
                other_angle += 360
        else:  # tan
            other_angle = adjusted_angle + 180

        
        # 填充模板
        return explanation_template.format(
            func=inv_func_name,
            orig_func=f"\\{func_name}",
            val=value_latex,
            angle=adjusted_angle,
            other_angle=other_angle,
            domain=self.value_ranges.get(func_name, "$未知$")
        )


    
    def get_question_size(self) -> int:
        """獲取題目大小"""
        return QuestionSize.SMALL
    
    def get_category(self) -> str:
        """獲取題目類別"""
        return "三角比"
    
    def get_subcategory(self) -> str:
        """獲取題目子類別"""
        return "反三角函數值計算"