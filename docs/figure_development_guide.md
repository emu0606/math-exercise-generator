# 數學測驗生成器 - 圖形生成器開發指南 (新架構版)

本文檔提供了如何在新模組化架構下為數學測驗生成器開發新的圖形生成器的詳細指引。

> 🆕 **Phase 4 更新**：本指南已根據 **Phase 4 Generators 現代化完成** 的經驗更新，整合 Pydantic 參數驗證最佳實踐和新架構工具使用。

## 🏗️ 新架構概述

數學測驗生成器的圖形系統採用 6 層模組化架構：

### 核心架構層次
1. **Generators 層** (`generators/`): 題目生成器，調用圖形渲染功能
2. **Rendering 層** (`utils/rendering/`): 圖形渲染協調和管理
3. **TikZ 層** (`utils/tikz/`): TikZ 代碼生成和座標處理
4. **Geometry 層** (`utils/geometry/`): 數學計算和幾何運算
5. **Core 層** (`utils/core/`): 配置管理、註冊系統、日誌
6. **Base 層**: Python 標準庫和第三方依賴

### 圖形系統組件
1. **`FigureRenderer` 統一接口**：新的圖形渲染統一入口
2. **幾何計算模組**：三角形構造、特殊點計算等
3. **TikZ 渲染器**：座標轉換、弧線渲染、標籤定位
4. **註冊系統**：自動發現和管理生成器
5. **配置管理**：全域配置和環境設定

## 📝 Sphinx 友善的 Docstring 標準

**所有新開發的程式碼必須遵循 Sphinx 友善的 docstring 格式**，以確保 API 文檔的完整性。

### ✅ 標準 Docstring 格式

```python
def example_function(param1: str, param2: int = 10) -> bool:
    """函數的簡短描述（一行內）
    
    詳細描述可以多行，解釋函數的用途、行為和注意事項。
    可以包含使用場景和重要資訊。
    
    Args:
        param1 (str): 第一個參數的描述
        param2 (int, optional): 第二個參數的描述。預設為 10。
        
    Returns:
        bool: 返回值的詳細描述
        
    Raises:
        ValueError: 何時會拋出此異常
        TypeError: 另一種可能的異常
        
    Example:
        >>> result = example_function("test", 5)
        >>> print(result)
        True
        
    Note:
        特殊注意事項或使用限制。
    """
    return True
```

### 🎯 類別 Docstring 範例

```python
class MyFigureGenerator:
    """新圖形生成器類別
    
    這個類別負責生成特定類型的數學圖形，支援多種變體和配置選項。
    使用新的模組化架構，整合了幾何計算和 TikZ 渲染功能。
    
    Attributes:
        name (str): 生成器的唯一識別名稱
        supported_variants (List[str]): 支援的變體類型
        
    Example:
        >>> generator = MyFigureGenerator()
        >>> tikz_code = generator.generate_tikz(params)
        >>> print(tikz_code)
    """
```

## 🔧 開發新的圖形生成器

### 1. 創建生成器類別

在 `generators/` 目錄下創建新的生成器，必須包含完整的 docstring：

### 2. 新架構生成器範例

在 `generators/` 目錄下創建新的生成器，使用新的統一 API：

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 我的新圖形生成器

此模組實現了新架構下的圖形生成器，整合了幾何計算、TikZ 渲染等功能。
使用統一的 utils API 進行數學計算和圖形渲染。
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, validator

# 導入新架構的統一 API
from utils import (
    construct_triangle, get_centroid, tikz_coordinate,
    global_config, get_logger
)
from utils.core.registry import registry
from utils.rendering import FigureRenderer

# 模組日誌器
logger = get_logger(__name__)

