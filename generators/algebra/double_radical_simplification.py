#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 雙重根式化簡題目生成器

生成形如 √(c ± d√e) 的雙重根式化簡練習題目。
使用LaTeX模版化確保輸出格式標準，options.get()提供彈性配置。
"""

import math
import random
from typing import Dict, Any

import sympy as sp
from sympy import sqrt, expand, latex

from utils import global_config, get_logger
from ..base import QuestionGenerator, QuestionSize, register_generator

logger = get_logger(__name__)


@register_generator
class DoubleRadicalSimplificationGenerator(QuestionGenerator):
    """雙重根式化簡題目生成器

    生成形如 √(c ± d√e) 的雙重根式，要求學生將其化簡為 √a ± √b 的形式。

    Args:
        options (Dict[str, Any], optional): 生成器配置選項
            max_value (int): 根式內數值最大範圍，預設25
            max_attempts (int): 最大嘗試次數，預設100
            allow_addition (bool): 是否允許加法形式，預設True
            allow_subtraction (bool): 是否允許減法形式，預設True

    Returns:
        Dict[str, Any]: 包含完整題目資訊的字典
            question (str): 題目LaTeX字串
            answer (str): 答案LaTeX字串
            explanation (str): 解釋LaTeX字串
            size (int): 題目顯示大小
            difficulty (str): 難度等級
            category (str): 主類別
            subcategory (str): 子類別
            grade (str): 年級分類（G10S1格式）

    Example:
        >>> generator = DoubleRadicalSimplificationGenerator()
        >>> question = generator.generate_question()
        >>> print(question['question'])
        化簡：$\\sqrt{7 + 2\\sqrt{10}}$
        >>> print(question['grade'])
        G10S1
    """

    # LaTeX模版確保解釋步驟格式一致，結合優雅的有理無理分離
    # 過度複雜化修正：使用 a×b 顯示實際運算過程，避免預計算參數
    EXPLANATION_TEMPLATES = {
        "addition": [
            "$\\sqrt{{{ordered_latex}}}$",
            "$= \\sqrt{{{a}+{b} + 2\\sqrt{{{a} \\times {b}}}}}$",
            "$= \\sqrt{{(\\sqrt{{{a}}} + \\sqrt{{{b}}})^2}}$",
            "$= |\\sqrt{{{a}}} + \\sqrt{{{b}}}|$",
            "$= \\sqrt{{{a}}} + \\sqrt{{{b}}}$"
        ],
        "subtraction": [
            "$\\sqrt{{{ordered_latex}}}$",
            "$= \\sqrt{{{a}+{b} - 2\\sqrt{{{a} \\times {b}}}}}$",
            "$= \\sqrt{{(\\sqrt{{{a}}} - \\sqrt{{{b}}})^2}}$",
            "$= |\\sqrt{{{a}}} - \\sqrt{{{b}}}|$",
            "$= \\sqrt{{{a}}} - \\sqrt{{{b}}}$"
        ]
    }

    def __init__(self, options: Dict[str, Any] = None):
        """初始化雙重根式化簡題目生成器"""
        super().__init__(options)
        self.logger = get_logger(self.__class__.__name__)

        # 使用options.get()提供預設值，避免KeyError且比Pydantic驗證更簡潔
        options = options or {}
        self.max_value = options.get('max_value', 25)
        self.max_attempts = options.get('max_attempts', 100)
        self.allow_addition = options.get('allow_addition', True)
        self.allow_subtraction = options.get('allow_subtraction', True)

        # 確保至少有一種運算形式可用
        if not (self.allow_addition or self.allow_subtraction):
            self.logger.warning("至少需要允許一種運算形式，自動啟用加法")
            self.allow_addition = True

    def generate_question(self) -> Dict[str, Any]:
        """生成雙重根式題目

        使用異常處理確保生成穩定性，失敗時提供預設題目。
        """
        self.logger.info("開始生成雙重根式化簡題目")

        for attempt in range(self.max_attempts):
            try:
                result = self._generate_core_logic()
                if result and self._is_valid_result(result):
                    self.logger.info(f"生成成功（第 {attempt + 1} 次嘗試）")
                    return result
            except Exception as e:
                self.logger.warning(f"生成嘗試 {attempt + 1} 失敗: {str(e)}")
                continue

        # 當所有嘗試都失敗時，使用預設題目防止系統崩潰
        self.logger.warning("達到最大嘗試次數，使用預設題目")
        return self._get_fallback_question()

    def _generate_core_logic(self) -> Dict[str, Any]:
        """過度複雜化修正：核心數學邏輯生成，恢復舊版本的正確整體重試邏輯

        雙重根式化簡原理：
        給定答案形式 √a ± √b，透過平方展開得到題目形式
        (√a ± √b)² = a + b ± 2√(ab) = c ± d√e 形式的嵌套根式

        關鍵修復：恢復完整的協調式決策流程，確保：
        1. 數值選擇與運算類型的協調性
        2. 完全平方數檢查的完整重試機制
        3. 數學條件的正確性（如減法時 a ≥ b）

        過度複雜化修正重點：
        - 直接使用原始參數 a, b, is_addition 生成解釋
        - 移除不必要的反向參數提取邏輯
        - 保持數學正確性的同時簡化代碼結構
        """
        # 整體重試邏輯：所有條件必須協調滿足
        for attempt in range(self.max_attempts):
            try:
                # 步驟1: 隨機選擇基礎數值對
                # 使用 random.sample 確保 a ≠ b，避免退化情況
                values = list(range(1, self.max_value + 1))
                a, b = random.sample(values, 2)

                # 步驟2: 預防性大小調整，確保減法運算的數學正確性
                # 無論後續選擇加法還是減法，都能產生有效的正數結果
                if a < b:
                    a, b = b, a  # 確保 a ≥ b，使得 √a - √b ≥ 0

                # 步驟3: 運算類型的隨機決策
                # 根據用戶配置決定允許的運算類型
                operation_choices = []
                if self.allow_addition:
                    operation_choices.append(True)
                if self.allow_subtraction:
                    operation_choices.append(False)

                if not operation_choices:
                    # 安全機制：如果配置錯誤，默認允許加法
                    operation_choices = [True]

                is_addition = random.choice(operation_choices)

                # 步驟4: 教學價值驗證 - 完全平方數檢查
                # 如果 a*b 是完全平方數，則 2√(ab) 會簡化為整數
                # 導致題目失去雙重根式的教學意義，需要重新生成
                if self._is_perfect_square(a * b):
                    self.logger.debug(f"嘗試 {attempt + 1}: a={a}, b={b}, ab={a*b} 是完全平方數，重新生成")
                    continue  # 重新整個流程，不是部分重試

                # 步驟5: 生成數學正確的題目
                # 使用Sympy確保數學運算的精確性
                answer_expr = sqrt(a) + sqrt(b) if is_addition else sqrt(a) - sqrt(b)
                squared_expr = expand(answer_expr**2)

                # 使用優雅的有理無理分離生成格式一致的題目
                question = self._format_question_with_ordered_latex(squared_expr)

                # 過度複雜化修正：直接使用原始參數構造答案，避免Sympy排序問題
                answer = self._format_answer_with_original_params(a, b, is_addition)

                # 過度複雜化修正：直接使用原有參數 a, b, is_addition，無需反向提取
                explanation = self._build_explanation_with_original_params(squared_expr, answer_expr, a, b, is_addition)

                self.logger.info(f"生成成功（第 {attempt + 1} 次嘗試）: a={a}, b={b}, 運算={'加法' if is_addition else '減法'}")
                return {
                    **self._get_core_content(question, answer, explanation),
                    **self._get_standard_metadata()
                }

            except Exception as e:
                self.logger.warning(f"生成嘗試 {attempt + 1} 失敗: {str(e)}")
                continue

        # 如果所有嘗試都失敗，使用預設題目確保系統穩定性
        self.logger.warning("達到最大嘗試次數，使用預設題目")
        return self._get_fallback_question()





    def _format_question_with_ordered_latex(self, squared_expr) -> str:
        """使用as_coefficients_dict優雅地生成常數項在前的題目LaTeX

        這是核心突破方法：利用Sympy原生的有理無理分離能力，
        自動生成格式一致的題目，確保常數項始終在前。

        Args:
            squared_expr: Sympy展開的平方表達式

        Returns:
            str: 格式化的題目字串，形如 "化簡：$\sqrt{c + d\sqrt{e}}$"

        Example:
            輸入: 2*sqrt(14) + 9
            輸出: "化簡：$\sqrt{9 + 2\sqrt{14}}$"
        """
        # 使用Sympy原生方法分離有理部和無理部
        coeff_dict = squared_expr.as_coefficients_dict()

        # 提取有理部（常數項）
        rational_part = coeff_dict.get(1, 0)

        # 提取無理部項目
        irrational_terms = [(coeff, term) for term, coeff in coeff_dict.items() if term != 1]

        # 構造LaTeX片段：確保常數項在前
        latex_parts = []

        # 添加有理部（常數項）
        if rational_part != 0:
            latex_parts.append(str(int(rational_part)))

        # 添加無理部，處理符號和係數
        for coeff, term in irrational_terms:
            # 處理符號：正數時添加+號，負數時添加-號
            if coeff > 0 and latex_parts:
                latex_parts.append(' + ')
            elif coeff < 0:
                if latex_parts:
                    latex_parts.append(' - ')
                    coeff = abs(coeff)  # 負號已處理，係數取絕對值
                else:
                    latex_parts.append('-')
                    coeff = abs(coeff)

            # 添加係數（當係數不為1時）
            if coeff != 1:
                latex_parts.append(str(int(coeff)))

            # 添加根式部分，使用latex()確保格式正確
            latex_parts.append(latex(term))

        # 組合完整的題目字串
        inner_latex = ''.join(latex_parts)
        return f"化簡：$\\sqrt{{{inner_latex}}}$"

    def _build_explanation_with_original_params(self, squared_expr, answer_expr, a: int, b: int, is_addition: bool) -> str:
        """過度複雜化修正：直接使用原有參數，無需反向提取

        使用原始參數和模版生成解釋，避免複雜的反向解析。
        結合舊版本的直接參數使用和新版本的模版化優勢，
        既保持數學正確性又維持代碼的可維護性。

        Args:
            squared_expr: Sympy展開的平方表達式
            answer_expr: 最終答案表達式
            a: 第一個根式的被開方數
            b: 第二個根式的被開方數
            is_addition: 是否為加法形式

        Returns:
            str: 完整的解釋步驟LaTeX字串
        """
        # 過度複雜化修正：直接使用 as_coefficients_dict() 創建優雅的有序LaTeX
        ordered_latex = self._create_ordered_latex_from_expr(squared_expr)

        # 選擇對應的模版
        template_key = "addition" if is_addition else "subtraction"
        template_steps = self.EXPLANATION_TEMPLATES[template_key]

        # 過度複雜化修正：直接使用原始參數填充模版，移除預計算的 ab 參數
        params = {
            'ordered_latex': ordered_latex,
            'a': a,
            'b': b
        }

        formatted_steps = []
        for step in template_steps:
            formatted_step = step.format(**params)
            formatted_steps.append(formatted_step)

        return "\\\\[0.3em]".join(formatted_steps)

    def _create_ordered_latex_from_expr(self, squared_expr) -> str:
        """過度複雜化修正：直接從表達式創建有序LaTeX，避免字串處理

        使用 as_coefficients_dict() 優雅地生成常數項在前的LaTeX內容。
        相比複雜的字串替換，直接從Sympy表達式生成更可靠。

        Args:
            squared_expr: Sympy展開的平方表達式

        Returns:
            str: 有序的LaTeX內容（不含外層sqrt包裝）
        """
        # 使用Sympy原生方法分離有理部和無理部
        coeff_dict = squared_expr.as_coefficients_dict()

        # 提取有理部（常數項）
        rational_part = coeff_dict.get(1, 0)

        # 提取無理部項目
        irrational_terms = [(coeff, term) for term, coeff in coeff_dict.items() if term != 1]

        # 構造LaTeX片段：確保常數項在前
        latex_parts = []

        # 添加有理部（常數項）
        if rational_part != 0:
            latex_parts.append(str(int(rational_part)))

        # 添加無理部，處理符號和係數
        for coeff, term in irrational_terms:
            # 處理符號：正數時添加+號，負數時添加-號
            if coeff > 0 and latex_parts:
                latex_parts.append(' + ')
            elif coeff < 0:
                if latex_parts:
                    latex_parts.append(' - ')
                    coeff = abs(coeff)  # 負號已處理，係數取絕對值
                else:
                    latex_parts.append('-')
                    coeff = abs(coeff)

            # 添加係數（當係數不為1時）
            if coeff != 1:
                latex_parts.append(str(int(coeff)))

            # 添加根式部分，使用latex()確保格式正確
            latex_parts.append(latex(term))

        return ''.join(latex_parts)

    def _format_question_from_expr(self, question_expr) -> str:
        """從Sympy表達式生成題目字串

        使用Sympy表達式直接生成LaTeX格式，確保數學表達式的正確性。
        相比手動參數拼接，Sympy自動處理複雜嵌套根式的LaTeX輸出。

        Args:
            question_expr: Sympy表達式物件（通常是sqrt(展開結果)）

        Returns:
            str: LaTeX格式的題目字串

        Example:
            >>> expr = sqrt(7 + 2*sqrt(10))
            >>> _format_question_from_expr(expr)
            "化簡：$\\sqrt{7 + 2\\sqrt{10}}$"
        """
        return f"化簡：${latex(question_expr)}$"

    def _format_answer_with_original_params(self, a: int, b: int, is_addition: bool) -> str:
        """過度複雜化修正：直接使用原始參數構造答案，避免Sympy排序問題

        基於數學教學習慣，確保答案格式為 √a ± √b (a ≥ b)。
        避免Sympy自動簡化和重排序導致的格式問題。

        Args:
            a: 第一個根式的被開方數 (較大值)
            b: 第二個根式的被開方數 (較小值)
            is_addition: 是否為加法形式

        Returns:
            str: 標準格式的LaTeX答案字串

        Example:
            >>> _format_answer_with_original_params(19, 4, False)
            "$\\sqrt{19} - 2$"
        """
        # 格式化各根式項，處理完全平方數化簡
        sqrt_a = self._format_sqrt_term(a)
        sqrt_b = self._format_sqrt_term(b)

        if is_addition:
            return f"${sqrt_a} + {sqrt_b}$"
        else:
            return f"${sqrt_a} - {sqrt_b}$"

    def _format_sqrt_term(self, n: int) -> str:
        """格式化單個根式項，處理完全平方數化簡

        根據數學教學習慣：
        - 完全平方數直接顯示簡化結果 (√4 → 2)
        - 非完全平方數顯示根式 (√19 → √19)
        - 根式需要化簡 (√12 → 2√3)

        Args:
            n: 被開方數

        Returns:
            str: LaTeX格式的根式或簡化後的表達式
        """
        if self._is_perfect_square(n):
            # 完全平方數直接顯示簡化結果
            return str(int(math.sqrt(n)))
        else:
            # 非完全平方數顯示根式，並進行化簡
            return self._simplify_sqrt_term(n)

    def _simplify_sqrt_term(self, n: int) -> str:
        """化簡根式項 (如 √12 → 2√3)

        提取完全平方因子，按照數學教學標準格式化。

        Args:
            n: 被開方數

        Returns:
            str: 化簡後的LaTeX根式
        """
        # 找出最大的完全平方因子
        factor = 1
        remaining = n

        i = 2
        while i * i <= remaining:
            while remaining % (i * i) == 0:
                factor *= i
                remaining //= (i * i)
            i += 1

        if factor == 1:
            # 無法化簡
            return f"\\sqrt{{{n}}}"
        else:
            # 可以化簡：factor√remaining
            return f"{factor}\\sqrt{{{remaining}}}"

    def _is_valid_result(self, result: Dict[str, Any]) -> bool:
        """驗證結果有效性

        檢查生成的題目是否包含必要欄位且內容非空。

        Args:
            result (Dict[str, Any]): 生成的題目結果

        Returns:
            bool: 結果是否有效
        """
        required_keys = ['question', 'answer', 'explanation']
        return all(key in result and result[key] for key in required_keys)

    def _is_perfect_square(self, n: int) -> bool:
        """檢查完全平方數

        判斷給定數字是否為完全平方數，用於避免生成過簡單的題目。

        Args:
            n (int): 要檢查的數字

        Returns:
            bool: 是否為完全平方數
        """
        # 排除非正數，避免計算錯誤
        if n <= 0:
            return False
        sqrt_n = int(math.sqrt(n))
        return sqrt_n * sqrt_n == n

    def _get_core_content(self, question: str, answer: str, explanation: str) -> Dict[str, str]:
        """獲取核心內容

        將題目、答案、解釋組成字典，分離核心內容與元數據處理邏輯。

        Args:
            question (str): 題目LaTeX字串
            answer (str): 答案LaTeX字串
            explanation (str): 解釋LaTeX字串

        Returns:
            Dict[str, str]: 包含核心內容的字典
        """
        return {
            "question": question,
            "answer": answer,
            "explanation": explanation
        }

    def _get_standard_metadata(self) -> Dict[str, Any]:
        """獲取標準元數據

        提供PDF生成所需的完整元數據，包括尺寸、難度、分類等資訊。

        Returns:
            Dict[str, Any]: 包含標準元數據的字典
        """
        return {
            "size": QuestionSize.WIDE.value,  # 雙重根式較複雜，需要寬版面顯示
            "difficulty": "MEDIUM",
            "category": self.get_category(),
            "subcategory": self.get_subcategory(),
            "grade": "G10S1",  # 年級分類：十年級上學期（高中代數）
            # 預留圖形相關欄位，確保PDF兼容
            "figure_data_question": None,
            "figure_data_explanation": None,
            "figure_position": "right",
            "explanation_figure_position": "right"
        }

    def _get_fallback_question(self) -> Dict[str, Any]:
        """獲取預設題目

        當動態生成失敗時，提供固定的有效題目作為安全機制。
        使用Sympy確保預設題目的數學正確性。

        Returns:
            Dict[str, Any]: 預設題目的完整資訊
        """
        # 過度複雜化修正：直接使用簡單的預設參數
        a, b = 9, 5  # 對應 √9 - √5 = 3 - √5
        is_addition = False

        # 使用Sympy展開得到題目表達式
        answer_expr = sqrt(a) - sqrt(b)
        squared_expr = expand(answer_expr**2)  # 9 + 5 - 6*sqrt(5) = 14 - 6*sqrt(5)

        return {
            "question": self._format_question_with_ordered_latex(squared_expr),
            "answer": self._format_answer_with_original_params(a, b, is_addition),
            "explanation": self._build_explanation_with_original_params(squared_expr, answer_expr, a, b, is_addition),
            **self._get_standard_metadata()
        }

    # 以下方法實現標準介面，確保與PDF生成系統兼容
    def get_question_size(self) -> int:
        """獲取題目顯示大小"""
        return QuestionSize.WIDE.value

    def get_category(self) -> str:
        """獲取題目主類別"""
        return "數與式"

    def get_subcategory(self) -> str:
        """獲取題目子類別

        Returns:
            str: 子類別名稱
        """
        return "重根號練習"