#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 基礎幾何圖形參數

此模組定義了基本幾何圖形的參數模型，包括點、線、角、三角形和圓等
基礎幾何元素的參數定義。這些參數模型為幾何圖形生成器提供標準化的
輸入驗證和類型安全保證。

主要組件：
1. **點參數模型**: 座標點的參數定義
2. **線段參數模型**: 直線和線段的參數配置
3. **角度參數模型**: 角度顯示和標註參數
4. **三角形參數模型**: 基本三角形幾何參數
5. **圓形參數模型**: 圓和弧的基礎參數

設計原則：
- 所有模型繼承自 BaseFigureParams 確保一致性
- 使用 Pydantic 框架進行參數驗證
- 支援 question/explanation 雙變體模式
- 提供豐富的樣式和顯示配置選項

Example:
    基本三角形參數使用::
    
        from figures.params.geometry import TriangleParams
        
        params = TriangleParams(
            points=[[0, 0], [3, 0], [1.5, 2.6]],
            show_labels=True,
            label_names=['A', 'B', 'C'],
            variant='explanation'
        )
        
    單位圓參數配置::
    
        from figures.params.geometry import UnitCircleParams
        
        params = UnitCircleParams(
            angle=60,
            show_coordinates=True,
            show_angle=True,
            variant='question'
        )

Note:
    - 所有幾何參數模型支援 variant 參數控制顯示模式
    - 座標使用標準數學座標系統（y 軸向上）
    - 角度使用度數制，範圍為 0-360 度
    - 顏色參數支援標準 TikZ 顏色名稱
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Literal
from .base import BaseFigureParams
from .types import PointTuple

class PointParams(BaseFigureParams):
    """點參數模型
    
    定義座標平面上一個點的參數，包括座標位置和顯示樣式。
    支援點的標註、顏色配置和形狀選擇。
    
    Attributes:
        x (float): 點的 x 座標
        y (float): 點的 y 座標  
        label (Optional[str]): 點的標籤文字，為 None 時不顯示標籤
        color (str): 點的顏色，預設為 'red'
        size (str): 點的大小，使用 TikZ 單位，預設為 '2pt'
        shape (Literal): 點的形狀，支援 'circle', 'square', 'triangle'
        
    Example:
        創建帶標籤的紅色圓點::
        
            point = PointParams(
                x=2.0, y=3.0,
                label='P',
                color='red',
                shape='circle'
            )
    """
    x: float = Field(default=0.0, description="點的 x 座標")
    y: float = Field(default=0.0, description="點的 y 座標")
    label: Optional[str] = Field(default=None, description="點的標籤文字")
    color: str = Field(default='red', description="點的顏色")
    size: str = Field(default='2pt', description="點的大小")
    shape: Literal['circle', 'square', 'triangle'] = Field(default='circle', description="點的形狀")

class LineParams(BaseFigureParams):
    """直線/線段參數模型
    
    定義直線或線段的參數，支援端點座標、樣式配置和標註選項。
    可以配置線條的顏色、粗細、樣式和箭頭等視覺屬性。
    
    Attributes:
        start_point (PointTuple): 線段起始點座標 [x, y]
        end_point (PointTuple): 線段結束點座標 [x, y]  
        color (str): 線條顏色，預設為 'black'
        width (str): 線條粗細，使用 TikZ 單位，預設為 'thick'
        style (Literal): 線條樣式，支援實線、虛線等
        arrow (Optional[str]): 箭頭樣式，None 為無箭頭
        label (Optional[str]): 線段標籤
        label_position (float): 標籤在線段上的位置，0.5 為中點
        
    Example:
        創建帶箭頭的藍色直線::
        
            line = LineParams(
                start_point=[0, 0],
                end_point=[3, 2],
                color='blue',
                arrow='->',
                label='AB'
            )
    """
    start_point: PointTuple = Field(default=[0, 0], description="線段起始點座標")
    end_point: PointTuple = Field(default=[1, 1], description="線段結束點座標")  
    color: str = Field(default='black', description="線條顏色")
    width: str = Field(default='thick', description="線條粗細")
    style: Literal['solid', 'dashed', 'dotted', 'dash dot'] = Field(default='solid', description="線條樣式")
    arrow: Optional[str] = Field(default=None, description="箭頭樣式")
    label: Optional[str] = Field(default=None, description="線段標籤")
    label_position: float = Field(default=0.5, ge=0, le=1, description="標籤在線段上的位置比例")