class MyFigureParams(BaseModel):
    """我的圖形參數 Pydantic 模型
    
    使用 Phase 4 標準的 Pydantic 進行參數驗證，提供強大的類型檢查和自動驗證。
    參考 Phase 4 中 TrigonometricFunctionGeneratorRadius 的參數驗證最佳實踐。
    
    Attributes:
        side_a (float): 三角形邊長 a
        side_b (float): 三角形邊長 b  
        side_c (float): 三角形邊長 c
        show_centroid (bool): 是否顯示質心
        variant (str): 變體類型 ('question' 或 'explanation')
        
    Example:
        >>> params = MyFigureParams(side_a=3, side_b=4, side_c=5)
        >>> params.side_a
        3.0
        >>> params = MyFigureParams(side_a=-1, side_b=4, side_c=5)  # 會觸發驗證錯誤
    """
    side_a: float = Field(
        default=3.0,
        gt=0,
        le=100.0,
        description="三角形邊長 a，必須大於 0"
    )
    side_b: float = Field(
        default=4.0, 
        gt=0,
        le=100.0,
        description="三角形邊長 b，必須大於 0"
    )
    side_c: float = Field(
        default=5.0,
        gt=0, 
        le=100.0,
        description="三角形邊長 c，必須大於 0"
    )
    show_centroid: bool = Field(
        default=False,
        description="是否顯示質心"
    )
    variant: str = Field(
        default="question",
        description="圖形變體類型"
    )
    
    @validator('variant')
    def validate_variant(cls, v):
        """驗證變體類型"""
        valid_variants = ['question', 'explanation']
        if v not in valid_variants:
            raise ValueError(f"variant 必須是 {valid_variants} 中的一個")
        return v
    
    @validator('side_c')
    def validate_triangle_inequality(cls, v, values):
        """驗證三角形不等式"""
        if 'side_a' in values and 'side_b' in values:
            a, b, c = values['side_a'], values['side_b'], v
            if not (a + b > c and a + c > b and b + c > a):
                raise ValueError(f"邊長 ({a}, {b}, {c}) 不符合三角形不等式")
        return v

