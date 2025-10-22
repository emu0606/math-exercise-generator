#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 對數內插法練習題目生成器

本模組提供對數概算（內插法）練習題目生成器，支援正向內插（給定真數求對數值）
和反向內插（給定對數值求真數）兩種題型。使用預建可逆配對表確保數學邏輯一致性，
並附帶數線圖形輔助視覺化。

設計理念：
- 使用預篩選可逆配對表，確保正向和反向內插結果一致
- 詳解採用「公式 → 代入 → 答案」三步驟結構
- 所有對數以十為底（LaTeX 寫作 \\log 不標底數）
- 整合數線圖形生成器進行視覺化展示

Example:
    基本使用（混合模式）::

        generator = LogarithmInterpolationGenerator()
        question = generator.generate_question()

    指定題型（正向內插）::

        generator = LogarithmInterpolationGenerator({
            'question_type': 'forward'
        })
        question = generator.generate_question()

Note:
    - 真數範圍: 1.1 ~ 9.9（一位小數）
    - 對數精度: 二位小數
    - 可逆配對數量: 69組
    - 年級分類: G10S2（高一下）
"""

from generators.base import QuestionGenerator, QuestionSize, register_generator
from utils import get_logger
import random
import math
from typing import Dict, Any

# 詳解模板
EXPLANATION_TEMPLATE_FORWARD = """
$\\frac{{\\log {x} - \\log {lower}}}{{\\log {upper} - \\log {lower}}} = \\frac{{{x} - {lower}}}{{{upper} - {lower}}}$
\\\\[0.3em]
$\\log {x}$
\\\\[0.3em]
$= \\log {lower} + \\frac{{{x} - {lower}}}{{{upper} - {lower}}} \\times (\\log {upper} - \\log {lower})$
\\\\[0.3em]
$= {log_lower} + {{\\frac{{{x_minus_lower}}}{{{upper_minus_lower}}}}} \\times ({log_upper} - {log_lower})$
\\\\[0.3em]
$\\approx {log_x}$
"""

EXPLANATION_TEMPLATE_BACKWARD = """
$\\frac{{x - {lower}}}{{{upper} - {lower}}} = \\frac{{{log_x} - {log_lower}}}{{{log_upper} - {log_lower}}}$
\\\\[0.3em]
$x = {lower} + \\frac{{{log_x} - {log_lower}}}{{{log_upper} - {log_lower}}}$
\\\\[0.3em]
$\\phantom{{x}} = {lower} + {increment:.4f}$
\\\\[0.3em]
$\\phantom{{x}} \\approx {x}$
"""

@register_generator
class LogarithmInterpolationGenerator(QuestionGenerator):
    """對數內插法練習題目生成器

    生成對數概算練習題，使用線性內插法估算對數值或反推真數。
    附帶數線圖形輔助視覺化。

    Args:
        options (Dict[str, Any], optional): 生成器配置選項
            question_type (str): 題型選擇
                - "forward": 正向（給真數求對數）
                - "backward": 反向（給對數求真數）
                - "mixed": 混合模式（預設）

    Returns:
        Dict[str, Any]: 包含題目、答案、解釋及圖形資料

    Example:
        >>> generator = LogarithmInterpolationGenerator()
        >>> question = generator.generate_question()
        >>> print(question['question'])
        利用內插法估算：$\\log 2.5 \\approx$ ?
        >>> print(question['answer'])
        $0.39$
    """

    # 標準對數值表（以十為底）
    STANDARD_LOG_VALUES = {
        1: 0.0000, 2: 0.3010, 3: 0.4771, 4: 0.6020, 5: 0.6990,
        6: 0.7781, 7: 0.8451, 8: 0.9030, 9: 0.9542, 10: 1.0000
    }

    def __init__(self, options: Dict[str, Any] = None):
        """初始化對數內插法生成器

        Args:
            options: 配置選項字典，包含 question_type 等參數
        """
        super().__init__(options)
        self.logger = get_logger(self.__class__.__name__)

        # 配置讀取
        options = options or {}
        self.question_type = options.get('question_type', 'mixed')
        self.show_log_values = options.get('show_log_values', True)

        # 預建可逆配對表
        self._build_valid_pairs()

        # 當前圖形資料（由 _generate_core_question 設置）
        self._current_figure_data_question = None  # 題目圖形（有問號）
        self._current_figure_data_explanation = None  # 詳解圖形（有答案）

        self.logger.info(f"對數內插法生成器初始化完成，題型: {self.question_type}")

    def _build_valid_pairs(self):
        """建立所有可逆的(真數, 對數值)配對

        遍歷所有候選真數（1.1 ~ 9.9），計算對數值後反推真數，
        僅保留可逆的配對（誤差 < 0.05）。

        結果儲存於 self.valid_pairs，格式: [(x, log_x), ...]
        """
        self.valid_pairs = []

        for x_int in range(11, 100):  # 1.1 ~ 9.9
            x = round(x_int * 0.1, 1)

            # 跳過整數真數
            if x in [2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]:
                continue

            log_x = self._interpolate_log(x)
            x_recovered = self._interpolate_antilog(log_x)

            # 檢查可逆性（允許小誤差）
            if abs(x - x_recovered) < 0.05:
                self.valid_pairs.append((x, log_x))

        self.logger.info(f"建立可逆配對 {len(self.valid_pairs)} 個")

    def _interpolate_log(self, x: float) -> float:
        """正向內插法：真數 → 對數值

        使用線性內插公式計算對數值。

        Args:
            x: 真數（1.1 ~ 9.9）

        Returns:
            float: 對數值（二位小數）
        """
        lower = int(x)
        upper = lower + 1
        log_lower = self.STANDARD_LOG_VALUES[lower]
        log_upper = self.STANDARD_LOG_VALUES[upper]

        # 線性內插公式
        ratio = (x - lower) / (upper - lower)
        log_approx = log_lower + ratio * (log_upper - log_lower)

        return round(log_approx, 2)

    def _interpolate_antilog(self, log_val: float) -> float:
        """反向內插法：對數值 → 真數

        使用線性內插公式反推真數。

        Args:
            log_val: 對數值（0 ~ 1）

        Returns:
            float: 真數（一位小數）
        """
        # 找到對數值所在區間
        for i in range(1, 10):
            log_i = self.STANDARD_LOG_VALUES[i]
            log_i_plus_1 = self.STANDARD_LOG_VALUES[i + 1]

            if log_i <= log_val <= log_i_plus_1:
                lower = i
                upper = i + 1
                log_lower = log_i
                log_upper = log_i_plus_1
                break

        # 線性內插公式
        ratio = (log_val - log_lower) / (log_upper - log_lower)
        x_approx = lower + ratio * (upper - lower)

        return round(x_approx, 1)

    def _generate_core_question(self) -> Dict[str, Any]:
        """核心題目生成邏輯

        從可逆配對表隨機選擇，生成正向或反向題型。

        Returns:
            Dict[str, Any]: 包含題目、答案、詳解、圖形資料和元數據
        """
        # 從可逆配對表選擇
        x, log_x = random.choice(self.valid_pairs)

        # 確定題型
        if self.question_type == 'mixed':
            is_forward = random.choice([True, False])
        else:
            is_forward = (self.question_type == 'forward')

        # 找到基準點
        lower = int(x)
        upper = lower + 1
        log_lower = self.STANDARD_LOG_VALUES[lower]
        log_upper = self.STANDARD_LOG_VALUES[upper]

        # 生成題目內容
        if is_forward:
            question = f"估算：$\\log {x} \\approx$ ?"
            answer = f"${log_x}$"
            explanation = self._generate_forward_explanation(
                x, log_x, lower, upper, log_lower, log_upper
            )
        else:
            question = f"$\\log x = {log_x}$，估算 $x$ = ?"
            answer = f"${x}$"
            explanation = self._generate_backward_explanation(
                x, log_x, lower, upper, log_lower, log_upper
            )

        # 生成兩套圖形資料：題目用問號，詳解用答案
        self._current_figure_data_question = self._generate_figure_data(
            x, log_x, lower, upper, log_lower, log_upper, is_forward, use_question_mark=True
        )
        self._current_figure_data_explanation = self._generate_figure_data(
            x, log_x, lower, upper, log_lower, log_upper, is_forward, use_question_mark=False
        )

        return {
            "question": question,
            "answer": answer,
            "explanation": explanation,
            **self._get_standard_metadata()
        }

    def _generate_figure_data(self, x: float, log_x: float,
                             lower: int, upper: int,
                             log_lower: float, log_upper: float,
                             is_forward: bool,
                             use_question_mark: bool = True) -> Dict[str, Any]:
        """生成數線圖形資料

        返回符合圖形生成器系統的標準格式。

        Args:
            x: 真數
            log_x: 對數值
            lower: 左端點整數
            upper: 右端點整數
            log_lower: 左端點對數值
            log_upper: 右端點對數值
            is_forward: 是否為正向題型
            use_question_mark: 是否使用問號（題目用True，詳解用False）

        Returns:
            Dict[str, Any]: 圖形資料，包含 type, params, options
        """
        # 上方標籤（對數值）
        # 詳解階段必定全顯示，題目階段考慮配置
        if not use_question_mark:
            # 詳解圖形：完整顯示所有對數值
            top_left = f"{log_lower:.4f}"
            top_middle = f"{log_x}"
            top_right = f"{log_upper:.4f}"
        else:
            # 題目圖形：端點受配置控制，中間值視題型決定
            if is_forward:
                # 正向題型（求對數）：中間顯示問號
                top_left = f"{log_lower:.4f}" if self.show_log_values else ""
                top_middle = "?"  # 問題本身，必須顯示
                top_right = f"{log_upper:.4f}" if self.show_log_values else ""
            else:
                # 反向題型（求真數）：中間顯示已知對數值
                top_left = f"{log_lower:.4f}" if self.show_log_values else ""
                top_middle = f"{log_x}"  # 題目條件，必須顯示
                top_right = f"{log_upper:.4f}" if self.show_log_values else ""

        # 下方標籤（真數）
        if is_forward:
            bottom_left = f"{lower}"
            bottom_middle = f"{x}"
            bottom_right = f"{upper}"
        else:
            bottom_left = f"{lower}"
            bottom_middle = "?" if use_question_mark else f"{x}"
            bottom_right = f"{upper}"

        return {
            'type': 'number_line',
            'params': {
                'lower_value': lower,
                'upper_value': upper,
                'middle_value': x,
                'lower_label': top_left,
                'upper_label': top_right,
                'middle_label': top_middle,
                'lower_bottom': bottom_left,
                'upper_bottom': bottom_right,
                'middle_bottom': bottom_middle,
                'line_length': 4.0,
                'tick_height': 0.15
            },
            'options': {
                'scale': 1.0
            }
        }

    def _generate_forward_explanation(self, x, log_x, lower, upper,
                                      log_lower, log_upper) -> str:
        """生成正向題型詳解

        使用模板系統生成「公式 → 代入 → 答案」格式詳解。

        Args:
            x: 真數
            log_x: 對數值
            lower: 左端點
            upper: 右端點
            log_lower: 左端點對數值
            log_upper: 右端點對數值

        Returns:
            str: LaTeX 格式詳解
        """
        # 修正浮點數精度問題
        x_minus_lower = round(x - lower, 1)
        upper_minus_lower = upper - lower  # 永遠是整數1

        return EXPLANATION_TEMPLATE_FORWARD.format(
            x=x,
            lower=lower,
            upper=upper,
            log_lower=log_lower,
            log_upper=log_upper,
            log_x=log_x,
            x_minus_lower=x_minus_lower,
            upper_minus_lower=upper_minus_lower
        )

    def _generate_backward_explanation(self, x, log_x, lower, upper,
                                       log_lower, log_upper) -> str:
        """生成反向題型詳解

        使用模板系統生成「公式 → 代入 → 答案」格式詳解。

        Args:
            x: 真數
            log_x: 對數值
            lower: 左端點
            upper: 右端點
            log_lower: 左端點對數值
            log_upper: 右端點對數值

        Returns:
            str: LaTeX 格式詳解
        """
        increment = (log_x - log_lower) / (log_upper - log_lower)

        return EXPLANATION_TEMPLATE_BACKWARD.format(
            x=x,
            lower=lower,
            upper=upper,
            log_x=log_x,
            log_lower=log_lower,
            log_upper=log_upper,
            increment=increment
        )

    def _get_fallback_question(self) -> Dict[str, Any]:
        """後備題目

        當生成失敗時提供固定的後備題目。

        Returns:
            Dict[str, Any]: 後備題目資料
        """
        return {
            "question": "利用內插法估算：$\\log 2.5 \\approx$ ?",
            "answer": "$0.40$",
            "explanation": (
                "$\\frac{\\log 2.5 - \\log 2}{\\log 3 - \\log 2} = \\frac{2.5 - 2}{3 - 2}$\n"
                "\\\\[0.3em]\n"
                "$\\log 2.5 = \\log 2 + \\frac{2.5 - 2}{3 - 2} \\times (\\log 3 - \\log 2)$\n"
                "\\\\[0.3em]\n"
                "$\\phantom{\\log 2.5} = 0.3010 + \\frac{0.5}{1} \\times (0.4771 - 0.3010)$\n"
                "\\\\[0.3em]\n"
                "$\\phantom{\\log 2.5} \\approx 0.40$"
            ),
            **self._get_standard_metadata()
        }

    def get_figure_data_question(self) -> Dict[str, Any]:
        """獲取題目圖形資料

        Returns:
            Dict[str, Any]: 數線圖形資料（顯示問號），如果沒有則返回 None
        """
        return self._current_figure_data_question

    def get_figure_data_explanation(self) -> Dict[str, Any]:
        """獲取詳解圖形資料

        詳解圖形顯示答案數值（不顯示問號）

        Returns:
            Dict[str, Any]: 數線圖形資料（顯示答案）
        """
        return self._current_figure_data_explanation

    # 元數據方法
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
        return "對數概算練習"

    def get_grade(self) -> str:
        """獲取年級

        Returns:
            str: 年級代碼（G10S2 = 高一下）
        """
        return "G10S2"

    def get_difficulty(self) -> str:
        """獲取難度

        Returns:
            str: 難度等級
        """
        return "MEDIUM"

    def get_question_size(self) -> int:
        """獲取題目尺寸

        Returns:
            int: 題目尺寸值（WIDE = 2x1）
        """
        return QuestionSize.WIDE.value

    def get_figure_position(self) -> str:
        """獲取圖形位置

        Returns:
            str: 圖形放置位置
        """
        return "right"

    @classmethod
    def get_config_schema(cls) -> Dict[str, Dict[str, Any]]:
        """配置選項定義

        Returns:
            Dict[str, Dict[str, Any]]: 配置項目 schema
        """
        return {
            "question_type": {
                "type": "select",
                "label": "題型選擇",
                "default": "mixed",
                "options": ["求對數", "求真數", "mixed"],
                "description": "求對數:給真數求對數\n求真數: 給對數求真數\nmixed: 混合模式"
            },
            "show_log_values": {
                "type": "checkbox",
                "label": "顯示端點對數值",
                "default": True,
                "description": "數線上方是否顯示兩端對數值\n關閉可增加題目挑戰性"
            }
        }
