#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
測試 figures.label 模塊
"""

import unittest
from pydantic import ValidationError

from figures import get_figure_generator
from figures.params_models import LabelParams # Updated LabelParams
from figures.label import LabelGenerator

class TestLabelGenerator(unittest.TestCase):
    """測試 LabelGenerator"""

    def setUp(self):
        self.generator_cls = LabelGenerator
        self.generator = self.generator_cls()

    def test_get_name(self):
        """測試 get_name 方法"""
        self.assertEqual(self.generator_cls.get_name(), "label")

    def test_registration(self):
        """測試生成器是否已通過 get_figure_generator 正確註冊"""
        try:
            retrieved_generator_cls = get_figure_generator("label")
            self.assertIs(retrieved_generator_cls, self.generator_cls)
        except ValueError:
            self.fail("LabelGenerator 未能通過 get_figure_generator 正確獲取。")

    def test_generate_tikz_basic_label(self):
        """測試基本標籤"""
        params = {
            "x": 1.0, "y": 1.5, "text": "A",
            "variant": "question" # from BaseFigureParams
        }
        # Expected: \node[color=black] at (1,1.5) {$A$}; (using .7g for coords)
        expected_tikz = "\\node[color=black] at (1,1.5) {$A$};"
        self.assertEqual(self.generator.generate_tikz(params), expected_tikz)

    def test_generate_tikz_with_position_modifiers(self):
        """測試帶 position_modifiers"""
        params = {
            "x": 1, "y": 1, "text": "B", 
            "position_modifiers": "above right=0.1cm",
            "variant": "question"
        }
        expected_tikz = "\\node[above right=0.1cm, color=black] at (1,1) {$B$};"
        self.assertEqual(self.generator.generate_tikz(params), expected_tikz)

    def test_generate_tikz_with_anchor_and_rotate(self):
        """測試帶 anchor 和 rotate"""
        params = {
            "x": 2.2, "y": 2.8, "text": "C",
            "anchor": "north west", "rotate": 45.0,
            "variant": "question"
        }
        expected_tikz = "\\node[anchor=north west, rotate=45, color=black] at (2.2,2.8) {$C$};"
        self.assertEqual(self.generator.generate_tikz(params), expected_tikz)

    def test_generate_tikz_with_font_color_no_math(self):
        """測試帶 font_size, color, 且非數學模式"""
        params = {
            "x": 0, "y": 0, "text": "Hello",
            "font_size": "\\small", "color": "blue", "math_mode": False,
            "variant": "question"
        }
        expected_tikz = "\\node[color=blue, font=\\small] at (0,0) {Hello};"
        self.assertEqual(self.generator.generate_tikz(params), expected_tikz)

    def test_generate_tikz_with_additional_options(self):
        """測試帶 additional_node_options"""
        params = {
            "x": 0, "y": 0, "text": "X",
            "additional_node_options": "draw, circle, minimum size=5mm",
            "variant": "question"
        }
        expected_tikz = "\\node[color=black, draw, circle, minimum size=5mm] at (0,0) {$X$};"
        self.assertEqual(self.generator.generate_tikz(params), expected_tikz)

    def test_generate_tikz_all_options_combined(self):
        """測試所有選項組合"""
        params = {
            "x": 1.23, "y": 4.56, "text": "Mix",
            "position_modifiers": "below=0.2cm",
            "anchor": "east",
            "rotate": -30.0,
            "color": "red",
            "font_size": "\\Large",
            "math_mode": True,
            "additional_node_options": "fill=yellow!20, rounded corners",
            "variant": "explanation"
        }
        # Order of options in style_str might vary if not careful, but join should be consistent.
        # Current implementation: pos, anchor, rotate, color, font, additional
        expected_tikz = ("\\node[below=0.2cm, anchor=east, rotate=-30, color=red, font=\\Large, fill=yellow!20, rounded corners] "
                         "at (1.23,4.56) {$Mix$};")
        self.assertEqual(self.generator.generate_tikz(params), expected_tikz)
        
    def test_generate_tikz_empty_text_math_mode(self):
        """測試空文本在數學模式下"""
        params = {"x": 0, "y": 0, "text": "", "math_mode": True, "variant": "question"}
        # Current LabelGenerator: formatted_text = f"${text}$" if text else "" -> ""
        expected_tikz = "\\node[color=black] at (0,0) {};" 
        self.assertEqual(self.generator.generate_tikz(params), expected_tikz)

    def test_validation_error_missing_text(self):
        """測試缺少 text 參數 (Pydantic default should cover, but explicit test is good)"""
        # text has a default of '', so this won't raise ValidationError for missing, but for type if not str
        with self.assertRaises(ValidationError):
             self.generator.generate_tikz({"x":0, "y":0, "text": None, "variant": "question"}) # text=None should fail type check

    def test_validation_error_invalid_types(self):
        """測試無效的參數類型"""
        with self.assertRaises(ValidationError): # x is not float
            self.generator.generate_tikz({"x":"a", "y":0, "text":"T", "variant": "question"})
        with self.assertRaises(ValidationError): # rotate is not float
            self.generator.generate_tikz({"x":0, "y":0, "text":"T", "rotate": " ৪৫", "variant": "question"})
        with self.assertRaises(ValidationError): # color is not str
            self.generator.generate_tikz({"x":0, "y":0, "text":"T", "color": 123, "variant": "question"})


if __name__ == "__main__":
    unittest.main()