#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import re # 導入正則表達式模塊
from typing import Optional # 導入 Optional
from figures import get_figure_generator, FigureGenerator # 假設 figures 包在 PYTHONPATH
from figures.params_models import PredefinedTriangleCoordinatesParams

class TestPredefinedTriangleCoordinatesGenerator(unittest.TestCase):
    """測試預定義座標三角形圖形生成器"""

    @staticmethod # 將輔助函數定義為靜態方法
    def _extract_text_from_label_static(tikz_content: str, id_prefix: str) -> Optional[str]:
        """
        從 TikZ 內容中提取指定 ID 前綴的子圖形的標籤文本。
        能夠處理類型為 'label' (使用 \node) 和 'angle_arc_with_label' (使用 \draw pic) 的情況。
        """
        text_to_return = None
        
        # 嘗試匹配 'label' 類型的註釋和 \node
        # 例如: % 子圖形 label_side_a_BC (類型: label) ... \node ... {TEXT};
        # 正則表達式解釋:
        # fr"% 子圖形 {id_prefix} \(類型: label\)" : 匹配註釋頭
        # .*? : 非貪婪匹配任意字符
        # \\node(?:\[[^\]]*\])? : 匹配 \node 和可選的 [...] 選項
        # \s*at\s*\(.*?\) : 匹配 at (coordinates)
        # \s*\{{([^{{}}]*)\}}; : 匹配並捕獲 {TEXT} 中的 TEXT
        label_match = re.search(
            fr"% 子圖形 {id_prefix} \(類型: label\).*?\\node(?:\[[^\]]*\])?\s*at\s*\(.*?\)\s*\{{([^{{}}]*)\}};",
            tikz_content,
            re.DOTALL
        )
        if label_match:
            text_to_return = label_match.group(1)
        else:
            # 嘗試匹配 'angle_arc_with_label' 類型的註釋和 \draw pic
            # 例如: % 子圖形 angle_arc_angle_A (類型: angle_arc_with_label) ... \draw pic[..., "TEXT", ...] {angle=...};
            # 正則表達式解釋:
            # fr"% 子圖形 {id_prefix} \(類型: angle_arc_with_label\)" : 匹配註釋頭
            # .*? : 非貪婪匹配任意字符
            # \\draw\s+pic\s*\[ : 匹配 \draw pic[
            # [^\]]*? : 非貪婪匹配選項內的任意字符
            # \"([^\"]*)\" : 匹配並捕獲 "TEXT" 中的 TEXT
            # [^\]]*? : 非貪婪匹配標籤後的剩餘選項
            # \]\s*{{angle=.*?}}; : 匹配 pic 命令的結尾
            angle_arc_match = re.search(
                fr"% 子圖形 {id_prefix} \(類型: angle_arc_with_label\).*?\\draw\s+pic\s*\[[^\]]*?\"([^\"]*)\"[^\]]*?\]\s*{{angle=.*?}};",
                tikz_content,
                re.DOTALL
            )
            if angle_arc_match:
                text_to_return = angle_arc_match.group(1)
        
        if text_to_return is not None:
            cleaned_text = text_to_return.strip()
            # 移除可能的 LaTeX 數學模式定界符 $...$
            if cleaned_text.startswith('$') and cleaned_text.endswith('$') and len(cleaned_text) > 1:
                cleaned_text = cleaned_text[1:-1]
            # 移除末尾的度數符號 ° 以便進行 float 轉換
            return cleaned_text.rstrip('°').strip()
        return None

    def setUp(self):
        """設置測試環境"""
        try:
            self.generator_cls = get_figure_generator('predefined_triangle_coordinates')
            self.generator = self.generator_cls()
        except ValueError as e:
            self.fail(f"無法獲取 predefined_triangle_coordinates 生成器: {e}")

    def test_generate_valid_triangle(self):
        """測試生成有效三角形的 TikZ 代碼"""
        params = {
            "variant": "question",
            "point_A": [0, 0],
            "point_B": [3, 0],
            "point_C": [0, 4],
            "show_vertex_labels": True,
            "vertex_A_label": "A",
            "vertex_B_label": "B",
            "vertex_C_label": "C",
            "show_side_a_label": True, # BC (length 5)
            "side_a_label_value": "?",
            "show_side_b_label": True, # AC (length 4)
            "side_b_label_value": "4cm",
            "show_side_c_label": True, # AB (length 3)
            "show_angle_A_label": True,
            "show_angle_B_label": True, # 確保測試所有角度
            "show_angle_C_label": True,
        }
        
        tikz_content = self.generator.generate_tikz(params)

        # 使用靜態方法提取標籤
        extract_text_from_label = lambda id_prefix: TestPredefinedTriangleCoordinatesGenerator._extract_text_from_label_static(tikz_content, id_prefix)

        self.assertIn("(0.000, 0.000)", tikz_content)
        self.assertIn("(3.000, 0.000)", tikz_content)
        self.assertIn("(0.000, 4.000)", tikz_content)
        self.assertIn("--", tikz_content)

        self.assertIn("A", tikz_content)
        self.assertIn("B", tikz_content)
        self.assertIn("C", tikz_content)

        # 檢查邊長標籤
        self.assertIn("label_side_a_BC", tikz_content)
        self.assertEqual(extract_text_from_label("label_side_a_BC"), "5.0")

        self.assertIn("label_side_b_CA", tikz_content)
        self.assertEqual(extract_text_from_label("label_side_b_CA"), "4cm")

        self.assertIn("label_side_c_AB", tikz_content)
        self.assertEqual(extract_text_from_label("label_side_c_AB"), "3.0")
        
        # 檢查角度標籤
        self.assertIn("angle_arc_angle_A", tikz_content) # 更新 ID
        angle_A_text = extract_text_from_label("angle_arc_angle_A") # 更新 ID
        self.assertIsNotNone(angle_A_text, "找不到 angle_A 的標籤文本")
        self.assertAlmostEqual(float(angle_A_text), 90.0, places=1)

        self.assertIn("angle_arc_angle_B", tikz_content) # 更新 ID
        angle_B_text = extract_text_from_label("angle_arc_angle_B") # 更新 ID
        self.assertIsNotNone(angle_B_text, "找不到 angle_B 的標籤文本")
        self.assertAlmostEqual(float(angle_B_text), 53.1, places=1)

        self.assertIn("angle_arc_angle_C", tikz_content) # 更新 ID
        angle_C_text = extract_text_from_label("angle_arc_angle_C") # 更新 ID
        self.assertIsNotNone(angle_C_text, "找不到 angle_C 的標籤文本")
        self.assertAlmostEqual(float(angle_C_text), 36.9, places=1)

    def test_collinear_points(self):
        """測試三點共線的情況"""
        # 原 test_collinear_points 內容
        params = {
            "variant": "question",
            "point_A": [0, 0],
            "point_B": [1, 1],
            "point_C": [2, 2], # 共線
        }
        tikz_content = self.generator.generate_tikz(params)
        self.assertIn("無法構成三角形：提供的三個點共線。", tikz_content)
        self.assertIn("color=red", tikz_content)

    def test_parameter_validation_error(self):
        """測試 Pydantic 參數驗證錯誤"""
        # 修改測試用例以觸發 Pydantic 錯誤 (例如，類型錯誤)
        params = {
            "variant": "question",
            "point_A": [0, 0],
            "point_B": [1, 1],
            "point_C": "not_a_valid_tuple_or_list", # 提供錯誤類型
        }
        tikz_content = self.generator.generate_tikz(params)
        # 調整斷言以匹配可能的 Pydantic v2 錯誤訊息
        self.assertIn("參數驗證失敗", tikz_content)
        # Pydantic v2 的錯誤訊息可能不直接包含字段名 'point_C'，而是關於類型
        self.assertIn("tuple", tikz_content) # 檢查是否提及期望的類型
        self.assertIn("color=red", tikz_content)

    def test_no_labels(self):
        """測試不顯示任何標籤的情況"""
        params = {
            "variant": "question",
            "point_A": [0, 0],
            "point_B": [1, 0],
            "point_C": [0, 1],
            "show_vertex_labels": False,
            "show_side_a_label": False,
            "show_side_b_label": False,
            "show_side_c_label": False,
            "show_angle_A_label": False,
            "show_angle_B_label": False,
            "show_angle_C_label": False,
        }
        tikz_content = self.generator.generate_tikz(params)
        
        self.assertNotIn("label_vertex_A", tikz_content)
        self.assertNotIn("label_side_a_BC", tikz_content)
        self.assertNotIn("label_angle_A", tikz_content)
        # 確保仍然繪製了線 (檢查座標點, 嚴格3位小數)
        self.assertIn("(0.000, 0.000)", tikz_content)
        self.assertIn("(1.000, 0.000)", tikz_content)
        self.assertIn("(0.000, 1.000)", tikz_content)
        self.assertIn("--", tikz_content) # 確保有線段連接符

if __name__ == "__main__":
    # 為了能直接運行此文件進行測試，可能需要調整 PYTHONPATH
    # 例如，從項目根目錄運行 python -m unittest tests.test_figure_triangle_coordinates
    unittest.main()