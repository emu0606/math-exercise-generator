"""
基礎幾何運算

提供基礎的幾何計算功能，包括距離、角度、面積等常用運算。
這是從原始 geometry_utils.py 中提取的基礎計算功能。

使用方式：
    from utils.geometry.basic_ops import distance, midpoint, area_of_triangle
    
    # 計算距離
    dist = distance(p1, p2)
    
    # 計算中點
    mid = midpoint(p1, p2)
    
    # 計算三角形面積
    area = area_of_triangle(p1, p2, p3)
"""

import math
from typing import Union, Tuple, Optional
from .types import Point, Vector, Triangle, ensure_point, ensure_triangle
from .exceptions import ValidationError, ComputationError, DegenerateTriangleError
from .math_backend import get_math_backend, AbstractMathBackend
from ..core.logging import get_logger

# 模組專用日誌器
logger = get_logger(__name__)


def distance(p1: Union[Point, Tuple[float, float]], 
            p2: Union[Point, Tuple[float, float]], 
            backend: Optional[str] = None) -> float:
    """計算兩點間距離
    
    Args:
        p1: 第一個點
        p2: 第二個點
        backend: 數學後端名稱 ('numpy', 'sympy', 'python')，預設使用全域設定
        
    Returns:
        兩點間的歐幾里得距離
        
    Raises:
        ValidationError: 如果點座標無效
    """
    # 確保輸入為Point類型
    point1 = ensure_point(p1)
    point2 = ensure_point(p2)
    
    # 獲取數學後端
    math_backend = get_math_backend(backend)
    
    try:
        result = math_backend.distance(point1, point2)
        logger.debug(f"計算距離: {point1} 到 {point2} = {result}")
        return result
    except Exception as e:
        raise ComputationError(
            "distance_calculation",
            f"距離計算失敗: {str(e)}",
            p1=point1, p2=point2, backend=math_backend.name
        ) from e


def midpoint(p1: Union[Point, Tuple[float, float]], 
            p2: Union[Point, Tuple[float, float]]) -> Point:
    """計算兩點的中點
    
    Args:
        p1: 第一個點
        p2: 第二個點
        
    Returns:
        中點座標
        
    Raises:
        ValidationError: 如果點座標無效
    """
    # 確保輸入為Point類型
    point1 = ensure_point(p1)
    point2 = ensure_point(p2)
    
    try:
        mid_x = (point1.x + point2.x) / 2
        mid_y = (point1.y + point2.y) / 2
        
        result = Point(mid_x, mid_y)
        logger.debug(f"計算中點: {point1} 和 {point2} 的中點 = {result}")
        return result
    except Exception as e:
        raise ComputationError(
            "midpoint_calculation",
            f"中點計算失敗: {str(e)}",
            p1=point1, p2=point2
        ) from e


def centroid(*points: Union[Point, Tuple[float, float]]) -> Point:
    """計算多個點的質心（重心）
    
    Args:
        *points: 任意數量的點座標
        
    Returns:
        質心座標
        
    Raises:
        ValidationError: 如果沒有提供點或點座標無效
    """
    if not points:
        raise ValidationError("points", points, "必須提供至少一個點")
    
    # 確保所有輸入為Point類型
    valid_points = [ensure_point(p) for p in points]
    
    try:
        sum_x = sum(p.x for p in valid_points)
        sum_y = sum(p.y for p in valid_points)
        n = len(valid_points)
        
        result = Point(sum_x / n, sum_y / n)
        logger.debug(f"計算質心: {len(valid_points)} 個點的質心 = {result}")
        return result
    except Exception as e:
        raise ComputationError(
            "centroid_calculation",
            f"質心計算失敗: {str(e)}",
            points=valid_points
        ) from e


def area_of_triangle(triangle: Union[Triangle, Tuple]) -> float:
    """計算三角形面積
    
    Args:
        triangle: Triangle實例或包含三個點的元組
        
    Returns:
        三角形面積（非負值）
        
    Raises:
        ValidationError: 如果三角形無效
        DegenerateTriangleError: 如果三角形退化
    """
    # 確保輸入為Triangle類型
    tri = ensure_triangle(triangle)
    
    try:
        # 使用Triangle類自帶的area方法
        result = tri.area()
        logger.debug(f"計算三角形面積: {tri} = {result}")
        return result
    except Exception as e:
        raise ComputationError(
            "area_calculation",
            f"三角形面積計算失敗: {str(e)}",
            triangle=tri
        ) from e


