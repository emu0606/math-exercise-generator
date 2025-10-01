#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 三角反函數題目生成器

生成特殊角的三角反函數計算練習題目，採用台灣高中教育習慣的sin⁻¹表示法。
使用簡化架構確保教學邏輯正確性，options.get()提供彈性配置。
"""

import random
import math
from typing import Dict, Any, Optional

import sympy
from sympy import latex, rad

from utils import get_logger
from ..base import QuestionGenerator, QuestionSize, register_generator

logger = get_logger(__name__)


@register_generator
class InverseTrigonometricFunctionGenerator(QuestionGenerator):
    """三角反函數題目生成器

    生成特殊角的三角反函數計算練習題目，採用台灣高中教育習慣的sin⁻¹表示法。

    Args:
        options (Dict[str, Any], optional): 生成器配置選項
            functions (List[str]): 允許的函數類型，預設["sin", "cos", "tan"]
            difficulty (str): 題目難度等級，預設"MEDIUM"

    Returns:
        Dict[str, Any]: 包含題目、答案、解釋等完整資訊

    Example:
        >>> generator = InverseTrigonometricFunctionGenerator()
        >>> question = generator.generate_question()
        >>> print(question['question'])
        $\\sin^{-1}(\\frac{1}{2}) = $
        >>> print(question['grade'])
        G10S2
    """

    def __init__(self, options: Dict[str, Any] = None):
        """初始化三角反函數題目生成器"""
        super().__init__(options)
        self.logger = get_logger(self.__class__.__name__)

        # 使用options.get()提供彈性配置：簡單的參數配置無需複雜驗證框架
        # 適合參數少且邏輯簡單的生成器，避免過度工程化
        options = options or {}

        # 設定可用的三角函數及其對應的反三角函數
        self.functions = options.get("functions", ["sin", "cos", "tan"])

        # 台灣高中教育習慣的反三角函數名稱映射
        self.func_name_map = {
            "sin": "\\sin^{-1}",
            "cos": "\\cos^{-1}",
            "tan": "\\tan^{-1}"
        }

        # 預建特殊角度清單，為學生好記憶：包含30°、45°、60°及其象限角
        # 涵蓋四個象限確保完整性，避免動態計算導致非標準角度
        # 這些角度的三角函數值都是標準根號形式，便於教學和記憶
        self.special_angles = [
            -90, -60, -45, -30, 0, 30, 45, 60, 90,
            120, 135, 150, 180, 210, 225, 240, 270
        ]

        # 反三角函數值域範圍，確保數學符號被$包裹
        self.value_ranges = {
            "sin": "$[-90^\\circ, 90^\\circ]$",
            "cos": "$[0^\\circ, 180^\\circ]$",
            "tan": "$(-90^\\circ, 90^\\circ)$"
        }

        # 難度設為備用鍵值，不實現複雜分級邏輯
        self.difficulty = options.get("difficulty", "MEDIUM")

        self.logger.info("三角反函數生成器初始化完成")

    def _generate_core_question(self) -> Dict[str, Any]:
        """核心三角反函數題目生成邏輯

        使用正確的教學邏輯：特殊角→函數值→反函數題目。
        采用確定性設計，使用預建特殊角清單避免隨機失敗。
        """
        # 1. 先選擇函數類型
        func_name = random.choice(self.functions)

        # 2. 根據函數選擇合適的特殊角度（教學重點）
        if func_name == "tan":
            # 排除90°和270°：tan函數在這些角度未定義（分母cos=0）
            # 避免生成無意義題目，確保所有題目都有明確答案
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

        # 使用Sympy的latex()函數確保根號、分數等複雜表達式的LaTeX格式標準化
        # 避免手動字串拼接可能產生的格式錯誤，特別是√2/2、√3/2等表達式
        value_latex = latex(value)

        # 5. 生成題目文字，使用台灣教育習慣的表示法
        question_text = f"${self.func_name_map[func_name]}({value_latex}) = $"

        # 使用LaTeX度數符號^\\circ避免Unicode°錯誤：確保PDF正確顯示
        answer = f"${adjusted_angle}^\\circ$"

        # 生成解析，使用LaTeX換行而非HTML標籤，避免PDF中顯示錯誤
        explanation = self._generate_explanation(func_name, value_latex, adjusted_angle)

        return {
            "question": question_text,
            "answer": answer,
            "explanation": explanation,
            **self._get_standard_metadata()
        }

    def _adjust_angle_to_range(self, angle_deg: int, func_name: str) -> int:
        """將角度調整到對應反三角函數的標準值域範圍內

        這是核心教學邏輯，確保：
        - arcsin值域為[-90°, 90°]
        - arccos值域為[0°, 180°]
        - arctan值域為(-90°, 90°)

        Args:
            angle_deg: 輸入角度
            func_name: 函數名稱

        Returns:
            int: 調整後的角度
        """
        if func_name == "sin":
            # arcsin值域為[-90°, 90°]：避免反函數歧義，確保唯一解
            if -90 <= angle_deg <= 90:
                return angle_deg
            elif 90 < angle_deg <= 270:
                return 180 - angle_deg  # 利用sin(180°-θ)=sin(θ)取補角
            else:  # 270 < angle_deg
                return angle_deg - 360  # 轉為負角，保持在值域內

        elif func_name == "cos":
            # arccos值域為[0°, 180°]：避免反函數歧義，確保唯一解
            if 0 <= angle_deg <= 180:
                return angle_deg
            elif -90 <= angle_deg < 0:
                return abs(angle_deg)  # 利用cos(-θ)=cos(θ)的偶函數性質
            else:  # 180 < angle_deg <= 270
                return 360 - angle_deg  # 轉為對稱角度

        else:  # func_name == "tan"
            # arctan值域為(-90°, 90°)：避免反函數歧義，確保唯一解
            if -90 < angle_deg <= 90:
                return angle_deg
            else:  # 90 < angle_deg <= 270，不包含-90和90
                return angle_deg - 180  # 利用tan週期性：tan(θ+180°)=tan(θ)

    def _generate_explanation(self, func_name: str, value_latex: str, adjusted_angle: int) -> str:
        """生成詳細解析，包含其他可能的角度

        Args:
            func_name: 三角函數名稱
            value_latex: LaTeX格式的函數輸入值
            adjusted_angle: 調整後的角度（度數）

        Returns:
            str: LaTeX格式的解釋文本
        """
        inv_func_name = self.func_name_map[func_name]

        # 根據函數類型確定其他角度
        if func_name == "sin":
            other_angle = 180 - adjusted_angle  # 補角
        elif func_name == "cos":
            other_angle = -adjusted_angle  # 負角
            if other_angle < 0:
                other_angle += 360
        else:  # tan
            other_angle = adjusted_angle + 180

        # 使用LaTeX換行符號\\\\[0.3em]而非HTML的<br>：確保PDF編譯正確
        # 避免HTML標籤在LaTeX環境中產生顯示錯誤
        explanation_steps = [
            f"$\\{func_name}({adjusted_angle}^\\circ) = \\{func_name}({other_angle}^\\circ) = {value_latex}$",
            f"但 ${inv_func_name}$ 的值域為 {self.value_ranges.get(func_name, '$未知$')}",
            f"因此 ${inv_func_name}({value_latex}) = {adjusted_angle}^\\circ$"
        ]

        return "\\\\\\\\[0.3em]".join(explanation_steps)

    def _get_fallback_question(self) -> Dict[str, Any]:
        """獲取後備題目

        當核心生成邏輯失敗時，提供固定的有效題目作為安全機制。
        選擇簡單、可靠的sin^{-1}(1/2)題目，確保系統在任何情況下都能產生有效輸出。

        Returns:
            Dict[str, Any]: 後備題目的完整資訊
        """
        self.logger.info("使用後備三角反函數題目")

        return {
            "question": "$\\sin^{-1}(\\frac{1}{2}) = $",
            "answer": "$30^\\circ$",
            "explanation": (
                "$\\sin(30^\\circ) = \\sin(150^\\circ) = \\frac{1}{2}$\\\\[0.3em]"
                "但 $\\sin^{-1}$ 的值域為 $[-90^\\circ, 90^\\circ]$\\\\[0.3em]"
                "因此 $\\sin^{-1}(\\frac{1}{2}) = 30^\\circ$"
            ),
            **self._get_standard_metadata()
        }

    def get_grade(self) -> str:
        """獲取適用年級"""
        return "G10S2"  # 高一下學期（三角反函數適用年級）

    def get_difficulty(self) -> str:
        """獲取難度等級"""
        return self.difficulty

    # 以下方法實現標準介面，確保與PDF生成系統相容
    def get_question_size(self) -> int:
        """獲取題目顯示大小"""
        return QuestionSize.SMALL.value

    def get_category(self) -> str:
        """獲取題目主類別"""
        return "三角函數"

    def get_subcategory(self) -> str:
        """獲取題目子類別"""
        return "反三角函數值計算"

    def get_subject(self) -> str:
        """獲取科目，數學測驗生成器標準實作"""
        return "數學"

    def get_figure_data_question(self) -> Optional[Dict[str, Any]]:
        """獲取題目圖形數據，反三角函數題目通常無需圖形輔助"""
        return None

    def get_figure_data_explanation(self) -> Optional[Dict[str, Any]]:
        """獲取解釋圖形數據，反三角函數題目通常無需圖形輔助"""
        return None

    def get_figure_position(self) -> str:
        """獲取題目圖形位置，標準配置為右側"""
        return "right"

    def get_explanation_figure_position(self) -> str:
        """獲取解釋圖形位置，標準配置為右側"""
        return "right"