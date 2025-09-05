"""Pydantic 參數模型基礎類型定義

提供所有參數模型使用的通用類型定義，包含 TikZ 相關的
錨點、位置修飾符和基礎數據類型。

Example:
    >>> from figures.params.types import PointTuple, TikzAnchor
    >>> point: PointTuple = (1.0, 2.0)
    >>> anchor: TikzAnchor = "north"

Note:
    此模組包含純類型定義，不包含業務邏輯。所有類型都與 TikZ
    圖形系統兼容，確保生成的圖形代碼符合 TikZ 語法要求。
"""

from typing import Literal, Tuple, Union

# --- TikZ 錨點類型定義 ---

TikzAnchor = Literal[
    'center', 'north', 'south', 'east', 'west',
    'north east', 'north west', 'south east', 'south west',
    'mid', 'mid east', 'mid west', 'base', 'base east', 'base west'
]
"""TikZ 錨點類型定義

用於指定圖形節點的錨定位置。錨點決定圖形的哪個部分用於
定位、對齊或連接操作。

支援的錨點包括：
- 基本方向: center, north, south, east, west
- 對角線方向: north east, north west, south east, south west  
- 文字對齊: mid, mid east, mid west, base, base east, base west

Example:
    >>> anchor: TikzAnchor = "north"
    >>> diagonal_anchor: TikzAnchor = "south east"
    >>> text_anchor: TikzAnchor = "base"
    
Note:
    錨點選擇影響圖形的最終渲染位置和對齊效果。
"""

# --- TikZ 相對位置類型定義 ---

TikzPlacement = Literal[
    'right', 'left', 'above', 'below',
    'above left', 'above right', 'below left', 'below right'
]
"""TikZ 相對位置類型

用於指定一個圖形相對於另一個圖形的位置關係。與 TikZ positioning
庫的放置選項完全兼容。

支援的放置方向：
- 基本方向: right, left, above, below
- 對角線方向: above left, above right, below left, below right

Example:
    >>> placement: TikzPlacement = "right"
    >>> diagonal_placement: TikzPlacement = "above right"
    
Note:
    相對位置通常與距離參數組合使用，創建精確的圖形佈局。
"""

# --- 基礎數據類型定義 ---

PointTuple = Tuple[Union[int, float], Union[int, float]]
"""二維點座標類型

表示平面上一個點的 (x, y) 座標對。支援整數和浮點數坐標值。

Example:
    >>> point: PointTuple = (1.0, 2.0)
    >>> integer_point: PointTuple = (3, 4)
    >>> mixed_point: PointTuple = (1.5, 2)
    
Note:
    座標系統遵循 TikZ 預設座標約定，通常以 cm 為單位。
"""