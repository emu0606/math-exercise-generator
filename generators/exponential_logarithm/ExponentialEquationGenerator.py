#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""指數方程式生成器

統一的指數方程式題目生成器，整合三種題型：
- 題型一：同底數轉換（基礎）- 通過同底數比較指數求解
- 題型二：單底數代換（進階）- 二次因式分解
- 題型三：多底數分組（高階）- 分組因式分解

新架構整合特點：
- 自動註冊機制：使用@register_generator自動註冊到系統
- 動態配置支援：整合percentage_group控件，支援題型比例調整
- 統一元數據：採用_get_standard_metadata()標準格式
- 完整錯誤處理：現代化的異常處理和日誌記錄
"""

import random
from typing import Dict, Any, List, Tuple, Optional
from fractions import Fraction
from dataclasses import dataclass

from utils import get_logger
from generators.base import QuestionGenerator, QuestionSize, register_generator


@dataclass
class Factor:
    """指數因式數據結構

    表示形如 (base^var - target) 或 (base^var + target) 的因式。

    Attributes:
        base (int): 底數（如 2, 3, 5）
        var (str): 變數名（通常為 'x'）
        target (Fraction): 目標值 k
            - target > 0: 有實數解因式 (base^var - target)
            - target < 0: 無實數解因式 (base^var + |target|)

    Example:
        >>> f1 = Factor(base=2, var='x', target=Fraction(8))  # 2^x - 8
        >>> f1.has_real_solution()
        True
        >>> f1.solution()
        Fraction(3, 1)
    """
    base: int
    var: str
    target: Fraction

    def has_real_solution(self) -> bool:
        """判斷因式是否有實數解

        Returns:
            bool: target > 0 時有實數解
        """
        return self.target > 0

    def solution(self) -> Optional[Fraction]:
        """計算因式的實數解

        求解 base^x = target，得到 x = log_base(target)

        Returns:
            Optional[Fraction]: 實數解（若存在），否則為 None

        Mathematics:
            利用對數性質計算：
            - 2^x = 8 → x = 3 (因為 8 = 2^3)
            - 3^x = 1/9 → x = -2 (因為 1/9 = 3^(-2))
        """
        if not self.has_real_solution():
            return None

        # 計算 log_base(target)
        # 使用試探法找到精確的有理數解
        target_val = self.target

        # 處理 target = 1 的特殊情況
        if target_val == 1:
            return Fraction(0)

        # 正指數試探（target > 1）
        if target_val > 1:
            power = 1
            current = self.base
            while current <= target_val and power <= 10:
                if current == target_val:
                    return Fraction(power)
                current *= self.base
                power += 1

        # 負指數試探（target < 1）
        else:
            power = -1
            current = Fraction(1, self.base)
            while current >= target_val and power >= -10:
                if current == target_val:
                    return Fraction(power)
                current *= Fraction(1, self.base)
                power -= 1

        # 處理分數指數（如 2^(1/2) = sqrt(2)）
        # 簡化版本：只處理常見情況
        return None


@register_generator
class ExponentialEquationGenerator(QuestionGenerator):
    """指數方程式生成器

    生成三種類型的指數方程式題目，採用統一的因式框架，
    整合動態配置UI系統支援。

    Args:
        options (Dict[str, Any], optional): 生成器配置選項
            type_weights (Dict[str, int]): 題型權重配置
                type1: 同底數轉換權重，預設40
                type2: 單底數代換權重，預設30
                type3: 多底數分組權重，預設30

    Returns:
        Dict[str, Any]: 包含完整題目資訊的字典
            question (str): 題目LaTeX字串
            answer (str): 答案LaTeX字串
            explanation (str): 詳細解析LaTeX字串
            size (int): 題目顯示大小
            difficulty (str): 難度等級
            category (str): 主類別（指數與對數）
            subcategory (str): 子類別（基礎指數方程式）
            grade (str): 年級分類（G11S1 = 高二上學期）

    Example:
        >>> generator = ExponentialEquationGenerator()
        >>> question = generator.generate_question()
        >>> print(question['question'])
        求解方程式：$9^{x+2} = \\left(\\frac{1}{3}\\right)^{2x+8}$
        >>> print(question['answer'])
        $x = -3$
    """

    # 常用底數
    COMMON_BASES = [2, 3, 5]

    def __init__(self, options: Dict[str, Any] = None):
        """初始化指數方程式生成器

        採用簡潔的配置處理方式，整合動態配置UI支援。

        Args:
            options (Dict[str, Any], optional): 生成器配置選項
        """
        super().__init__(options)
        self.logger = get_logger(self.__class__.__name__)
        options = options or {}

        # percentage_group控件在UI層已驗證總和=100%，此處直接使用配置值
        type_config = options.get("type_weights", {})
        if type_config:
            self.type_weights = [
                type_config.get("type1", 40),
                type_config.get("type2", 30),
                type_config.get("type3", 30)
            ]
            self.logger.info(f"使用自定義題型權重: {self.type_weights}")
        else:
            # 無配置時使用預設值
            self.type_weights = [40, 30, 30]

        self.logger.info("指數方程式生成器初始化完成")

    @classmethod
    def get_config_schema(cls):
        """提供動態配置UI描述

        定義percentage_group控件，支援教師調整題型比例。

        Returns:
            Dict[str, Any]: 配置選項描述字典
        """
        return {
            "type_weights": {
                "type": "percentage_group",
                "label": "題型比例分配",
                "description": "調整三種題型的出現頻率，總和自動保持為100%",
                "items": {
                    "type1": {
                        "label": "同底數轉換",
                        "default": 40
                    },
                    "type2": {
                        "label": "單底數代換",
                        "default": 30
                    },
                    "type3": {
                        "label": "多底數分組",
                        "default": 30
                    }
                }
            }
        }

    def _generate_core_question(self) -> Dict[str, Any]:
        """核心指數方程式題目生成邏輯

        使用權重選擇題型，三種題型都有完善的生成邏輯。

        Returns:
            Dict[str, Any]: 包含完整題目資訊的字典
        """
        # 使用配置的權重選擇題型
        question_type = random.choices(
            ["type1", "type2", "type3"],
            weights=self.type_weights
        )[0]

        # 根據題型調用對應方法
        if question_type == "type1":
            return self._generate_type1()
        elif question_type == "type2":
            return self._generate_type2()
        else:  # type3
            return self._generate_type3()

    def _generate_type1(self) -> Dict[str, Any]:
        """生成題型一：同底數轉換題（包含基本型和鏈式型）

        以30%機率選擇鏈式型，70%機率選擇基本型。

        Returns:
            Dict[str, Any]: 題型一題目字典
        """
        # 30% 機率選擇鏈式求解，70% 機率選擇基本型
        use_chain = random.random() < 0.3

        if use_chain:
            return self._generate_type1_chain()
        else:
            return self._generate_type1_basic()

    def _generate_type1_basic(self) -> Dict[str, Any]:
        """生成題型一基本型：同底數轉換題

        生成形如 a^(mx+p) = b^(nx+q) 的方程式，其中 a, b 可化為同底數。

        Returns:
            Dict[str, Any]: 題型一基本題目字典

        Example:
            9^(x+2) = (1/3)^(2x+8)
            → (3^2)^(x+2) = (3^(-1))^(2x+8)
            → 3^(2x+4) = 3^(-2x-8)
            → 2x+4 = -2x-8
            → x = -3
        """
        # 選擇共同底數
        common_base = random.choice(self.COMMON_BASES)

        # 選擇指數偏移（p, q 分別為 a, b 的指數偏移）
        p = random.choice([2, -1, 3])  # a = common_base^p
        q = random.choice([1, -1, -2])  # b = common_base^q

        # 確保 p != q（避免平凡情況）
        while p == q:
            q = random.choice([1, -1, -2, 2])

        # 計算實際底數
        if p > 0:
            base_a = common_base ** p
        else:
            base_a = Fraction(1, common_base ** abs(p))

        if q > 0:
            base_b = common_base ** q
        else:
            base_b = Fraction(1, common_base ** abs(q))

        # 選擇指數係數和常數項（左邊：m1*x + c1，右邊：m2*x + c2）
        m1 = random.choice([1, 2])
        m2 = random.choice([1, 2, 3])

        # 預先決定解 x_solution
        x_solution = random.choice([-3, -2, -1, 1, 2])

        # 根據解反推常數項，使得 p*(m1*x + c1) = q*(m2*x + c2)
        # p*m1*x + p*c1 = q*m2*x + q*c2
        # p*c1 - q*c2 = q*m2*x - p*m1*x = x*(q*m2 - p*m1)
        # c1 = (q*c2 + x*(q*m2 - p*m1)) / p

        c2 = random.choice([2, 4, 6, 8])
        c1_numerator = q * c2 + x_solution * (q * m2 - p * m1)

        # 確保 c1 是整數
        if c1_numerator % p != 0:
            c2 = c2 + (p - c1_numerator % p)
            c1_numerator = q * c2 + x_solution * (q * m2 - p * m1)

        c1 = c1_numerator // p

        # 構建題目字串
        left_exp = self._format_linear_expr(m1, c1, 'x')
        right_exp = self._format_linear_expr(m2, c2, 'x')

        # 格式化底數（分數需要用 \frac）
        if isinstance(base_a, Fraction) and base_a.denominator != 1:
            left_base = f"\\left(\\frac{{{base_a.numerator}}}{{{base_a.denominator}}}\\right)"
        else:
            left_base = str(int(base_a) if isinstance(base_a, int) else base_a.numerator)

        if isinstance(base_b, Fraction) and base_b.denominator != 1:
            right_base = f"\\left(\\frac{{{base_b.numerator}}}{{{base_b.denominator}}}\\right)"
        else:
            right_base = str(int(base_b) if isinstance(base_b, int) else base_b.numerator)

        question_text = f"求解方程式：${left_base}^{{{left_exp}}} = {right_base}^{{{right_exp}}}$"
        answer_text = f"$x = {x_solution}$"

        # 生成詳解
        explanation = self._generate_type1_explanation(
            common_base, p, q, m1, c1, m2, c2, x_solution
        )

        return {
            "question": question_text,
            "answer": answer_text,
            "explanation": explanation,
            "figure_data_question": None,
            "figure_data_explanation": None,
            **self._get_standard_metadata()
        }

    def _generate_type1_chain(self) -> Dict[str, Any]:
        """生成題型一鏈式求解題

        關係一：base1^x = value （保證 x 為簡單整數）
        關係二：base2^y = base3^x （需要代入 x 求 y）

        Returns:
            Dict[str, Any]: 題型一鏈式題目字典

        Example:
            已知 2^x = 8，求 81^y = 27^x 中的 y 值。
            → x = 3
            → 81^y = 27^3
            → (3^4)^y = (3^3)^3
            → 4y = 9
            → y = 9/4
        """
        # Step 1: 生成關係一（保證 x 為簡單整數）
        base1 = random.choice(self.COMMON_BASES)
        x_solution = random.choice([1, 2, 3])
        value = base1 ** x_solution

        # Step 2: 生成關係二
        # 選擇不同的底數（避免太簡單）
        available_bases = [b for b in self.COMMON_BASES if b != base1]
        common_base_2 = random.choice(available_bases)

        # 選擇指數偏移
        p = random.choice([2, 3, 4])  # left_base = common_base_2^p
        q = random.choice([2, 3, 4])  # right_base = common_base_2^q

        # 確保 p != q（避免平凡情況）
        while p == q:
            q = random.choice([2, 3, 4])

        left_base_2 = common_base_2 ** p
        right_base_2 = common_base_2 ** q

        # Step 3: 計算 y 的解
        # (common_base_2^p)^y = (common_base_2^q)^x
        # p*y = q*x
        # y = q*x / p
        y_solution = Fraction(q * x_solution, p)

        # Step 4: 構建題目
        relation1 = f"{base1}^x = {value}"
        relation2 = f"{left_base_2}^y = {right_base_2}^x"

        question_text = f"已知 ${relation1}$，求 ${relation2}$ 中的 $y$ 值。"
        answer_text = f"$x = {x_solution}, y = {self._format_fraction(y_solution)}$"

        # Step 5: 生成詳解
        explanation = self._generate_type1_chain_explanation(
            base1, value, x_solution,
            left_base_2, right_base_2, common_base_2, p, q, y_solution
        )

        return {
            "question": question_text,
            "answer": answer_text,
            "explanation": explanation,
            "figure_data_question": None,
            "figure_data_explanation": None,
            **self._get_standard_metadata()
        }

    def _generate_type2(self) -> Dict[str, Any]:
        """生成題型二：單底數代換題

        生成需要代換求解的單底數指數方程式。

        Returns:
            Dict[str, Any]: 題型二題目字典

        Example:
            4^x - 5·2^(x+1) + 16 = 0
            → 令 y = 2^x
            → y^2 - 10y + 16 = 0
            → (y-2)(y-8) = 0
            → x = 1 或 x = 3
        """
        # 選擇底數
        base = random.choice(self.COMMON_BASES)

        # 選擇兩個因式
        # 因式1: base^x - k1 = 0 → base^x = k1 → x = log_base(k1)
        # 因式2: base^x - k2 = 0 或 base^x + k2 = 0

        # 選擇 k1（確保有簡單的對數解）
        exp1 = random.choice([1, 2, 3])
        k1 = Fraction(base ** exp1)

        # 選擇 k2（可能有解或無解）
        has_second_solution = random.choice([True, False])

        if has_second_solution:
            exp2 = random.choice([0, 1, 2])
            k2 = Fraction(base ** exp2)
            # 確保 k1 != k2
            while k1 == k2:
                exp2 = random.choice([0, 1, 2, 3])
                k2 = Fraction(base ** exp2)
        else:
            # 無解因式：base^x + k2 = 0
            k2 = -Fraction(random.choice([1, 2, 4, 8]))

        factor1 = Factor(base=base, var='x', target=k1)
        factor2 = Factor(base=base, var='x', target=k2)

        # 展開 (base^x - k1)(base^x - k2)
        # 令 y = base^x，得 (y - k1)(y - k2) = y^2 - (k1+k2)y + k1*k2

        coeff_y2 = 1
        coeff_y1 = -(k1 + k2)
        coeff_y0 = k1 * k2

        # 應用隱藏變形（SINGLE_BASE）- 四種變化類型
        # none: base^(2x) + a·base^x + b = 0
        # base: (base^2)^x + a·base^x + b = 0
        # exp:  base^(2x) + a·base^(x+1) + b = 0
        # both: (base^2)^x + a·base^(x+1) + b = 0

        # 進階版機率分配：30% 基本，25% 底數，25% 指數，20% 兩者
        hiding_type = random.choices(
            ['none', 'base', 'exp', 'both'],
            weights=[0.30, 0.25, 0.25, 0.20]
        )[0]

        # 應用隱藏變形（含降級回退機制）
        question_latex = self._apply_type2_hiding(base, coeff_y1, coeff_y0, hiding_type)

        # 計算解並建立 solution → target 映射
        solutions = []
        solution_to_target = {}  # 映射：解 → 目標值

        if factor1.has_real_solution():
            sol1 = factor1.solution()
            if sol1 is not None:
                solutions.append(sol1)
                solution_to_target[sol1] = k1

        if factor2.has_real_solution():
            sol2 = factor2.solution()
            if sol2 is not None:
                solutions.append(sol2)
                solution_to_target[sol2] = k2

        # 格式化答案
        if len(solutions) == 1:
            answer_text = f"$x = {self._format_fraction(solutions[0])}$"
        elif len(solutions) == 2:
            answer_text = f"$x = {self._format_fraction(solutions[0])}$ 或 $x = {self._format_fraction(solutions[1])}$"
        else:
            answer_text = "$無實數解$"

        question_text = f"求解方程式：${question_latex}$"

        # 生成詳解（傳遞映射關係）
        explanation = self._generate_type2_explanation(
            base, coeff_y1, coeff_y0, k1, k2, solutions, solution_to_target
        )

        return {
            "question": question_text,
            "answer": answer_text,
            "explanation": explanation,
            "figure_data_question": None,
            "figure_data_explanation": None,
            **self._get_standard_metadata()
        }

    def _generate_type3(self) -> Dict[str, Any]:
        """生成題型三：多底數分組題

        生成需要分組因式分解的多底數指數方程式。

        Returns:
            Dict[str, Any]: 題型三題目字典

        Example:
            10^x - 4·5^x - 5·2^x + 20 = 0
            → (10^x - 4·5^x) - (5·2^x - 20) = 0
            → 5^x(2^x - 4) - 5(2^x - 4) = 0
            → (5^x - 5)(2^x - 4) = 0
            → x = 1 或 x = 2
        """
        # 選擇兩個不同的底數
        base1 = random.choice(self.COMMON_BASES)
        base2 = random.choice([b for b in self.COMMON_BASES if b != base1])

        # 選擇目標值（確保有簡單解）
        exp1 = random.choice([1, 2])
        k1 = Fraction(base1 ** exp1)

        exp2 = random.choice([1, 2])
        k2 = Fraction(base2 ** exp2)

        factor1 = Factor(base=base1, var='x', target=k1)
        factor2 = Factor(base=base2, var='x', target=k2)

        # 展開 (base1^x - k1)(base2^x - k2)
        # = base1^x · base2^x - k2·base1^x - k1·base2^x + k1·k2
        # = (base1·base2)^x - k2·base1^x - k1·base2^x + k1·k2

        mixed_base = base1 * base2
        coeff_mixed = 1
        coeff_base1 = -k2
        coeff_base2 = -k1
        constant = k1 * k2

        # 構建方程式字串
        terms = []

        # 項1: (base1·base2)^x
        terms.append(f"{mixed_base}^x")

        # 項2: -k2·base1^x
        if coeff_base1 < 0:
            terms.append(f"- {self._format_fraction(abs(coeff_base1))} \\cdot {base1}^x")
        else:
            terms.append(f"+ {self._format_fraction(coeff_base1)} \\cdot {base1}^x")

        # 項3: -k1·base2^x
        if coeff_base2 < 0:
            terms.append(f"- {self._format_fraction(abs(coeff_base2))} \\cdot {base2}^x")
        else:
            terms.append(f"+ {self._format_fraction(coeff_base2)} \\cdot {base2}^x")

        # 項4: 常數
        if constant > 0:
            terms.append(f"+ {self._format_fraction(constant)}")
        else:
            terms.append(f"- {self._format_fraction(abs(constant))}")

        equation_latex = " ".join(terms) + " = 0"
        question_text = f"求解方程式：${equation_latex}$"

        # 計算解並建立映射
        solution_to_base_target = {}  # 映射：解 → (底數, 目標值)

        solutions = []
        if factor1.has_real_solution():
            sol1 = factor1.solution()
            if sol1 is not None:
                solutions.append(sol1)
                solution_to_base_target[sol1] = (base1, k1)

        if factor2.has_real_solution():
            sol2 = factor2.solution()
            if sol2 is not None:
                solutions.append(sol2)
                solution_to_base_target[sol2] = (base2, k2)

        # 去重並排序（兩個因式可能產生相同的解）
        solutions = list(set(solutions))
        solutions.sort()

        # 格式化答案
        if len(solutions) == 2:
            answer_text = f"$x = {self._format_fraction(solutions[0])}$ 或 $x = {self._format_fraction(solutions[1])}$"
        elif len(solutions) == 1:
            answer_text = f"$x = {self._format_fraction(solutions[0])}$"
        else:
            answer_text = "$無實數解$"

        # 生成詳解（傳遞映射關係）
        explanation = self._generate_type3_explanation(
            base1, base2, k1, k2, mixed_base, solutions, solution_to_base_target
        )

        return {
            "question": question_text,
            "answer": answer_text,
            "explanation": explanation,
            "figure_data_question": None,
            "figure_data_explanation": None,
            **self._get_standard_metadata()
        }

    # ==================== 輔助方法 ====================

    def _format_linear_expr(self, m: int, c: int, var: str) -> str:
        """格式化線性表達式 mx + c

        Args:
            m (int): 係數
            c (int): 常數項
            var (str): 變數名

        Returns:
            str: 格式化的表達式

        Example:
            _format_linear_expr(2, 3, 'x') → '2x+3'
            _format_linear_expr(1, -2, 'x') → 'x-2'
        """
        # 係數部分
        if m == 1:
            expr = var
        elif m == -1:
            expr = f"-{var}"
        else:
            expr = f"{m}{var}"

        # 常數項部分
        if c > 0:
            expr += f"+{c}"
        elif c < 0:
            expr += f"{c}"  # 負號已包含

        return expr

    def _format_fraction(self, frac: Fraction) -> str:
        """格式化分數為LaTeX

        Args:
            frac (Fraction): 分數

        Returns:
            str: LaTeX格式的分數
        """
        if frac.denominator == 1:
            return str(frac.numerator)
        else:
            return f"\\frac{{{frac.numerator}}}{{{frac.denominator}}}"

    def _format_type2_equation_basic(self, base: int, coeff_y2: int,
                                     coeff_y1: Fraction, coeff_y0: Fraction) -> str:
        """格式化題型二的基本方程式

        格式：base^(2x) + a·base^x + b = 0

        Args:
            base (int): 底數
            coeff_y2 (int): y^2 係數
            coeff_y1 (Fraction): y 係數
            coeff_y0 (Fraction): 常數項

        Returns:
            str: LaTeX格式的方程式
        """
        terms = []

        # base^(2x) 項
        terms.append(f"{base}^{{2x}}")

        # a·base^x 項
        if coeff_y1 > 0:
            if coeff_y1 == 1:
                terms.append(f"+ {base}^x")
            else:
                terms.append(f"+ {self._format_fraction(coeff_y1)} \\cdot {base}^x")
        elif coeff_y1 < 0:
            if coeff_y1 == -1:
                terms.append(f"- {base}^x")
            else:
                terms.append(f"- {self._format_fraction(abs(coeff_y1))} \\cdot {base}^x")

        # 常數項
        if coeff_y0 > 0:
            terms.append(f"+ {self._format_fraction(coeff_y0)}")
        elif coeff_y0 < 0:
            terms.append(f"- {self._format_fraction(abs(coeff_y0))}")

        return " ".join(terms) + " = 0"

    def _apply_type2_hiding(self, base: int, coeff_y1: Fraction,
                           coeff_y0: Fraction, hiding_type: str) -> str:
        """應用題型二隱藏變形（含降級回退機制）

        Args:
            base (int): 底數
            coeff_y1 (Fraction): y 係數
            coeff_y0 (Fraction): 常數項
            hiding_type (str): 隱藏類型 - 'none', 'base', 'exp', 'both'

        Returns:
            str: LaTeX格式的方程式

        Hiding Types:
            none: base^(2x) + a·base^x + b = 0
            base: (base^2)^x + a·base^x + b = 0
            exp:  base^(2x) + (a/base)·base^(x+1) + b = 0
            both: (base^2)^x + (a/base)·base^(x+1) + b = 0
        """
        # 檢查指數變化是否可行（係數必須被底數整除）
        can_exp_hiding = (coeff_y1 % base == 0)

        # 降級回退邏輯
        if hiding_type == 'both' and not can_exp_hiding:
            hiding_type = 'base'  # 降級：兩者都變 → 只變底數
        elif hiding_type == 'exp' and not can_exp_hiding:
            hiding_type = 'none'  # 降級：指數變化 → 基本型

        # 應用對應的隱藏
        if hiding_type == 'none':
            # 基本形式
            return self._format_type2_equation_basic(base, 1, coeff_y1, coeff_y0)

        elif hiding_type == 'base':
            # 底數變化：4^x - 10·2^x + 16 = 0
            new_base = base ** 2
            terms = []
            terms.append(f"{new_base}^x")

            # a·base^x 項
            if coeff_y1 > 0:
                if coeff_y1 == 1:
                    terms.append(f"+ {base}^x")
                else:
                    terms.append(f"+ {self._format_fraction(coeff_y1)} \\cdot {base}^x")
            elif coeff_y1 < 0:
                if coeff_y1 == -1:
                    terms.append(f"- {base}^x")
                else:
                    terms.append(f"- {self._format_fraction(abs(coeff_y1))} \\cdot {base}^x")

            # 常數項
            if coeff_y0 > 0:
                terms.append(f"+ {self._format_fraction(coeff_y0)}")
            elif coeff_y0 < 0:
                terms.append(f"- {self._format_fraction(abs(coeff_y0))}")

            return " ".join(terms) + " = 0"

        elif hiding_type == 'exp':
            # 指數變化：2^(2x) - 5·2^(x+1) + 16 = 0
            new_coeff = coeff_y1 // base
            terms = []
            terms.append(f"{base}^{{2x}}")

            # (a/base)·base^(x+1) 項
            if new_coeff > 0:
                if new_coeff == 1:
                    terms.append(f"+ {base}^{{x+1}}")
                else:
                    terms.append(f"+ {self._format_fraction(new_coeff)} \\cdot {base}^{{x+1}}")
            elif new_coeff < 0:
                if new_coeff == -1:
                    terms.append(f"- {base}^{{x+1}}")
                else:
                    terms.append(f"- {self._format_fraction(abs(new_coeff))} \\cdot {base}^{{x+1}}")

            # 常數項
            if coeff_y0 > 0:
                terms.append(f"+ {self._format_fraction(coeff_y0)}")
            elif coeff_y0 < 0:
                terms.append(f"- {self._format_fraction(abs(coeff_y0))}")

            return " ".join(terms) + " = 0"

        else:  # 'both'
            # 兩者都變：4^x - 5·2^(x+1) + 16 = 0
            new_base = base ** 2
            new_coeff = coeff_y1 // base
            terms = []
            terms.append(f"{new_base}^x")

            # (a/base)·base^(x+1) 項
            if new_coeff > 0:
                if new_coeff == 1:
                    terms.append(f"+ {base}^{{x+1}}")
                else:
                    terms.append(f"+ {self._format_fraction(new_coeff)} \\cdot {base}^{{x+1}}")
            elif new_coeff < 0:
                if new_coeff == -1:
                    terms.append(f"- {base}^{{x+1}}")
                else:
                    terms.append(f"- {self._format_fraction(abs(new_coeff))} \\cdot {base}^{{x+1}}")

            # 常數項
            if coeff_y0 > 0:
                terms.append(f"+ {self._format_fraction(coeff_y0)}")
            elif coeff_y0 < 0:
                terms.append(f"- {self._format_fraction(abs(coeff_y0))}")

            return " ".join(terms) + " = 0"

    # ==================== 詳解生成方法 ====================

    def _generate_type1_explanation(self, common_base: int, p: int, q: int,
                                    m1: int, c1: int, m2: int, c2: int,
                                    x_solution: int) -> str:
        """生成題型一的詳細解析

        Args:
            common_base (int): 共同底數
            p, q (int): 指數偏移
            m1, c1, m2, c2 (int): 指數表達式的係數和常數
            x_solution (int): 方程式的解

        Returns:
            str: LaTeX格式的詳細解析
        """
        steps = []

        # 步驟1：轉換為共同底數
        if p > 0:
            left_conversion = f"({common_base}^{{{p}}})^{{{self._format_linear_expr(m1, c1, 'x')}}}"
        else:
            left_conversion = f"({common_base}^{{{p}}})^{{{self._format_linear_expr(m1, c1, 'x')}}}"

        if q > 0:
            right_conversion = f"({common_base}^{{{q}}})^{{{self._format_linear_expr(m2, c2, 'x')}}}"
        else:
            right_conversion = f"({common_base}^{{{q}}})^{{{self._format_linear_expr(m2, c2, 'x')}}}"

        steps.append(f"${left_conversion} = {right_conversion}$")

        # 步驟2：展開指數
        left_expanded = self._format_linear_expr(p * m1, p * c1, 'x')
        right_expanded = self._format_linear_expr(q * m2, q * c2, 'x')
        steps.append(f"${common_base}^{{{left_expanded}}} = {common_base}^{{{right_expanded}}}$")

        # 步驟3：比較指數
        steps.append(f"比較指數：${left_expanded} = {right_expanded}$")

        # 步驟4：求解線性方程
        # p*m1*x + p*c1 = q*m2*x + q*c2
        # (p*m1 - q*m2)x = q*c2 - p*c1
        lhs_coeff = p * m1 - q * m2
        rhs_const = q * c2 - p * c1

        steps.append(f"${lhs_coeff}x = {rhs_const}$")
        steps.append(f"$x = {x_solution}$")

        return "\\\\".join(steps)

    def _generate_type1_chain_explanation(self, base1: int, value: int, x_solution: int,
                                          left_base_2: int, right_base_2: int,
                                          common_base_2: int, p: int, q: int,
                                          y_solution: Fraction) -> str:
        """生成題型一鏈式求解的詳細解析

        Args:
            base1 (int): 關係一的底數
            value (int): 關係一的值
            x_solution (int): x 的解
            left_base_2 (int): 關係二左邊底數
            right_base_2 (int): 關係二右邊底數
            common_base_2 (int): 關係二的共同底數
            p, q (int): 關係二的指數偏移
            y_solution (Fraction): y 的解

        Returns:
            str: LaTeX格式的詳細解析
        """
        steps = []

        # 步驟1：求解 x（關係一）
        steps.append(f"1. 從 ${base1}^x = {value}$ 開始")
        steps.append(f"   $({base1}^1)^x = {base1}^{x_solution}$")
        steps.append(f"   $x = {x_solution}$")

        # 步驟2：代入關係二
        steps.append(f"2. 代入第二式：${left_base_2}^y = {right_base_2}^{{{x_solution}}}$")
        steps.append(f"   $({common_base_2}^{{{p}}})^y = ({common_base_2}^{{{q}}})^{{{x_solution}}}$")
        steps.append(f"   ${common_base_2}^{{{p}y}} = {common_base_2}^{{{q * x_solution}}}$")

        # 步驟3：比較指數
        steps.append(f"3. 比較指數：${p}y = {q * x_solution}$")
        steps.append(f"   $y = {self._format_fraction(y_solution)}$")

        return "\\\\".join(steps)

    def _generate_type2_explanation(self, base: int, coeff_y1: Fraction,
                                    coeff_y0: Fraction, k1: Fraction,
                                    k2: Fraction, solutions: List[Fraction],
                                    solution_to_target: Dict[Fraction, Fraction]) -> str:
        """生成題型二的詳細解析

        Args:
            base (int): 底數
            coeff_y1, coeff_y0 (Fraction): 方程式係數
            k1, k2 (Fraction): 因式目標值
            solutions (List[Fraction]): 實數解列表
            solution_to_target (Dict[Fraction, Fraction]): 解到目標值的映射

        Returns:
            str: LaTeX格式的詳細解析
        """
        steps = []

        # 步驟1：代換
        steps.append(f"令 $y = {base}^x$，則 ${base}^{{2x}} = y^2$")

        # 步驟2：代入得二次方程
        y_eq = f"y^2 {'+' if coeff_y1 >= 0 else ''}{self._format_fraction(coeff_y1)}y "
        y_eq += f"{'+' if coeff_y0 >= 0 else ''}{self._format_fraction(coeff_y0)} = 0"
        steps.append(f"原方程變為：${y_eq}$")

        # 步驟3：因式分解
        if k2 > 0:
            factored = f"(y - {self._format_fraction(k1)})(y - {self._format_fraction(k2)}) = 0"
        else:
            factored = f"(y - {self._format_fraction(k1)})(y + {self._format_fraction(abs(k2))}) = 0"
        steps.append(f"${factored}$")

        # 步驟4：求解 y
        if k2 > 0:
            steps.append(f"$y = {self._format_fraction(k1)}$ 或 $y = {self._format_fraction(k2)}$")
        else:
            steps.append(f"$y = {self._format_fraction(k1)}$ 或 $y = {self._format_fraction(k2)}$（無實數解）")

        # 步驟5：代回求 x（使用正確的映射關係）
        for sol in solutions:
            target = solution_to_target[sol]
            steps.append(f"${base}^x = {self._format_fraction(target)} \\Rightarrow x = {self._format_fraction(sol)}$")

        return "\\\\".join(steps)

    def _generate_type3_explanation(self, base1: int, base2: int,
                                    k1: Fraction, k2: Fraction,
                                    mixed_base: int, solutions: List[Fraction],
                                    solution_to_base_target: Dict[Fraction, Tuple[int, Fraction]]) -> str:
        """生成題型三的詳細解析

        Args:
            base1, base2 (int): 兩個底數
            k1, k2 (Fraction): 因式目標值
            mixed_base (int): 混合底數 (base1 * base2)
            solutions (List[Fraction]): 實數解列表
            solution_to_base_target (Dict[Fraction, Tuple[int, Fraction]]): 解到(底數,目標值)的映射

        Returns:
            str: LaTeX格式的詳細解析
        """
        steps = []

        # 步驟1：分組
        steps.append(f"分組：$({mixed_base}^x - {self._format_fraction(k2)} \\cdot {base1}^x) - "
                    f"({self._format_fraction(k1)} \\cdot {base2}^x - {self._format_fraction(k1 * k2)}) = 0$")

        # 步驟2：提取公因式
        steps.append(f"第一組提 ${base1}^x$：${base1}^x({base2}^x - {self._format_fraction(k2)}) - "
                    f"{self._format_fraction(k1)}({base2}^x - {self._format_fraction(k2)}) = 0$")

        # 步驟3：提取公因式
        steps.append(f"提取公因式 $({base2}^x - {self._format_fraction(k2)})$："
                    f"$({base1}^x - {self._format_fraction(k1)})({base2}^x - {self._format_fraction(k2)}) = 0$")

        # 步驟4：求解（使用正確的映射關係）
        for sol in solutions:
            base, target = solution_to_base_target[sol]
            steps.append(f"${base}^x = {self._format_fraction(target)} \\Rightarrow x = {self._format_fraction(sol)}$")

        return "\\\\".join(steps)

    # ==================== 元數據方法 ====================

    def get_grade(self) -> str:
        """獲取適用年級"""
        return "G11S1"  # 高二上學期

    def get_category(self) -> str:
        """獲取題目主類別"""
        return "指數與對數"

    def get_subcategory(self) -> str:
        """獲取題目子類別"""
        return "基礎指數方程式"

    def get_question_size(self) -> int:
        """獲取題目顯示大小

        指數方程式使用MEDIUM尺寸（2x2），適合複雜方程式顯示。

        Returns:
            int: QuestionSize.MEDIUM.value (4)
        """
        return QuestionSize.MEDIUM.value

    def get_subject(self) -> str:
        """獲取科目"""
        return "數學"

    def get_difficulty(self) -> str:
        """獲取難度等級"""
        return "MEDIUM"

    def _get_fallback_question(self) -> Dict[str, Any]:
        """提供預設題目確保系統穩定性

        Returns:
            Dict[str, Any]: 預設題目的完整資訊
        """
        return {
            'question': "求解方程式：$9^{x+2} = \\left(\\frac{1}{3}\\right)^{2x+8}$",
            'answer': "$x = -3$",
            'explanation': "$(3^2)^{x+2} = (3^{-1})^{2x+8}$ \\\\ "
                          "$3^{2x+4} = 3^{-2x-8}$ \\\\ "
                          "$2x+4 = -2x-8$ \\\\ "
                          "$4x = -12$ \\\\ "
                          "$x = -3$",
            'figure_data_question': None,
            'figure_data_explanation': None,
            **self._get_standard_metadata()
        }
