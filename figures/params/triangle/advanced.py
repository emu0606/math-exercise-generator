"""高級三角形參數模型 - 複雜配置專區

⚠️ 警告: 此文件包含極其複雜的參數配置系統！

包含 162 行的 PredefinedTriangleParams 類別，支援多種
三角形類型、自動標籤、幾何計算等高級功能。

建議開發者優先使用 BasicTriangleParams，除非需要
高度客製化的三角形生成功能。

主要組件:
- 各種樣式配置類別 (Label, Point, Vertex, Side, Angle 等)
- PredefinedTriangleParams 超級複雜參數模型
- 支援多種三角形定義模式 (SSS, SAS, ASA, AAS, Coordinates)
- 完整的顯示配置系統

Example:
    >>> # 基本使用 - 等邊三角形
    >>> params = PredefinedTriangleParams(
    ...     definition_mode="sss",
    ...     side_a=2.0, side_b=2.0, side_c=2.0,
    ...     variant="question"
    ... )
    
    >>> # 複雜使用 - 自定義直角三角形
    >>> params = PredefinedTriangleParams(
    ...     definition_mode="coordinates",
    ...     p1=(0, 0), p2=(3, 0), p3=(0, 4),
    ...     variant="explanation"
    ... )

Note:
    此模組的複雜性較高，建議搭配具體範例和測試用例學習。
    未來可能會將此類別進一步分解為更小的專用類別。
"""

from typing import Dict, List, Optional, Literal, Any
from pydantic import BaseModel, Field, model_validator

from ..base import BaseFigureParams  
from ..types import PointTuple


# ================================
# 樣式配置類別
# ================================

class LabelStyleConfig(BaseModel):
    """標籤樣式配置模型
    
    用於覆蓋 LabelParams 的部分字段或提供給 get_label_placement_params
    的可配置部分，支援完整的文字標籤自定義。
    
    Attributes:
        text_override (str, optional): 覆蓋預設文字內容
        position_modifiers (str, optional): 位置修飾符，如 "above", "left" 等
        anchor (str, optional): 錨點位置，如 "center", "north" 等
        rotate (float, optional): 文字旋轉角度（度）
        color (str, optional): 文字顏色
        font_size (str, optional): 字體大小，如 "small", "large" 等
        math_mode (bool, optional): 是否使用數學模式渲染
        additional_node_options (str, optional): 額外的 TikZ 節點選項
        default_offset_override (float, optional): 覆蓋預設偏移量
        
    Example:
        >>> style = LabelStyleConfig(
        ...     color="blue",
        ...     font_size="large", 
        ...     math_mode=True,
        ...     position_modifiers="above right"
        ... )
    """
    text_override: Optional[str] = Field(
        default=None,
        description="覆蓋預設文字內容"
    )
    position_modifiers: Optional[str] = Field(
        default=None,
        description="位置修飾符，如 'above', 'left' 等"
    )
    anchor: Optional[str] = Field(
        default=None,
        description="錨點位置，如 'center', 'north' 等"
    )
    rotate: Optional[float] = Field(
        default=None,
        description="文字旋轉角度（度）"
    )
    color: Optional[str] = Field(
        default=None,
        description="文字顏色"
    )
    font_size: Optional[str] = Field(
        default=None,
        description="字體大小，如 'small', 'large' 等"
    )
    math_mode: Optional[bool] = Field(
        default=None,
        description="是否使用數學模式渲染"
    )
    additional_node_options: Optional[str] = Field(
        default=None,
        description="額外的 TikZ 節點選項"
    )
    default_offset_override: Optional[float] = Field(
        default=None,
        description="覆蓋 get_label_placement_params 的預設偏移量"
    )


