#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 函數圖形生成器

本模組提供萬用函數圖形生成功能，支援多項式、指數、對數、三角函數
等常見高中數學函數的圖形繪製。使用 PGFPlots 生成高品質圖形，
自動處理不連續點和漸近線。

支援的函數類型：
- polynomial: 多項式函數（如 x^2 - 2x + 1）
- exponential: 指數函數（如 2^x, e^x）
- logarithmic: 對數函數（如 log₂(x), ln(x)）
- trigonometric: 三角函數（如 sin(x), cos(x), tan(x)）

主要特點：
- 使用 PGFPlots 繪製，自動處理 tan 函數的不連續點
- 支援振幅、週期等高級三角函數參數
- 可選的 y 截距標記功能（含安全檢查）
- 完整的 Pydantic 參數驗證

Example:
    生成二次函數圖形::

        generator = FunctionPlotGenerator()
        params = {
            'function_type': 'polynomial',
            'coefficients': [1, -2, 1],  # x^2 - 2x + 1
            'x_range': (-2, 4),
            'y_range': (-1, 5),
            'show_y_intercept': True
        }
        tikz_code = generator.generate_tikz(params)

    生成三角函數圖形::

        params = {
            'function_type': 'trigonometric',
            'trig_function': 'sin',
            'amplitude': 2.0,
            'period': 6.28,
            'x_range': (-6.28, 6.28),
            'y_range': (-2.5, 2.5)
        }
        tikz_code = generator.generate_tikz(params)

Note:
    - tan 函數自動使用 unbounded coords=jump 處理不連續點
    - 對數函數定義域應從 0.001 開始避免無效值
    - y 截距標記包含安全檢查，確保截距在繪圖範圍內
