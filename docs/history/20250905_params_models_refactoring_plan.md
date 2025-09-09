# 20250905 - params_models.py 緊急重構計畫

> **文檔類型**: 歷史檔案 - 重構工作計畫  
> **創建時間**: 2025-09-05  
> **執行期間**: 2025-09-05 ~ 2025-09-07  
> **目標**: 將 562 行的 params_models.py 重構為模組化架構  
> **狀態**: ✅ **已完成** (Day 1-4 全部完成)  
> **歸檔原因**: 重構工作圓滿完成，作為歷史記錄保存  

## 🚨 問題分析

### 📊 當前狀態
- **文件大小**: 562 行單一文件
- **主要問題**: 
  - 162 行的 `PredefinedTriangleParams` 巨型類別
  - 所有參數模型集中在單一文件
  - 維護困難，可讀性差
  - 違反單一職責原則

### 💣 最大痛點
**PredefinedTriangleParams**: 162 行的參數怪物，包含過多職責和複雜邏輯

## 🏗️ 重構策略

### 新架構設計
```
figures/
├── params/
│   ├── __init__.py          # 統一導出接口
│   ├── types.py            # 基礎類型定義
│   ├── base.py             # 基礎參數類
│   ├── geometry.py         # 基礎幾何圖形參數
│   ├── shapes.py           # 標準形狀參數
│   ├── composite.py        # 複合圖形參數
│   ├── triangle/
│   │   ├── __init__.py
│   │   ├── basic.py        # BasicTriangleParams
│   │   └── advanced.py     # PredefinedTriangleParams (162行怪物隔離區)
│   └── styles/
│       ├── __init__.py
│       ├── labels.py       # 標籤樣式參數
│       └── display.py      # 顯示配置參數
```

### 🎯 重構原則
1. **單一職責**: 每個文件負責一類參數
2. **模組化**: 清晰的邏輯分組
3. **向後兼容**: 暫時保持現有導入接口
4. **漸進式**: 分步驗證，降低風險
5. **文檔同步**: 重構時同步添加 Sphinx docstring，確保項目一致性

## 📅 詳細實施計畫 (4 天)

### Day 1: 基礎架構建立 + 核心文檔

#### Morning (4 小時): 目錄結構與框架
##### Task 1.1: 創建目錄結構
```bash
mkdir figures/params
mkdir figures/params/triangle
mkdir figures/params/styles
```

##### Task 1.2: 創建基礎文件框架
- [ ] `figures/params/__init__.py` - 統一導出接口 + 模組 docstring
- [ ] `figures/params/types.py` - 基礎類型定義框架
- [ ] `figures/params/base.py` - 基礎參數類框架
- [ ] 所有子目錄的 `__init__.py` 文件

#### Afternoon (4 小時): 基礎類型 + Sphinx 文檔
##### Task 1.3: 提取基礎類型定義 + Sphinx
**目標文件**: `figures/params/types.py`
```python
"""Pydantic 參數模型基礎類型定義

提供所有參數模型使用的通用類型定義，包含 TikZ 相關的
錨點、位置修飾符和基礎數據類型。

Example:
    >>> from figures.params.types import PointTuple, TikzAnchor
    >>> point: PointTuple = (1.0, 2.0)
    >>> anchor: TikzAnchor = "north"
"""

from typing import Literal, Tuple, Union, Optional

TikzAnchor = Literal[
    "north", "south", "east", "west",
    "north east", "north west", 
    "south east", "south west", "center"
]
"""TikZ 錨點類型定義，用於指定節點的錨定位置"""

TikzPlacement = Literal[
    "above", "below", "left", "right",
    "above left", "above right",
    "below left", "below right"
]
"""TikZ 相對位置類型，用於標籤和元素的相對定位"""

PointTuple = Tuple[Union[int, float], Union[int, float]]
"""二維點座標類型，表示 (x, y) 座標對"""
```

