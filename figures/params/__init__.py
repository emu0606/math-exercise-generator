"""圖形參數模型統一接口

本模組提供所有圖形生成器所需的參數模型，採用模組化設計
以提高可維護性和可擴展性。

模組結構：
- types: 基礎類型定義
- base: 基礎參數類別  
- geometry: 基礎幾何圖形參數
- shapes: 標準幾何形狀參數
- triangle: 三角形專用參數（包含複雜的高級配置）
- styles: 樣式和顯示相關參數
- composite: 複合圖形參數

Example:
    >>> # 基礎使用
    >>> from figures.params import PointParams, CircleParams
    >>> point = PointParams(x=1, y=2, variant="question")
    
    >>> # 向後兼容 (舊代碼仍然可用)
    >>> from figures.params_models import BasicTriangleParams
    
    >>> # 新模組化方式 (推薦)
    >>> from figures.params.triangle import BasicTriangleParams
    >>> from figures.params.geometry import PointParams

Note:
    本模組重構自原本 562 行的單一文件，現已模組化為
    清晰的職責分離結構，同時保持完整的向後兼容性。
"""

# 目前在重構過程中，先創建空的導出接口
# 隨著重構進行，將逐步添加各模組的導出

__all__ = []

# TODO: 重構完成後將添加以下導出
# from .types import *
# from .base import *
# from .geometry import *
# from .shapes import *
# from .composite import *
# from .triangle import *
# from .styles import *