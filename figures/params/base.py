"""參數模型基礎類別

定義所有圖形參數的基礎類別和通用功能，提供統一的
參數驗證和處理機制。

Example:
    >>> class MyParams(BaseFigureParams):
    ...     value: float = 1.0
    >>> params = MyParams(variant="question", value=2.5)

Note:
    所有具體的圖形參數類別都應繼承 BaseFigureParams，
    確保參數模型的一致性和相容性。
"""

from pydantic import BaseModel
from typing import Literal, Optional
from .types import TikzAnchor, TikzPlacement, PointTuple

class BaseFigureParams(BaseModel):
    """所有圖形參數的抽象基類
    
    提供通用的圖形參數接口，包含變體類型和基礎驗證邏輯。
    所有具體的圖形參數類別都應繼承此基類。
    
    Attributes:
        variant (Literal['question', 'explanation']): 圖形變體類型。
            - 'question': 題目變體，通常顯示較少資訊
            - 'explanation': 詳解變體，通常包含更多標註和說明
            預設為 'question'。
            
    Example:
        創建自定義參數模型::
        
            class MyFigureParams(BaseFigureParams):
                radius: float = 1.0
                color: str = 'blue'
                
            # 使用
            params = MyFigureParams(
                variant='explanation',
                radius=2.5,
                color='red'
            )
            
    Note:
        - 所有圖形生成器都應該支援 variant 參數
        - variant 影響圖形的顯示內容和複雜度
        - 繼承此類別確保參數模型的一致性
    """
    variant: Literal['question', 'explanation'] = 'question'

class AbsolutePosition(BaseModel):
    """絕對定位模型
    
    定義圖形在座標系中的絕對位置。圖形將被放置在指定的 (x, y) 座標上，
    可以選擇圖形的哪個錨點與該座標對齊。
    
    Attributes:
        mode (Literal['absolute']): 定位模式標識符，固定為 'absolute'
        x (float): 水平座標位置，預設為 0.0
        y (float): 垂直座標位置，預設為 0.0
        anchor (TikzAnchor): 圖形用於定位的錨點，預設為 'center'。
            支援標準 TikZ 錨點如 'north', 'south', 'east', 'west' 等。
            
    Example:
        將圖形的左上角放置在 (2, 3) 位置::
        
            position = AbsolutePosition(
                x=2.0,
                y=3.0,
                anchor='north west'
            )
            
    Note:
        - 座標使用 TikZ 預設單位系統
        - 錨點決定圖形的哪個部分對齊到指定座標
        - 適用於精確控制圖形位置的場景
    """
    mode: Literal['absolute'] = 'absolute'
    x: float = 0.0
    y: float = 0.0
    anchor: TikzAnchor = 'center'

class RelativePosition(BaseModel):
    """相對定位模型
    
    定義一個圖形相對於另一個圖形的位置關係。支援各種相對放置模式
    和精確的錨點對齊控制。
    
    Attributes:
        mode (Literal['relative']): 定位模式標識符，固定為 'relative'
        relative_to (str): 參考圖形的 ID，必須是已定義的子圖形標識符
        placement (TikzPlacement): 相對放置方向，如 'right', 'above', 'below left' 等
        distance (str): 與參考圖形的距離，使用 TikZ 單位（如 '1cm', '2mm', '0.5'）
        my_anchor (Optional[TikzAnchor]): 當前圖形用於對齊的錨點，預設為 None
        target_anchor (Optional[TikzAnchor]): 參考圖形用於對齊的錨點，預設為 None
        
    Example:
        將圖形放置在 ID 為 'circle1' 的圖形右側::
        
            position = RelativePosition(
                relative_to='circle1',
                placement='right',
                distance='2cm'
            )
            
        精確錨點對齊::
        
            position = RelativePosition(
                relative_to='triangle1',
                placement='above right',
                distance='1.5cm',
                my_anchor='south west',
                target_anchor='north east'
            )
            
    Note:
        - 參考圖形必須在當前圖形之前定義
        - 距離支援所有 TikZ 單位系統
        - 錨點對齊提供精確的位置控制
        - 適用於創建複雜的圖形佈局關係
    """
    mode: Literal['relative'] = 'relative'
    relative_to: str
    placement: TikzPlacement = 'right'
    distance: str = '1cm'
    my_anchor: Optional[TikzAnchor] = None
    target_anchor: Optional[TikzAnchor] = None

