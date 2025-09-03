"""
TikZ 座標轉換器

提供座標系統轉換、格式化和 TikZ 代碼生成輔助功能。

主要功能：
- 座標格式化 (Point -> TikZ 座標字符串)
- 角度轉換 (弧度 -> 度數)
- 距離格式化 (數值 -> TikZ 距離字符串)
- TikZ 選項格式化

使用方式：
    from utils.tikz.coordinate_transform import CoordinateTransformer
    
    transformer = CoordinateTransformer()
    coord_str = transformer.tikz_coordinate((1.5, 2.3))  # "(1.5,2.3)"
    angle_deg = transformer.tikz_angle_degrees(math.pi/4)  # 45.0
"""

import math
from typing import Union, Dict, Any, List, Tuple, Optional
from ..geometry.types import Point, ensure_point
from .types import TikZCoordinate, TikZDistance, TikZAngle, CoordinateTransform
from .exceptions import CoordinateTransformError
from ..core.logging import get_logger

# 模組專用日誌器
logger = get_logger(__name__)


class CoordinateTransformer:
    """TikZ 座標轉換器
    
    負責處理各種座標系統轉換和 TikZ 格式化任務。
    """
    
    def __init__(self, precision: int = 3, unit: str = "cm"):
        """初始化座標轉換器
        
        Args:
            precision: 數值精度（小數位數）
            unit: 預設距離單位
        """
        self.precision = precision
        self.unit = unit
        logger.debug(f"初始化座標轉換器，精度: {precision}, 單位: {unit}")
    
    def tikz_coordinate(self, point: Union[Point, Tuple[float, float]], 
                       precision: Optional[int] = None) -> str:
        """將點轉換為 TikZ 座標字符串
        
        Args:
            point: 二維點座標
            precision: 可選的精度覆蓋
            
        Returns:
            TikZ 格式的座標字符串，例如 "(1.500,2.300)"
            
        Raises:
            CoordinateTransformError: 當座標轉換失敗時
        """
        try:
            point_obj = ensure_point(point)
            prec = precision if precision is not None else self.precision
            
            # 格式化座標
            x_str = f"{point_obj.x:.{prec}f}"
            y_str = f"{point_obj.y:.{prec}f}"
            
            coord_str = f"({x_str},{y_str})"
            logger.debug(f"座標轉換: {point} -> {coord_str}")
            
            return coord_str
            
        except Exception as e:
            raise CoordinateTransformError(
                f"座標轉換失敗: {point}",
                original_error=e,
                context={'point': point, 'precision': precision}
            )
    
    def tikz_angle_degrees(self, radians: float) -> float:
        """將弧度轉換為度數
        
        Args:
            radians: 角度（弧度）
            
        Returns:
            角度（度數）
            
        Raises:
            CoordinateTransformError: 當角度轉換失敗時
        """
        try:
            if not isinstance(radians, (int, float)):
                raise ValueError(f"角度必須為數值，得到: {type(radians)}")
            
            degrees = math.degrees(radians)
            logger.debug(f"角度轉換: {radians:.6f} rad -> {degrees:.3f}°")
            
            return degrees
            
        except Exception as e:
            raise CoordinateTransformError(
                f"角度轉換失敗: {radians}",
                original_error=e,
                context={'radians': radians}
            )
    
    def tikz_distance(self, value: float, unit: Optional[str] = None) -> str:
        """將數值轉換為 TikZ 距離字符串
        
        Args:
            value: 距離數值
            unit: 可選的單位覆蓋
            
        Returns:
            TikZ 格式的距離字符串，例如 "1.500cm"
            
        Raises:
            CoordinateTransformError: 當距離轉換失敗時
        """
        try:
            if not isinstance(value, (int, float)):
                raise ValueError(f"距離值必須為數值，得到: {type(value)}")
            
            if value < 0:
                raise ValueError(f"距離值不能為負數: {value}")
            
            unit_str = unit if unit is not None else self.unit
            distance_str = f"{value:.{self.precision}f}{unit_str}"
            
            logger.debug(f"距離轉換: {value} -> {distance_str}")
            return distance_str
            
        except Exception as e:
            raise CoordinateTransformError(
                f"距離轉換失敗: {value}",
                original_error=e,
                context={'value': value, 'unit': unit}
            )
    
    def tikz_options_format(self, options: Dict[str, Any]) -> str:
        """將選項字典格式化為 TikZ 選項字符串
        
        Args:
            options: 選項字典
            
        Returns:
            TikZ 格式的選項字符串，例如 "[draw=red,thick,rotate=45]"
            
        Raises:
            CoordinateTransformError: 當選項格式化失敗時
        """
        try:
            if not isinstance(options, dict):
                raise ValueError(f"選項必須為字典，得到: {type(options)}")
            
            if not options:
                return ""
            
            option_pairs = []
            for key, value in options.items():
                if isinstance(value, str):
                    option_pairs.append(f"{key}={value}")
                elif isinstance(value, (int, float)):
                    if key in ['rotate', 'scale', 'xshift', 'yshift']:
                        # 角度和縮放參數保持原值
                        option_pairs.append(f"{key}={value}")
                    else:
                        # 距離參數加上單位
                        option_pairs.append(f"{key}={value:.{self.precision}f}{self.unit}")
                elif isinstance(value, bool):
                    if value:
                        option_pairs.append(key)  # 布林選項只在為 True 時加入
                else:
                    # 其他類型轉為字符串
                    option_pairs.append(f"{key}={str(value)}")
            
            options_str = f"[{','.join(option_pairs)}]"
            logger.debug(f"選項格式化: {options} -> {options_str}")
            
            return options_str
            
        except Exception as e:
            raise CoordinateTransformError(
                f"選項格式化失敗: {options}",
                original_error=e,
                context={'options': options}
            )
    
    def normalize_angle_range(self, angle_degrees: float, 
                             min_angle: float = 0, 
                             max_angle: float = 360) -> float:
        """將角度標準化到指定範圍
        
        Args:
            angle_degrees: 輸入角度（度數）
            min_angle: 最小角度
            max_angle: 最大角度
            
        Returns:
            標準化後的角度
            
        Raises:
            CoordinateTransformError: 當角度標準化失敗時
        """
        try:
            if not isinstance(angle_degrees, (int, float)):
                raise ValueError(f"角度必須為數值，得到: {type(angle_degrees)}")
            
            if max_angle <= min_angle:
                raise ValueError(f"最大角度必須大於最小角度: {min_angle} >= {max_angle}")
            
            range_size = max_angle - min_angle
            normalized = angle_degrees
            
            # 將角度標準化到 [min_angle, max_angle) 範圍
            while normalized >= max_angle:
                normalized -= range_size
            while normalized < min_angle:
                normalized += range_size
            
            logger.debug(f"角度標準化: {angle_degrees:.3f}° -> {normalized:.3f}° (範圍: [{min_angle}, {max_angle}))")
            return normalized
            
        except Exception as e:
            raise CoordinateTransformError(
                f"角度標準化失敗: {angle_degrees}",
                original_error=e,
                context={
                    'angle_degrees': angle_degrees,
                    'min_angle': min_angle,
                    'max_angle': max_angle
                }
            )
    
    def coordinate_offset(self, point: Union[Point, Tuple[float, float]], 
                         offset_x: float, offset_y: float) -> str:
        """計算偏移後的座標字符串
        
        Args:
            point: 基準點
            offset_x: X 軸偏移量
            offset_y: Y 軸偏移量
            
        Returns:
            偏移後的 TikZ 座標字符串
            
        Raises:
            CoordinateTransformError: 當座標偏移計算失敗時
        """
        try:
            point_obj = ensure_point(point)
            new_x = point_obj.x + offset_x
            new_y = point_obj.y + offset_y
            
            return self.tikz_coordinate((new_x, new_y))
            
        except Exception as e:
            raise CoordinateTransformError(
                f"座標偏移計算失敗: {point} + ({offset_x}, {offset_y})",
                original_error=e,
                context={
                    'point': point,
                    'offset_x': offset_x,
                    'offset_y': offset_y
                }
            )
    
    def polar_to_cartesian(self, center: Union[Point, Tuple[float, float]], 
                          radius: float, angle_degrees: float) -> str:
        """將極座標轉換為直角座標字符串
        
        Args:
            center: 極座標原點
            radius: 半徑
            angle_degrees: 角度（度數）
            
        Returns:
            直角座標的 TikZ 字符串
            
        Raises:
            CoordinateTransformError: 當極座標轉換失敗時
        """
        try:
            center_point = ensure_point(center)
            
            if radius < 0:
                raise ValueError(f"半徑不能為負數: {radius}")
            
            # 轉換為弧度
            angle_rad = math.radians(angle_degrees)
            
            # 計算直角座標
            x = center_point.x + radius * math.cos(angle_rad)
            y = center_point.y + radius * math.sin(angle_rad)
            
            return self.tikz_coordinate((x, y))
            
        except Exception as e:
            raise CoordinateTransformError(
                f"極座標轉換失敗: 中心={center}, 半徑={radius}, 角度={angle_degrees}°",
                original_error=e,
                context={
                    'center': center,
                    'radius': radius,
                    'angle_degrees': angle_degrees
                }
            )