##### Task 1.4: 提取基礎參數類 + Sphinx
**目標文件**: `figures/params/base.py`
```python
"""參數模型基礎類別

定義所有圖形參數的基礎類別和通用功能，提供統一的
參數驗證和處理機制。
"""

from pydantic import BaseModel
from .types import PointTuple, TikzAnchor

class BaseFigureParams(BaseModel):
    """所有圖形參數的抽象基類
    
    提供通用的圖形參數接口，包含變體類型和基礎驗證邏輯。
    所有具體的圖形參數類別都應繼承此基類。
    
    Attributes:
        variant (str): 圖形變體類型，通常為 "question" 或 "explanation"
        
    Example:
        >>> class MyParams(BaseFigureParams):
        ...     value: float = 1.0
        >>> params = MyParams(variant="question")
    """
```

### Day 2: 幾何與形狀參數分離 + Sphinx

#### Morning (4 小時): 基礎幾何參數
##### Task 2.1: 分離基礎幾何參數 + Sphinx
**目標文件**: `figures/params/geometry.py`
```python
"""基礎幾何圖形參數模型

包含點、線、角等基本幾何元素的參數定義，提供幾何圖形
生成所需的所有配置選項。

Example:
    >>> params = PointParams(x=1.0, y=2.0, variant="question")
    >>> line_params = LineParams(p1=(0,0), p2=(1,1), variant="question")
"""

class PointParams(BaseFigureParams):
    """點生成器參數
    
    定義二維平面上點的位置和顯示屬性。
    
    Args:
        x (float): X 座標
        y (float): Y 座標
        marker_style (str, optional): 點標記樣式
        
    Example:
        >>> params = PointParams(x=1.0, y=2.0, variant="question")
    """
```

##### Task 2.2: 分離標準形狀參數 + Sphinx
**目標文件**: `figures/params/shapes.py`
```python
"""標準幾何形狀參數模型

包含圓形、圓弧、座標系統等標準幾何形狀的參數定義，
提供豐富的自定義選項和樣式配置。
"""

class CircleParams(BaseFigureParams):
    """圓形生成器參數
    
    定義圓形的中心、半徑和繪製選項。支援填充、
    邊框樣式等多種視覺效果。
    
    Example:
        >>> params = CircleParams(
        ...     center=(0, 0), 
        ...     radius=1.0, 
        ...     variant="question"
        ... )
    """
```

#### Afternoon (4 小時): 樣式與複合參數
##### Task 2.3: 分離標籤和樣式參數 + Sphinx
**目標文件**: `figures/params/styles/labels.py`
```python
"""標籤樣式參數模型

定義文字標籤的位置、字體、顏色等樣式屬性，
支援數學模式和 TikZ 高級選項。

Example:
    >>> params = LabelParams(
    ...     x=1.0, y=2.0, 
    ...     text="A", 
    ...     variant="question"
    ... )
"""

class LabelParams(BaseFigureParams):
    """文字標籤參數
    
    定義標籤的位置、內容和顯示樣式，支援數學模式、
    字體設定、顏色配置等豐富的視覺選項。
    
    Attributes:
        x (float): 標籤 X 座標
        y (float): 標籤 Y 座標
        text (str): 標籤文字內容
        math_mode (bool): 是否使用數學模式
        
    Example:
        >>> params = LabelParams(
        ...     x=1.0, y=2.0,
        ...     text="A",
        ...     color="blue",
        ...     variant="question"
        ... )
    """
```

##### Task 2.4: 分離複合圖形參數 + Sphinx

### Day 3: 三角形參數隔離 + 重點文檔

#### Morning (4 小時): 基礎三角形參數
##### Task 3.1: 隔離三角形基礎參數 + Sphinx
**目標文件**: `figures/params/triangle/basic.py`
```python
"""基礎三角形參數模型

定義簡單三角形的頂點位置和基本顯示選項，適用於
大多數常見的三角形生成需求。
"""

class BasicTriangleParams(BaseFigureParams):
    """基礎三角形生成器參數
    
    通過三個頂點定義三角形，支援基本的繪製和填充選項。
    這是最簡單和最常用的三角形參數模型。
    
    Attributes:
        p1 (PointTuple): 第一個頂點座標
        p2 (PointTuple): 第二個頂點座標
        p3 (PointTuple): 第三個頂點座標
        draw_options (str, optional): TikZ 繪製選項
        fill_color (str, optional): 填充顏色
        
    Example:
        >>> params = BasicTriangleParams(
        ...     p1=(0, 0), p2=(1, 0), p3=(0.5, 1),
        ...     variant="question"
        ... )
    """
```

