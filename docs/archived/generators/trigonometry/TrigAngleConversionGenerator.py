#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 擴展版三角函數角度變換題生成器
"""

import random
from typing import Dict, Any, Tuple, List, Optional

from ..base import QuestionGenerator, QuestionSize, register_generator


@register_generator
class EnhancedTrigAngleConversionGenerator(QuestionGenerator):
    """擴展版三角函數角度變換題生成器
    
    生成三種類型的三角函數角度題目：
    1. 第一象限角轉換題 (70%)
    2. 純公式問答題 (10%) 
    3. 0~45度角轉換題 (20%)
    """
    
    # 三角函數的LaTeX表示
    FUNC_LATEX = {
        "sin": "\\sin",
        "cos": "\\cos",
        "tan": "\\tan",
        "cot": "\\cot"
    }
    
    # 公式問答題庫 (使用角度制)
    FORMULA_QUESTIONS = {
        "sin": [
            {"question": "\\sin(180^\\circ-\\theta) = ", "answer": "\\sin(\\theta)"},
            {"question": "\\sin(\\theta \\pm 180^\\circ) = ", "answer": "-\\sin(\\theta)"},
            {"question": "\\sin(-\\theta) = ", "answer": "-\\sin(\\theta)"},
            {"question": "\\sin(90^\\circ-\\theta) = ", "answer": "\\cos(\\theta)"},
            {"question": "\\sin(90^\\circ+\\theta) = ", "answer": "\\cos(\\theta)"}
        ],
        "cos": [
            {"question": "\\cos(180^\\circ-\\theta) = ", "answer": "-\\cos(\\theta)"},
            {"question": "\\cos(\\theta \\pm 180^\\circ) = ", "answer": "-\\cos(\\theta)"},
            {"question": "\\cos(-\\theta) = ", "answer": "\\cos(\\theta)"},
            {"question": "\\cos(90^\\circ-\\theta) = ", "answer": "\\sin(\\theta)"},
            {"question": "\\cos(90^\\circ+\\theta) = ", "answer": "-\\sin(\\theta)"}
        ],
        "tan": [
            {"question": "\\tan(180^\\circ-\\theta) = ", "answer": "-\\tan(\\theta)"},
            {"question": "\\tan(\\theta \\pm 180^\\circ) = ", "answer": "\\tan(\\theta)"},
            {"question": "\\tan(-\\theta) = ", "answer": "-\\tan(\\theta)"},
            {"question": "\\tan(90^\\circ-\\theta) = ", "answer": "\\cot(\\theta)"},
            {"question": "\\tan(90^\\circ+\\theta) = ", "answer": "-\\cot(\\theta)"}
        ]
    }

    
    def __init__(self, options: Optional[Dict[str, Any]] = None):
        """初始化生成器。
        
        Args:
            options: 可選的配置項。
        """
        super().__init__(options)
        self.options = options or {}
        
        # 設定可用的三角函數
        self.functions = ["sin", "cos", "tan"]
        
        # 基本角度 (-80度到260度，避開0度和90度的倍數)
        # 保留原始範圍以便讓學生練習負角關係
        self.base_angles = list(range(-80, 261, 10))
        # 移除0度和90度的倍數
        self.base_angles = [angle for angle in self.base_angles if angle % 90 != 0]
        
        # 難度設定
        self.difficulty = self.options.get("difficulty", "MEDIUM")
        
        # 設定各種題型的出現機率 (70%, 10%, 20%)
        self.mode_weights = [70, 10, 20]
    
    def generate_question(self) -> Dict[str, Any]:
        """生成一個題目及其相關資訊。
        
        Returns:
            包含題目資訊的字典。
        """
        # 隨機選擇題型模式
        mode = random.choices(
            ["original", "formula", "narrow_angle"], 
            weights=self.mode_weights
        )[0]
        
        if mode == "formula":
            return self._generate_formula_question()
        elif mode == "narrow_angle":
            return self._generate_narrow_angle_question()
        else:  # mode == "original"
            return self._generate_original_question()
    
    def _generate_formula_question(self) -> Dict[str, Any]:
        """生成公式問答題。
        
        Returns:
            包含題目資訊的字典。
        """
        # 選擇一個三角函數
        func = random.choice(self.functions)
        
        # 從該函數的題庫中隨機選一題
        question_data = random.choice(self.FORMULA_QUESTIONS[func])
        
        question_text = f"計算 ${question_data['question']}$"
        answer_text = f"${question_data['answer']}$"
        
        # 對於公式問答題，不提供詳解
        explanation_text = "公式基本關係題，請熟記基本公式。"
        
        return {
            "question": question_text,
            "answer": answer_text,
            "explanation": explanation_text,
            "size": self.get_question_size(),
            "difficulty": self.difficulty,
            "figure_data_question": None,
            "figure_data_explanation": None
        }
    
    def _generate_original_question(self) -> Dict[str, Any]:
        """生成原始的第一象限角轉換題。
        
        Returns:
            包含題目資訊的字典。
        """
        # 選擇一個三角函數
        func = random.choice(self.functions)
        func_latex = self.FUNC_LATEX[func]
        
        # 選擇一個角度作為基準
        base_angle = random.choice(self.base_angles)
        
        # 從 -4 到 4 選擇一個非零的倍數來生成超出基本範圍的角度
        multipliers = [m for m in range(-4, 5) if m != 0]
        turns = random.choice(multipliers)
        
        # 計算題目角度
        question_angle = base_angle + turns * 360
        
        # 確保 tan 函數的角度不是 90 度的奇數倍
        if func == "tan" and (question_angle % 180 == 90 or question_angle % 180 == -90):
            question_angle += 10  # 避開不合法的角度
        
        # 直接使用base_angle進行轉換，而不是question_angle
        # 這樣就不需要處理週期性，更符合教學需求
        first_quadrant_angle, sign = self._convert_to_first_quadrant(func, base_angle)
        
        # 生成題目文字
        question_text = f"以 $0\\sim90^\\circ$ 表示 ${func_latex}({question_angle}^\\circ)$ "
        
        # 生成答案，考慮正負號
        sign_text = "-" if sign == -1 else ""
        answer_text = f"${sign_text}{func_latex}({first_quadrant_angle}^\\circ)$"
        
        # 生成詳解
        explanation_text = self._generate_explanation(func, question_angle, first_quadrant_angle, sign, turns)
        
        return {
            "question": question_text,
            "answer": answer_text,
            "explanation": explanation_text,
            "size": self.get_question_size(),
            "difficulty": self.difficulty,
            "figure_data_question": None,
            "figure_data_explanation": None
        }
    
    def _generate_narrow_angle_question(self) -> Dict[str, Any]:
        """生成0~45度角轉換題。
        
        Returns:
            包含題目資訊的字典。
        """
        # 選擇一個三角函數
        func = random.choice(self.functions)
        func_latex = self.FUNC_LATEX[func]
        
        # 選擇一個角度作為基準
        base_angle = random.choice(self.base_angles)
        
        # 從 -4 到 4 選擇一個非零的倍數來生成超出基本範圍的角度
        multipliers = [m for m in range(-4, 5) if m != 0]
        turns = random.choice(multipliers)
        
        # 計算題目角度
        question_angle = base_angle + turns * 360
        
        # 確保 tan 函數的角度不是 90 度的奇數倍
        if func == "tan" and (question_angle % 180 == 90 or question_angle % 180 == -90):
            question_angle += 10  # 避開不合法的角度
        
        # 先轉換為第一象限角
        first_quadrant_angle, sign = self._convert_to_first_quadrant(func, base_angle)
        
        # 再轉換為0~45度角
        narrow_angle, new_sign, new_func = self._convert_to_narrow_angle(func, first_quadrant_angle, sign)
        new_func_latex = self.FUNC_LATEX[new_func]
        
        # 生成題目文字
        question_text = f"以 $0\\sim45^\\circ$ 表示 ${func_latex}({question_angle}^\\circ)$ "
        
        # 生成答案，考慮正負號
        sign_text = "-" if new_sign == -1 else ""
        answer_text = f"${sign_text}{new_func_latex}({narrow_angle}^\\circ)$"
        
        # 生成詳解，先轉為第一象限，再轉為窄角
        explanation_text = self._generate_narrow_angle_explanation(
            func, question_angle, first_quadrant_angle, sign, 
            new_func, narrow_angle, new_sign, turns
        )
        
        return {
            "question": question_text,
            "answer": answer_text,
            "explanation": explanation_text,
            "size": self.get_question_size(),
            "difficulty": self.difficulty,
            "figure_data_question": None,
            "figure_data_explanation": None
        }
    
    def _convert_to_first_quadrant(self, func: str, angle: int) -> Tuple[int, int]:
        """將給定角度轉換為對應的第一象限角，並返回符號。
        
        Args:
            func: 三角函數名稱。
            angle: 基本角度。
            
        Returns:
            Tuple[int, int]: (第一象限角度, 符號)，符號為1或-1。
        """
        # 根據象限和函數特性轉換為第一象限角並確定符號
        if 0 <= angle <= 90:  # 第一象限
            return angle, 1  # 直接返回角度，符號為正
        
        elif 90 < angle < 180:  # 第二象限
            # sin(180-x) = sin(x), cos(180-x) = -cos(x), tan(180-x) = -tan(x)
            equivalent_angle = 180 - angle
            if func == "sin":
                return equivalent_angle, 1
            else:  # cos or tan
                return equivalent_angle, -1
        
        elif 180 <= angle < 270:  # 第三象限
            # sin(180+x) = -sin(x), cos(180+x) = -cos(x), tan(180+x) = tan(x)
            equivalent_angle = angle - 180
            if func == "tan":
                return equivalent_angle, 1
            else:  # sin or cos
                return equivalent_angle, -1
        
        elif 270 <= angle < 360:  # 第四象限
            # sin(360-x) = -sin(x), cos(360-x) = cos(x), tan(360-x) = -tan(x)
            equivalent_angle = 360 - angle
            if func == "cos":
                return equivalent_angle, 1
            else:  # sin or tan
                return equivalent_angle, -1
        
        else:  # 處理負角 -90 < angle < 0
            # sin(-x) = -sin(x), cos(-x) = cos(x), tan(-x) = -tan(x)
            equivalent_angle = -angle  # 轉為正角度
            if func == "cos":
                return equivalent_angle, 1
            else:  # sin or tan
                return equivalent_angle, -1
    
    def _convert_to_narrow_angle(self, func: str, angle: int, sign: int) -> Tuple[int, int, str]:
        """將第一象限角（0~90度）轉換為窄角（0~45度）並返回新符號和函數。
        
        Args:
            func: 三角函數名稱。
            angle: 第一象限角度。
            sign: 原始符號 (1 或 -1)。
            
        Returns:
            Tuple[int, int, str]: (轉換後角度, 新符號, 新函數名稱)。
        """
        if 0 <= angle <= 45:
            return angle, sign, func  # 不變
        else:  # 45 < angle <= 90
            # 運用餘角公式
            new_angle = 90 - angle
            if func == "sin":
                return new_angle, sign, "cos"
            elif func == "cos":
                return new_angle, sign, "sin"
            else:  # tan
                return new_angle, sign, "cot"
    
    def _generate_explanation(self, func: str, original_angle: int, first_quadrant_angle: int, sign: int, turns: int) -> str:
        """生成轉換為第一象限的解析步驟。
        
        Args:
            func: 三角函數名稱。
            original_angle: 原始角度。
            first_quadrant_angle: 轉換後的第一象限角度。
            sign: 符號 (1 或 -1)。
            turns: 完整轉動圈數。
            
        Returns:
            解析步驟的 LaTeX 格式文字。
        """
        func_latex = self.FUNC_LATEX[func]
        
        # 僅處理超過一圈的角度，保留負角度
        base_angle = original_angle
        if turns != 0:
            # 首先移除完整圈數，但保留角度的正負性質
            base_angle = original_angle - turns * 360
        
        # 定義模板：
        # 1. 週期性處理模板
        periodicity_templates = {
            "positive_turns": f"${func_latex}({original_angle}^\\circ) = {func_latex}({original_angle}^\\circ - {turns} \\cdot 360^\\circ) = {func_latex}({base_angle}^\\circ)",
            "negative_turns": f"${func_latex}({original_angle}^\\circ) = {func_latex}({original_angle}^\\circ + {-turns} \\cdot 360^\\circ) = {func_latex}({base_angle}^\\circ)",
            "no_turns": f"${func_latex}({original_angle}^\\circ)"
        }
        
        # 2. 象限轉換模板
        quadrant_templates = {
            # 第一象限 (0° ≤ θ ≤ 90°)
            "first_quadrant": {
                "all": "$"  # 不需要轉換
            },
            # 第二象限 (90° < θ < 180°)
            "second_quadrant": {
                "sin": f" = {func_latex}(180^\\circ - {base_angle}^\\circ) = {func_latex}({first_quadrant_angle}^\\circ)$",
                "cos": f" = -{func_latex}(180^\\circ - {base_angle}^\\circ) = -{func_latex}({first_quadrant_angle}^\\circ)$",
                "tan": f" = -{func_latex}(180^\\circ - {base_angle}^\\circ) = -{func_latex}({first_quadrant_angle}^\\circ)$"
            },
            # 第三象限 (180° ≤ θ < 270°)
            "third_quadrant": {
                "sin": f" = -{func_latex}({base_angle}^\\circ - 180^\\circ) = -{func_latex}({first_quadrant_angle}^\\circ)$",
                "cos": f" = -{func_latex}({base_angle}^\\circ - 180^\\circ) = -{func_latex}({first_quadrant_angle}^\\circ)$",
                "tan": f" = {func_latex}({base_angle}^\\circ - 180^\\circ) = {func_latex}({first_quadrant_angle}^\\circ)$"
            },
            # 第四象限 (270° ≤ θ < 360°)
            "fourth_quadrant": {
                "sin": f" = -{func_latex}(360^\\circ - {base_angle}^\\circ) = -{func_latex}({first_quadrant_angle}^\\circ)$",
                "cos": f" = {func_latex}(360^\\circ - {base_angle}^\\circ) = {func_latex}({first_quadrant_angle}^\\circ)$",
                "tan": f" = -{func_latex}(360^\\circ - {base_angle}^\\circ) = -{func_latex}({first_quadrant_angle}^\\circ)$"
            },
            # 負角 (-90° < θ < 0°)
            "negative_angle": {
                "sin": f" = -{func_latex}(-{base_angle}^\\circ) = -{func_latex}({first_quadrant_angle}^\\circ)$",
                "cos": f" = {func_latex}(-{base_angle}^\\circ) = {func_latex}({first_quadrant_angle}^\\circ)$",
                "tan": f" = -{func_latex}(-{base_angle}^\\circ) = -{func_latex}({first_quadrant_angle}^\\circ)$"
            }
        }
        
        # 第一步：處理週期性
        if turns > 0:
            explanation = periodicity_templates["positive_turns"]
        elif turns < 0:
            explanation = periodicity_templates["negative_turns"]
        else:
            explanation = periodicity_templates["no_turns"]
        
        # 第二步：根據角度所在象限選擇適當的模板
        if 0 <= base_angle <= 90:  # 第一象限
            explanation += quadrant_templates["first_quadrant"]["all"]
        elif 90 < base_angle < 180:  # 第二象限
            explanation += quadrant_templates["second_quadrant"][func]
        elif 180 <= base_angle < 270:  # 第三象限
            explanation += quadrant_templates["third_quadrant"][func]
        elif 270 <= base_angle < 360:  # 第四象限
            explanation += quadrant_templates["fourth_quadrant"][func]
        elif -90 < base_angle < 0:  # 負角 -90° < θ < 0°
            explanation += quadrant_templates["negative_angle"][func]
        else:  # 其他角度 (包括 -180° < θ ≤ -90°)
            # 可以根據需要添加更多範圍的處理
            # 此處為簡化起見暫不處理
            explanation += "$"
        
        # 確保末尾有$符號關閉LaTeX
        if not explanation.endswith("$"):
            explanation += "$"
            
        return explanation
    
    def _generate_narrow_angle_explanation(self, func: str, original_angle: int, 
                                          first_quadrant_angle: int, first_sign: int, 
                                          new_func: str, narrow_angle: int, 
                                          new_sign: int, turns: int) -> str:
        """生成轉換為0~45度角的解析步驟。
        
        Args:
            func: 原始三角函數名稱。
            original_angle: 原始角度。
            first_quadrant_angle: 第一象限角度。
            first_sign: 第一階段符號 (1 或 -1)。
            new_func: 轉換後的三角函數名稱。
            narrow_angle: 轉換後的0~45度角度。
            new_sign: 最終符號 (1 或 -1)。
            turns: 完整轉動圈數。
            
        Returns:
            解析步驟的 LaTeX 格式文字。
        """
        # 先生成轉換為第一象限的解釋
        first_stage = self._generate_explanation(func, original_angle, first_quadrant_angle, first_sign, turns)
        
        # 如果角度已經在0~45度範圍內，就不需要再轉換
        if first_quadrant_angle <= 45:
            return first_stage
        
        # 移除末尾的$ (如果有)
        if first_stage.endswith("$"):
            first_stage = first_stage[:-1]
        
        # 添加轉換為0~45度的步驟
        func_latex = self.FUNC_LATEX[func]
        new_func_latex = self.FUNC_LATEX[new_func]
        sign_text = "-" if first_sign == -1 else ""
        
        if func == "sin":
            second_stage = f" = {sign_text}{func_latex}({first_quadrant_angle}^\\circ) = {sign_text}{func_latex}(90^\\circ - {narrow_angle}^\\circ) = {sign_text}{new_func_latex}({narrow_angle}^\\circ)$"
        elif func == "cos":
            second_stage = f" = {sign_text}{func_latex}({first_quadrant_angle}^\\circ) = {sign_text}{func_latex}(90^\\circ - {narrow_angle}^\\circ) = {sign_text}{new_func_latex}({narrow_angle}^\\circ)$"
        else:  # func == "tan"
            second_stage = f" = {sign_text}{func_latex}({first_quadrant_angle}^\\circ) = {sign_text}{func_latex}(90^\\circ - {narrow_angle}^\\circ) = {sign_text}{new_func_latex}({narrow_angle}^\\circ)$"
        
        return first_stage + second_stage
    
    def get_question_size(self) -> int:
        """獲取題目大小。"""
        return QuestionSize.WIDE
    
    def get_category(self) -> str:
        """獲取題目主類別。"""
        return "三角比"
    
    def get_subcategory(self) -> str:
        """獲取題目子類別。"""
        return "三角函數角度變換"