class PointStyleConfig(BaseModel):
    """點樣式配置模型
    
    定義點的視覺樣式，用於 matplotlib 可視化或未來的 TikZ 點生成器。
    支援顏色、標記樣式、大小等完整自定義。
    
    Attributes:
        color (str): 點的顏色，預設為 'black'
        marker (str): 標記樣式，如 'o', 'x', '*', 's' 等
        size_mpl (float): matplotlib 散點圖的大小（points^2）
        tikz_scale (float): TikZ 點縮放比例
        
    Example:
        >>> style = PointStyleConfig(
        ...     color="red",
        ...     marker="*",
        ...     size_mpl=50,
        ...     tikz_scale=1.5
        ... )
    """
    color: Optional[str] = Field(
        default='black',
        description="點的顏色"
    )
    marker: Optional[str] = Field(
        default='o',
        description="標記樣式，如 'o', 'x', '*', 's' (square)"
    )
    size_mpl: Optional[float] = Field(
        default=30,
        description="matplotlib scatter 的大小 (points^2)"
    )
    tikz_scale: Optional[float] = Field(
        default=1.0,
        description="TikZ 點縮放比例"
    )


class VertexDisplayConfig(BaseModel):
    """頂點顯示配置模型
    
    控制三角形頂點的顯示方式，包括點本身和對應的標籤。
    提供完整的頂點可視化控制。
    
    Attributes:
        show_point (bool): 是否顯示頂點點，預設為 True
        point_style (PointStyleConfig, optional): 點的樣式配置
        show_label (bool): 是否顯示頂點標籤，預設為 True  
        label_style (LabelStyleConfig, optional): 標籤的樣式配置
        
    Example:
        >>> config = VertexDisplayConfig(
        ...     show_point=True,
        ...     point_style=PointStyleConfig(color="red", marker="*"),
        ...     show_label=True,
        ...     label_style=LabelStyleConfig(color="blue", font_size="large")
        ... )
    """
    show_point: bool = Field(
        default=True,
        description="是否顯示頂點點"
    )
    point_style: Optional[PointStyleConfig] = Field(
        default_factory=PointStyleConfig,
        description="點的樣式配置"
    )
    show_label: bool = Field(
        default=True,
        description="是否顯示頂點標籤"
    )
    label_style: Optional[LabelStyleConfig] = Field(
        default_factory=LabelStyleConfig,
        description="標籤的樣式配置"
    )


class SideDisplayConfig(BaseModel):
    """邊顯示配置模型
    
    控制三角形邊的標籤顯示，支援多種標籤內容類型：
    名稱、長度值或自定義文字。
    
    Attributes:
        show_label (bool): 是否顯示邊標籤，預設為 True
        label_text_type (Literal): 標籤文字類型，'default_name', 'length', 'custom'
        custom_label_text (str, optional): 自定義標籤文字
        length_format (str): 長度值格式化字符串
        label_style (LabelStyleConfig, optional): 標籤樣式配置
        
    Example:
        >>> config = SideDisplayConfig(
        ...     show_label=True,
        ...     label_text_type="length",
        ...     length_format="{value:.1f}",
        ...     label_style=LabelStyleConfig(color="green")
        ... )
    """
    show_label: bool = Field(
        default=True,
        description="是否顯示邊標籤"
    )
    label_text_type: Literal['default_name', 'length', 'custom'] = Field(
        default='default_name',
        description="標籤文字類型：'default_name' (e.g. 'a'), 'length' (數值), 'custom' (自定義)"
    )
    custom_label_text: Optional[str] = Field(
        default=None,
        description="自定義標籤文字 (當 label_text_type='custom' 時使用)"
    )
    length_format: str = Field(
        default="{value:.2f}",
        description="長度值格式化字符串 (當 label_text_type='length' 時使用)"
    )
    label_style: Optional[LabelStyleConfig] = Field(
        default_factory=LabelStyleConfig,
        description="標籤樣式配置"
    )


class ArcStyleConfig(BaseModel):
    """角弧樣式配置模型
    
    定義角度標記弧線的樣式，用於 ArcGenerator 的 draw_options。
    
    Attributes:
        draw_options (str, optional): TikZ 繪製選項，預設為 "thin"
        
    Example:
        >>> style = ArcStyleConfig(draw_options="thick, blue, dashed")
    """
    draw_options: Optional[str] = Field(
        default="thin",
        description="角弧的 TikZ 繪製選項"
    )


