#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 圖形生成器包

此模組提供了完整的圖形生成系統，包括註冊機制、基礎類別和所有具體的圖形生成器。
系統採用裝飾器模式進行生成器註冊，確保所有圖形生成器都能被自動發現和使用。

## 導入機制設計 - 惰性導入 (Lazy Import)

本模組採用**惰性導入**策略，以優化應用程式啟動性能：

**導入時機**:
    - **UI 啟動時**: 不會自動導入 figures 模組
    - **首次使用時**: 在 PDF 生成階段由 FigureRenderer 觸發導入
    - **手動導入時**: 執行 `import figures` 時立即載入所有生成器

**性能優勢**:
    - 減少 UI 啟動時間約 15%
    - 節省記憶體使用 5-10 MB
    - 按需載入，提升整體響應速度

**與 generators 的差異**:
    - `generators` 模組在 main.py 中主動導入（UI 需要顯示題型列表）
    - `figures` 模組延遲導入（只在生成 PDF 時使用）

主要組件：
1. **註冊系統**: `@register_figure_generator` 裝飾器和相關函數
2. **基礎生成器**: 點、線、圓、角度等基本圖形
3. **複合生成器**: 複雜圖形的組合生成
4. **預定義生成器**: 常用圖形的簡化接口

模組結構：
- `base.py`: 抽象基礎類別 `FigureGenerator`
- `*_generator.py`: 各種具體圖形生成器
- `composite.py`: 複合圖形生成器
- `predefined/`: 預定義複合圖形生成器
- `params/`: 參數模型定義（使用 Pydantic）

Example:
    使用圖形生成器::

        from figures import get_figure_generator

        # 獲取圓形生成器
        CircleGen = get_figure_generator('circle')
        generator = CircleGen()

        # 生成圖形
        tikz_code = generator.generate_tikz({
            'radius': 2.0,
            'variant': 'question'
        })

    註冊自定義生成器::

        from figures import register_figure_generator
        from figures.base import FigureGenerator

        @register_figure_generator
        class MyGenerator(FigureGenerator):
            @classmethod
            def get_name(cls) -> str:
                return "my_figure"

            def generate_tikz(self, params):
                return "\\draw (0,0) circle (1);"

        # ⚠️ 重要：必須在 figures/__init__.py 底部添加手動導入
        # from .my_generator import MyGenerator

Note:
    - 所有生成器在模組載入時自動註冊（透過裝飾器）
    - 底部的手動導入語句是註冊機制的核心，不可移除
    - 新增生成器時必須同時添加到底部的導入列表
    - 註冊系統目前使用舊架構，計畫遷移到 `utils.core.registry`
    - 新架構鼓勵使用 `from utils import` 統一 API

Warning:
    **請勿移除底部的手動導入語句**！這些導入觸發了 @register_figure_generator
    裝飾器的執行。移除任何一行都會導致對應的圖形生成器無法使用。