class MyFigureGenerator:
    """我的新圖形生成器
    
    使用新架構的統一 API 生成三角形及其特殊點的 TikZ 圖形。
    整合了幾何計算模組和 TikZ 渲染功能。
    
    此生成器展示如何：
    1. 使用統一的幾何 API 進行數學計算
    2. 使用 TikZ 模組進行圖形渲染
    3. 整合配置管理和日誌系統
    4. 支援多種變體和自定義選項
    
    Attributes:
        name (str): 生成器唯一識別名稱
        renderer (FigureRenderer): 圖形渲染器實例
        
    Example:
        >>> generator = MyFigureGenerator()
        >>> params = {'side_a': 3, 'side_b': 4, 'side_c': 5, 'variant': 'question'}
        >>> tikz_code = generator.generate(params)
        >>> print(tikz_code)
    """
    
    def __init__(self):
        """初始化生成器 (Phase 4 標準)
        
        使用新架構核心工具進行初始化，參考 Phase 4 最佳實踐。
        """
        self.name = "my_triangle_figure"
        
        # Phase 4: 新架構日誌系統
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
        self.logger.info(f"{self.name} 圖形生成器初始化完成")
        
        # Phase 4: 新架構配置系統整合
        self.precision = global_config.get('geometry.precision', 6)
        self.backend = global_config.get('geometry.backend', 'python')
        
        self.logger.debug(f"使用數學後端：{self.backend}，精度：{self.precision}")
    
    @classmethod
    def get_name(cls) -> str:
        """獲取生成器唯一識別名稱
        
        Returns:
            str: 生成器名稱，用於註冊系統
        """
        return "my_triangle_figure"
    
    def generate(self, params: Dict[str, Any]) -> str:
        """生成 TikZ 圖形代碼
        
        使用新架構的統一 API 進行幾何計算和圖形渲染。
        
        Args:
            params (Dict[str, Any]): 圖形參數字典
                - side_a (float): 三角形邊長 a
                - side_b (float): 三角形邊長 b
                - side_c (float): 三角形邊長 c
                - show_centroid (bool, optional): 是否顯示質心
                - variant (str, optional): 變體類型
                
        Returns:
            str: TikZ 圖形代碼（不含 tikzpicture 環境）
            
        Raises:
            ValueError: 如果參數無效
            GeometryError: 如果幾何計算失敗
            
        Example:
            >>> generator = MyFigureGenerator()
            >>> params = {'side_a': 3, 'side_b': 4, 'side_c': 5}
            >>> tikz = generator.generate(params)
            >>> '\\draw' in tikz
            True
        """
        self.logger.debug(f"開始生成圖形，參數：{params}")
        
        # Phase 4: 使用 Pydantic 模型進行參數驗證
        figure_params = MyFigureParams(**params)
        
        try:
            # 使用統一幾何 API 構造三角形
            triangle = construct_triangle(
                "sss",
                side_a=figure_params.side_a,
                side_b=figure_params.side_b, 
                side_c=figure_params.side_c
            )
            
            # 生成基礎 TikZ 代碼
            tikz_lines = []
            tikz_lines.append("% 三角形圖形")
            
            # 繪製三角形
            tikz_lines.append(
                f"\\draw {tikz_coordinate(triangle.A)} -- "
                f"{tikz_coordinate(triangle.B)} -- "
                f"{tikz_coordinate(triangle.C)} -- cycle;"
            )
            
            # 標記頂點
            tikz_lines.append(f"\\node[below left] at {tikz_coordinate(triangle.A)} {{A}};")
            tikz_lines.append(f"\\node[below right] at {tikz_coordinate(triangle.B)} {{B}};")
            tikz_lines.append(f"\\node[above] at {tikz_coordinate(triangle.C)} {{C}};")
            
            # 根據變體添加額外內容
            if figure_params.variant == "explanation" or figure_params.show_centroid:
                # 計算並顯示質心
                centroid = get_centroid(triangle)
                tikz_lines.append(
                    f"\\fill[red] {tikz_coordinate(centroid)} circle (2pt);"
                )
                tikz_lines.append(
                    f"\\node[above right, red] at {tikz_coordinate(centroid)} {{G}};"
                )
            
            result = "\n".join(tikz_lines)
            self.logger.info(f"圖形生成成功，代碼長度：{len(result)}")
            return result
            
        except Exception as e:
            self.logger.error(f"圖形生成失敗：{e}")
            raise
    
    def get_supported_variants(self) -> List[str]:
        """獲取支援的變體類型
        
        Returns:
            List[str]: 支援的變體類型列表
        """
        return ["question", "explanation"]
    
    def get_parameter_info(self) -> Dict[str, Any]:
        """獲取參數資訊
        
        提供參數的詳細說明，用於 UI 生成和文檔。
        
        Returns:
            Dict[str, Any]: 參數資訊字典，包含類型、預設值、說明等
        """
        return {
            "side_a": {
                "type": "float",
                "default": 3.0,
                "min": 0.1,
                "max": 100.0,
                "description": "三角形邊長 a"
            },
            "side_b": {
                "type": "float", 
                "default": 4.0,
                "min": 0.1,
                "max": 100.0,
                "description": "三角形邊長 b"
            },
            "side_c": {
                "type": "float",
                "default": 5.0,
                "min": 0.1, 
                "max": 100.0,
                "description": "三角形邊長 c"
            },
            "show_centroid": {
                "type": "bool",
                "default": False,
                "description": "是否顯示質心"
            }
        }

# Phase 4: 圖形生成器使用不同的註冊系統
# 圖形生成器使用 @register_figure_generator 裝飾器
# (與 QuestionGenerator 的 @register_generator 不同)

logger.debug(f"圖形生成器定義完成：{MyFigureGenerator.get_name()}")
```

### 3. Phase 4 圖形生成器註冊系統

圖形生成器有其獨立的註冊系統，與題目生成器不同：

```python
# 圖形生成器的註冊方式 (與題目生成器不同)
from figures import register_figure_generator

