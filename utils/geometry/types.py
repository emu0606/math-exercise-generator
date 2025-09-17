"""
幾何類型定義

定義現代化的幾何數據類型，替代原始的元組表示法，提供類型安全和更好的代碼可讀性。

使用方式：
    from utils.geometry.types import Point, Triangle, Circle
    
    # 創建點
    p1 = Point(0.0, 0.0)
    p2 = Point(1.0, 0.0)
    p3 = Point(0.5, 0.866)
    
    # 創建三角形
    triangle = Triangle(p1, p2, p3)
    
    # 訪問屬性
    area = triangle.area()
    centroid = triangle.centroid()
"""

import math
from typing import Tuple, NamedTuple, Optional, Literal, Union, Dict, Any
from dataclasses import dataclass
from .exceptions import ValidationError, TriangleDefinitionError, DegenerateTriangleError


# 基礎類型別名（保持向後相容）
PointTuple = Tuple[float, float]
TriangleTuple = Tuple[PointTuple, PointTuple, PointTuple]

# 三角形定義模式
TriangleDefinitionMode = Literal['sss', 'sas', 'asa', 'aas', 'coordinates']

# 數學後端類型
MathBackend = Literal['numpy', 'sympy', 'python']


@dataclass(frozen=True)
class Point:
    """點座標數據類
    
    提供不可變的點座標表示，替代原始的元組格式。
    
    Attributes:
        x: X座標
        y: Y座標
    """
    x: float
    y: float
    
    def __post_init__(self):
        """驗證座標值的有效性"""
        if not isinstance(self.x, (int, float)) or not isinstance(self.y, (int, float)):
            raise ValidationError("coordinates", (self.x, self.y), "座標必須是數值類型")
        
        if not (math.isfinite(self.x) and math.isfinite(self.y)):
            raise ValidationError("coordinates", (self.x, self.y), "座標必須是有限數值")
    
    def distance_to(self, other: 'Point') -> float:
        """計算到另一點的距離
        
        Args:
            other: 目標點
            
        Returns:
            兩點間的歐幾里得距離
        """
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def midpoint_to(self, other: 'Point') -> 'Point':
        """計算到另一點的中點
        
        Args:
            other: 目標點
            
        Returns:
            中點座標
        """
        return Point(
            (self.x + other.x) / 2,
            (self.y + other.y) / 2
        )
    
    def translate(self, dx: float, dy: float) -> 'Point':
        """平移點座標
        
        Args:
            dx: X方向位移
            dy: Y方向位移
            
        Returns:
            平移後的新點
        """
        return Point(self.x + dx, self.y + dy)
    
    def rotate(self, angle: float, center: Optional['Point'] = None) -> 'Point':
        """繞指定中心旋轉點
        
        Args:
            angle: 旋轉角度（弧度制）
            center: 旋轉中心，預設為原點
            
        Returns:
            旋轉後的新點
        """
        if center is None:
            center = Point(0.0, 0.0)
        
        # 相對於旋轉中心的座標
        rel_x = self.x - center.x
        rel_y = self.y - center.y
        
        # 旋轉變換
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        new_x = rel_x * cos_a - rel_y * sin_a + center.x
        new_y = rel_x * sin_a + rel_y * cos_a + center.y
        
        return Point(new_x, new_y)
    
    def to_tuple(self) -> PointTuple:
        """轉換為元組格式（向後相容）
        
        Returns:
            (x, y) 元組
        """
        return (self.x, self.y)
    
    @classmethod
    def from_tuple(cls, point_tuple: PointTuple) -> 'Point':
        """從元組創建點（向後相容）
        
        Args:
            point_tuple: (x, y) 元組
            
        Returns:
            Point 實例
        """
        if not isinstance(point_tuple, (tuple, list)) or len(point_tuple) != 2:
            raise ValidationError("point_tuple", point_tuple, "必須是長度為2的元組或列表")
        
        return cls(float(point_tuple[0]), float(point_tuple[1]))
    
    def to_tikz(self) -> str:
        """轉換為TikZ座標格式

        Returns:
            str: TikZ格式的座標字串，例如 "(1.5, 2.0)"

        Example:
            >>> p = Point(1.5, 2.0)
            >>> p.to_tikz()
            '(1.5, 2.0)'
        """
        return f"({self.x}, {self.y})"

    def __str__(self) -> str:
        """字串表示"""
        return f"Point({self.x:.3f}, {self.y:.3f})"

    def __repr__(self) -> str:
        """詳細字串表示"""
        return f"Point(x={self.x}, y={self.y})"


