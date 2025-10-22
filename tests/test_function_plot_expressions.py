#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
測試 figures.function_plot 模塊的表達式生成方法
"""

import unittest
import math

from figures import get_figure_generator
from figures.params.function_plot import FunctionPlotParams


class TestPolynomialExpression(unittest.TestCase):
    """測試多項式表達式生成"""

    def setUp(self):
        """設置測試環境"""
        FuncGen = get_figure_generator('function_plot')
        self.generator = FuncGen()

    def test_quadratic_simple(self):
        """測試簡單二次函數: x^2 - 2x + 1"""
        params = FunctionPlotParams(
            function_type='polynomial',
            coefficients=[1, -2, 1]
        )
        expr = self.generator._polynomial_expression(params)
        self.assertEqual(expr, "x^2 - 2*x + 1")

    def test_cubic_with_zero_coefficient(self):
        """測試包含零係數的三次函數: x^3 - 8"""
        params = FunctionPlotParams(
            function_type='polynomial',
            coefficients=[1, 0, 0, -8]
        )
        expr = self.generator._polynomial_expression(params)
        self.assertEqual(expr, "x^3 - 8")

    def test_linear_positive(self):
        """測試一次函數: 2x + 3"""
        params = FunctionPlotParams(
            function_type='polynomial',
            coefficients=[2, 3]
        )
        expr = self.generator._polynomial_expression(params)
        self.assertEqual(expr, "2*x + 3")

    def test_linear_negative_coefficient(self):
        """測試負係數一次函數: -x + 5"""
        params = FunctionPlotParams(
            function_type='polynomial',
            coefficients=[-1, 5]
        )
        expr = self.generator._polynomial_expression(params)
        self.assertEqual(expr, "-x + 5")

    def test_constant(self):
        """測試常數函數: 5"""
        params = FunctionPlotParams(
            function_type='polynomial',
            coefficients=[5]
        )
        expr = self.generator._polynomial_expression(params)
        self.assertEqual(expr, "5")

    def test_coefficient_one(self):
        """測試係數為1的特殊情況: x^2 + x + 1"""
        params = FunctionPlotParams(
            function_type='polynomial',
            coefficients=[1, 1, 1]
        )
        expr = self.generator._polynomial_expression(params)
        self.assertEqual(expr, "x^2 + x + 1")

    def test_all_zero_coefficients(self):
        """測試所有係數為零"""
        params = FunctionPlotParams(
            function_type='polynomial',
            coefficients=[0, 0, 0]
        )
        expr = self.generator._polynomial_expression(params)
        self.assertEqual(expr, "0")


class TestExponentialExpression(unittest.TestCase):
    """測試指數函數表達式生成"""

    def setUp(self):
        """設置測試環境"""
        FuncGen = get_figure_generator('function_plot')
        self.generator = FuncGen()

    def test_natural_exponential(self):
        """測試自然指數函數: e^x"""
        params = FunctionPlotParams(
            function_type='exponential'
        )
        expr = self.generator._exponential_expression(params)
        self.assertEqual(expr, "exp(x)")

    def test_base_2(self):
        """測試底數為2的指數函數: 2^x"""
        params = FunctionPlotParams(
            function_type='exponential',
            base=2.0
        )
        expr = self.generator._exponential_expression(params)
        self.assertEqual(expr, "2.0^x")

    def test_base_10(self):
        """測試底數為10的指數函數: 10^x"""
        params = FunctionPlotParams(
            function_type='exponential',
            base=10.0
        )
        expr = self.generator._exponential_expression(params)
        self.assertEqual(expr, "10.0^x")


class TestLogarithmicExpression(unittest.TestCase):
    """測試對數函數表達式生成"""

    def setUp(self):
        """設置測試環境"""
        FuncGen = get_figure_generator('function_plot')
        self.generator = FuncGen()

    def test_natural_logarithm(self):
        """測試自然對數: ln(x)"""
        params = FunctionPlotParams(
            function_type='logarithmic',
            x_range=(0.001, 10)
        )
        expr = self.generator._logarithmic_expression(params)
        self.assertEqual(expr, "ln(x)")

    def test_base_10_logarithm(self):
        """測試常用對數: log₁₀(x)"""
        params = FunctionPlotParams(
            function_type='logarithmic',
            base=10.0,
            x_range=(0.001, 100)
        )
        expr = self.generator._logarithmic_expression(params)
        self.assertEqual(expr, "log10(x)")

    def test_base_2_logarithm(self):
        """測試以2為底的對數: log₂(x)"""
        params = FunctionPlotParams(
            function_type='logarithmic',
            base=2.0,
            x_range=(0.001, 10)
        )
        expr = self.generator._logarithmic_expression(params)
        self.assertEqual(expr, "ln(x)/ln(2.0)")


class TestTrigonometricExpression(unittest.TestCase):
    """測試三角函數表達式生成"""

    def setUp(self):
        """設置測試環境"""
        FuncGen = get_figure_generator('function_plot')
        self.generator = FuncGen()

    def test_sine_standard(self):
        """測試標準正弦函數: sin(x)"""
        params = FunctionPlotParams(
            function_type='trigonometric',
            trig_function='sin'
        )
        expr = self.generator._trigonometric_expression(params)
        self.assertEqual(expr, "sin(x)")

    def test_cosine_standard(self):
        """測試標準餘弦函數: cos(x)"""
        params = FunctionPlotParams(
            function_type='trigonometric',
            trig_function='cos'
        )
        expr = self.generator._trigonometric_expression(params)
        self.assertEqual(expr, "cos(x)")

    def test_tangent_standard(self):
        """測試標準正切函數: tan(x)"""
        params = FunctionPlotParams(
            function_type='trigonometric',
            trig_function='tan'
        )
        expr = self.generator._trigonometric_expression(params)
        self.assertEqual(expr, "tan(x)")

    def test_sine_with_amplitude(self):
        """測試帶振幅的正弦函數: 2*sin(x)"""
        params = FunctionPlotParams(
            function_type='trigonometric',
            trig_function='sin',
            amplitude=2.0
        )
        expr = self.generator._trigonometric_expression(params)
        self.assertEqual(expr, "2*sin(x)")

    def test_sine_with_period(self):
        """測試帶週期的正弦函數: sin(2x)"""
        params = FunctionPlotParams(
            function_type='trigonometric',
            trig_function='sin',
            period=math.pi  # 週期為π，頻率為2
        )
        expr = self.generator._trigonometric_expression(params)
        # 頻率 = 2π/π = 2
        self.assertIn("2*x", expr)
        self.assertIn("sin(", expr)

    def test_sine_with_amplitude_and_period(self):
        """測試帶振幅和週期的正弦函數: 3*sin(2x)"""
        params = FunctionPlotParams(
            function_type='trigonometric',
            trig_function='sin',
            amplitude=3.0,
            period=math.pi
        )
        expr = self.generator._trigonometric_expression(params)
        self.assertIn("3*sin(2*x)", expr)


class TestYInterceptCalculation(unittest.TestCase):
    """測試 y 截距計算"""

    def setUp(self):
        """設置測試環境"""
        FuncGen = get_figure_generator('function_plot')
        self.generator = FuncGen()

    def test_polynomial_intercept(self):
        """測試多項式 y 截距: x^2 - 2x + 1 在 x=0 時 y=1"""
        params = FunctionPlotParams(
            function_type='polynomial',
            coefficients=[1, -2, 1]
        )
        intercept = self.generator._calculate_y_intercept(params)
        self.assertEqual(intercept, 1)

    def test_exponential_intercept(self):
        """測試指數函數 y 截距: 2^x 在 x=0 時 y=1"""
        params = FunctionPlotParams(
            function_type='exponential',
            base=2.0
        )
        intercept = self.generator._calculate_y_intercept(params)
        self.assertEqual(intercept, 1.0)

    def test_logarithmic_undefined(self):
        """測試對數函數 y 截距未定義"""
        params = FunctionPlotParams(
            function_type='logarithmic',
            x_range=(0.001, 10)
        )
        with self.assertRaises(ValueError) as context:
            self.generator._calculate_y_intercept(params)
        self.assertIn("未定義", str(context.exception))

    def test_sine_intercept(self):
        """測試正弦函數 y 截距: sin(0) = 0"""
        params = FunctionPlotParams(
            function_type='trigonometric',
            trig_function='sin'
        )
        intercept = self.generator._calculate_y_intercept(params)
        self.assertEqual(intercept, 0.0)

    def test_cosine_intercept(self):
        """測試餘弦函數 y 截距: cos(0) = 1"""
        params = FunctionPlotParams(
            function_type='trigonometric',
            trig_function='cos',
            amplitude=1.0
        )
        intercept = self.generator._calculate_y_intercept(params)
        self.assertEqual(intercept, 1.0)

    def test_cosine_with_amplitude(self):
        """測試帶振幅的餘弦函數 y 截距: 2*cos(0) = 2"""
        params = FunctionPlotParams(
            function_type='trigonometric',
            trig_function='cos',
            amplitude=2.0
        )
        intercept = self.generator._calculate_y_intercept(params)
        self.assertEqual(intercept, 2.0)

    def test_tangent_intercept(self):
        """測試正切函數 y 截距: tan(0) = 0"""
        params = FunctionPlotParams(
            function_type='trigonometric',
            trig_function='tan'
        )
        intercept = self.generator._calculate_y_intercept(params)
        self.assertEqual(intercept, 0.0)


if __name__ == "__main__":
    unittest.main()
