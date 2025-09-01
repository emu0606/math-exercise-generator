#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
測試 figures.arc 模塊
"""

import unittest
import math
from pydantic import ValidationError

from figures import get_figure_generator
from figures.params_models import ArcParams, PointTuple
from figures.arc import ArcGenerator

# 輔助函數，用於比較浮點數，考慮到 .7g 格式化可能帶來的微小差異
def assertFloatStrEqual(test_case, actual_str, expected_val, places=6):
    test_case.assertAlmostEqual(float(actual_str), expected_val, places=places)

class TestArcGenerator(unittest.TestCase):
    """測試 ArcGenerator"""

    def setUp(self):
        self.generator_cls = ArcGenerator
        self.generator = self.generator_cls()

    def test_get_name(self):
        """測試 get_name 方法"""
        self.assertEqual(self.generator_cls.get_name(), "arc")

    def test_registration(self):
        """測試生成器是否已通過 get_figure_generator 正確註冊"""
        try:
            retrieved_generator_cls = get_figure_generator("arc")
            self.assertIs(retrieved_generator_cls, self.generator_cls)
        except ValueError:
            self.fail("ArcGenerator 未能通過 get_figure_generator 正確獲取。")

    def test_generate_tikz_simple_arc_90_deg(self):
        """測試生成簡單90度圓弧的 TikZ 代碼"""
        center: PointTuple = (0.0, 0.0)
        radius = 1.0
        start_rad = 0.0
        end_rad = math.pi / 2.0
        
        params = {
            "center": center, "radius": radius,
            "start_angle_rad": start_rad, "end_angle_rad": end_rad,
            "variant": "question"
        }
        
        # Expected: \draw (1,0) arc (0:90:1);
        # start_x = 0 + 1*cos(0) = 1
        # start_y = 0 + 1*sin(0) = 0
        # start_deg = 0, end_deg = 90
        # Using .7g for float formatting in generator
        expected_tikz = "\\draw (1,0) arc (0:90:1);" 
        # Note: .7g on integers like 0, 90, 1 should produce "0", "90", "1"
        # For (1.0, 0.0) -> "(1,0)" if .0 is dropped by .7g for whole numbers.
        # Let's verify the exact output format of .7g for these cases.
        # float(1.0) -> "1" by .7g. float(0.0) -> "0".
        # float(90.0) -> "90".
        # So the expected_tikz should be correct.

        self.assertEqual(self.generator.generate_tikz(params), expected_tikz)

    def test_generate_tikz_with_draw_options(self):
        """測試帶繪製選項的 TikZ 代碼"""
        center: PointTuple = (1.0, 1.0)
        radius = 2.0
        start_rad = math.pi / 4.0 # 45 deg
        end_rad = 3.0 * math.pi / 4.0 # 135 deg
        draw_options = "dashed,purple"
        
        params = {
            "center": center, "radius": radius,
            "start_angle_rad": start_rad, "end_angle_rad": end_rad,
            "draw_options": draw_options,
            "variant": "question"
        }
        
        start_x = center[0] + radius * math.cos(start_rad) # 1 + 2*sqrt(2)/2 = 1+sqrt(2)
        start_y = center[1] + radius * math.sin(start_rad) # 1 + 2*sqrt(2)/2 = 1+sqrt(2)
        
        # Format numbers as they would be by f"{val:.7g}"
        fmt_start_x = f"{start_x:.7g}"
        fmt_start_y = f"{start_y:.7g}"
        fmt_start_deg = f"{math.degrees(start_rad):.7g}"
        fmt_end_deg = f"{math.degrees(end_rad):.7g}"
        fmt_radius = f"{radius:.7g}"

        expected_tikz = f"\\draw[{draw_options}] ({fmt_start_x},{fmt_start_y}) arc ({fmt_start_deg}:{fmt_end_deg}:{fmt_radius});"
        self.assertEqual(self.generator.generate_tikz(params), expected_tikz)

    def test_generate_tikz_angle_wraparound(self):
        """測試角度環繞 (-90 to 90 deg)"""
        center: PointTuple = (0.0, 0.0)
        radius = 1.5
        start_rad = -math.pi / 2.0 # -90 deg
        end_rad = math.pi / 2.0   # 90 deg
        
        params = {
            "center": center, "radius": radius,
            "start_angle_rad": start_rad, "end_angle_rad": end_rad,
            "variant": "question"
        }
        
        start_x = center[0] + radius * math.cos(start_rad) # 0 + 1.5 * 0 = 0
        start_y = center[1] + radius * math.sin(start_rad) # 0 + 1.5 * (-1) = -1.5
        
        fmt_start_x = f"{start_x:.7g}"
        fmt_start_y = f"{start_y:.7g}"
        fmt_start_deg = f"{math.degrees(start_rad):.7g}" # -90
        fmt_end_deg = f"{math.degrees(end_rad):.7g}"     # 90
        fmt_radius = f"{radius:.7g}"                     # 1.5

        expected_tikz = f"\\draw ({fmt_start_x},{fmt_start_y}) arc ({fmt_start_deg}:{fmt_end_deg}:{fmt_radius});"
        self.assertEqual(self.generator.generate_tikz(params), expected_tikz)

    def test_validation_error_missing_radius(self):
        """測試缺少 radius 參數時的 ValidationError"""
        with self.assertRaises(ValidationError):
            self.generator.generate_tikz({
                "center": (0,0), 
                "start_angle_rad": 0, "end_angle_rad": 1, 
                "variant": "question"
            }) # radius missing
            
    def test_validation_error_non_positive_radius(self):
        """測試 radius 非正數時的 ValidationError"""
        with self.assertRaises(ValidationError): # gt=0 in ArcParams
            self.generator.generate_tikz({
                "center": (0,0), "radius": 0,
                "start_angle_rad": 0, "end_angle_rad": 1,
                "variant": "question"
            })
        with self.assertRaises(ValidationError):
            self.generator.generate_tikz({
                "center": (0,0), "radius": -1.0,
                "start_angle_rad": 0, "end_angle_rad": 1,
                "variant": "question"
            })

    def test_validation_error_invalid_center_format(self):
        """測試 center 格式錯誤時的 ValidationError"""
        with self.assertRaises(ValidationError):
            self.generator.generate_tikz({
                "center": "invalid", "radius": 1, # type: ignore
                "start_angle_rad": 0, "end_angle_rad": 1,
                "variant": "question"
            })


if __name__ == "__main__":
    unittest.main()