# 便利函數 - 與原始 geometry_utils.py 相容

def get_arc_render_params(
    vertex: Union[Point, Tuple[float, float]],
    p_on_arm1: Union[Point, Tuple[float, float]],
    p_on_arm2: Union[Point, Tuple[float, float]],
    radius_config: Any = "auto",
    is_right_angle_symbol: bool = False,
    default_ratio: float = 0.15,
    min_auto_radius: float = 0.1,
    max_auto_radius: float = 1.0
) -> Dict[str, Any]:
    """
    計算繪製角弧或直角符號所需的參數。
    
    這是對原始 geometry_utils.get_arc_render_params 的相容性包裝，
    內部使用新的 ArcRenderer 實現。
    
    Args:
        vertex: 角的頂點
        p_on_arm1: 角的第一條臂上的點
        p_on_arm2: 角的第二條臂上的點
        radius_config: 角弧半徑配置
        is_right_angle_symbol: 是否為直角符號生成參數
        default_ratio: "auto"模式下，半徑為較短臂長的比例
        min_auto_radius: "auto"模式下的最小半徑
        max_auto_radius: "auto"模式下的最大半徑
        
    Returns:
        與原始函數相容的參數字典
        
    Raises:
        CoordinateTransformError: 當參數計算失敗時
    """
    try:
        from .arc_renderer import ArcRenderer
        from .types import RenderingContext
        
        # 創建渲染器
        context = RenderingContext(precision=7, unit="cm")
        renderer = ArcRenderer(context)
        
        # 準備半徑配置
        if isinstance(radius_config, str) and radius_config == "auto":
            radius_cfg = {
                "type": "auto",
                "ratio": default_ratio,
                "min_radius": min_auto_radius,
                "max_radius": max_auto_radius
            }
        else:
            radius_cfg = radius_config
        
        # 使用新的渲染器
        if is_right_angle_symbol:
            arc_params = renderer.render_right_angle(vertex, p_on_arm1, p_on_arm2, radius_cfg)
            
            # 轉換為原始格式
            return {
                'type': 'right_angle_symbol',
                'vertex': vertex,
                'p_on_arm1_for_symbol': arc_params.additional_data.get('p_sym_arm1'),
                'p_on_arm2_for_symbol': arc_params.additional_data.get('p_sym_arm2'),
                'size': arc_params.radius
            }
        else:
            arc_params = renderer.render_angle_arc(vertex, p_on_arm1, p_on_arm2, radius_cfg)
            
            # 轉換為原始格式
            return {
                'type': 'arc',
                'center': (arc_params.center.x, arc_params.center.y),
                'radius': arc_params.radius,
                'start_angle_rad': arc_params.start_angle,
                'end_angle_rad': arc_params.end_angle
            }
            
    except Exception as e:
        raise CoordinateTransformError(
            f"弧線參數計算失敗",
            original_error=e,
            context={
                'vertex': vertex,
                'p_on_arm1': p_on_arm1,
                'p_on_arm2': p_on_arm2,
                'radius_config': radius_config,
                'is_right_angle_symbol': is_right_angle_symbol
            }
        )


