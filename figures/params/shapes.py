#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 標準形狀參數

此模組定義了常用標準形狀和特殊圖形的參數模型，包括單位圓、
座標系統等預定義形狀的專門參數配置。這些參數模型針對特定
應用場景進行了優化，提供豐富的配置選項。

主要組件：
1. **標準單位圓參數**: 完整功能的單位圓配置
2. **座標系統參數**: 座標軸和網格的參數配置  
3. **基礎三角形參數**: 簡化版三角形參數模型
4. **標籤參數**: 文字標籤的詳細配置選項

設計特點：
- 針對教學場景優化的預設參數
- 豐富的顯示控制選項
- 支援多種標註和樣式配置
- 與基礎幾何參數互補使用

Example:
    標準單位圓使用::
    
        from figures.params.shapes import StandardUnitCircleParams
        
        params = StandardUnitCircleParams(
            angle=60,
            show_coordinates=True,
            show_angle=True,
            show_radius=True,
            label_point=True,
            point_label='P',
            variant='explanation'
        )
        
    座標系統配置::
    
        from figures.params.shapes import CoordinateSystemParams
        
        params = CoordinateSystemParams(
            x_range=[-3, 3],
            y_range=[-2, 2], 
            show_grid=True,
            show_axes_labels=True
        )

Note:
    - 標準形狀參數包含更多預設配置選項
    - 適合快速創建常用的教學圖形
    - 可與基礎幾何參數組合使用
    - 支援高度自定義的視覺效果
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Literal, Tuple
from .base import BaseFigureParams
from .types import PointTuple

class StandardUnitCircleParams(BaseFigureParams):
    """標準單位圓參數模型
    
    專為教學設計的完整功能單位圓，包含角度標記、座標顯示、
    三角函數可視化等豐富功能。相比基礎 UnitCircleParams，
    提供更多教學相關的配置選項。
    
    Attributes:
        angle (float): 標記的角度（度），範圍 0-360
        show_coordinates (bool): 是否顯示點的座標值
        show_angle (bool): 是否顯示角度弧線標記
        show_point (bool): 是否顯示角度對應的點
        show_radius (bool): 是否顯示從圓心到點的半徑線
        line_color (str): 圓周線條顏色
        point_color (str): 角度點的顏色  
        angle_color (str): 角度弧線顏色
        radius_color (str): 半徑線顏色
        coordinate_color (str): 座標標籤顏色
        radius (float): 圓的半徑，預設為 1.0
        label_point (bool): 是否為角度點添加標籤
        point_label (str): 角度點的標籤文字
        
    Example:
        創建完整功能的單位圓::
        
            params = StandardUnitCircleParams(
                angle=45,
                show_coordinates=True,
                show_angle=True, 
                show_radius=True,
                label_point=True,
                point_label='P',
                coordinate_color='gray',
                variant='explanation'
            )
            
    Note:
        - 專為三角函數教學設計
        - explanation 模式下顯示更多輔助資訊
        - 座標顯示格式為 (cos θ, sin θ)
        - 支援角度和弧度制轉換顯示
    """
    angle: float = Field(..., ge=0, le=360, description="標記的角度（度）")
    show_coordinates: bool = Field(default=True, description="是否顯示點的座標值")
    show_angle: bool = Field(default=True, description="是否顯示角度弧線標記")
    show_point: bool = Field(default=True, description="是否顯示角度對應的點")
    show_radius: bool = Field(default=True, description="是否顯示半徑線")
    line_color: str = Field(default='black', description="圓周線條顏色")
    point_color: str = Field(default='red', description="角度點顏色")
    angle_color: str = Field(default='blue', description="角度弧線顏色")
    radius_color: str = Field(default='red', description="半徑線顏色")
    coordinate_color: str = Field(default='gray', description="座標標籤顏色")
    radius: float = Field(default=1.0, description="圓的半徑")
    label_point: bool = Field(default=True, description="是否為角度點添加標籤")
    point_label: str = Field(default='P', description="角度點的標籤文字")

