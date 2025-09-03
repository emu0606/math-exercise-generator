"""
TikZ 渲染類型定義

定義 TikZ 圖形渲染相關的數據類型和配置結構。

使用方式：
    from utils.tikz.types import ArcConfig, LabelConfig, TikZPosition
    
    # 創建弧線配置
    arc_config = ArcConfig(radius=0.3, arc_type='angle_arc')
    
    # 創建標籤配置
    label_config = LabelConfig(offset=0.15, position=TikZPosition.ABOVE)
"""

from typing import Union, Literal, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
from ..geometry.types import Point


# 基本類型別名
TikZCoordinate = Union[Point, str]  # TikZ 座標：Point 物件或座標字串
TikZDistance = Union[float, str]    # TikZ 距離：數值或帶單位的字串
TikZAngle = float                   # TikZ 角度（弧度制）

# 弧線類型
ArcType = Literal['angle_arc', 'right_angle', 'custom']

# 標籤類型  
LabelType = Literal['vertex', 'side', 'angle_value']

# 座標轉換類型
CoordinateSystem = Literal['cartesian', 'polar', 'tikz_native']


class TikZPosition(Enum):
    """TikZ 位置枚舉
    
    定義標準的 TikZ 位置關鍵字。
    """
    # 基本方向
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"
    CENTER = "center"
    
    # 對角線方向
    NORTH_EAST = "north east"
    NORTH_WEST = "north west"
    SOUTH_EAST = "south east"
    SOUTH_WEST = "south west"
    
    # 簡化別名
    ABOVE = "above"
    BELOW = "below"
    LEFT = "left"
    RIGHT = "right"
    
    # 帶距離的位置
    ABOVE_LEFT = "above left"
    ABOVE_RIGHT = "above right"
    BELOW_LEFT = "below left"
    BELOW_RIGHT = "below right"


class TikZAnchor(Enum):
    """TikZ 錨點枚舉
    
    定義節點的錨點位置。
    """
    # 基本錨點
    CENTER = "center"
    BASE = "base"
    
    # 邊界錨點
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"
    
    # 角落錨點
    NORTH_EAST = "north east"
    NORTH_WEST = "north west"
    SOUTH_EAST = "south east"
    SOUTH_WEST = "south west"
    
    # 文本錨點
    BASE_EAST = "base east"
    BASE_WEST = "base west"
    MID_EAST = "mid east"
    MID_WEST = "mid west"


@dataclass
class ArcConfig:
    """弧線渲染配置
    
    Attributes:
        radius: 弧線半徑
        arc_type: 弧線類型
        start_angle: 起始角度（弧度制）
        end_angle: 結束角度（弧度制）
        style_options: TikZ 樣式選項
    """
    radius: float
    arc_type: ArcType = 'angle_arc'
    start_angle: Optional[float] = None
    end_angle: Optional[float] = None
    style_options: Optional[Dict[str, str]] = None
    
    def __post_init__(self):
        """驗證配置參數"""
        if self.radius <= 0:
            from .exceptions import TikZConfigError
            raise TikZConfigError("arc_radius", self.radius, "弧線半徑必須為正數")
        
        if self.style_options is None:
            self.style_options = {}


@dataclass
class LabelConfig:
    """標籤渲染配置
    
    Attributes:
        offset: 標籤偏移距離
        position: TikZ 位置關鍵字
        anchor: TikZ 錨點
        style_options: TikZ 樣式選項
        auto_position: 是否自動推斷位置
    """
    offset: float = 0.15
    position: Optional[Union[TikZPosition, str]] = None
    anchor: Optional[Union[TikZAnchor, str]] = None
    style_options: Optional[Dict[str, str]] = None
    auto_position: bool = True
    
    def __post_init__(self):
        """驗證和標準化配置參數"""
        if self.offset <= 0:
            from .exceptions import TikZConfigError
            raise TikZConfigError("label_offset", self.offset, "標籤偏移必須為正數")
        
        if self.style_options is None:
            self.style_options = {}
        
        # 標準化位置和錨點
        if isinstance(self.position, TikZPosition):
            self.position = self.position.value
        if isinstance(self.anchor, TikZAnchor):
            self.anchor = self.anchor.value


@dataclass
class CoordinateTransform:
    """座標轉換配置
    
    Attributes:
        source_system: 源座標系統
        target_system: 目標座標系統
        scale_factor: 縮放係數
        offset: 偏移量
        rotation: 旋轉角度（弧度制）
    """
    source_system: CoordinateSystem = 'cartesian'
    target_system: CoordinateSystem = 'tikz_native'
    scale_factor: float = 1.0
    offset: Point = None
    rotation: float = 0.0
    
    def __post_init__(self):
        """初始化預設值"""
        if self.offset is None:
            self.offset = Point(0.0, 0.0)


