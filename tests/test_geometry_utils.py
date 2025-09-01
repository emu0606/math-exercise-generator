#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
測試 utils.geometry_utils 模塊
"""

import unittest
import math

# 假設 utils 和 tests 是同級目錄，並且測試是從項目根目錄運行的
# 或者 Python 環境已配置為能找到 utils 包
from utils.geometry_utils import get_vertices, Point, TriangleDefinitionError, get_midpoint, get_centroid, get_incenter, get_circumcenter, get_orthocenter, get_arc_render_params, get_label_placement_params, _distance

# 輔助函數，用於比較浮點數元組 (點)
def assertPointAlmostEqual(test_case, p1: Point, p2: Point, places=7, msg=None):
    test_case.assertAlmostEqual(p1[0], p2[0], places=places, msg=f"{msg} (x座標)" if msg else "x座標不匹配")
    test_case.assertAlmostEqual(p1[1], p2[1], places=places, msg=f"{msg} (y座標)" if msg else "y座標不匹配")

class TestGetVerticesSSS(unittest.TestCase):
    """測試 get_vertices SSS 模式"""

    def test_sss_right_triangle_3_4_5(self):
        """測試 SSS 直角三角形 (3,4,5)"""
        # a=3 (P2P3), b=4 (P1P3), c=5 (P1P2)
        p1, p2, p3 = get_vertices(definition_mode='sss', side_a=3.0, side_b=4.0, side_c=5.0)
        
        expected_p1: Point = (0.0, 0.0)
        expected_p2: Point = (5.0, 0.0)
        # x = (4^2 + 5^2 - 3^2) / (2*5) = (16+25-9)/10 = 32/10 = 3.2
        # y = sqrt(4^2 - 3.2^2) = sqrt(16 - 10.24) = sqrt(5.76) = 2.4
        expected_p3: Point = (3.2, 2.4)
        
        assertPointAlmostEqual(self, p1, expected_p1, msg="P1 座標不正確")
        assertPointAlmostEqual(self, p2, expected_p2, msg="P2 座標不正確")
        assertPointAlmostEqual(self, p3, expected_p3, msg="P3 座標不正確")

        # 逆向驗證邊長
        dist_p1p2 = math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)
        dist_p1p3 = math.sqrt((p3[0]-p1[0])**2 + (p3[1]-p1[1])**2)
        dist_p2p3 = math.sqrt((p3[0]-p2[0])**2 + (p3[1]-p2[1])**2)

        self.assertAlmostEqual(dist_p1p2, 5.0, places=7, msg="P1P2 邊長 (c) 不正確")
        self.assertAlmostEqual(dist_p1p3, 4.0, places=7, msg="P1P3 邊長 (b) 不正確")
        self.assertAlmostEqual(dist_p2p3, 3.0, places=7, msg="P2P3 邊長 (a) 不正確")

    def test_sss_equilateral_triangle(self):
        """測試 SSS 等邊三角形"""
        side = 6.0
        p1, p2, p3 = get_vertices(definition_mode='sss', side_a=side, side_b=side, side_c=side)
        
        expected_p1: Point = (0.0, 0.0)
        expected_p2: Point = (side, 0.0)
        # x = (s^2 + s^2 - s^2) / (2s) = s^2 / (2s) = s/2
        # y = sqrt(s^2 - (s/2)^2) = sqrt(s^2 - s^2/4) = sqrt(3s^2/4) = (s * sqrt(3)) / 2
        expected_p3_x = side / 2.0
        expected_p3_y = (side * math.sqrt(3)) / 2.0
        expected_p3: Point = (expected_p3_x, expected_p3_y)
        
        assertPointAlmostEqual(self, p1, expected_p1, msg="等邊 P1")
        assertPointAlmostEqual(self, p2, expected_p2, msg="等邊 P2")
        assertPointAlmostEqual(self, p3, expected_p3, msg="等邊 P3")

    def test_sss_invalid_triangle_inequality(self):
        """測試 SSS 不滿足三角形不等式"""
        with self.assertRaisesRegex(TriangleDefinitionError, "不滿足三角形不等式"):
            get_vertices(definition_mode='sss', side_a=1.0, side_b=2.0, side_c=5.0)

    def test_sss_zero_side_length(self):
        """測試 SSS 邊長為零或負數，這些情況通常會先不滿足三角形不等式"""
        with self.assertRaisesRegex(TriangleDefinitionError, "不滿足三角形不等式"): # 0+4 > 5 is False
            get_vertices(definition_mode='sss', side_a=0.0, side_b=4.0, side_c=5.0)
        with self.assertRaisesRegex(TriangleDefinitionError, "不滿足三角形不等式"): # 3-1 > 5 is False
            get_vertices(definition_mode='sss', side_a=3.0, side_b=-1.0, side_c=5.0)
        # side_c=0.0 的情況，會導致 p3_x 計算中的除零錯誤，或者不等式檢查失敗
        # 例如 3+0 > 4 is False
        with self.assertRaisesRegex(TriangleDefinitionError, "不滿足三角形不等式"):
            get_vertices(definition_mode='sss', side_a=3.0, side_b=4.0, side_c=0.0)
            
    def test_sss_discriminant_slightly_negative_due_to_float_error(self):
        """測試 SSS 由於浮點誤差導致判別式略微為負的情況"""
        # 這種情況很難精確構造，但我們的代碼中有 discriminant < -1e-9 的檢查
        # 這裡我們嘗試一個非常接近退化但理論上有效的三角形
        # 例如 a=2.00000001, b=1.0, c=1.0 (P1P2=1, P1P3=1, P2P3=2.00000001)
        # x = (1^2 + 1^2 - 2.00000001^2) / (2*1) = (2 - 4.00000004) / 2 = -1.00000002
        # discriminant = b^2 - x^2 = 1^2 - (-1.00000002)^2 = 1 - 1.00000004... 會是負數
        # 預期 TriangleDefinitionError 因為它首先不滿足三角形不等式
        with self.assertRaisesRegex(TriangleDefinitionError, "不滿足三角形不等式"):
             get_vertices(definition_mode='sss', side_a=2.00000001, side_b=1.0, side_c=1.0)


class TestGetVerticesCoordinates(unittest.TestCase):
    """測試 get_vertices coordinates 模式"""

    def test_coordinates_basic(self):
        p1_in, p2_in, p3_in = (1.0, 2.0), (3.0, 4.0), (5.0, 0.0)
        p1, p2, p3 = get_vertices(definition_mode='coordinates', p1=p1_in, p2=p2_in, p3=p3_in)
        assertPointAlmostEqual(self, p1, p1_in, msg="Coord P1")
        assertPointAlmostEqual(self, p2, p2_in, msg="Coord P2")
        assertPointAlmostEqual(self, p3, p3_in, msg="Coord P3")

    def test_coordinates_missing_param(self):
        with self.assertRaisesRegex(ValueError, "參數是必需的"):
            get_vertices(definition_mode='coordinates', p1=(0,0), p2=(1,0)) # p3 is missing

    def test_coordinates_invalid_type(self):
        with self.assertRaisesRegex(ValueError, "座標點必須是包含兩個數字"):
            get_vertices(definition_mode='coordinates', p1=(0,0), p2=(1,0), p3="invalid")
        with self.assertRaisesRegex(ValueError, "座標點必須是包含兩個數字"):
            get_vertices(definition_mode='coordinates', p1=(0,0), p2=(1,0), p3=(1,2,3))
        with self.assertRaisesRegex(ValueError, "座標點必須是包含兩個數字"):
            get_vertices(definition_mode='coordinates', p1=(0,0), p2=(1,0), p3=(1,'a'))


class TestGetVerticesSAS(unittest.TestCase):
    """測試 get_vertices SAS 模式"""

    def test_sas_right_triangle(self):
        """測試 SAS 直角三角形 (3, 90deg, 4)"""
        side1 = 3.0
        angle_rad = math.pi / 2.0 # 90 degrees
        side2 = 4.0
        p1, p2, p3 = get_vertices(definition_mode='sas', side1=side1, angle_rad=angle_rad, side2=side2)

        expected_p1: Point = (0.0, 0.0)
        expected_p2: Point = (side1, 0.0) # (3.0, 0.0)
        expected_p3: Point = (0.0, side2) # (0.0, 4.0) (since cos(pi/2)=0, sin(pi/2)=1)
        
        assertPointAlmostEqual(self, p1, expected_p1, msg="SAS Right P1")
        assertPointAlmostEqual(self, p2, expected_p2, msg="SAS Right P2")
        assertPointAlmostEqual(self, p3, expected_p3, msg="SAS Right P3")

        # 逆向驗證第三邊長 (斜邊)
        dist_p2p3 = math.sqrt((p3[0]-p2[0])**2 + (p3[1]-p2[1])**2)
        expected_hypotenuse = math.sqrt(side1**2 + side2**2) # sqrt(3^2+4^2) = 5
        self.assertAlmostEqual(dist_p2p3, expected_hypotenuse, places=7, msg="SAS Right Hypotenuse")

    def test_sas_equilateral_triangle_equivalent(self):
        """測試 SAS 等邊三角形 (side, 60deg, side)"""
        side = 5.0
        angle_rad = math.pi / 3.0 # 60 degrees
        p1, p2, p3 = get_vertices(definition_mode='sas', side1=side, angle_rad=angle_rad, side2=side)

        expected_p1: Point = (0.0, 0.0)
        expected_p2: Point = (side, 0.0) # (5.0, 0.0)
        expected_p3_x = side * math.cos(angle_rad) # 5 * 0.5 = 2.5
        expected_p3_y = side * math.sin(angle_rad) # 5 * sqrt(3)/2
        expected_p3: Point = (expected_p3_x, expected_p3_y)

        assertPointAlmostEqual(self, p1, expected_p1, msg="SAS Equilateral P1")
        assertPointAlmostEqual(self, p2, expected_p2, msg="SAS Equilateral P2")
        assertPointAlmostEqual(self, p3, expected_p3, msg="SAS Equilateral P3")
        
        # 逆向驗證第三邊長
        dist_p2p3 = math.sqrt((p3[0]-p2[0])**2 + (p3[1]-p2[1])**2)
        self.assertAlmostEqual(dist_p2p3, side, places=7, msg="SAS Equilateral third side")

    def test_sas_general_triangle(self):
        """測試 SAS 一般三角形 (6, 45deg, 4)"""
        side1 = 6.0
        angle_rad = math.pi / 4.0 # 45 degrees
        side2 = 4.0
        p1, p2, p3 = get_vertices(definition_mode='sas', side1=side1, angle_rad=angle_rad, side2=side2)

        expected_p1: Point = (0.0, 0.0)
        expected_p2: Point = (side1, 0.0) # (6.0, 0.0)
        expected_p3_x = side2 * math.cos(angle_rad) # 4 * sqrt(2)/2 = 2*sqrt(2)
        expected_p3_y = side2 * math.sin(angle_rad) # 4 * sqrt(2)/2 = 2*sqrt(2)
        expected_p3: Point = (expected_p3_x, expected_p3_y)

        assertPointAlmostEqual(self, p1, expected_p1, msg="SAS General P1")
        assertPointAlmostEqual(self, p2, expected_p2, msg="SAS General P2")
        assertPointAlmostEqual(self, p3, expected_p3, msg="SAS General P3")

    def test_sas_invalid_side_length(self):
        """測試 SAS 邊長無效"""
        with self.assertRaisesRegex(TriangleDefinitionError, "必須為正數"):
            get_vertices(definition_mode='sas', side1=0.0, angle_rad=math.pi/2, side2=4.0)
        with self.assertRaisesRegex(TriangleDefinitionError, "必須為正數"):
            get_vertices(definition_mode='sas', side1=3.0, angle_rad=math.pi/2, side2=-1.0)

    def test_sas_invalid_angle(self):
        """測試 SAS 角度無效"""
        with self.assertRaisesRegex(TriangleDefinitionError, "必須在 \(0, pi\) 弧度範圍內"):
            get_vertices(definition_mode='sas', side1=3.0, angle_rad=0.0, side2=4.0)
        with self.assertRaisesRegex(TriangleDefinitionError, "必須在 \(0, pi\) 弧度範圍內"):
            get_vertices(definition_mode='sas', side1=3.0, angle_rad=math.pi, side2=4.0)
        with self.assertRaisesRegex(TriangleDefinitionError, "必須在 \(0, pi\) 弧度範圍內"):
            get_vertices(definition_mode='sas', side1=3.0, angle_rad=-math.pi/4, side2=4.0)
        with self.assertRaisesRegex(TriangleDefinitionError, "必須在 \(0, pi\) 弧度範圍內"):
            get_vertices(definition_mode='sas', side1=3.0, angle_rad=2*math.pi, side2=4.0)

    def test_sas_missing_parameters(self):
        """測試 SAS 缺少參數"""
        with self.assertRaisesRegex(ValueError, "參數是必需的"):
            get_vertices(definition_mode='sas', side1=3.0, angle_rad=math.pi/2) # missing side2
        with self.assertRaisesRegex(ValueError, "參數是必需的"):
            get_vertices(definition_mode='sas', side1=3.0, side2=4.0) # missing angle_rad
        with self.assertRaisesRegex(ValueError, "參數是必需的"):
            get_vertices(definition_mode='sas', angle_rad=math.pi/2, side2=4.0) # missing side1

    def test_sas_invalid_parameter_types(self):
        """測試 SAS 參數類型無效"""
        with self.assertRaisesRegex(ValueError, "必須是數字"):
            get_vertices(definition_mode='sas', side1="3", angle_rad=math.pi/2, side2=4.0)
        with self.assertRaisesRegex(ValueError, "必須是數字"):
            get_vertices(definition_mode='sas', side1=3.0, angle_rad="pi/2", side2=4.0)
        with self.assertRaisesRegex(ValueError, "必須是數字"):
            get_vertices(definition_mode='sas', side1=3.0, angle_rad=math.pi/2, side2="4")


class TestGetVerticesASA(unittest.TestCase):
    """測試 get_vertices ASA 模式"""

    def test_asa_isosceles_right_triangle(self):
        """ASA: 45-90-45 triangle (angle1=45, side=5, angle2=90)"""
        # P1=(0,0), P2=(5,0). Angle at P1 is 45deg, Angle at P2 is 90deg.
        # So, Angle at P3 must be 180-90-45 = 45deg.
        # This means P1P3 = P2P3.
        # Side P1P3 (side_b_equiv) using Sine Rule:
        # P1P3 / sin(P2_angle) = P1P2 / sin(P3_angle)
        # P1P3 = P1P2 * sin(P2_angle) / sin(P3_angle)
        #      = 5.0 * sin(pi/2) / sin(pi/4) = 5.0 * 1 / (sqrt(2)/2) = 5*sqrt(2)
        # P3.x = P1P3 * cos(P1_angle) = 5*sqrt(2) * cos(pi/4) = 5*sqrt(2) * (sqrt(2)/2) = 5.0
        # P3.y = P1P3 * sin(P1_angle) = 5*sqrt(2) * sin(pi/4) = 5.0
        angle1 = math.pi / 4.0 # 45 deg at P1
        side = 5.0
        angle2 = math.pi / 2.0 # 90 deg at P2
        
        p1, p2, p3 = get_vertices(definition_mode='asa', angle1_rad=angle1, side_length=side, angle2_rad=angle2)

        expected_p1: Point = (0.0, 0.0)
        expected_p2: Point = (side, 0.0) # (5.0, 0.0)
        expected_p3: Point = (side, side) # (5.0, 5.0)

        assertPointAlmostEqual(self, p1, expected_p1, msg="ASA Isosceles Right P1")
        assertPointAlmostEqual(self, p2, expected_p2, msg="ASA Isosceles Right P2")
        assertPointAlmostEqual(self, p3, expected_p3, msg="ASA Isosceles Right P3")

        # Verify side lengths: P1P2=side, P2P3=side, P1P3=side*sqrt(2)
        dist_p2p3 = math.sqrt((p3[0]-p2[0])**2 + (p3[1]-p2[1])**2)
        self.assertAlmostEqual(dist_p2p3, side, places=7, msg="ASA Isosceles Right P2P3 side")

    def test_asa_equilateral_triangle(self):
        """ASA: 60-side-60 triangle"""
        angle = math.pi / 3.0 # 60 deg
        side = 7.0
        p1, p2, p3 = get_vertices(definition_mode='asa', angle1_rad=angle, side_length=side, angle2_rad=angle)

        expected_p1: Point = (0.0, 0.0)
        expected_p2: Point = (side, 0.0) # (7.0, 0.0)
        # side_b_equiv (P1P3) = side * sin(angle) / sin(angle) = side
        expected_p3_x = side * math.cos(angle) # 7.0 * 0.5 = 3.5
        expected_p3_y = side * math.sin(angle) # 7.0 * sqrt(3)/2
        expected_p3: Point = (expected_p3_x, expected_p3_y)

        assertPointAlmostEqual(self, p1, expected_p1, msg="ASA Equilateral P1")
        assertPointAlmostEqual(self, p2, expected_p2, msg="ASA Equilateral P2")
        assertPointAlmostEqual(self, p3, expected_p3, msg="ASA Equilateral P3")
        
        # Verify all side lengths are 'side'
        dist_p1p3 = math.sqrt((p3[0]-p1[0])**2 + (p3[1]-p1[1])**2)
        dist_p2p3 = math.sqrt((p3[0]-p2[0])**2 + (p3[1]-p2[1])**2)
        self.assertAlmostEqual(dist_p1p3, side, places=7, msg="ASA Equilateral P1P3 side")
        self.assertAlmostEqual(dist_p2p3, side, places=7, msg="ASA Equilateral P2P3 side")

    def test_asa_general_triangle(self):
        """ASA: 30-10-45 triangle"""
        angle1 = math.pi / 6.0 # 30 deg
        side = 10.0
        angle2 = math.pi / 4.0 # 45 deg
        p1, p2, p3 = get_vertices(definition_mode='asa', angle1_rad=angle1, side_length=side, angle2_rad=angle2)

        expected_p1: Point = (0.0, 0.0)
        expected_p2: Point = (side, 0.0) # (10.0, 0.0)
        # angle3 = pi - pi/6 - pi/4 = 7pi/12
        # side_b_equiv (P1P3) = side * sin(angle2) / sin(angle3)
        # = 10 * (sqrt(2)/2) / ((sqrt(6)+sqrt(2))/4) = 10 * (sqrt(3)-1)
        side_b_equiv = 10.0 * (math.sqrt(3) - 1.0)
        expected_p3_x = side_b_equiv * math.cos(angle1) # 10*(sqrt(3)-1) * sqrt(3)/2 = 5*(3-sqrt(3))
        expected_p3_y = side_b_equiv * math.sin(angle1) # 10*(sqrt(3)-1) * 1/2 = 5*(sqrt(3)-1)
        expected_p3: Point = (5.0 * (3.0 - math.sqrt(3)), 5.0 * (math.sqrt(3) - 1.0))
        
        assertPointAlmostEqual(self, p1, expected_p1, msg="ASA General P1")
        assertPointAlmostEqual(self, p2, expected_p2, msg="ASA General P2")
        assertPointAlmostEqual(self, p3, expected_p3, msg="ASA General P3")

    def test_asa_invalid_side_length(self):
        with self.assertRaisesRegex(TriangleDefinitionError, "必須為正數"):
            get_vertices(definition_mode='asa', angle1_rad=math.pi/4, side_length=0, angle2_rad=math.pi/4)
        with self.assertRaisesRegex(TriangleDefinitionError, "必須為正數"):
            get_vertices(definition_mode='asa', angle1_rad=math.pi/4, side_length=-5, angle2_rad=math.pi/4)

    def test_asa_invalid_angles_range(self):
        with self.assertRaisesRegex(TriangleDefinitionError, "必須在 \(0, pi\) 弧度範圍內"):
            get_vertices(definition_mode='asa', angle1_rad=0, side_length=5, angle2_rad=math.pi/4)
        with self.assertRaisesRegex(TriangleDefinitionError, "必須在 \(0, pi\) 弧度範圍內"):
            get_vertices(definition_mode='asa', angle1_rad=math.pi/4, side_length=5, angle2_rad=math.pi)
        with self.assertRaisesRegex(TriangleDefinitionError, "必須在 \(0, pi\) 弧度範圍內"):
            get_vertices(definition_mode='asa', angle1_rad=math.pi/4, side_length=5, angle2_rad= -math.pi/4)


    def test_asa_invalid_angle_sum(self):
        with self.assertRaisesRegex(TriangleDefinitionError, "兩個輸入角的和必須小於 pi 弧度"):
            get_vertices(definition_mode='asa', angle1_rad=math.pi/2, side_length=5, angle2_rad=math.pi/2) # Sum is pi
        with self.assertRaisesRegex(TriangleDefinitionError, "兩個輸入角的和必須小於 pi 弧度"):
            get_vertices(definition_mode='asa', angle1_rad=3*math.pi/4, side_length=5, angle2_rad=math.pi/2) # Sum > pi

    def test_asa_missing_parameters(self):
        with self.assertRaisesRegex(ValueError, "參數是必需的"):
            get_vertices(definition_mode='asa', angle1_rad=math.pi/4, side_length=5) # missing angle2_rad
    
    def test_asa_invalid_parameter_types(self):
        with self.assertRaisesRegex(ValueError, "必須是數字"):
            get_vertices(definition_mode='asa', angle1_rad="pi/4", side_length=5, angle2_rad=math.pi/4)


class TestGetVerticesAAS(unittest.TestCase):
    """測試 get_vertices AAS 模式"""

    def test_aas_right_triangle_30_60_side_opp_30_is_5(self):
        """AAS: A=30, B=60, a=5 (P2P3=5) -> C=90"""
        # P1=(0,0)
        # angleA=pi/6 (30), angleB=pi/3 (60), side_a (P2P3)=5.0
        # angleC=pi - pi/6 - pi/3 = pi/2 (90)
        # side_c (P1P2) = side_a * sin(C)/sin(A) = 5 * sin(pi/2)/sin(pi/6) = 5 * 1 / 0.5 = 10.0
        # side_b (P1P3) = side_a * sin(B)/sin(A) = 5 * sin(pi/3)/sin(pi/6) = 5 * (sqrt(3)/2) / 0.5 = 5*sqrt(3)
        # P2 = (10.0, 0)
        # P3.x = side_b * cos(A) = 5*sqrt(3) * cos(pi/6) = 5*sqrt(3) * sqrt(3)/2 = 15/2 = 7.5
        # P3.y = side_b * sin(A) = 5*sqrt(3) * sin(pi/6) = 5*sqrt(3) * 0.5 = 2.5*sqrt(3)
        angle_A = math.pi / 6.0
        angle_B = math.pi / 3.0
        side_a = 5.0
        
        p1, p2, p3 = get_vertices(definition_mode='aas',
                                  angle1_rad=angle_A,
                                  angle2_rad=angle_B,
                                  side_opposite_angle1=side_a)

        expected_p1: Point = (0.0, 0.0)
        expected_p2: Point = (10.0, 0.0)
        expected_p3: Point = (7.5, 2.5 * math.sqrt(3))

        assertPointAlmostEqual(self, p1, expected_p1, msg="AAS Right P1")
        assertPointAlmostEqual(self, p2, expected_p2, msg="AAS Right P2")
        assertPointAlmostEqual(self, p3, expected_p3, msg="AAS Right P3")

        # Verify other side lengths
        dist_p1p2 = math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2) # side_c
        dist_p1p3 = math.sqrt((p3[0]-p1[0])**2 + (p3[1]-p1[1])**2) # side_b
        self.assertAlmostEqual(dist_p1p2, 10.0, places=7, msg="AAS Right P1P2 side_c")
        self.assertAlmostEqual(dist_p1p3, 5.0 * math.sqrt(3), places=7, msg="AAS Right P1P3 side_b")


    def test_aas_isosceles_triangle(self):
        """AAS: A=22.5, B=22.5, a=4 (P2P3=4) -> C=135, b=4"""
        angle_A = math.pi / 8.0
        angle_B = angle_A
        side_a = 4.0

        p1, p2, p3 = get_vertices(definition_mode='aas',
                                  angle1_rad=angle_A,
                                  angle2_rad=angle_B,
                                  side_opposite_angle1=side_a)
        
        expected_p1: Point = (0.0, 0.0)
        
        assertPointAlmostEqual(self, p1, expected_p1, msg="AAS Isosceles P1")
        
        dist_p1p3 = math.sqrt((p3[0]-p1[0])**2 + (p3[1]-p1[1])**2) # side_b
        self.assertAlmostEqual(dist_p1p3, side_a, places=7, msg="AAS Isosceles P1P3 (side_b) should equal side_a")
        
        expected_p3_x = 4.0 * math.cos(math.pi/8.0)
        expected_p3_y = 4.0 * math.sin(math.pi/8.0)
        assertPointAlmostEqual(self, p3, (expected_p3_x, expected_p3_y), msg="AAS Isosceles P3")


    def test_aas_invalid_side_length(self):
        with self.assertRaisesRegex(TriangleDefinitionError, "必須為正數"):
            get_vertices(definition_mode='aas', angle1_rad=math.pi/6, angle2_rad=math.pi/3, side_opposite_angle1=0)

    def test_aas_invalid_angles_range(self):
        with self.assertRaisesRegex(TriangleDefinitionError, "必須在 \(0, pi\) 弧度範圍內"):
            get_vertices(definition_mode='aas', angle1_rad=0, angle2_rad=math.pi/3, side_opposite_angle1=5)
        with self.assertRaisesRegex(TriangleDefinitionError, "必須在 \(0, pi\) 弧度範圍內"):
            get_vertices(definition_mode='aas', angle1_rad=math.pi/6, angle2_rad=math.pi, side_opposite_angle1=5)

    def test_aas_invalid_angle_sum(self):
        with self.assertRaisesRegex(TriangleDefinitionError, "兩個輸入角的和必須小於 pi 弧度"):
            get_vertices(definition_mode='aas', angle1_rad=math.pi/2, angle2_rad=math.pi/2, side_opposite_angle1=5)

    def test_aas_missing_parameters(self):
        with self.assertRaisesRegex(ValueError, "參數是必需的"):
            get_vertices(definition_mode='aas', angle1_rad=math.pi/6, angle2_rad=math.pi/3) # missing side

    def test_aas_invalid_parameter_types(self):
        with self.assertRaisesRegex(ValueError, "必須是數字"):
            get_vertices(definition_mode='aas', angle1_rad="pi/6", angle2_rad=math.pi/3, side_opposite_angle1=5)


class TestGetMidpoint(unittest.TestCase):
    """測試 get_midpoint 函數"""

    def test_midpoint_simple_integers(self):
        p1: Point = (0, 0)
        p2: Point = (2, 4)
        expected_midpoint: Point = (1.0, 2.0)
        assertPointAlmostEqual(self, get_midpoint(p1, p2), expected_midpoint, msg="Midpoint Simple Integers")

    def test_midpoint_floats(self):
        p1: Point = (1.5, 2.5)
        p2: Point = (3.5, 4.5)
        expected_midpoint: Point = (2.5, 3.5)
        assertPointAlmostEqual(self, get_midpoint(p1, p2), expected_midpoint, msg="Midpoint Floats")

    def test_midpoint_negative_coords(self):
        p1: Point = (-1.0, -2.0)
        p2: Point = (3.0, -4.0)
        expected_midpoint: Point = (1.0, -3.0)
        assertPointAlmostEqual(self, get_midpoint(p1, p2), expected_midpoint, msg="Midpoint Negative Coords")

    def test_midpoint_same_point(self):
        p1: Point = (1.0, 1.0)
        p2: Point = (1.0, 1.0)
        expected_midpoint: Point = (1.0, 1.0)
        assertPointAlmostEqual(self, get_midpoint(p1, p2), expected_midpoint, msg="Midpoint Same Point")

    def test_midpoint_invalid_input_type(self):
        with self.assertRaisesRegex(ValueError, "輸入點必須是包含兩個數字"):
            get_midpoint("not_a_tuple", (1,1)) # type: ignore
        with self.assertRaisesRegex(ValueError, "輸入點必須是包含兩個數字"):
            get_midpoint((1,1), [2,2]) # type: ignore
            
    def test_midpoint_invalid_tuple_length(self):
        with self.assertRaisesRegex(ValueError, "輸入點必須是包含兩個數字"):
            get_midpoint((1,2,3), (1,1)) # type: ignore
        with self.assertRaisesRegex(ValueError, "輸入點必須是包含兩個數字"):
            get_midpoint((1,1), (1,)) # type: ignore


class TestGetCentroid(unittest.TestCase):
    """測試 get_centroid 函數"""

    def test_centroid_simple_triangle(self):
        p1: Point = (0,0)
        p2: Point = (3,0)
        p3: Point = (0,3)
        # Centroid = ((0+3+0)/3, (0+0+3)/3) = (1,1)
        expected_centroid: Point = (1.0, 1.0)
        assertPointAlmostEqual(self, get_centroid(p1, p2, p3), expected_centroid, msg="Centroid Simple")

    def test_centroid_general_triangle(self):
        p1: Point = (1,1)
        p2: Point = (5,1)
        p3: Point = (3,4)
        # Centroid = ((1+5+3)/3, (1+1+4)/3) = (9/3, 6/3) = (3,2)
        expected_centroid: Point = (3.0, 2.0)
        assertPointAlmostEqual(self, get_centroid(p1, p2, p3), expected_centroid, msg="Centroid General")

    def test_centroid_degenerate_collinear(self):
        """測試質心對於共線點（退化三角形）"""
        p1: Point = (0,0)
        p2: Point = (2,0)
        p3: Point = (4,0)
        # Centroid = ((0+2+4)/3, (0+0+0)/3) = (2,0)
        expected_centroid: Point = (2.0, 0.0)
        assertPointAlmostEqual(self, get_centroid(p1, p2, p3), expected_centroid, msg="Centroid Collinear")

    def test_centroid_invalid_input_type(self):
        with self.assertRaisesRegex(ValueError, "輸入頂點必須是包含兩個數字"):
            get_centroid("invalid", (1,1), (2,2)) # type: ignore
        with self.assertRaisesRegex(ValueError, "輸入頂點必須是包含兩個數字"):
            get_centroid((0,0), (1,1), [2,2]) # type: ignore


class TestGetIncenter(unittest.TestCase):
    """測試 get_incenter 函數"""

    def test_incenter_equilateral_triangle(self):
        """內心：等邊三角形，內心與質心重合"""
        # P1=(0,0), P2=(6,0), P3=(3, 3*sqrt(3))
        p1: Point = (0.0, 0.0)
        p2: Point = (6.0, 0.0)
        p3_y = 3.0 * math.sqrt(3)
        p3: Point = (3.0, p3_y)
        
        # For equilateral triangle, incenter = centroid
        # Centroid = ((0+6+3)/3, (0+0+3*sqrt(3))/3) = (3, sqrt(3))
        expected_incenter: Point = (3.0, math.sqrt(3))
        actual_incenter = get_incenter(p1, p2, p3)
        assertPointAlmostEqual(self, actual_incenter, expected_incenter, msg="Incenter Equilateral")

    def test_incenter_right_triangle_3_4_5(self):
        """內心：直角三角形 (0,0)-(3,0)-(0,4)"""
        p1: Point = (0.0, 0.0) # A
        p2: Point = (3.0, 0.0) # B
        p3: Point = (0.0, 4.0) # C
        
        # side_a (BC) = 5
        # side_b (AC) = 4
        # side_c (AB) = 3
        # Perimeter = 12
        # Ix = (5*0 + 4*3 + 3*0) / 12 = 1
        # Iy = (5*0 + 4*0 + 3*4) / 12 = 1
        expected_incenter: Point = (1.0, 1.0)
        actual_incenter = get_incenter(p1, p2, p3)
        assertPointAlmostEqual(self, actual_incenter, expected_incenter, msg="Incenter 3-4-5 Right")

    def test_incenter_collinear_points(self):
        """內心：三點共線"""
        p1: Point = (0,0)
        p2: Point = (1,0)
        p3: Point = (2,0)
        with self.assertRaisesRegex(TriangleDefinitionError, "三點共線或無法構成非退化三角形"):
            get_incenter(p1, p2, p3)

        p1_v: Point = (0,0)
        p2_v: Point = (0,1)
        p3_v: Point = (0,2)
        with self.assertRaisesRegex(TriangleDefinitionError, "三點共線或無法構成非退化三角形"):
            get_incenter(p1_v, p2_v, p3_v)
            
    def test_incenter_coincident_points(self):
        """內心：至少兩點重合"""
        p1: Point = (0,0)
        p2: Point = (0,0)
        p3: Point = (1,1)
        # This will fail the strict triangle inequality a+b > c + eps etc.
        # side_a (p2p3) = sqrt(2), side_b (p1p3) = sqrt(2), side_c (p1p2) = 0
        # b+c > a => sqrt(2)+0 > sqrt(2) (False with epsilon)
        with self.assertRaisesRegex(TriangleDefinitionError, "三點共線或無法構成非退化三角形"):
            get_incenter(p1, p2, p3)

        p_all_coincident1: Point = (1,1)
        p_all_coincident2: Point = (1.0000000001, 1.0000000001) # Almost coincident
        p_all_coincident3: Point = (1.0000000002, 1.0000000002)
        # This should be caught by perimeter check if points are extremely close
        # or by triangle inequality if they form a very thin "triangle"
        with self.assertRaisesRegex(TriangleDefinitionError, "頂點幾乎重合，無法計算內心。"):
             get_incenter(p_all_coincident1, p_all_coincident2, p_all_coincident3)


    def test_incenter_invalid_input_type(self):
        with self.assertRaisesRegex(ValueError, "輸入頂點必須是包含兩個數字"):
            get_incenter("invalid", (1,1), (2,2)) # type: ignore


class TestGetCircumcenter(unittest.TestCase):
    """測試 get_circumcenter 函數"""

    def test_circumcenter_equilateral_triangle(self):
        """外心：等邊三角形，外心與質心、內心重合"""
        s = 6.0
        p1: Point = (0.0, 0.0)
        p2: Point = (s, 0.0)
        p3: Point = (s / 2.0, s * math.sqrt(3) / 2.0)
        
        # For equilateral triangle, circumcenter = centroid
        expected_circumcenter: Point = (s / 2.0, s * math.sqrt(3) / 6.0) # (3.0, sqrt(3))
        actual_circumcenter = get_circumcenter(p1, p2, p3)
        assertPointAlmostEqual(self, actual_circumcenter, expected_circumcenter, msg="Circumcenter Equilateral")

    def test_circumcenter_right_triangle_origin_axes(self):
        """外心：直角三角形 P1(0,0), P2(a,0), P3(0,b) -> 外心是斜邊中點 (a/2, b/2)"""
        a = 6.0
        b = 8.0
        p1: Point = (0.0, 0.0)
        p2: Point = (a, 0.0)
        p3: Point = (0.0, b)
        
        expected_circumcenter: Point = (a / 2.0, b / 2.0) # (3.0, 4.0)
        actual_circumcenter = get_circumcenter(p1, p2, p3)
        assertPointAlmostEqual(self, actual_circumcenter, expected_circumcenter, msg="Circumcenter Right Triangle on Axes")

    def test_circumcenter_general_triangle(self):
        """外心：一般三角形 P1(0,0), P2(5,0), P3(3,4)"""
        p1: Point = (0.0, 0.0)
        p2: Point = (5.0, 0.0)
        p3: Point = (3.0, 4.0)
        # Expected: (2.5, 1.25) based on manual calculation
        expected_circumcenter: Point = (2.5, 1.25)
        actual_circumcenter = get_circumcenter(p1, p2, p3)
        assertPointAlmostEqual(self, actual_circumcenter, expected_circumcenter, msg="Circumcenter General Triangle")
        
        # Verify distances from circumcenter to vertices are equal
        dist1 = _distance(actual_circumcenter, p1)
        dist2 = _distance(actual_circumcenter, p2)
        dist3 = _distance(actual_circumcenter, p3)
        self.assertAlmostEqual(dist1, dist2, places=7)
        self.assertAlmostEqual(dist2, dist3, places=7)


    def test_circumcenter_collinear_points(self):
        """外心：三點共線"""
        p1: Point = (0,0)
        p2: Point = (1,0)
        p3: Point = (2,0)
        with self.assertRaisesRegex(TriangleDefinitionError, "三點共線，無法計算外心。"):
            get_circumcenter(p1, p2, p3)

    def test_circumcenter_invalid_input_type(self):
        with self.assertRaisesRegex(ValueError, "輸入頂點必須是包含兩個數字"):
            get_circumcenter("invalid", (1,1), (2,2)) # type: ignore


class TestGetOrthocenter(unittest.TestCase):
    """測試 get_orthocenter 函數"""

    def test_orthocenter_equilateral_triangle(self):
        """垂心：等邊三角形，垂心與質心等重合"""
        s = 6.0
        p1: Point = (0.0, 0.0)
        p2: Point = (s, 0.0)
        p3: Point = (s / 2.0, s * math.sqrt(3) / 2.0)
        
        expected_orthocenter: Point = (s / 2.0, s * math.sqrt(3) / 6.0) # (3.0, sqrt(3))
        actual_orthocenter = get_orthocenter(p1, p2, p3)
        assertPointAlmostEqual(self, actual_orthocenter, expected_orthocenter, msg="Orthocenter Equilateral")

    def test_orthocenter_right_triangle_at_origin(self):
        """垂心：直角在原點的直角三角形，垂心是原點"""
        p1: Point = (0.0, 0.0) # Right angle vertex
        p2: Point = (5.0, 0.0)
        p3: Point = (0.0, 3.0)
        expected_orthocenter: Point = p1
        actual_orthocenter = get_orthocenter(p1, p2, p3)
        assertPointAlmostEqual(self, actual_orthocenter, expected_orthocenter, msg="Orthocenter Right Triangle at Origin")

    def test_orthocenter_right_triangle_not_at_origin(self):
        """垂心：直角不在原點的直角三角形"""
        p1: Point = (1.0, 1.0) # Right angle vertex
        p2: Point = (5.0, 1.0)
        p3: Point = (1.0, 4.0)
        expected_orthocenter: Point = p1
        actual_orthocenter = get_orthocenter(p1, p2, p3)
        assertPointAlmostEqual(self, actual_orthocenter, expected_orthocenter, msg="Orthocenter Right Triangle not at Origin")

    def test_orthocenter_general_triangle(self):
        """垂心：一般三角形 P1(0,0), P2(5,0), P3(3,4)"""
        p1: Point = (0.0, 0.0)
        p2: Point = (5.0, 0.0)
        p3: Point = (3.0, 4.0)
        # Manual calculation:
        # Slope BC = (4-0)/(3-5) = -2. Altitude from A has slope 1/2. Eq: y = 0.5x
        # Slope AC = (4-0)/(3-0) = 4/3. Altitude from B has slope -3/4. Eq: y - 0 = -3/4 (x - 5) => y = -0.75x + 3.75
        # 0.5x = -0.75x + 3.75 => 1.25x = 3.75 => x = 3. y = 0.5*3 = 1.5
        expected_orthocenter: Point = (3.0, 1.5)
        actual_orthocenter = get_orthocenter(p1, p2, p3)
        assertPointAlmostEqual(self, actual_orthocenter, expected_orthocenter, msg="Orthocenter General Triangle")

    def test_orthocenter_horizontal_side_triangle(self):
        """垂心：一邊水平的三角形 P1(0,5), P2(-2,1), P3(2,1)"""
        p1: Point = (0.0, 5.0)
        p2: Point = (-2.0, 1.0)
        p3: Point = (2.0, 1.0) # Side P2P3 is horizontal
        # Altitude from P1 is x=0.
        # Slope P1P3 = (1-5)/(2-0) = -2. Altitude from P2 has slope 1/2.
        # Eq: y - 1 = 1/2 (x - (-2)) => y = 0.5x + 1 + 1 = 0.5x + 2
        # Intersection: x=0, y=2.
        expected_orthocenter: Point = (0.0, 2.0)
        actual_orthocenter = get_orthocenter(p1, p2, p3)
        assertPointAlmostEqual(self, actual_orthocenter, expected_orthocenter, msg="Orthocenter Horizontal Side")
        
    def test_orthocenter_vertical_side_triangle(self):
        """垂心：一邊垂直的三角形 P1(1,5), P2(1,1), P3(4,3)"""
        p1: Point = (1.0, 5.0)
        p2: Point = (1.0, 1.0) # Side P1P2 is vertical
        p3: Point = (4.0, 3.0)
        # Altitude from P3 is y=3.
        # Slope P1P3 = (3-5)/(4-1) = -2/3. Altitude from P2 has slope 3/2.
        # Eq: y - 1 = 3/2 (x - 1) => y = 1.5x - 1.5 + 1 = 1.5x - 0.5
        # Intersection: y=3 => 3 = 1.5x - 0.5 => 3.5 = 1.5x => x = 3.5/1.5 = 7/3
        expected_orthocenter: Point = (7.0/3.0, 3.0)
        actual_orthocenter = get_orthocenter(p1, p2, p3)
        assertPointAlmostEqual(self, actual_orthocenter, expected_orthocenter, msg="Orthocenter Vertical Side")


    def test_orthocenter_collinear_points(self):
        """垂心：三點共線"""
        p1: Point = (0,0)
        p2: Point = (1,0)
        p3: Point = (2,0)
        with self.assertRaisesRegex(TriangleDefinitionError, "三點共線，無法計算垂心。"):
            get_orthocenter(p1, p2, p3)

    def test_orthocenter_invalid_input_type(self):
        with self.assertRaisesRegex(ValueError, "輸入頂點必須是包含兩個數字"):
            get_orthocenter("invalid", (1,1), (2,2)) # type: ignore

if __name__ == "__main__":
    unittest.main()


class TestGetArcRenderParams(unittest.TestCase):
    """測試 get_arc_render_params 函數"""

    def test_arc_fixed_radius(self):
        """普通角弧 - 固定半徑"""
        vertex: Point = (0,0)
        p_arm1: Point = (2,0) # Angle 0
        p_arm2: Point = (0,2) # Angle pi/2
        params = get_arc_render_params(vertex, p_arm1, p_arm2, radius_config=0.5)
        
        self.assertEqual(params['type'], 'arc')
        assertPointAlmostEqual(self, params['center'], vertex)
        self.assertAlmostEqual(params['radius'], 0.5)
        self.assertAlmostEqual(params['start_angle_rad'], 0)
        self.assertAlmostEqual(params['end_angle_rad'], math.pi/2)

    def test_arc_auto_radius_basic(self):
        """普通角弧 - 'auto' 半徑，基本情況"""
        vertex: Point = (0,0)
        p_arm1: Point = (2,0)
        p_arm2: Point = (0,3)
        # shorter_arm_len = 2. default_ratio = 0.15. radius = 2 * 0.15 = 0.3
        # min_auto_radius=0.1, max_auto_radius=1.0. 0.3 is within range.
        params = get_arc_render_params(vertex, p_arm1, p_arm2, radius_config="auto")
        
        self.assertEqual(params['type'], 'arc')
        assertPointAlmostEqual(self, params['center'], vertex)
        self.assertAlmostEqual(params['radius'], 0.3) # 2 * 0.15
        self.assertAlmostEqual(params['start_angle_rad'], 0)
        self.assertAlmostEqual(params['end_angle_rad'], math.pi/2)

    def test_arc_auto_radius_min_triggered(self):
        """普通角弧 - 'auto' 半徑，觸發最小半徑"""
        vertex: Point = (0,0)
        p_arm1: Point = (0.2,0)
        p_arm2: Point = (0,0.3)
        # shorter_arm_len = 0.2. default_ratio = 0.15. radius = 0.2 * 0.15 = 0.03
        # min_auto_radius=0.1. So, radius becomes 0.1.
        params = get_arc_render_params(vertex, p_arm1, p_arm2, radius_config="auto", min_auto_radius=0.1)
        self.assertAlmostEqual(params['radius'], 0.1)

    def test_arc_auto_radius_max_triggered(self):
        """普通角弧 - 'auto' 半徑，觸發最大半徑"""
        vertex: Point = (0,0)
        p_arm1: Point = (10,0)
        p_arm2: Point = (0,12)
        # shorter_arm_len = 10. default_ratio = 0.15. radius = 10 * 0.15 = 1.5
        # max_auto_radius=1.0. So, radius becomes 1.0.
        params = get_arc_render_params(vertex, p_arm1, p_arm2, radius_config="auto", max_auto_radius=1.0)
        self.assertAlmostEqual(params['radius'], 1.0)

    def test_arc_angle_wraparound(self):
        """普通角弧 - 角度環繞 (例如從 arm2 到 arm1)"""
        vertex: Point = (0,0)
        p_arm1: Point = (0,2) # Angle pi/2
        p_arm2: Point = (2,0) # Angle 0
        # start_angle = pi/2, end_angle = 0.
        # Code: if end_angle < start_angle: end_angle += 2*pi. So end_angle becomes 2*pi.
        # Current test output shows 0.0.
        # get_arc_render_params returns raw atan2 angles; p_arm2 (2,0) gives angle 0.
        params = get_arc_render_params(vertex, p_arm1, p_arm2, radius_config=0.5)
        self.assertAlmostEqual(params['start_angle_rad'], math.pi/2)
        self.assertAlmostEqual(params['end_angle_rad'], 0.0, msg="end_angle_rad for p_arm2=(2,0) should be 0.0 from atan2.")

    def test_right_angle_symbol(self):
        """直角符號參數生成"""
        vertex: Point = (1,1)
        p_arm1: Point = (4,1) # Horizontal arm (length 3)
        p_arm2: Point = (1,5) # Vertical arm (length 4)
        size = 0.5
        params = get_arc_render_params(vertex, p_arm1, p_arm2, radius_config=size, is_right_angle_symbol=True)

        self.assertEqual(params['type'], 'right_angle_symbol')
        assertPointAlmostEqual(self, params['vertex'], vertex)
        self.assertEqual(params['size'], size)
        # vec_v_arm1 = (3,0), unit = (1,0). p_sym_arm1 = (1+0.5*1, 1+0.5*0) = (1.5, 1)
        # vec_v_arm2 = (0,4), unit = (0,1). p_sym_arm2 = (1+0.5*0, 1+0.5*1) = (1, 1.5)
        assertPointAlmostEqual(self, params['p_on_arm1_for_symbol'], (1.5, 1.0))
        assertPointAlmostEqual(self, params['p_on_arm2_for_symbol'], (1.0, 1.5))

    def test_invalid_radius_config_type(self):
        with self.assertRaisesRegex(ValueError, r"不支持的 radius_config 類型: .*"): # Corrected regex
            get_arc_render_params((0,0), (1,0), (0,1), radius_config=[0.5]) # type: ignore

    def test_invalid_fixed_radius_value(self):
        with self.assertRaisesRegex(ValueError, "固定半徑必須為正數"):
            get_arc_render_params((0,0), (1,0), (0,1), radius_config=0)
        with self.assertRaisesRegex(ValueError, "固定半徑必須為正數"):
            get_arc_render_params((0,0), (1,0), (0,1), radius_config=-0.5)
            
    def test_arm_length_too_short(self):
        with self.assertRaisesRegex(ValueError, "角臂的長度過短"):
            get_arc_render_params((0,0), (0,0), (0,1))
        with self.assertRaisesRegex(ValueError, "角臂的長度過短"):
            get_arc_render_params((0,0), (1,0), (0,0))
            
    def test_invalid_point_format(self):
        with self.assertRaisesRegex(ValueError, r"輸入點 .* 必須是包含兩個數字 \(x,y\).*"): # Corrected regex
            get_arc_render_params("vertex", (1,0), (0,1)) # type: ignore


if __name__ == "__main__":
    unittest.main()


class TestGetLabelPlacementParams(unittest.TestCase):
    """測試 get_label_placement_params 函數 (初步框架)"""

    def setUp(self):
        self.p1: Point = (0.0, 0.0)
        self.p2: Point = (4.0, 0.0)
        self.p3: Point = (2.0, 3.0)
        self.all_vertices = (self.p1, self.p2, self.p3)
        self.special_points = {'incenter': (2.0, 1.0)} # Dummy value for now

    def test_placement_vertex_label_auto(self):
        """頂點標籤 - auto (測試等腰三角形頂角)"""
        # 等腰三角形 P1(2,3), P2(0,0), P3(4,0). 測試頂點 P1(2,3) 的標籤。
        # 角平分線的反方向應該是沿著 +y 方向。
        peak_vertex: Point = (2.0, 3.0)
        base_v1: Point = (0.0, 0.0)
        base_v2: Point = (4.0, 0.0)
        all_vertices_isosceles = (peak_vertex, base_v1, base_v2)
        default_offset = 0.15 # 函數中的默認值

        params = get_label_placement_params(
            element_type='vertex',
            target_elements={'vertex_coord': peak_vertex},
            all_vertices=all_vertices_isosceles,
            special_points=self.special_points, # special_points 可能影響更高級的定位
            user_preference="auto",
            default_offset=default_offset
        )
        self.assertIsNotNone(params)
        
        # 預期 reference_point 在 peak_vertex 的正上方 default_offset 距離
        expected_ref_point: Point = (peak_vertex[0], peak_vertex[1] + default_offset)
        actual_ref_point = params.get('reference_point')
        
        self.assertIsNotNone(actual_ref_point, "reference_point 不應為 None")
        if actual_ref_point: # Pylance happy
            assertPointAlmostEqual(self, actual_ref_point, expected_ref_point, msg="Vertex label reference_point")
        
        self.assertEqual(params.get('label_anchor'), "c", "Vertex label_anchor 應為 'c'")
        # tikz_options 可能為空或不包含簡單的 "above" 了，因為我們返回絕對座標
        # self.assertIsNone(params.get('tikz_options'), "tikz_options 應為 None 或空")

    def test_placement_side_label_auto(self):
        """邊標籤 - auto (測試水平邊 P1P2)"""
        # P1(0,0), P2(4,0), P3(2,3)
        # 測試邊 P1P2
        p1_test: Point = (0.0, 0.0)
        p2_test: Point = (4.0, 0.0)
        p3_test: Point = (2.0, 3.0)
        all_vertices_test = (p1_test, p2_test, p3_test)
        default_offset = 0.15 # 函數中的默認值

        params = get_label_placement_params(
            element_type='side',
            target_elements={'p_start': p1_test, 'p_end': p2_test},
            all_vertices=all_vertices_test,
            special_points=self.special_points,
            user_preference="auto",
            default_offset=default_offset
        )
        self.assertIsNotNone(params)
        
        # mid_point = (2,0)
        # side_dy=0, side_dx=4. initial_normal=(0,4). unit_normal=(0,1)
        # p_other=(2,3). vec_mid_to_other=(0,3).
        # dot_product = 0*0 + 1*3 = 3 > 0. So, unit_normal becomes (0,-1).
        # label_pos = (2, 0 - 0.15) = (2, -0.15)
        expected_ref_point: Point = (2.0, -default_offset)
        actual_ref_point = params.get('reference_point')

        self.assertIsNotNone(actual_ref_point, "reference_point 不應為 None")
        if actual_ref_point:
            assertPointAlmostEqual(self, actual_ref_point, expected_ref_point, msg="Side label reference_point for P1P2")
        
        self.assertEqual(params.get('label_anchor'), "c", "Side label_anchor 應為 'c'")
        self.assertAlmostEqual(params.get('rotation', None), 0.0, msg="Side label rotation for P1P2")

    def test_placement_side_label_auto_slanted_side(self):
        """邊標籤 - auto (測試斜邊 P1P3)"""
        # P1(0,0), P2(4,0), P3(2,3)
        # 測試邊 P1P3
        p1_test: Point = (0.0, 0.0)
        # p2_test: Point = (4.0, 0.0) # This is p_other
        p3_test: Point = (2.0, 3.0)
        all_vertices_test = (p1_test, (4.0,0.0), p3_test) # Ensure p2_test is p_other
        default_offset = 0.15

        params = get_label_placement_params(
            element_type='side',
            target_elements={'p_start': p1_test, 'p_end': p3_test},
            all_vertices=all_vertices_test,
            special_points=self.special_points,
            user_preference="auto",
            default_offset=default_offset
        )
        self.assertIsNotNone(params)

        mid_point = get_midpoint(p1_test, p3_test) # (1.0, 1.5)
        side_dx = p3_test[0] - p1_test[0] # 2.0
        side_dy = p3_test[1] - p1_test[1] # 3.0
        len_side = math.sqrt(side_dx**2 + side_dy**2) # sqrt(4+9) = sqrt(13)

        # initial_normal=(-3, 2). unit_normal=(-3/sqrt(13), 2/sqrt(13))
        unit_normal_dx_initial = -side_dy / len_side
        unit_normal_dy_initial = side_dx / len_side
        
        p_other = (4.0,0.0)
        vec_mid_to_other_dx = p_other[0] - mid_point[0] # 4 - 1 = 3
        vec_mid_to_other_dy = p_other[1] - mid_point[1] # 0 - 1.5 = -1.5
        
        # dot_product = (-3/sqrt(13))*3 + (2/sqrt(13))*(-1.5) = (-9 - 3)/sqrt(13) = -12/sqrt(13) < 0
        # So, initial unit_normal is already pointing "outwards" relative to p_other.
        final_unit_normal_dx = unit_normal_dx_initial
        final_unit_normal_dy = unit_normal_dy_initial
        
        expected_label_pos_x = mid_point[0] + final_unit_normal_dx * default_offset
        expected_label_pos_y = mid_point[1] + final_unit_normal_dy * default_offset
        expected_ref_point: Point = (expected_label_pos_x, expected_label_pos_y)
        
        actual_ref_point = params.get('reference_point')
        self.assertIsNotNone(actual_ref_point, "reference_point 不應為 None")
        if actual_ref_point:
            assertPointAlmostEqual(self, actual_ref_point, expected_ref_point, msg="Side label reference_point for P1P3")

        self.assertEqual(params.get('label_anchor'), "c")
        expected_rotation = math.degrees(math.atan2(side_dy, side_dx))
        self.assertAlmostEqual(params.get('rotation', None), expected_rotation, msg="Side label rotation for P1P3")

    def test_placement_angle_value_label_auto(self):
        """角標籤 - auto (測試90度角)"""
        vertex_test: Point = (0.0, 0.0)
        p_arm1_test: Point = (1.0, 0.0) # Along X-axis
        p_arm2_test: Point = (0.0, 1.0) # Along Y-axis
        # all_vertices is not directly used by this specific logic path but required by func signature
        all_vertices_test = (vertex_test, p_arm1_test, p_arm2_test)
        default_offset = 0.15 # Default in get_label_placement_params

        params = get_label_placement_params(
            element_type='angle_value',
            target_elements={'vertex': vertex_test, 'p_on_arm1': p_arm1_test, 'p_on_arm2': p_arm2_test},
            all_vertices=all_vertices_test, # Dummy for this test path
            special_points=self.special_points, # Dummy for this test path
            user_preference="auto",
            default_offset=default_offset
        )
        self.assertIsNotNone(params)

        # Expected logic:
        # unit_vec1 = (1,0), unit_vec2 = (0,1)
        # bisector_vec = (1,1). unit_bisector_vec = (1/sqrt(2), 1/sqrt(2))
        # arc_params uses default_ratio=0.1 for angle_value label placement.
        # len_arm1=1, len_arm2=1. shorter_arm=1. arc_radius = 1 * 0.1 = 0.1.
        # label_distance = arc_radius (0.1) + default_offset (0.15) = 0.25
        # label_pos_x = 0 + (1/sqrt(2)) * 0.25
        # label_pos_y = 0 + (1/sqrt(2)) * 0.25
        
        expected_val = (1.0 / math.sqrt(2)) * 0.25
        expected_ref_point: Point = (expected_val, expected_val)
        actual_ref_point = params.get('reference_point')

        self.assertIsNotNone(actual_ref_point, "reference_point 不應為 None")
        if actual_ref_point:
            assertPointAlmostEqual(self, actual_ref_point, expected_ref_point, msg="Angle value label reference_point")
        
        self.assertEqual(params.get('label_anchor'), "c", "Angle value label_anchor 應為 'c'")
        self.assertAlmostEqual(params.get('rotation', None), 0.0, msg="Angle value label rotation")

    def test_invalid_element_type(self):
        with self.assertRaisesRegex(ValueError, "不支持的 element_type"):
            get_label_placement_params(
                element_type='invalid_type', # type: ignore
                target_elements={},
                all_vertices=self.all_vertices,
                special_points=self.special_points
            )

    def test_missing_target_elements_vertex(self):
        with self.assertRaisesRegex(ValueError, r"對於 'vertex' 類型，target_elements\['vertex_coord'\] 必須是一個有效的 Point。"):
            get_label_placement_params(
                element_type='vertex',
                target_elements={}, # Missing vertex_coord
                all_vertices=self.all_vertices,
                special_points=self.special_points
            )

    def test_missing_target_elements_side(self):
        with self.assertRaisesRegex(ValueError, r"對於 'side' 類型，target_elements 必須包含有效的 'p_start' 和 'p_end' Point 對象。"):
            get_label_placement_params(
                element_type='side',
                target_elements={'p_start': self.p1}, # Missing p_end
                all_vertices=self.all_vertices,
                special_points=self.special_points
            )

    def test_missing_target_elements_angle(self):
        with self.assertRaisesRegex(ValueError, r"對於 'angle_value' 類型，target_elements 必須包含有效的 'vertex', 'p_on_arm1', 'p_on_arm2' Point 對象。"):
            get_label_placement_params(
                element_type='angle_value',
                target_elements={'vertex': self.p1}, # Missing arms
                all_vertices=self.all_vertices,
                special_points=self.special_points
            )