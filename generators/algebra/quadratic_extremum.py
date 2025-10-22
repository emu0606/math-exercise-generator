#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 二次函數極值題目生成器

生成兩種二次函數極值問題：
1. 全域極值：找出二次函數 y=ax²+bx+c 的頂點極值
2. 區間極值：找出二次函數在給定 x 範圍內的最大與最小值

使用逆推生成策略確保係數為整數，採用教學友善的參數範圍。
"""

import random
from typing import Dict, Any, Tuple

from utils import get_logger
from ..base import QuestionGenerator, QuestionSize, register_generator

logger = get_logger(__name__)


# 詳解模板常量
EXPLANATION_TEMPLATE_GLOBAL = """配方法：

$y = {function}$\\\\[0.3em]
$\\quad = {a_str}(x^2 {b_over_a_term} + {h_squared}) - {h_squared} \\times {a_paren} + {c}$\\\\[0.3em]
$\\quad = {a_str}(x - {h_paren})^2 + {k}$

因為 $a = {a}$ {comparison} $0$，開口{direction}，
所以當 $x = {h}$ 時，$y$ 有{extremum_type} ${k}$"""

EXPLANATION_TEMPLATE_INTERVAL_INSIDE = """配方法：

$y = {function}$\\\\[0.3em]
$\\quad = {a_str}(x^2 {b_over_a_term} + {h_squared}) - {h_squared} \\times {a_paren} + {c}$\\\\[0.3em]
$\\quad = {a_str}(x - {h_paren})^2 + {k}$

頂點為 $({h}, {k})$

判斷：
因為 ${x1} \\leq {h} \\leq {x2}$，頂點在區間內

開口{direction}，頂點為{vertex_extremum_type}值 ${k}$

因為 ${farther_x}$ 離頂點較遠，將 $x = {farther_x}$ 代入：

{calc_farther}

因此，最大值為 ${y_max}$，最小值為 ${y_min}$"""

EXPLANATION_TEMPLATE_INTERVAL_OUTSIDE = """配方法：

$y = {function}$\\\\[0.3em]
$\\quad = {a_str}(x^2 {b_over_a_term} + {h_squared}) - {h_squared} \\times {a_paren} + {c}$\\\\[0.3em]
$\\quad = {a_str}(x - {h_paren})^2 + {k}$

頂點為 $({h}, {k})$

判斷：
因為 ${h}$ {h_comparison} ${boundary}$，頂點在區間{side}方

開口{direction}，函數在 $[{x1}, {x2}]$ {monotonicity}

