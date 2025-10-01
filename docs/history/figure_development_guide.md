# 數學測驗生成器 - 圖形生成器開發指南 (過期版本)

> ⚠️ **此版本已過期** (2025-09-28)：本文檔保留作為歷史參考，新版本正在重構中。
> 新版本將簡化結構，移除混淆術語，並更清楚說明圖形生成器在數學測驗系統中的角色。

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

## 🎆 **5分鐘快速入門** - 必讀！

在深入研究之前，先讓我們用 5 分鐘建立一個最簡單的圖形生成器：

### 🚀 **Hello World 圖形生成器**

在 `figures/` 目錄下創建 `my_first_figure.py`：

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
我的第一個圖形生成器 - Hello World
"""

from typing import Dict, Any
from .base import FigureGenerator
from . import register_figure_generator

@register_figure_generator
class MyFirstFigureGenerator(FigureGenerator):
    """最簡單的圖形生成器 - 繪製一個簡單的圓形"""

    @classmethod
    def get_name(cls) -> str:
        return "my_first_figure"

    def generate_tikz(self, params: Dict[str, Any]) -> str:
        # 獲取參數，設定預設值
        radius = params.get('radius', 1.0)
        color = params.get('color', 'blue')

        # 生成 TikZ 代碼
        return f"\\draw[{color}] (0,0) circle ({radius});"
```

### 🎩 **立即測試**

```python
# 在專案根目錄執行
py -c "
from figures import get_figure_generator
gen = get_figure_generator('my_first_figure')()
print(gen.generate_tikz({'radius': 2, 'color': 'red'}))
"

# 輸出： \draw[red] (0,0) circle (2);
```

**恩喜您！您已經成功創建了第一個圖形生成器！** 🎉

---

## 🔧 開發進階圖形生成器

### 1. 創建完整功能的生成器

為了建立具備完整功能的生成器，我們需要：

### 2. 使用 Pydantic 參數驗證的進階範例

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
我的進階圖形生成器 - 使用 Pydantic 參數驗證
"""

from typing import Dict, Any
from pydantic import BaseModel, Field, validator
from utils import construct_triangle, get_centroid, Point, get_logger
from .base import FigureGenerator
from . import register_figure_generator

logger = get_logger(__name__)

class TriangleParams(BaseModel):
    """三角形參數模型"""
    side_a: float = Field(default=3.0, gt=0, description="邊長 a")
    side_b: float = Field(default=4.0, gt=0, description="邊長 b")
    side_c: float = Field(default=5.0, gt=0, description="邊長 c")
    show_centroid: bool = Field(default=False, description="顯示質心")

    @validator('side_c')
    def validate_triangle(cls, v, values):
        if 'side_a' in values and 'side_b' in values:
            a, b, c = values['side_a'], values['side_b'], v
            if not (a + b > c and a + c > b and b + c > a):
                raise ValueError("邊長不符合三角形不等式")
        return v

@register_figure_generator
class MyTriangleGenerator(FigureGenerator):
    """進階三角形生成器 - 使用 Pydantic 驗證和新架構 API"""

    @classmethod
    def get_name(cls) -> str:
        return "my_triangle"

    def generate_tikz(self, params: Dict[str, Any]) -> str:
        # 使用 Pydantic 驗證參數
        validated = TriangleParams(**params)

        # 使用新架構 API 構造三角形
        triangle = construct_triangle(
            "sss",
            side_a=validated.side_a,
            side_b=validated.side_b,
            side_c=validated.side_c
        )

        # 生成 TikZ 代碼
        tikz_parts = [
            f"\\draw {triangle.A.to_tikz()} -- {triangle.B.to_tikz()} -- {triangle.C.to_tikz()} -- cycle;",
            f"\\node[below] at {triangle.A.to_tikz()} {{A}};",
            f"\\node[below] at {triangle.B.to_tikz()} {{B}};",
            f"\\node[above] at {triangle.C.to_tikz()} {{C}};"
        ]

        # 選擇性添加質心
        if validated.show_centroid:
            centroid = get_centroid(triangle)
            tikz_parts.extend([
                f"\\fill[red] {centroid.to_tikz()} circle (2pt);",
                f"\\node[above, red] at {centroid.to_tikz()} {{G}};"
            ])

        return "\n".join(tikz_parts)
```

### 🎩 **測試進階生成器**

```python
from figures import get_figure_generator
gen = get_figure_generator('my_triangle')()
print(gen.generate_tikz({
    'side_a': 3, 'side_b': 4, 'side_c': 5,
    'show_centroid': True
}))
```

**完成！您現在已經掌握了使用 Pydantic 驗證和新架構 API 的進階技巧。**
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
    Point, Triangle         # 數據類型 (Point.to_tikz()用於座標轉換)
)

# 構造三角形
triangle = construct_triangle("sss", side_a=3, side_b=4, side_c=5)

# 計算特殊點
centroid = get_centroid(triangle)
incenter = get_incenter(triangle)

# 生成 TikZ 座標 (使用Point類的to_tikz方法)
coord_a = triangle.A.to_tikz()  # 結果: "(0.0, 0.0)"
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

首先，在 `figures/params/` 目錄下定義新的預定義複合圖形參數模型。

**推薦方式**: 在合適的參數模組中添加參數類，例如 `figures/params/shapes.py`：

```python
class MyPredefinedCompositeParams(BaseFigureParams):
    """我的預定義複合圖形參數模型"""
    param1: float = 1.0
    param2: str = 'default'
    # 其他參數...
```

然後在 `figures/params/__init__.py` 中導出：

```python
from .shapes import MyPredefinedCompositeParams
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
from ..params import MyPredefinedCompositeParams, CompositeParams, SubFigureParams, AbsolutePosition
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

## 🚀 **快速開始檢查清單**

### ✅ **基礎檢查清單** (必做)
- [ ] 使用 `@register_figure_generator` 註冊
- [ ] 實現 `get_name()` 和 `generate_tikz()` 方法
- [ ] 測試基本功能正常

### 🎆 **進階檢查清單** (可選)
- [ ] 使用 Pydantic 參數驗證
- [ ] 整合新架構 `utils` API
- [ ] 編寫單元測試

### 🎉 **完成開發後執行**：
```bash
# 基礎驗證
py -c "from figures import get_figure_generator; print('✅ 圖形系統正常')"

# (可選) 完整測試
py -m pytest tests/test_utils/test_geometry/ -q
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