def signed_area_of_triangle(p1: Union[Point, Tuple[float, float]], 
                           p2: Union[Point, Tuple[float, float]], 
                           p3: Union[Point, Tuple[float, float]]) -> float:
    """計算三角形有符號面積
    
    有符號面積可以用來判斷三個點的方向：
    - 正值：逆時針順序
    - 負值：順時針順序
    - 零：三點共線
    
    Args:
        p1: 第一個點
        p2: 第二個點
        p3: 第三個點
        
    Returns:
        有符號面積
    """
    # 確保輸入為Point類型
    point1 = ensure_point(p1)
    point2 = ensure_point(p2)
    point3 = ensure_point(p3)
    
    try:
        # 使用叉積公式計算有符號面積
        result = 0.5 * (
            (point2.x - point1.x) * (point3.y - point1.y) - 
            (point3.x - point1.x) * (point2.y - point1.y)
        )
        
        logger.debug(f"計算有符號面積: ({point1}, {point2}, {point3}) = {result}")
        return result
    except Exception as e:
        raise ComputationError(
            "signed_area_calculation",
            f"有符號面積計算失敗: {str(e)}",
            p1=point1, p2=point2, p3=point3
        ) from e


def is_clockwise(p1: Union[Point, Tuple[float, float]], 
                p2: Union[Point, Tuple[float, float]], 
                p3: Union[Point, Tuple[float, float]], 
                tolerance: float = 1e-9) -> bool:
    """判斷三個點是否按順時針排列
    
    Args:
        p1: 第一個點
        p2: 第二個點
        p3: 第三個點
        tolerance: 共線判斷容忍度
        
    Returns:
        True 如果順時針排列，False 如果逆時針排列
        
    Raises:
        DegenerateTriangleError: 如果三點共線
    """
    signed_area = signed_area_of_triangle(p1, p2, p3)
    
    if abs(signed_area) < tolerance:
        raise DegenerateTriangleError(
            (ensure_point(p1).to_tuple(), ensure_point(p2).to_tuple(), ensure_point(p3).to_tuple()),
            f"三點共線，無法判斷方向（有符號面積: {signed_area}）"
        )
    
    return signed_area < 0


def angle_between_vectors(v1: Union[Vector, Tuple[float, float]], 
                         v2: Union[Vector, Tuple[float, float]], 
                         backend: Optional[str] = None) -> float:
    """計算兩向量夾角
    
    Args:
        v1: 第一個向量
        v2: 第二個向量
        backend: 數學後端名稱，預設使用全域設定
        
    Returns:
        兩向量夾角（弧度制，範圍 [0, π]）
        
    Raises:
        ValidationError: 如果向量無效
        ComputationError: 如果包含零向量
    """
    # 確保輸入為Vector類型
    if isinstance(v1, (tuple, list)):
        vec1 = Vector(v1[0], v1[1])
    else:
        vec1 = v1
        
    if isinstance(v2, (tuple, list)):
        vec2 = Vector(v2[0], v2[1])
    else:
        vec2 = v2
    
    # 獲取數學後端
    math_backend = get_math_backend(backend)
    
    try:
        result = math_backend.angle_between_vectors(vec1, vec2)
        logger.debug(f"計算向量夾角: {vec1} 和 {vec2} = {result} 弧度")
        return result
    except Exception as e:
        raise ComputationError(
            "angle_calculation",
            f"向量夾角計算失敗: {str(e)}",
            v1=vec1, v2=vec2, backend=math_backend.name
        ) from e


def angle_at_vertex(vertex: Union[Point, Tuple[float, float]], 
                   point1: Union[Point, Tuple[float, float]], 
                   point2: Union[Point, Tuple[float, float]], 
                   backend: Optional[str] = None) -> float:
    """計算在頂點處的角度
    
    計算從vertex到point1和從vertex到point2兩條射線的夾角。
    
    Args:
        vertex: 角度頂點
        point1: 第一條射線上的點
        point2: 第二條射線上的點
        backend: 數學後端名稱，預設使用全域設定
        
    Returns:
        角度（弧度制，範圍 [0, π]）
        
    Raises:
        ValidationError: 如果點無效
        ComputationError: 如果計算失敗
    """
    # 確保輸入為Point類型
    v = ensure_point(vertex)
    p1 = ensure_point(point1)
    p2 = ensure_point(point2)
    
    # 創建向量
    vec1 = Vector.from_points(v, p1)
    vec2 = Vector.from_points(v, p2)
    
    return angle_between_vectors(vec1, vec2, backend)