class CoordinateSystemParams(BaseFigureParams):
    """座標系統參數模型
    
    定義 2D 笛卡爾座標系統的參數，包括座標軸範圍、網格線、
    刻度標記和軸標籤等功能。用於為其他圖形提供座標背景。
    
    Attributes:
        x_range (Tuple[float, float]): x 軸顯示範圍 [最小值, 最大值]
        y_range (Tuple[float, float]): y 軸顯示範圍 [最小值, 最大值]
        show_axes (bool): 是否顯示座標軸
        show_grid (bool): 是否顯示網格線
        show_ticks (bool): 是否顯示刻度標記
        show_axes_labels (bool): 是否顯示軸標籤（x, y）
        x_label (str): x 軸標籤文字
        y_label (str): y 軸標籤文字
        axes_color (str): 座標軸顏色
        grid_color (str): 網格線顏色
        grid_style (Literal): 網格線樣式
        tick_interval (float): 刻度間隔
        origin_marker (bool): 是否標記原點
        
    Example:
        創建標準座標系統::
        
            coord_system = CoordinateSystemParams(
                x_range=[-5, 5],
                y_range=[-3, 3],
                show_grid=True,
                show_axes_labels=True,
                tick_interval=1.0,
                grid_style='dashed'
            )
            
    Note:
        - 適合作為其他圖形的背景
        - 網格有助於讀取座標值
        - 可調整範圍適應不同比例的圖形
    """
    x_range: Tuple[float, float] = Field(default=(-5, 5), description="x 軸顯示範圍")
    y_range: Tuple[float, float] = Field(default=(-5, 5), description="y 軸顯示範圍")
    show_axes: bool = Field(default=True, description="是否顯示座標軸")
    show_grid: bool = Field(default=False, description="是否顯示網格線")
    show_ticks: bool = Field(default=True, description="是否顯示刻度標記")
    show_axes_labels: bool = Field(default=True, description="是否顯示軸標籤")
    x_label: str = Field(default='x', description="x 軸標籤文字")
    y_label: str = Field(default='y', description="y 軸標籤文字")
    axes_color: str = Field(default='black', description="座標軸顏色")
    grid_color: str = Field(default='lightgray', description="網格線顏色")
    grid_style: Literal['solid', 'dashed', 'dotted'] = Field(default='dashed', description="網格線樣式")
    tick_interval: float = Field(default=1.0, gt=0, description="刻度間隔")
    origin_marker: bool = Field(default=False, description="是否標記原點")
    
    @validator('x_range', 'y_range')
    def validate_range(cls, v):
        """驗證範圍格式"""
        if len(v) != 2:
            raise ValueError("範圍必須包含恰好兩個數值 [最小值, 最大值]")
        if v[0] >= v[1]:
            raise ValueError("範圍的最小值必須小於最大值")
        return v

class BasicTriangleParams(BaseFigureParams):
    """基礎三角形參數模型
    
    簡化版的三角形參數模型，提供最常用的配置選項。
    適合快速創建標準的三角形圖形，減少參數複雜度。
    
    Attributes:
        points (List[PointTuple]): 三角形三個頂點座標
        show_labels (bool): 是否顯示頂點標籤
        label_names (List[str]): 頂點標籤名稱
        color (str): 三角形顏色（邊框和填充）
        fill (bool): 是否填充三角形內部
        alpha (float): 填充透明度，範圍 0-1
        
    Example:
        創建簡單填充三角形::
        
            triangle = BasicTriangleParams(
                points=[[0, 0], [3, 0], [1.5, 2.6]],
                show_labels=True,
                color='blue',
                fill=True,
                alpha=0.3
            )
            
    Note:
        - 簡化的參數配置，適合快速使用
        - 統一的顏色設置，減少選擇困難
        - 透明度控制便於疊加顯示
    """
    points: List[PointTuple] = Field(..., min_items=3, max_items=3, description="三角形三個頂點座標")
    show_labels: bool = Field(default=True, description="是否顯示頂點標籤")
    label_names: List[str] = Field(default=['A', 'B', 'C'], description="頂點標籤名稱")
    color: str = Field(default='blue', description="三角形顏色")
    fill: bool = Field(default=False, description="是否填充三角形內部")
    alpha: float = Field(default=0.3, ge=0, le=1, description="填充透明度")
    
    @validator('label_names')
    def validate_label_names_length(cls, v, values):
        """驗證標籤數量與頂點數量匹配"""
        if 'points' in values and len(v) != len(values['points']):
            raise ValueError(f"標籤數量 ({len(v)}) 必須與頂點數量 ({len(values['points'])}) 匹配")
        return v

