#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 幾何計算工具集
"""

import math
from typing import Tuple, Dict, Any, Literal

# 類型別名
Point = Tuple[float, float]

class TriangleDefinitionError(ValueError):
    """自定義異常，用於表示三角形定義無效"""
    pass

def get_vertices(definition_mode: Literal['sss', 'sas', 'asa', 'aas', 'coordinates'], **kwargs) -> Tuple[Point, Point, Point]:
    """
    根據不同的定義方式計算並返回三角形的三個頂點座標。
    約定：
    - P1 (第一個頂點) 始終在原點 (0,0)。
    - P2 (第二個頂點) 始終在 x 軸正半軸上（或原點，如果邊長為0）。
    - P3 (第三個頂點) 的 y 座標通常取正值（使三角形在x軸上方），除非特定情況。

    Args:
        definition_mode: 三角形的定義方式。支持 'sss', 'sas', 'asa', 'aas', 'coordinates'。
        **kwargs: 對應定義方式所需的參數。
            - 'sss': side_a, side_b, side_c (a,b,c 分別是 P2P3, P1P3, P1P2 的長度)
            - 'coordinates': p1, p2, p3 (直接提供三個點的座標)
            - 其他模式待實現...

    Returns:
        一個包含三個頂點座標 (P1, P2, P3) 的元組。

    Raises:
        TriangleDefinitionError: 如果輸入的參數無法構成有效三角形。
        NotImplementedError: 如果請求的 definition_mode 尚未實現。
        ValueError: 如果缺少必要的參數。
    """
    if definition_mode == 'sss':
        side_a = kwargs.get('side_a')
        side_b = kwargs.get('side_b')
        side_c = kwargs.get('side_c')

        if side_a is None or side_b is None or side_c is None:
            raise ValueError("對於 'sss' 模式, 'side_a', 'side_b', 'side_c' 參數是必需的。")
        
        # 傳統上 a, b, c 分別是 P1 對邊, P2 對邊, P3 對邊
        # 但這裡為了方便計算 P1=(0,0), P2=(side_c, 0)
        # 所以參數 side_a 是 P2P3 的長度, side_b 是 P1P3 的長度, side_c 是 P1P2 的長度

        # 驗證三角形不等式
        if not (side_a + side_b > side_c and \
                side_a + side_c > side_b and \
                side_b + side_c > side_a):
            raise TriangleDefinitionError("三邊長無法構成三角形 (不滿足三角形不等式)。")
        
        if side_a <= 0 or side_b <= 0 or side_c <= 0:
            raise TriangleDefinitionError("三邊長必須為正數。")

        p1: Point = (0.0, 0.0)
        p2: Point = (side_c, 0.0)

        # 計算 P3 的 x 座標
        # 根據餘弦定理推導: (side_b^2 + side_c^2 - side_a^2) / (2 * side_c)
        # side_b 是 P1P3, side_c 是 P1P2, side_a 是 P2P3
        if side_c == 0: # 理論上已被 side_c <= 0 捕獲
             # 這個分支在當前邏輯下（邊長必須為正）實際不會被執行
             # 但保留以防未來邏輯變更允許 side_c 為0的特殊情況
             if side_a == side_b: 
                 p3_x = 0.0
             else: 
                 raise TriangleDefinitionError("side_c 為 0 時，side_a 必須等於 side_b 才能定義 P3.x。")
        else:
            p3_x = (side_b**2 + side_c**2 - side_a**2) / (2 * side_c)

        # 計算 P3 的 y 座標
        # y^2 = side_b^2 - x^2
        # 確保根號內的值非負 (理論上三角形不等式已保證，但浮點誤差可能導致問題)
        discriminant = side_b**2 - p3_x**2
        if discriminant < -1e-9: # 允許非常小的負數作為浮點誤差容忍
            raise TriangleDefinitionError(f"無法計算 P3.y (根號內為負: {discriminant})。檢查邊長是否合理或存在嚴重浮點誤差。")
        if discriminant < 0: # 強制為0避免 math.sqrt 報錯
            discriminant = 0.0
            
        p3_y = math.sqrt(discriminant)
        
        p3: Point = (p3_x, p3_y)

        return p1, p2, p3

    elif definition_mode == 'coordinates':
        p1 = kwargs.get('p1')
        p2 = kwargs.get('p2')
        p3 = kwargs.get('p3')
        if p1 is None or p2 is None or p3 is None:
            raise ValueError("對於 'coordinates' 模式, 'p1', 'p2', 'p3' 參數是必需的。")
        if not (isinstance(p1, tuple) and len(p1) == 2 and isinstance(p1[0], (int, float)) and isinstance(p1[1], (int, float)) and
                isinstance(p2, tuple) and len(p2) == 2 and isinstance(p2[0], (int, float)) and isinstance(p2[1], (int, float)) and
                isinstance(p3, tuple) and len(p3) == 2 and isinstance(p3[0], (int, float)) and isinstance(p3[1], (int, float))):
            raise ValueError("座標點必須是包含兩個數字 (x,y) 的元組。")
        return p1, p2, p3

    elif definition_mode == 'sas':
        side1 = kwargs.get('side1') # P1P2
        angle_rad = kwargs.get('angle_rad') # Angle at P1, in radians
        side2 = kwargs.get('side2') # P1P3

        if side1 is None or angle_rad is None or side2 is None:
            raise ValueError("對於 'sas' 模式, 'side1', 'angle_rad', 'side2' 參數是必需的。")

        if not (isinstance(side1, (int, float)) and isinstance(angle_rad, (int, float)) and isinstance(side2, (int, float))):
            raise ValueError("'side1', 'angle_rad', 'side2' 必須是數字。")

        if side1 <= 0 or side2 <= 0:
            raise TriangleDefinitionError("邊長 ('side1', 'side2') 必須為正數。")
        
        if not (0 < angle_rad < math.pi):
            # angle_rad == 0 or angle_rad == math.pi would lead to a degenerate triangle (collinear points)
            raise TriangleDefinitionError("角度 ('angle_rad') 必須在 (0, pi) 弧度範圍內。")

        p1: Point = (0.0, 0.0)
        p2: Point = (side1, 0.0)
        
        p3_x = side2 * math.cos(angle_rad)
        p3_y = side2 * math.sin(angle_rad)
        p3: Point = (p3_x, p3_y)
        
        return p1, p2, p3

    elif definition_mode == 'asa':
        angle1_rad = kwargs.get('angle1_rad') # Angle at P1
        side_length = kwargs.get('side_length') # Length of P1P2
        angle2_rad = kwargs.get('angle2_rad') # Angle at P2

        if angle1_rad is None or side_length is None or angle2_rad is None:
            raise ValueError("對於 'asa' 模式, 'angle1_rad', 'side_length', 'angle2_rad' 參數是必需的。")

        if not (isinstance(angle1_rad, (int, float)) and
                isinstance(side_length, (int, float)) and
                isinstance(angle2_rad, (int, float))):
            raise ValueError("'angle1_rad', 'side_length', 'angle2_rad' 必須是數字。")

        if side_length <= 0:
            raise TriangleDefinitionError("邊長 ('side_length') 必須為正數。")
        
        if not (0 < angle1_rad < math.pi and 0 < angle2_rad < math.pi):
            raise TriangleDefinitionError("角度 ('angle1_rad', 'angle2_rad') 必須在 (0, pi) 弧度範圍內。")
        
        if angle1_rad + angle2_rad >= math.pi:
            # This also implies angle3_rad <= 0, making sin(angle3_rad) zero or negative (problematic for sine rule)
            raise TriangleDefinitionError("兩個輸入角的和必須小於 pi 弧度。")

        p1: Point = (0.0, 0.0)
        p2: Point = (side_length, 0.0)

        angle3_rad = math.pi - angle1_rad - angle2_rad
        
        # Using Sine Rule to find side_b (length of P1P3)
        # side_b / sin(angle2_rad) = side_length / sin(angle3_rad)
        # sin_angle3 = math.sin(angle3_rad)
        # if abs(sin_angle3) < 1e-9: # angle3 is close to 0 or pi (already checked by angle1+angle2 >= pi)
        #     raise TriangleDefinitionError("計算得到的第三個角接近0或pi，無法形成有效三角形。")
        
        side_b_equiv = side_length * math.sin(angle2_rad) / math.sin(angle3_rad)
        
        p3_x = side_b_equiv * math.cos(angle1_rad)
        p3_y = side_b_equiv * math.sin(angle1_rad)
        p3: Point = (p3_x, p3_y)
        
        return p1, p2, p3

    elif definition_mode == 'aas':
        angle1_rad = kwargs.get('angle1_rad') # Angle at P1 (A)
        angle2_rad = kwargs.get('angle2_rad') # Angle at P2 (B)
        side_opposite_angle1 = kwargs.get('side_opposite_angle1') # Length of side P2P3 (side a)

        if angle1_rad is None or angle2_rad is None or side_opposite_angle1 is None:
            raise ValueError("對於 'aas' 模式, 'angle1_rad', 'angle2_rad', 'side_opposite_angle1' 參數是必需的。")

        if not (isinstance(angle1_rad, (int, float)) and
                isinstance(angle2_rad, (int, float)) and
                isinstance(side_opposite_angle1, (int, float))):
            raise ValueError("'angle1_rad', 'angle2_rad', 'side_opposite_angle1' 必須是數字。")

        if side_opposite_angle1 <= 0:
            raise TriangleDefinitionError("邊長 ('side_opposite_angle1') 必須為正數。")

        if not (0 < angle1_rad < math.pi and 0 < angle2_rad < math.pi):
            raise TriangleDefinitionError("角度 ('angle1_rad', 'angle2_rad') 必須在 (0, pi) 弧度範圍內。")
        
        if angle1_rad + angle2_rad >= math.pi:
            raise TriangleDefinitionError("兩個輸入角的和必須小於 pi 弧度。")

        p1: Point = (0.0, 0.0)
        
        angle3_rad = math.pi - angle1_rad - angle2_rad # Angle at P3 (C)

        # sin_angle1 = math.sin(angle1_rad)
        # if abs(sin_angle1) < 1e-9: # angle1 is close to 0 or pi (already checked by 0 < angle1 < pi)
        #     raise TriangleDefinitionError("angle1_rad 接近0或pi，無法使用正弦定理。")

        # Find side_c (length of P1P2) using Sine Rule: side_c / sin(C) = side_a / sin(A)
        side_c_equiv = side_opposite_angle1 * math.sin(angle3_rad) / math.sin(angle1_rad)
        
        p2: Point = (side_c_equiv, 0.0)

        # Now, find side_b (length of P1P3) using Sine Rule: side_b / sin(B) = side_c / sin(C)
        # (or use the fact that we have P1, P2 and angle at P1 to find P3, similar to SAS/ASA logic)
        # side_b_equiv / sin(angle2_rad) = side_c_equiv / sin(angle3_rad)
        side_b_equiv = side_c_equiv * math.sin(angle2_rad) / math.sin(angle3_rad)
        # An alternative for side_b_equiv: side_b / sin(B) = side_a / sin(A) => side_b = side_a * sin(B) / sin(A)
        # side_b_equiv_alt = side_opposite_angle1 * math.sin(angle2_rad) / math.sin(angle1_rad)
        # assert abs(side_b_equiv - side_b_equiv_alt) < 1e-9 # Should be equal

        p3_x = side_b_equiv * math.cos(angle1_rad)
        p3_y = side_b_equiv * math.sin(angle1_rad)
        p3: Point = (p3_x, p3_y)
        
        return p1, p2, p3
        
    else:
        raise NotImplementedError(f"定義模式 '{definition_mode}' 尚未實現。")


def get_midpoint(p1: Point, p2: Point) -> Point:
    """計算兩點連線的中點。

    Args:
        p1: 第一個點 (x1, y1)。
        p2: 第二個點 (x2, y2)。

    Returns:
        中點座標 (xm, ym)。
    
    Raises:
        ValueError: 如果輸入點的格式不正確。
    """
    if not (isinstance(p1, tuple) and len(p1) == 2 and isinstance(p1[0], (int, float)) and isinstance(p1[1], (int, float)) and
            isinstance(p2, tuple) and len(p2) == 2 and isinstance(p2[0], (int, float)) and isinstance(p2[1], (int, float))):
        raise ValueError("輸入點必須是包含兩個數字 (x,y) 的元組。")
    
    mid_x = (p1[0] + p2[0]) / 2.0
    mid_y = (p1[1] + p2[1]) / 2.0
    return (mid_x, mid_y)

def get_centroid(p1: Point, p2: Point, p3: Point) -> Point:
    """計算三角形的質心 (重心)。

    Args:
        p1: 三角形的第一個頂點 (x1, y1)。
        p2: 三角形的第二個頂點 (x2, y2)。
        p3: 三角形的第三個頂點 (x3, y3)。

    Returns:
        質心座標 (xc, yc)。

    Raises:
        ValueError: 如果輸入頂點的格式不正確。
    """
    if not (isinstance(p1, tuple) and len(p1) == 2 and isinstance(p1[0], (int, float)) and isinstance(p1[1], (int, float)) and
            isinstance(p2, tuple) and len(p2) == 2 and isinstance(p2[0], (int, float)) and isinstance(p2[1], (int, float)) and
            isinstance(p3, tuple) and len(p3) == 2 and isinstance(p3[0], (int, float)) and isinstance(p3[1], (int, float))):
        raise ValueError("輸入頂點必須是包含兩個數字 (x,y) 的元組。")

    centroid_x = (p1[0] + p2[0] + p3[0]) / 3.0
    centroid_y = (p1[1] + p2[1] + p3[1]) / 3.0
    return (centroid_x, centroid_y)


def _distance(p1: Point, p2: Point) -> float:
    """計算兩點之間的距離"""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def get_incenter(p1: Point, p2: Point, p3: Point) -> Point:
    """
    計算三角形的內心 (三個內角平分線的交點)。

    Args:
        p1: 三角形的第一個頂點 (x1, y1)。
        p2: 三角形的第二個頂點 (x2, y2)。
        p3: 三角形的第三個頂點 (x3, y3)。

    Returns:
        內心座標 (ix, iy)。

    Raises:
        ValueError: 如果輸入頂點的格式不正確。
        TriangleDefinitionError: 如果三點共線或無法構成有效三角形。
    """
    if not (isinstance(p1, tuple) and len(p1) == 2 and isinstance(p1[0], (int, float)) and isinstance(p1[1], (int, float)) and
            isinstance(p2, tuple) and len(p2) == 2 and isinstance(p2[0], (int, float)) and isinstance(p2[1], (int, float)) and
            isinstance(p3, tuple) and len(p3) == 2 and isinstance(p3[0], (int, float)) and isinstance(p3[1], (int, float))):
        raise ValueError("輸入頂點必須是包含兩個數字 (x,y) 的元組。")

    # p1, p2, p3 分別是 A, B, C 點
    # side_a 是 BC 的長度 (p1 的對邊)
    # side_b 是 AC 的長度 (p2 的對邊)
    # side_c 是 AB 的長度 (p3 的對邊)
    # 為了與內心公式 (a*xA + b*xB + c*xC)/(a+b+c) 的傳統表示一致，這裡的命名調整一下：
    # a_len (BC), b_len (AC), c_len (AB)
    
    a_len = _distance(p2, p3) # Length of side opposite to p1 (BC)
    b_len = _distance(p1, p3) # Length of side opposite to p2 (AC)
    c_len = _distance(p1, p2) # Length of side opposite to p3 (AB)

    perimeter = a_len + b_len + c_len
    if perimeter < 1e-9: # 頂點幾乎重合
        raise TriangleDefinitionError("頂點幾乎重合，無法計算內心。")

    # 檢查三點是否共線或無法構成非退化三角形
    # 使用嚴格的三角形不等式，並允許微小的浮點誤差
    epsilon = 1e-9
    if not (a_len + b_len > c_len + epsilon and \
            a_len + c_len > b_len + epsilon and \
            b_len + c_len > a_len + epsilon):
        raise TriangleDefinitionError("三點共線或無法構成非退化三角形，無法計算內心。")

    # 內心公式: I = (a*A + b*B + c*C) / (a+b+c)
    # 其中 a,b,c 是對應頂點 A,B,C 的對邊長度。
    # p1=A, p2=B, p3=C
    # a_len is opposite A (p1), b_len is opposite B (p2), c_len is opposite C (p3)
    incenter_x = (a_len * p1[0] + b_len * p2[0] + c_len * p3[0]) / perimeter
    incenter_y = (a_len * p1[1] + b_len * p2[1] + c_len * p3[1]) / perimeter
    
    return (incenter_x, incenter_y)


def get_circumcenter(p1: Point, p2: Point, p3: Point) -> Point:
    """
    計算三角形的外心 (三邊垂直平分線的交點)。

    Args:
        p1: 三角形的第一個頂點 (x1, y1)。
        p2: 三角形的第二個頂點 (x2, y2)。
        p3: 三角形的第三個頂點 (x3, y3)。

    Returns:
        外心座標 (cx, cy)。

    Raises:
        ValueError: 如果輸入頂點的格式不正確。
        TriangleDefinitionError: 如果三點共線，外心無定義。
    """
    if not (isinstance(p1, tuple) and len(p1) == 2 and isinstance(p1[0], (int, float)) and isinstance(p1[1], (int, float)) and
            isinstance(p2, tuple) and len(p2) == 2 and isinstance(p2[0], (int, float)) and isinstance(p2[1], (int, float)) and
            isinstance(p3, tuple) and len(p3) == 2 and isinstance(p3[0], (int, float)) and isinstance(p3[1], (int, float))):
        raise ValueError("輸入頂點必須是包含兩個數字 (x,y) 的元組。")

    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3

    # D = 2 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
    # 如果 D == 0, 三點共線
    D_val = 2 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))

    if abs(D_val) < 1e-9: # 檢查是否共線 (D_val 是面積的兩倍乘以 +/-1)
        raise TriangleDefinitionError("三點共線，無法計算外心。")

    p1_sq = x1**2 + y1**2
    p2_sq = x2**2 + y2**2
    p3_sq = x3**2 + y3**2
    
    circumcenter_x = (p1_sq * (y2 - y3) + p2_sq * (y3 - y1) + p3_sq * (y1 - y2)) / D_val
    circumcenter_y = (p1_sq * (x3 - x2) + p2_sq * (x1 - x3) + p3_sq * (x2 - x1)) / D_val

    return (circumcenter_x, circumcenter_y)


def get_orthocenter(p1: Point, p2: Point, p3: Point) -> Point:
    """
    計算三角形的垂心 (三條高的交點)。

    Args:
        p1: 三角形的第一個頂點 (x1, y1)。
        p2: 三角形的第二個頂點 (x2, y2)。
        p3: 三角形的第三個頂點 (x3, y3)。

    Returns:
        垂心座標 (ox, oy)。

    Raises:
        ValueError: 如果輸入頂點的格式不正確。
        TriangleDefinitionError: 如果三點共線，垂心無定義或不唯一。
                                 對於直角三角形，垂心是直角頂點。
    """
    if not (isinstance(p1, tuple) and len(p1) == 2 and isinstance(p1[0], (int, float)) and isinstance(p1[1], (int, float)) and
            isinstance(p2, tuple) and len(p2) == 2 and isinstance(p2[0], (int, float)) and isinstance(p2[1], (int, float)) and
            isinstance(p3, tuple) and len(p3) == 2 and isinstance(p3[0], (int, float)) and isinstance(p3[1], (int, float))):
        raise ValueError("輸入頂點必須是包含兩個數字 (x,y) 的元組。")

    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3

    # 檢查共線性 (使用與外心計算中相同的 D_val)
    D_val = 2 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
    if abs(D_val) < 1e-9:
        raise TriangleDefinitionError("三點共線，無法計算垂心。")

    # 特殊情況：直角三角形，垂心是直角頂點
    # 檢查 P1 是否為直角頂點: (P2-P1) . (P3-P1) = 0
    dot_p1 = (x2 - x1) * (x3 - x1) + (y2 - y1) * (y3 - y1)
    if abs(dot_p1) < 1e-9:
        return p1
    # 檢查 P2 是否為直角頂點: (P1-P2) . (P3-P2) = 0
    dot_p2 = (x1 - x2) * (x3 - x2) + (y1 - y2) * (y3 - y2)
    if abs(dot_p2) < 1e-9:
        return p2
    # 檢查 P3 是否為直角頂點: (P1-P3) . (P2-P3) = 0
    dot_p3 = (x1 - x3) * (x2 - x3) + (y1 - y3) * (y2 - y3)
    if abs(dot_p3) < 1e-9:
        return p3
        
    # 通用情況：解兩條高線的方程
    # 高線 h1: 從 p1 到邊 p2p3
    # 高線 h2: 從 p2 到邊 p1p3

    ortho_x: float
    ortho_y: float

    # 處理邊 p2p3 平行於 x 軸 (y2 == y3)
    if abs(y2 - y3) < 1e-9: # 邊 p2p3 水平，高線 h1 垂直 x = x1
        m_p1p3 = (y1 - y3) / (x1 - x3) if abs(x1 - x3) > 1e-9 else float('inf')
        if abs(m_p1p3) < 1e-9: # 邊 p1p3 水平, 高線 h2 垂直 x = x2 (不可能，除非共線)
             raise TriangleDefinitionError("計算垂心時出現異常情況 (兩邊水平)。") # 理論上已被共線性檢查排除
        
        ortho_x = x1
        if abs(x1 - x3) < 1e-9: # 邊 p1p3 垂直，高線 h2 水平 y = y2
            ortho_y = y2
        else: # 邊 p1p3 是斜線
            m_h2 = -(x1 - x3) / (y1 - y3) # 斜率
            # y - y2 = m_h2 * (x - x2)
            ortho_y = m_h2 * (ortho_x - x2) + y2
        return (ortho_x, ortho_y)

    # 處理邊 p1p3 平行於 x 軸 (y1 == y3)
    if abs(y1 - y3) < 1e-9: # 邊 p1p3 水平，高線 h2 垂直 x = x2
        m_p2p3 = (y2 - y3) / (x2 - x3) if abs(x2 - x3) > 1e-9 else float('inf')
        if abs(m_p2p3) < 1e-9: # 邊 p2p3 水平, 高線 h1 垂直 x = x1 (不可能，除非共線)
            raise TriangleDefinitionError("計算垂心時出現異常情況 (兩邊水平)。") # 理論上已被共線性檢查排除

        ortho_x = x2
        if abs(x2 - x3) < 1e-9: # 邊 p2p3 垂直，高線 h1 水平 y = y1
            ortho_y = y1
        else: # 邊 p2p3 是斜線
            m_h1 = -(x2 - x3) / (y2 - y3) # 斜率
            # y - y1 = m_h1 * (x - x1)
            ortho_y = m_h1 * (ortho_x - x1) + y1
        return (ortho_x, ortho_y)

    # 一般情況，兩條邊都不是水平的
    m_p2p3 = (y2 - y3) / (x2 - x3) # 可能為0 (垂直邊) 或 inf (水平邊已處理)
    m_p1p3 = (y1 - y3) / (x1 - x3) # 可能為0 (垂直邊) 或 inf (水平邊已處理)

    # 斜率 of 高線 h1 (perpendicular to p2p3)
    # 如果 p2p3 垂直 (x2==x3), m_p2p3 is inf, m_h1 = 0. 高線: y = y1
    if abs(x2 - x3) < 1e-9: # 邊 p2p3 垂直
        m_h1 = 0.0
        c_h1 = y1 # y = y1
        # 斜率 of 高線 h2 (perpendicular to p1p3)
        # 如果 p1p3 垂直 (x1==x3), m_p1p3 is inf, m_h2 = 0. 高線: y = y2 (不可能，除非共線)
        if abs(x1 - x3) < 1e-9:
             raise TriangleDefinitionError("計算垂心時出現異常情況 (兩邊垂直)。") # 理論上已被共線性檢查排除
        m_h2 = -(x1 - x3) / (y1 - y3)
        c_h2 = y2 - m_h2 * x2 # y = m_h2*x + c_h2
        
        ortho_y = y1
        # y1 = m_h2*x + c_h2 => x = (y1 - c_h2) / m_h2
        if abs(m_h2) < 1e-9: # p1p3 水平, h2 垂直 x = x2
            ortho_x = x2
        else:
            ortho_x = (ortho_y - c_h2) / m_h2
        return (ortho_x, ortho_y)

    # 如果 p1p3 垂直 (x1==x3), m_p1p3 is inf, m_h2 = 0. 高線: y = y2
    if abs(x1 - x3) < 1e-9: # 邊 p1p3 垂直
        m_h2 = 0.0
        c_h2 = y2 # y = y2
        # (邊 p2p3 不會垂直，因為上面已處理過兩邊垂直的情況)
        m_h1 = -(x2 - x3) / (y2 - y3)
        c_h1 = y1 - m_h1 * x1 # y = m_h1*x + c_h1

        ortho_y = y2
        # y2 = m_h1*x + c_h1 => x = (y2 - c_h1) / m_h1
        if abs(m_h1) < 1e-9: # p2p3 水平, h1 垂直 x = x1
            ortho_x = x1
        else:
            ortho_x = (ortho_y - c_h1) / m_h1
        return (ortho_x, ortho_y)

    # 兩條高線都是斜線
    m_h1 = -(x2 - x3) / (y2 - y3)
    m_h2 = -(x1 - x3) / (y1 - y3)

    # y = m_h1 * (x - x1) + y1  => y = m_h1*x - m_h1*x1 + y1
    # y = m_h2 * (x - x2) + y2  => y = m_h2*x - m_h2*x2 + y2
    # m_h1*x - m_h1*x1 + y1 = m_h2*x - m_h2*x2 + y2
    # (m_h1 - m_h2)*x = m_h1*x1 - y1 - m_h2*x2 + y2
    # (m_h1 - m_h2)*x = m_h1*x1 - m_h2*x2 + y2 - y1
    
    # 如果 m_h1 == m_h2, 則兩條高線平行。
    # 這意味著原始邊 p2p3 和 p1p3 平行，這只在 p1,p2,p3 共線時發生，但已被排除。
    if abs(m_h1 - m_h2) < 1e-9:
        # This case should ideally not be reached if collinearity is properly checked.
        # It implies altitudes are parallel, meaning original sides were parallel.
        raise TriangleDefinitionError("計算垂心時高線平行，可能三點共線或接近共線。")

    ortho_x = (m_h1 * x1 - m_h2 * x2 + y2 - y1) / (m_h1 - m_h2)
    ortho_y = m_h1 * (ortho_x - x1) + y1
    
    return (ortho_x, ortho_y)


def get_arc_render_params(
    vertex: Point,
    p_on_arm1: Point,
    p_on_arm2: Point,
    radius_config: Any = "auto", # float, "auto", or dict
    is_right_angle_symbol: bool = False,
    default_ratio: float = 0.15, # For "auto" radius
    min_auto_radius: float = 0.1, # Min radius for "auto"
    max_auto_radius: float = 1.0   # Max radius for "auto"
) -> Dict[str, Any]:
    """
    計算繪製角弧或直角符號所需的參數。

    Args:
        vertex: 角的頂點。
        p_on_arm1: 角的第一條臂上的點。
        p_on_arm2: 角的第二條臂上的點。
        radius_config: 角弧半徑配置。
            - float: 固定半徑。
            - "auto": 自動計算半徑 (基於臂長和 default_ratio, min/max_auto_radius)。
            - dict: 更詳細的配置 (待實現)。
        is_right_angle_symbol: 是否為直角符號生成參數。
        default_ratio: "auto"模式下，半徑為較短臂長的比例。
        min_auto_radius: "auto"模式下的最小半徑。
        max_auto_radius: "auto"模式下的最大半徑。

    Returns:
        一個字典，包含傳遞給 ArcGenerator 的參數。
        例如:
        - For arc: {'type': 'arc', 'center': Point, 'radius': float,
                    'start_angle_rad': float, 'end_angle_rad': float}
                   (角度為弧度制, 是 math.atan2 的直接結果, 未經標準化以確保特定掃描方向或範圍,
                    例如 end_angle > start_angle。角度的解釋和轉換 (如轉為度數) 由調用者負責。)
        - For right_angle: {'type': 'right_angle_symbol', 'vertex': Point,
                            'p_on_arm1_for_symbol': Point,
                            'p_on_arm2_for_symbol': Point, 'size': float}
    Raises:
        ValueError: 如果輸入點或配置無效。
    """
    if not (isinstance(vertex, tuple) and len(vertex) == 2 and isinstance(vertex[0], (int, float)) and isinstance(vertex[1], (int, float)) and
            isinstance(p_on_arm1, tuple) and len(p_on_arm1) == 2 and isinstance(p_on_arm1[0], (int, float)) and isinstance(p_on_arm1[1], (int, float)) and
            isinstance(p_on_arm2, tuple) and len(p_on_arm2) == 2 and isinstance(p_on_arm2[0], (int, float)) and isinstance(p_on_arm2[1], (int, float))):
        raise ValueError("輸入點 (vertex, p_on_arm1, p_on_arm2) 必須是包含兩個數字 (x,y) 的元組。")

    # 計算向量 vec_v_arm1 和 vec_v_arm2
    vec_v_arm1 = (p_on_arm1[0] - vertex[0], p_on_arm1[1] - vertex[1])
    vec_v_arm2 = (p_on_arm2[0] - vertex[0], p_on_arm2[1] - vertex[1])

    len_v_arm1 = math.sqrt(vec_v_arm1[0]**2 + vec_v_arm1[1]**2)
    len_v_arm2 = math.sqrt(vec_v_arm2[0]**2 + vec_v_arm2[1]**2)

    if len_v_arm1 < 1e-9 or len_v_arm2 < 1e-9:
        raise ValueError("角臂的長度過短，無法計算角弧參數。")

    calculated_radius: float
    if isinstance(radius_config, (int, float)):
        calculated_radius = float(radius_config)
        if calculated_radius <= 0:
            raise ValueError("固定半徑必須為正數。")
    elif radius_config == "auto":
        shorter_arm_len = min(len_v_arm1, len_v_arm2)
        calculated_radius = shorter_arm_len * default_ratio
        calculated_radius = max(min_auto_radius, min(calculated_radius, max_auto_radius))
    # TODO: elif isinstance(radius_config, dict):
    #     pass # Parse detailed config
    else:
        raise ValueError(f"不支持的 radius_config 類型: {radius_config}")

    if is_right_angle_symbol:
        # 對於直角符號，calculated_radius 通常用作符號臂的長度 (size)
        size = calculated_radius
        
        unit_vec_v_arm1 = (vec_v_arm1[0] / len_v_arm1, vec_v_arm1[1] / len_v_arm1)
        unit_vec_v_arm2 = (vec_v_arm2[0] / len_v_arm2, vec_v_arm2[1] / len_v_arm2)

        p_sym_arm1 = (vertex[0] + size * unit_vec_v_arm1[0], vertex[1] + size * unit_vec_v_arm1[1])
        p_sym_arm2 = (vertex[0] + size * unit_vec_v_arm2[0], vertex[1] + size * unit_vec_v_arm2[1])
        
        return {
            'type': 'right_angle_symbol',
            'vertex': vertex,
            'p_on_arm1_for_symbol': p_sym_arm1,
            'p_on_arm2_for_symbol': p_sym_arm2,
            'size': size
        }
    else:
        # 計算角度
        angle_arm1_rad = math.atan2(vec_v_arm1[1], vec_v_arm1[0])
        angle_arm2_rad = math.atan2(vec_v_arm2[1], vec_v_arm2[0])
        
        # 確保 sweep_angle 在 (0, 2*pi) 之間，從 arm1 到 arm2 逆時針
        sweep_angle = angle_arm2_rad - angle_arm1_rad
        if sweep_angle < 0:
            sweep_angle += 2 * math.pi
        
        # 如果 sweep_angle > pi，我們可能想要的是小於 pi 的那個角，通過反轉 start 和 end
        # 或者，這意味著 p_on_arm1 和 p_on_arm2 的順序定義了一個優角。
        # 為了繪製內角，通常我們期望 sweep_angle <= pi。
        # 如果 sweep_angle > pi，則從 arm2 到 arm1 的角度是 2*pi - sweep_angle。
        # 這裡的邏輯是：如果直接掃描角大於180度，則反向掃描，並交換起始和結束臂。
        # 這確保我們總是得到小於或等於180度的角弧（除非三點共線且vertex在中間，形成平角）。
        # 叉積可以判斷 p_on_arm1 -> vertex -> p_on_arm2 的轉向
        cross_product = vec_v_arm1[0] * vec_v_arm2[1] - vec_v_arm1[1] * vec_v_arm2[0]

        # 如果叉積為負，表示從 vec_v_arm1 到 vec_v_arm2 是順時針的（對於標準數學座標系 y 軸向上）
        # 我們希望 atan2 給出的角度是標準的，所以 start_angle 和 end_angle 的順序決定了方向。
        # 為了繪製 "內部" 的角弧，我們通常希望 sweep angle <= pi.
        # 如果 sweep_angle > pi, 則 (start_angle, end_angle) 描述的是優角。
        # 此時，我們應該交換它們並從反方向繪製 (2*pi - sweep_angle)。
        
        # 修正：標準化為從 arm1 到 arm2 的最小正角
        # start_angle = angle_arm1_rad
        # end_angle = angle_arm2_rad
        # if cross_product < 0: # arm1 to arm2 is clockwise if we want counter-clockwise
        #    start_angle, end_angle = end_angle, start_angle # Swap to make it counter-clockwise
        
        # if end_angle < start_angle:
        #    end_angle += 2 * math.pi
        
        # 保持原始的 start_angle 和 end_angle，讓 ArcGenerator 決定如何繪製
        # 或者，我們總是返回一個正的 sweep angle?
        # 這裡的目標是提供給 ArcGenerator 足夠的信息。
        # ArcGenerator 可能期望 start_angle 和一個 sweep_angle，或者 start 和 end。
        # TikZ \draw (center) -- (start_point) arc (start_angle:end_angle:radius);
        # TikZ 角度是度數，且逆時針為正。

        return {
            'type': 'arc',
            'center': vertex,
            'radius': calculated_radius,
            'start_angle_rad': angle_arm1_rad, # Angle of vector from center to arc start
            'end_angle_rad': angle_arm2_rad    # Angle of vector from center to arc end
        }


def get_label_placement_params(
    element_type: Literal['vertex', 'side', 'angle_value'],
    target_elements: Dict[str, Any], # Contains points defining the element
    # e.g., for 'vertex': {'vertex_coord': Point}
    # e.g., for 'side': {'p_start': Point, 'p_end': Point}
    # e.g., for 'angle_value': {'vertex': Point, 'p_on_arm1': Point, 'p_on_arm2': Point}
    all_vertices: Tuple[Point, Point, Point], # p1, p2, p3 of the triangle
    special_points: Dict[str, Point], # e.g., {'incenter': Point, 'centroid': Point}
    user_preference: Any = "auto", # e.g., "auto", "above", "offset:(dx,dy)"
    default_offset: float = 0.15 # Default offset distance for "auto" placement
) -> Dict[str, Any]:
    """
    計算標籤的最佳放置參數。

    Args:
        element_type: 標籤應用的元素類型 ('vertex', 'side', 'angle_value')。
        target_elements: 定義目標元素的點座標字典。
        all_vertices: 三角形的三個頂點 (p1, p2, p3)。
        special_points: 包含其他特殊點的字典，如內心、質心等。
        user_preference: 用戶指定的放置偏好。
        default_offset: "auto" 模式下的默認偏移距離。

    Returns:
        一個字典，包含傳遞給 LabelGenerator 的定位參數。
        可能的鍵包括:
        - 'reference_point': Point, 標籤定位的參考點。
        - 'tikz_options': str, 例如 "above right=0.1cm" 或 "anchor=north west".
        - 'offset_vector': Point, (dx, dy) 從參考點的偏移。
        - 'rotation': float, 標籤的旋轉角度 (度)。
        - 'label_anchor': str, 標籤自身的錨點 (e.g., 'c', 'nw', 's').
    """
    # 參數驗證 (簡化版，實際應更詳細)
    if element_type not in ['vertex', 'side', 'angle_value']:
        raise ValueError(f"不支持的 element_type: {element_type}")

    # TODO: 實現詳細的定位邏輯
    # 這是一個非常複雜的函數，這裡只是一個框架
    # 實際實現需要大量的幾何計算和啟發式規則

    placement_params: Dict[str, Any] = {}

    if element_type == 'vertex':
        vertex_coord = target_elements.get('vertex_coord')
        if not vertex_coord or not (isinstance(vertex_coord, tuple) and len(vertex_coord) == 2 and isinstance(vertex_coord[0], (int,float)) and isinstance(vertex_coord[1], (int,float))):
            raise ValueError("對於 'vertex' 類型，target_elements['vertex_coord'] 必須是一個有效的 Point。")
        
        # 找到另外兩個頂點
        other_vertices = [v for v in all_vertices if v != vertex_coord]
        if len(other_vertices) != 2:
            # 這種情況理論上不應發生，如果 all_vertices 總是包含3個不同的點
            # 作為備用方案，簡單地放在上方
            placement_params['reference_point'] = vertex_coord
            placement_params['tikz_options'] = f"above={default_offset}cm"
            placement_params['label_anchor'] = "south"
            return placement_params

        ov1, ov2 = other_vertices[0], other_vertices[1]

        # 計算從 vertex_coord 指向 ov1 和 ov2 的向量
        vec1 = (ov1[0] - vertex_coord[0], ov1[1] - vertex_coord[1])
        vec2 = (ov2[0] - vertex_coord[0], ov2[1] - vertex_coord[1])

        len_vec1 = _distance(vertex_coord, ov1)
        len_vec2 = _distance(vertex_coord, ov2)

        if len_vec1 < 1e-9 or len_vec2 < 1e-9: # 邊長過短
            placement_params['reference_point'] = vertex_coord
            placement_params['tikz_options'] = f"above right={default_offset}cm" # 備用
            placement_params['label_anchor'] = "sw"
            return placement_params

        # 單位向量
        unit_vec1 = (vec1[0] / len_vec1, vec1[1] / len_vec1)
        unit_vec2 = (vec2[0] / len_vec2, vec2[1] / len_vec2)

        # 角平分線的反方向向量 (指向外部)
        bisector_inv_x = unit_vec1[0] + unit_vec2[0]
        bisector_inv_y = unit_vec1[1] + unit_vec2[1]
        
        # 歸一化角平分線的反方向向量
        len_bisector_inv = math.sqrt(bisector_inv_x**2 + bisector_inv_y**2)

        label_pos_x: float
        label_pos_y: float
        tikz_position_keyword = "above" # Default
        label_anchor_guess = "s"    # Default

        if len_bisector_inv < 1e-9: # vec1 和 vec2 方向幾乎相反 (頂點在另兩點之間且共線)
            # 這種情況下，角平分線無定義或方向不穩定。
            # 取垂直於 ov1-ov2 連線的方向。例如，如果 ov1-ov2 近似水平，則向上/下。
            # 簡化：直接使用 (0,1) 或 (0,-1) 作為偏移方向，或基於一個固定的 "above"
            # 或者，如果 vertex_coord 是 (say) p1, ov1=p2, ov2=p3，
            # 且 p1 在 p2,p3 之間，那麼角是180度。標籤應放在 p2-p3 線段的上方或下方。
            # 這裡用一個簡單的備用：
            placement_direction_x, placement_direction_y = -vec1[1], vec1[0] # 垂直於 vec1
            len_pd = math.sqrt(placement_direction_x**2 + placement_direction_y**2)
            if len_pd < 1e-9: # 如果 vec1 也是零向量 (不可能，已檢查 len_vec1)
                 placement_direction_x, placement_direction_y = 0, 1 # 備用向上
            else:
                 placement_direction_x /= len_pd
                 placement_direction_y /= len_pd
            # 確保方向是 "外側" (這需要更複雜的判斷，例如基於三角形的順序或內心)
            # 暫時使用一個固定偏移
            label_pos_x = vertex_coord[0] + default_offset * placement_direction_x
            label_pos_y = vertex_coord[1] + default_offset * placement_direction_y
            # 根據 placement_direction_x/y 粗略猜測 tikz_position_keyword 和 label_anchor
            if abs(placement_direction_x) > abs(placement_direction_y):
                tikz_position_keyword = "right" if placement_direction_x > 0 else "left"
                label_anchor_guess = "w" if placement_direction_x > 0 else "e"
            else:
                tikz_position_keyword = "above" if placement_direction_y > 0 else "below"
                label_anchor_guess = "s" if placement_direction_y > 0 else "n"

        else:
            # 角平分線反方向 (指向外側)
            placement_direction_x = -bisector_inv_x / len_bisector_inv
            placement_direction_y = -bisector_inv_y / len_bisector_inv
            
            label_pos_x = vertex_coord[0] + default_offset * placement_direction_x
            label_pos_y = vertex_coord[1] + default_offset * placement_direction_y

            # 根據 placement_direction_x/y 粗略猜測 tikz_position_keyword 和 label_anchor
            # 這部分可以非常精細
            if placement_direction_y > 0.5: # 主要向上
                label_anchor_guess = "s"
                if placement_direction_x > 0.5: tikz_position_keyword = "above right"
                elif placement_direction_x < -0.5: tikz_position_keyword = "above left"
                else: tikz_position_keyword = "above"
            elif placement_direction_y < -0.5: # 主要向下
                label_anchor_guess = "n"
                if placement_direction_x > 0.5: tikz_position_keyword = "below right"
                elif placement_direction_x < -0.5: tikz_position_keyword = "below left"
                else: tikz_position_keyword = "below"
            else: # 主要水平
                if placement_direction_x > 0: # 主要向右
                    tikz_position_keyword = "right"
                    label_anchor_guess = "w"
                else: # 主要向左
                    tikz_position_keyword = "left"
                    label_anchor_guess = "e"
        
        placement_params['reference_point'] = (label_pos_x, label_pos_y) # 標籤的絕對位置
        # 為了使用 TikZ 的相對定位，我們也可以提供相對於 vertex_coord 的選項
        # 例如，不直接計算 label_pos_x, label_pos_y，而是返回 tikz_options
        # placement_params['reference_node_id'] = "id_of_vertex_node" (如果頂點有 TikZ node id)
        # placement_params['tikz_options'] = f"{tikz_position_keyword}={default_offset}cm"
        # placement_params['label_anchor'] = label_anchor_guess
        
        # 當前實現是計算絕對座標，然後讓 LabelGenerator 在那裡放一個中心錨定的標籤
        # 或者，我們可以讓 LabelGenerator 更智能，接收 tikz_position_keyword 和 label_anchor_guess
        # 這裡我們返回計算出的絕對座標，並建議一個錨點
        placement_params['label_anchor'] = "center" # 讓標籤中心在計算出的點上
        # tikz_options 留空，因為我們提供了絕對座標

    elif element_type == 'side':
        p_start = target_elements.get('p_start')
        p_end = target_elements.get('p_end')

        if not (p_start and p_end and
                isinstance(p_start, tuple) and len(p_start) == 2 and isinstance(p_start[0], (int,float)) and isinstance(p_start[1], (int,float)) and
                isinstance(p_end, tuple) and len(p_end) == 2 and isinstance(p_end[0], (int,float)) and isinstance(p_end[1], (int,float))):
            raise ValueError("對於 'side' 類型，target_elements 必須包含有效的 'p_start' 和 'p_end' Point 對象。")

        mid_point = get_midpoint(p_start, p_end)
        
        # 邊向量
        side_dx = p_end[0] - p_start[0]
        side_dy = p_end[1] - p_start[1]
        len_side = math.sqrt(side_dx**2 + side_dy**2)

        if len_side < 1e-9: # 邊長為零 (p_start 和 p_end 重合)
            placement_params['reference_point'] = mid_point
            # tikz_options 應由 LabelGenerator 根據其他參數（如顏色）構建，或由用戶偏好提供
            # 這裡提供一個簡單的相對定位給 LabelParams 的 position_modifiers
            placement_params['position_modifiers'] = f"above={default_offset}cm"
            placement_params['label_anchor'] = "south" # 標籤底部在中點上方
            placement_params['rotation'] = 0.0 # 水平
            # 注意：get_label_placement_params 的返回字典結構需要與 LabelParams 期望的輸入對應
            # 或者返回一個可以直接用於 TikZ node 的 options 字符串。
            # 根據當前 LabelParams 設計，我們應該填充 'reference_point', 'rotation', 'label_anchor' 等。
            # 'tikz_options' 這個鍵在 get_label_placement_params 的返回中不再直接使用，
            # 而是分解為更結構化的參數如 position_modifiers, anchor, rotate。
            return placement_params

        # 初始法向量 (p_start -> p_end 方向逆時針旋轉90度)
        normal_dx = -side_dy
        normal_dy = side_dx
        
        # 歸一化法向量
        unit_normal_dx = normal_dx / len_side # len_normal is same as len_side here
        unit_normal_dy = normal_dy / len_side

        # 確定法線朝向 (指向三角形 "外部" 或一個清晰的偏移方向)
        p_other = None
        # 確保比較的是值而不是對象引用，對於元組 (float, float) 來說，直接比較即可
        for v_coord_candidate in all_vertices:
            is_p_start = abs(v_coord_candidate[0] - p_start[0]) < 1e-9 and abs(v_coord_candidate[1] - p_start[1]) < 1e-9
            is_p_end = abs(v_coord_candidate[0] - p_end[0]) < 1e-9 and abs(v_coord_candidate[1] - p_end[1]) < 1e-9
            if not is_p_start and not is_p_end:
                p_other = v_coord_candidate
                break
        
        if p_other:
            vec_mid_to_other_dx = p_other[0] - mid_point[0]
            vec_mid_to_other_dy = p_other[1] - mid_point[1]
            
            dot_product = unit_normal_dx * vec_mid_to_other_dx + unit_normal_dy * vec_mid_to_other_dy
            if dot_product > 0: # 法線與指向 p_other 的向量同向 (即指向內部，或 p_other 所在一側)
                unit_normal_dx *= -1 # 反轉法線方向，使其指向外部
                unit_normal_dy *= -1
        # else: 如果找不到 p_other (例如，target_elements 不是完整三角形的邊，或者 all_vertices 不正確)
        #       則使用初步的法線方向 (normal_dx, normal_dy)。
        #       或者，如果 special_points['centroid'] 可用，可以用它來判斷內外側，這更魯棒。
        #       centroid = special_points.get('centroid')
        #       if centroid:
        #           vec_mid_to_centroid_dx = centroid[0] - mid_point[0]
        #           vec_mid_to_centroid_dy = centroid[1] - mid_point[1]
        #           dot_product_centroid = unit_normal_dx * vec_mid_to_centroid_dx + unit_normal_dy * vec_mid_to_centroid_dy
        #           if dot_product_centroid > 0: # 指向質心 (內部)
        #               unit_normal_dx *= -1
        #               unit_normal_dy *= -1
        
        label_pos_x = mid_point[0] + unit_normal_dx * default_offset
        label_pos_y = mid_point[1] + unit_normal_dy * default_offset
        
        placement_params['reference_point'] = (label_pos_x, label_pos_y) # 標籤將放置的絕對座標
        placement_params['label_anchor'] = "center" # 讓標籤的中心位於計算出的 label_pos
        
        angle_rad_side = math.atan2(side_dy, side_dx)
        rotation_deg = math.degrees(angle_rad_side)

        # 調整旋轉角度以確保文字可讀性
        # 如果角度 > 90度 或 < -90度，文字會倒置。
        # 將其調整到 [-90, 90] 範圍內，通過 +/- 180 度。
        if rotation_deg > 90:
            rotation_deg -= 180
        elif rotation_deg < -90:
            rotation_deg += 180
            
        placement_params['rotation'] = rotation_deg # 標籤與邊平行（或反平行），但文字方向正確
        # 'position_modifiers' 和 'additional_node_options' 可以在這裡留空，
        # 或者根據更複雜的規則填充 (例如，如果用戶偏好是 "above side")


    elif element_type == 'angle_value':
        vertex = target_elements.get('vertex')
        p_on_arm1 = target_elements.get('p_on_arm1')
        p_on_arm2 = target_elements.get('p_on_arm2')

        if not (vertex and p_on_arm1 and p_on_arm2 and
                isinstance(vertex, tuple) and len(vertex) == 2 and isinstance(vertex[0], (int,float)) and isinstance(vertex[1], (int,float)) and
                isinstance(p_on_arm1, tuple) and len(p_on_arm1) == 2 and isinstance(p_on_arm1[0], (int,float)) and isinstance(p_on_arm1[1], (int,float)) and
                isinstance(p_on_arm2, tuple) and len(p_on_arm2) == 2 and isinstance(p_on_arm2[0], (int,float)) and isinstance(p_on_arm2[1], (int,float))):
            raise ValueError("對於 'angle_value' 類型，target_elements 必須包含有效的 'vertex', 'p_on_arm1', 'p_on_arm2' Point 對象。")

        vec1_x, vec1_y = p_on_arm1[0] - vertex[0], p_on_arm1[1] - vertex[1]
        vec2_x, vec2_y = p_on_arm2[0] - vertex[0], p_on_arm2[1] - vertex[1]

        len_vec1 = math.sqrt(vec1_x**2 + vec1_y**2)
        len_vec2 = math.sqrt(vec2_x**2 + vec2_y**2)

        if len_vec1 < 1e-9 or len_vec2 < 1e-9:
            placement_params['reference_point'] = (vertex[0] + default_offset, vertex[1] + default_offset)
            placement_params['label_anchor'] = "sw"
            placement_params['rotation'] = 0.0
            return placement_params
            
        unit_vec1_x, unit_vec1_y = vec1_x / len_vec1, vec1_y / len_vec1
        unit_vec2_x, unit_vec2_y = vec2_x / len_vec2, vec2_y / len_vec2

        bisector_x = unit_vec1_x + unit_vec2_x
        bisector_y = unit_vec1_y + unit_vec2_y
        len_bisector = math.sqrt(bisector_x**2 + bisector_y**2)

        label_pos_x: float
        label_pos_y: float

        if len_bisector < 1e-9: # 兩向量方向相反 (180度角)
            placement_dir_x = -unit_vec1_y # 垂直於 vec1
            placement_dir_y = unit_vec1_x
            # 簡單處理方向，可能需要根據具體情況調整以確保 "外部"
            # 例如，如果 p_on_arm1 和 p_on_arm2 的中點在 vertex 的 "下方"，則向上偏移
            # mid_arms = get_midpoint(p_on_arm1, p_on_arm2)
            # if mid_arms[1] < vertex[1] and placement_dir_y < 0: placement_dir_y *= -1
            # if mid_arms[0] < vertex[0] and placement_dir_x < 0: placement_dir_x *= -1
            # 默認取一個方向
            if placement_dir_y < 0 : # 優先向上
                 placement_dir_y *= -1
                 placement_dir_x *= -1
            elif abs(placement_dir_y) < 1e-9 and placement_dir_x < 0: # 如果是水平的，優先向右
                 placement_dir_x *= -1

            label_pos_x = vertex[0] + placement_dir_x * (default_offset * 1.5) # 稍遠一點
            label_pos_y = vertex[1] + placement_dir_y * (default_offset * 1.5)
        else:
            unit_bisector_x = bisector_x / len_bisector
            unit_bisector_y = bisector_y / len_bisector
            
            # 使用較小的 default_ratio 讓角弧更貼近頂點，標籤在其外
            arc_params = get_arc_render_params(vertex, p_on_arm1, p_on_arm2, radius_config="auto",
                                               default_ratio=0.1, min_auto_radius=0.05, max_auto_radius=0.4)
            label_distance = arc_params['radius'] + default_offset
            
            label_pos_x = vertex[0] + unit_bisector_x * label_distance
            label_pos_y = vertex[1] + unit_bisector_y * label_distance
            
        placement_params['reference_point'] = (label_pos_x, label_pos_y)
        placement_params['label_anchor'] = "center"
        placement_params['rotation'] = 0.0 # 角度值標籤通常水平


    # 最終可以根據 user_preference 覆蓋或調整 "auto" 的結果
    # if isinstance(user_preference, str) and user_preference != "auto":
    #    placement_params['tikz_options'] = user_preference # e.g. "above left"

    return placement_params

# TODO: 實現更詳細的標籤定位邏輯和 user_preference 處理