#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 圖形參數模型
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Literal, Optional, Union, Tuple

# --- TikZ 常用錨點 ---
TikzAnchor = Literal[
    'center', 'north', 'south', 'east', 'west',
    'north east', 'north west', 'south east', 'south west',
    'mid', 'mid east', 'mid west', 'base', 'base east', 'base west'
]

# --- TikZ positioning 庫常用放置位置 ---
TikzPlacement = Literal[
    'right', 'left', 'above', 'below',
    'above left', 'above right', 'below left', 'below right'
]

class AbsolutePosition(BaseModel):
    """絕對定位模型"""
    mode: Literal['absolute'] = 'absolute'
    x: float = 0.0
    y: float = 0.0
    anchor: TikzAnchor = 'center'  # 子圖形的哪個錨點對齊到 (x, y)

class RelativePosition(BaseModel):
    """相對定位模型"""
    mode: Literal['relative'] = 'relative'
    relative_to: str  # 相對於哪個子圖形的 id
    placement: TikzPlacement = 'right'  # 放置方向
    distance: str = '1cm'  # 距離 (TikZ 單位)
    my_anchor: Optional[TikzAnchor] = None  # 當前子圖形用於對齊的錨點
    target_anchor: Optional[TikzAnchor] = None  # 相對目標用於對齊的錨點

class BaseFigureParams(BaseModel):
    """基礎圖形參數模型"""
    variant: Literal['question', 'explanation'] = 'question'

class UnitCircleParams(BaseFigureParams):
    """單位圓參數模型"""
    angle: float = Field(..., ge=0, le=360)
    show_coordinates: bool = True
    line_color: str = 'black'
    point_color: str = 'red'
    angle_color: str = 'blue'
    radius: float = 1.0

class TriangleParams(BaseFigureParams):
    """三角形參數模型"""
    points: List[List[float]] = Field(..., min_items=3, max_items=3)
    show_labels: bool = True
    label_names: List[str] = ['A', 'B', 'C']
    line_color: str = 'black'
    fill_color: Optional[str] = None
    line_style: str = 'solid'

class SubFigureParams(BaseModel):
    """子圖形參數模型"""
    id: Optional[str] = None  # 用於相對定位的引用 ID
    type: str  # 基礎圖形類型
    params: Dict[str, Any]  # 基礎圖形的參數 (需匹配其 Pydantic 模型)
    # position 可以是絕對或相對定位，預設為絕對定位在原點
    position: Union[AbsolutePosition, RelativePosition] = Field(default_factory=AbsolutePosition)

    @validator('id')
    def id_must_be_valid(cls, v):
        """驗證 ID 是否有效"""
        if v is not None and not v.isalnum() and not all(c.isalnum() or c == '_' for c in v):
            raise ValueError('ID 只能包含字母、數字和下劃線')
        return v

class CompositeParams(BaseFigureParams):
    """複合圖形參數模型"""
    sub_figures: List[SubFigureParams] = Field(..., min_items=1)
    
    @validator('sub_figures')
    def validate_sub_figures(cls, v):
        """驗證子圖形列表
        
        1. 確保 sub_figures 中 id 的唯一性（如果提供的話）
        2. 確保相對定位的 'relative_to' 引用列表中較早定義的子圖形的 id
        """
        ids = set()
        for i, sub_figure in enumerate(v):
            # 檢查 ID 唯一性
            if sub_figure.id is not None:
                if sub_figure.id in ids:
                    raise ValueError(f"重複的子圖形 ID: {sub_figure.id}")
                ids.add(sub_figure.id)
            
            # 檢查相對定位引用
            if isinstance(sub_figure.position, RelativePosition):
                relative_to = sub_figure.position.relative_to
                # 確保引用的 ID 存在且在當前子圖形之前定義
                if relative_to not in ids:
                    raise ValueError(f"子圖形 {i} 引用了未定義或後定義的 ID: {relative_to}")
        
        return v