因此：
{extremum_assignment}"""


@register_generator
class QuadraticExtremumGenerator(QuestionGenerator):
    """二次函數極值題目生成器

    生成兩種題型的二次函數極值問題，適合高一學生練習配方法和極值判斷。

    題型1 - 全域極值：
        給定 y=ax²+bx+c，求頂點極值
        答案格式：當 x=h 時，y有最[大/小]值 k

    題型2 - 區間極值：
        給定 y=ax²+bx+c 及 x 範圍，求區間內的最大與最小值
        答案格式：最大值為 M，最小值為 m

    Args:
        options (Dict[str, Any], optional): 生成器配置選項
            question_types (Dict): 題型比例配置
                global_extremum (int): 全域極值題型比例，預設50
                interval_extremum (int): 區間極值題型比例，預設50
            difficulty_level (str): 難度等級，預設"medium"
                - "easy": 簡單（a∈[-2,2], h,k∈[-5,5]）
                - "medium": 中等（a∈[-4,4], h,k∈[-10,10]）
                - "hard": 困難（a∈[-6,6], h,k∈[-15,15]）

    Returns:
        Dict[str, Any]: 包含完整題目資訊的字典
            question (str): 題目LaTeX字串
            answer (str): 答案LaTeX字串
            explanation (str): 詳解LaTeX字串
            size (int): 題目顯示大小（MEDIUM）
            difficulty (str): 難度等級
            category (str): 主類別（數與式）
            subcategory (str): 子類別（二次函數的極值）
            grade (str): 年級分類（G10S1）

    Example:
        >>> generator = QuadraticExtremumGenerator()
        >>> question = generator.generate_question()
        >>> print(question['question'])
        求二次函數 $y = 2x^2 - 12x + 13$ 的極值
        >>> print(question['grade'])
        G10S1

    Note:
        使用逆推生成策略：先選定頂點座標 (h,k) 和開口方向 a，
        再計算 b=-2ah, c=ah²+k，確保所有係數為整數。
    """

    # 難度等級預設參數
    DIFFICULTY_PRESETS = {
        'easy': {
            'a_range': (-2, 2),
            'h_range': (-5, 5),
            'k_range': (-5, 5),
            'description': '簡單：小範圍係數，適合初學'
        },
        'medium': {
            'a_range': (-4, 4),
            'h_range': (-10, 10),
            'k_range': (-10, 10),
            'description': '中等：標準範圍，適合一般練習'
        },
        'hard': {
            'a_range': (-6, 6),
            'h_range': (-15, 15),
            'k_range': (-15, 15),
            'description': '困難：大範圍係數，挑戰計算能力'
        }
    }

    def __init__(self, options: Dict[str, Any] = None):
        """初始化二次函數極值題目生成器"""
        super().__init__(options)
        self.logger = get_logger(self.__class__.__name__)
        self._figure_params = None  # 用於暫存繪圖參數供 get_figure_data_explanation() 使用

        # 配置處理
        options = options or {}

        # 題型比例配置
        question_types = options.get('question_types', {})
        self.global_weight = question_types.get('global_extremum', 50)
        self.interval_weight = question_types.get('interval_extremum', 50)

        # 難度等級配置
        difficulty = options.get('difficulty_level', 'medium')
        if difficulty not in self.DIFFICULTY_PRESETS:
            self.logger.warning(f"未知的難度等級 '{difficulty}'，使用預設值 'medium'")
            difficulty = 'medium'

        preset = self.DIFFICULTY_PRESETS[difficulty]
        self.a_min, self.a_max = preset['a_range']
        self.h_min, self.h_max = preset['h_range']
        self.k_min, self.k_max = preset['k_range']

        # 建立有效的 a 值列表（排除0）
        self.valid_a_values = [
            a for a in range(self.a_min, self.a_max + 1) if a != 0
        ]

        if not self.valid_a_values:
            raise ValueError(f"a的範圍 [{self.a_min}, {self.a_max}] 內沒有有效值（已排除0）")

        self.logger.info(
            f"初始化完成 - 難度: {difficulty}, "
            f"a範圍: {self.valid_a_values}, "
            f"h範圍: [{self.h_min}, {self.h_max}], "
            f"k範圍: [{self.k_min}, {self.k_max}]"
        )

    def _generate_core_question(self) -> Dict[str, Any]:
        """核心二次函數極值題目生成邏輯

        根據題型比例隨機選擇生成全域極值或區間極值題型。
        使用逆推策略確保係數為整數，避免浮點數精度問題。

        Returns:
            Dict[str, Any]: 包含完整題目資訊的字典

        設計原理:
            1. 先隨機選取 a, h, k（頂點式參數）
            2. 逆推計算 b=-2ah, c=ah²+k（一般式係數）
            3. 根據題型生成對應的題目和答案
        """
        # 隨機選取頂點式參數
        a = random.choice(self.valid_a_values)
        h = random.randint(self.h_min, self.h_max)
        k = random.randint(self.k_min, self.k_max)

        # 逆推計算一般式係數
        b = -2 * a * h
        c = a * h * h + k

        # 根據題型比例決定生成哪種題型
        total_weight = self.global_weight + self.interval_weight
        rand_value = random.randint(1, total_weight)

        if rand_value <= self.global_weight:
            # 生成全域極值題型
            return self._generate_global_extremum(a, b, c, h, k)
        else:
            # 生成區間極值題型
            return self._generate_interval_extremum(a, b, c, h, k)

    def _generate_global_extremum(
        self, a: int, b: int, c: int, h: int, k: int
    ) -> Dict[str, Any]:
        """生成全域極值題型

        題目形式：求二次函數 y=ax²+bx+c 的極值
        答案形式：當 x=h 時，y有最[大/小]值 k

        Args:
            a: 二次項係數
            b: 一次項係數
            c: 常數項
            h: 頂點x座標
            k: 頂點y座標（極值）

        Returns:
            Dict[str, Any]: 完整的題目資訊
        """
        # 判斷開口方向和極值類型
        extremum_type = "最小值" if a > 0 else "最大值"

        # 格式化二次函數表達式
        function_expr = self._format_quadratic_function(a, b, c)

        # 生成題目
        question = f"求${function_expr}$的極值"

        # 生成答案
        answer = f"當 $x = {h}$ 時，$y$ 有{extremum_type} ${k}$"

        # 生成詳解
        explanation = self._build_global_explanation(a, b, c, h, k, extremum_type)

        # 保存繪圖參數供 get_figure_data_explanation() 使用
        self._figure_params = {
            'question_type': 'global',
            'a': a,
            'h': h,
            'k': k
        }

        return {
            **self._get_core_content(question, answer, explanation),
            **self._get_standard_metadata()
        }

    def _generate_interval_extremum(
        self, a: int, b: int, c: int, h: int, k: int
    ) -> Dict[str, Any]:
        """生成區間極值題型

        題目形式：求二次函數 y=ax²+bx+c 在 x1≤x≤x2 範圍內的最大與最小值
        答案形式：最大值為 M，最小值為 m

        Args:
            a: 二次項係數
            b: 一次項係數
            c: 常數項
            h: 頂點x座標
            k: 頂點y座標（極值）

        Returns:
            Dict[str, Any]: 完整的題目資訊
        """
        # 生成區間範圍
        x1, x2 = self._generate_interval_range(h)

        # 計算區間極值
        y_max, y_min = self._calculate_interval_extremum(a, b, c, h, k, x1, x2)

        # 格式化二次函數表達式
        function_expr = self._format_quadratic_function(a, b, c)

        # 生成題目
        question = (
            f"求${function_expr}$"
            f"在 ${x1} \\leq x \\leq {x2}$ 範圍內的最大值與最小值"
        )

        # 生成答案
        answer = f"最大值為 ${y_max}$，最小值為 ${y_min}$"

        # 生成詳解
        explanation = self._build_interval_explanation(
            a, b, c, h, k, x1, x2, y_max, y_min
        )

        # 判斷頂點位置並保存繪圖參數
        if x1 <= h <= x2:
            question_type = 'interval_inside'
        elif h < x1:
            question_type = 'interval_outside_left'
        else:
            question_type = 'interval_outside_right'

        # 保存繪圖參數供 get_figure_data_explanation() 使用
        self._figure_params = {
            'question_type': question_type,
            'a': a,
            'h': h,
            'k': k,
            'x1': x1,
            'x2': x2
        }

        return {
            **self._get_core_content(question, answer, explanation),
            **self._get_standard_metadata()
        }

    def _generate_interval_range(self, h: int) -> Tuple[int, int]:
        """生成區間範圍

        70%機率生成包含頂點的區間，30%機率生成不包含頂點的區間。
        確保區間寬度合理，避免計算量過大。

        Args:
            h: 頂點x座標

        Returns:
            (x1, x2): 區間的左右端點

        Note:
            包含頂點：x1 = h-(1~5), x2 = h+(1~5)
            不包含頂點：離頂點2-6單位，區間寬度3-5單位
        """
        # 70% 包含頂點
        if random.random() < 0.7:
            x1 = h - random.randint(1, 5)
            x2 = h + random.randint(1, 5)
        # 30% 不包含頂點
        else:
            offset = random.randint(2, 6)   # 離頂點2-6單位
            width = random.randint(3, 5)    # 區間寬度3-5單位

            if random.choice([True, False]):
                # 左側區間
                x2 = h - offset
                x1 = x2 - width
            else:
                # 右側區間
                x1 = h + offset
                x2 = x1 + width

        return x1, x2

    def _calculate_interval_extremum(
        self, a: int, b: int, c: int, h: int, k: int, x1: int, x2: int
    ) -> Tuple[int, int]:
        """計算區間極值

        根據頂點是否在區間內，判斷極值位置並計算最大最小值。

        Args:
            a: 二次項係數
            b: 一次項係數
            c: 常數項
            h: 頂點x座標
            k: 頂點y座標
            x1: 區間左端點
            x2: 區間右端點

        Returns:
            (y_max, y_min): 區間內的最大值和最小值
        """
        # 計算端點函數值
        y1 = a * x1 * x1 + b * x1 + c
        y2 = a * x2 * x2 + b * x2 + c

        # 判斷頂點是否在區間內
        if x1 <= h <= x2:
            # 頂點在區間內
            if a > 0:
                # 開口向上，頂點為最小值
                y_min = k
                y_max = max(y1, y2)
            else:
                # 開口向下，頂點為最大值
                y_max = k
                y_min = min(y1, y2)
        else:
            # 頂點不在區間內，極值在端點
            y_max = max(y1, y2)
            y_min = min(y1, y2)

        return y_max, y_min

    def _format_quadratic_function(self, a: int, b: int, c: int) -> str:
        """格式化二次函數表達式為LaTeX字串

        處理係數的正負號和特殊情況（係數為0、1、-1）。

        Args:
            a: 二次項係數
            b: 一次項係數
            c: 常數項

        Returns:
            str: LaTeX格式的二次函數表達式

        Example:
            >>> self._format_quadratic_function(2, -12, 13)
            'y = 2x^2 - 12x + 13'
            >>> self._format_quadratic_function(-1, 0, 5)
            'y = -x^2 + 5'
        """
        parts = []

        # 處理二次項 ax²
        if a == 1:
            parts.append("x^2")
        elif a == -1:
            parts.append("-x^2")
        else:
            parts.append(f"{a}x^2")

        # 處理一次項 bx
        if b != 0:
            if b > 0:
                if b == 1:
                    parts.append("+ x")
                else:
                    parts.append(f"+ {b}x")
            else:
                if b == -1:
                    parts.append("- x")
                else:
                    parts.append(f"- {abs(b)}x")

        # 處理常數項 c
        if c != 0:
            if c > 0:
                parts.append(f"+ {c}")
            else:
                parts.append(f"- {abs(c)}")

        return "y = " + " ".join(parts)

    def _format_a_coefficient(self, a: int) -> str:
        """格式化a係數（處理±1的情況）

        Args:
            a: 二次項係數

        Returns:
            str: 格式化後的係數字串

        Example:
            >>> self._format_a_coefficient(1)
            ''
            >>> self._format_a_coefficient(-1)
            '-'
            >>> self._format_a_coefficient(3)
            '3'
        """
        if a == 1:
            return ''
        elif a == -1:
            return '-'
        else:
            return str(a)

    def _format_b_over_a_term(self, b: int, a: int) -> str:
        """格式化 b/a·x 項

        Args:
            b: 一次項係數
            a: 二次項係數

        Returns:
            str: 格式化後的項（含符號）

        Example:
            >>> self._format_b_over_a_term(-12, 2)
            '- 6x'
            >>> self._format_b_over_a_term(18, -3)
            '- 6x'
        """
        b_over_a = b // a
        if b_over_a >= 0:
            return f"+ {b_over_a}x"
        else:
            return f"- {abs(b_over_a)}x"

    def _format_a_with_paren(self, a: int) -> str:
        """格式化a係數（負數加括號）

        Args:
            a: 二次項係數

        Returns:
            str: a < 0 時返回 (a)，否則返回 a

        Example:
            >>> self._format_a_with_paren(3)
            '3'
            >>> self._format_a_with_paren(-3)
            '(-3)'
        """
        if a < 0:
            return f"({a})"
        else:
            return str(a)

    def _get_farther_endpoint(self, x1: int, x2: int, h: int) -> int:
        """取得離頂點較遠的端點

        Args:
            x1: 左端點
            x2: 右端點
            h: 頂點x座標

        Returns:
            int: 離頂點較遠的端點
        """
        dist1 = abs(x1 - h)
        dist2 = abs(x2 - h)
        return x1 if dist1 > dist2 else x2

    def _get_closer_endpoint(self, x1: int, x2: int, h: int) -> int:
        """取得離頂點較近的端點

        Args:
            x1: 左端點
            x2: 右端點
            h: 頂點x座標

        Returns:
            int: 離頂點較近的端點
        """
        dist1 = abs(x1 - h)
        dist2 = abs(x2 - h)
        return x1 if dist1 < dist2 else x2

    def _format_calculation(self, a: int, b: int, c: int, x: int) -> str:
        """格式化計算過程（多行展開格式）

        Args:
            a, b, c: 函數係數
            x: 要代入的x值

        Returns:
            str: 多行展開的計算式字串

        Example:
            >>> self._format_calculation(2, -28, 101, 3)
            '$y(3) = 2 \\times 3^2 - 28 \\times 3 + 101$
            $\\quad = 18 - 84 + 101$
            $\\quad = 35$'
        """
        ax2 = a * x * x
        bx = b * x
        result = ax2 + bx + c

        # 第一行：原式代入
        line1_parts = []

        # ax²項
        if a == 1:
            line1_parts.append(f"{x}^2")
        elif a == -1:
            if x < 0:
                line1_parts.append(f"-({x})^2")
            else:
                line1_parts.append(f"-{x}^2")
        else:
            if x < 0:
                line1_parts.append(f"{a} \\times ({x})^2")
            else:
                line1_parts.append(f"{a} \\times {x}^2")

        # bx項
        if b != 0:
            if b > 0:
                if b == 1:
                    line1_parts.append(f"+ {x}" if x >= 0 else f"+ ({x})")
                else:
                    line1_parts.append(f"+ {b} \\times {x}" if x >= 0 else f"+ {b} \\times ({x})")
            else:  # b < 0
                if b == -1:
                    line1_parts.append(f"- {x}" if x >= 0 else f"- ({x})")
                else:
                    line1_parts.append(f"- {abs(b)} \\times {x}" if x >= 0 else f"- {abs(b)} \\times ({x})")

        # c項
        if c > 0:
            line1_parts.append(f"+ {c}")
        elif c < 0:
            line1_parts.append(f"- {abs(c)}" if c != 0 else "")

        # 第二行：計算結果
        line2_parts = []

        if ax2 >= 0:
            line2_parts.append(str(ax2))
        else:
            line2_parts.append(str(ax2))

        if bx > 0:
            line2_parts.append(f"+ {bx}")
        elif bx < 0:
            line2_parts.append(f"- {abs(bx)}")

        if c > 0:
            line2_parts.append(f"+ {c}")
        elif c < 0:
            line2_parts.append(f"- {abs(c)}")

        # 組合成多行格式
        lines = [
            f"$y({x}) = {' '.join(line1_parts)}$",
            f"$\\quad = {' '.join(line2_parts)}$",
            f"$\\quad = {result}$"
        ]

        return "\\\\[0.3em]".join(lines)

    def _build_global_explanation(
        self, a: int, b: int, c: int, h: int, k: int, extremum_type: str
    ) -> str:
        """建立全域極值的詳解

        使用配方法展示如何將一般式轉換為頂點式，並說明極值判斷。

        Args:
            a: 二次項係數
            b: 一次項係數
            c: 常數項
            h: 頂點x座標
            k: 頂點y座標
            extremum_type: 極值類型（"最大值"或"最小值"）

        Returns:
            str: LaTeX格式的詳解
        """
        function_expr = self._format_quadratic_function(a, b, c)
        a_str = self._format_a_coefficient(a)
        b_over_a_term = self._format_b_over_a_term(b, a)
        a_paren = self._format_a_with_paren(a)
        h_squared = f"({h})^2" if h < 0 else f"{h}^2"
        h_paren = f"({h})" if h < 0 else str(h)
        comparison = '>' if a > 0 else '<'
        direction = '向上' if a > 0 else '向下'

        return EXPLANATION_TEMPLATE_GLOBAL.format(
            function=function_expr.replace('y = ', ''),
            a_str=a_str,
            b_over_a_term=b_over_a_term,
            h_squared=h_squared,
            h_paren=h_paren,
            a_paren=a_paren,
            c=c,
            k=k,
            h=h,
            a=a,
            comparison=comparison,
            direction=direction,
            extremum_type=extremum_type
        )

    def _build_interval_explanation(
        self, a: int, b: int, c: int, h: int, k: int,
        x1: int, x2: int, y_max: int, y_min: int
    ) -> str:
        """建立區間極值的詳解

        展示配方法、頂點判斷、端點計算和極值比較的完整過程。

        Args:
            a, b, c: 二次函數係數
            h, k: 頂點座標
            x1, x2: 區間端點
            y_max, y_min: 區間極值

        Returns:
            str: LaTeX格式的詳解
        """
        function_expr = self._format_quadratic_function(a, b, c)
        a_str = self._format_a_coefficient(a)
        b_over_a_term = self._format_b_over_a_term(b, a)
        a_paren = self._format_a_with_paren(a)
        h_squared = f"({h})^2" if h < 0 else f"{h}^2"
        h_paren = f"({h})" if h < 0 else str(h)
        direction = '向上' if a > 0 else '向下'

        # 判斷頂點是否在區間內
        if x1 <= h <= x2:
            # 頂點在區間內
            vertex_extremum_type = '最小' if a > 0 else '最大'
            farther_x = self._get_farther_endpoint(x1, x2, h)
            calc_farther = self._format_calculation(a, b, c, farther_x)

            return EXPLANATION_TEMPLATE_INTERVAL_INSIDE.format(
                function=function_expr.replace('y = ', ''),
                a_str=a_str,
                b_over_a_term=b_over_a_term,
                h_squared=h_squared,
                h_paren=h_paren,
                a_paren=a_paren,
                c=c,
                k=k,
                h=h,
                x1=x1,
                x2=x2,
                direction=direction,
                vertex_extremum_type=vertex_extremum_type,
                farther_x=farther_x,
                calc_farther=calc_farther,
                y_max=y_max,
                y_min=y_min
            )
        else:
            # 頂點在區間外
            closer_x = self._get_closer_endpoint(x1, x2, h)
            farther_x = self._get_farther_endpoint(x1, x2, h)
            calc_closer = self._format_calculation(a, b, c, closer_x)
            calc_farther = self._format_calculation(a, b, c, farther_x)

            # 判斷頂點在左方或右方
            if h < x1:
                h_comparison = '<'
                boundary = x1
                side = '左'
            else:
                h_comparison = '>'
                boundary = x2
                side = '右'

            # 判斷單調性和極值分配
            if (a > 0 and h < x1) or (a < 0 and h > x2):
                monotonicity = '遞增'
                # 遞增：closer端點為最小值，farther端點為最大值
                extremum_assignment = f"最小值為\n{calc_closer}\n\n最大值為\n{calc_farther}"
            else:
                monotonicity = '遞減'
                # 遞減：closer端點為最大值，farther端點為最小值
                extremum_assignment = f"最大值為\n{calc_closer}\n\n最小值為\n{calc_farther}"

            return EXPLANATION_TEMPLATE_INTERVAL_OUTSIDE.format(
                function=function_expr.replace('y = ', ''),
                a_str=a_str,
                b_over_a_term=b_over_a_term,
                h_squared=h_squared,
                h_paren=h_paren,
                a_paren=a_paren,
                c=c,
                k=k,
                h=h,
                x1=x1,
                x2=x2,
                direction=direction,
                h_comparison=h_comparison,
                boundary=boundary,
                side=side,
                monotonicity=monotonicity,
                extremum_assignment=extremum_assignment
            )

    def _get_fallback_question(self) -> Dict[str, Any]:
        """後備題目，當核心生成失敗時使用

        提供一個簡單的全域極值題型作為後備。

        Returns:
            Dict[str, Any]: 包含完整題目資訊的字典
        """
        question = "求二次函數 $y = x^2 - 4x + 3$ 的極值"
        answer = "當 $x = 2$ 時，$y$ 有最小值 $-1$"
        explanation = """$y = x^2 - 4x + 3$