@dataclass
class RenderingContext:
    """渲染上下文
    
    包含渲染過程中的全域設定和狀態資訊。
    
    Attributes:
        precision: TikZ 座標精度（小數位數）
        unit: 長度單位
        default_arc_config: 預設弧線配置
        default_label_config: 預設標籤配置
        coordinate_transform: 座標轉換配置
        debug_mode: 是否啟用調試模式
    """
    precision: int = 3
    unit: str = "cm"
    default_arc_config: Optional[ArcConfig] = None
    default_label_config: Optional[LabelConfig] = None
    coordinate_transform: Optional[CoordinateTransform] = None
    debug_mode: bool = False
    
    def __post_init__(self):
        """初始化預設配置"""
        if self.default_arc_config is None:
            self.default_arc_config = ArcConfig(radius=0.3)
        
        if self.default_label_config is None:
            self.default_label_config = LabelConfig()
        
        if self.coordinate_transform is None:
            self.coordinate_transform = CoordinateTransform()
        
        # 驗證精度設定
        if not 0 <= self.precision <= 10:
            from .exceptions import TikZConfigError
            raise TikZConfigError("precision", self.precision, "精度必須在 0-10 之間")


@dataclass
class ArcParameters:
    """弧線渲染參數
    
    包含弧線繪製所需的所有參數。
    
    Attributes:
        center: 弧線中心點
        radius: 弧線半徑
        start_angle: 起始角度（弧度制）
        end_angle: 結束角度（弧度制）
        arc_type: 弧線類型
        tikz_code: 生成的 TikZ 代碼
    """
    center: Point
    radius: float
    start_angle: float
    end_angle: float
    arc_type: ArcType
    tikz_code: str = ""
    
    @property
    def angle_span(self) -> float:
        """角度跨度（弧度制）"""
        return abs(self.end_angle - self.start_angle)
    
    @property
    def angle_span_degrees(self) -> float:
        """角度跨度（度數制）"""
        import math
        return math.degrees(self.angle_span)


@dataclass 
class LabelParameters:
    """標籤放置參數
    
    包含標籤放置所需的所有參數。
    
    Attributes:
        position: 標籤位置座標
        tikz_position: TikZ 位置關鍵字
        tikz_anchor: TikZ 錨點
        offset_distance: 偏移距離
        rotation_angle: 旋轉角度（弧度制）
        tikz_code: 生成的 TikZ 代碼
    """
    position: Point
    tikz_position: str
    tikz_anchor: str
    offset_distance: float
    rotation_angle: float = 0.0
    tikz_code: str = ""


# 工具函數

def normalize_tikz_position(position: Union[TikZPosition, str, None]) -> Optional[str]:
    """標準化 TikZ 位置字串
    
    Args:
        position: 位置值
        
    Returns:
        標準化的位置字串，或 None
    """
    if position is None:
        return None
    
    if isinstance(position, TikZPosition):
        return position.value
    
    if isinstance(position, str):
        # 移除多餘空格並轉為小寫
        normalized = ' '.join(position.lower().split())
        
        # 驗證是否為有效位置
        valid_positions = {pos.value for pos in TikZPosition}
        if normalized in valid_positions:
            return normalized
        
        # 如果不是標準位置，返回原值（可能是自定義位置）
        return normalized
    
    return str(position)


def normalize_tikz_anchor(anchor: Union[TikZAnchor, str, None]) -> Optional[str]:
    """標準化 TikZ 錨點字串
    
    Args:
        anchor: 錨點值
        
    Returns:
        標準化的錨點字串，或 None
    """
    if anchor is None:
        return None
    
    if isinstance(anchor, TikZAnchor):
        return anchor.value
    
    if isinstance(anchor, str):
        # 移除多餘空格並轉為小寫
        normalized = ' '.join(anchor.lower().split())
        
        # 驗證是否為有效錨點
        valid_anchors = {anchor.value for anchor in TikZAnchor}
        if normalized in valid_anchors:
            return normalized
        
        # 如果不是標準錨點，返回原值（可能是自定義錨點）
        return normalized
    
    return str(anchor)


def format_tikz_coordinate(point: Point, precision: int = 3, unit: str = "cm") -> str:
    """格式化 TikZ 座標字串
    
    Args:
        point: 座標點
        precision: 精度（小數位數）
        unit: 長度單位
        
    Returns:
        格式化的 TikZ 座標字串
        
    Example:
        >>> format_tikz_coordinate(Point(1.234, 5.678), precision=2)
        '(1.23cm, 5.68cm)'
    """
    if unit:
        return f"({point.x:.{precision}f}{unit}, {point.y:.{precision}f}{unit})"
    else:
        return f"({point.x:.{precision}f}, {point.y:.{precision}f})"


def format_tikz_angle(angle_rad: float, precision: int = 1) -> str:
    """格式化 TikZ 角度字串（轉為度數）
    
    Args:
        angle_rad: 角度（弧度制）
        precision: 精度（小數位數）
        
    Returns:
        格式化的角度字串
        
    Example:
        >>> import math
        >>> format_tikz_angle(math.pi/4)
        '45.0'
    """
    import math
    degrees = math.degrees(angle_rad)
    return f"{degrees:.{precision}f}"