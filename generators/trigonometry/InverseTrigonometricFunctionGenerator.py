#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 三角反函數題目生成器

生成特殊角的三角反函數計算練習題目，採用台灣高中教育習慣的sin⁻¹表示法。
使用簡化架構確保教學邏輯正確性，options.get()提供彈性配置。
"""

import random
import math
from typing import Dict, Any

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

        # 使用options.get()提供彈性配置，避免複雜驗證框架
        options = options or {}

        # 設定可用的三角函數及其對應的反三角函數
        self.functions = options.get("functions", ["sin", "cos", "tan"])

        # 台灣高中教育習慣的反三角函數名稱映射
        self.func_name_map = {
            "sin": "\\sin^{-1}",
            "cos": "\\cos^{-1}",
            "tan": "\\tan^{-1}"
        }

        # 特殊角度列表（以度數表示），確保教學正確性
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

    def generate_question(self) -> Dict[str, Any]:
        """生成一個三角反函數計算題目

        使用正確的教學邏輯：特殊角→函數值→反函數題目
        """
        self.logger.info("開始生成三角反函數題目")

        try:
            # 1. 先選擇函數類型
            func_name = random.choice(self.functions)

            # 2. 根據函數選擇合適的特殊角度（教學重點）
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

            # 5. 格式化值的顯示，使用Sympy確保LaTeX格式正確
            value_latex = latex(value)

            # 6. 生成題目文字，使用台灣教育習慣的表示法
            question_text = f"${self.func_name_map[func_name]}({value_latex}) = $"

            # 7. 生成答案，使用正確的LaTeX度數符號
            answer = f"${adjusted_angle}^\\circ$"

            # 8. 生成解析，使用LaTeX換行而非HTML標籤
            explanation = self._generate_explanation(func_name, value_latex, adjusted_angle)

            return {
                "question": question_text,
                "answer": answer,
                "explanation": explanation,
                **self._get_standard_metadata()
            }

        except Exception as e:
            # 當動態生成失敗時，使用預設題目確保系統穩定性
            self.logger.warning(f"生成反三角函數題目時出錯: {str(e)}")
            return self._get_default_question()

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

        # 使用LaTeX換行而非HTML標籤，避免PDF中顯示錯誤
        explanation_steps = [
            f"$\\{func_name}({adjusted_angle}^\\circ) = \\{func_name}({other_angle}^\\circ) = {value_latex}$",
            f"但 ${inv_func_name}$ 的值域為 {self.value_ranges.get(func_name, '$未知$')}",
            f"因此 ${inv_func_name}({value_latex}) = {adjusted_angle}^\\circ$"
        ]

        return "\\\\\\\\[0.3em]".join(explanation_steps)

    def _get_default_question(self) -> Dict[str, Any]:
        """獲取預設題目

        當動態生成失敗時，提供固定的有效題目作為安全機制。

        Returns:
            Dict[str, Any]: 預設題目的完整資訊
        """
        self.logger.info("使用預設三角反函數題目")

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

    def _get_standard_metadata(self) -> Dict[str, Any]:
        """獲取標準元數據

        提供PDF生成所需的完整元數據，包括尺寸、難度、分類等資訊。

        Returns:
            Dict[str, Any]: 包含標準元數據的字典
        """
        return {
            "size": self.get_question_size(),  # SMALL - 三角反函數題目較簡潔
            "difficulty": self.difficulty,     # 預設"MEDIUM"，可配置
            "category": self.get_category(),   # "三角函數"
            "subcategory": self.get_subcategory(),  # "反三角函數值計算"
            "grade": "G10S2",  # 高一下學期（三角反函數適用年級）
            # 預留圖形相關欄位，確保PDF相容
            "figure_data_question": None,
            "figure_data_explanation": None,
            "figure_position": "right",
            "explanation_figure_position": "right"
        }

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