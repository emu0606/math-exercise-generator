"""三角形參數模組統一接口

本子模組提供所有三角形相關的參數模型，從簡單的基礎三角形
到複雜的預定義三角形配置系統。

模組結構：
- basic: 基礎三角形參數 (BasicTriangleParams, TriangleParams)
- advanced: 高級三角形參數 (PredefinedTriangleParams + 完整配置系統)

建議使用順序：
1. 首先嘗試 BasicTriangleParams - 適用於大多數基本需求
2. 如需更多標籤控制，使用 TriangleParams
3. 只有在需要高度客製化時才使用 PredefinedTriangleParams

Example:
    >>> # 基本使用 - 推薦
    >>> from figures.params.triangle import BasicTriangleParams
    >>> params = BasicTriangleParams(
    ...     p1=(0, 0), p2=(1, 0), p3=(0.5, 1),
    ...     variant="question"
    ... )
    
    >>> # 進階使用 - 複雜配置
    >>> from figures.params.triangle import PredefinedTriangleParams
    >>> params = PredefinedTriangleParams(
    ...     definition_mode="sss",
    ...     side_a=3.0, side_b=4.0, side_c=5.0,
    ...     variant="explanation"
    ... )

Note:
    advanced 模組包含極其複雜的參數系統，建議在使用前
    先查看具體的使用範例和測試案例。
"""

# 基礎三角形參數 - 推薦日常使用
from .basic import (
    BasicTriangleParams,
    TriangleParams,
)

# 高級三角形參數 - 複雜配置專用
from .advanced import (
    # 主要參數類別
    PredefinedTriangleParams,
    
    # 樣式配置類別 (用於高級自定義)
    LabelStyleConfig,
    PointStyleConfig,
    VertexDisplayConfig,
    SideDisplayConfig,
    ArcStyleConfig,
    AngleDisplayConfig,
    SpecialPointDisplayConfig,
)

# 為了方便訪問，定義 __all__
__all__ = [
    # 基礎三角形參數
    'BasicTriangleParams',
    'TriangleParams',
    
    # 高級三角形參數
    'PredefinedTriangleParams',
    
    # 樣式配置類別
    'LabelStyleConfig',
    'PointStyleConfig', 
    'VertexDisplayConfig',
    'SideDisplayConfig',
    'ArcStyleConfig',
    'AngleDisplayConfig',
    'SpecialPointDisplayConfig',
]