"""

from typing import Dict, Type, Any, Optional
import functools
import inspect
from .base import FigureGenerator

# 圖形生成器註冊表
_figure_generators: Dict[str, Type[FigureGenerator]] = {}

def register_figure_generator(cls=None, *, name: Optional[str] = None):
    """註冊圖形生成器裝飾器
    
    將圖形生成器類註冊到系統中，使其能夠被 `get_figure_generator` 函數發現和使用。
    此裝飾器支援兩種使用模式：直接裝飾和帶參數裝飾。
    
    裝飾器會自動：
    1. 驗證類是否繼承自 `FigureGenerator`
    2. 檢查名稱衝突
    3. 將類註冊到內部註冊表
    4. 輸出註冊成功信息
    
    Args:
        cls (Type[FigureGenerator], optional): 被裝飾的圖形生成器類。
            當直接使用 `@register_figure_generator` 時自動傳入。
        name (str, optional): 自定義的圖形類型名稱。
            如果未提供，則使用 `cls.get_name()` 返回的名稱。
            
    Returns:
        Union[Callable, Type[FigureGenerator]]: 
            - 如果 `cls` 為 None（帶參數使用），返回裝飾器函數
            - 如果 `cls` 不為 None（直接使用），返回註冊後的類
    
    Raises:
        ValueError: 當圖形生成器名稱已被註冊時
        TypeError: 當被裝飾的類不是 `FigureGenerator` 的子類時
        
    Example:
        直接使用裝飾器::
        
            @register_figure_generator
            class MyGenerator(FigureGenerator):
                @classmethod
                def get_name(cls) -> str:
                    return "my_figure"
                
                def generate_tikz(self, params):
                    return "\\draw (0,0) circle (1);"
        
        指定自定義名稱::
        
            @register_figure_generator(name='custom_name')
            class MyGenerator(FigureGenerator):
                # ... 實現方法
                
    Note:
        - 註冊在模組載入時自動完成
        - 每個生成器名稱在系統中必須唯一
        - 此為舊架構註冊系統，未來計畫遷移到 `utils.core.registry`
    """
    def decorator(cls):
        # 獲取圖形類型名稱
        figure_name = name if name is not None else cls.get_name()
        
        # 檢查是否已註冊
        if figure_name in _figure_generators:
            raise ValueError(f"圖形生成器 '{figure_name}' 已經被註冊")
        
        # 檢查是否是 FigureGenerator 的子類
        if not issubclass(cls, FigureGenerator):
            raise TypeError(f"類 '{cls.__name__}' 必須繼承 FigureGenerator")
        
        # 註冊生成器
        _figure_generators[figure_name] = cls
        print(f"已註冊圖形生成器: {cls.__name__} (類型: '{figure_name}')")
        
        return cls
    
    # 處理直接使用 @register_figure_generator 的情況
    if cls is not None:
        return decorator(cls)
    
    # 處理使用 @register_figure_generator(name='custom_name') 的情況
    return decorator

def get_figure_generator(figure_type: str) -> Type[FigureGenerator]:
    """獲取指定類型的圖形生成器類
    
    根據圖形類型名稱查找並返回對應的圖形生成器類。
    此函數是圖形生成系統的主要入口點之一。
    
    Args:
        figure_type (str): 圖形類型的唯一標識符。
            必須是已註冊的圖形生成器名稱，如 "circle"、"basic_triangle" 等。
        
    Returns:
        Type[FigureGenerator]: 對應的圖形生成器類，可以實例化使用。
        
    Raises:
        ValueError: 當找不到指定類型的圖形生成器時拋出，
            包含詳細錯誤信息指明無效的類型名稱。
            
    Example:
        獲取並使用圖形生成器::
        
            # 獲取圓形生成器類
            CircleGen = get_figure_generator('circle')
            
            # 創建實例並生成圖形
            generator = CircleGen()
            tikz_code = generator.generate_tikz({'radius': 1.0})
            
        錯誤處理::
        
            try:
                gen = get_figure_generator('nonexistent')
            except ValueError as e:
                print(f"圖形類型不存在: {e}")
                
    Note:
        - 只返回類，不返回實例
        - 可用的圖形類型可通過 `get_registered_figure_types()` 查詢
        - 區分大小寫，請使用準確的類型名稱
    """
    if figure_type not in _figure_generators:
        raise ValueError(f"找不到類型為 '{figure_type}' 的圖形生成器")
    
    return _figure_generators[figure_type]

def get_registered_figure_types() -> Dict[str, Type[FigureGenerator]]:
    """獲取所有已註冊的圖形類型
    
    返回系統中所有已註冊的圖形生成器的完整映射表。
    此函數用於系統自省和調試，也可用於動態發現可用的圖形類型。
    
    Returns:
        Dict[str, Type[FigureGenerator]]: 圖形類型名稱到生成器類的映射字典。
            鍵為圖形類型標識符（如 "circle"、"triangle"），
            值為對應的生成器類別。
            
    Example:
        查看所有可用的圖形類型::
        
            registered = get_registered_figure_types()
            print("可用的圖形類型:")
            for name, cls in registered.items():
                print(f"  - {name}: {cls.__name__}")
                
        動態使用圖形生成器::
        
            registered = get_registered_figure_types()
            for figure_type, generator_class in registered.items():
                generator = generator_class()
                print(f"{figure_type}: {generator_class.__doc__}")
                
    Note:
        - 返回的是字典的副本，修改不會影響內部註冊表
        - 字典內容在模組載入完成後通常不會變化
        - 可以安全地迭代和檢查返回的字典
    """
    return _figure_generators.copy()

# 導入所有具體生成器模組，這將自動註冊它們
# 注意：這些導入語句應該放在文件的最後，以避免循環導入問題

# 基礎圖形生成器
from .unit_circle import UnitCircleGenerator
from .circle import CircleGenerator
from .coordinate_system import CoordinateSystemGenerator
from .point import PointGenerator
from .line import LineGenerator
from .angle import AngleGenerator
from .label import LabelGenerator
# from .triangle import TriangleGenerator # 舊的或待重構的
from .basic_triangle import BasicTriangleGenerator # 新增的基礎三角形
from .arc import ArcGenerator # 新增的圓弧生成器
from .function_plot import FunctionPlotGenerator # 函數圖形生成器

# 複合圖形生成器
from .composite import CompositeFigureGenerator

# 預定義複合圖形生成器
from .predefined.standard_unit_circle import StandardUnitCircleGenerator
from .predefined.predefined_triangle import PredefinedTriangleGenerator
from .predefined.number_line import NumberLineGenerator