"""

from typing import Dict, Any, Tuple, List
from pydantic import ValidationError
import math

from utils import get_logger, global_config
from .base import FigureGenerator
from .params.function_plot import FunctionPlotParams
from . import register_figure_generator

logger = get_logger(__name__)


@register_figure_generator
class FunctionPlotGenerator(FigureGenerator):
    """函數圖形生成器

    萬用函數圖形生成器，支援多種常見高中數學函數類型。
    使用 PGFPlots 繪製高品質函數圖形，自動處理邊界條件。

    支援的功能：
    - 4 種函數類型（polynomial/exponential/logarithmic/trigonometric）
    - 自動處理 tan 函數不連續點
    - 振幅、週期控制（三角函數）
    - y 截距標記（可選）
    - 網格和座標軸標籤顯示控制

    Attributes:
        logger: 模組日誌記錄器
        config: 全域配置物件

    Example:
        >>> generator = FunctionPlotGenerator()
        >>> params = {
        ...     'function_type': 'polynomial',
        ...     'coefficients': [1, 0, -1],
        ...     'x_range': (-3, 3),
        ...     'y_range': (-2, 10)
        ... }
        >>> tikz_code = generator.generate_tikz(params)
        >>> 'begin{axis}' in tikz_code
        True

    Note:
        此生成器依賴 LaTeX 模板中已配置的 PGFPlots 套件。
        所有參數驗證通過 FunctionPlotParams 模型進行。
    """

    @classmethod
    def get_name(cls) -> str:
        """獲取圖形類型唯一標識符"""
        return 'function_plot'

    def generate_tikz(self, params: Dict[str, Any]) -> str:
        """生成函數圖形 TikZ 代碼

        根據提供的參數生成函數圖形的 PGFPlots 代碼，包含完整的
        axis 環境和 addplot 命令。

        Args:
            params (Dict[str, Any]): 函數參數字典，詳見 FunctionPlotParams

        Returns:
            str: TikZ 圖形內容，包含 tikzpicture 和 axis 環境

        Raises:
            ValidationError: 如果參數驗證失敗
            ValueError: 如果函數類型不支援或參數無效

        Example:
            >>> generator = FunctionPlotGenerator()
            >>> params = {'function_type': 'exponential', 'base': 2.0}
            >>> result = generator.generate_tikz(params)
            >>> 'addplot' in result
            True

        Note:
            生成的代碼使用 PGFPlots 的標準語法。
            tan 函數會自動添加 unbounded coords=jump 選項。
        """
        # 參數驗證
        try:
            validated_params = FunctionPlotParams(**params)
            logger.debug(
                f"函數圖形參數驗證成功: type={validated_params.function_type}, "
                f"x_range={validated_params.x_range}, y_range={validated_params.y_range}"
            )
        except ValidationError as e:
            logger.error(f"函數圖形參數驗證失敗: {str(e)}")
            raise

        # 生成函數表達式
        expression = self._generate_expression(validated_params)
        logger.debug(f"生成函數表達式: {expression}")

        # 構建 axis 選項
        axis_options = self._build_axis_options(validated_params)

        # 構建 addplot 選項
        plot_options = self._build_plot_options(validated_params)

        # 生成 TikZ 代碼
        tikz_content = "% 函數圖形\n"
        tikz_content += f"\\begin{{axis}}[{axis_options}]\n"
        tikz_content += f"  \\addplot[{plot_options}] {{{expression}}};\n"

        # 添加額外曲線
        if validated_params.additional_plots:
            for i, plot_spec in enumerate(validated_params.additional_plots):
                domain = plot_spec['domain']
                color = plot_spec.get('color', 'blue')
                thickness = plot_spec.get('thickness', 'thick')
                samples = plot_spec.get('samples', validated_params.samples)

                # 使用指定表達式或主函數
                expr = plot_spec.get('expression', expression)

                add_options = f"{color}, {thickness}, domain={domain[0]:.6g}:{domain[1]:.6g}, samples={samples}"
                tikz_content += f"  \\addplot[{add_options}] {{{expr}}};\n"

        # 添加 y 截距標記（如果需要）
        if validated_params.show_y_intercept:
            intercept_code = self._add_y_intercept_marker(validated_params, expression)
            if intercept_code:
                tikz_content += intercept_code

        # 添加標記點
        if validated_params.plot_points:
            tikz_content += "\n  % 標記點\n"
            for point in validated_params.plot_points:
                x, y = point['x'], point['y']
                color = point.get('color', 'black')
                size = point.get('size', '1.5pt')
                tikz_content += f"  \\node[circle, fill={color}, inner sep={size}] at (axis cs:{x},{y}) {{}};\n"

        # 添加標籤
        if validated_params.plot_labels:
            tikz_content += "\n  % 標籤\n"
            for label in validated_params.plot_labels:
                x, y = label['x'], label['y']
                text = label['text']
                pos = label.get('position', 'above')
                color = label.get('color', 'black')
                math_mode = label.get('math_mode', True)

                # 根據 math_mode 決定是否包裹 $...$
                label_text = f"${text}$" if math_mode else text
                tikz_content += f"  \\node[{pos}, color={color}] at (axis cs:{x},{y}) {{{label_text}}};\n"

        tikz_content += "\\end{axis}\n"

        logger.debug(f"生成函數圖形 TikZ 代碼完成: {validated_params.function_type}")

        return tikz_content

    def _generate_expression(self, params: FunctionPlotParams) -> str:
        """生成函數數學表達式

        根據函數類型生成 PGFPlots 可用的數學表達式字串。

        Args:
            params (FunctionPlotParams): 驗證後的參數模型

        Returns:
            str: PGFPlots 數學表達式

        Raises:
            ValueError: 如果函數類型不支援

        Example:
            多項式: x^2 - 2*x + 1
            指數: 2^x
            對數: ln(x)
            三角: 2*sin(deg(x))
        """
        if params.function_type == 'polynomial':
            return self._polynomial_expression(params)
        elif params.function_type == 'exponential':
            return self._exponential_expression(params)
        elif params.function_type == 'logarithmic':
            return self._logarithmic_expression(params)
        elif params.function_type == 'trigonometric':
            return self._trigonometric_expression(params)
        else:
            raise ValueError(f"不支援的函數類型: {params.function_type}")

    def _polynomial_expression(self, params: FunctionPlotParams) -> str:
        """生成多項式表達式

        將係數列表轉換為 PGFPlots 多項式表達式。
        係數按降冪排列: [a_n, ..., a_1, a_0] → a_n*x^n + ... + a_1*x + a_0

        Args:
            params (FunctionPlotParams): 參數模型（必須包含 coefficients）

        Returns:
            str: 多項式表達式

        Example:
            [1, -2, 1] → x^2 - 2*x + 1
            [1, 0, 0, -8] → x^3 - 8
            [2, 3] → 2*x + 3
            [5] → 5

        Note:
            - 自動處理係數為 0 的項（省略）
            - 自動處理係數為 1/-1 的特殊情況
            - 自動處理正負號（避免 +- 或 --）
            - 常數項單獨處理
        """
        coefficients = params.coefficients
        if not coefficients:
            raise ValueError("多項式係數不能為空")

        degree = len(coefficients) - 1
        terms = []

        for i, coef in enumerate(coefficients):
            if coef == 0:
                continue  # 跳過係數為 0 的項

            power = degree - i

            # 格式化係數（整數不顯示小數點）
            coef_str = str(int(coef)) if coef == int(coef) else str(coef)

            # 構建項
            if power == 0:
                # 常數項
                term = coef_str
            elif power == 1:
                # 一次項
                if coef == 1:
                    term = "x"
                elif coef == -1:
                    term = "-x"
                else:
                    term = f"{coef_str}*x"
            else:
                # 高次項
                if coef == 1:
                    term = f"x^{power}"
                elif coef == -1:
                    term = f"-x^{power}"
                else:
                    term = f"{coef_str}*x^{power}"

            terms.append(term)

        if not terms:
            return "0"  # 所有係數都是 0

        # 組合項，處理正負號
        expression = terms[0]
        for term in terms[1:]:
            if term.startswith('-'):
                expression += f" - {term[1:]}"  # 移除負號，用 - 連接
            else:
                expression += f" + {term}"

        return expression

    def _exponential_expression(self, params: FunctionPlotParams) -> str:
        """生成指數函數表達式

        生成形如 a^x 或 e^x 的指數函數表達式。

        Args:
            params (FunctionPlotParams): 參數模型

        Returns:
            str: 指數函數表達式

        Example:
            base=2 → 2^x
            base=None → exp(x)  # 自然指數 e^x
            base=10 → 10^x
        """
        if params.base is None:
            # 自然指數 e^x
            return "exp(x)"
        else:
            # 指定底數
            return f"{params.base}^x"

    def _logarithmic_expression(self, params: FunctionPlotParams) -> str:
        """生成對數函數表達式

        生成形如 log_a(x) 或 ln(x) 的對數函數表達式。

        Args:
            params (FunctionPlotParams): 參數模型

        Returns:
            str: 對數函數表達式

        Example:
            base=None → ln(x)  # 自然對數
            base=2 → ln(x)/ln(2)  # log₂(x) 使用換底公式
            base=10 → log10(x)  # 常用對數
        """
        if params.base is None:
            # 自然對數
            return "ln(x)"
        elif params.base == 10:
            # 常用對數
            return "log10(x)"
        else:
            # 其他底數，使用換底公式: log_a(x) = ln(x) / ln(a)
            return f"ln(x)/ln({params.base})"

    def _trigonometric_expression(self, params: FunctionPlotParams) -> str:
        """生成三角函數表達式

        生成支援振幅和週期的三角函數表達式。
        形式: A * trig((2π/T) * x)

        Args:
            params (FunctionPlotParams): 參數模型（必須包含 trig_function）

        Returns:
            str: 三角函數表達式

        Example:
            sin, A=1, T=2π → sin(x)
            cos, A=2, T=π → 2*cos(2*x)
            tan, A=1, T=2π → tan(x)

        Note:
            - 使用弧度模式（axis 選項中會添加 trig format=rad）
            - 週期調整通過頻率係數實現: freq = 2π/T
            - 振幅直接乘在函數前
        """
        trig_func = params.trig_function
        amplitude = params.amplitude or 1.0
        period = params.period or (2 * math.pi)

        # 計算頻率係數: ω = 2π/T
        frequency = (2 * math.pi) / period

        # 構建內部表達式
        if abs(frequency - 1.0) < 1e-6:
            # 標準週期
            inner = "x"
        else:
            inner = f"{frequency:.6g}*x"

        # 構建三角函數調用（使用弧度）
        trig_call = f"{trig_func}({inner})"

        # 添加振幅
        if abs(amplitude - 1.0) < 1e-6:
            expression = trig_call
        else:
            expression = f"{amplitude:.6g}*{trig_call}"

        return expression

    def _build_axis_options(self, params: FunctionPlotParams) -> str:
        """構建 PGFPlots axis 環境選項

        生成 axis 環境的配置選項字串。

        Args:
            params (FunctionPlotParams): 參數模型

        Returns:
            str: 逗號分隔的選項字串

        Example:
            "xmin=-5, xmax=5, ymin=-5, ymax=5, grid=major, xlabel=$x$, ylabel=$y$"
        """
        xmin, xmax = params.x_range
        ymin, ymax = params.y_range

        options = [
            f"xmin={xmin:.6g}, xmax={xmax:.6g}",
            f"ymin={ymin:.6g}, ymax={ymax:.6g}",
            f"axis lines={params.axis_lines_style}",
            f"width={params.figure_width}, height={params.figure_height}"
        ]

        # 刻度控制
        if not params.show_ticks:
            options.append("xtick=\\empty, ytick=\\empty")

        # 網格
        if params.show_grid:
            options.append("grid=major")

        # 座標軸標籤
        if params.show_axes_labels:
            options.append("xlabel=$x$, ylabel=$y$")

        # 三角函數使用弧度模式
        if params.function_type == 'trigonometric':
            options.append("trig format=rad")
            # tan 函數需要特殊處理不連續點
            if params.trig_function == 'tan':
                options.append("unbounded coords=jump")

        return ", ".join(options)

    def _build_plot_options(self, params: FunctionPlotParams, domain: Tuple[float, float] = None) -> str:
        """構建 PGFPlots addplot 命令選項

        生成 addplot 命令的配置選項字串。

        Args:
            params (FunctionPlotParams): 參數模型
            domain (Tuple[float, float], optional): 繪製範圍，None 則使用 x_range

        Returns:
            str: 逗號分隔的選項字串

        Example:
            "blue, thick, domain=-5:5, samples=100"
        """
        # 決定繪製範圍
        if domain:
            xmin, xmax = domain
        elif params.main_plot_domain:
            xmin, xmax = params.main_plot_domain
        else:
            xmin, xmax = params.x_range

        options = [
            params.plot_color,
            params.line_thickness,
            f"domain={xmin:.6g}:{xmax:.6g}",
            f"samples={params.samples}"
        ]

        return ", ".join(options)

    def _add_y_intercept_marker(
        self,
        params: FunctionPlotParams,
        expression: str
    ) -> str:
        """添加 y 截距標記點

        在 x=0 處標記 y 截距，包含安全檢查確保截距在繪圖範圍內。

        Args:
            params (FunctionPlotParams): 參數模型
            expression (str): 函數表達式

        Returns:
            str: y 截距標記的 TikZ 代碼，如果截距不在範圍內則返回空字串

        Example:
            多項式 [1, -2, 1]（即 x^2-2x+1）在 x=0 時 y=1
            → "    \\addplot[red, only marks, mark=*] coordinates {(0, 1)};\n"

        Note:
            - 檢查 x=0 是否在 x_range 內
            - 檢查計算出的 y 值是否在 y_range 內
            - 對數函數通常不會有 x=0 的截距（定義域限制）
        """
        xmin, xmax = params.x_range
        ymin, ymax = params.y_range

        # 安全檢查 1: x=0 必須在定義域內
        if xmin > 0 or xmax < 0:
            logger.debug("x=0 不在定義域內，跳過 y 截距標記")
            return ""

        # 計算 y 截距值
        try:
            y_intercept = self._calculate_y_intercept(params)
        except (ValueError, ZeroDivisionError) as e:
            logger.warning(f"計算 y 截距失敗: {e}")
            return ""

        # 安全檢查 2: y 截距必須在值域內
        if y_intercept < ymin or y_intercept > ymax:
            logger.debug(
                f"y 截距 {y_intercept:.3f} 超出值域範圍 [{ymin}, {ymax}]，跳過標記"
            )
            return ""

        # 生成標記點代碼
        marker_code = (
            f"    \\addplot[{params.y_intercept_color}, only marks, mark=*] "
            f"coordinates {{(0, {y_intercept:.6g})}};\n"
        )

        logger.debug(f"添加 y 截距標記: (0, {y_intercept:.6g})")
        return marker_code

    def _calculate_y_intercept(self, params: FunctionPlotParams) -> float:
        """計算函數在 x=0 處的 y 值

        Args:
            params (FunctionPlotParams): 參數模型

        Returns:
            float: y 截距值

        Raises:
            ValueError: 如果函數在 x=0 處未定義（如 log(0)）
            ZeroDivisionError: 如果計算過程發生除零錯誤

        Example:
            polynomial [1, -2, 1] → 1
            exponential base=2 → 1
            logarithmic → ValueError（x=0 未定義）
        """
        if params.function_type == 'polynomial':
            # 多項式: y = a_n*0^n + ... + a_0 = a_0（常數項）
            return params.coefficients[-1]

        elif params.function_type == 'exponential':
            # 指數: y = a^0 = 1（任何底數的 0 次方都是 1）
            return 1.0

        elif params.function_type == 'logarithmic':
            # 對數: log(0) 未定義
            raise ValueError("對數函數在 x=0 處未定義")

        elif params.function_type == 'trigonometric':
            # 三角函數在 x=0 處的值
            amplitude = params.amplitude or 1.0
            if params.trig_function == 'sin':
                return 0.0  # sin(0) = 0
            elif params.trig_function == 'cos':
                return amplitude  # cos(0) = 1
            elif params.trig_function == 'tan':
                return 0.0  # tan(0) = 0

        raise ValueError(f"不支援的函數類型: {params.function_type}")