@register_figure_generator
class MyFigureGenerator:
    """圖形生成器使用專門的註冊裝飾器"""
    
    @classmethod
    def get_name(cls) -> str:
        return "my_triangle_figure"
    
    def generate_tikz(self, params: Dict[str, Any]) -> str:
        # Phase 4: 使用 Pydantic 參數驗證
        validated_params = MyFigureParams(**params)
        # 圖形生成邏輯...
        return tikz_code

# 在 figures/__init__.py 中導入
from .my_new_figure import MyFigureGenerator
```

### Phase 4 圖形系統與題目系統的差異

| 特徵 | 題目生成器 | 圖形生成器 |
|------|-----------|-----------|
| **基類** | QuestionGenerator | 無特定基類 |  
| **註冊裝飾器** | @register_generator | @register_figure_generator |
| **主要方法** | generate_question() | generate_tikz() |
| **參數驗證** | Pydantic 模型 | Pydantic 模型 |
| **註冊系統** | 統一註冊系統 | 圖形專用註冊系統 |

## 🎯 新架構整合模式

### 使用統一幾何 API

新架構提供統一的幾何計算接口：

```python
from utils import (
    construct_triangle,      # 三角形構造
    get_centroid,           # 質心計算
    get_incenter,           # 內心計算
    distance,               # 距離計算
    area_of_triangle,       # 面積計算
    tikz_coordinate,        # 座標轉換
    Point, Triangle         # 數據類型
)

# 構造三角形
triangle = construct_triangle("sss", side_a=3, side_b=4, side_c=5)

# 計算特殊點
centroid = get_centroid(triangle)
incenter = get_incenter(triangle)

# 生成 TikZ 座標
coord_a = tikz_coordinate(triangle.A)  # 結果: (0.0,0.0)
```

### 使用配置和日誌系統

```python
from utils.core import global_config, get_logger

# 獲取模組日誌器
logger = get_logger(__name__)

# 存取全域配置
config = global_config
precision = config.get('geometry.precision', 6)
backend = config.get('geometry.backend', 'python')

logger.info(f"使用數學後端: {backend}，精度: {precision}")
```

### 整合渲染系統

```python
from utils.rendering import FigureRenderer

class MyAdvancedGenerator:
    """進階圖形生成器
    
    展示如何使用渲染系統創建複雜圖形。
    """
    
    def __init__(self):
        """初始化渲染器"""
        self.renderer = FigureRenderer()
    
    def generate_complex_figure(self, params: Dict[str, Any]) -> str:
        """生成複雜圖形
        
        使用渲染器協調多個圖形元素的生成。
        
        Args:
            params: 圖形參數
            
        Returns:
            str: 完整的 TikZ 代碼
        """
        # 使用渲染器生成複合圖形
        return self.renderer.render_composite_figure([
            {'type': 'triangle', 'params': {...}},
            {'type': 'circle', 'params': {...}},
            {'type': 'label', 'params': {...}}
        ])
```

### 1. 創建參數模型

首先，在 `figures/params_models.py` 中定義新的預定義複合圖形參數模型：

```python
class MyPredefinedCompositeParams(BaseFigureParams):
    """我的預定義複合圖形參數模型"""
    param1: float = 1.0
    param2: str = 'default'
    # 其他參數...
