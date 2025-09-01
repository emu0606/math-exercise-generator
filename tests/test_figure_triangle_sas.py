#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import math
import re # 導入正則表達式模塊
from typing import Optional # 導入 Optional
from figures import get_figure_generator
from figures.params_models import PredefinedTriangleSASParams

class TestPredefinedTriangleSASGenerator(unittest.TestCase):
    """測試預定義 SAS 三角形圖形生成器"""

    def setUp(self):
        """設置測試環境"""
        try:
            self.generator_cls = get_figure_generator('predefined_triangle_sas')
            self.generator = self.generator_cls()
        except ValueError as e:
            self.fail(f"無法獲取 predefined_triangle_sas 生成器: {e}")

    def test_generate_valid_triangle_sas(self):
        """測試生成有效 SAS 三角形的 TikZ 代碼 (例如 b=4, A=60deg, c=3)"""
        params = {
            "variant": "question",
            "side_b": 4.0,  # AC
            "angle_A": 60.0, # 夾角 A
            "side_c": 3.0,  # AB
            "angle_unit": "deg",
            "show_vertex_labels": True,
            "show_side_b_label": True, # AC
            "side_b_label_value": "?", # 應顯示 4.0
            "show_side_c_label": True, # AB
            "side_c_label_value": "3cm", # 應顯示 3cm
            "show_angle_A_label": True, # 角A
            "angle_A_label_value": "?", # 應顯示 60°
            "show_angle_B_label": True, # 添加以顯示角B標籤
            "angle_B_label_value": "?",
            "show_angle_C_label": True, # 添加以顯示角C標籤
            "angle_C_label_value": "?",
            "show_side_a_label": True, # BC (對邊 a)
            "side_a_label_value": "?", # 應計算並顯示
        }
        
        tikz_content = self.generator.generate_tikz(params)

        # 預期頂點: A(0,0), C(4,0)
        # B_x = 3 * cos(60deg) = 3 * 0.5 = 1.5
        # B_y = 3 * sin(60deg) = 3 * sqrt(3)/2 approx 3 * 0.866 = 2.598
        # 邊 a (BC) 長度: sqrt((4-1.5)^2 + (0-2.598)^2) = sqrt(2.5^2 + (-2.598)^2)
        # = sqrt(6.25 + 6.7496) = sqrt(12.9996) approx 3.605
        
        # 檢查線段 (檢查座標點和連接符, 使用3位精度)
        # Line AB: (0.000, 0.000) -- (1.500, 2.598)
        self.assertIn("(0.000, 0.000)", tikz_content)
        self.assertIn("(1.500, 2.598)", tikz_content)
        # Line BC: (1.500, 2.598) -- (4.000, 0.000)
        self.assertIn("(4.000, 0.000)", tikz_content)
        # Line CA: (4.000, 0.000) -- (0.000, 0.000)
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
        self.assertIn("label_side_b_CA", tikz_content) # AC
        # side_b_label_value 是 "?"，期望計算值 4.0 (s_b 是 4.0)
        self.assertEqual(extract_text_from_label("label_side_b_CA"), "4.0") # 修改為一位小數

        self.assertIn("label_side_c_AB", tikz_content) # AB
        # side_c_label_value 是 "3cm"，期望 "3cm" (自定義文本不受精度影響)
        self.assertEqual(extract_text_from_label("label_side_c_AB"), "3cm")
        
        self.assertIn("label_side_a_BC", tikz_content) # BC
        side_a_text = extract_text_from_label("label_side_a_BC")
        self.assertIsNotNone(side_a_text)
        # side_a_label_value 是 "?"，期望計算值 approx 3.6
        self.assertAlmostEqual(float(side_a_text), 3.6, places=1) # 3.6055 rounds to 3.6
        
        # 檢查角度標籤
        # 測試用例參數: "show_angle_A_label": True, "angle_A_label_value": "?"
        # "show_angle_B_label": True, "angle_B_label_value": "?"
        # "show_angle_C_label": True, "angle_C_label_value": "?"
        # 所以角 B 和 C 也應該測試

        self.assertIn("label_angle_A", tikz_content)
        angle_A_text = extract_text_from_label("label_angle_A")
        self.assertIsNotNone(angle_A_text)
        # angle_A_label_value 是 "?"，期望輸入值 60.0
        self.assertAlmostEqual(float(angle_A_text), 60.0, places=1) # 修改為一位小數

        # 根據 test_figure_triangle_sas.py 的 params，角B和C也應該顯示
        # params from test:
        # "show_angle_A_label": True, "angle_A_label_value": "?",
        # "show_angle_B_label": True, "angle_B_label_value": "?",
        # "show_angle_C_label": True, "angle_C_label_value": "?",

        self.assertIn("label_angle_B", tikz_content)
        angle_B_text = extract_text_from_label("label_angle_B")
        self.assertIsNotNone(angle_B_text)
        # 計算: B = arcsin(b*sinA/a) approx 73.897 deg -> 73.9
        self.assertAlmostEqual(float(angle_B_text), 73.9, places=1)

        self.assertIn("label_angle_C", tikz_content)
        angle_C_text = extract_text_from_label("label_angle_C")
        self.assertIsNotNone(angle_C_text)
        # 計算: C = 180 - A - B approx 46.103 deg -> 46.1
        self.assertAlmostEqual(float(angle_C_text), 46.1, places=1)

    def test_invalid_angle_zero(self):
        """測試角度為0 (Pydantic 應捕獲)"""
        params = {
            "variant": "question",
            "side_b": 4.0,
            "angle_A": 0.0, 
            "side_c": 3.0,
            "angle_unit": "deg",
        }
        tikz_content = self.generator.generate_tikz(params)
        # 調整 Pydantic 錯誤訊息斷言
        self.assertIn("參數驗證失敗", tikz_content)
        self.assertIn("Input should be greater than 0", tikz_content)
        self.assertIn("color=red", tikz_content)

    def test_invalid_angle_180(self):
        """測試角度為180 (Pydantic 應捕獲)"""
        params = {
            "variant": "question",
            "side_b": 4.0,
            "angle_A": 180.0, 
            "side_c": 3.0,
            "angle_unit": "deg",
        }
        tikz_content = self.generator.generate_tikz(params)
        # 調整 Pydantic 錯誤訊息斷言
        self.assertIn("參數驗證失敗", tikz_content)
        self.assertIn("Input should be less than 180", tikz_content)
        self.assertIn("color=red", tikz_content)
        
    def test_zero_side_length(self):
        """測試邊長為0 (Pydantic 應捕獲)"""
        params = {
            "variant": "question",
            "side_b": 0.0, # 邊長為0
            "angle_A": 60.0, 
            "side_c": 3.0,
            "angle_unit": "deg",
        }
        tikz_content = self.generator.generate_tikz(params)
        # 調整 Pydantic 錯誤訊息斷言
        self.assertIn("參數驗證失敗", tikz_content)
        self.assertIn("Input should be greater than 0", tikz_content)
        self.assertIn("color=red", tikz_content)

if __name__ == "__main__":
    unittest.main()