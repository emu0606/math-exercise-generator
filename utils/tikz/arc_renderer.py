"""
TikZ 弧線渲染器

從原始 geometry_utils.py 重構而來的弧線渲染功能，提供角弧和直角符號的渲染參數計算。

主要功能：
- 角弧渲染參數計算
- 直角符號渲染參數計算  
- 自動半徑計算
- TikZ 代碼生成

使用方式：
    from utils.tikz.arc_renderer import ArcRenderer
    
    renderer = ArcRenderer()
    arc_params = renderer.render_angle_arc(vertex, p1, p2, radius_config="auto")
    print(arc_params.tikz_code)
"""

import math
from typing import Union, Dict, Any, Optional, Tuple
from ..geometry.types import Point, ensure_point
from ..geometry.basic_ops import distance, angle_at_vertex, normalize_angle
from .types import ArcConfig, ArcParameters, ArcType, RenderingContext, format_tikz_coordinate, format_tikz_angle
from .exceptions import ArcRenderingError, TikZConfigError
from ..core.logging import get_logger

# 模組專用日誌器
logger = get_logger(__name__)


class ArcRenderer:
    """TikZ 弧線渲染器
    
    負責計算和生成各種弧線的渲染參數，包括角弧和直角符號。
    """
    
    def __init__(self, context: Optional[RenderingContext] = None):
        """初始化弧線渲染器
        
        Args:
            context: 渲染上下文，提供全域配置
        """
        self.context = context or RenderingContext()
        logger.debug(f"初始化弧線渲染器，精度: {self.context.precision}")
    
    def render_angle_arc(self, 
                        vertex: Union[Point, Tuple[float, float]], 
                        point1: Union[Point, Tuple[float, float]], 
                        point2: Union[Point, Tuple[float, float]], 
                        radius_config: Union[float, str, Dict[str, Any]] = "auto") -> ArcParameters:
        """渲染角弧
        
        計算在指定頂點處繪製角弧所需的所有參數。
        
        Args:
            vertex: 角的頂點
            point1: 角的第一條邊上的點
            point2: 角的第二條邊上的點
            radius_config: 半徑配置
                - float: 固定半徑值
                - "auto": 自動計算半徑
                - dict: 詳細配置 {"radius": float, "ratio": float}
                
        Returns:
            ArcParameters 物件，包含所有渲染參數
            
        Raises:
            ArcRenderingError: 當渲染參數計算失敗時
        """
        # 輸入驗證和轉換
        vertex_point = ensure_point(vertex)
        p1 = ensure_point(point1)
        p2 = ensure_point(point2)
        
        logger.debug(f"渲染角弧: 頂點={vertex_point}, 點1={p1}, 點2={p2}")
        
        try:
            # 解析半徑配置
            radius = self._parse_radius_config(radius_config, vertex_point, p1, p2)
            
            # 計算角度
            angles = self._calculate_arc_angles(vertex_point, p1, p2)
            start_angle, end_angle = angles
            
            # 生成 TikZ 代碼
            tikz_code = self._generate_arc_tikz_code(
                vertex_point, radius, start_angle, end_angle, 'angle_arc'
            )
            
            # 創建弧線參數
            arc_params = ArcParameters(
                center=vertex_point,
                radius=radius,
                start_angle=start_angle,
                end_angle=end_angle,
                arc_type='angle_arc',
                tikz_code=tikz_code
            )
            
            logger.debug(f"角弧渲染完成: 半徑={radius:.3f}, 角度跨度={arc_params.angle_span_degrees:.1f}°")
            return arc_params
            
        except Exception as e:
            if isinstance(e, ArcRenderingError):
                raise
            else:
                raise ArcRenderingError(
                    "angle_arc",
                    f"角弧渲染失敗: {str(e)}",
                    vertex=vertex_point,
                    point1=p1,
                    point2=p2,
                    radius_config=radius_config
                ) from e
    
    def render_right_angle(self, 
                          vertex: Union[Point, Tuple[float, float]], 
                          point1: Union[Point, Tuple[float, float]], 
                          point2: Union[Point, Tuple[float, float]], 
                          size: float = 0.2) -> ArcParameters:
        """渲染直角符號
        
        計算在指定頂點處繪製直角符號所需的所有參數。
        
        Args:
            vertex: 直角頂點
            point1: 第一條邊上的點
            point2: 第二條邊上的點
            size: 直角符號邊長
            
        Returns:
            ArcParameters 物件，包含所有渲染參數
            
        Raises:
            ArcRenderingError: 當渲染參數計算失敗時
        """
        # 輸入驗證和轉換
        vertex_point = ensure_point(vertex)
        p1 = ensure_point(point1)
        p2 = ensure_point(point2)
        
        if size <= 0:
            raise TikZConfigError("right_angle_size", size, "直角符號大小必須為正數")
        
        logger.debug(f"渲染直角符號: 頂點={vertex_point}, 大小={size}")
        
        try:
            # 計算直角符號的四個頂點
            corners = self._calculate_right_angle_corners(vertex_point, p1, p2, size)
            
            # 生成 TikZ 代碼
            tikz_code = self._generate_right_angle_tikz_code(corners)
            
            # 創建弧線參數（直角符號特殊情況）
            arc_params = ArcParameters(
                center=vertex_point,
                radius=size,
                start_angle=0.0,  # 直角符號不使用角度
                end_angle=math.pi/2,
                arc_type='right_angle',
                tikz_code=tikz_code
            )
            
            logger.debug(f"直角符號渲染完成: 大小={size}")
            return arc_params
            
        except Exception as e:
            if isinstance(e, ArcRenderingError):
                raise
            else:
                raise ArcRenderingError(
                    "right_angle",
                    f"直角符號渲染失敗: {str(e)}",
                    vertex=vertex_point,
                    point1=p1,
                    point2=p2,
                    size=size
                ) from e
    
    def render_custom_arc(self, 
                         center: Union[Point, Tuple[float, float]], 
                         radius: float, 
                         start_angle: float, 
                         end_angle: float, 
                         arc_config: Optional[ArcConfig] = None) -> ArcParameters:
        """渲染自定義弧線
        
        根據指定的中心、半徑和角度範圍渲染弧線。
        
        Args:
            center: 弧線中心
            radius: 半徑
            start_angle: 起始角度（弧度制）
            end_angle: 結束角度（弧度制）
            arc_config: 弧線配置
            
        Returns:
            ArcParameters 物件
            
        Raises:
            ArcRenderingError: 當渲染參數無效時
        """
        center_point = ensure_point(center)
        
        if radius <= 0:
            raise TikZConfigError("arc_radius", radius, "弧線半徑必須為正數")
        
        # 標準化角度
        start_angle = normalize_angle(start_angle)
        end_angle = normalize_angle(end_angle)
        
        logger.debug(f"渲染自定義弧線: 中心={center_point}, 半徑={radius}")
        
        try:
            # 生成 TikZ 代碼
            tikz_code = self._generate_arc_tikz_code(
                center_point, radius, start_angle, end_angle, 'custom'
            )
            
            # 創建弧線參數
            arc_params = ArcParameters(
                center=center_point,
                radius=radius,
                start_angle=start_angle,
                end_angle=end_angle,
                arc_type='custom',
                tikz_code=tikz_code
            )
            
            logger.debug(f"自定義弧線渲染完成: 角度跨度={arc_params.angle_span_degrees:.1f}°")
            return arc_params
            
        except Exception as e:
            raise ArcRenderingError(
                "custom_arc",
                f"自定義弧線渲染失敗: {str(e)}",
                center=center_point,
                radius=radius,
                start_angle=start_angle,
                end_angle=end_angle
            ) from e
    
    def _parse_radius_config(self, 
                           radius_config: Union[float, str, Dict[str, Any]], 
                           vertex: Point, 
                           p1: Point, 
                           p2: Point) -> float:
        """解析半徑配置
        
        Args:
            radius_config: 半徑配置
            vertex: 角頂點
            p1, p2: 角的兩個端點
            
        Returns:
            計算出的半徑值
        """
        if isinstance(radius_config, (int, float)):
            if radius_config <= 0:
                raise TikZConfigError("radius", radius_config, "半徑必須為正數")
            return float(radius_config)
        
        elif radius_config == "auto":
            # 自動計算半徑：取兩條邊較短者的 15%
            arm1_length = distance(vertex, p1)
            arm2_length = distance(vertex, p2)
            
            if arm1_length < 1e-9 or arm2_length < 1e-9:
                raise ArcRenderingError(
                    "auto_radius",
                    "無法自動計算半徑：角的臂長過短",
                    arm1_length=arm1_length,
                    arm2_length=arm2_length
                )
            
            shorter_arm = min(arm1_length, arm2_length)
            radius = shorter_arm * 0.15  # 使用 15% 比例
            
            # 確保半徑在合理範圍內
            radius = max(0.05, min(radius, 1.0))
            
            logger.debug(f"自動計算半徑: 臂長=({arm1_length:.3f}, {arm2_length:.3f}), 半徑={radius:.3f}")
            return radius
        
        elif isinstance(radius_config, dict):
            # 字典配置
            if "radius" in radius_config:
                radius = radius_config["radius"]
                if not isinstance(radius, (int, float)) or radius <= 0:
                    raise TikZConfigError("radius", radius, "半徑必須為正數")
                return float(radius)
            
            elif "ratio" in radius_config:
                # 使用比例計算
                ratio = radius_config["ratio"]
                if not isinstance(ratio, (int, float)) or ratio <= 0:
                    raise TikZConfigError("radius_ratio", ratio, "半徑比例必須為正數")
                
                arm1_length = distance(vertex, p1)
                arm2_length = distance(vertex, p2)
                shorter_arm = min(arm1_length, arm2_length)
                return shorter_arm * ratio
            
            else:
                raise TikZConfigError(
                    "radius_config", 
                    radius_config, 
                    "字典配置必須包含 'radius' 或 'ratio' 鍵"
                )
        
        else:
            raise TikZConfigError(
                "radius_config", 
                radius_config, 
                "半徑配置必須是數值、'auto' 或字典"
            )
    
    def _calculate_arc_angles(self, vertex: Point, p1: Point, p2: Point) -> Tuple[float, float]:
        """計算弧線的起始和結束角度
        
        Args:
            vertex: 角頂點
            p1, p2: 角的兩個端點
            
        Returns:
            (start_angle, end_angle) 元組
        """
        # 計算兩條邊相對於正X軸的角度
        angle1 = math.atan2(p1.y - vertex.y, p1.x - vertex.x)
        angle2 = math.atan2(p2.y - vertex.y, p2.x - vertex.x)
        
        # 標準化角度到 [0, 2π) 範圍
        angle1 = normalize_angle(angle1)
        angle2 = normalize_angle(angle2)
        
        # 確保弧線方向正確（總是畫較小的角）
        if abs(angle2 - angle1) > math.pi:
            if angle1 < angle2:
                angle1 += 2 * math.pi
            else:
                angle2 += 2 * math.pi
        
        # 確保 start_angle < end_angle
        start_angle = min(angle1, angle2)
        end_angle = max(angle1, angle2)
        
        logger.debug(f"計算弧線角度: {math.degrees(start_angle):.1f}° 到 {math.degrees(end_angle):.1f}°")
        
        return start_angle, end_angle
    
    def _calculate_right_angle_corners(self, vertex: Point, p1: Point, p2: Point, size: float) -> Tuple[Point, Point, Point, Point]:
        """計算直角符號的四個角點
        
        Args:
            vertex: 直角頂點
            p1, p2: 直角的兩條邊上的點
            size: 直角符號邊長
            
        Returns:
            四個角點的元組 (corner1, corner2, corner3, corner4)
        """
        # 計算兩條邊的單位向量
        from ..geometry.types import Vector
        
        vec1 = Vector.from_points(vertex, p1).normalize()
        vec2 = Vector.from_points(vertex, p2).normalize()
        
        # 計算直角符號的四個頂點
        corner1 = vertex.translate(vec1.x * size, vec1.y * size)
        corner2 = corner1.translate(vec2.x * size, vec2.y * size)
        corner3 = vertex.translate(vec2.x * size, vec2.y * size)
        
        return vertex, corner1, corner2, corner3
    
    def _generate_arc_tikz_code(self, 
                               center: Point, 
                               radius: float, 
                               start_angle: float, 
                               end_angle: float, 
                               arc_type: ArcType) -> str:
        """生成弧線的 TikZ 代碼
        
        Args:
            center: 弧線中心
            radius: 半徑
            start_angle: 起始角度（弧度制）
            end_angle: 結束角度（弧度制）
            arc_type: 弧線類型
            
        Returns:
            TikZ 代碼字串
        """
        center_coord = format_tikz_coordinate(center, self.context.precision)
        start_deg = format_tikz_angle(start_angle)
        end_deg = format_tikz_angle(end_angle)
        
        if arc_type in ['angle_arc', 'custom']:
            # 使用 TikZ 的 arc 命令
            tikz_code = f"\\draw {center_coord} ++({start_deg}:{radius:.{self.context.precision}f}cm) arc ({start_deg}:{end_deg}:{radius:.{self.context.precision}f}cm);"
        else:
            # 其他類型的弧線
            tikz_code = f"% Custom arc type: {arc_type}"
        
        return tikz_code
    
    def _generate_right_angle_tikz_code(self, corners: Tuple[Point, Point, Point, Point]) -> str:
        """生成直角符號的 TikZ 代碼
        
        Args:
            corners: 直角符號的四個角點
            
        Returns:
            TikZ 代碼字串
        """
        corner0, corner1, corner2, corner3 = corners
        
        # 格式化座標
        coords = [
            format_tikz_coordinate(corner, self.context.precision)
            for corner in corners
        ]
        
        # 生成直角符號的路徑
        tikz_code = f"\\draw {coords[1]} -- {coords[2]} -- {coords[3]};"
        
        return tikz_code
    
    def set_context(self, context: RenderingContext) -> None:
        """設定渲染上下文
        
        Args:
            context: 新的渲染上下文
        """
        self.context = context
        logger.debug(f"更新渲染上下文，精度: {context.precision}")
    
    def get_default_configs(self) -> Dict[str, ArcConfig]:
        """獲取預設的弧線配置
        
        Returns:
            預設配置字典
        """
        return {
            'small_arc': ArcConfig(radius=0.15, arc_type='angle_arc'),
            'medium_arc': ArcConfig(radius=0.3, arc_type='angle_arc'),
            'large_arc': ArcConfig(radius=0.5, arc_type='angle_arc'),
            'right_angle': ArcConfig(radius=0.2, arc_type='right_angle')
        }