@dataclass(frozen=True)
class Vector:
    """向量數據類
    
    表示二維向量，提供向量運算功能。
    
    Attributes:
        x: X分量
        y: Y分量
    """
    x: float
    y: float
    
    def __post_init__(self):
        """驗證向量分量的有效性"""
        if not (math.isfinite(self.x) and math.isfinite(self.y)):
            raise ValidationError("vector", (self.x, self.y), "向量分量必須是有限數值")
    
    @property
    def magnitude(self) -> float:
        """向量長度（模）"""
        return math.sqrt(self.x**2 + self.y**2)
    
    @property
    def angle(self) -> float:
        """向量角度（弧度制）"""
        return math.atan2(self.y, self.x)
    
    def normalize(self) -> 'Vector':
        """單位化向量
        
        Returns:
            單位向量
            
        Raises:
            ValidationError: 如果向量長度為零
        """
        mag = self.magnitude
        if abs(mag) < 1e-9:
            raise ValidationError("vector", self, "無法單位化零向量")
        
        return Vector(self.x / mag, self.y / mag)
    
    def dot(self, other: 'Vector') -> float:
        """向量點積
        
        Args:
            other: 另一個向量
            
        Returns:
            點積結果
        """
        return self.x * other.x + self.y * other.y
    
    def cross(self, other: 'Vector') -> float:
        """向量叉積（二維情況下返回標量）
        
        Args:
            other: 另一個向量
            
        Returns:
            叉積結果
        """
        return self.x * other.y - self.y * other.x
    
    def __add__(self, other: 'Vector') -> 'Vector':
        """向量加法"""
        return Vector(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: 'Vector') -> 'Vector':
        """向量減法"""
        return Vector(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar: float) -> 'Vector':
        """標量乘法"""
        return Vector(self.x * scalar, self.y * scalar)
    
    def __rmul__(self, scalar: float) -> 'Vector':
        """右標量乘法"""
        return self.__mul__(scalar)
    
    @classmethod
    def from_points(cls, start: Point, end: Point) -> 'Vector':
        """從兩個點創建向量
        
        Args:
            start: 起點
            end: 終點
            
        Returns:
            從起點到終點的向量
        """
        return cls(end.x - start.x, end.y - start.y)


