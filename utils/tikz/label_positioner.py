"""
TikZ 標籤定位器

從原始 geometry_utils.py 重構而來的標籤定位功能，提供智能的標籤放置算法。

主要功能：
- 頂點標籤定位：自動計算最佳位置避免重疊
- 邊標籤定位：沿邊放置並確保可讀性
- 角度值標籤定位：在角弧外側合適位置
- 衝突避免：智能避免與其他元素重疊

使用方式：
    from utils.tikz.label_positioner import LabelPositioner
    from utils.tikz.types import LabelConfig
    
    positioner = LabelPositioner()
    
    # 頂點標籤定位
    vertex_params = positioner.position_vertex_label(
        vertex_coord=(0, 0),
        adjacent_vertices=[(1, 0), (0, 1)],
        triangle_vertices=[(0, 0), (1, 0), (0, 1)]
    )
    
    # 邊標籤定位
    side_params = positioner.position_side_label(
        p_start=(0, 0), 
        p_end=(1, 0),
        triangle_vertices=[(0, 0), (1, 0), (0, 1)]
    )
"""

import math
from typing import Union, Tuple, List, Dict, Any, Optional
from ..geometry.types import Point, ensure_point
from ..geometry.basic_ops import distance, midpoint, normalize_angle
from .types import (
    LabelConfig, LabelParameters, TikZPosition, RenderingContext,
    format_tikz_coordinate, normalize_tikz_position
)
from .exceptions import LabelPlacementError, TikZConfigError
from ..core.logging import get_logger

# 模組專用日誌器
logger = get_logger(__name__)


