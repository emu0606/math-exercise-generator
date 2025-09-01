#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import math
import re # 導入正則表達式模塊
from typing import Optional # 導入 Optional
from figures import get_figure_generator
from figures.params_models import PredefinedTriangleAASParams

class TestPredefinedTriangleAASGenerator(unittest.TestCase):
    """測試預定義 AAS 三角形圖形生成器"""

    def setUp(self):
        """設置測試環境"""
        try:
            self.generator_cls = get_figure_generator('predefined_triangle_aas')
            self.generator = self.generator_cls()
        except ValueError as e:
            self.fail(f"無法獲取 predefined_triangle_aas 生成器: {e}")

    def test_generate_valid_triangle_aas(self):
        """測試生成有效 AAS 三角形的 TikZ 代碼 (A=70, B=50, a=6)"""
        params = {
            "variant": "question",
            "angle_A": 70.0,
            "angle_B": 50.0,
            "side_a": 6.0,  # BC (對應角A)
            "angle_unit": "deg",
            "show_vertex_labels": True,
            "show_side_a_label": True, # BC
            "side_a_label_value": "?", # 應顯示 6.0
            "show_angle_A_label": True,
            "angle_A_label_value": "70°", 
            "show_angle_B_label": True,
            "angle_B_label_value": "?", # 應顯示 50.0°
            "show_angle_C_label": True, # 應計算 C = 180-70-50 = 60°
            "angle_C_label_value": "?",
            "show_side_b_label": True, # AC (對應角B)
            "side_b_label_value": "?", # 應計算
            "show_side_c_label": True, # AB (對應角C)
            "side_c_label_value": "?", # 應計算
        }
        
        tikz_content = self.generator.generate_tikz(params)

        # 預期計算:
        # A=70, B=50, C=60 degrees
        # a = 6 (BC)
        # b/sinB = a/sinA => b = 6 * sin(50)/sin(70) = 6 * 0.7660 / 0.9397 approx 4.891 (AC)
        # c/sinC = a/sinA => c = 6 * sin(60)/sin(70) = 6 * 0.8660 / 0.9397 approx 5.529 (AB)
        # 頂點: A(0,0), B(c,0) = (5.529,0)
        # C_x = b * cos(A) = 4.891 * cos(70) = 4.891 * 0.3420 = 1.673
        # C_y = b * sin(A) = 4.891 * sin(70) = 4.891 * 0.9397 = 4.596

        # 檢查線段 (檢查座標點和連接符, 使用3位精度)
        # Line AB: (0.000, 0.000) -- (5.530, 0.000) # 5.5296 rounds to 5.530
        self.assertIn("(0.000, 0.000)", tikz_content)
        self.assertIn("(5.530, 0.000)", tikz_content)
        # Line BC: (5.530, 0.000) -- (1.673, 4.596)
        self.assertIn("(1.673, 4.596)", tikz_content) # 這些是計算結果，已捨入
        # Line CA: (1.673, 4.596) -- (0.000, 0.000)
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
        self.assertIn("label_side_a_BC", tikz_content) # BC
        # side_a_label_value 是 "?"，期望計算值 6.0 (s_a_val 是 6.0)
        self.assertEqual(extract_text_from_label("label_side_a_BC"), "6.0") # 修改為一位小數

        self.assertIn("label_side_b_CA", tikz_content) # AC
        side_b_text = extract_text_from_label("label_side_b_CA")
        self.assertIsNotNone(side_b_text)
        # side_b_label_value 是 "?"，期望計算值 approx 4.9 (4.891 rounds to 4.9)
        self.assertAlmostEqual(float(side_b_text), 4.9, places=1)

        self.assertIn("label_side_c_AB", tikz_content) # AB
        side_c_text = extract_text_from_label("label_side_c_AB")
        self.assertIsNotNone(side_c_text)
        # side_c_label_value 是 "?"，期望計算值 approx 5.5 (5.5296... rounds to 5.5)
        self.assertAlmostEqual(float(side_c_text), 5.5, places=1)
        
        # 檢查角度標籤
        # 測試用例參數: "angle_A_label_value": "70°"
        # "angle_B_label_value": "?"
        # "angle_C_label_value": "?" (默認)
        self.assertIn("label_angle_A", tikz_content)
        # angle_A_label_value 是 "70°"，提取後應為 "70"
        self.assertEqual(extract_text_from_label("label_angle_A"), "70")

        self.assertIn("label_angle_B", tikz_content)
        angle_B_text = extract_text_from_label("label_angle_B")
        self.assertIsNotNone(angle_B_text)
        # angle_B_label_value 是 "?"，期望輸入值 50.0
        self.assertAlmostEqual(float(angle_B_text), 50.0, places=1) # 修改為一位小數

        self.assertIn("label_angle_C", tikz_content)
        angle_C_text = extract_text_from_label("label_angle_C")
        self.assertIsNotNone(angle_C_text)
        # angle_C_label_value 是 "?"，期望計算值 60.0
        self.assertAlmostEqual(float(angle_C_text), 60.0, delta=0.05) # 60.003 rounds to 60.0; delta for safety

    def test_invalid_angle_sum_180_aas(self):
        """測試角度和為180 (Pydantic 應捕獲)"""
        params = {
            "variant": "question",
            "angle_A": 90.0,
            "angle_B": 90.0, # A+B = 180
            "side_a": 5.0,
            "angle_unit": "deg",
        }
        tikz_content = self.generator.generate_tikz(params)
        self.assertIn("參數驗證失敗", tikz_content)
        self.assertIn("角A和角B的和必須小於180度", tikz_content)
        self.assertIn("color=red", tikz_content)

    def test_zero_side_length_a_aas(self):
        """測試給定邊長度為0 (Pydantic 應捕獲)"""
        params = {
            "variant": "question",
            "angle_A": 60.0,
            "angle_B": 45.0,
            "side_a": 0.0, # 邊長為0
            "angle_unit": "deg",
        }
        tikz_content = self.generator.generate_tikz(params)
        # 調整 Pydantic 錯誤訊息斷言
        self.assertIn("參數驗證失敗", tikz_content)
        self.assertIn("Input should be greater than 0", tikz_content)
        self.assertIn("color=red", tikz_content)

if __name__ == "__main__":
    unittest.main()