```

### 2. 創建生成器類

創建一個新的 Python 文件（例如 `figures/predefined/my_predefined.py`），實現一個繼承自 `FigureGenerator` 的生成器類：

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 我的預定義複合圖形生成器
"""

from typing import Dict, Any, List
from pydantic import ValidationError

from ..base import FigureGenerator
from ..params_models import MyPredefinedCompositeParams, CompositeParams, SubFigureParams, AbsolutePosition
from .. import register_figure_generator, get_figure_generator

@register_figure_generator
class MyPredefinedCompositeGenerator(FigureGenerator):
    """我的預定義複合圖形生成器
    
    [簡短描述]
    """
    
    @classmethod
    def get_name(cls) -> str:
        """獲取圖形類型唯一標識符"""
        return 'my_predefined_composite'
    
    def generate_tikz(self, params: Dict[str, Any]) -> str:
        """生成 TikZ 圖形內容
        
        Args:
            params: 圖形參數字典，應符合 MyPredefinedCompositeParams 模型
            
        Returns:
            TikZ 圖形內容（不包含 tikzpicture 環境）
            
        Raises:
            ValidationError: 如果參數驗證失敗
        """
        # 使用 Pydantic 模型驗證參數
        try:
            validated_params = MyPredefinedCompositeParams(**params)
        except ValidationError as e:
            raise ValidationError(f"參數驗證失敗: {str(e)}", e.raw_errors)
        
        # 構建 CompositeParams 實例
        composite_params = self._build_composite_params(validated_params)
        
        # 獲取 CompositeFigureGenerator 實例
        composite_generator = get_figure_generator('composite')()
        
        # 使用 CompositeFigureGenerator 生成 TikZ 代碼
        return composite_generator.generate_tikz(composite_params.dict())
    
    def _build_composite_params(self, params: MyPredefinedCompositeParams) -> CompositeParams:
        """構建 CompositeParams 實例
        
        Args:
            params: 驗證後的 MyPredefinedCompositeParams 實例
            
        Returns:
            CompositeParams 實例
        """
        # 提取參數
        param1 = params.param1
        param2 = params.param2
        variant = params.variant
        
        # 創建子圖形列表
        sub_figures: List[SubFigureParams] = []
        
        # 添加第一個子圖形
        sub_figures.append(
            SubFigureParams(
                id="figure1",
                type="circle",
                params={
                    "radius": param1,
                    "center_x": 0,
                    "center_y": 0,
                    "variant": variant
                },
                position=AbsolutePosition(x=0, y=0)
            )
        )
        
        # 添加第二個子圖形
        sub_figures.append(
            SubFigureParams(
                id="figure2",
                type="label",
                params={
                    "x": 0,
                    "y": 0,
                    "text": param2,
                    "variant": variant
                },
                position=AbsolutePosition(x=0, y=0)
            )
        )
        
        # 創建 CompositeParams 實例
        return CompositeParams(
            variant=variant,
            sub_figures=sub_figures
        )
```

### 3. 更新 `figures/__init__.py`

在 `figures/__init__.py` 中導入新的生成器類：

```python
# 預定義複合圖形生成器
from .predefined.my_predefined import MyPredefinedCompositeGenerator
```

## 處理命名空間衝突

在複合圖形中，可能會出現命名空間衝突，例如多個子圖形使用相同的節點名稱。`CompositeFigureGenerator` 通過以下方式處理這個問題：

1. 為每個子圖形分配一個唯一的前綴（例如 `sf0_`, `sf1_` 等）。
2. 在子圖形的 TikZ 代碼中，將所有命名（如 `\coordinate`, `\node`, `\path` 等）替換為帶前綴的版本。
3. 使用 TikZ 的 `scope` 環境隔離每個子圖形。

開發者不需要手動處理這些問題，只需確保每個基礎圖形生成器生成的 TikZ 代碼使用標準的命名方式。

## 處理定位

複合圖形中的子圖形可以使用絕對定位或相對定位：

### 絕對定位

```python
'position': {
    'mode': 'absolute',
    'x': 0,
    'y': 0,
    'anchor': 'center'  # 子圖形的哪個錨點對齊到 (x, y)
}
```

### 相對定位

```python
'position': {
    'mode': 'relative',
    'relative_to': 'figure1',  # 相對於哪個子圖形的 id
    'placement': 'right',      # 放置方向
    'distance': '1cm',         # 距離
    'my_anchor': 'center',     # 當前子圖形用於對齊的錨點
    'target_anchor': 'east'    # 相對目標用於對齊的錨點
}
```