class LabelPositioner:
    """TikZ 標籤定位器
    
    負責計算各種類型標籤的最佳放置位置，包括頂點標籤、邊標籤和角度值標籤。
    """
    
    def __init__(self, context: Optional[RenderingContext] = None):
        """初始化標籤定位器
        
        Args:
            context: 渲染上下文，提供全域配置
        """
        self.context = context or RenderingContext()
        logger.debug("初始化標籤定位器")
    
    def position_vertex_label(self,
                            vertex_coord: Union[Point, Tuple[float, float]],
                            adjacent_vertices: List[Union[Point, Tuple[float, float]]],
                            triangle_vertices: Optional[List[Union[Point, Tuple[float, float]]]] = None,
                            config: Optional[LabelConfig] = None,
                            special_points: Optional[Dict[str, Point]] = None) -> LabelParameters:
        """計算頂點標籤的最佳放置位置
        
        使用角平分線算法確定標籤放置的方向，避免與三角形內部重疊。
        
        Args:
            vertex_coord: 頂點座標
            adjacent_vertices: 相鄰頂點列表（通常是2個）
            triangle_vertices: 完整三角形頂點列表（可選，用於更精確的計算）
            config: 標籤配置
            special_points: 特殊點座標字典（如內心、外心等）
            
        Returns:
            LabelParameters 物件，包含定位資訊
            
        Raises:
            LabelPlacementError: 當無法計算合適位置時
        """
        vertex_point = ensure_point(vertex_coord)
        adj_points = [ensure_point(p) for p in adjacent_vertices]
        
        if len(adj_points) < 2:
            raise LabelPlacementError(
                "vertex", 
                "頂點標籤定位需要至少2個相鄰頂點",
                vertex=vertex_point,
                adjacent_count=len(adj_points)
            )
        
        config = config or self.context.default_label_config
        offset = config.offset
        
        logger.debug(f"計算頂點標籤位置: {vertex_point}, 相鄰點: {adj_points}")
        
        try:
            # 計算從頂點指向相鄰頂點的向量
            vectors = []
            for adj_point in adj_points[:2]:  # 只使用前兩個相鄰點
                dist = distance(vertex_point, adj_point)
                if dist < 1e-9:
                    logger.warning(f"相鄰頂點 {adj_point} 與當前頂點 {vertex_point} 距離過近")
                    continue
                
                # 計算單位向量
                vec_x = (adj_point.x - vertex_point.x) / dist
                vec_y = (adj_point.y - vertex_point.y) / dist
                vectors.append((vec_x, vec_y))
            
            if len(vectors) < 2:
                # 備用方案：放置在右上方
                label_pos = Point(vertex_point.x + offset, vertex_point.y + offset)
                position = "above right"
                anchor = "south west"
            else:
                # 使用角平分線的反方向（指向外部）
                vec1, vec2 = vectors[0], vectors[1]
                
                # 計算角平分線向量（內部方向）
                bisector_x = vec1[0] + vec2[0]
                bisector_y = vec1[1] + vec2[1]
                bisector_length = math.sqrt(bisector_x**2 + bisector_y**2)
                
                if bisector_length < 1e-9:
                    # 兩向量方向相反（180度角），使用垂直方向
                    placement_x = -vec1[1]  # 垂直於第一個向量
                    placement_y = vec1[0]
                    
                    # 確保向上偏移
                    if placement_y < 0:
                        placement_x *= -1
                        placement_y *= -1
                else:
                    # 使用角平分線的反方向（外部方向）
                    placement_x = -bisector_x / bisector_length
                    placement_y = -bisector_y / bisector_length
                
                # 計算標籤位置
                label_pos = Point(
                    vertex_point.x + placement_x * offset,
                    vertex_point.y + placement_y * offset
                )
                
                # 確定 TikZ 位置關鍵字和錨點
                position, anchor = self._determine_tikz_position_and_anchor(
                    placement_x, placement_y
                )
            
            # 生成 TikZ 代碼
            tikz_code = self._generate_label_tikz_code(
                label_pos, position, anchor, config
            )
            
            label_params = LabelParameters(
                position=label_pos,
                tikz_position=position,
                tikz_anchor=anchor,
                offset_distance=offset,
                rotation_angle=0.0,
                tikz_code=tikz_code
            )
            
            logger.debug(f"頂點標籤定位完成: 位置={label_pos}, TikZ位置={position}")
            return label_params
            
        except Exception as e:
            if isinstance(e, LabelPlacementError):
                raise
            else:
                raise LabelPlacementError(
                    "vertex",
                    f"頂點標籤定位計算失敗: {str(e)}",
                    vertex=vertex_point,
                    adjacent_vertices=adj_points
                ) from e
    
    def position_side_label(self,
                          p_start: Union[Point, Tuple[float, float]],
                          p_end: Union[Point, Tuple[float, float]],
                          triangle_vertices: List[Union[Point, Tuple[float, float]]],
                          config: Optional[LabelConfig] = None) -> LabelParameters:
        """計算邊標籤的最佳放置位置
        
        在邊的中點外側放置標籤，並確保文字方向可讀。
        
        Args:
            p_start: 邊的起點
            p_end: 邊的終點
            triangle_vertices: 三角形所有頂點（用於確定內外側）
            config: 標籤配置
            
        Returns:
            LabelParameters 物件，包含定位和旋轉資訊
            
        Raises:
            LabelPlacementError: 當無法計算合適位置時
        """
        start_point = ensure_point(p_start)
        end_point = ensure_point(p_end)
        tri_vertices = [ensure_point(p) for p in triangle_vertices]
        
        config = config or self.context.default_label_config
        offset = config.offset
        
        logger.debug(f"計算邊標籤位置: {start_point} -> {end_point}")
        
        try:
            # 計算邊的中點
            mid_point = midpoint(start_point, end_point)
            
            # 計算邊向量
            edge_length = distance(start_point, end_point)
            if edge_length < 1e-9:
                raise LabelPlacementError(
                    "side",
                    "邊長度為零，無法計算標籤位置",
                    p_start=start_point,
                    p_end=end_point
                )
            
            side_dx = end_point.x - start_point.x
            side_dy = end_point.y - start_point.y
            
            # 計算法向量（垂直於邊）
            normal_dx = -side_dy
            normal_dy = side_dx
            
            # 歸一化法向量
            unit_normal_dx = normal_dx / edge_length
            unit_normal_dy = normal_dy / edge_length
            
            # 確定法線方向（指向三角形外部）
            p_other = self._find_third_vertex(start_point, end_point, tri_vertices)
            
            if p_other:
                # 計算中點到第三個頂點的向量
                vec_to_other_x = p_other.x - mid_point.x
                vec_to_other_y = p_other.y - mid_point.y
                
                # 檢查法向量是否指向第三個頂點（內部）
                dot_product = unit_normal_dx * vec_to_other_x + unit_normal_dy * vec_to_other_y
                if dot_product > 0:  # 指向內部，需要反轉
                    unit_normal_dx *= -1
                    unit_normal_dy *= -1
            
            # 計算標籤位置
            label_pos = Point(
                mid_point.x + unit_normal_dx * offset,
                mid_point.y + unit_normal_dy * offset
            )
            
            # 計算標籤旋轉角度（平行於邊）
            angle_rad = math.atan2(side_dy, side_dx)
            rotation_deg = math.degrees(angle_rad)
            
            # 調整旋轉角度確保文字可讀性
            if rotation_deg > 90:
                rotation_deg -= 180
            elif rotation_deg < -90:
                rotation_deg += 180
            
            # TikZ 位置設置
            position = "center"  # 使用絕對座標
            anchor = "center"
            
            # 生成 TikZ 代碼
            tikz_code = self._generate_label_tikz_code(
                label_pos, position, anchor, config, rotation_deg
            )
            
            label_params = LabelParameters(
                position=label_pos,
                tikz_position=position,
                tikz_anchor=anchor,
                offset_distance=offset,
                rotation_angle=rotation_deg,
                tikz_code=tikz_code
            )
            
            logger.debug(f"邊標籤定位完成: 位置={label_pos}, 旋轉={rotation_deg:.1f}°")
            return label_params
            
        except Exception as e:
            if isinstance(e, LabelPlacementError):
                raise
            else:
                raise LabelPlacementError(
                    "side",
                    f"邊標籤定位計算失敗: {str(e)}",
                    p_start=start_point,
                    p_end=end_point
                ) from e
    
    def position_angle_label(self,
                           vertex: Union[Point, Tuple[float, float]],
                           p_on_arm1: Union[Point, Tuple[float, float]],
                           p_on_arm2: Union[Point, Tuple[float, float]],
                           arc_radius: Optional[float] = None,
                           config: Optional[LabelConfig] = None) -> LabelParameters:
        """計算角度值標籤的最佳放置位置
        
        在角弧外側沿角平分線方向放置標籤。
        
        Args:
            vertex: 角的頂點
            p_on_arm1: 第一條臂上的點
            p_on_arm2: 第二條臂上的點
            arc_radius: 角弧半徑（如果已知）
            config: 標籤配置
            
        Returns:
            LabelParameters 物件，包含定位資訊
            
        Raises:
            LabelPlacementError: 當無法計算合適位置時
        """
        vertex_point = ensure_point(vertex)
        arm1_point = ensure_point(p_on_arm1)
        arm2_point = ensure_point(p_on_arm2)
        
        config = config or self.context.default_label_config
        offset = config.offset
        
        logger.debug(f"計算角度標籤位置: 頂點={vertex_point}, 臂1={arm1_point}, 臂2={arm2_point}")
        
        try:
            # 計算兩條臂的向量
            vec1_x = arm1_point.x - vertex_point.x
            vec1_y = arm1_point.y - vertex_point.y
            vec2_x = arm2_point.x - vertex_point.x
            vec2_y = arm2_point.y - vertex_point.y
            
            len_vec1 = math.sqrt(vec1_x**2 + vec1_y**2)
            len_vec2 = math.sqrt(vec2_x**2 + vec2_y**2)
            
            if len_vec1 < 1e-9 or len_vec2 < 1e-9:
                # 備用位置
                label_pos = Point(vertex_point.x + offset, vertex_point.y + offset)
                position = "above right"
                anchor = "south west"
                label_distance = offset
            else:
                # 計算單位向量
                unit_vec1_x = vec1_x / len_vec1
                unit_vec1_y = vec1_y / len_vec1
                unit_vec2_x = vec2_x / len_vec2
                unit_vec2_y = vec2_y / len_vec2
                
                # 計算角平分線向量
                bisector_x = unit_vec1_x + unit_vec2_x
                bisector_y = unit_vec1_y + unit_vec2_y
                bisector_length = math.sqrt(bisector_x**2 + bisector_y**2)
                
                if bisector_length < 1e-9:  # 180度角
                    # 使用垂直於其中一條臂的方向
                    placement_x = -unit_vec1_y
                    placement_y = unit_vec1_x
                    
                    # 確保向上偏移
                    if placement_y < 0:
                        placement_x *= -1
                        placement_y *= -1
                    
                    label_distance = offset * 1.5  # 180度角標籤稍遠一些
                else:
                    # 使用角平分線方向
                    unit_bisector_x = bisector_x / bisector_length
                    unit_bisector_y = bisector_y / bisector_length
                    
                    # 標籤距離：角弧半徑 + 偏移
                    if arc_radius is None:
                        # 估算角弧半徑（使用較短臂長的15%）
                        arc_radius = min(len_vec1, len_vec2) * 0.15
                        arc_radius = max(0.05, min(arc_radius, 1.0))  # 限制範圍
                    
                    label_distance = arc_radius + offset
                    placement_x = unit_bisector_x
                    placement_y = unit_bisector_y
                
                # 計算標籤位置
                label_pos = Point(
                    vertex_point.x + placement_x * label_distance,
                    vertex_point.y + placement_y * label_distance
                )
                
                position = "center"  # 使用絕對座標
                anchor = "center"
            
            # 生成 TikZ 代碼
            tikz_code = self._generate_label_tikz_code(
                label_pos, position, anchor, config
            )
            
            label_params = LabelParameters(
                position=label_pos,
                tikz_position=position,
                tikz_anchor=anchor,
                offset_distance=label_distance,
                rotation_angle=0.0,  # 角度值標籤通常水平
                tikz_code=tikz_code
            )
            
            logger.debug(f"角度標籤定位完成: 位置={label_pos}, 距離={label_distance:.3f}")
            return label_params
            
        except Exception as e:
            if isinstance(e, LabelPlacementError):
                raise
            else:
                raise LabelPlacementError(
                    "angle_value",
                    f"角度標籤定位計算失敗: {str(e)}",
                    vertex=vertex_point,
                    p_on_arm1=arm1_point,
                    p_on_arm2=arm2_point
                ) from e
    
    def _determine_tikz_position_and_anchor(self, 
                                          placement_x: float, 
                                          placement_y: float) -> Tuple[str, str]:
        """根據放置方向確定 TikZ 位置關鍵字和錨點
        
        Args:
            placement_x: X 方向的單位向量分量
            placement_y: Y 方向的單位向量分量
            
        Returns:
            (TikZ位置關鍵字, 錨點) 元組
        """
        # 根據方向向量確定位置
        if placement_y > 0.5:  # 主要向上
            if placement_x > 0.5:
                return "above right", "south west"
            elif placement_x < -0.5:
                return "above left", "south east"
            else:
                return "above", "south"
        elif placement_y < -0.5:  # 主要向下
            if placement_x > 0.5:
                return "below right", "north west"
            elif placement_x < -0.5:
                return "below left", "north east"
            else:
                return "below", "north"
        else:  # 主要水平
            if placement_x > 0:
                return "right", "west"
            else:
                return "left", "east"
    
    def _find_third_vertex(self,
                          p1: Point,
                          p2: Point,
                          all_vertices: List[Point]) -> Optional[Point]:
        """在頂點列表中找到不是 p1 和 p2 的第三個頂點
        
        Args:
            p1: 第一個頂點
            p2: 第二個頂點
            all_vertices: 所有頂點列表
            
        Returns:
            第三個頂點，如果沒找到則返回 None
        """
        for vertex in all_vertices:
            # 使用距離判斷而不是直接比較，避免浮點誤差
            if (distance(vertex, p1) > 1e-9 and 
                distance(vertex, p2) > 1e-9):
                return vertex
        return None
    
    def _generate_label_tikz_code(self,
                                position: Point,
                                tikz_position: str,
                                anchor: str,
                                config: LabelConfig,
                                rotation: float = 0.0) -> str:
        """生成標籤的 TikZ 代碼
        
        Args:
            position: 標籤位置
            tikz_position: TikZ 位置關鍵字
            anchor: 錨點
            config: 標籤配置
            rotation: 旋轉角度（度）
            
        Returns:
            TikZ 代碼字串
        """
        pos_coord = format_tikz_coordinate(position, self.context.precision)
        
        # 構建選項
        options = []
        
        if anchor != "center":
            options.append(f"anchor={anchor}")
        
        if abs(rotation) > 1e-3:
            options.append(f"rotate={rotation:.1f}")
        
        # 添加樣式選項
        for key, value in config.style_options.items():
            options.append(f"{key}={value}")
        
        # 構建 TikZ 代碼
        if options:
            option_str = "[" + ",".join(options) + "]"
        else:
            option_str = ""
        
        tikz_code = f"\\node{option_str} at {pos_coord} {{LABEL_TEXT}};"
        
        return tikz_code
    
    def set_context(self, context: RenderingContext) -> None:
        """設定渲染上下文
        
        Args:
            context: 新的渲染上下文
        """
        self.context = context
        logger.debug(f"更新標籤定位器渲染上下文，精度: {context.precision}")