def perpendicular_distance(point: Union[Point, Tuple[float, float]], 
                          line_p1: Union[Point, Tuple[float, float]], 
                          line_p2: Union[Point, Tuple[float, float]]) -> float:
    """計算點到直線的垂直距離
    
    Args:
        point: 目標點
        line_p1: 直線上的第一個點
        line_p2: 直線上的第二個點
        
    Returns:
        點到直線的垂直距離
        
    Raises:
        ValidationError: 如果點無效
        ComputationError: 如果兩個點相同（無法定義直線）
    """
    # 確保輸入為Point類型
    p = ensure_point(point)
    lp1 = ensure_point(line_p1)
    lp2 = ensure_point(line_p2)
    
    # 檢查是否能定義直線
    if distance(lp1, lp2) < 1e-9:
        raise ComputationError(
            "line_definition",
            "兩個點太接近，無法定義直線",
            line_p1=lp1, line_p2=lp2
        )
    
    try:
        # 使用點到直線距離公式
        # |（p2-p1) × (p1-p0)| / |p2-p1|
        # 其中 × 表示叉積，p0是目標點
        
        x0, y0 = p.x, p.y
        x1, y1 = lp1.x, lp1.y
        x2, y2 = lp2.x, lp2.y
        
        # 計算分子：|(y2-y1)*x0 - (x2-x1)*y0 + x2*y1 - y2*x1|
        numerator = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
        
        # 計算分母：√((y2-y1)² + (x2-x1)²)
        denominator = math.sqrt((y2 - y1)**2 + (x2 - x1)**2)
        
        result = numerator / denominator
        logger.debug(f"計算點到直線距離: {p} 到直線({lp1}, {lp2}) = {result}")
        return result
        
    except Exception as e:
        raise ComputationError(
            "perpendicular_distance_calculation",
            f"點到直線距離計算失敗: {str(e)}",
            point=p, line_p1=lp1, line_p2=lp2
        ) from e


def normalize_angle(angle: float) -> float:
    """將角度標準化到 [0, 2π) 範圍
    
    Args:
        angle: 角度（弧度制）
        
    Returns:
        標準化後的角度
    """
    try:
        # 使用模運算將角度標準化到 [0, 2π) 範圍
        result = angle % (2 * math.pi)
        if result < 0:
            result += 2 * math.pi
        
        return result
    except Exception as e:
        raise ComputationError(
            "angle_normalization",
            f"角度標準化失敗: {str(e)}",
            angle=angle
        ) from e


def angle_difference(angle1: float, angle2: float) -> float:
    """計算兩個角度的最小差值
    
    Args:
        angle1: 第一個角度（弧度制）
        angle2: 第二個角度（弧度制）
        
    Returns:
        角度差值，範圍 [0, π]
    """
    try:
        # 標準化角度
        a1 = normalize_angle(angle1)
        a2 = normalize_angle(angle2)
        
        # 計算差值
        diff = abs(a1 - a2)
        
        # 取最小角度差
        if diff > math.pi:
            diff = 2 * math.pi - diff
        
        return diff
    except Exception as e:
        raise ComputationError(
            "angle_difference_calculation",
            f"角度差值計算失敗: {str(e)}",
            angle1=angle1, angle2=angle2
        ) from e


def rotate_point(point: Union[Point, Tuple[float, float]], 
                center: Union[Point, Tuple[float, float]], 
                angle: float) -> Point:
    """繞指定中心旋轉點
    
    Args:
        point: 要旋轉的點
        center: 旋轉中心
        angle: 旋轉角度（弧度制，逆時針為正）
        
    Returns:
        旋轉後的點
        
    Raises:
        ValidationError: 如果點座標無效
    """
    # 確保輸入為Point類型
    p = ensure_point(point)
    c = ensure_point(center)
    
    try:
        # 平移到原點
        rel_x = p.x - c.x
        rel_y = p.y - c.y
        
        # 旋轉變換
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        new_x = rel_x * cos_a - rel_y * sin_a + c.x
        new_y = rel_x * sin_a + rel_y * cos_a + c.y
        
        result = Point(new_x, new_y)
        logger.debug(f"旋轉點: {p} 繞 {c} 旋轉 {angle} 弧度 = {result}")
        return result
        
    except Exception as e:
        raise ComputationError(
            "point_rotation",
            f"點旋轉計算失敗: {str(e)}",
            point=p, center=c, angle=angle
        ) from e


