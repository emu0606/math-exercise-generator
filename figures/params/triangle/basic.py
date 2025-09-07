"""基礎三角形參數模型

定義簡單三角形的頂點位置和基本顯示選項，適用於
大多數常見的三角形生成需求。

這個模組包含最基礎和最常用的三角形參數定義，提供
清晰簡潔的接口用於基本三角形生成。

Example:
    >>> from figures.params.triangle.basic import BasicTriangleParams, TriangleParams
    >>> 
    >>> # 基礎三角形 - 通過三個頂點定義
    >>> params = BasicTriangleParams(
    ...     p1=(0, 0), p2=(1, 0), p3=(0.5, 1),
    ...     variant="question"
    ... )
    >>> 
    >>> # 通用三角形 - 通過點列表定義
    >>> triangle_params = TriangleParams(
    ...     points=[[0, 0], [1, 0], [0.5, 1]],
    ...     variant="explanation",
    ...     show_labels=True
    ... )

Note:
    這個模組包含最常用的三角形參數類型。如需要更複雜的
    三角形生成功能（如預定義形狀、自動標籤等），
    請參考 triangle.advanced 模組。
"""

from typing import List, Optional
from pydantic import Field, validator

from ..base import BaseFigureParams
from ..types import PointTuple


class BasicTriangleParams(BaseFigureParams):
    """基礎三角形生成器參數
    
    通過三個頂點定義三角形，支援基本的繪製和填充選項。
    這是最簡單和最常用的三角形參數模型。
    
    Attributes:
        p1 (PointTuple): 第一個頂點座標 (x, y)
        p2 (PointTuple): 第二個頂點座標 (x, y)
        p3 (PointTuple): 第三個頂點座標 (x, y)
        draw_options (str, optional): TikZ 繪製選項，如 'thick,blue'
        fill_color (str, optional): 填充顏色，如 'blue!30'
        
    Example:
        >>> # 基本三角形
        >>> params = BasicTriangleParams(
        ...     p1=(0, 0), p2=(1, 0), p3=(0.5, 1),
        ...     variant="question"
        ... )
        
        >>> # 帶樣式的三角形
        >>> params = BasicTriangleParams(
        ...     p1=(0, 0), p2=(2, 0), p3=(1, 2),
        ...     draw_options="thick,red",
        ...     fill_color="red!20",
        ...     variant="explanation"
        ... )
        
    Note:
        頂點座標使用笛卡兒座標系統，原點在左下角。
        填充顏色使用 TikZ 語法，如 'blue!30' 表示30%透明度的藍色。
    """
    p1: PointTuple = Field(..., description="第一個頂點座標 (x, y)")
    p2: PointTuple = Field(..., description="第二個頂點座標 (x, y)")
    p3: PointTuple = Field(..., description="第三個頂點座標 (x, y)")
    draw_options: Optional[str] = Field(
        default=None, 
        description="TikZ draw options, e.g., 'thick,blue'"
    )
    fill_color: Optional[str] = Field(
        default=None, 
        description="Fill color for the triangle, e.g., 'blue!30'"
    )
    
    @validator('p1', 'p2', 'p3')
    def check_point_format(cls, v):
        """驗證點的格式是否正確
        
        Args:
            v: 待驗證的點座標
            
        Returns:
            tuple: 驗證通過的點座標
            
        Raises:
            ValueError: 當點格式不正確時拋出
        """
        if not (isinstance(v, tuple) and len(v) == 2 and
                isinstance(v[0], (int, float)) and isinstance(v[1], (int, float))):
            raise ValueError("Point must be a tuple of two numbers (x,y)")
        return v


class TriangleParams(BaseFigureParams):
    """通用三角形參數模型
    
    通過點列表定義三角形，支援標籤顯示和樣式設定。
    這個類別提供了更靈活的三角形定義方式。
    
    Attributes:
        points (List[List[float]]): 三個頂點的座標列表 [[x1,y1], [x2,y2], [x3,y3]]
        show_labels (bool): 是否顯示頂點標籤，預設為 True
        label_names (List[str]): 頂點標籤名稱，預設為 ['A', 'B', 'C']
        line_color (str): 線條顏色，預設為 'black'
        fill_color (str, optional): 填充顏色
        line_style (str): 線條樣式，預設為 'solid'
        
    Example:
        >>> # 基本使用
        >>> params = TriangleParams(
        ...     points=[[0, 0], [1, 0], [0.5, 1]],
        ...     variant="question"
        ... )
        
        >>> # 自定義標籤和樣式
        >>> params = TriangleParams(
        ...     points=[[0, 0], [3, 0], [0, 4]],
        ...     show_labels=True,
        ...     label_names=['P', 'Q', 'R'],
        ...     line_color='blue',
        ...     fill_color='blue!10',
        ...     line_style='dashed',
        ...     variant="explanation"
        ... )
        
    Note:
        點的座標格式為 [x, y]，必須提供正好三個點。
        標籤會自動放置在頂點附近的適當位置。
    """
    points: List[List[float]] = Field(
        ..., 
        min_items=3, 
        max_items=3,
        description="三個頂點的座標列表 [[x1,y1], [x2,y2], [x3,y3]]"
    )
    show_labels: bool = Field(
        default=True, 
        description="是否顯示頂點標籤"
    )
    label_names: List[str] = Field(
        default=['A', 'B', 'C'],
        description="頂點標籤名稱"
    )
    line_color: str = Field(
        default='black',
        description="線條顏色"
    )
    fill_color: Optional[str] = Field(
        default=None,
        description="填充顏色"
    )
    line_style: str = Field(
        default='solid',
        description="線條樣式"
    )
    
    @validator('points')
    def validate_points(cls, v):
        """驗證點列表的格式
        
        Args:
            v: 待驗證的點列表
            
        Returns:
            List: 驗證通過的點列表
            
        Raises:
            ValueError: 當點格式不正確時拋出
        """
        if len(v) != 3:
            raise ValueError("Must provide exactly 3 points")
        
        for i, point in enumerate(v):
            if not (isinstance(point, list) and len(point) == 2 and
                    all(isinstance(coord, (int, float)) for coord in point)):
                raise ValueError(f"Point {i} must be a list of two numbers [x, y]")
        return v
    
    @validator('label_names')
    def validate_label_names(cls, v):
        """驗證標籤名稱的數量
        
        Args:
            v: 待驗證的標籤名稱列表
            
        Returns:
            List[str]: 驗證通過的標籤名稱列表
            
        Raises:
            ValueError: 當標籤數量不正確時拋出
        """
        if len(v) != 3:
            raise ValueError("Must provide exactly 3 label names")
        return v