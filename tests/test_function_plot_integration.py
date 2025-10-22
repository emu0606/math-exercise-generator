#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
測試 figures.function_plot 模塊的整合功能
測試完整的 TikZ 代碼生成
"""

import unittest

from figures import get_figure_generator


class TestFunctionPlotIntegration(unittest.TestCase):
    """測試函數圖形生成器整合功能"""

    def setUp(self):
        """設置測試環境"""
        FuncGen = get_figure_generator('function_plot')
        self.generator = FuncGen()

    def test_polynomial_basic_tikz(self):
        """測試多項式函數生成完整 TikZ 代碼"""
        params = {
            'function_type': 'polynomial',
            'coefficients': [1, -2, 1],
            'x_range': (-2, 4),
            'y_range': (-1, 5)
        }

        tikz = self.generator.generate_tikz(params)

        # 檢查基本結構
        self.assertIn('\\begin{tikzpicture}', tikz)
        self.assertIn('\\end{tikzpicture}', tikz)
        self.assertIn('\\begin{axis}', tikz)
        self.assertIn('\\end{axis}', tikz)

        # 檢查函數表達式
        self.assertIn('x^2 - 2*x + 1', tikz)

        # 檢查範圍設定
        self.assertIn('xmin=-2', tikz)
        self.assertIn('xmax=4', tikz)
        self.assertIn('ymin=-1', tikz)
        self.assertIn('ymax=5', tikz)

    def test_exponential_tikz(self):
        """測試指數函數生成 TikZ 代碼"""
        params = {
            'function_type': 'exponential',
            'base': 2.0,
            'x_range': (-3, 3),
            'y_range': (0, 8)
        }

        tikz = self.generator.generate_tikz(params)

        self.assertIn('\\addplot', tikz)
        self.assertIn('2.0^x', tikz)
        self.assertIn('domain=-3:3', tikz)

    def test_logarithmic_tikz(self):
        """測試對數函數生成 TikZ 代碼"""
        params = {
            'function_type': 'logarithmic',
            'base': 10.0,
            'x_range': (0.001, 100),
            'y_range': (-3, 3)
        }

        tikz = self.generator.generate_tikz(params)

        self.assertIn('log10(x)', tikz)
        self.assertIn('xmin=0.001', tikz)

    def test_trigonometric_sine_tikz(self):
        """測試正弦函數生成 TikZ 代碼"""
        params = {
            'function_type': 'trigonometric',
            'trig_function': 'sin',
            'x_range': (-6.28, 6.28),
            'y_range': (-1.5, 1.5)
        }

        tikz = self.generator.generate_tikz(params)

        self.assertIn('sin(x)', tikz)
        self.assertIn('trig format=rad', tikz)

    def test_trigonometric_tangent_tikz(self):
        """測試正切函數生成 TikZ 代碼（含不連續處理）"""
        params = {
            'function_type': 'trigonometric',
            'trig_function': 'tan',
            'x_range': (-6.28, 6.28),
            'y_range': (-4, 4)
        }

        tikz = self.generator.generate_tikz(params)

        self.assertIn('tan(x)', tikz)
        self.assertIn('unbounded coords=jump', tikz)
        self.assertIn('trig format=rad', tikz)

    def test_with_grid(self):
        """測試網格顯示"""
        params = {
            'function_type': 'polynomial',
            'coefficients': [1, 0],
            'show_grid': True
        }

        tikz = self.generator.generate_tikz(params)

        self.assertIn('grid=major', tikz)

    def test_with_axes_labels(self):
        """測試座標軸標籤"""
        params = {
            'function_type': 'polynomial',
            'coefficients': [1, 0],
            'show_axes_labels': True
        }

        tikz = self.generator.generate_tikz(params)

        self.assertIn('xlabel=$x$', tikz)
        self.assertIn('ylabel=$y$', tikz)

    def test_with_y_intercept_marker(self):
        """測試 y 截距標記"""
        params = {
            'function_type': 'polynomial',
            'coefficients': [1, -2, 5],  # y截距=5
            'x_range': (-3, 3),
            'y_range': (0, 10),
            'show_y_intercept': True,
            'y_intercept_color': 'red'
        }

        tikz = self.generator.generate_tikz(params)

        # 應該包含截距標記
        self.assertIn('only marks', tikz)
        self.assertIn('coordinates', tikz)
        self.assertIn('(0, 5)', tikz)

    def test_y_intercept_out_of_range(self):
        """測試 y 截距超出範圍時不顯示"""
        params = {
            'function_type': 'polynomial',
            'coefficients': [1, 0, 10],  # y截距=10
            'x_range': (-3, 3),
            'y_range': (-5, 5),  # y截距10超出範圍
            'show_y_intercept': True
        }

        tikz = self.generator.generate_tikz(params)

        # 不應該包含截距標記（因為超出範圍）
        self.assertNotIn('only marks', tikz)

    def test_custom_colors(self):
        """測試自定義顏色"""
        params = {
            'function_type': 'polynomial',
            'coefficients': [1, 0],
            'plot_color': 'red',
            'line_thickness': 'very thick'
        }

        tikz = self.generator.generate_tikz(params)

        self.assertIn('red', tikz)
        self.assertIn('very thick', tikz)

    def test_custom_samples(self):
        """測試自定義採樣點數"""
        params = {
            'function_type': 'polynomial',
            'coefficients': [1, 0, 0, 0],  # x^3
            'samples': 200
        }

        tikz = self.generator.generate_tikz(params)

        self.assertIn('samples=200', tikz)

    def test_sine_with_amplitude_and_period(self):
        """測試帶振幅和週期的三角函數"""
        params = {
            'function_type': 'trigonometric',
            'trig_function': 'sin',
            'amplitude': 2.0,
            'period': 3.14159,  # π
            'x_range': (-6.28, 6.28),
            'y_range': (-2.5, 2.5)
        }

        tikz = self.generator.generate_tikz(params)

        # 應該包含振幅
        self.assertIn('2*sin', tikz)
        # 應該包含頻率調整（2π/π = 2）
        self.assertIn('2*x', tikz)


class TestFunctionPlotValidation(unittest.TestCase):
    """測試參數驗證"""

    def setUp(self):
        """設置測試環境"""
        FuncGen = get_figure_generator('function_plot')
        self.generator = FuncGen()

    def test_invalid_function_type(self):
        """測試無效的函數類型"""
        from pydantic import ValidationError

        params = {
            'function_type': 'invalid_type',
            'coefficients': [1, 0]
        }

        with self.assertRaises(ValidationError):
            self.generator.generate_tikz(params)

    def test_polynomial_missing_coefficients(self):
        """測試多項式缺少係數"""
        from pydantic import ValidationError

        params = {
            'function_type': 'polynomial'
        }

        with self.assertRaises(ValidationError):
            self.generator.generate_tikz(params)

    def test_trigonometric_missing_function(self):
        """測試三角函數缺少函數類型"""
        from pydantic import ValidationError

        params = {
            'function_type': 'trigonometric'
        }

        with self.assertRaises(ValidationError):
            self.generator.generate_tikz(params)


if __name__ == "__main__":
    unittest.main()
