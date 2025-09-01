#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
測試 figures.basic_triangle 模塊
"""

import unittest
from pydantic import ValidationError

# 假設 figures 和 tests 是同級目錄，或者環境配置正確
from figures import get_figure_generator
from figures.params_models import BasicTriangleParams, PointTuple
from figures.basic_triangle import BasicTriangleGenerator

class TestBasicTriangleGenerator(unittest.TestCase):
    """測試 BasicTriangleGenerator"""

    def setUp(self):
        self.generator_cls = BasicTriangleGenerator
        self.generator = self.generator_cls()

    def test_get_name(self):
        """測試 get_name 方法"""
        self.assertEqual(self.generator_cls.get_name(), "basic_triangle")

    def test_registration(self):
        """測試生成器是否已通過 get_figure_generator 正確註冊"""
        try:
            retrieved_generator_cls = get_figure_generator("basic_triangle")
            self.assertIs(retrieved_generator_cls, self.generator_cls)
        except ValueError:
            self.fail("BasicTriangleGenerator 未能通過 get_figure_generator 正確獲取。")

    def test_generate_tikz_simple_triangle(self):
        """測試生成簡單三角形的 TikZ 代碼"""
        p1: PointTuple = (0.0, 0.0)
        p2: PointTuple = (1.0, 0.0)
        p3: PointTuple = (0.0, 1.0)
        params = {
            "p1": p1, "p2": p2, "p3": p3,
            "variant": "question" # BaseFigureParams 需要 variant
        }
        expected_tikz = "\\draw (0.0,0.0) -- (1.0,0.0) -- (0.0,1.0) -- cycle;"
        self.assertEqual(self.generator.generate_tikz(params), expected_tikz)

    def test_generate_tikz_with_draw_options(self):
        """測試帶繪製選項的 TikZ 代碼"""
        params = {
            "p1": (0,0), "p2": (2,0), "p3": (1,1),
            "draw_options": "thick,blue",
            "variant": "question"
        }
        expected_tikz = "\\draw[thick,blue] (0.0,0.0) -- (2.0,0.0) -- (1.0,1.0) -- cycle;"
        self.assertEqual(self.generator.generate_tikz(params), expected_tikz)

    def test_generate_tikz_with_fill_color(self):
        """測試帶填充顏色的 TikZ 代碼"""
        params = {
            "p1": (0,0), "p2": (2,0), "p3": (1,1),
            "fill_color": "yellow",
            "variant": "question"
        }
        expected_tikz = "\\draw[fill=yellow] (0.0,0.0) -- (2.0,0.0) -- (1.0,1.0) -- cycle;"
        self.assertEqual(self.generator.generate_tikz(params), expected_tikz)

    def test_generate_tikz_with_draw_and_fill_options(self):
        """測試同時帶繪製和填充選項的 TikZ 代碼"""
        params = {
            "p1": (0,0), "p2": (2,0), "p3": (1,1),
            "draw_options": "dashed",
            "fill_color": "green!30",
            "variant": "question"
        }
        expected_tikz = "\\draw[dashed, fill=green!30] (0.0,0.0) -- (2.0,0.0) -- (1.0,1.0) -- cycle;"
        self.assertEqual(self.generator.generate_tikz(params), expected_tikz)

    def test_validation_error_missing_point(self):
        """測試缺少點參數時的 ValidationError"""
        with self.assertRaises(ValidationError):
            self.generator.generate_tikz({"p1": (0,0), "p2": (1,0), "variant": "question"}) # p3 missing
    
    def test_validation_error_invalid_point_format(self):
        """測試點格式錯誤時的 ValidationError (由 Pydantic 模型驗證器處理)"""
        with self.assertRaises(ValidationError):
            self.generator.generate_tikz({"p1": "invalid", "p2": (1,0), "p3": (0,1), "variant": "question"})
        
        with self.assertRaises(ValidationError):
            # BasicTriangleParams 的 validator 會檢查元組內的類型
            self.generator.generate_tikz({"p1": (0,'a'), "p2": (1,0), "p3": (0,1), "variant": "question"})


if __name__ == "__main__":
    unittest.main()