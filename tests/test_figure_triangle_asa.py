#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import math
import re # 導入正則表達式模塊
from typing import Optional # 導入 Optional
from figures import get_figure_generator
from figures.params_models import PredefinedTriangleASAParams

class TestPredefinedTriangleASAGenerator(unittest.TestCase):
    """測試預定義 ASA 三角形圖形生成器"""

    def setUp(self):
        """設置測試環境"""
        try:
            self.generator_cls = get_figure_generator('predefined_triangle_asa')
            self.generator = self.generator_cls()
        except ValueError as e:
            self.fail(f"無法獲取 predefined_triangle_asa 生成器: {e}")

    def test_generate_valid_triangle_asa(self):
        """測試生成有效 ASA 三角形的 TikZ 代碼 (A=60, c=5, B=45)"""
        params = {
            "variant": "question",
            "angle_A": 60.0,
            "side_c": 5.0,  # AB
            "angle_B": 45.0,
            "angle_unit": "deg",
            "show_vertex_labels": True,
            "show_side_c_label": True, # AB
            "side_c_label_value": "?", # 應顯示 5.0
            "show_angle_A_label": True,
            "angle_A_label_value": "60°", # 應顯示 60°
            "show_angle_B_label": True,
            "angle_B_label_value": "?", # 應顯示 45.0°
            "show_angle_C_label": True, # 應計算並顯示 C = 180-60-45 = 75°
            "angle_C_label_value": "?",
            "show_side_a_label": True, # BC
            "side_a_label_value": "?", # 應計算
            "show_side_b_label": True, # AC
            "side_b_label_value": "?", # 應計算
        }
        
        tikz_content = self.generator.generate_tikz(params)

        # 預期計算:
        # A=60, B=45, C=75 degrees
        # c = 5 (AB)
        # a/sinA = c/sinC => a = 5 * sin(60)/sin(75) = 5 * 0.8660 / 0.9659 approx 4.483 (BC)
        # b/sinB = c/sinC => b = 5 * sin(45)/sin(75) = 5 * 0.7071 / 0.9659 approx 3.660 (AC)
        # 頂點: A(0,0), B(5,0)
        # C_x = b * cos(A) = 3.660 * cos(60) = 3.660 * 0.5 = 1.83
        # C_y = b * sin(A) = 3.660 * sin(60) = 3.660 * 0.8660 = 3.170

        # 檢查線段 (檢查座標點和連接符, 使用3位精度)
        # Line AB: (0.000, 0.000) -- (5.000, 0.000)
        self.assertIn("(0.000, 0.000)", tikz_content)
        self.assertIn("(5.000, 0.000)", tikz_content)
        # Line BC: (5.000, 0.000) -- (1.830, 3.170)
        self.assertIn("(1.830, 3.170)", tikz_content) # 這些是計算結果，已捨入
        # Line CA: (1.830, 3.170) -- (0.000, 0.000)
        self.assertIn("--", tikz_content)

        self.assertIn("A", tikz_content)
        self.assertIn("B", tikz_content)
        self.assertIn("C", tikz_content)

        # 輔助函數從 TikZ 提取標籤文本
        def extract_text_from_label(id_prefix: str) -> Optional[str]:
            # 修正正則表達式以精確匹配註釋結構
            match = re.search(fr"% 子圖形 {id_prefix} \(類型: label\).*?\\node.*?\{{([^{{}}]*)\}};", tikz_content, re.DOTALL)
            if match:
                return match.group(1).strip('$').strip('°')
            return None

        # 檢查邊長標籤
        self.assertIn("label_side_c_AB", tikz_content) # AB
        # side_c_label_value 是 "?"，期望計算值 5.0 (s_c_val 是 5.0)
        self.assertEqual(extract_text_from_label("label_side_c_AB"), "5.0") # 修改為一位小數

        self.assertIn("label_side_a_BC", tikz_content) # BC
        side_a_text = extract_text_from_label("label_side_a_BC")
        self.assertIsNotNone(side_a_text)
        # side_a_label_value 是 "?"，期望計算值 approx 4.5 (4.483 rounds to 4.5)
        self.assertAlmostEqual(float(side_a_text), 4.5, places=1)

        self.assertIn("label_side_b_CA", tikz_content) # AC
        side_b_text = extract_text_from_label("label_side_b_CA")
        self.assertIsNotNone(side_b_text)
        # side_b_label_value 是 "?"，期望計算值 approx 3.7 (3.660 rounds to 3.7)
        self.assertAlmostEqual(float(side_b_text), 3.7, places=1)
        
        # 檢查角度標籤
        # 測試用例參數: "angle_A_label_value": "60°"
        # "angle_B_label_value": "?"
        # "angle_C_label_value": "?" (默認)
        self.assertIn("label_angle_A", tikz_content)
        # angle_A_label_value 是 "60°"，提取後應為 "60"
        self.assertEqual(extract_text_from_label("label_angle_A"), "60")


        self.assertIn("label_angle_B", tikz_content)
        angle_B_text = extract_text_from_label("label_angle_B")
        self.assertIsNotNone(angle_B_text)
        # angle_B_label_value 是 "?"，期望輸入值 45.0
        self.assertAlmostEqual(float(angle_B_text), 45.0, places=1) # 修改為一位小數

        self.assertIn("label_angle_C", tikz_content)
        angle_C_text = extract_text_from_label("label_angle_C")
        self.assertIsNotNone(angle_C_text)
        # angle_C_label_value 是 "?"，期望計算值 75.0
        self.assertAlmostEqual(float(angle_C_text), 75.0, delta=0.05) # 74.997 rounds to 75.0; delta for safety


    def test_invalid_angle_sum_180(self):
        """測試角度和為180 (Pydantic 應捕獲)"""
        params = {
            "variant": "question",
            "angle_A": 90.0,
            "side_c": 5.0,
            "angle_B": 90.0, # A+B = 180
            "angle_unit": "deg",
        }
        tikz_content = self.generator.generate_tikz(params)
        self.assertIn("參數驗證失敗", tikz_content)
        self.assertIn("角A和角B的和必須小於180度", tikz_content)
        self.assertIn("color=red", tikz_content)

    def test_invalid_angle_sum_over_180(self):
        """測試角度和超過180 (Pydantic 應捕獲)"""
        params = {
            "variant": "question",
            "angle_A": 100.0,
            "side_c": 5.0,
            "angle_B": 90.0, # A+B = 190
            "angle_unit": "deg",
        }
        tikz_content = self.generator.generate_tikz(params)
        self.assertIn("參數驗證失敗", tikz_content)
        self.assertIn("角A和角B的和必須小於180度", tikz_content)
        self.assertIn("color=red", tikz_content)

    def test_zero_side_length_c(self):
        """測試夾邊長度為0 (Pydantic 應捕獲)"""
        params = {
            "variant": "question",
            "angle_A": 60.0,
            "side_c": 0.0, # 邊長為0
            "angle_B": 45.0,
            "angle_unit": "deg",
        }
        tikz_content = self.generator.generate_tikz(params)
        # 調整 Pydantic 錯誤訊息斷言
        self.assertIn("參數驗證失敗", tikz_content)
        self.assertIn("Input should be greater than 0", tikz_content)
        self.assertIn("color=red", tikz_content)
        
    def test_angle_C_becomes_zero(self):
        """測試計算出的角C趨近於0 (例如 A=89.99, B=89.99)"""
        params = {
            "variant": "question",
            "angle_A": 89.999, # 非常接近90
            "side_c": 5.0,
            "angle_B": 89.999, # 非常接近90, A+B 接近180
            "angle_unit": "deg",
        }
        # Pydantic 的 validator 應該先捕獲 angle_A + angle_B < 180
        # 如果 validator 允許非常接近的值，則 _calculate_vertices 中的 angle_C_rad <= 1e-9 會捕獲
        tikz_content = self.generator.generate_tikz(params)
        if "參數驗證失敗" in tikz_content: # Pydantic 捕獲
            self.assertIn("角A和角B的和必須小於180度", tikz_content)
        else: # _calculate_vertices 捕獲 (現在應該是座標過大錯誤)
            self.assertIn("無法構成三角形：計算出的頂點座標值過大 (可能由於角度接近0或180)。", tikz_content)
        self.assertIn("color=red", tikz_content)

if __name__ == "__main__":
    unittest.main()