class AngleDisplayConfig(BaseModel):
    """角度顯示配置模型
    
    控制三角形內角的顯示，包括角弧和角度標籤。
    支援多種標籤內容：名稱、角度值或自定義文字。
    
    Attributes:
        show_arc (bool): 是否顯示角弧，預設為 True
        arc_style (ArcStyleConfig, optional): 角弧樣式配置
        arc_radius_config (Any, optional): 角弧半徑配置
        show_label (bool): 是否顯示角度標籤，預設為 True
        label_text_type (Literal): 標籤文字類型
        custom_label_text (str, optional): 自定義標籤文字
        value_format (str): 角度值格式化字符串
        label_style (LabelStyleConfig, optional): 標籤樣式配置
        
    Example:
        >>> config = AngleDisplayConfig(
        ...     show_arc=True,
        ...     arc_style=ArcStyleConfig(draw_options="thick, red"),
        ...     show_label=True,
        ...     label_text_type="value",
        ...     value_format="{value:.0f}°"
        ... )
    """
    show_arc: bool = Field(
        default=True,
        description="是否顯示角弧"
    )
    arc_style: Optional[ArcStyleConfig] = Field(
        default_factory=ArcStyleConfig,
        description="角弧樣式配置"
    )
    arc_radius_config: Optional[Any] = Field(
        default=None,
        description="特定於此角的角弧半徑配置 (如 'auto', 0.5)。若為 None, 則使用全局配置。"
    )
    show_label: bool = Field(
        default=True,
        description="是否顯示角度標籤"
    )
    label_text_type: Literal['default_name', 'value', 'custom'] = Field(
        default='value',
        description="標籤文字類型：'default_name', 'value', 'custom'"
    )
    custom_label_text: Optional[str] = Field(
        default=None,
        description="自定義標籤文字"
    )
    value_format: str = Field(
        default="{value:.1f}°",
        description="角度值格式化字符串（度數）"
    )
    label_style: Optional[LabelStyleConfig] = Field(
        default_factory=LabelStyleConfig,
        description="標籤樣式配置"
    )


class SpecialPointDisplayConfig(BaseModel):
    """特殊點顯示配置模型
    
    控制三角形特殊點（重心、內心、外心、垂心）的顯示方式。
    
    Attributes:
        show_point (bool): 是否顯示特殊點，預設為 True
        point_style (PointStyleConfig, optional): 點的樣式配置
        show_label (bool): 是否顯示點標籤，預設為 True
        label_style (LabelStyleConfig, optional): 標籤樣式配置
        
    Example:
        >>> config = SpecialPointDisplayConfig(
        ...     show_point=True,
        ...     point_style=PointStyleConfig(color="purple", marker="*"),
        ...     show_label=True,
        ...     label_style=LabelStyleConfig(color="purple", font_size="large")
        ... )
    """
    show_point: bool = Field(
        default=True,
        description="是否顯示特殊點"
    )
    point_style: Optional[PointStyleConfig] = Field(
        default_factory=PointStyleConfig,
        description="點的樣式配置"
    )
    show_label: bool = Field(
        default=True,
        description="是否顯示點標籤"
    )
    label_style: Optional[LabelStyleConfig] = Field(
        default_factory=LabelStyleConfig,
        description="標籤樣式配置"
    )


# ================================
# 主要參數類別
# ================================

