#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import math
import re # 導入正則表達式模塊
from typing import Optional # 導入 Optional
from figures import get_figure_generator
from figures.params_models import PredefinedTriangleRHSParams

class TestPredefinedTriangleRHSGenerator(unittest.TestCase):
    """測試預定義 RHS 三角形圖形生成器"""

    def setUp(self):
        """設置測試環境"""
        try:
            self.generator_cls = get_figure_generator('predefined_triangle_rhs')
            self.generator = self.generator_cls()
        except ValueError as e:
            self.fail(f"無法獲取 predefined_triangle_rhs 生成器: {e}")

    def test_generate_valid_triangle_rhs_3_4_5(self):
        """測試生成有效 RHS 三角形的 TikZ 代碼 (斜邊=5, 一直角邊=3)"""
        params = {
            "variant": "question",
            "hypotenuse": 5.0,
            "one_leg": 3.0, # 假設這是 side_a (BC)
            "show_vertex_labels": True,
            "show_side_a_label": True, # BC (one_leg)
            "side_a_label_value": "?", # 應顯示 3.0
            "show_side_b_label": True, # AC (other_leg = 4.0)
            "side_b_label_value": "?", # 應顯示 4.0
            "show_side_c_label": True, # AB (hypotenuse)
            "side_c_label_value": "5cm", # 應顯示 5cm
            "show_angle_C_label": True, # 直角C
            "angle_C_label_value": "?", # 應顯示 90°
            "angle_C_notation": "right_angle", # 應嘗試繪製直角符號
            "show_angle_A_label": True,
            "angle_A_label_value": "?", # 應計算
        }
        
        tikz_content = self.generator.generate_tikz(params)

        # 預期頂點: C(0,0), B(3,0) (one_leg=a=BC), A(0,4) (other_leg=b=AC)
        # 斜邊 AB = 5
        
        # 檢查線段 (檢查座標點和連接符, 使用3位精度)
        # Line AB: (0.000, 4.000) -- (3.000, 0.000)
        self.assertIn("(0.000, 4.000)", tikz_content)
        self.assertIn("(3.000, 0.000)", tikz_content)
        # Line BC: (3.000, 0.000) -- (0.000, 0.000)
        self.assertIn("(0.000, 0.000)", tikz_content)
        # Line CA: (0.000, 0.000) -- (0.000, 4.000)
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
        self.assertIn("label_side_a_BC", tikz_content) # one_leg
        # side_a_label_value 是 "?"，期望計算值 3.0 (one_leg 是 3.0)
        self.assertEqual(extract_text_from_label("label_side_a_BC"), "3.0") # 修改為一位小數

        self.assertIn("label_side_b_CA", tikz_content) # other_leg
        side_b_text = extract_text_from_label("label_side_b_CA")
        self.assertIsNotNone(side_b_text)
        # side_b_label_value 是 "?"，期望計算值 4.0
        self.assertAlmostEqual(float(side_b_text), 4.0, places=1) # 修改為一位小數

        self.assertIn("label_side_c_AB", tikz_content) # hypotenuse
        # side_c_label_value 是 "5cm"，期望 "5cm" (自定義文本不受精度影響)
        self.assertEqual(extract_text_from_label("label_side_c_AB"), "5cm")
        
        # 檢查角度標籤
        # 測試用例參數: "show_angle_C_label": True, "angle_C_label_value": "?"
        # "show_angle_A_label": True, "angle_A_label_value": "?"
        # 角 B 默認不顯示

        self.assertIn("label_angle_C", tikz_content) # 直角C
        angle_C_text = extract_text_from_label("label_angle_C")
        self.assertIsNotNone(angle_C_text)
        # angle_C_label_value 是 "?"，期望計算值 90.0
        self.assertAlmostEqual(float(angle_C_text), 90.0, places=1) # 修改為一位小數
        # TODO: 測試直角符號的實際繪製 (當實現時)

        self.assertIn("label_angle_A", tikz_content)
        angle_A_text = extract_text_from_label("label_angle_A")
        self.assertIsNotNone(angle_A_text)
        # angle_A_label_value 是 "?"，期望計算值 approx 36.9 (36.870 rounds to 36.9)
        self.assertAlmostEqual(float(angle_A_text), 36.9, places=1)

    def test_invalid_leg_equals_hypotenuse(self):
        """測試直角邊等於斜邊 (Pydantic 應捕獲)"""
        params = {
            "variant": "question",
            "hypotenuse": 5.0,
            "one_leg": 5.0, 
        }
        tikz_content = self.generator.generate_tikz(params)
        # 調整 Pydantic 錯誤訊息斷言
        self.assertIn("參數驗證失敗", tikz_content)
        self.assertIn("直角邊長度必須小於斜邊長度", tikz_content) # Pydantic validator message
        self.assertIn("color=red", tikz_content)

    def test_invalid_leg_greater_than_hypotenuse(self):
        """測試直角邊大於斜邊 (Pydantic 應捕獲)"""
        params = {
            "variant": "question",
            "hypotenuse": 5.0,
            "one_leg": 6.0, 
        }
        tikz_content = self.generator.generate_tikz(params)
        # 調整 Pydantic 錯誤訊息斷言
        self.assertIn("參數驗證失敗", tikz_content)
        self.assertIn("直角邊長度必須小於斜邊長度", tikz_content) # Pydantic validator message
        self.assertIn("color=red", tikz_content)
        
    def test_calculated_other_leg_zero(self):
        """測試計算出的另一邊為0 (例如 hypotenuse=5, one_leg=5，但Pydantic先捕獲)"""
        # 此情況會被 Pydantic 的 one_leg < hypotenuse 捕獲
        # 如果 Pydantic 允許 one_leg == hypotenuse (例如改為 <=)，則 _calculate_vertices 會出錯
        params = {
            "variant": "question",
            "hypotenuse": 5.00000001, # 略大於 one_leg
            "one_leg": 5.0, 
        }
        # side_b_squared will be very small, side_b will be very small. Area will be small.
        # The _calculate_vertices might raise "無法構成三角形：根據勾股定理計算出的另一邊無效。" if side_b_squared <= 1e-9
        # Or the area check in _build_composite_params might catch it.
        tikz_content = self.generator.generate_tikz(params)
        if "無法構成三角形：根據勾股定理計算出的另一邊無效。" in tikz_content:
            self.assertIn("無法構成三角形：根據勾股定理計算出的另一邊無效。", tikz_content)
        else:
            self.assertIn("無法構成三角形：計算得到的頂點共線或面積為零。", tikz_content)
        self.assertIn("color=red", tikz_content)


if __name__ == "__main__":
    unittest.main()