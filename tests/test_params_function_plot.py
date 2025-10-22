#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
測試 figures.params.function_plot 模塊
測試 FunctionPlotParams 參數模型的驗證邏輯
"""

import unittest
import math
from pydantic import ValidationError

from figures.params.function_plot import FunctionPlotParams


class TestFunctionPlotParamsPolynomial(unittest.TestCase):
    """測試多項式函數參數"""

    def test_valid_polynomial_simple(self):
        """測試有效的簡單多項式參數"""
        params = FunctionPlotParams(
            function_type='polynomial',
            coefficients=[1, -2, 1],  # x^2 - 2x + 1
            x_range=(-2, 4),
            y_range=(-1, 5)
        )
        self.assertEqual(params.function_type, 'polynomial')
        self.assertEqual(params.coefficients, [1, -2, 1])
        self.assertEqual(params.x_range, (-2, 4))
        self.assertEqual(params.y_range, (-1, 5))

    def test_valid_polynomial_cubic(self):
        """測試有效的三次多項式"""
        params = FunctionPlotParams(
            function_type='polynomial',
            coefficients=[1, 0, -3, 2],  # x^3 - 3x + 2
            x_range=(-3, 3),
            y_range=(-5, 5)
        )
        self.assertEqual(len(params.coefficients), 4)

    def test_polynomial_missing_coefficients(self):
        """測試多項式缺少 coefficients 參數"""
        with self.assertRaises(ValidationError) as context:
            FunctionPlotParams(
                function_type='polynomial',
                x_range=(-2, 2),
                y_range=(-2, 2)
            )
        self.assertIn("coefficients", str(context.exception).lower())

    def test_polynomial_empty_coefficients(self):
        """測試多項式 coefficients 為空列表"""
        with self.assertRaises(ValidationError) as context:
            FunctionPlotParams(
                function_type='polynomial',
                coefficients=[],
                x_range=(-2, 2),
                y_range=(-2, 2)
            )
        self.assertIn("coefficients", str(context.exception).lower())

    def test_polynomial_invalid_coefficient_type(self):
        """測試多項式 coefficients 包含非數值"""
        with self.assertRaises(ValidationError):
            FunctionPlotParams(
                function_type='polynomial',
                coefficients=[1, "invalid", 3],  # type: ignore
                x_range=(-2, 2),
                y_range=(-2, 2)
            )


class TestFunctionPlotParamsTrigonometric(unittest.TestCase):
    """測試三角函數參數"""

    def test_valid_sine_function(self):
        """測試有效的正弦函數"""
        params = FunctionPlotParams(
            function_type='trigonometric',
            trig_function='sin',
            x_range=(-6.28, 6.28),
            y_range=(-1.5, 1.5)
        )
        self.assertEqual(params.function_type, 'trigonometric')
        self.assertEqual(params.trig_function, 'sin')
        self.assertEqual(params.amplitude, 1.0)  # 預設值
        self.assertAlmostEqual(params.period, 2 * math.pi, places=5)

    def test_valid_cosine_with_amplitude(self):
        """測試帶振幅的餘弦函數"""
        params = FunctionPlotParams(
            function_type='trigonometric',
            trig_function='cos',
            amplitude=2.5,
            x_range=(-6.28, 6.28),
            y_range=(-3, 3)
        )
        self.assertEqual(params.trig_function, 'cos')
        self.assertEqual(params.amplitude, 2.5)

    def test_valid_tangent_with_period(self):
        """測試帶週期的正切函數"""
        params = FunctionPlotParams(
            function_type='trigonometric',
            trig_function='tan',
            period=math.pi,
            samples=200,
            x_range=(-6.28, 6.28),
            y_range=(-4, 4)
        )
        self.assertEqual(params.trig_function, 'tan')
        self.assertAlmostEqual(params.period, math.pi, places=5)
        self.assertEqual(params.samples, 200)

    def test_trigonometric_missing_function(self):
        """測試三角函數缺少 trig_function 參數"""
        with self.assertRaises(ValidationError) as context:
            FunctionPlotParams(
                function_type='trigonometric',
                x_range=(-6.28, 6.28),
                y_range=(-2, 2)
            )
        self.assertIn("trig_function", str(context.exception).lower())

    def test_trigonometric_invalid_amplitude(self):
        """測試三角函數振幅為非正數"""
        with self.assertRaises(ValidationError) as context:
            FunctionPlotParams(
                function_type='trigonometric',
                trig_function='sin',
                amplitude=0,  # 必須為正數
                x_range=(-6.28, 6.28),
                y_range=(-2, 2)
            )
        self.assertIn("amplitude", str(context.exception).lower())

        with self.assertRaises(ValidationError):
            FunctionPlotParams(
                function_type='trigonometric',
                trig_function='sin',
                amplitude=-1.5,
                x_range=(-6.28, 6.28),
                y_range=(-2, 2)
            )

    def test_trigonometric_invalid_period(self):
        """測試三角函數週期為非正數"""
        with self.assertRaises(ValidationError) as context:
            FunctionPlotParams(
                function_type='trigonometric',
                trig_function='cos',
                period=0,
                x_range=(-6.28, 6.28),
                y_range=(-2, 2)
            )
        self.assertIn("period", str(context.exception).lower())


class TestFunctionPlotParamsExponential(unittest.TestCase):
    """測試指數函數參數"""

    def test_valid_natural_exponential(self):
        """測試有效的自然指數函數 e^x"""
        params = FunctionPlotParams(
            function_type='exponential',
            x_range=(-3, 3),
            y_range=(0, 10)
        )
        self.assertEqual(params.function_type, 'exponential')
        self.assertIsNone(params.base)  # 預設 e

    def test_valid_exponential_with_base(self):
        """測試指定底數的指數函數"""
        params = FunctionPlotParams(
            function_type='exponential',
            base=2.0,
            x_range=(-3, 3),
            y_range=(0, 8)
        )
        self.assertEqual(params.base, 2.0)

    def test_exponential_invalid_base_zero(self):
        """測試指數函數底數為零"""
        with self.assertRaises(ValidationError) as context:
            FunctionPlotParams(
                function_type='exponential',
                base=0,
                x_range=(-3, 3),
                y_range=(0, 8)
            )
        self.assertIn("底數", str(context.exception))

    def test_exponential_invalid_base_negative(self):
        """測試指數函數底數為負數"""
        with self.assertRaises(ValidationError) as context:
            FunctionPlotParams(
                function_type='exponential',
                base=-2.0,
                x_range=(-3, 3),
                y_range=(0, 8)
            )
        self.assertIn("底數", str(context.exception))


class TestFunctionPlotParamsLogarithmic(unittest.TestCase):
    """測試對數函數參數"""

    def test_valid_natural_logarithm(self):
        """測試有效的自然對數函數 ln(x)"""
        params = FunctionPlotParams(
            function_type='logarithmic',
            x_range=(0.001, 10),
            y_range=(-3, 3)
        )
        self.assertEqual(params.function_type, 'logarithmic')
        self.assertIsNone(params.base)  # 預設 e

    def test_valid_logarithm_with_base(self):
        """測試指定底數的對數函數"""
        params = FunctionPlotParams(
            function_type='logarithmic',
            base=10.0,
            x_range=(0.001, 100),
            y_range=(-3, 3)
        )
        self.assertEqual(params.base, 10.0)

    def test_logarithmic_invalid_domain_negative(self):
        """測試對數函數定義域包含負數"""
        with self.assertRaises(ValidationError) as context:
            FunctionPlotParams(
                function_type='logarithmic',
                x_range=(-1, 10),  # 包含負數
                y_range=(-3, 3)
            )
        self.assertIn("對數函數", str(context.exception))
        self.assertIn("0", str(context.exception))

    def test_logarithmic_invalid_domain_zero(self):
        """測試對數函數定義域起點為零"""
        with self.assertRaises(ValidationError) as context:
            FunctionPlotParams(
                function_type='logarithmic',
                x_range=(0, 10),  # 包含零
                y_range=(-3, 3)
            )
        self.assertIn("對數函數", str(context.exception))

    def test_logarithmic_invalid_base(self):
        """測試對數函數底數為非正數"""
        with self.assertRaises(ValidationError):
            FunctionPlotParams(
                function_type='logarithmic',
                base=0,
                x_range=(0.001, 10),
                y_range=(-3, 3)
            )

        with self.assertRaises(ValidationError):
            FunctionPlotParams(
                function_type='logarithmic',
                base=-5.0,
                x_range=(0.001, 10),
                y_range=(-3, 3)
            )


class TestFunctionPlotParamsRangeValidation(unittest.TestCase):
    """測試範圍參數驗證"""

    def test_valid_ranges(self):
        """測試有效的範圍參數"""
        params = FunctionPlotParams(
            function_type='polynomial',
            coefficients=[1, 0],
            x_range=(-5.5, 5.5),
            y_range=(-10.2, 10.2)
        )
        self.assertEqual(params.x_range, (-5.5, 5.5))
        self.assertEqual(params.y_range, (-10.2, 10.2))

    def test_invalid_x_range_reversed(self):
        """測試 x_range 最小值大於最大值"""
        with self.assertRaises(ValidationError) as context:
            FunctionPlotParams(
                function_type='polynomial',
                coefficients=[1],
                x_range=(5, -5),  # 反向
                y_range=(-5, 5)
            )
        self.assertIn("最小值", str(context.exception))

    def test_invalid_y_range_equal(self):
        """測試 y_range 最小值等於最大值"""
        with self.assertRaises(ValidationError):
            FunctionPlotParams(
                function_type='polynomial',
                coefficients=[1],
                x_range=(-5, 5),
                y_range=(3, 3)  # 相等
            )

    def test_invalid_range_wrong_length(self):
        """測試範圍參數長度錯誤"""
        with self.assertRaises(ValidationError):
            FunctionPlotParams(
                function_type='polynomial',
                coefficients=[1],
                x_range=(-5, 0, 5),  # 三個值 # type: ignore
                y_range=(-5, 5)
            )


class TestFunctionPlotParamsPlotOptions(unittest.TestCase):
    """測試繪圖選項參數"""

    def test_valid_samples_range(self):
        """測試有效的採樣點數量"""
        params = FunctionPlotParams(
            function_type='polynomial',
            coefficients=[1, 0],
            samples=50,
            x_range=(-5, 5),
            y_range=(-5, 5)
        )
        self.assertEqual(params.samples, 50)

        params_high = FunctionPlotParams(
            function_type='polynomial',
            coefficients=[1, 0],
            samples=300,
            x_range=(-5, 5),
            y_range=(-5, 5)
        )
        self.assertEqual(params_high.samples, 300)

    def test_invalid_samples_too_low(self):
        """測試採樣點數量過低"""
        with self.assertRaises(ValidationError):
            FunctionPlotParams(
                function_type='polynomial',
                coefficients=[1, 0],
                samples=10,  # < 20
                x_range=(-5, 5),
                y_range=(-5, 5)
            )

    def test_invalid_samples_too_high(self):
        """測試採樣點數量過高"""
        with self.assertRaises(ValidationError):
            FunctionPlotParams(
                function_type='polynomial',
                coefficients=[1, 0],
                samples=600,  # > 500
                x_range=(-5, 5),
                y_range=(-5, 5)
            )

    def test_valid_color_options(self):
        """測試有效的顏色選項"""
        params = FunctionPlotParams(
            function_type='polynomial',
            coefficients=[1],
            plot_color='red',
            y_intercept_color='blue',
            x_range=(-5, 5),
            y_range=(-5, 5)
        )
        self.assertEqual(params.plot_color, 'red')
        self.assertEqual(params.y_intercept_color, 'blue')

    def test_valid_line_thickness(self):
        """測試有效的線條粗細"""
        params = FunctionPlotParams(
            function_type='polynomial',
            coefficients=[1],
            line_thickness='very thick',
            x_range=(-5, 5),
            y_range=(-5, 5)
        )
        self.assertEqual(params.line_thickness, 'very thick')

    def test_valid_boolean_options(self):
        """測試布林選項"""
        params = FunctionPlotParams(
            function_type='polynomial',
            coefficients=[1, 2],
            show_grid=False,
            show_axes_labels=False,
            show_y_intercept=True,
            x_range=(-5, 5),
            y_range=(-5, 5)
        )
        self.assertFalse(params.show_grid)
        self.assertFalse(params.show_axes_labels)
        self.assertTrue(params.show_y_intercept)


class TestFunctionPlotParamsDefaults(unittest.TestCase):
    """測試預設值"""

    def test_polynomial_defaults(self):
        """測試多項式的預設值"""
        params = FunctionPlotParams(
            function_type='polynomial',
            coefficients=[1, 0, 0]
        )
        self.assertEqual(params.x_range, (-5, 5))
        self.assertEqual(params.y_range, (-5, 5))
        self.assertEqual(params.samples, 100)
        self.assertEqual(params.plot_color, 'blue')
        self.assertEqual(params.line_thickness, 'thick')
        self.assertTrue(params.show_grid)
        self.assertTrue(params.show_axes_labels)
        self.assertFalse(params.show_y_intercept)

    def test_trigonometric_defaults(self):
        """測試三角函數的預設值"""
        params = FunctionPlotParams(
            function_type='trigonometric',
            trig_function='sin'
        )
        self.assertEqual(params.amplitude, 1.0)
        self.assertAlmostEqual(params.period, 2 * math.pi, places=5)

    def test_exponential_defaults(self):
        """測試指數函數的預設值"""
        params = FunctionPlotParams(
            function_type='exponential'
        )
        self.assertIsNone(params.base)  # 預設 e


if __name__ == "__main__":
    unittest.main()