# --- 預定義複合圖形參數模型 ---
class StandardUnitCircleParams(BaseFigureParams):
    """標準單位圓參數模型"""
    angle: float = Field(..., ge=0, le=360)
    show_coordinates: bool = True
    show_angle: bool = True
    show_point: bool = True
    show_radius: bool = True
    line_color: str = 'black'
    point_color: str = 'red'
    angle_color: str = 'blue'
    radius_color: str = 'red'
    coordinate_color: str = 'gray'
    radius: float = 1.0
    label_point: bool = True
    point_label: str = 'P'

# --- 基礎圖形參數 ---
PointTuple = Tuple[float, float] # 與 utils.geometry.types.Point 一致

class LabelParams(BaseFigureParams):
    """標籤參數模型"""
    x: float = Field(default=0.0, description="標籤節點放置的絕對 x 座標")
    y: float = Field(default=0.0, description="標籤節點放置的絕對 y 座標")
    text: str = Field(default='', description="標籤文本")
    
    position_modifiers: Optional[str] = Field(default=None, description="TikZ 定位修飾詞, 例如 'above', 'below left', 'right=0.1cm of other_node_id'")
    anchor: Optional[str] = Field(default=None, description="標籤節點自身的錨點, 例如 'north west', 'center'")
    rotate: Optional[float] = Field(default=None, description="旋轉角度 (度)")
    
    color: str = Field(default='black', description="文本顏色")
    font_size: Optional[str] = Field(default=None, description="TikZ 字體大小命令, 例如 '\\small', '\\tiny'")
    math_mode: bool = Field(default=True, description="文本是否使用數學模式 ($...$)")
    additional_node_options: Optional[str] = Field(default=None, description="其他傳遞給 TikZ node 的原始選項字符串, 例如 'draw, circle'")

    # variant: Literal['question', 'explanation'] (繼承自 BaseFigureParams)

    @validator('x', 'y', pre=True, always=True) # Removed 'rotate'
    def ensure_xy_float_if_not_none(cls, v): # Renamed for clarity
        if v is not None:
            try:
                return float(v)
            except ValueError as e_conv:
                raise ValueError("座標值 (x,y) 無法轉換為浮點數。") from e_conv
        return v

    # For 'rotate: Optional[float]', Pydantic will attempt conversion. If " ৪৫" is passed,
    # Pydantic's core validation should raise a ValidationError if it can't convert to float.
    # For 'color: str', Pydantic will attempt conversion or check type. If 123 is passed,
    # Pydantic's core validation should raise a ValidationError.

    @validator('anchor', 'position_modifiers', 'font_size', 'additional_node_options', pre=True, always=True) # Removed 'color'
    def ensure_optional_strings_are_strings(cls,v): # Renamed for clarity
        if v is not None: # These fields are Optional[str]
            if not isinstance(v, str):
                raise ValueError("錨點、位置修飾詞、字體大小和附加節點選項等值必須是字符串。")
            return v
        return v

# --- PredefinedTriangleGenerator 相關參數模型 ---

class LabelStyleConfig(BaseModel):
    """標籤樣式的可配置部分，用於覆蓋 LabelParams 的部分字段或提供給 get_label_placement_params"""
    text_override: Optional[str] = None
    position_modifiers: Optional[str] = None
    anchor: Optional[str] = None
    rotate: Optional[float] = None
    color: Optional[str] = None
    font_size: Optional[str] = None
    math_mode: Optional[bool] = None # If None, LabelGenerator's default (True) might apply
    additional_node_options: Optional[str] = None
    # Offset for get_label_placement_params, if needed to be configurable per label
    default_offset_override: Optional[float] = None

class PointStyleConfig(BaseModel):
    """點樣式的可配置部分 (用於 matplotlib 可視化或未來 TikZ 點生成器)"""
    color: Optional[str] = Field(default='black')
    marker: Optional[str] = Field(default='o') # e.g., 'o', 'x', '*', 's' (square)
    size_mpl: Optional[float] = Field(default=30)  # For matplotlib scatter s (size in points^2)
    tikz_scale: Optional[float] = Field(default=1.0) # For TikZ point scale if using \draw circle or similar