class AngleParams(BaseFigureParams):
    """角度參數模型
    
    定義角度的顯示參數，支援角度標記、弧線樣式和角度數值標註。
    用於在幾何圖形中標示和強調角度資訊。
    
    Attributes:
        vertex (PointTuple): 角度頂點座標 [x, y]
        ray1_point (PointTuple): 第一條射線上的點座標
        ray2_point (PointTuple): 第二條射線上的點座標
        angle_value (Optional[float]): 角度數值（度），為 None 時不顯示數值
        show_arc (bool): 是否顯示角度弧線標記
        arc_radius (float): 弧線半徑
        color (str): 角度標記顏色
        label (Optional[str]): 角度標籤，如 'α', '∠A'
        
    Example:
        創建 60 度角標記::
        
            angle = AngleParams(
                vertex=[0, 0],
                ray1_point=[2, 0], 
                ray2_point=[1, 1.732],
                angle_value=60,
                show_arc=True,
                label='α'
            )
    """
    vertex: PointTuple = Field(default=[0, 0], description="角度頂點座標")
    ray1_point: PointTuple = Field(default=[1, 0], description="第一條射線上的點座標")
    ray2_point: PointTuple = Field(default=[0, 1], description="第二條射線上的點座標")
    angle_value: Optional[float] = Field(default=None, ge=0, le=360, description="角度數值（度）")
    show_arc: bool = Field(default=True, description="是否顯示角度弧線標記")
    arc_radius: float = Field(default=0.5, gt=0, description="弧線半徑")
    color: str = Field(default='blue', description="角度標記顏色")
    label: Optional[str] = Field(default=None, description="角度標籤")

class TriangleParams(BaseFigureParams):
    """基礎三角形參數模型
    
    定義三角形的基本幾何參數，包括三個頂點座標、標籤和樣式配置。
    支援三角形的填充、邊框和頂點標註等視覺效果。
    
    Attributes:
        points (List[PointTuple]): 三角形三個頂點的座標列表，必須包含恰好 3 個點
        show_labels (bool): 是否顯示頂點標籤
        label_names (List[str]): 頂點標籤名稱，預設為 ['A', 'B', 'C']
        line_color (str): 邊框顏色
        fill_color (Optional[str]): 填充顏色，None 為不填充
        line_style (Literal): 邊框線條樣式
        show_sides (bool): 是否顯示邊長
        show_angles (bool): 是否顯示內角
        
    Example:
        創建等邊三角形::
        
            triangle = TriangleParams(
                points=[[0, 0], [2, 0], [1, 1.732]],
                show_labels=True,
                label_names=['A', 'B', 'C'],
                fill_color='lightblue',
                variant='explanation'
            )
            
    Note:
        - points 列表必須包含恰好 3 個座標點
        - 座標按逆時針順序定義頂點
        - label_names 的長度必須與 points 長度匹配
    """
    points: List[PointTuple] = Field(..., min_items=3, max_items=3, description="三角形三個頂點座標")
    show_labels: bool = Field(default=True, description="是否顯示頂點標籤")
    label_names: List[str] = Field(default=['A', 'B', 'C'], description="頂點標籤名稱")
    line_color: str = Field(default='black', description="邊框顏色")
    fill_color: Optional[str] = Field(default=None, description="填充顏色")
    line_style: Literal['solid', 'dashed', 'dotted'] = Field(default='solid', description="邊框樣式")
    show_sides: bool = Field(default=False, description="是否顯示邊長")
    show_angles: bool = Field(default=False, description="是否顯示內角")
    
    @validator('label_names')
    def validate_label_names_length(cls, v, values):
        """驗證標籤名稱數量與頂點數量匹配"""
        if 'points' in values and len(v) != len(values['points']):
            raise ValueError(f"標籤數量 ({len(v)}) 必須與頂點數量 ({len(values['points'])}) 匹配")
        return v

