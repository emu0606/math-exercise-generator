#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 三角方程式求解生成器

生成基礎三角方程式求解練習題目，支援角度/弧度雙模式及通解/範圍解雙類型。
使用預建查表策略確保數學邏輯100%正確，避免邊界情況遺漏。
"""

import random
from typing import Dict, Any, Optional, List, Tuple

import sympy
from sympy import latex, pi, sin, cos, tan, Rational, sqrt

from utils import get_logger
from ..base import QuestionGenerator, QuestionSize, register_generator

logger = get_logger(__name__)


@register_generator
class TrigEquationSolverGenerator(QuestionGenerator):
    """三角方程式求解生成器

    生成形如 sin(x) = value, cos(x) = value, tan(x) = value 的基礎三角方程式求解題目。
    支援通解和限定範圍解兩種答案類型，以及角度/弧度雙模式輸出。

    配置選項：
        angle_unit (str): 角度單位模式 - "角度"、"弧度"、"混合"
        answer_type (str): 答案類型 - "通解"、"範圍解"、"混合"

    Returns:
        Dict[str, Any]: 包含題目、答案、詳解等完整資訊

    Example:
        >>> generator = TrigEquationSolverGenerator()
        >>> question = generator.generate_question()
        >>> print(question['question'])
        請寫出 $\\sin(x) = \\frac{1}{2}$ 的通解，以角度表示。
    """

    def __init__(self, options: Dict[str, Any] = None):
        """初始化三角方程式求解生成器"""
        super().__init__(options)
        self.logger = get_logger(self.__class__.__name__)

        options = options or {}

        # 配置項讀取
        self.angle_unit_mode = options.get("angle_unit", "混合")
        self.answer_type_mode = options.get("answer_type", "混合")

        # 預建特殊角資料表（使用sympy確保精確計算）
        self._build_special_angles()

        # 預建完整解表（核心策略：查表方案）
        self._build_solution_table()

        self.logger.info(f"三角方程式生成器初始化完成 (角度模式: {self.angle_unit_mode}, 答案類型: {self.answer_type_mode})")

    @classmethod
    def get_config_schema(cls):
        """配置項架構定義（UI顯示用）"""
        return {
            "angle_unit": {
                "type": "select",
                "label": "角度單位",
                "default": "混合",
                "options": ["角度", "弧度", "混合"],
                "description": "題目和答案的角度單位表示方式"
            },
            "answer_type": {
                "type": "select",
                "label": "答案類型",
                "default": "混合",
                "options": ["通解", "範圍解", "混合"],
                "description": "通解為週期性通解，範圍解為限定區間解"
            }
        }

    def _build_special_angles(self):
        """預建特殊角資料表

        包含 0°~360° 範圍內 16 個標準特殊角的完整三角函數值。
        使用 sympy 確保精確計算，避免浮點誤差。
        """
        self.special_angles = [
            {"deg": 0, "rad": 0, "sin": 0, "cos": 1, "tan": 0},
            {"deg": 30, "rad": pi/6, "sin": Rational(1,2), "cos": sqrt(3)/2, "tan": sqrt(3)/3},
            {"deg": 45, "rad": pi/4, "sin": sqrt(2)/2, "cos": sqrt(2)/2, "tan": 1},
            {"deg": 60, "rad": pi/3, "sin": sqrt(3)/2, "cos": Rational(1,2), "tan": sqrt(3)},
            {"deg": 90, "rad": pi/2, "sin": 1, "cos": 0, "tan": None},
            {"deg": 120, "rad": 2*pi/3, "sin": sqrt(3)/2, "cos": -Rational(1,2), "tan": -sqrt(3)},
            {"deg": 135, "rad": 3*pi/4, "sin": sqrt(2)/2, "cos": -sqrt(2)/2, "tan": -1},
            {"deg": 150, "rad": 5*pi/6, "sin": Rational(1,2), "cos": -sqrt(3)/2, "tan": -sqrt(3)/3},
            {"deg": 180, "rad": pi, "sin": 0, "cos": -1, "tan": 0},
            {"deg": 210, "rad": 7*pi/6, "sin": -Rational(1,2), "cos": -sqrt(3)/2, "tan": sqrt(3)/3},
            {"deg": 225, "rad": 5*pi/4, "sin": -sqrt(2)/2, "cos": -sqrt(2)/2, "tan": 1},
            {"deg": 240, "rad": 4*pi/3, "sin": -sqrt(3)/2, "cos": -Rational(1,2), "tan": sqrt(3)},
            {"deg": 270, "rad": 3*pi/2, "sin": -1, "cos": 0, "tan": None},
            {"deg": 300, "rad": 5*pi/3, "sin": -sqrt(3)/2, "cos": Rational(1,2), "tan": -sqrt(3)},
            {"deg": 315, "rad": 7*pi/4, "sin": -sqrt(2)/2, "cos": sqrt(2)/2, "tan": -1},
            {"deg": 330, "rad": 11*pi/6, "sin": -Rational(1,2), "cos": sqrt(3)/2, "tan": -sqrt(3)/3},
        ]

    def _build_solution_table(self):
        """預建完整解表（核心策略：查表方案）

        為每個三角函數值預先計算所有可能的解（所有範圍）。
        這樣生成時只需查表，確保 100% 正確，避免即時計算的邊界判斷錯誤。
        """
        self.solutions = {
            "sin": {},
            "cos": {},
            "tan": {}
        }

        for angle_data in self.special_angles:
            for func_name in ["sin", "cos", "tan"]:
                value = angle_data[func_name]

                # 跳過 tan 未定義的角度
                if value is None:
                    continue

                # 使用 sympy 表達式作為 key（確保精確匹配）
                value_key = str(value)

                # 如果這個值還沒有解集，初始化
                if value_key not in self.solutions[func_name]:
                    self.solutions[func_name][value_key] = {
                        "value_expr": value,
                        "deg_solutions": [],
                        "rad_solutions": []
                    }

                # 收集所有角度解（在 [0°, 360°) 範圍內）
                deg = angle_data["deg"]
                rad = angle_data["rad"]

                # 避免重複添加（因為不同象限可能有相同函數值）
                if deg not in self.solutions[func_name][value_key]["deg_solutions"]:
                    self.solutions[func_name][value_key]["deg_solutions"].append(deg)
                    self.solutions[func_name][value_key]["rad_solutions"].append(rad)

        # 排序解集（方便後續處理）
        for func_name in ["sin", "cos", "tan"]:
            for value_key in self.solutions[func_name]:
                self.solutions[func_name][value_key]["deg_solutions"].sort()
                self.solutions[func_name][value_key]["rad_solutions"].sort()

        self.logger.info("解表建立完成")

    def _generate_core_question(self) -> Dict[str, Any]:
        """核心題目生成邏輯"""

        # 1. 決定角度單位（角度/弧度/隨機）
        if self.angle_unit_mode == "混合":
            use_degree = random.choice([True, False])
        else:
            use_degree = (self.angle_unit_mode == "角度")

        # 2. 決定答案類型（通解/範圍解/隨機）
        if self.answer_type_mode == "混合":
            use_general = random.choice([True, False])
        else:
            use_general = (self.answer_type_mode == "通解")

        # 3. 隨機選擇函數和值
        func_name = random.choice(["sin", "cos", "tan"])
        value_key = random.choice(list(self.solutions[func_name].keys()))
        solution_data = self.solutions[func_name][value_key]

        value_expr = solution_data["value_expr"]
        value_latex = latex(value_expr)

        # 4. 生成題目
        if use_general:
            # 通解題型
            unit_text = "角度" if use_degree else "弧度"
            question = f"請寫出 $\\{func_name}(x) = {value_latex}$ 的通解，以{unit_text}表示。"

            answer, explanation = self._generate_general_solution(
                func_name, value_latex, solution_data, use_degree
            )
        else:
            # 範圍解題型
            # 隨機選擇範圍類型（50% 各）
            if use_degree:
                use_positive_range = random.choice([True, False])
                if use_positive_range:
                    range_text = "[0^\\circ, 360^\\circ)"
                    range_tuple = (0, 360)
                else:
                    range_text = "(-180^\\circ, 180^\\circ]"
                    range_tuple = (-180, 180)
            else:
                use_positive_range = random.choice([True, False])
                if use_positive_range:
                    range_text = "[0, 2\\pi)"
                    range_tuple = (0, 2*pi)
                else:
                    range_text = "(-\\pi, \\pi]"
                    range_tuple = (-pi, pi)

            unit_text = "角度" if use_degree else "弧度"
            question = f"求 $\\{func_name}(x) = {value_latex}$ 在 ${range_text}$ 範圍內的解，以{unit_text}表示。"

            answer, explanation = self._generate_range_solution(
                func_name, value_latex, solution_data, use_degree, range_tuple
            )

        return {
            "question": question,
            "answer": answer,
            "explanation": explanation,
            **self._get_standard_metadata()
        }

    def _generate_general_solution(
        self, func_name: str, value_latex: str,
        solution_data: Dict, use_degree: bool
    ) -> Tuple[str, str]:
        """生成通解題型的答案和詳解"""

        if use_degree:
            solutions = solution_data["deg_solutions"]
            period = 360 if func_name in ["sin", "cos"] else 180
            period_latex = f"{period}^\\circ"
            unit = "^\\circ"
        else:
            solutions = solution_data["rad_solutions"]
            period = 2*pi if func_name in ["sin", "cos"] else pi
            period_latex = latex(period)
            unit = ""

        # 答案格式（注意：換行符必須在數學模式外，否則不會換行）
        if len(solutions) == 1:
            if use_degree:
                sol_latex = f"{solutions[0]}{unit}"
                answer = f"$x = {sol_latex} + {period_latex} n, n \\in \\mathbb{{Z}}$"
            else:
                sol_latex = latex(solutions[0])
                answer = f"$x = {sol_latex} + {period_latex} n, n \\in \\mathbb{{Z}}$"
        else:
            # 兩個解的情況：換行符放在數學模式外才有效
            if use_degree:
                sol1_latex = f"{solutions[0]}{unit}"
                sol2_latex = f"{solutions[1]}{unit}"
                # 換行符在數學模式外：$...$或\\[0.5em]$...$
                answer = f"$x = {sol1_latex} + {period_latex} n$ 或 $x = {sol2_latex} + {period_latex} n, n \\in \\mathbb{{Z}}$"
            else:
                sol1_latex = latex(solutions[0])
                sol2_latex = latex(solutions[1])
                answer = f"$x = {sol1_latex} + {period_latex} n$ 或 $x = {sol2_latex} + {period_latex} n, n \\in \\mathbb{{Z}}$"

        # 詳解生成
        explanation_parts = []

        # 步驟1：基本角
        if use_degree:
            base_angle = f"{solutions[0]}{unit}"
        else:
            base_angle = latex(solutions[0])
        explanation_parts.append(f"1. 基本角：$\\{func_name}({base_angle}) = {value_latex}$")

        # 步驟2：對稱解（如果有）
        if len(solutions) > 1:
            if func_name == "sin":
                symmetry_property = "$\\sin(180^\\circ - \\theta) = \\sin(\\theta)$" if use_degree else "$\\sin(\\pi - \\theta) = \\sin(\\theta)$"
            elif func_name == "cos":
                symmetry_property = "$\\cos(360^\\circ - \\theta) = \\cos(\\theta)$" if use_degree else "$\\cos(2\\pi - \\theta) = \\cos(\\theta)$"
            else:
                symmetry_property = ""

            if use_degree:
                other_angle = f"{solutions[1]}{unit}"
            else:
                other_angle = latex(solutions[1])

            if symmetry_property:
                explanation_parts.append(f"2. 對稱解：由 {symmetry_property}，得 $x = {other_angle}$")

        # 步驟3：週期性通解
        period_name = "正弦" if func_name == "sin" else ("餘弦" if func_name == "cos" else "正切")
        step_num = 3 if len(solutions) > 1 else 2
        explanation_parts.append(f"{step_num}. 週期性：{period_name}函數週期為 ${period_latex}$，通解為：")

        # 詳解中的答案：不需要換行符（版面充足）
        if len(solutions) == 1:
            if use_degree:
                explanation_answer = f"   $x = {solutions[0]}{unit} + {period_latex} n, n \\in \\mathbb{{Z}}$"
            else:
                explanation_answer = f"   $x = {latex(solutions[0])} + {period_latex} n, n \\in \\mathbb{{Z}}$"
        else:
            if use_degree:
                explanation_answer = f"   $x = {solutions[0]}{unit} + {period_latex} n$ 或 ${solutions[1]}{unit} + {period_latex} n, n \\in \\mathbb{{Z}}$"
            else:
                explanation_answer = f"   $x = {latex(solutions[0])} + {period_latex} n$ 或 ${latex(solutions[1])} + {period_latex} n, n \\in \\mathbb{{Z}}$"

        explanation_parts.append(explanation_answer)

        explanation = "\n\n".join(explanation_parts)

        return answer, explanation

    def _generate_range_solution(
        self, func_name: str, value_latex: str,
        solution_data: Dict, use_degree: bool,
        range_tuple: Tuple
    ) -> Tuple[str, str]:
        """生成範圍解題型的答案和詳解"""

        if use_degree:
            base_solutions = solution_data["deg_solutions"]
            range_min, range_max = range_tuple
            unit = "^\\circ"

            # 轉換解到指定範圍
            valid_solutions = []
            for sol in base_solutions:
                # 將 [0, 360) 範圍的解轉換到目標範圍
                adjusted = sol
                while adjusted > range_max:
                    adjusted -= 360
                while adjusted <= range_min:
                    adjusted += 360

                if range_min < adjusted <= range_max:
                    if adjusted not in valid_solutions:
                        valid_solutions.append(adjusted)

            valid_solutions.sort()

        else:
            base_solutions = solution_data["rad_solutions"]
            range_min, range_max = range_tuple
            unit = ""

            # 轉換解到指定範圍
            valid_solutions = []
            for sol in base_solutions:
                adjusted = sol
                # 調整到範圍內（注意：[0, 2π) 左閉右開，(-π, π] 左開右閉）
                while sympy.simplify(adjusted - range_max).is_positive or sympy.simplify(adjusted - range_max).is_zero:
                    adjusted -= 2*pi
                while not (sympy.simplify(adjusted - range_min).is_positive or sympy.simplify(adjusted - range_min).is_zero):
                    adjusted += 2*pi

                # 簡化並檢查是否在範圍內
                adjusted_simplified = sympy.simplify(adjusted)

                # 檢查是否真的在範圍內（處理左開右閉或左閉右開）
                in_range = False
                if sympy.simplify(adjusted_simplified - range_min).is_positive and \
                   sympy.simplify(range_max - adjusted_simplified).is_positive:
                    in_range = True
                elif sympy.simplify(adjusted_simplified - range_max).is_zero:
                    # 右邊界：(-π, π] 包含，[0, 2π) 不包含
                    if range_max == pi or range_max == 180:  # 右閉
                        in_range = True
                elif sympy.simplify(adjusted_simplified - range_min).is_zero:
                    # 左邊界：[0, 2π) 包含，(-π, π] 不包含
                    if range_min == 0:  # 左閉
                        in_range = True

                if in_range:
                    # 避免重複
                    is_duplicate = False
                    for existing in valid_solutions:
                        if sympy.simplify(adjusted_simplified - existing).is_zero:
                            is_duplicate = True
                            break
                    if not is_duplicate:
                        valid_solutions.append(adjusted_simplified)

            # 排序（sympy表達式需要特殊處理）
            valid_solutions = sorted(valid_solutions, key=lambda x: float(x.evalf()))

        # 答案格式
        if len(valid_solutions) == 0:
            answer = "無解"
        elif len(valid_solutions) == 1:
            if use_degree:
                sol_latex = f"{valid_solutions[0]}{unit}"
            else:
                sol_latex = latex(valid_solutions[0])
            answer = f"$x = {sol_latex}$"
        else:
            if use_degree:
                sol_parts = [f"{s}{unit}" for s in valid_solutions]
            else:
                sol_parts = [latex(s) for s in valid_solutions]
            # 範圍解不需要換行符（放得進去）
            answer = "$x = " + "$ 或 $".join(sol_parts) + "$"

        # 詳解生成
        explanation_parts = []

        # 步驟1：基本角
        if use_degree:
            base_angle = f"{base_solutions[0]}{unit}"
        else:
            base_angle = latex(base_solutions[0])
        explanation_parts.append(f"1. 基本角：$\\{func_name}({base_angle}) = {value_latex}$")

        # 步驟2：對稱解（如果原始有多個解）
        if len(base_solutions) > 1:
            if func_name == "sin":
                symmetry_property = "$\\sin(180^\\circ - \\theta) = \\sin(\\theta)$" if use_degree else "$\\sin(\\pi - \\theta) = \\sin(\\theta)$"
            elif func_name == "cos":
                symmetry_property = "$\\cos(360^\\circ - \\theta) = \\cos(\\theta)$" if use_degree else "$\\cos(2\\pi - \\theta) = \\cos(\\theta)$"
            else:
                symmetry_property = ""

            if use_degree:
                other_angle = f"{base_solutions[1]}{unit}"
            else:
                other_angle = latex(base_solutions[1])

            if symmetry_property:
                explanation_parts.append(f"2. 對稱解：由 {symmetry_property}，得 $x = {other_angle}$")

        # 步驟3：範圍轉換（如需要）
        step_num = 3 if len(base_solutions) > 1 else 2
        if use_degree and range_tuple[0] < 0:
            explanation_parts.append(f"{step_num}. 範圍轉換：將角度轉換到 ${latex(range_tuple[0])}{unit}, {latex(range_tuple[1])}{unit}]$ 範圍")
            step_num += 1
        elif not use_degree and range_tuple[0] != 0:
            range_text = f"({latex(range_tuple[0])}, {latex(range_tuple[1])}]"
            explanation_parts.append(f"{step_num}. 範圍轉換：將角度轉換到 ${range_text}$ 範圍")
            step_num += 1

        # 步驟4：最終答案
        explanation_parts.append(f"{step_num}. 在指定範圍內的解為：{answer}")

        explanation = "\n\n".join(explanation_parts)

        return answer, explanation

    def _get_fallback_question(self) -> Dict[str, Any]:
        """獲取後備題目"""
        self.logger.info("使用後備三角方程式題目")

        return {
            "question": "請寫出 $\\sin(x) = \\frac{1}{2}$ 的通解，以角度表示。",
            "answer": "$x = 30^\\circ + 360^\\circ n$ 或\\\\[0.5em]$x = 150^\\circ + 360^\\circ n, n \\in \\mathbb{Z}$",
            "explanation": (
                "1. 基本角：$\\sin(30^\\circ) = \\frac{1}{2}$\n\n"
                "2. 對稱解：由 $\\sin(180^\\circ - \\theta) = \\sin(\\theta)$，得 $x = 150^\\circ$\n\n"
                "3. 週期性：正弦函數週期為 $360^\\circ$，通解為：\n\n"
                "   $x = 30^\\circ + 360^\\circ n$ 或 $x = 150^\\circ + 360^\\circ n, n \\in \\mathbb{Z}$"
            ),
            **self._get_standard_metadata()
        }

    def get_grade(self) -> str:
        """獲取適用年級"""
        return "G11S1"  # 高二上學期

    def get_difficulty(self) -> str:
        """獲取難度等級"""
        return "MEDIUM"

    def get_question_size(self) -> int:
        """獲取題目顯示大小"""
        return QuestionSize.MEDIUM.value

    def get_category(self) -> str:
        """獲取題目主類別"""
        return "三角函數"

    def get_subcategory(self) -> str:
        """獲取題目子類別"""
        return "三角方程式求解"

    def get_subject(self) -> str:
        """獲取科目"""
        return "數學"

    def get_figure_data_question(self) -> Optional[Dict[str, Any]]:
        """獲取題目圖形數據"""
        return None

    def get_figure_data_explanation(self) -> Optional[Dict[str, Any]]:
        """獲取解釋圖形數據"""
        return None

    def get_figure_position(self) -> str:
        """獲取題目圖形位置"""
        return "right"

    def get_explanation_figure_position(self) -> str:
        """獲取解釋圖形位置"""
        return "right"