##### Task 3.2: 隔離 162 行怪物 + 重點 Sphinx 🗡️
**目標文件**: `figures/params/triangle/advanced.py`
```python
"""高級三角形參數模型 - 複雜配置專區

⚠️ 警告: 此文件包含極其複雜的參數配置系統！
包含 162 行的 PredefinedTriangleParams 類別，支援多種
三角形類型、自動標籤、幾何計算等高級功能。

建議開發者優先使用 BasicTriangleParams，除非需要
高度客製化的三角形生成功能。

Note:
    此模組的複雜性較高，建議搭配具體範例和測試用例學習。
"""

class PredefinedTriangleParams(BaseFigureParams):
    """預定義三角形參數配置 - 超級複雜版本
    
    ⚠️ 這是一個 162 行的複雜參數類別！
    
    支援多種預定義三角形類型的完整參數系統，包含：
    - 多種三角形類型 (等邊、等腰、直角等)
    - 自動頂點標籤和幾何標記
    - 複雜的樣式和顯示選項
    - 內建幾何計算和驗證
    - 高度可客製化的渲染選項
    
    此類別包含複雜的內部邏輯和驗證規則，建議：
    1. 優先使用 BasicTriangleParams 滿足基本需求
    2. 參考測試檔案中的使用範例
    3. 查看具體三角形類型的文檔說明
    
    Attributes:
        triangle_type (str): 三角形類型，支援多種預定義類型
        vertices (Dict): 複雜的頂點配置系統
        labels (Dict, optional): 自動標籤生成配置
        geometric_marks (Dict, optional): 幾何標記配置
        rendering_options (Dict, optional): 高級渲染選項
        
    Example:
        >>> # 基本使用 - 等邊三角形
        >>> params = PredefinedTriangleParams(
        ...     triangle_type="equilateral",
        ...     side_length=2.0,
        ...     variant="question"
        ... )
        
        >>> # 複雜使用 - 自定義直角三角形
        >>> params = PredefinedTriangleParams(
        ...     triangle_type="right_triangle",
        ...     vertices={"custom": True, "A": (0,0), "B": (3,0), "C": (0,4)},
        ...     labels={"show_vertices": True, "show_sides": True},
        ...     variant="explanation"
        ... )
        
    Warning:
        此類別的複雜性很高，不當的參數組合可能導致意外結果。
        強烈建議先閱讀相關文檔和測試範例。
        
    Note:
        未來可能會將此類別進一步分解為更小的專用類別，
        以降低複雜性和提高可維護性。
    """
    # 162 行的複雜參數定義和驗證邏輯
    # [保持原有實現，但添加詳細的字段文檔]
```

#### Afternoon (4 小時): 統一接口與導出
##### Task 3.3: 建立統一導出接口 + 完整 Sphinx
**目標文件**: `figures/params/__init__.py`
```python
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

# 重新導出所有參數類，保持向後兼容
from .types import *
from .base import *
from .geometry import *
from .shapes import *
from .composite import *
from .triangle import *
from .styles import *

# 確保現有代碼仍能正常工作:
# from figures.params_models import BasicTriangleParams ✅
```

### Day 4: Sphinx 文檔完善 + 最終整合

#### Morning (4 小時): 文檔完善
##### Task 4.1: 完善所有模組 docstring
- [ ] 檢查所有文件的模組級 docstring
- [ ] 完善類別和重要方法的文檔
- [ ] 添加更多實用的 Example 區段
- [ ] 確保所有 Note 和 Warning 適當

##### Task 4.2: 子包文檔完善
- [ ] `figures/params/triangle/__init__.py` - 三角形模組總覽
- [ ] `figures/params/styles/__init__.py` - 樣式模組總覽
- [ ] 確保導出接口清晰明確

#### Afternoon (4 小時): 測試與最終驗證
##### Task 4.3: Sphinx 文檔驗證
- [ ] 運行 `sphinx-build` 檢查文檔生成
- [ ] 確保無 Sphinx 警告或錯誤
- [ ] 檢查文檔格式和連結正確