class VertexDisplayConfig(BaseModel):
    show_point: bool = True
    point_style: Optional[PointStyleConfig] = Field(default_factory=PointStyleConfig)
    show_label: bool = True
    # label_text: Optional[str] = None # If None, PredefinedTriangleGenerator uses default e.g. 'A'
    label_style: Optional[LabelStyleConfig] = Field(default_factory=LabelStyleConfig)

class SideDisplayConfig(BaseModel):
    show_label: bool = True
    # label_content_type: Literal['name', 'value', 'custom_text'] = 'name'
    # 'name' (e.g. 'a'), 'value' (length), 'custom_text' (user provided)
    label_text_type: Literal['default_name', 'length', 'custom'] = 'default_name'
    custom_label_text: Optional[str] = None # Used if label_text_type is 'custom'
    length_format: str = "{value:.2f}" # Used if label_text_type is 'length'
    label_style: Optional[LabelStyleConfig] = Field(default_factory=LabelStyleConfig)

class ArcStyleConfig(BaseModel):
    """角弧樣式的可配置部分 (傳給 ArcGenerator 的 draw_options)"""
    draw_options: Optional[str] = Field(default="thin") # Default to thin arc

class AngleDisplayConfig(BaseModel):
    show_arc: bool = True
    arc_style: Optional[ArcStyleConfig] = Field(default_factory=ArcStyleConfig)
    arc_radius_config: Optional[Any] = Field(default=None, description="特定於此角的角弧半徑配置 (如 'auto', 0.5)。若為 None, 則使用全局配置。")

    show_label: bool = True
    # label_content_type: Literal['name', 'value', 'custom_text'] = 'value'
    label_text_type: Literal['default_name', 'value', 'custom'] = 'value'
    custom_label_text: Optional[str] = None
    value_format: str = "{value:.1f}°" # For angle value in degrees
    label_style: Optional[LabelStyleConfig] = Field(default_factory=LabelStyleConfig)

class SpecialPointDisplayConfig(BaseModel):
    show_point: bool = True
    point_style: Optional[PointStyleConfig] = Field(default_factory=PointStyleConfig)
    show_label: bool = True
    # label_text: Optional[str] = None # If None, PredefinedTriangleGenerator uses default e.g. 'I'
    label_style: Optional[LabelStyleConfig] = Field(default_factory=LabelStyleConfig)