class CircleParams(BaseFigureParams):
    """圓形參數模型
    
    定義圓形的幾何和樣式參數，包括圓心、半徑和各種顯示選項。
    支援圓的填充、邊框和標註等功能。
    
    Attributes:
        center (PointTuple): 圓心座標 [x, y]
        radius (float): 圓的半徑，必須為正數
        color (str): 圓邊框顏色
        fill_color (Optional[str]): 填充顏色，None 為不填充
        line_width (str): 邊框線條粗細
        show_center (bool): 是否標記圓心
        center_label (Optional[str]): 圓心標籤
        show_radius (bool): 是否顯示半徑線
        
    Example:
        創建填充的紅色圓::
        
            circle = CircleParams(
                center=[0, 0],
                radius=2.0,
                color='red',
                fill_color='pink',
                show_center=True,
                center_label='O'
            )
    """
    center: PointTuple = Field(default=[0, 0], description="圓心座標")
    radius: float = Field(default=1.0, gt=0, description="圓的半徑")
    color: str = Field(default='black', description="圓邊框顏色")
    fill_color: Optional[str] = Field(default=None, description="填充顏色")
    line_width: str = Field(default='thick', description="邊框線條粗細")
    show_center: bool = Field(default=False, description="是否標記圓心")
    center_label: Optional[str] = Field(default=None, description="圓心標籤")
    show_radius: bool = Field(default=False, description="是否顯示半徑線")

class UnitCircleParams(BaseFigureParams):
    """單位圓參數模型
    
    專門用於單位圓（半徑為1的圓）的參數配置，支援角度標記、
    座標顯示和三角函數相關的可視化功能。
    
    Attributes:
        angle (float): 標記的角度（度），範圍 0-360
        show_coordinates (bool): 是否顯示點的座標
        line_color (str): 圓和線條顏色
        point_color (str): 角度點顏色
        angle_color (str): 角度弧線顏色
        radius (float): 圓的半徑，預設為 1.0
        show_angle (bool): 是否顯示角度弧線
        show_point (bool): 是否顯示角度對應的點
        show_radius (bool): 是否顯示半徑線
        
    Example:
        創建 45 度角的單位圓::
        
            unit_circle = UnitCircleParams(
                angle=45,
                show_coordinates=True,
                show_angle=True,
                show_radius=True,
                variant='explanation'
            )
            
    Note:
        - angle 參數決定在圓上標記的角度位置
        - show_coordinates 在 explanation 模式下特別有用
        - 適用於三角函數教學和角度概念說明
    """
    angle: float = Field(..., ge=0, le=360, description="標記的角度（度）")
    show_coordinates: bool = Field(default=True, description="是否顯示點的座標")
    line_color: str = Field(default='black', description="圓和線條顏色")
    point_color: str = Field(default='red', description="角度點顏色")
    angle_color: str = Field(default='blue', description="角度弧線顏色")
    radius: float = Field(default=1.0, description="圓的半徑")
    show_angle: bool = Field(default=True, description="是否顯示角度弧線")
    show_point: bool = Field(default=True, description="是否顯示角度對應的點")
    show_radius: bool = Field(default=True, description="是否顯示半徑線")

class ArcParams(BaseFigureParams):
    """弧形參數模型
    
    定義圓弧的幾何參數，包括圓心、半徑、起始角度和結束角度。
    支援弧線的樣式配置和角度標註。
    
    Attributes:
        center (PointTuple): 弧的圓心座標
        radius (float): 弧的半徑
        start_angle (float): 起始角度（度）
        end_angle (float): 結束角度（度）
        color (str): 弧線顏色
        line_width (str): 線條粗細
        show_endpoints (bool): 是否標記端點
        arrow (Optional[str]): 箭頭樣式
        
    Example:
        創建 90 度弧線::
        
            arc = ArcParams(
                center=[0, 0],
                radius=2.0,
                start_angle=0,
                end_angle=90,
                color='blue',
                show_endpoints=True
            )
    """
    center: PointTuple = Field(default=[0, 0], description="弧的圓心座標")
    radius: float = Field(default=1.0, gt=0, description="弧的半徑")
    start_angle: float = Field(default=0, ge=0, le=360, description="起始角度（度）")
    end_angle: float = Field(default=90, ge=0, le=360, description="結束角度（度）")
    color: str = Field(default='black', description="弧線顏色")
    line_width: str = Field(default='thick', description="線條粗細")
    show_endpoints: bool = Field(default=False, description="是否標記端點")
    arrow: Optional[str] = Field(default=None, description="箭頭樣式")
    
    @validator('end_angle')
    def validate_angle_range(cls, v, values):
        """驗證結束角度必須大於起始角度"""
        if 'start_angle' in values and v <= values['start_angle']:
            raise ValueError("結束角度必須大於起始角度")
        return v