@dataclass(frozen=True)
class Triangle:
    """三角形數據類
    
    表示由三個頂點構成的三角形，提供相關計算功能。
    
    Attributes:
        p1: 第一個頂點
        p2: 第二個頂點
        p3: 第三個頂點
    """
    p1: Point
    p2: Point
    p3: Point
    
    def __post_init__(self):
        """驗證三角形的有效性"""
        # 檢查是否為退化三角形（三點共線）
        area = self._calculate_signed_area()
        if abs(area) < 1e-9:
            raise DegenerateTriangleError(
                (self.p1.to_tuple(), self.p2.to_tuple(), self.p3.to_tuple()),
                f"三點共線或過於接近，面積 = {area}"
            )
    
    def _calculate_signed_area(self) -> float:
        """計算有符號面積（用於判斷方向和退化情況）"""
        return 0.5 * (
            (self.p2.x - self.p1.x) * (self.p3.y - self.p1.y) - 
            (self.p3.x - self.p1.x) * (self.p2.y - self.p1.y)
        )
    
    def area(self) -> float:
        """計算三角形面積
        
        Returns:
            三角形面積（非負值）
        """
        return abs(self._calculate_signed_area())
    
    def perimeter(self) -> float:
        """計算三角形周長
        
        Returns:
            三角形周長
        """
        return (self.p1.distance_to(self.p2) + 
                self.p2.distance_to(self.p3) + 
                self.p3.distance_to(self.p1))
    
    def side_lengths(self) -> Tuple[float, float, float]:
        """獲取三邊長度
        
        Returns:
            (a, b, c) 其中 a=|p2p3|, b=|p1p3|, c=|p1p2|
        """
        a = self.p2.distance_to(self.p3)  # P1對邊
        b = self.p1.distance_to(self.p3)  # P2對邊
        c = self.p1.distance_to(self.p2)  # P3對邊
        return (a, b, c)
    
    def centroid(self) -> Point:
        """計算質心（重心）
        
        Returns:
            質心座標
        """
        return Point(
            (self.p1.x + self.p2.x + self.p3.x) / 3,
            (self.p1.y + self.p2.y + self.p3.y) / 3
        )
    
    def is_clockwise(self) -> bool:
        """判斷頂點順序是否為順時針
        
        Returns:
            True 如果順時針，False 如果逆時針
        """
        return self._calculate_signed_area() < 0
    
    def to_tuple(self) -> TriangleTuple:
        """轉換為元組格式（向後相容）
        
        Returns:
            ((x1, y1), (x2, y2), (x3, y3)) 元組
        """
        return (self.p1.to_tuple(), self.p2.to_tuple(), self.p3.to_tuple())
    
    @classmethod
    def from_tuple(cls, triangle_tuple: TriangleTuple) -> 'Triangle':
        """從元組創建三角形（向後相容）
        
        Args:
            triangle_tuple: ((x1, y1), (x2, y2), (x3, y3)) 元組
            
        Returns:
            Triangle 實例
        """
        if not isinstance(triangle_tuple, (tuple, list)) or len(triangle_tuple) != 3:
            raise ValidationError("triangle_tuple", triangle_tuple, "必須是長度為3的元組或列表")
        
        return cls(
            Point.from_tuple(triangle_tuple[0]),
            Point.from_tuple(triangle_tuple[1]),
            Point.from_tuple(triangle_tuple[2])
        )


@dataclass(frozen=True)
class Circle:
    """圓形數據類
    
    表示由圓心和半徑定義的圓。
    
    Attributes:
        center: 圓心座標
        radius: 半徑
    """
    center: Point
    radius: float
    
    def __post_init__(self):
        """驗證圓的有效性"""
        if self.radius <= 0:
            raise ValidationError("radius", self.radius, "半徑必須為正數")
        
        if not math.isfinite(self.radius):
            raise ValidationError("radius", self.radius, "半徑必須是有限數值")
    
    def area(self) -> float:
        """計算圓面積
        
        Returns:
            圓面積
        """
        return math.pi * self.radius**2
    
    def circumference(self) -> float:
        """計算圓周長
        
        Returns:
            圓周長
        """
        return 2 * math.pi * self.radius
    
    def contains_point(self, point: Point) -> bool:
        """判斷點是否在圓內
        
        Args:
            point: 待判斷的點
            
        Returns:
            True 如果點在圓內或圓上
        """
        distance = self.center.distance_to(point)
        return distance <= self.radius
    
    def point_on_circle(self, angle: float) -> Point:
        """獲取圓上指定角度的點
        
        Args:
            angle: 角度（弧度制），從正X軸開始測量
            
        Returns:
            圓上的點
        """
        x = self.center.x + self.radius * math.cos(angle)
        y = self.center.y + self.radius * math.sin(angle)
        return Point(x, y)