##### Task 4.4: 最終功能驗證
- [ ] 完整測試套件運行
- [ ] 向後兼容性驗證
- [ ] 新導入方式測試
- [ ] 性能基準檢查

## 🧪 測試與驗證策略

### 每日驗證檢查
**每完成一個 Task 後**:
1. [ ] 運行現有測試: `pytest tests/test_figure_*.py`
2. [ ] 驗證參數模型導入: `from figures.params_models import ...`
3. [ ] 檢查 Pydantic 模型驗證正常
4. [ ] 確保無循環導入問題

### 最終整合測試
**Day 3 結束時**:
1. [ ] 完整測試套件運行
2. [ ] 所有現有功能正常
3. [ ] 新架構導入測試: `from figures.params import ...`
4. [ ] 性能基準測試 (確保無顯著下降)

## 🔧 實施細節

### 文件遷移模式
```python
# Step 1: 在新位置創建類別
# figures/params/shapes.py
from .base import BaseFigureParams
from .types import PointTuple

class CircleParams(BaseFigureParams):
    # 移動來的內容

# Step 2: 在 __init__.py 重新導出
# figures/params/__init__.py  
from .shapes import CircleParams

# Step 3: 暫時保持舊文件兼容
# figures/params_models.py (暫時保留)
from .params import CircleParams  # 重新導入
```

### 風險控制措施
1. **小步提交**: 每個 Task 完成後立即 git commit
2. **測試先行**: 移動任何類別前先運行測試
3. **向後兼容**: 確保 `from figures.params_models import` 仍然工作
4. **逐步驗證**: 每個文件移動後立即驗證功能

## 📊 成功指標

### 定量指標
- [ ] **文件數量**: 1 → 12+ 文件 
- [ ] **最大文件行數**: < 100 行 (除了 advanced.py)
- [ ] **PredefinedTriangleParams**: 隔離到專門文件
- [ ] **測試通過率**: 100% (與重構前相同)
- [ ] **功能完整性**: 所有參數類正常工作
- [ ] **Sphinx 文檔**: 完整的 docstring 覆蓋率 100%

### 定性指標  
- [ ] **可讀性**: 每個文件職責清晰
- [ ] **可維護性**: 邏輯分組合理
- [ ] **可擴展性**: 新參數類型易於添加
- [ ] **向後兼容**: 現有代碼無需修改
- [ ] **文檔品質**: Sphinx 無警告生成，文檔清晰易懂

## 🚨 風險與緩解

### 高風險項目
1. **循環導入風險**
   - **緩解**: 仔細設計導入層次，base.py 不依賴其他參數文件

2. **Pydantic 驗證器失效**  
   - **緩解**: 移動類別時保持完整的 validator 和 model_config

3. **測試破損風險**
   - **緩解**: 每步都運行測試，小步提交

### 中風險項目
1. **性能下降** - 緩解: 導入優化，避免過深嵌套
2. **IDE 提示失效** - 緩解: 正確設置 `__all__` 和類型提示

## 📋 工作檢查清單

### 開始前準備
- [ ] 確認 git 狀態乾淨
- [ ] 創建專門分支: `feature/refactor-params-models`
- [ ] 運行基準測試獲取當前狀態
- [ ] 備份當前 `params_models.py` 文件

### 每日結束檢查
- [ ] 所有 Task 對應的 git commit 完成
- [ ] 測試通過率維持 100%
- [ ] 文檔更新 (如適用)
- [ ] 下一日 Task 準備就緒

### 項目完成標準
- [ ] **562 行怪物消失** ✅ 
- [ ] **模組化架構建立** ✅
- [ ] **PredefinedTriangleParams 成功隔離** ✅
- [ ] **向後兼容性維持** ✅
- [ ] **所有測試通過** ✅
- [ ] **完整 Sphinx docstring 覆蓋** ✅

---

**創建日期**: 2025-09-04  
**預計完成**: 2025-09-08 (4天計畫)  
**負責人**: Claude Code Assistant  
**審查要求**: 每日進度檢查，完成後代碼審查