# 獨立的工具函數

def tikz_coordinate(point: Union[Point, Tuple[float, float]], precision: int = 3) -> str:
    """將點轉換為 TikZ 座標字符串（獨立函數版本）
    
    Args:
        point: 二維點座標
        precision: 數值精度
        
    Returns:
        TikZ 格式的座標字符串
    """
    transformer = CoordinateTransformer(precision=precision)
    return transformer.tikz_coordinate(point, precision)


def tikz_angle_degrees(radians: float) -> float:
    """將弧度轉換為度數（獨立函數版本）
    
    Args:
        radians: 角度（弧度）
        
    Returns:
        角度（度數）
    """
    transformer = CoordinateTransformer()
    return transformer.tikz_angle_degrees(radians)


def tikz_distance(value: float, unit: str = "cm", precision: int = 3) -> str:
    """將數值轉換為 TikZ 距離字符串（獨立函數版本）
    
    Args:
        value: 距離數值
        unit: 距離單位
        precision: 數值精度
        
    Returns:
        TikZ 格式的距離字符串
    """
    transformer = CoordinateTransformer(precision=precision, unit=unit)
    return transformer.tikz_distance(value, unit)


def tikz_options_format(options: Dict[str, Any], precision: int = 3, unit: str = "cm") -> str:
    """將選項字典格式化為 TikZ 選項字符串（獨立函數版本）
    
    Args:
        options: 選項字典
        precision: 數值精度
        unit: 距離單位
        
    Returns:
        TikZ 格式的選項字符串
    """
    transformer = CoordinateTransformer(precision=precision, unit=unit)
    return transformer.tikz_options_format(options)


# 便利函數用於批次轉換