def reflect_point(point: Union[Point, Tuple[float, float]], 
                 line_p1: Union[Point, Tuple[float, float]], 
                 line_p2: Union[Point, Tuple[float, float]]) -> Point:
    """計算點關於直線的反射點
    
    Args:
        point: 要反射的點
        line_p1: 直線上的第一個點
        line_p2: 直線上的第二個點
        
    Returns:
        反射後的點
        
    Raises:
        ValidationError: 如果點座標無效
        ComputationError: 如果無法定義直線
    """
    # 確保輸入為Point類型
    p = ensure_point(point)
    lp1 = ensure_point(line_p1)
    lp2 = ensure_point(line_p2)
    
    # 檢查是否能定義直線
    line_length = distance(lp1, lp2)
    if line_length < 1e-9:
        raise ComputationError(
            "line_definition",
            "兩個點太接近，無法定義反射直線",
            line_p1=lp1, line_p2=lp2
        )
    
    try:
        # 計算直線的方向向量和法向量
        dx = lp2.x - lp1.x
        dy = lp2.y - lp1.y
        
        # 直線的法向量（垂直向量）
        nx = -dy / line_length
        ny = dx / line_length
        
        # 計算點到直線的距離（帶符號）
        # 使用點積判斷點在直線的哪一側
        px_rel = p.x - lp1.x
        py_rel = p.y - lp1.y
        
        # 距離（帶符號）
        signed_distance = px_rel * nx + py_rel * ny
        
        # 反射點：原點 - 2 * 距離 * 法向量
        reflected_x = p.x - 2 * signed_distance * nx
        reflected_y = p.y - 2 * signed_distance * ny
        
        result = Point(reflected_x, reflected_y)
        logger.debug(f"反射點: {p} 關於直線({lp1}, {lp2}) = {result}")
        return result
        
    except Exception as e:
        raise ComputationError(
            "point_reflection",
            f"點反射計算失敗: {str(e)}",
            point=p, line_p1=lp1, line_p2=lp2
        ) from e


def is_point_on_segment(point: Union[Point, Tuple[float, float]], 
                       segment_start: Union[Point, Tuple[float, float]], 
                       segment_end: Union[Point, Tuple[float, float]], 
                       tolerance: float = 1e-9) -> bool:
    """判斷點是否在線段上
    
    Args:
        point: 待判斷的點
        segment_start: 線段起點
        segment_end: 線段終點
        tolerance: 判斷容忍度
        
    Returns:
        True 如果點在線段上
    """
    # 確保輸入為Point類型
    p = ensure_point(point)
    start = ensure_point(segment_start)
    end = ensure_point(segment_end)
    
    try:
        # 計算向量
        seg_vec = Vector.from_points(start, end)
        point_vec = Vector.from_points(start, p)
        
        # 檢查是否平行（叉積為零）
        cross_product = seg_vec.cross(point_vec)
        if abs(cross_product) > tolerance:
            return False  # 不在直線上
        
        # 檢查是否在線段範圍內
        # 使用點積判斷方向和長度
        dot_product = seg_vec.dot(point_vec)
        seg_length_squared = seg_vec.dot(seg_vec)
        
        # 點積在 [0, seg_length²] 範圍內表示在線段上
        return 0 <= dot_product <= seg_length_squared
        
    except Exception as e:
        logger.debug(f"點在線段判斷失敗: {str(e)}")
        return False


# 便利函數：批次計算

def distances_from_point(source: Union[Point, Tuple[float, float]], 
                        targets: list, 
                        backend: Optional[str] = None) -> list:
    """計算從一個點到多個目標點的距離
    
    Args:
        source: 源點
        targets: 目標點列表
        backend: 數學後端名稱
        
    Returns:
        距離列表
    """
    source_point = ensure_point(source)
    results = []
    
    for target in targets:
        try:
            dist = distance(source_point, target, backend)
            results.append(dist)
        except Exception as e:
            logger.warning(f"計算到點 {target} 的距離失敗: {e}")
            results.append(float('inf'))
    
    return results


def find_closest_point(reference: Union[Point, Tuple[float, float]], 
                      candidates: list, 
                      backend: Optional[str] = None) -> Tuple[Point, float, int]:
    """找到最接近參考點的點
    
    Args:
        reference: 參考點
        candidates: 候選點列表
        backend: 數學後端名稱
        
    Returns:
        (最近點, 距離, 索引) 元組
        
    Raises:
        ValidationError: 如果候選點列表為空
    """
    if not candidates:
        raise ValidationError("candidates", candidates, "候選點列表不能為空")
    
    ref_point = ensure_point(reference)
    distances = distances_from_point(ref_point, candidates, backend)
    
    min_distance = min(distances)
    min_index = distances.index(min_distance)
    closest_point = ensure_point(candidates[min_index])
    
    return closest_point, min_distance, min_index