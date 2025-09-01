#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import re # 導入正則表達式模塊
from typing import Optional # 導入 Optional
from figures import get_figure_generator
from figures.params_models import PredefinedTriangleSSSParams

class TestPredefinedTriangleSSSGenerator(unittest.TestCase):
    """測試預定義 SSS 三角形圖形生成器"""

    def setUp(self):
        """設置測試環境"""
        try:
            self.generator_cls = get_figure_generator('predefined_triangle_sss')
            self.generator = self.generator_cls()
        except ValueError as e:
            self.fail(f"無法獲取 predefined_triangle_sss 生成器: {e}")

    def test_generate_valid_triangle_3_4_5(self):
        """測試生成有效三角形 (3,4,5) 的 TikZ 代碼"""
        params = {
            "variant": "question",
            "side_a": 5.0, # BC
            "side_b": 4.0, # AC
            "side_c": 3.0, # AB
            "show_vertex_labels": True,
            "show_side_a_label": True, # BC
            "side_a_label_value": "?", # 應顯示 5.0
            "show_side_b_label": True, # AC
            "side_b_label_value": "4.0cm", # 應顯示 4.0cm
            "show_side_c_label": True, # AB
            # side_c_label_value 未提供，但 SSS 輸入中 side_c 是 3.0，所以應顯示 3.0
            "show_angle_A_label": True, # 角A (直角)
        }
        
        tikz_content = self.generator.generate_tikz(params)

        # 預期頂點: A(0,0), B(3,0), C(x,y)
        # cos_A = (4^2 + 3^2 - 5^2) / (2*4*3) = (16+9-25)/24 = 0 => A = 90 deg
        # C_x = 4 * cos(90) = 0
        # C_y = 4 * sin(90) = 4
        # 所以 C 應該是 (0,4) 或非常接近
        
        # 檢查線段 (檢查座標點和連接符)
        # Line AB: (0.000, 0.000) -- (3.000, 0.000)
        self.assertIn("(0.000, 0.000)", tikz_content)
        self.assertIn("(3.000, 0.000)", tikz_content)
        # Line BC: (3.000, 0.000) -- (0.000, 4.000)
        self.assertIn("(0.000, 4.000)", tikz_content)
        # Line CA: (0.000, 4.000) -- (0.000, 0.000)
        self.assertIn("--", tikz_content) # 確保有線段連接符

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
        self.assertIn("label_side_a_BC", tikz_content)
        # side_a_label_value 是 "?"，期望計算值 5.0
        self.assertEqual(extract_text_from_label("label_side_a_BC"), "5.0") # 修改為一位小數

        self.assertIn("label_side_b_CA", tikz_content)
        # side_b_label_value 是 "4.0cm"，期望 "4.0cm" (自定義文本不受精度影響)
        self.assertEqual(extract_text_from_label("label_side_b_CA"), "4.0cm")
        
        self.assertIn("label_side_c_AB", tikz_content)
        # side_c_label_value 未提供 (默認為 "?")，期望計算值 3.0
        self.assertEqual(extract_text_from_label("label_side_c_AB"), "3.0") # 修改為一位小數
        
        # 檢查角度標籤
        # For a=5, b=4, c=3: Angle A (opposite side_a) is 90 deg.
        # Angle B (opposite side_b) is arccos((5^2+3^2-4^2)/(2*5*3)) = arccos(18/30) = arccos(0.6) approx 53.130 deg
        # Angle C (opposite side_c) is arccos((5^2+4^2-3^2)/(2*5*4)) = arccos(32/40) = arccos(0.8) approx 36.870 deg
        # Note: The test setup has A=(0,0), B=(c,0)=(3,0), C=(b*cosA, b*sinA).
        # If A is 90 deg, C=(4*cos90, 4*sin90) = (0,4).
        # So, sp_A=(0,0), sp_B=(3,0), sp_C=(0,4).
        # Angle A (at sp_A, BAC) is indeed 90.
        # Angle B (at sp_B, ABC) is angle between BA and BC. BA=(-3,0), BC=(-3,4). arccos(9/15)=arccos(0.6) approx 53.130
        # Angle C (at sp_C, BCA) is angle between CA and CB. CA=(0,-4), CB=(3,-4). arccos(16/20)=arccos(0.8) approx 36.870

        self.assertIn("label_angle_A", tikz_content)
        angle_A_text = extract_text_from_label("label_angle_A")
        self.assertIsNotNone(angle_A_text)
        self.assertAlmostEqual(float(angle_A_text), 90.0, places=1) # 修改為一位小數

        # Add assertions for angle_B and angle_C if they are shown by default or by params
        # Assuming params has show_angle_B_label=True, angle_B_label_value="?" (and similar for C)
        # The current test params only has "show_angle_A_label": True
        # We should add other angles to params to test them.
        # For now, only test angle A as per current params.
        # If other angle labels are present by default (e.g. if show_angle_X_label defaults to True if not specified),
        # then we would need to add tests for them.
        # Based on PredefinedTriangleBaseParams, show_angle_X_label defaults to False.
        # So, only angle A will be shown and tested here.

    def test_invalid_triangle_inequality(self):
        """測試不滿足三角形不等式的情況 (1,2,5)"""
        params = {
            "variant": "question",
            "side_a": 5.0,
            "side_b": 2.0,
            "side_c": 1.0,
        }
        tikz_content = self.generator.generate_tikz(params)
        self.assertIn("無法構成三角形：邊長不滿足三角形不等式。", tikz_content)
        self.assertIn("color=red", tikz_content)

    def test_degenerate_triangle(self):
        """測試退化三角形 (1,2,3) - 邊長和導致角度計算問題"""
        params = {
            "variant": "question",
            "side_a": 3.0,
            "side_b": 2.0,
            "side_c": 1.0,
        }
        # cos_A = (2^2 + 1^2 - 3^2) / (2*2*1) = (4+1-9)/4 = -4/4 = -1. Angle A = 180 deg.
        # 這應該被視為無效或退化
        tikz_content = self.generator.generate_tikz(params)
        # 預期 _calculate_vertices 中的 cos_A 檢查或面積檢查會捕獲此問題
        self.assertIn("無法構成三角形", tikz_content) # 錯誤訊息可能不同
        self.assertIn("color=red", tikz_content)

    def test_parameter_validation_error_missing_side(self):
        """測試 Pydantic 參數驗證錯誤 (缺少邊長)"""
        params = {
            "variant": "question",
            "side_a": 5.0,
            # side_b 缺失
            "side_c": 3.0,
        }
        tikz_content = self.generator.generate_tikz(params)
        # 調整 Pydantic 錯誤訊息斷言
        self.assertIn("參數驗證失敗", tikz_content)
        self.assertIn("Field required", tikz_content) # Pydantic v2 可能的錯誤訊息
        self.assertIn("color=red", tikz_content)

    def test_parameter_validation_error_zero_side(self):
        """測試 Pydantic 參數驗證錯誤 (邊長為0)"""
        params = {
            "variant": "question",
            "side_a": 5.0,
            "side_b": 0.0, # 邊長為0
            "side_c": 3.0,
        }
        # Pydantic Field(..., gt=0) 應該會捕獲這個
        tikz_content = self.generator.generate_tikz(params)
        # 調整 Pydantic 錯誤訊息斷言
        self.assertIn("參數驗證失敗", tikz_content)
        self.assertIn("Input should be greater than 0", tikz_content) # Pydantic v2 可能的錯誤訊息
        self.assertIn("color=red", tikz_content)

if __name__ == "__main__":
    unittest.main()