def batch_coordinate_transform(points: List[Union[Point, Tuple[float, float]]], 
                              precision: int = 3) -> List[str]:
    """批次轉換座標點
    
    Args:
        points: 點座標列表
        precision: 數值精度
        
    Returns:
        TikZ 座標字符串列表
        
    Raises:
        CoordinateTransformError: 當批次轉換失敗時
    """
    try:
        transformer = CoordinateTransformer(precision=precision)
        return [transformer.tikz_coordinate(point) for point in points]
        
    except Exception as e:
        raise CoordinateTransformError(
            f"批次座標轉換失敗",
            original_error=e,
            context={'points_count': len(points), 'precision': precision}
        )


def batch_angle_transform(angles_rad: List[float]) -> List[float]:
    """批次轉換角度
    
    Args:
        angles_rad: 弧度角度列表
        
    Returns:
        度數角度列表
        
    Raises:
        CoordinateTransformError: 當批次轉換失敗時
    """
    try:
        transformer = CoordinateTransformer()
        return [transformer.tikz_angle_degrees(angle) for angle in angles_rad]
        
    except Exception as e:
        raise CoordinateTransformError(
            f"批次角度轉換失敗",
            original_error=e,
            context={'angles_count': len(angles_rad)}
        )


# 高級轉換功能

class AdvancedCoordinateTransformer(CoordinateTransformer):
    """進階座標轉換器
    
    提供更複雜的座標轉換功能，如座標系變換、投影等。
    """
    
    def __init__(self, precision: int = 3, unit: str = "cm"):
        super().__init__(precision, unit)
        self.transform_matrix = None
        logger.debug("初始化進階座標轉換器")
    
    def set_transform_matrix(self, matrix: List[List[float]]):
        """設置座標變換矩陣
        
        Args:
            matrix: 2x2 變換矩陣 [[a, b], [c, d]]
        """
        if not (isinstance(matrix, list) and len(matrix) == 2 and
                all(isinstance(row, list) and len(row) == 2 for row in matrix)):
            raise CoordinateTransformError(
                "變換矩陣必須為 2x2 列表格式",
                context={'matrix': matrix}
            )
        
        self.transform_matrix = matrix
        logger.debug(f"設置變換矩陣: {matrix}")
    
    def apply_transform(self, point: Union[Point, Tuple[float, float]]) -> str:
        """應用座標變換並返回 TikZ 座標
        
        Args:
            point: 原始點座標
            
        Returns:
            變換後的 TikZ 座標字符串
            
        Raises:
            CoordinateTransformError: 當變換失敗時
        """
        try:
            if self.transform_matrix is None:
                raise ValueError("未設置變換矩陣")
            
            point_obj = ensure_point(point)
            x, y = point_obj.x, point_obj.y
            
            # 應用變換矩陣
            new_x = self.transform_matrix[0][0] * x + self.transform_matrix[0][1] * y
            new_y = self.transform_matrix[1][0] * x + self.transform_matrix[1][1] * y
            
            result = self.tikz_coordinate((new_x, new_y))
            logger.debug(f"座標變換: {point} -> {result}")
            
            return result
            
        except Exception as e:
            raise CoordinateTransformError(
                f"座標變換失敗: {point}",
                original_error=e,
                context={
                    'point': point,
                    'transform_matrix': self.transform_matrix
                }
            )


# 向後相容的模組級函數

def ensure_tikz_coordinate(coord: Any) -> str:
    """確保輸入為有效的 TikZ 座標字符串
    
    Args:
        coord: 座標輸入（可能是 Point, tuple, 或已經是字符串）
        
    Returns:
        有效的 TikZ 座標字符串
    """
    if isinstance(coord, str):
        # 假設已經是 TikZ 格式
        return coord
    else:
        return tikz_coordinate(coord)


def ensure_tikz_angle(angle: Any) -> float:
    """確保輸入為有效的 TikZ 角度（度數）
    
    Args:
        angle: 角度輸入（可能是弧度或度數）
        
    Returns:
        角度（度數）
    """
    if isinstance(angle, str):
        try:
            return float(angle.rstrip('°'))
        except ValueError:
            raise CoordinateTransformError(f"無法解析角度字符串: {angle}")
    elif isinstance(angle, (int, float)):
        # 假設大於 2π 的是度數，否則是弧度
        if abs(angle) > 2 * math.pi:
            return float(angle)  # 已經是度數
        else:
            return tikz_angle_degrees(angle)  # 是弧度，需要轉換
    else:
        raise CoordinateTransformError(f"不支持的角度類型: {type(angle)}")


# 模組資訊
__version__ = "1.0.0"
__author__ = "Math Exercise Generator Team"

logger.debug(f"TikZ 座標轉換器模組載入完成: {__version__}")