class PredefinedTriangleParams(BaseFigureParams):
    """
    預定義三角形生成器的參數模型。
    用於定義三角形的幾何形狀以及要顯示的各種標記和樣式。
    """
    # 1. 三角形定義 (對應 utils.geometry.triangle_constructions.TriangleConstructor 的參數)
    definition_mode: Literal['sss', 'sas', 'asa', 'aas', 'coordinates'] = Field(
        description="定義三角形的方式。"
    )
    
    # SSS 參數
    side_a: Optional[float] = Field(default=None, description="P2P3 長度 (用於 SSS 模式)")
    side_b: Optional[float] = Field(default=None, description="P1P3 長度 (用於 SSS 模式)")
    side_c: Optional[float] = Field(default=None, description="P1P2 長度 (用於 SSS 模式)")
    
    # Coordinates 參數
    p1: Optional[PointTuple] = Field(default=None, description="頂點 P1 座標 (用於 'coordinates' 模式)")
    p2: Optional[PointTuple] = Field(default=None, description="頂點 P2 座標 (用於 'coordinates' 模式)")
    p3: Optional[PointTuple] = Field(default=None, description="頂點 P3 座標 (用於 'coordinates' 模式)")
    
    # SAS 參數 (P1 為夾角頂點，P1P2 為 side1, P1P3 為 side2)
    sas_side1: Optional[float] = Field(default=None, description="第一邊長 (P1P2) (用於 SAS 模式)")
    sas_angle_rad: Optional[float] = Field(default=None, description="夾角 (P1處)，弧度制 (用於 SAS 模式)")
    sas_side2: Optional[float] = Field(default=None, description="第二邊長 (P1P3) (用於 SAS 模式)")
    
    # ASA 參數 (P1P2 為夾邊 side_length, 角在 P1, P2)
    asa_angle1_rad: Optional[float] = Field(default=None, description="P1 處的角，弧度制 (用於 ASA 模式)")
    asa_side_length: Optional[float] = Field(default=None, description="夾邊 P1P2 的長度 (用於 ASA 模式)")
    asa_angle2_rad: Optional[float] = Field(default=None, description="P2 處的角，弧度制 (用於 ASA 模式)")
    
    # AAS 參數 (角A at P1, 角B at P2, P1的對邊 a 即 P2P3)
    aas_angle1_rad: Optional[float] = Field(default=None, description="P1 處的角 A，弧度制 (用於 AAS 模式)")
    aas_angle2_rad: Optional[float] = Field(default=None, description="P2 處的角 B，弧度制 (用於 AAS 模式)")
    aas_side_a_opposite_p1: Optional[float] = Field(default=None, description="P1 對邊 (P2P3) 的長度 (用於 AAS 模式)")

    # 2. 元素顯示配置
    # 頂點 (P1, P2, P3 的順序由 get_vertices 按約定返回)
    vertex_p1_display_config: VertexDisplayConfig = Field(default_factory=VertexDisplayConfig)
    vertex_p2_display_config: VertexDisplayConfig = Field(default_factory=VertexDisplayConfig)
    vertex_p3_display_config: VertexDisplayConfig = Field(default_factory=VertexDisplayConfig)
    default_vertex_labels: List[str] = Field(default=['A', 'B', 'C'], description="頂點的默認標籤名 (若對應配置中 label_text 未指定)")

    # 邊 (P1P2, P2P3, P3P1)
    side_p1p2_display_config: SideDisplayConfig = Field(default_factory=SideDisplayConfig) # 通常對應 'c'
    side_p2p3_display_config: SideDisplayConfig = Field(default_factory=SideDisplayConfig) # 通常對應 'a'
    side_p3p1_display_config: SideDisplayConfig = Field(default_factory=SideDisplayConfig) # 通常對應 'b'
    default_side_names: List[str] = Field(default=['c', 'a', 'b'], description="邊的默認名稱 (P1P2, P2P3, P3P1)")

    # 角 (角於 P1, P2, P3)
    angle_at_p1_display_config: AngleDisplayConfig = Field(default_factory=AngleDisplayConfig)
    angle_at_p2_display_config: AngleDisplayConfig = Field(default_factory=AngleDisplayConfig)
    angle_at_p3_display_config: AngleDisplayConfig = Field(default_factory=AngleDisplayConfig)
    default_angle_names: List[str] = Field(default=['A', 'B', 'C'], description="角的默認名稱 (頂點P1, P2, P3處)")

    # 特殊點
    display_centroid: Optional[SpecialPointDisplayConfig] = Field(default=None)
    display_incenter: Optional[SpecialPointDisplayConfig] = Field(default=None)
    display_circumcenter: Optional[SpecialPointDisplayConfig] = Field(default=None)
    display_orthocenter: Optional[SpecialPointDisplayConfig] = Field(default=None)
    default_special_point_labels: Dict[str, str] = Field(default={
        'centroid': 'G', 'incenter': 'I',
        'circumcenter': 'O', 'orthocenter': 'H'
    })

    # 3. 全局樣式和行為控制
    global_angle_arc_radius_config: Any = Field(default="auto", description="全局角弧半徑配置 (傳給 get_arc_render_params)")
    global_label_default_offset: float = Field(default=0.15, description="全局標籤默認偏移量 (傳給 get_label_placement_params)")
    
    triangle_draw_options: Optional[str] = Field(default="thin, black", description="主三角形輪廓的 TikZ 選項 (傳給 BasicTriangleGenerator)")
    triangle_fill_color: Optional[str] = Field(default=None, description="主三角形的填充顏色 (傳給 BasicTriangleGenerator)")

    # @root_validator(pre=False, skip_on_failure=True) # Pydantic v2 uses model_validator
    # def check_definition_params(cls, values):
    #     mode = values.get('definition_mode')
    #     # Basic checks, detailed validation happens in get_vertices
    #     if mode == 'sss':
    #         if not (values.get('side_a') is not None and values.get('side_b') is not None and values.get('side_c') is not None):
    #             raise ValueError("SSS模式需要 side_a, side_b, side_c。")
    #     elif mode == 'coordinates':
    #         if not (values.get('p1') is not None and values.get('p2') is not None and values.get('p3') is not None):
    #             raise ValueError("Coordinates模式需要 p1, p2, p3。")
    #     elif mode == 'sas':
    #         if not (values.get('sas_side1') is not None and values.get('sas_angle_rad') is not None and values.get('sas_side2') is not None):
    #             raise ValueError("SAS模式需要 sas_side1, sas_angle_rad, sas_side2。")
    #     elif mode == 'asa':
    #         if not (values.get('asa_angle1_rad') is not None and values.get('asa_side_length') is not None and values.get('asa_angle2_rad') is not None):
    #             raise ValueError("ASA模式需要 asa_angle1_rad, asa_side_length, asa_angle2_rad。")
    #     elif mode == 'aas':
    #         if not (values.get('aas_angle1_rad') is not None and values.get('aas_angle2_rad') is not None and values.get('aas_side_a_opposite_p1') is not None):
    #             raise ValueError("AAS模式需要 aas_angle1_rad, aas_angle2_rad, aas_side_a_opposite_p1。")
    #     return values
    
    # Pydantic v2 model_validator
    from pydantic import model_validator

    @model_validator(mode='after')
    def check_definition_params_v2(self) -> 'PredefinedTriangleParams':
        mode = self.definition_mode
        if mode == 'sss':
            if not (self.side_a is not None and self.side_b is not None and self.side_c is not None):
                raise ValueError("SSS模式需要 side_a, side_b, side_c。")
        elif mode == 'coordinates':
            if not (self.p1 is not None and self.p2 is not None and self.p3 is not None):
                raise ValueError("Coordinates模式需要 p1, p2, p3。")
        elif mode == 'sas':
            if not (self.sas_side1 is not None and self.sas_angle_rad is not None and self.sas_side2 is not None):
                raise ValueError("SAS模式需要 sas_side1, sas_angle_rad, sas_side2。")
        elif mode == 'asa':
            if not (self.asa_angle1_rad is not None and self.asa_side_length is not None and self.asa_angle2_rad is not None):
                raise ValueError("ASA模式需要 asa_angle1_rad, asa_side_length, asa_angle2_rad。")
        elif mode == 'aas':
            if not (self.aas_angle1_rad is not None and self.aas_angle2_rad is not None and self.aas_side_a_opposite_p1 is not None):
                raise ValueError("AAS模式需要 aas_angle1_rad, aas_angle2_rad, aas_side_a_opposite_p1。")
        return self

