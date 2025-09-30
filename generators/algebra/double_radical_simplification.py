#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 雙重根式化簡題目生成器

生成形如 √(c ± d√e) 的雙重根式化簡練習題目。
使用LaTeX模版化確保輸出格式標準，options.get()提供彈性配置。
"""

import math
import random
from typing import Dict, Any, Optional

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

    # LaTeX模版確保解釋步驟格式一致
    # 使用 a×b 顯示實際運算過程，避免預計算參數
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

        # 配置處理
        options = options or {}
        self.max_value = options.get('max_value', 25)

        # 建立有效數值組合，避免生成過程中的重複計算
        self._build_valid_combinations()

    def _build_valid_combinations(self):
        """建立所有有效的數值組合

        預先篩選出所有數學上有效的 (a,b) 組合，避免生成時重複檢查。
        過濾條件：a*b 不能是完全平方數，否則失去雙重根式教學價值。
        """
        from itertools import combinations

        self.valid_pairs = [
            (max(a, b), min(a, b))  # 確保 a >= b，使減法結果為正
            for a, b in combinations(range(1, self.max_value + 1), 2)
            if not self._is_perfect_square(a * b)
        ]

        if not self.valid_pairs:
            raise ValueError(f"在範圍1-{self.max_value}內找不到有效組合")

        self.logger.info(f"建立有效組合 {len(self.valid_pairs)} 個（範圍1-{self.max_value}）")

    def generate_question(self) -> Dict[str, Any]:
        """生成雙重根式題目

        使用預篩選組合確保一次成功生成，失敗時提供預設題目。
        """
        self.logger.info("開始生成雙重根式化簡題目")

        try:
            # 從預篩選列表隨機選擇有效組合
            a, b = random.choice(self.valid_pairs)

            # 隨機決定加減法，兩種形式教學價值相同
            is_addition = random.choice([True, False])

            # 確定性生成，無需重試
            result = self._generate_with_params(a, b, is_addition)

            operation_type = "加法" if is_addition else "減法"
            self.logger.info(f"生成成功: a={a}, b={b}, 運算={operation_type}")
            return result

        except Exception as e:
            self.logger.error(f"生成失敗: {str(e)}")
            return self._get_fallback_question()

    def _generate_with_params(self, a: int, b: int, is_addition: bool) -> Dict[str, Any]:
        """使用給定參數生成題目

        直接使用預篩選的有效參數生成題目，確保數學正確性。

        Args:
            a: 第一個根式的被開方數（較大值）
            b: 第二個根式的被開方數（較小值）
            is_addition: 是否為加法形式

        Returns:
            Dict[str, Any]: 完整的題目資訊
        """
        # 使用 Sympy 確保數學運算精確性
        answer_expr = sqrt(a) + sqrt(b) if is_addition else sqrt(a) - sqrt(b)
        squared_expr = expand(answer_expr**2)

        # 生成各部分內容
        question = self._format_question_with_ordered_latex(squared_expr)
        answer = self._format_answer_with_original_params(a, b, is_addition)
        explanation = self._build_explanation_with_original_params(
            squared_expr, answer_expr, a, b, is_addition)

        return {
            **self._get_core_content(question, answer, explanation),
            **self._get_standard_metadata()
        }

    def _format_question_with_ordered_latex(self, squared_expr) -> str:
        """生成完整題目字串，包含題目前綴和外層根號包裝

        職責：將Sympy表達式轉換為完整的題目LaTeX格式
        用途：題目生成階段使用，輸出給學生的完整題目文字

        Args:
            squared_expr: Sympy展開的平方表達式

        Returns:
            str: 完整題目字串，形如 "化簡：$\sqrt{c + d\sqrt{e}}$"

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
        """使用原有參數生成解釋步驟

        使用原始參數和模版生成解釋，避免複雜的反向解析。
        直接參數使用結合模版化，保持數學正確性和代碼可維護性。

        Args:
            squared_expr: Sympy展開的平方表達式
            answer_expr: 最終答案表達式
            a: 第一個根式的被開方數
            b: 第二個根式的被開方數
            is_addition: 是否為加法形式

        Returns:
            str: 完整的解釋步驟LaTeX字串
        """
        # 取得純LaTeX內容用於模板填充（不含外層包裝）
        ordered_latex = self._create_ordered_latex_from_expr(squared_expr)

        # 選擇對應的模版
        template_key = "addition" if is_addition else "subtraction"
        template_steps = self.EXPLANATION_TEMPLATES[template_key]

        # 使用原始參數填充模版
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
        """生成純LaTeX內容，不含包裝格式

        職責：提取Sympy表達式的LaTeX內容部分，用於模板變數填充
        用途：解釋步驟中的模板參數，需要不含外層包裝的純內容

        使用as_coefficients_dict()確保常數項在前的標準順序

        Args:
            squared_expr: Sympy展開的平方表達式

        Returns:
            str: 純LaTeX內容，形如 "9 + 2\sqrt{14}"（不含外層sqrt包裝）
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

    def _format_answer_with_original_params(self, a: int, b: int, is_addition: bool) -> str:
        """使用原始參數構造答案，避免Sympy排序問題

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

    def get_grade(self) -> str:
        """獲取適用年級"""
        return "G10S1"  # 年級分類：十年級上學期（高中代數）

    def _get_fallback_question(self) -> Dict[str, Any]:
        """獲取預設題目

        當動態生成失敗時，提供固定的有效題目作為安全機制。
        使用Sympy確保預設題目的數學正確性。

        Returns:
            Dict[str, Any]: 預設題目的完整資訊
        """
        # 使用簡單的預設參數
        a, b = 9, 5  # 對應 √9 - √5 = 3 - √5
        is_addition = False

        # 使用Sympy展開得到題目表達式
        answer_expr = sqrt(a) - sqrt(b)
        squared_expr = expand(answer_expr**2)  # 9 + 5 - 6*sqrt(5) = 14 - 6*sqrt(5)

        return {
            "question": self._format_question_with_ordered_latex(squared_expr),  # 完整題目字串
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

    def get_subject(self) -> str:
        """獲取科目，數學測驗生成器標準實作"""
        return "數學"

    def get_difficulty(self) -> str:
        """獲取難度等級，雙重根式化簡為中等難度"""
        return "MEDIUM"

    def get_figure_data_question(self) -> Optional[Dict[str, Any]]:
        """獲取題目圖形數據，代數題目通常無需圖形輔助"""
        return None

    def get_figure_data_explanation(self) -> Optional[Dict[str, Any]]:
        """獲取解釋圖形數據，代數題目通常無需圖形輔助"""
        return None

    def get_figure_position(self) -> str:
        """獲取題目圖形位置，標準配置為右側"""
        return "right"

    def get_explanation_figure_position(self) -> str:
        """獲取解釋圖形位置，標準配置為右側"""
        return "right"

    @classmethod
    def get_config_schema(cls) -> Dict[str, Dict[str, Any]]:
        """取得雙重根式生成器配置描述，供UI動態生成配置介面

        定義用戶可調整的配置選項，UI系統將自動生成對應控件。
        主要提供數值範圍控制，讓教師可根據學生程度調整題目難度。

        Returns:
            Dict[str, Dict[str, Any]]: 配置選項描述字典

        Example:
            >>> schema = DoubleRadicalSimplificationGenerator.get_config_schema()
            >>> schema['max_value']['type']
            'number_input'
            >>> schema['max_value']['default']
            25

        Note:
            配置選項說明：
            - max_value: 控制根式內數值的最大範圍，影響題目的數值複雜度
              較小值(10-15)適合初學者，較大值(25-50)適合進階練習
        """
        return {
            "max_value": {
                "type": "number_input",
                "label": "數值上限",
                "default": 25,
                "min": 5,
                "max": 100,
                "description": "控制生成答案數字的最大值"
            }
        }