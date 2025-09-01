#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
測試 figures.predefined.predefined_triangle 模塊
"""

import unittest
import math
from pydantic import ValidationError

from figures import get_figure_generator
from figures.params_models import PredefinedTriangleParams, PointTuple, VertexDisplayConfig
from figures.predefined.predefined_triangle import PredefinedTriangleGenerator

class TestPredefinedTriangleGenerator(unittest.TestCase):
    """測試 PredefinedTriangleGenerator"""

    def setUp(self):
        self.generator_cls = PredefinedTriangleGenerator
        self.generator = self.generator_cls()

    def test_get_name(self):
        """測試 get_name 方法"""
        self.assertEqual(self.generator_cls.get_name(), "predefined_triangle")

    def test_registration(self):
        """測試生成器是否已通過 get_figure_generator 正確註冊"""
        try:
            retrieved_generator_cls = get_figure_generator("predefined_triangle")
            self.assertIs(retrieved_generator_cls, self.generator_cls)
        except ValueError:
            self.fail("PredefinedTriangleGenerator 未能通過 get_figure_generator 正確獲取。")

    def test_generate_tikz_basic_outline_sss(self):
        """測試僅生成SSS三角形輪廓 (無額外標記)"""
        params_dict = {
            "variant": "question",
            "definition_mode": "sss",
            "side_a": 3.0,
            "side_b": 4.0,
            "side_c": 5.0,
            # 禁用所有標籤和特殊點的顯示
            "vertex_p1_display_config": {"show_point": False, "show_label": False},
            "vertex_p2_display_config": {"show_point": False, "show_label": False},
            "vertex_p3_display_config": {"show_point": False, "show_label": False},
            "side_p1p2_display_config": {"show_label": False},
            "side_p2p3_display_config": {"show_label": False},
            "side_p3p1_display_config": {"show_label": False},
            "angle_at_p1_display_config": {"show_arc": False, "show_label": False},
            "angle_at_p2_display_config": {"show_arc": False, "show_label": False},
            "angle_at_p3_display_config": {"show_arc": False, "show_label": False},
            "triangle_draw_options": "draw=blue, thick", # 確保基礎三角形被畫出
        }
        
        # 預期 p1=(0,0), p2=(5,0), p3=(3.2,2.4)
        # 預期 BasicTriangleGenerator 的輸出, 經過 .7g 格式化後
        # 0.0 -> "0", 5.0 -> "5", 3.2 -> "3.2", 2.4 -> "2.4"
        expected_tikz_part = "\\draw[draw=blue, thick] (0,0) -- (5,0) -- (3.2,2.4) -- cycle;"
        
        generated_tikz = self.generator.generate_tikz(params_dict)
        
        # 由於可能還有其他默認生成的註釋或空行，我們檢查核心部分
        self.assertIn(expected_tikz_part, generated_tikz)
        
        # 也可以檢查不應出現的內容，例如 \node (標籤) 或 arc (角弧)
        self.assertNotIn("\\node", generated_tikz)
        self.assertNotIn("arc", generated_tikz) # 除非 draw_options 包含 "arc"

    def test_params_validation_sss_missing_side(self):
        """測試 PredefinedTriangleParams 的 SSS 模式缺少邊長時的驗證"""
        params_dict = {
            "variant": "question",
            "definition_mode": "sss",
            "side_a": 3.0,
            "side_b": 4.0,
            # side_c is missing
        }
        with self.assertRaisesRegex(ValueError, "SSS模式需要 side_a, side_b, side_c。"):
            self.generator.generate_tikz(params_dict)

    def test_generate_tikz_with_vertex_labels_and_points(self):
        """測試帶頂點標籤和點標記的三角形"""
        p1_coord: PointTuple = (0.0, 0.0)
        p2_coord: PointTuple = (4.0, 0.0)
        p3_coord: PointTuple = (2.0, 3.0)
        
        params_dict = {
            "variant": "question",
            "definition_mode": "coordinates",
            "p1": p1_coord, "p2": p2_coord, "p3": p3_coord,
            
            "vertex_p1_display_config": {
                "show_point": True,
                "point_style": {"color": "red", "tikz_scale": 1.2}, # tikz_scale not used yet by current point drawing
                "show_label": True,
                "label_style": {"text_override": "P1_custom", "color": "magenta"}
            },
            "vertex_p2_display_config": { # Use default label text 'B'
                "show_point": True,
                "show_label": True
            },
            "vertex_p3_display_config": { # Only point, no label
                "show_point": True,
                "point_style": {"color": "green"},
                "show_label": False
            },
            "default_vertex_labels": ["A", "B", "C"], # P2 should use 'B'
            "global_label_default_offset": 0.2,

            # Disable other elements for focused test
            "side_p1p2_display_config": {"show_label": False},
            "side_p2p3_display_config": {"show_label": False},
            "side_p3p1_display_config": {"show_label": False},
            "angle_at_p1_display_config": {"show_arc": False, "show_label": False},
            "angle_at_p2_display_config": {"show_arc": False, "show_label": False},
            "angle_at_p3_display_config": {"show_arc": False, "show_label": False},
        }

        generated_tikz = self.generator.generate_tikz(params_dict)
        # print("\nGenerated TikZ (Vertex Labels Test):\n", generated_tikz) # For debugging

        # 1. Check base triangle
        self.assertIn("\\draw[thin, black] (0,0) -- (4,0) -- (2,3) -- cycle;", generated_tikz)

        # 2. Check P1 point and label
        self.assertIn("\\filldraw[red] (0,0) circle (1.5pt);", generated_tikz) # P1 point
        # P1 label: text "P1_custom", color "magenta", anchor "center"
        self.assertIn("\\node[anchor=center, color=magenta", generated_tikz)
        self.assertIn("P1_custom", generated_tikz)

        # 3. Check P2 point and label
        self.assertIn("\\filldraw[black] (4,0) circle (1.5pt);", generated_tikz) # P2 point (default color black)
        # P2 label: default text "B", default color "black", anchor "center"
        self.assertIn("\\node[anchor=center, color=black", generated_tikz)
        self.assertIn("{$B$}", generated_tikz) # Default math mode

        # 4. Check P3 point (no label)
        self.assertIn("\\filldraw[green] (2,3) circle (1.5pt);", generated_tikz) # P3 point
        # Ensure P3 default label "C" is NOT present if show_label is False
        # This is tricky because "C" might appear in color spec like "cyan"
        # A more robust check would be to count \node occurrences or parse.
        # For now, let's assume if "{$C$}" is not there, it's good.
        # A better check: count nodes. There should be 2 label nodes.
        self.assertEqual(generated_tikz.count("\\node"), 2, "Should only be two labels (P1_custom, B)")


    # TODO: 添加更多集成測試用例:
    # - 帶邊標籤 (next)
    # - 帶角標記 (弧和值)
    # - 帶特殊點
    # - 不同 definition_mode (sas, asa, aas)
    # - 測試樣式覆蓋是否生效 (more deeply)
    # - 測試 label_text_type 和 custom_label_text 的不同組合

    def test_generate_tikz_with_side_labels(self):
        """測試帶邊標籤的三角形"""
        p1_coord: PointTuple = (0.0, 0.0)
        p2_coord: PointTuple = (5.0, 0.0) # side_c = 5
        p3_coord: PointTuple = (0.0, 3.0) # side_b = 3, side_a = sqrt(5^2+3^2) = sqrt(34) ~ 5.83
        
        params_dict = {
            "variant": "question",
            "definition_mode": "coordinates",
            "p1": p1_coord, "p2": p2_coord, "p3": p3_coord,
            
            "vertex_p1_display_config": {"show_point": False, "show_label": False},
            "vertex_p2_display_config": {"show_point": False, "show_label": False},
            "vertex_p3_display_config": {"show_point": False, "show_label": False},

            "side_p1p2_display_config": { # Side c
                "show_label": True,
                "label_text_type": "length",
                "length_format": "c={value:.1f}",
                "label_style": {"color": "blue"}
            },
            "side_p2p3_display_config": { # Side a
                "show_label": True,
                "label_text_type": "default_name", # Should use 'a' from default_side_names
                "label_style": {"color": "green", "math_mode": False} # Default name 'a' is not math
            },
            "side_p3p1_display_config": { # Side b
                "show_label": True,
                "label_text_type": "custom",
                "custom_label_text": "Side b is {value:.2f} units",
                "length_format": "{value:.2f}", # Used by custom_label_text's {value}
                "label_style": {"color": "purple", "font_size": "\\scriptsize"}
            },
            "default_side_names": ["c", "a", "b"], # For P1P2, P2P3, P3P1
            "global_label_default_offset": 0.1, # Smaller offset for sides

            "angle_at_p1_display_config": {"show_arc": False, "show_label": False},
            "angle_at_p2_display_config": {"show_arc": False, "show_label": False},
            "angle_at_p3_display_config": {"show_arc": False, "show_label": False},
            "triangle_draw_options": "black",
        }

        generated_tikz = self.generator.generate_tikz(params_dict)
        # print("\nGenerated TikZ (Side Labels Test):\n", generated_tikz)

        # 1. Check base triangle
        self.assertIn("\\draw[black] (0,0) -- (5,0) -- (0,3) -- cycle;", generated_tikz)

        # 2. Check side P1P2 (side c) label: "c=5.0", blue, rotation 0
        # Placement depends on get_label_placement_params. Midpoint (2.5,0), normal (0,-1) (pointing out)
        # Ref point (2.5, -0.1)
        # LabelGenerator will use math_mode=False for text "c=5.0", but won't add "math_mode=false" to TikZ options.
        self.assertIn("\\node[anchor=center, rotate=0, color=blue]", generated_tikz)
        self.assertIn("{c=5.0}", generated_tikz)

        # 3. Check side P2P3 (side a) label: "a", green
        # Rotation: atan2(3, -5) = 2.60117 rad = 149.036 deg. Adjusted: 149.036 - 180 = -30.963...
        # LabelGenerator formats rotate with .7g: f"{-30.963759...:.7g}" -> "-30.96376"
        self.assertIn("\\node[anchor=center, rotate=-30.96376, color=green]", generated_tikz)
        self.assertIn("{a}", generated_tikz) # math_mode=false was explicitly set in PredefinedTriangleGenerator for this

        # 4. Check side P3P1 (side b) label: "Side b is 3.00 units", purple, scriptsize, rotation -90
        # Midpoint (0, 1.5), normal (-1,0) (pointing out)
        # side_dx = 0, side_dy = -3. atan2(-3,0) = -pi/2 = -90 deg.
        # LabelGenerator will use math_mode=False, but not add "math_mode=false" to TikZ options.
        self.assertIn("\\node[anchor=center, rotate=-90, color=purple, font=\\scriptsize]", generated_tikz)
        self.assertIn("{Side b is 3.00 units}", generated_tikz)
        
        # Check number of labels
        self.assertEqual(generated_tikz.count("\\node"), 3, "Should be three side labels")

    def test_generate_tikz_with_angle_markers(self):
        """測試帶角標記 (角弧和角度值) 的三角形"""
        # Right angle triangle: P1(0,0), P2(3,0), P3(0,4)
        # Angles: P1=atan2(4,3)~53.13, P2=90, P3=atan2(3,4)~36.87
        p1_coord: PointTuple = (0.0, 0.0)
        p2_coord: PointTuple = (3.0, 0.0)
        p3_coord: PointTuple = (0.0, 4.0)

        params_dict = {
            "variant": "question",
            "definition_mode": "coordinates",
            "p1": p1_coord, "p2": p2_coord, "p3": p3_coord,

            "vertex_p1_display_config": {"show_point": False, "show_label": False},
            "vertex_p2_display_config": {"show_point": False, "show_label": False},
            "vertex_p3_display_config": {"show_point": False, "show_label": False},
            "side_p1p2_display_config": {"show_label": False},
            "side_p2p3_display_config": {"show_label": False},
            "side_p3p1_display_config": {"show_label": False},

            "angle_at_p1_display_config": { # Angle A ~ 53.1 deg
                "show_arc": True,
                "arc_style": {"draw_options": "red,thin"},
                "show_label": True,
                "label_text_type": "value", # Show calculated value
                "value_format": "{value:.0f}deg", # Custom format
                "label_style": {"color": "red", "font_size": "\\tiny"}
            },
            "angle_at_p2_display_config": { # Angle B = 90 deg
                "show_arc": True,
                # TODO: Test right_angle_symbol if get_arc_render_params supports it via config
                "arc_style": {"draw_options": "blue"},
                "show_label": True,
                "label_text_type": "custom",
                "custom_label_text": "Right", # Custom text
                "label_style": {"color": "blue"}
            },
            "angle_at_p3_display_config": { # Angle C ~ 36.9 deg
                "show_arc": False, # No arc for P3
                "show_label": True,
                "label_text_type": "default_name", # Should use 'C'
                "label_style": {"color": "green"}
            },
            "default_angle_names": ["Alpha", "Beta", "Gamma"], # P3 should use "Gamma"
            "global_angle_arc_radius_config": 0.5, # Fixed radius for arcs in this test
            "global_label_default_offset": 0.15,
            "triangle_draw_options": "black",
        }

        generated_tikz = self.generator.generate_tikz(params_dict)
        # print("\nGenerated TikZ (Angle Markers Test):\n", generated_tikz)

        # 1. Check base triangle
        self.assertIn("\\draw[black] (0,0) -- (3,0) -- (0,4) -- cycle;", generated_tikz)

        # 2. Angle at P1 (~53.1 deg)
        # Arc: center (0,0), radius 0.5, start_angle (P1P3) ~ 90deg, end_angle (P1P2) = 0deg.
        # ArcGenerator uses .7g. For P1 (0,0), arm P1P2 (3,0) is angle 0, arm P1P3 (0,4) is angle 90.
        # Cross product (P1P2 x P1P3) is 3*4 - 0*0 = 12 > 0. So, tikz_start=0, tikz_end=90.
        self.assertIn("\\draw[red,thin] (0.5,0) arc (0:90:0.5);", generated_tikz) # Arc for P1
        # Label: P1 is a 90deg angle. value_format="{value:.0f}deg" -> "90deg"
        # Text "90deg" does not contain "°", so math_mode will be True by default from LabelParams.
        self.assertIn("\\node[anchor=center, rotate=0, color=red, font=\\tiny]", generated_tikz) # Removed math_mode=true check
        self.assertIn("{$90deg$}", generated_tikz) # P1 is 90 deg.

        # 3. Angle at P2 (actual angle ~53.13 deg)
        # Vertex P2(3,0). arm_pt1=P1(0,0), arm_pt2=P3(0,4).
        # raw_start (P2P1) = 180 deg. raw_end (P2P3) = atan2(4,-3) ~ 126.8699 deg.
        # Cross product (P2P1 x P2P3) is negative. So, tikz_start=126.8699, tikz_end=180.
        # Arc start point: x = 3 + 0.5*cos(126.8699deg) = 2.7. y = 0 + 0.5*sin(126.8699deg) = 0.4.
        # Angles for arc command: 126.8699, 180 (formatted by .7g)
        self.assertIn("\\draw[blue] (2.7,0.4) arc (126.8699:180:0.5);", generated_tikz) # Arc for P2
        # Label: "Right" (custom text), blue.
        self.assertIn("\\node[anchor=center, rotate=0, color=blue]", generated_tikz) # Default math_mode for label
        self.assertIn("{Right}", generated_tikz) # Custom text is not necessarily math

        # 4. Angle at P3 (actual angle ~36.87 deg) - No arc, only label
        # Label: "Gamma" (default_angle_names[2]), green.
        # Check that no new arc for P3 was drawn. Count existing arcs.
        # Count occurrences of "arc (" to ensure only 2 arcs are present.
        # self.assertNotIn("arc (", generated_tikz.split("cycle;")[-1]) # This check is weak
        self.assertIn("\\node[anchor=center, rotate=0, color=green]", generated_tikz)
        self.assertIn("{$Gamma$}", generated_tikz) # Expecting math mode for default_name
        
        # Check number of labels and arcs
        self.assertEqual(generated_tikz.count("\\node"), 3, "Should be three angle labels")
        self.assertEqual(generated_tikz.count("\\draw") -1, 2, "Should be two arcs + 1 triangle draw")


if __name__ == "__main__":
    unittest.main()

    def test_generate_tikz_with_special_points(self):
        """測試帶特殊點 (例如質心) 的三角形"""
        p1_coord: PointTuple = (0.0, 0.0)
        p2_coord: PointTuple = (6.0, 0.0)
        p3_coord: PointTuple = (3.0, 3.0 * math.sqrt(3)) # Equilateral triangle for easy centroid (3, sqrt(3))
        
        params_dict = {
            "variant": "question",
            "definition_mode": "coordinates",
            "p1": p1_coord, "p2": p2_coord, "p3": p3_coord,
            
            "vertex_p1_display_config": {"show_point": False, "show_label": False},
            "vertex_p2_display_config": {"show_point": False, "show_label": False},
            "vertex_p3_display_config": {"show_point": False, "show_label": False},
            "side_p1p2_display_config": {"show_label": False},
            "side_p2p3_display_config": {"show_label": False},
            "side_p3p1_display_config": {"show_label": False},
            "angle_at_p1_display_config": {"show_arc": False, "show_label": False},
            "angle_at_p2_display_config": {"show_arc": False, "show_label": False},
            "angle_at_p3_display_config": {"show_arc": False, "show_label": False},

            "display_centroid": {
                "show_point": True,
                "point_style": {"color": "orange", "tikz_scale": 0.8}, # tikz_scale not used yet
                "show_label": True,
                "label_text": "G_cent", # Custom label text
                "label_style": {"color": "orange", "font_size": "\\small"}
            },
            "display_incenter": { # Test another special point with default label
                "show_point": True,
                "show_label": True
            },
            "default_special_point_labels": {"incenter": "I_default"}, # Override default for incenter
            "global_label_default_offset": 0.1,
            "triangle_draw_options": "gray, very thin",
        }

        generated_tikz = self.generator.generate_tikz(params_dict)
        # print("\nGenerated TikZ (Special Points Test):\n", generated_tikz)

        # 1. Check base triangle
        self.assertIn("\\draw[gray, very thin] (0,0) -- (6,0) -- (3,5.196152) -- cycle;", generated_tikz) # 3*sqrt(3) ~ 5.196152

        # 2. Check Centroid G_cent
        # Centroid of (0,0), (6,0), (3, 3*sqrt(3)) is ( (0+6+3)/3, (0+0+3*sqrt(3))/3 ) = (3, sqrt(3))
        # sqrt(3) ~ 1.73205
        centroid_x_str = "3"
        centroid_y_str = "1.732051" # from f"{math.sqrt(3):.7g}"
        self.assertIn(f"\\filldraw[orange] ({centroid_x_str},{centroid_y_str}) circle (1.2pt);", generated_tikz)
        # Label "G_cent", orange, small. Placement by get_label_placement_params.
        self.assertIn("\\node[anchor=centerenter, color=orange, font=\\small", generated_tikz)
        self.assertIn("{$G_cent$}", generated_tikz) # Default math_mode True

        # 3. Check Incenter I_default
        # For equilateral triangle, incenter is same as centroid.
        incenter_x_str = centroid_x_str
        incenter_y_str = centroid_y_str
        self.assertIn(f"\\filldraw[gray] ({incenter_x_str},{incenter_y_str}) circle (1.2pt);", generated_tikz) # Default color gray
        # Label "I_default", darkgray (default for special point labels if color not in style)
        self.assertIn("\\node[anchor=centerenter, color=darkgray", generated_tikz)
        self.assertIn("{$I_default$}", generated_tikz)

        # Check number of labels and points
        # 2 special point labels + 0 vertex/side/angle labels = 2 nodes
        self.assertEqual(generated_tikz.count("\\node"), 2, "Should be two special point labels")
        # 2 special points + 0 vertex points = 2 filldraw circles
        self.assertEqual(generated_tikz.count("\\filldraw"), 2, "Should be two special points drawn")