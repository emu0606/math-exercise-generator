#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 三角方程式練習生成器（改進版）
"""

import random
import sympy
from typing import Dict, Any, Tuple, List
from ..base import QuestionGenerator, QuestionSize, register_generator


@register_generator
class TrigEquationSolverGenerator(QuestionGenerator):
    """三角方程式練習生成器
    
    生成基礎三角方程式求解題，包括：
    1. 以角度表示答案的題目 (50%)
    2. 以弧度表示答案的題目 (50%)
    """
    
    # 解題步驟模版
    SOLUTION_TEMPLATES = {
        "degree": {
            "sin": {
                "intro": "求解 $\\sin(x) = {value}$ 的步驟如下：",
                "basic_solution": "1. 首先，我們知道 $\\sin({angle}°) = {value}$。",
                "additional_solution": "2. 根據三角函數的性質，在一個週期內還有其他角度也滿足條件：\n\n   由於 $\\sin(180° - \\theta) = \\sin(\\theta)$，\n   另一個解為 $x = 180° - {base_angle}° = {additional_angle}°$",
                "no_additional": "2. 在一個週期內沒有其他角度滿足條件。",
                "general_solution": "{step}. 考慮函數的週期性（週期為 $360°$），通解為：",
                "final_answer": "{step}. 因此，方程式 $\\sin(x) = {value}$ 的通解為："
            },
            "cos": {
                "intro": "求解 $\\cos(x) = {value}$ 的步驟如下：",
                "basic_solution": "1. 首先，我們知道 $\\cos({angle}°) = {value}$。",
                "additional_solution": "2. 根據三角函數的性質，在一個週期內還有其他角度也滿足條件：\n\n   由於 $\\cos(360° - \\theta) = \\cos(\\theta)$，\n   另一個解為 $x = 360° - {base_angle}° = {additional_angle}°$",
                "no_additional": "2. 在一個週期內沒有其他角度滿足條件。",
                "general_solution": "{step}. 考慮函數的週期性（週期為 $360°$），通解為：",
                "final_answer": "{step}. 因此，方程式 $\\cos(x) = {value}$ 的通解為："
            },
            "tan": {
                "intro": "求解 $\\tan(x) = {value}$ 的步驟如下：",
                "basic_solution": "1. 首先，我們知道 $\\tan({angle}°) = {value}$。",
                "additional_solution": "",  # tan 函數在一個週期內只有一個解
                "no_additional": "2. 在一個週期內沒有其他角度滿足條件。",
                "general_solution": "2. 考慮函數的週期性（週期為 $180°$），通解為：",
                "final_answer": "3. 因此，方程式 $\\tan(x) = {value}$ 的通解為："
            }
        },
        "radian": {
            "sin": {
                "intro": "求解 $\\sin(x) = {value}$ 的步驟如下：",
                "basic_solution": "1. 首先，我們知道 $\\sin({angle}) = {value}$。",
                "additional_solution": "2. 根據三角函數的性質，在一個週期內還有其他角度也滿足條件：\n\n   由於 $\\sin(\\pi - \\theta) = \\sin(\\theta)$，\n   另一個解為 $x = \\pi - {base_angle} = {additional_angle}$",
                "no_additional": "2. 在一個週期內沒有其他角度滿足條件。",
                "general_solution": "{step}. 考慮函數的週期性（週期為 $2\\pi$），通解為：",
                "final_answer": "{step}. 因此，方程式 $\\sin(x) = {value}$ 的通解為："
            },
            "cos": {
                "intro": "求解 $\\cos(x) = {value}$ 的步驟如下：",
                "basic_solution": "1. 首先，我們知道 $\\cos({angle}) = {value}$。",
                "additional_solution": "2. 根據三角函數的性質，在一個週期內還有其他角度也滿足條件：\n\n   由於 $\\cos(2\\pi - \\theta) = \\cos(\\theta)$，\n   另一個解為 $x = 2\\pi - {base_angle} = {additional_angle}$",
                "no_additional": "2. 在一個週期內沒有其他角度滿足條件。",
                "general_solution": "{step}. 考慮函數的週期性（週期為 $2\\pi$），通解為：",
                "final_answer": "{step}. 因此，方程式 $\\cos(x) = {value}$ 的通解為："
            },
            "tan": {
                "intro": "求解 $\\tan(x) = {value}$ 的步驟如下：",
                "basic_solution": "1. 首先，我們知道 $\\tan({angle}) = {value}$。",
                "additional_solution": "",  # tan 函數在一個週期內只有一個解
                "no_additional": "2. 在一個週期內沒有其他角度滿足條件。",
                "general_solution": "2. 考慮函數的週期性（週期為 $\\pi$），通解為：",
                "final_answer": "3. 因此，方程式 $\\tan(x) = {value}$ 的通解為："
            }
        }
    }
    
    def __init__(self, options=None):
        """初始化生成器。
        
        Args:
            options: 可選的配置項。
        """
        super().__init__(options)
        self.options = options or {}
        
        # 三角函數
        self.trig_functions = ["sin", "cos", "tan"]
        
        # 建立 SymPy 符號
        self.x = sympy.Symbol('x')
        
        # 特殊角度定義（弧度制）
        self.special_angles_data = [
            {"rad": 0, "deg": 0, "sin": 0, "cos": 1, "tan": 0},
            {"rad": sympy.pi/6, "deg": 30, "sin": sympy.Rational(1,2), "cos": sympy.sqrt(3)/2, "tan": sympy.sqrt(3)/3},
            {"rad": sympy.pi/4, "deg": 45, "sin": sympy.sqrt(2)/2, "cos": sympy.sqrt(2)/2, "tan": 1},
            {"rad": sympy.pi/3, "deg": 60, "sin": sympy.sqrt(3)/2, "cos": sympy.Rational(1,2), "tan": sympy.sqrt(3)},
            {"rad": sympy.pi/2, "deg": 90, "sin": 1, "cos": 0, "tan": None},  # tan(90°) 未定義
            {"rad": 2*sympy.pi/3, "deg": 120, "sin": sympy.sqrt(3)/2, "cos": -sympy.Rational(1,2), "tan": -sympy.sqrt(3)},
            {"rad": 3*sympy.pi/4, "deg": 135, "sin": sympy.sqrt(2)/2, "cos": -sympy.sqrt(2)/2, "tan": -1},
            {"rad": 5*sympy.pi/6, "deg": 150, "sin": sympy.Rational(1,2), "cos": -sympy.sqrt(3)/2, "tan": -sympy.sqrt(3)/3},
            {"rad": sympy.pi, "deg": 180, "sin": 0, "cos": -1, "tan": 0},
            {"rad": 7*sympy.pi/6, "deg": 210, "sin": -sympy.Rational(1,2), "cos": -sympy.sqrt(3)/2, "tan": sympy.sqrt(3)/3},
            {"rad": 5*sympy.pi/4, "deg": 225, "sin": -sympy.sqrt(2)/2, "cos": -sympy.sqrt(2)/2, "tan": 1},
            {"rad": 4*sympy.pi/3, "deg": 240, "sin": -sympy.sqrt(3)/2, "cos": -sympy.Rational(1,2), "tan": sympy.sqrt(3)},
            {"rad": 3*sympy.pi/2, "deg": 270, "sin": -1, "cos": 0, "tan": None},  # tan(270°) 未定義
            {"rad": 5*sympy.pi/3, "deg": 300, "sin": -sympy.sqrt(3)/2, "cos": sympy.Rational(1,2), "tan": -sympy.sqrt(3)},
            {"rad": 7*sympy.pi/4, "deg": 315, "sin": -sympy.sqrt(2)/2, "cos": sympy.sqrt(2)/2, "tan": -1},
            {"rad": 11*sympy.pi/6, "deg": 330, "sin": -sympy.Rational(1,2), "cos": sympy.sqrt(3)/2, "tan": -sympy.sqrt(3)/3},
        ]
        
        # 答案表示方式選項
        self.answer_formats = ["degree", "radian"]
        
    def generate_question(self) -> Dict[str, Any]:
        """生成一個題目及其相關資訊。
        
        Returns:
            包含題目資訊的字典。
        """
        # 隨機選擇答案表示方式（角度或弧度）
        answer_format = random.choice(self.answer_formats)
        
        # 隨機選擇三角函數
        trig_func = random.choice(self.trig_functions)
        
        # 隨機選擇一個特殊角度，確保該函數有定義
        valid_angles = [angle for angle in self.special_angles_data if angle[trig_func] is not None]
        selected_angle = random.choice(valid_angles)
        
        angle_rad = selected_angle["rad"]
        angle_deg = selected_angle["deg"]
        func_value = selected_angle[trig_func]
        
        # 生成題目
        question_text = f"解方程式 ${trig_func}(x) = {sympy.latex(func_value)}$，"
        if answer_format == "degree":
            question_text += "以角度表示。"
        else:
            question_text += "以弧度表示。"
        
        # 生成答案和詳解
        answer_text, explanation_text = self._generate_answer_and_explanation(
            trig_func, func_value, angle_rad, angle_deg, answer_format
        )
        
        return {
            "question": question_text,
            "answer": answer_text,
            "explanation": explanation_text,
            "size": self.get_question_size(),
            "difficulty": "MEDIUM",
            "figure_data_question": None,
            "figure_data_explanation": None
        }
    
    def _generate_answer_and_explanation(
        self, trig_func: str, func_value: sympy.Expr, base_angle_rad: sympy.Expr, 
        base_angle_deg: int, answer_format: str
    ) -> Tuple[str, str]:
        """生成答案和詳解。
        
        Args:
            trig_func: 三角函數名稱。
            func_value: 函數值。
            base_angle_rad: 基本角度（弧度）。
            base_angle_deg: 基本角度（度數）。
            answer_format: 答案表示方式（"degree"或"radian"）。
        
        Returns:
            答案和詳解的字串。
        """
        if answer_format == "degree":
            return self._generate_degree_solution(trig_func, func_value, base_angle_deg)
        else:
            return self._generate_radian_solution(trig_func, func_value, base_angle_rad)
    
    def _generate_degree_solution(self, trig_func: str, func_value: sympy.Expr, base_angle_deg: int) -> Tuple[str, str]:
        """生成以角度表示的解答。"""
        # 找出基本解
        basic_solutions = [base_angle_deg]
        
        # 根據三角函數性質找出其他解
        if trig_func == "sin":
            # sin(x) = sin(θ) => x = θ + 360n° 或 x = (180° - θ) + 360n°
            additional_angle = 180 - base_angle_deg
            if additional_angle != base_angle_deg and 0 <= additional_angle <= 360:
                basic_solutions.append(additional_angle)
        elif trig_func == "cos":
            # cos(x) = cos(θ) => x = θ + 360n° 或 x = -θ + 360n° (即 360° - θ)
            additional_angle = 360 - base_angle_deg
            if additional_angle != base_angle_deg and additional_angle != 360:
                basic_solutions.append(additional_angle)
        # tan 函數在一個週期內只有一個解
        
        # 排序基本解
        basic_solutions.sort()
        
        # 生成通解
        period_deg = 360 if trig_func in ["sin", "cos"] else 180
        general_solutions = [f"x = {angle}° + {period_deg}°n" for angle in basic_solutions]
        
        # 生成答案
        if len(general_solutions) == 1:
            answer_text = f"${general_solutions[0]}$，其中 $n \\in \\mathbb{{Z}}$"
        else:
            answer_text = f"$" + "$ 或 $".join(general_solutions) + "$，其中 $n \\in \\mathbb{Z}$"
        
        # 生成詳解
        explanation_text = self._generate_degree_explanation(
            trig_func, func_value, basic_solutions, period_deg
        )
        
        return answer_text, explanation_text
    
    def _generate_radian_solution(self, trig_func: str, func_value: sympy.Expr, base_angle_rad: sympy.Expr) -> Tuple[str, str]:
        """生成以弧度表示的解答。"""
        # 找出基本解
        basic_solutions = [base_angle_rad]
        
        # 根據三角函數性質找出其他解
        if trig_func == "sin":
            # sin(x) = sin(θ) => x = θ + 2πn 或 x = (π - θ) + 2πn
            additional_angle = sympy.pi - base_angle_rad
            # 簡化並檢查是否為不同的解
            additional_angle = sympy.simplify(additional_angle)
            if not sympy.simplify(additional_angle - base_angle_rad).equals(0):
                basic_solutions.append(additional_angle)
        elif trig_func == "cos":
            # cos(x) = cos(θ) => x = θ + 2πn 或 x = -θ + 2πn (即 2π - θ)
            additional_angle = 2*sympy.pi - base_angle_rad
            additional_angle = sympy.simplify(additional_angle)
            if not sympy.simplify(additional_angle - base_angle_rad).equals(0) and additional_angle != 2*sympy.pi:
                basic_solutions.append(additional_angle)
        # tan 函數在一個週期內只有一個解
        
        # 生成通解
        period_rad = 2*sympy.pi if trig_func in ["sin", "cos"] else sympy.pi
        general_solutions = [f"x = {sympy.latex(angle)} + {sympy.latex(period_rad)}n" for angle in basic_solutions]
        
        # 生成答案
        if len(general_solutions) == 1:
            answer_text = f"${general_solutions[0]}$，其中 $n \\in \\mathbb{{Z}}$"
        else:
            answer_text = f"$" + "$ 或 $".join(general_solutions) + "$，其中 $n \\in \\mathbb{Z}$"
        
        # 生成詳解
        explanation_text = self._generate_radian_explanation(
            trig_func, func_value, basic_solutions, period_rad
        )
        
        return answer_text, explanation_text
    
    def _generate_degree_explanation(self, trig_func: str, func_value: sympy.Expr, 
                                   basic_solutions: List[int], period_deg: int) -> str:
        """使用模版生成以角度表示的詳解。"""
        template = self.SOLUTION_TEMPLATES["degree"][trig_func]
        
        explanation_parts = []
        
        # 步驟1：介紹和基本解
        explanation_parts.append(template["intro"].format(value=sympy.latex(func_value)))
        explanation_parts.append("")
        explanation_parts.append(template["basic_solution"].format(
            angle=basic_solutions[0], 
            value=sympy.latex(func_value)
        ))
        explanation_parts.append("")
        
        # 步驟2：額外解（如果有）
        if len(basic_solutions) > 1:
            explanation_parts.append(template["additional_solution"].format(
                base_angle=basic_solutions[0],
                additional_angle=basic_solutions[1]
            ))
            next_step = 3
        else:
            explanation_parts.append(template["no_additional"])
            next_step = 3 if trig_func == "tan" else 2
        
        explanation_parts.append("")
        
        # 步驟3：通解
        explanation_parts.append(template["general_solution"].format(step=next_step))
        explanation_parts.append("")
        
        for i, angle in enumerate(basic_solutions):
            explanation_parts.append(f"   $x = {angle}° + {period_deg}°n$，其中 $n \\in \\mathbb{{Z}}$")
        
        # 最終答案（如果有多個解）
        if len(basic_solutions) > 1:
            explanation_parts.append("")
            explanation_parts.append(template["final_answer"].format(
                step=next_step + 1,
                value=sympy.latex(func_value)
            ))
            explanation_parts.append("")
            general_solutions = [f"x = {angle}° + {period_deg}°n" for angle in basic_solutions]
            explanation_parts.append(f"   $" + "$ 或 $".join(general_solutions) + "$，其中 $n \\in \\mathbb{Z}$")
        
        return "\n".join(explanation_parts)
    
    def _generate_radian_explanation(self, trig_func: str, func_value: sympy.Expr,
                                   basic_solutions: List[sympy.Expr], period_rad: sympy.Expr) -> str:
        """使用模版生成以弧度表示的詳解。"""
        template = self.SOLUTION_TEMPLATES["radian"][trig_func]
        
        explanation_parts = []
        
        # 步驟1：介紹和基本解
        explanation_parts.append(template["intro"].format(value=sympy.latex(func_value)))
        explanation_parts.append("")
        explanation_parts.append(template["basic_solution"].format(
            angle=sympy.latex(basic_solutions[0]), 
            value=sympy.latex(func_value)
        ))
        explanation_parts.append("")
        
        # 步驟2：額外解（如果有）
        if len(basic_solutions) > 1:
            explanation_parts.append(template["additional_solution"].format(
                base_angle=sympy.latex(basic_solutions[0]),
                additional_angle=sympy.latex(basic_solutions[1])
            ))
            next_step = 3
        else:
            explanation_parts.append(template["no_additional"])
            next_step = 3 if trig_func == "tan" else 2
        
        explanation_parts.append("")
        
        # 步驟3：通解
        explanation_parts.append(template["general_solution"].format(step=next_step))
        explanation_parts.append("")
        
        for i, angle in enumerate(basic_solutions):
            explanation_parts.append(f"   $x = {sympy.latex(angle)} + {sympy.latex(period_rad)}n$，其中 $n \\in \\mathbb{{Z}}$")
        
        # 最終答案（如果有多個解）
        if len(basic_solutions) > 1:
            explanation_parts.append("")
            explanation_parts.append(template["final_answer"].format(
                step=next_step + 1,
                value=sympy.latex(func_value)
            ))
            explanation_parts.append("")
            general_solutions = [f"x = {sympy.latex(angle)} + {sympy.latex(period_rad)}n" for angle in basic_solutions]
            explanation_parts.append(f"   $" + "$ 或 $".join(general_solutions) + "$，其中 $n \\in \\mathbb{Z}$")
        
        return "\n".join(explanation_parts)
    
    def get_question_size(self) -> int:
        """獲取題目大小。"""
        return QuestionSize.MEDIUM
    
    def get_category(self) -> str:
        """獲取題目主類別。"""
        return "三角比"
    
    def get_subcategory(self) -> str:
        """獲取題目子類別。"""
        return "三角方程式求解"