使用配方法：
$= (x^2 - 4x + 4) - 4 + 3$
$= (x - 2)^2 - 1$

因為 $a = 1 > 0$，開口向上
所以當 $x = 2$ 時，$y$ 有最小值 $-1$"""

        return {
            **self._get_core_content(question, answer, explanation),
            **self._get_standard_metadata()
        }

    def _get_core_content(
        self, question: str, answer: str, explanation: str
    ) -> Dict[str, str]:
        """組合核心內容

        Args:
            question: 題目字串
            answer: 答案字串
            explanation: 詳解字串

        Returns:
            Dict: 包含題目、答案、詳解的字典
        """
        return {
            "question": question,
            "answer": answer,
            "explanation": explanation
        }


    @classmethod
    def get_config_schema(cls) -> Dict[str, Any]:
        """取得配置架構

        定義UI中顯示的配置選項。
        使用難度分級簡化配置，提供簡潔易用的介面。

        Returns:
            Dict: 配置架構定義
        """
        return {
            "question_types": {
                "type": "percentage_group",
                "label": "題型比例",
                "items": {
                    "global_extremum": {"label": "全域極值", "default": 50},
                    "interval_extremum": {"label": "區間極值", "default": 50}
                }
            },
            "difficulty_level": {
                "type": "select",
                "label": "難度等級",
                "default": "medium",
                "options": ["easy", "medium", "hard"],
                "description": "簡單: a∈[-2,2], h,k∈[-5,5] | 中等: a∈[-4,4], h,k∈[-10,10] | 困難: a∈[-6,6], h,k∈[-15,15]"
            }
        }

    def get_question_size(self) -> int:
        """取得題目顯示大小

        Returns:
            int: QuestionSize.SQUARE (1x2)
        """
        return QuestionSize.MEDIUM

    def get_category(self) -> str:
        """取得主類別

        Returns:
            str: "數與式"
        """
        return "數與式"

    def get_subcategory(self) -> str:
        """取得子類別

        Returns:
            str: "二次函數的極值"
        """
        return "二次函數的極值"

    def get_grade(self) -> str:
        """取得年級分類

        Returns:
            str: "G10S1" (高一上學期)
        """
        return "G10S1"

    def get_explanation_figure_position(self) -> str:
        """取得詳解圖形位置

        Returns:
            str: "bottom" (圖形在文字下方，使用全寬)
        """
        return "bottom"

    def get_figure_data_explanation(self) -> dict:
        """取得詳解配圖資料

        框架標準方法，用於返回詳解頁面的圖形配置。
        根據 _figure_params 中保存的參數調用 _generate_schematic_figure() 生成圖形。

        Returns:
            dict: 圖形配置字典 (function_plot 格式)，若無配圖則返回 None
        """
        if self._figure_params is None:
            return None

        return self._generate_schematic_figure(**self._figure_params)

    def _generate_schematic_figure(
        self, question_type: str, a: int, h: int, k: int, x1: int = None, x2: int = None
    ) -> dict:
        """生成示意圖配置（使用增強的 function_plot）

        根據題型生成抽象化的拋物線示意圖，包含分段顏色和標註點。
        使用單一 function_plot 生成器的多曲線功能。

        Args:
            question_type: 題型類型
                - 'global': 全域極值
                - 'interval_inside': 頂點在區間內
                - 'interval_outside_left': 頂點在區間外（左方）
                - 'interval_outside_right': 頂點在區間外（右方）
            a: 二次項係數（決定開口方向）
            h, k: 實際頂點座標（用於標註）
            x1, x2: 區間端點（區間極值題型）

        Returns:
            dict: 圖形配置字典（function_plot 格式）
        """
        # 決定函數形狀（開口向上/向下）
        coeff = 1/3 if a > 0 else -1/3

        # 計算 y 軸範圍
        if a > 0:
            y_range = (-0.5, 3.5)
        else:
            y_range = (-3.5, 0.5)

        # 基礎參數
        base_params = {
            'variant': 'explanation',
            'function_type': 'polynomial',
            'coefficients': [coeff, 0, 0],
            'x_range': (-3, 3),
            'y_range': y_range,
            'figure_width': '9cm',
            'figure_height': '6cm',
            'axis_lines_style': 'none',
            'show_grid': False,
            'show_ticks': False,
            'show_axes_labels': False,
        }

        # 根據題型設定曲線和標註
        if question_type == 'global':
            # 全域極值：全紅色拋物線
            base_params.update({
                'main_plot_domain': (-3, 3),
                'plot_color': 'red',
                'line_thickness': 'very thick',
                'plot_points': [
                    {'x': 0, 'y': 0, 'color': 'red'}
                ],
                'plot_labels': [
                    {'x': 0, 'y': 0, 'text': f'({h}, {k})', 'position': 'above=8pt' if a > 0 else 'below=8pt', 'color': 'red'}
                ]
            })

        elif question_type == 'interval_inside':
            # 頂點在區間內：判斷遠近決定佈局
            dist_left = abs(h - x1)
            dist_right = abs(h - x2)

            if dist_left < dist_right:  # 左近右遠
                plot_x1, plot_x2 = -1, 2
            else:  # 右近左遠
                plot_x1, plot_x2 = -2, 1

            base_params.update({
                'main_plot_domain': (-3, plot_x1),
                'plot_color': 'gray',
                'line_thickness': 'thick',
                'additional_plots': [
                    {'domain': (plot_x1, plot_x2), 'color': 'red', 'thickness': 'very thick'},
                    {'domain': (plot_x2, 3), 'color': 'gray', 'thickness': 'thick'}
                ],
                'plot_points': [
                    {'x': plot_x1, 'y': coeff * plot_x1**2, 'color': 'black'},
                    {'x': 0, 'y': 0, 'color': 'red'},
                    {'x': plot_x2, 'y': coeff * plot_x2**2, 'color': 'black'}
                ],
                'plot_labels': [
                    {'x': plot_x1, 'y': coeff * plot_x1**2, 'text': str(x1), 'position': 'below=5pt'},
                    {'x': 0, 'y': 0, 'text': f'({h}, {k})', 'position': 'above=8pt' if a > 0 else 'below=8pt', 'color': 'red'},
                    {'x': plot_x2, 'y': coeff * plot_x2**2, 'text': str(x2), 'position': 'below=5pt'}
                ]
            })

        elif question_type == 'interval_outside_left':
            # 頂點在左方（頂點在原點，區間在右側）
            base_params.update({
                'main_plot_domain': (-3, 1.0),
                'plot_color': 'gray',
                'line_thickness': 'thick',
                'additional_plots': [
                    {'domain': (1.0, 2.5), 'color': 'red', 'thickness': 'very thick'},
                    {'domain': (2.5, 3), 'color': 'gray', 'thickness': 'thick'}
                ],
                'plot_points': [
                    {'x': 0, 'y': 0, 'color': 'red'},
                    {'x': 1.0, 'y': coeff * 1.0**2, 'color': 'black'},
                    {'x': 2.5, 'y': coeff * 2.5**2, 'color': 'black'}
                ],
                'plot_labels': [
                    {'x': 0, 'y': 0, 'text': f'({h}, {k})', 'position': 'above=8pt' if a > 0 else 'below=8pt', 'color': 'red'},
                    {'x': 1.0, 'y': coeff * 1.0**2, 'text': str(x1), 'position': 'below=5pt'},
                    {'x': 2.5, 'y': coeff * 2.5**2, 'text': str(x2), 'position': 'below=5pt'}
                ]
            })

        elif question_type == 'interval_outside_right':
            # 頂點在右方（頂點在原點，區間在左側）
            base_params.update({
                'main_plot_domain': (-3, -2.5),
                'plot_color': 'gray',
                'line_thickness': 'thick',
                'additional_plots': [
                    {'domain': (-2.5, -1.0), 'color': 'red', 'thickness': 'very thick'},
                    {'domain': (-1.0, 3), 'color': 'gray', 'thickness': 'thick'}
                ],
                'plot_points': [
                    {'x': -2.5, 'y': coeff * 2.5**2, 'color': 'black'},
                    {'x': -1.0, 'y': coeff * 1.0**2, 'color': 'black'},
                    {'x': 0, 'y': 0, 'color': 'red'}
                ],
                'plot_labels': [
                    {'x': -2.5, 'y': coeff * 2.5**2, 'text': str(x1), 'position': 'below=5pt'},
                    {'x': -1.0, 'y': coeff * 1.0**2, 'text': str(x2), 'position': 'below=5pt'},
                    {'x': 0, 'y': 0, 'text': f'({h}, {k})', 'position': 'above=8pt' if a > 0 else 'below=8pt', 'color': 'red'}
                ]
            })

        return {
            'type': 'function_plot',
            'params': base_params
        }