class PredefinedTriangleParams(BaseFigureParams):
    """預定義三角形參數配置 - 超級複雜版本
    
    ⚠️ 這是一個 162 行的複雜參數類別！
    
    支援多種預定義三角形類型的完整參數系統，包含：
    - 多種三角形類型 (等邊、等腰、直角等)
    - 自動頂點標籤和幾何標記
    - 複雜的樣式和顯示選項
    - 內建幾何計算和驗證
    - 高度可客製化的渲染選項
    
    此類別包含複雜的內部邏輯和驗證規則，建議：
    1. 優先使用 BasicTriangleParams 滿足基本需求
    2. 參考測試檔案中的使用範例
    3. 查看具體三角形類型的文檔說明
    
    支援的定義模式：
    - 'sss': 三邊長定義 (side_a, side_b, side_c)
    - 'sas': 兩邊夾角定義 (sas_side1, sas_angle_rad, sas_side2)  
    - 'asa': 兩角夾邊定義 (asa_angle1_rad, asa_side_length, asa_angle2_rad)
    - 'aas': 兩角一邊定義 (aas_angle1_rad, aas_angle2_rad, aas_side_a_opposite_p1)
    - 'coordinates': 直接座標定義 (p1, p2, p3)
    
    Attributes:
        definition_mode (Literal): 三角形定義方式
        
        # SSS 模式參數
        side_a (float, optional): P2P3 邊長
        side_b (float, optional): P1P3 邊長  
        side_c (float, optional): P1P2 邊長
        
        # 座標模式參數
        p1 (PointTuple, optional): 頂點 P1 座標
        p2 (PointTuple, optional): 頂點 P2 座標
        p3 (PointTuple, optional): 頂點 P3 座標
        
        # SAS 模式參數
        sas_side1 (float, optional): 第一邊長 (P1P2)
        sas_angle_rad (float, optional): 夾角 (P1處)，弧度制
        sas_side2 (float, optional): 第二邊長 (P1P3)
        
        # ASA 模式參數
        asa_angle1_rad (float, optional): P1 處的角，弧度制
        asa_side_length (float, optional): 夾邊 P1P2 的長度
        asa_angle2_rad (float, optional): P2 處的角，弧度制
        
        # AAS 模式參數
        aas_angle1_rad (float, optional): P1 處的角 A，弧度制
        aas_angle2_rad (float, optional): P2 處的角 B，弧度制
        aas_side_a_opposite_p1 (float, optional): P1 對邊 (P2P3) 的長度
        
        # 顯示配置
        vertex_p1_display_config (VertexDisplayConfig): P1 頂點顯示配置
        vertex_p2_display_config (VertexDisplayConfig): P2 頂點顯示配置
        vertex_p3_display_config (VertexDisplayConfig): P3 頂點顯示配置
        default_vertex_labels (List[str]): 頂點預設標籤名
        
        side_p1p2_display_config (SideDisplayConfig): P1P2 邊顯示配置
        side_p2p3_display_config (SideDisplayConfig): P2P3 邊顯示配置
        side_p3p1_display_config (SideDisplayConfig): P3P1 邊顯示配置
        default_side_names (List[str]): 邊的預設名稱
        
        angle_at_p1_display_config (AngleDisplayConfig): P1 處角度顯示配置
        angle_at_p2_display_config (AngleDisplayConfig): P2 處角度顯示配置
        angle_at_p3_display_config (AngleDisplayConfig): P3 處角度顯示配置
        default_angle_names (List[str]): 角的預設名稱
        
        # 特殊點顯示
        display_centroid (SpecialPointDisplayConfig, optional): 重心顯示配置
        display_incenter (SpecialPointDisplayConfig, optional): 內心顯示配置
        display_circumcenter (SpecialPointDisplayConfig, optional): 外心顯示配置
        display_orthocenter (SpecialPointDisplayConfig, optional): 垂心顯示配置
        default_special_point_labels (Dict[str, str]): 特殊點預設標籤
        
        # 全局樣式控制
        global_angle_arc_radius_config (Any): 全局角弧半徑配置
        global_label_default_offset (float): 全局標籤預設偏移量
        triangle_draw_options (str, optional): 主三角形輪廓的 TikZ 選項
        triangle_fill_color (str, optional): 主三角形的填充顏色
        
    Example:
        >>> # 基本使用 - 等邊三角形
        >>> params = PredefinedTriangleParams(
        ...     definition_mode="sss",
        ...     side_a=2.0, side_b=2.0, side_c=2.0,
        ...     variant="question"
        ... )
        
        >>> # 複雜使用 - 自定義直角三角形
        >>> params = PredefinedTriangleParams(
        ...     definition_mode="coordinates",
        ...     p1=(0, 0), p2=(3, 0), p3=(0, 4),
        ...     variant="explanation"
        ... )
        
        >>> # 高級配置 - 帶特殊點和自定義樣式
        >>> params = PredefinedTriangleParams(
        ...     definition_mode="sas",
        ...     sas_side1=3.0, sas_angle_rad=1.047, sas_side2=4.0,  # 60度角
        ...     display_centroid=SpecialPointDisplayConfig(
        ...         show_point=True,
        ...         point_style=PointStyleConfig(color="red", marker="*")
        ...     ),
        ...     variant="explanation"
        ... )
        
    Warning:
        此類別的複雜性很高，不當的參數組合可能導致意外結果。
        強烈建議先閱讀相關文檔和測試範例。
        
    Note:
        未來可能會將此類別進一步分解為更小的專用類別，
        以降低複雜性和提高可維護性。
    """
    
    # 1. 三角形定義 (對應 utils.geometry.triangle_constructions.TriangleConstructor 的參數)
    definition_mode: Literal['sss', 'sas', 'asa', 'aas', 'coordinates'] = Field(
        ...,
        description="定義三角形的方式"
    )
    
    # SSS 參數
    side_a: Optional[float] = Field(
        default=None, 
        description="P2P3 長度 (用於 SSS 模式)"
    )
    side_b: Optional[float] = Field(
        default=None, 
        description="P1P3 長度 (用於 SSS 模式)"
    )
    side_c: Optional[float] = Field(
        default=None, 
        description="P1P2 長度 (用於 SSS 模式)"
    )
    
    # Coordinates 參數
    p1: Optional[PointTuple] = Field(
        default=None, 
        description="頂點 P1 座標 (用於 'coordinates' 模式)"
    )
    p2: Optional[PointTuple] = Field(
        default=None, 
        description="頂點 P2 座標 (用於 'coordinates' 模式)"
    )
    p3: Optional[PointTuple] = Field(
        default=None, 
        description="頂點 P3 座標 (用於 'coordinates' 模式)"
    )
    
    # SAS 參數 (P1 為夾角頂點，P1P2 為 side1, P1P3 為 side2)
    sas_side1: Optional[float] = Field(
        default=None, 
        description="第一邊長 (P1P2) (用於 SAS 模式)"
    )
    sas_angle_rad: Optional[float] = Field(
        default=None, 
        description="夾角 (P1處)，弧度制 (用於 SAS 模式)"
    )
    sas_side2: Optional[float] = Field(
        default=None, 
        description="第二邊長 (P1P3) (用於 SAS 模式)"
    )
    
    # ASA 參數 (P1P2 為夾邊 side_length, 角在 P1, P2)
    asa_angle1_rad: Optional[float] = Field(
        default=None, 
        description="P1 處的角，弧度制 (用於 ASA 模式)"
    )
    asa_side_length: Optional[float] = Field(
        default=None, 
        description="夾邊 P1P2 的長度 (用於 ASA 模式)"
    )
    asa_angle2_rad: Optional[float] = Field(
        default=None, 
        description="P2 處的角，弧度制 (用於 ASA 模式)"
    )
    
    # AAS 參數 (角A at P1, 角B at P2, P1的對邊 a 即 P2P3)
    aas_angle1_rad: Optional[float] = Field(
        default=None, 
        description="P1 處的角 A，弧度制 (用於 AAS 模式)"
    )
    aas_angle2_rad: Optional[float] = Field(
        default=None, 
        description="P2 處的角 B，弧度制 (用於 AAS 模式)"
    )
    aas_side_a_opposite_p1: Optional[float] = Field(
        default=None, 
        description="P1 對邊 (P2P3) 的長度 (用於 AAS 模式)"
    )

    # 2. 元素顯示配置
    # 頂點 (P1, P2, P3 的順序由 get_vertices 按約定返回)
    vertex_p1_display_config: VertexDisplayConfig = Field(
        default_factory=VertexDisplayConfig,
        description="P1 頂點顯示配置"
    )
    vertex_p2_display_config: VertexDisplayConfig = Field(
        default_factory=VertexDisplayConfig,
        description="P2 頂點顯示配置"
    )
    vertex_p3_display_config: VertexDisplayConfig = Field(
        default_factory=VertexDisplayConfig,
        description="P3 頂點顯示配置"
    )
    default_vertex_labels: List[str] = Field(
        default=['A', 'B', 'C'], 
        description="頂點的預設標籤名 (若對應配置中 label_text 未指定)"
    )

    # 邊 (P1P2, P2P3, P3P1)
    side_p1p2_display_config: SideDisplayConfig = Field(
        default_factory=SideDisplayConfig,
        description="P1P2 邊顯示配置 (通常對應 'c')"
    )
    side_p2p3_display_config: SideDisplayConfig = Field(
        default_factory=SideDisplayConfig,
        description="P2P3 邊顯示配置 (通常對應 'a')"
    )
    side_p3p1_display_config: SideDisplayConfig = Field(
        default_factory=SideDisplayConfig,
        description="P3P1 邊顯示配置 (通常對應 'b')"
    )
    default_side_names: List[str] = Field(
        default=['c', 'a', 'b'], 
        description="邊的預設名稱 (P1P2, P2P3, P3P1)"
    )

    # 角 (角於 P1, P2, P3)
    angle_at_p1_display_config: AngleDisplayConfig = Field(
        default_factory=AngleDisplayConfig,
        description="P1 處角度顯示配置"
    )
    angle_at_p2_display_config: AngleDisplayConfig = Field(
        default_factory=AngleDisplayConfig,
        description="P2 處角度顯示配置"
    )
    angle_at_p3_display_config: AngleDisplayConfig = Field(
        default_factory=AngleDisplayConfig,
        description="P3 處角度顯示配置"
    )
    default_angle_names: List[str] = Field(
        default=['A', 'B', 'C'], 
        description="角的預設名稱 (頂點P1, P2, P3處)"
    )

    # 特殊點
    display_centroid: Optional[SpecialPointDisplayConfig] = Field(
        default=None,
        description="重心顯示配置"
    )
    display_incenter: Optional[SpecialPointDisplayConfig] = Field(
        default=None,
        description="內心顯示配置"
    )
    display_circumcenter: Optional[SpecialPointDisplayConfig] = Field(
        default=None,
        description="外心顯示配置"
    )
    display_orthocenter: Optional[SpecialPointDisplayConfig] = Field(
        default=None,
        description="垂心顯示配置"
    )
    default_special_point_labels: Dict[str, str] = Field(
        default={
            'centroid': 'G', 'incenter': 'I',
            'circumcenter': 'O', 'orthocenter': 'H'
        },
        description="特殊點的預設標籤名稱"
    )

    # 3. 全局樣式和行為控制
    global_angle_arc_radius_config: Any = Field(
        default="auto", 
        description="全局角弧半徑配置 (傳給 get_arc_render_params)"
    )
    global_label_default_offset: float = Field(
        default=0.15, 
        description="全局標籤預設偏移量 (傳給 get_label_placement_params)"
    )
    
    triangle_draw_options: Optional[str] = Field(
        default="thin, black", 
        description="主三角形輪廓的 TikZ 選項 (傳給 BasicTriangleGenerator)"
    )
    triangle_fill_color: Optional[str] = Field(
        default=None, 
        description="主三角形的填充顏色 (傳給 BasicTriangleGenerator)"
    )

    @model_validator(mode='after')
    def check_definition_params_v2(self) -> 'PredefinedTriangleParams':
        """驗證三角形定義參數的完整性
        
        根據不同的 definition_mode，檢查對應的參數是否都已提供。
        確保每種定義模式都有足夠的參數來構造三角形。
        
        Returns:
            PredefinedTriangleParams: 驗證通過的參數實例
            
        Raises:
            ValueError: 當必需參數缺失時拋出
        """
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