class LabelParams(BaseFigureParams):
    """標籤參數模型
    
    詳細的文字標籤配置模型，支援位置控制、樣式設定、
    旋轉和各種 TikZ 高級功能。適用於添加說明文字和標註。
    
    Attributes:
        x (float): 標籤 x 座標
        y (float): 標籤 y 座標  
        text (str): 標籤文字內容
        position_modifiers (Optional[str]): TikZ 位置修飾詞
        anchor (Optional[str]): 標籤錨點設定
        rotate (Optional[float]): 文字旋轉角度
        color (str): 文字顏色
        font_size (Optional[str]): 字體大小命令
        math_mode (bool): 是否使用數學模式
        additional_node_options (Optional[str]): 額外的 TikZ 節點選項
        
    Example:
        創建數學公式標籤::
        
            label = LabelParams(
                x=2.0, y=3.0,
                text=r'f(x) = x^2',
                math_mode=True,
                color='blue',
                font_size=r'\\large',
                anchor='center'
            )
            
        創建旋轉標籤::
        
            rotated_label = LabelParams(
                x=1.0, y=1.0,
                text='傾斜文字',
                rotate=45,
                anchor='south west',
                color='red'
            )
            
    Note:
        - 支援 LaTeX 數學公式
        - 靈活的位置控制選項
        - 可與其他圖形元素精確對齊
        - 支援 TikZ 的所有文字樣式功能
    """
    x: float = Field(default=0.0, description="標籤 x 座標")
    y: float = Field(default=0.0, description="標籤 y 座標")
    text: str = Field(default='', description="標籤文字內容")
    position_modifiers: Optional[str] = Field(default=None, description="TikZ 位置修飾詞")
    anchor: Optional[str] = Field(default=None, description="標籤錨點設定")
    rotate: Optional[float] = Field(default=None, description="文字旋轉角度")
    color: str = Field(default='black', description="文字顏色")
    font_size: Optional[str] = Field(default=None, description="字體大小命令")
    math_mode: bool = Field(default=True, description="是否使用數學模式")
    additional_node_options: Optional[str] = Field(default=None, description="額外的 TikZ 節點選項")
    
    @validator('x', 'y', pre=True, always=True)
    def ensure_xy_float_if_not_none(cls, v):
        """確保座標為浮點數"""
        if v is not None:
            try:
                return float(v)
            except ValueError as e_conv:
                raise ValueError("座標值 (x,y) 無法轉換為浮點數") from e_conv
        return v
        
    @validator('anchor', 'position_modifiers', 'font_size', 'additional_node_options', pre=True, always=True)
    def ensure_optional_strings_are_strings(cls, v):
        """確保可選字串欄位為字串類型"""
        if v is not None:
            if not isinstance(v, str):
                raise ValueError("錨點、位置修飾詞、字體大小和附加選項等值必須是字符串")
            return v
        return v

class GridParams(BaseFigureParams):
    """網格參數模型
    
    專門用於繪製各種類型網格的參數配置，包括方形網格、
    極座標網格等。可作為獨立圖形或其他圖形的背景。
    
    Attributes:
        grid_type (Literal): 網格類型 - 方形或極座標
        x_range (Tuple[float, float]): x 方向範圍
        y_range (Tuple[float, float]): y 方向範圍
        x_step (float): x 方向網格間距
        y_step (float): y 方向網格間距
        major_color (str): 主網格線顏色
        minor_color (str): 次網格線顏色
        show_major (bool): 是否顯示主網格線
        show_minor (bool): 是否顯示次網格線
        line_width (str): 網格線粗細
        
    Example:
        創建精細網格::
        
            grid = GridParams(
                grid_type='rectangular',
                x_range=(-3, 3),
                y_range=(-2, 2),
                x_step=0.5, y_step=0.5,
                show_minor=True,
                minor_color='lightgray'
            )
    """
    grid_type: Literal['rectangular', 'polar'] = Field(default='rectangular', description="網格類型")
    x_range: Tuple[float, float] = Field(default=(-5, 5), description="x 方向範圍")
    y_range: Tuple[float, float] = Field(default=(-5, 5), description="y 方向範圍")
    x_step: float = Field(default=1.0, gt=0, description="x 方向網格間距")
    y_step: float = Field(default=1.0, gt=0, description="y 方向網格間距")
    major_color: str = Field(default='gray', description="主網格線顏色")
    minor_color: str = Field(default='lightgray', description="次網格線顏色")
    show_major: bool = Field(default=True, description="是否顯示主網格線")
    show_minor: bool = Field(default=False, description="是否顯示次網格線")
    line_width: str = Field(default='thin', description="網格線粗細")