class BasicTriangleParams(BaseFigureParams):
    """基礎三角形參數模型，由三個頂點定義"""
    p1: PointTuple
    p2: PointTuple
    p3: PointTuple
    draw_options: Optional[str] = Field(default=None, description="TikZ draw options, e.g., 'thick,blue'")
    fill_color: Optional[str] = Field(default=None, description="Fill color for the triangle, e.g., 'blue!30'")
    
    @validator('p1', 'p2', 'p3')
    def check_point_format(cls, v):
        if not (isinstance(v, tuple) and len(v) == 2 and
                isinstance(v[0], (int, float)) and isinstance(v[1], (int, float))):
            raise ValueError("Point must be a tuple of two numbers (x,y)")
        return v

class ArcParams(BaseFigureParams):
    """圓弧參數模型"""
    center: PointTuple
    radius: float = Field(..., gt=0) # 半徑必須為正
    start_angle_rad: float # 弧度制起始角
    end_angle_rad: float   # 弧度制結束角
    draw_options: Optional[str] = Field(default=None, description="TikZ draw options, e.g., 'thick,red'")

    @validator('center')
    def check_center_format(cls, v):
        if not (isinstance(v, tuple) and len(v) == 2 and
                isinstance(v[0], (int, float)) and isinstance(v[1], (int, float))):
            raise ValueError("Center must be a tuple of two numbers (x,y)")
        return v