## 測試新的圖形生成器

創建一個測試文件來測試新的圖形生成器：

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
測試我的新圖形生成器
"""

import unittest
from figures import get_figure_generator

class TestMyNewFigureGenerator(unittest.TestCase):
    """測試我的新圖形生成器"""
    
    def setUp(self):
        """設置測試環境"""
        self.generator_cls = get_figure_generator('my_new_figure')
        self.generator = self.generator_cls()
    
    def test_generate_tikz(self):
        """測試生成 TikZ 代碼"""
        params = {
            'variant': 'question',
            'param1': 1.0,
            'param2': 'test',
            'param3': True
        }
        
        tikz_content = self.generator.generate_tikz(params)
        
        # 檢查 TikZ 代碼是否包含預期的內容
        self.assertIn('circle', tikz_content)
        self.assertIn('1.0', tikz_content)
        
        # 測試詳解變體
        params['variant'] = 'explanation'
        tikz_content = self.generator.generate_tikz(params)
        
        self.assertIn('red', tikz_content)
        self.assertIn('test', tikz_content)

if __name__ == "__main__":
    unittest.main()
```

## ✅ 新架構最佳實踐

### 1. **必須遵循 Sphinx Docstring 標準**
- 所有函數、類別、模組必須包含完整 docstring
- 使用 Google Style 格式 (`Args:`, `Returns:`, `Raises:`)
- 包含使用範例和重要注意事項
- 確保 `sphinx-build` 能自動生成 API 文檔

### 2. **統一 API 使用**
- 優先使用 `utils` 統一入口導入功能
- 遵循新的模組化架構，避免直接導入內部模組
- 使用統一的數據類型 (`Point`, `Triangle`, `Circle`)

### 3. **配置和日誌整合**
- 使用 `utils.core.global_config` 獲取配置
- 使用 `utils.core.get_logger(__name__)` 獲取日誌器
- 記錄重要操作和錯誤資訊

### 4. **錯誤處理和驗證**
- 使用 dataclass 或自定義類別進行參數驗證
- 提供清晰的錯誤訊息和異常類型
- 包含參數範圍檢查和邏輯驗證

### 5. **變體支援**
- 支援 `question` 和 `explanation` 變體
- 詳解變體提供更豐富的視覺資訊
- 可擴展支援自定義變體類型

### 6. **測試驅動開發**
- 為每個生成器編寫完整單元測試
- 使用 `pytest` 框架和 fixture
- 測試各種參數組合和邊界情況

### 7. **效能考量**
- 避免重複計算，快取中間結果
- 使用適當的數學後端 (numpy/sympy/python)
- 記錄生成時間和效能指標

### 8. **圖形尺寸控制**
- 生成器負責圖形的**相對比例**和**內容結構**
- **絕對尺寸**由 LaTeX 生成器的 `\resizebox` 統一控制
- 支援 `scale` 參數調整內部比例
- 不直接處理 `width`、`height` 等絕對尺寸參數

## 📚 參考資源和範例

### 新架構範例文件
- 幾何計算範例：`utils/geometry/triangle_construction.py`
- TikZ 渲染範例：`utils/tikz/coordinate_transform.py`
- 統一 API 使用：`utils/__init__.py`
- 生成器註冊：`utils/core/registry.py`

### 測試範例
- 幾何功能測試：`tests/test_utils/test_geometry/`
- TikZ 功能測試：`tests/test_utils/test_tikz/`
- 整合測試：`tests/test_integration/`

### 文檔資源
- API 文檔：`docs/build/html/api/` (執行 `make html` 生成)
- 架構指南：`docs/source/guides/architecture.rst`
- 快速開始：`docs/source/guides/quickstart.rst`
- 工作流程：`docs/workflow.md`

### 開發工具
- 編碼檢查：`tools/check_encoding.py`
- 視覺化工具：`tools/dev_visualizer.py`
- 批次修復：`tools/batch_fix_tikz.py`

---

## 🚀 快速開始檢查清單

創建新生成器時，確保完成以下項目：

- [ ] **完整 Sphinx Docstring** - 所有函數和類別
- [ ] **統一 API 導入** - 使用 `from utils import ...`
- [ ] **參數驗證** - 使用 dataclass 或自定義驗證
- [ ] **日誌整合** - 使用 `get_logger(__name__)`
- [ ] **註冊系統** - 使用 `registry.register_generator()`
- [ ] **變體支援** - 實現 question/explanation 變體
- [ ] **單元測試** - pytest 測試文件
- [ ] **範例代碼** - docstring 中的使用範例
- [ ] **錯誤處理** - 適當的異常類型和訊息

完成開發後執行：
```bash
# Phase 4 驗證命令

# 1. 檢查圖形生成器註冊
py -c "from figures import get_figure_generator; print('✅ 圖形生成器註冊系統正常')"

# 2. 測試圖形生成功能  
py -c "from figures import get_figure_generator; gen = get_figure_generator('my_triangle_figure')(); print('✅ 圖形生成器運行正常')"

# 3. 檢查 Pydantic 參數驗證
py -c "from my_figure_module import MyFigureParams; p = MyFigureParams(side_a=3, side_b=4, side_c=5); print('✅ Pydantic 驗證正常')"

# 4. 執行測試
py -m pytest tests/test_figures/ -v

# 5. 檢查新架構工具整合
py -c "from utils import get_logger, global_config; print('✅ 新架構工具正常')"
```

## 📋 **長期維護計劃**

### **🔄 定期更新任務**

1. **圖形系統與題目系統同步** (每季度)
   - 確保圖形生成器的 Pydantic 參數驗證與題目生成器保持一致
   - 檢查註冊系統差異是否需要統一
   - 驗證所有範例代碼可正常執行

2. **實用性和準確性維護** (持續進行)
   - 收集開發者對圖形開發工具的反饋
   - 改善範例代碼的實用性，提供更多實際可運行的小範例
   - 新增常見圖形開發錯誤的除錯指南

3. **新功能和最佳實踐整合** (隨新功能發布)
   - 當 Phase 4 引入新的圖形渲染特性時，及時更新指南
   - 整合新的 Pydantic 特性和圖形參數驗證最佳實踐
   - 更新測試和驗證流程

### **🎯 改善優先順序**

**高優先級**：
- 保持圖形註冊系統範例的準確性 (@register_figure_generator)
- 確保 Pydantic 參數驗證範例可運行
- 維護新架構工具導入的正確性 (utils API)

**中優先級**：
- 擴展實際可運行的圖形生成範例
- 改善 TikZ 代碼生成的測試指導
- 新增圖形效能優化建議

**低優先級**：
- 美化文檔排版和圖表展示
- 新增更多複雜圖形組合的使用場景
- 建立圖形系統的視覺化架構圖

### **🔧 圖形系統特有維護項目**

1. **圖形註冊系統一致性**
   - 監控圖形生成器註冊機制是否與題目生成器統一
   - 評估是否需要將 @register_figure_generator 遷移到統一系統

2. **TikZ 代碼品質**
   - 檢查生成的 TikZ 代碼範例是否符合最新 LaTeX 標準
   - 驗證幾何計算 API 的使用是否正確

3. **Pydantic 參數模型最佳實踐**
   - 確保圖形參數驗證遵循 Phase 4 建立的最佳實踐
   - 維護參數驗證器的數學正確性

### **📞 維護聯絡**

當發現文檔問題時：
1. 優先檢查是否為圖形系統代碼變更導致
2. 參考最新的 figures/ 目錄實際代碼
3. 確保修正後的範例可以生成正確的 TikZ 代碼
4. 特別注意圖形註冊系統與題目註冊系統的差異