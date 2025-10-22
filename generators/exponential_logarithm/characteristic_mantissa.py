#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""大指數估算題目生成器

使用對數的首數（characteristic）與尾數（mantissa）方法，
估算形如 a^b 的大指數值，答案以科學記號表示。

本模組遵循典範B設計模式：
- 預篩選有效組合（對數表 + 基數指數配對）
- 確定性生成（從預建清單隨機選取）
- 完整數學驗證（首數尾數計算正確性）

Technical Details:
    本生成器使用預建對數表和預篩選組合策略，確保100%生成成功率。
    支援整數底數（2-9）和分數底數（2-9組成的最簡真分數），
    指數範圍為30-100的十的倍數。

Example:
    >>> generator = LargeExponentEstimationGenerator()
    >>> question = generator.generate_question()
    >>> print(question['question'])
    估算 $7^{30} \\approx ?$（已知 $\\log_{10}7 \\approx 0.8451$）
    >>> print(question['answer'])
    $2.3 \\times 10^{25}$
"""

import random
import math
from typing import Dict, Any, List, Tuple

from utils import get_logger
from ..base import QuestionGenerator, QuestionSize, register_generator


@register_generator
class LargeExponentEstimationGenerator(QuestionGenerator):
    """大指數估算題目生成器

    生成形如「估算 7^30 ≈ ?」的題目，利用對數首數尾數方法計算。

    Args:
        options (Dict[str, Any], optional): 生成器配置選項
            type_ratio (dict): 題型比例分配
                integer (int): 整數基數題型百分比，預設50
                fraction (int): 分數基數題型百分比，預設50

    Returns:
        Dict[str, Any]: 包含題目、答案、解釋等完整資訊
            question (str): 題目 LaTeX 字串
            answer (str): 答案 LaTeX 字串（科學記號）
            explanation (str): 詳解 LaTeX 字串（含對數運算步驟）
            metadata (dict): 元數據資訊

    Example:
        >>> options = {"type_ratio": {"integer": 100, "fraction": 0}}
        >>> generator = LargeExponentEstimationGenerator(options)
        >>> question = generator.generate_question()
        >>> print(question['question'])
        估算 $7^{30} \\approx ?$（已知 $\\log_{10}7 \\approx 0.8451$）
        >>> print(question['answer'])
        $2.3 \\times 10^{25}$
    """

    # 學生應背記的對數表（四捨五入至第四位）
    STANDARD_LOG_VALUES = {
        2: 0.3010, 3: 0.4771, 4: 0.6021, 5: 0.6990,
        6: 0.7782, 7: 0.8451, 8: 0.9031, 9: 0.9542
    }

    def __init__(self, options: Dict[str, Any] = None):
        """初始化大指數估算生成器

        Args:
            options: 配置選項字典，支援 type_ratio 百分比組配置
        """
        super().__init__(options)
        self.logger = get_logger(self.__class__.__name__)

        options = options or {}

        # 讀取 percentage_group 配置
        type_ratio = options.get('type_ratio', {
            'integer': 50,
            'fraction': 50
        })
        self.integer_weight = type_ratio.get('integer', 50)
        self.fraction_weight = type_ratio.get('fraction', 50)

        # 建立題型權重清單（參考典範C）
        self.question_types = (['integer'] * self.integer_weight +
                              ['fraction'] * self.fraction_weight)

        # 預篩選有效組合（參考典範B核心設計）
        self.valid_combinations = self._build_valid_combinations()

        self.logger.info(f"已預篩選 {len(self.valid_combinations)} 個有效組合")

    def _build_valid_combinations(self) -> List[Dict[str, Any]]:
        """預篩選所有有效的題目組合

        本方法實作典範B的核心策略：預先建立所有有效組合，確保生成時100%成功。
        組合包含整數底數（2-9）和分數底數（2-9組成的最簡真分數）。

        Returns:
            List[Dict]: 每個字典包含：
                - type: 'integer' 或 'fraction'
                - base: 底數（整數或元組 (分子, 分母)）
                - exponent: 指數
                - log_value: 對數值
                - result: 預計算結果 (characteristic, mantissa, first_digit)

        Note:
            預期組合總數為216個（整數64個 + 分數152個）
        """
        combinations = []

        # 整數底數組合（2-9，共8個）
        for base in range(2, 10):
            log_val = self.STANDARD_LOG_VALUES[base]
            for exp in range(30, 101, 10):  # 指數: 30, 40, 50, 60, 70, 80, 90, 100
                char, mant, digit = self._calculate_result(base, exp, log_val)
                combinations.append({
                    'type': 'integer',
                    'base': base,
                    'exponent': exp,
                    'log_value': log_val,
                    'result': (char, mant, digit)
                })

        # 分數底數組合（2-9組成的所有最簡真分數）
        fraction_pairs = []
        for num in range(2, 10):
            for denom in range(2, 10):
                if num >= denom:
                    continue  # 只要真分數
                if math.gcd(num, denom) == 1:  # 最簡分數
                    fraction_pairs.append((num, denom))

        # 預計有19個分數底數
        self.logger.info(f"生成 {len(fraction_pairs)} 個最簡真分數底數（預期19個）")

        for num, denom in fraction_pairs:
            log_num = self.STANDARD_LOG_VALUES.get(num)
            log_denom = self.STANDARD_LOG_VALUES.get(denom)
            if log_num is None or log_denom is None:
                continue

            log_val = log_num - log_denom
            for exp in range(30, 101, 10):  # 指數: 30, 40, 50, 60, 70, 80, 90, 100
                char, mant, digit = self._calculate_result(
                    (num, denom), exp, log_val, is_fraction=True
                )
                combinations.append({
                    'type': 'fraction',
                    'base': (num, denom),
                    'exponent': exp,
                    'log_value': log_val,
                    'result': (char, mant, digit)
                })

        return combinations

    def _calculate_result(self, base, exp: int, log_val: float,
                         is_fraction: bool = False) -> Tuple[int, float, float]:
        """計算對數結果的首數、尾數和首位有效數字

        實作對數首數尾數分離算法，處理正數和負數對數的情況。

        Args:
            base: 基數（整數或元組）
            exp: 指數
            log_val: 對數值
            is_fraction: 是否為分數基數

        Returns:
            Tuple[int, float, float]: (characteristic, mantissa, first_digit)
                - characteristic: 首數（整數部分）
                - mantissa: 尾數（小數部分，範圍0-1）
                - first_digit: 首位有效數字（10^mantissa的值）

        Note:
            負數對數處理：-13.314 → characteristic=-14, mantissa=0.686
        """
        # 計算 log10(base^exp)
        total_log = exp * log_val

        # 分離首數和尾數
        if total_log >= 0:
            characteristic = int(total_log)
            mantissa = total_log - characteristic
        else:
            # 負數情況：-13.314 → -14 + 0.686
            characteristic = int(total_log) - 1 if total_log != int(total_log) else int(total_log)
            mantissa = total_log - characteristic

        # 計算首位有效數字（10^mantissa）
        first_digit = 10 ** mantissa

        return characteristic, mantissa, first_digit

    def _generate_core_question(self) -> Dict[str, Any]:
        """核心題目生成邏輯（從預篩選清單隨機選取）

        實作確定性生成策略：從預建組合清單中隨機選取，確保100%成功率。

        Returns:
            Dict[str, Any]: 完整的題目資訊字典
        """
        # 1. 根據權重選擇題型
        q_type = random.choice(self.question_types)

        # 2. 從對應題型的組合中隨機選取
        filtered = [c for c in self.valid_combinations if c['type'] == q_type]
        if not filtered:
            self.logger.warning(f"題型 {q_type} 無有效組合，使用後備題目")
            return self._get_fallback_question()

        combo = random.choice(filtered)

        # 3. 格式化題目
        question = self._format_question(combo)

        # 4. 格式化答案
        answer = self._format_answer(combo)

        # 5. 格式化詳解
        explanation = self._format_explanation(combo)

        return {
            "question": question,
            "answer": answer,
            "explanation": explanation,
            **self._get_standard_metadata()
        }

    def _format_question(self, combo: Dict) -> str:
        """格式化題目文字

        Args:
            combo: 題目組合字典

        Returns:
            str: LaTeX 格式的題目字串
        """
        base = combo['base']
        exp = combo['exponent']
        log_val = combo['log_value']

        if combo['type'] == 'integer':
            base_str = str(base)
            log_info = f"$\\log {base} = {log_val:.4f}$"
        else:
            num, denom = base
            base_str = f"\\frac{{{num}}}{{{denom}}}"
            log_num = self.STANDARD_LOG_VALUES[num]
            log_denom = self.STANDARD_LOG_VALUES[denom]
            log_info = f"$\\log {num} = {log_num:.4f}, \\log {denom} = {log_denom:.4f}$"

        return f"估算 $({base_str})^{{{exp}}} \\approx ?$（{log_info}）"

    def _format_answer(self, combo: Dict) -> str:
        """格式化答案（科學記號）

        Args:
            combo: 題目組合字典

        Returns:
            str: LaTeX 格式的答案字串（科學記號形式）
        """
        char, mant, digit = combo['result']

        # 四捨五入至一位小數
        digit_rounded = round(digit, 1)

        return f"${digit_rounded} \\times 10^{{{char}}}$"

    def _format_explanation(self, combo: Dict) -> str:
        """格式化詳解（遵循 explanation_level = B）

        生成包含公式、代入、計算步驟和最終答案的完整詳解。

        Args:
            combo: 題目組合字典

        Returns:
            str: LaTeX 格式的詳解字串，使用雙重轉義換行符
        """
        base = combo['base']
        exp = combo['exponent']
        log_val = combo['log_value']
        char, mant, digit = combo['result']

        digit_rounded = round(digit, 1)

        if combo['type'] == 'integer':
            base_str = str(base)
            step1 = f"$\\log({base_str}^{{{exp}}}) = {exp} \\times {log_val:.4f} = {exp * log_val:.3f}$"
        else:
            num, denom = base
            log_num = self.STANDARD_LOG_VALUES[num]
            log_denom = self.STANDARD_LOG_VALUES[denom]
            step1 = f"$\\log\\left(\\left(\\frac{{{num}}}{{{denom}}}\\right)^{{{exp}}}\\right) = {exp} \\times ({log_num:.4f} - {log_denom:.4f}) = {exp} \\times ({log_val:.4f}) = {exp * log_val:.3f}$"

        total_log = exp * log_val
        step2 = f"$= {char} + {mant:.3f}$"
        step3 = f"$= \\log(10^{{{char}}}) + \\log({digit:.2f})$"
        step4 = f"$\\implies$ 原式 $\\approx {digit_rounded} \\times 10^{{{char}}}$"

        # 使用 \\\\ 換行（遵循 RULES.latex_boundary）
        return f"{step1} \\\\\\\\ {step2} \\\\\\\\ {step3} \\\\\\\\ {step4}"

    def _get_fallback_question(self) -> Dict[str, Any]:
        """後備題目（固定安全題目）

        當核心生成邏輯失敗時使用的後備題目，確保系統穩定性。

        Returns:
            Dict[str, Any]: 完整的後備題目資訊
        """
        return {
            "question": "估算 $2^{100} \\approx ?$（$\\log 2 = 0.3010$）",
            "answer": "$1.3 \\times 10^{30}$",
            "explanation": (
                "$\\log(2^{100}) = 100 \\times 0.3010 = 30.100$ \\\\\\\\ "
                "$= 30 + 0.100$ \\\\\\\\ "
                "$= \\log(10^{30}) + \\log(1.26)$ \\\\\\\\ "
                "$\\implies 2^{100} \\approx 1.3 \\times 10^{30}$"
            ),
            **self._get_standard_metadata()
        }

    @classmethod
    def get_config_schema(cls) -> Dict[str, Dict[str, Any]]:
        """定義生成器的UI配置選項

        Returns:
            Dict[str, Dict[str, Any]]: 配置Schema，定義UI控制項
        """
        return {
            "type_ratio": {
                "type": "percentage_group",
                "label": "題型比例",
                "description": "調整整數基數與分數基數題型的出現頻率",
                "items": {
                    "integer": {
                        "label": "整數底數（如 7^30）",
                        "default": 50
                    },
                    "fraction": {
                        "label": "分數底數（如 (3/5)^60）",
                        "default": 50
                    }
                }
            }
        }

    def get_category(self) -> str:
        """獲取主分類

        Returns:
            str: 主分類名稱
        """
        return "指數與對數"

    def get_subcategory(self) -> str:
        """獲取子分類

        Returns:
            str: 子分類名稱
        """
        return "首數尾數應用"

    def get_grade(self) -> str:
        """獲取年級

        Returns:
            str: 年級代碼（G11S1 = 高二上）
        """
        return "G11S1"

    def get_question_size(self) -> int:
        """獲取題目尺寸

        Returns:
            int: 題目尺寸值（WIDE = 2x1）
        """
        return QuestionSize.WIDE.value