# 便利函數

def position_vertex_label_auto(vertex: Union[Point, Tuple[float, float]],
                              adjacent_vertices: List[Union[Point, Tuple[float, float]]],
                              offset: float = 0.15) -> LabelParameters:
    """自動定位頂點標籤的快速方法
    
    Args:
        vertex: 頂點座標
        adjacent_vertices: 相鄰頂點列表
        offset: 偏移距離
        
    Returns:
        標籤參數
    """
    config = LabelConfig(offset=offset)
    positioner = LabelPositioner()
    return positioner.position_vertex_label(vertex, adjacent_vertices, config=config)


def position_side_label_auto(p_start: Union[Point, Tuple[float, float]],
                            p_end: Union[Point, Tuple[float, float]],
                            triangle_vertices: List[Union[Point, Tuple[float, float]]],
                            offset: float = 0.15) -> LabelParameters:
    """自動定位邊標籤的快速方法
    
    Args:
        p_start: 邊的起點
        p_end: 邊的終點
        triangle_vertices: 三角形頂點列表
        offset: 偏移距離
        
    Returns:
        標籤參數
    """
    config = LabelConfig(offset=offset)
    positioner = LabelPositioner()
    return positioner.position_side_label(p_start, p_end, triangle_vertices, config=config)


def position_angle_label_auto(vertex: Union[Point, Tuple[float, float]],
                             p_on_arm1: Union[Point, Tuple[float, float]],
                             p_on_arm2: Union[Point, Tuple[float, float]],
                             offset: float = 0.15) -> LabelParameters:
    """自動定位角度標籤的快速方法
    
    Args:
        vertex: 角的頂點
        p_on_arm1: 第一條臂上的點
        p_on_arm2: 第二條臂上的點
        offset: 偏移距離
        
    Returns:
        標籤參數
    """
    config = LabelConfig(offset=offset)
    positioner = LabelPositioner()
    return positioner.position_angle_label(vertex, p_on_arm1, p_on_arm2, config=config)