@dataclass(frozen=True)
class Line:
    """直線數據類
    
    表示經過兩個點的直線。
    
    Attributes:
        p1: 直線上的第一個點
        p2: 直線上的第二個點
    """
    p1: Point
    p2: Point
    
    def __post_init__(self):
        """驗證直線的有效性"""
        if self.p1.distance_to(self.p2) < 1e-9:
            raise DegenerateTriangleError(
                (self.p1.to_tuple(), self.p2.to_tuple()),
                "兩點過於接近，無法定義直線"
            )
    
    @property
    def direction_vector(self) -> Vector:
        """獲取方向向量
        
        Returns:
            從p1到p2的方向向量
        """
        return Vector.from_points(self.p1, self.p2)
    
    @property
    def slope(self) -> float:
        """獲取斜率
        
        Returns:
            直線斜率
            
        Raises:
            ValueError: 如果直線垂直（斜率無窮大）
        """
        dx = self.p2.x - self.p1.x
        if abs(dx) < 1e-9:
            raise ValueError("垂直線的斜率無窮大")
        
        return (self.p2.y - self.p1.y) / dx
    
    def distance_to_point(self, point: Point) -> float:
        """計算點到直線的距離
        
        Args:
            point: 目標點
            
        Returns:
            點到直線的垂直距離
        """
        # 使用點到直線距離公式
        x0, y0 = point.x, point.y
        x1, y1 = self.p1.x, self.p1.y
        x2, y2 = self.p2.x, self.p2.y
        
        numerator = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
        denominator = math.sqrt((y2 - y1)**2 + (x2 - x1)**2)
        
        return numerator / denominator


# 幾何配置類型
@dataclass
class GeometryConfig:
    """幾何計算配置
    
    Attributes:
        precision: 數值精度容忍度
        math_backend: 數學計算後端
        angle_unit: 角度單位（'radian' 或 'degree'）
    """
    precision: float = 1e-9
    math_backend: MathBackend = 'python'
    angle_unit: Literal['radian', 'degree'] = 'radian'
    
    def __post_init__(self):
        """驗證配置有效性"""
        if self.precision <= 0:
            raise ValidationError("precision", self.precision, "精度必須為正數")
        
        if self.angle_unit not in ['radian', 'degree']:
            raise ValidationError("angle_unit", self.angle_unit, "角度單位必須是 'radian' 或 'degree'")


# 渲染相關類型
@dataclass
class LabelConfig:
    """標籤配置
    
    Attributes:
        offset_ratio: 偏移比例
        min_distance: 最小距離
        font_size: 字體大小
    """
    offset_ratio: float = 0.15
    min_distance: float = 0.1
    font_size: float = 10.0


@dataclass
class ArcConfig:
    """弧線配置
    
    Attributes:
        radius_ratio: 半徑比例
        angle_precision: 角度精度
        min_radius: 最小半徑
    """
    radius_ratio: float = 0.2
    angle_precision: int = 2
    min_radius: float = 0.1


# 工具函數：類型轉換和驗證

def ensure_point(point: Union[Point, PointTuple, Any]) -> Point:
    """確保輸入為 Point 類型
    
    Args:
        point: 點座標，可以是 Point 實例或元組
        
    Returns:
        Point 實例
        
    Raises:
        ValidationError: 如果無法轉換為有效點
    """
    if isinstance(point, Point):
        return point
    
    if isinstance(point, (tuple, list)) and len(point) == 2:
        try:
            return Point(float(point[0]), float(point[1]))
        except (ValueError, TypeError):
            pass
    
    raise ValidationError("point", point, "必須是 Point 實例或 (x, y) 數值對")


def ensure_triangle(triangle: Union[Triangle, TriangleTuple, Any]) -> Triangle:
    """確保輸入為 Triangle 類型
    
    Args:
        triangle: 三角形，可以是 Triangle 實例或座標元組
        
    Returns:
        Triangle 實例
        
    Raises:
        ValidationError: 如果無法轉換為有效三角形
    """
    if isinstance(triangle, Triangle):
        return triangle
    
    if isinstance(triangle, (tuple, list)) and len(triangle) == 3:
        try:
            return Triangle.from_tuple(triangle)
        except Exception:
            pass
    
    raise ValidationError("triangle", triangle, "必須是 Triangle 實例或三個點座標的元組")