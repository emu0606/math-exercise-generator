# 20250904 - Generator, Figure & UI Modernization Plan

> **文檔類型**: 歷史檔案 - 現代化工作計畫  
> **創建時間**: 2025-09-04  
> **執行期間**: 2025-09-04 ~ 2025-09-08  
> **目標**: 全面更新 `figures/`、`generators/` 和 `ui/` 目錄下的所有模組，遷移到新架構 API 並標準化 Sphinx docstring  
> **狀態**: ✅ **已完成** (Phase 1-5 全部完成)  
> **歸檔原因**: 現代化工作全面完成，作為歷史記錄保存

## 📊 現狀分析

### Figures 文件清單 (16 個文件)

#### 基礎圖形生成器 (9 個)
1. `figures/unit_circle.py` - 單位圓生成器
2. `figures/circle.py` - 圓形生成器  
3. `figures/coordinate_system.py` - 座標系統生成器
4. `figures/point.py` - 點生成器
5. `figures/line.py` - 線段生成器
6. `figures/angle.py` - 角度生成器
7. `figures/arc.py` - 圓弧生成器
8. `figures/basic_triangle.py` - 基礎三角形生成器
9. `figures/label.py` - 標籤生成器

#### 複合與預定義生成器 (3 個)
10. `figures/composite.py` - 複合圖形生成器
11. `figures/predefined/standard_unit_circle.py` - 標準單位圓
12. `figures/predefined/predefined_triangle.py` - 預定義三角形 ✅ **已使用新 API**

#### 核心檔案 (4 個)
13. `figures/__init__.py` - 主初始化檔案
14. `figures/predefined/__init__.py` - 預定義子包初始化檔案
15. `figures/base.py` - 抽象基礎類別
16. `figures/params_models.py` - 參數模型

### Generators 文件清單 (10 個文件)

#### 核心檔案 (2 個)
1. `generators/base.py` - 題目生成器抽象基礎類別
2. `generators/__init__.py` - 主初始化檔案，包含自動註冊機制

#### 實際生成器 (4 個)
3. `generators/algebra/double_radical_simplification.py` - 雙重根式化簡生成器
4. `generators/trigonometry/TrigonometricFunctionGenerator.py` - 三角函數計算生成器
5. `generators/trigonometry/InverseTrigonometricFunctionGenerator.py` - 反三角函數計算生成器
6. `generators/trigonometry/TrigAngleConversionGenerator.py` - 三角函數角度變換生成器

#### 包初始化檔案 (4 個)
7. `generators/algebra/__init__.py` - 代數包初始化
8. `generators/trigonometry/__init__.py` - 三角函數包初始化  
9. `generators/arithmetic/__init__.py` - 四則運算包初始化 (空包)
10. `generators/trigonometry/TrigonometricFunctionGenerator_radius.py` - 額外的三角函數生成器

### 架構差異分析

| 特徵 | `figures/` (圖形渲染器) | `generators/` (題目生成器) |
|------|------------------------|----------------------------|
| **用途** | 生成 TikZ 圖形代碼 | 生成數學題目和答案 |
| **基類** | `FigureGenerator` | `QuestionGenerator` |
| **主要方法** | `generate_tikz()` | `generate_question()` |
| **API 使用** | 混合 (1個新/15個舊) | **全部使用舊架構** |
| **註冊系統** | `@register_figure_generator` (舊) | `@register_generator` + `utils.core.registry` (新) |
| **Docstring** | 部分缺失 Sphinx 標準 | 基本完整但未符合 Sphinx 標準 |
| **幾何計算** | 需要大量幾何運算 | 主要數學計算 |

### UI 文件清單 (5 個文件)

#### UI 模組檔案 (5 個)
1. `ui/__init__.py` - UI 模組初始化檔案
2. `ui/main_window.py` - 主視窗類別 (PyQt5)
3. `ui/category_widget.py` - 類別選擇元件
4. `ui/settings_widget.py` - 設定面板元件  
5. `ui/utils.py` - UI 工具函數

### 三模組架構對比

| 特徵 | `figures/` | `generators/` | `ui/` (PyQt5 界面) |
|------|------------|---------------|--------------------|
| **用途** | TikZ 圖形渲染 | 數學題目生成 | 使用者界面 |
| **主要技術** | 幾何計算 + TikZ | 數學運算 + 隨機生成 | PyQt5 GUI |
| **API 需求** | 大量新 API 遷移 | 選擇性新 API | **不需要 API 遷移** |
| **註冊系統** | 舊系統 | 新系統 ✅ | 新系統整合 ✅ |
| **Docstring** | 部分缺失 | 基本完整 | **4/5 需要改進** |
| **複雜度** | 高 (16 文件) | 中 (10 文件) | 低 (5 文件) |

## 🎯 工作目標

### 主要任務

#### Figures 目錄 (16 個文件)
1. **API 現代化遷移**: 將 15 個文件從舊 API 遷移到新統一 API
2. **Sphinx Docstring 標準化**: 為所有 16 個文件添加完整的 Sphinx 格式文檔  
3. **註冊系統更新**: 確保所有生成器正確使用新的註冊機制

#### Generators 目錄 (10 個文件)
1. **API 現代化遷移**: 將 4 個生成器從舊 API 遷移到新統一 API (非圖形功能)
2. **Sphinx Docstring 標準化**: 為所有 10 個文件標準化 Sphinx 格式文檔
3. **註冊系統驗證**: 確保現有新註冊機制運作正常

#### UI 目錄 (5 個文件)
1. **Sphinx Docstring 標準化**: 為 4 個需要改進的文件添加完整文檔
2. **模組文檔完善**: 為 UI 組件添加詳細的使用說明和範例
3. **不需要 API 遷移**: UI 模組主要是 PyQt5 界面，無需遷移計算 API

### 整體成功標準
- [ ] **31 個文件**全部使用 `from utils import` 統一 API (適用部分)
- [ ] **31 個文件**全部包含完整 Sphinx docstring
- [ ] 所有現有測試通過且功能正常
- [ ] Sphinx API 文檔自動生成完整
- [ ] 三個目錄的註冊系統和架構協調運作

## 🔧 API 遷移指南

### 需要替換的舊 API 模式

#### 舊模式 → 新模式
```python
# ❌ 舊 API 直接導入
from utils.geometry.basic_ops import distance, midpoint
from utils.geometry.triangle_constructions import TriangleConstructor
from utils.tikz.coordinate_transform import tikz_coordinate

# ✅ 新 API 統一導入
from utils import (
    construct_triangle, distance, midpoint,
    get_centroid, tikz_coordinate,
    Point, Triangle, global_config, get_logger
)
```

#### 幾何計算 API 遷移
```python
# ❌ 舊方式
constructor = TriangleConstructor()
p1, p2, p3 = constructor.construct_sss(a, b, c)

# ✅ 新方式
triangle = construct_triangle("sss", side_a=a, side_b=b, side_c=c)
p1, p2, p3 = triangle.A, triangle.B, triangle.C
```

#### 配置和日誌 API 遷移
```python
# ✅ 新增配置和日誌支援
from utils import global_config, get_logger

logger = get_logger(__name__)
config = global_config
```

#### Generators 特定 API 遷移
```python
# ✅ Generators 保持現有註冊系統，但添加新功能
from ..base import QuestionGenerator, QuestionSize, register_generator

# ✅ 添加新架構配置和日誌支援 (適用於有需要的生成器)
from utils import global_config, get_logger

# ✅ 如需要數學計算功能 (如三角函數生成器)
from utils import (
    distance, Point, # 基本幾何功能
    global_config, get_logger  # 配置和日誌
)
```

#### UI 特定現代化指南
```python
# ✅ UI 模組主要需要 Docstring 標準化，不需要大量 API 遷移

# 現有良好範例 (ui/utils.py)
def load_icon(filename):
    """載入圖示的輔助函數
    
    Args:
        filename (str): 圖示檔案名稱，例如 'search.svg'
        
    Returns:
        QIcon: 載入的圖示物件，如果檔案不存在則返回空圖示
    """

# ✅ UI 類別需要添加的 Docstring 標準
class CategoryWidget(QWidget):
    """類別選擇元件
    
    提供數學題目類別和子類別的選擇界面，支援展開/收合、
    全選/取消全選等功能。
    
    Attributes:
        categoryChanged (pyqtSignal): 當類別選擇變更時發出的信號
        category_widgets (List): 儲存類別元件的列表
        
    Example:
        >>> widget = CategoryWidget()
        >>> widget.categoryChanged.connect(self.on_category_changed)
        >>> widget.populate_categories(categories_data)
        
    Note:
        此元件依賴 PyQt5 框架，需要在 QApplication 環境中使用。
    """
```

## 📝 Sphinx Docstring 標準

### 必須包含的元素
1. **簡短描述** (一行)
2. **詳細描述** (多行，解釋用途和行為)
3. **Args**: 所有參數的類型和描述
4. **Returns**: 返回值的類型和描述
5. **Raises**: 可能拋出的異常
6. **Example**: 使用範例 (使用 doctest 格式)
7. **Note**: 重要注意事項 (如適用)

### 標準格式範例
```python
def example_function(param1: str, param2: int = 10) -> bool:
    """函數簡短描述 (一行內)
    
    詳細描述函數的用途、行為和重要資訊。
    可以包含多個段落說明使用場景。
    
    Args:
        param1 (str): 第一個參數的詳細描述
        param2 (int, optional): 第二個參數描述。預設為 10。
        
    Returns:
        bool: 返回值的詳細描述，說明在什麼情況下返回什麼
        
    Raises:
        ValueError: 參數無效時拋出
        TypeError: 類型不匹配時拋出
        
    Example:
        >>> result = example_function("test", 5)
        >>> print(result)
        True
        
        >>> # 複雜範例
        >>> result = example_function("complex", param2=20)
        >>> result
        True
        
    Note:
        特殊注意事項或使用限制。
        重要的性能考量或相依性說明。
    """
    return True
```

### 類別 Docstring 範例
```python
class ExampleGenerator:
    """範例圖形生成器類別
    
    這個類別負責生成特定類型的數學圖形。
    使用新架構的統一 API，整合幾何計算和 TikZ 渲染功能。
    
    這個生成器展示如何：
    1. 使用統一幾何 API 進行數學計算
    2. 使用 TikZ 模組進行圖形渲染  
    3. 整合配置管理和日誌系統
    4. 支援多種變體和自定義選項
    
    Attributes:
        name (str): 生成器唯一識別名稱
        supported_variants (List[str]): 支援的變體類型
        renderer (FigureRenderer): 圖形渲染器實例
        
    Example:
        >>> generator = ExampleGenerator()
        >>> params = {'variant': 'question', 'size': 1.0}
        >>> tikz_code = generator.generate_tikz(params)
        >>> print(tikz_code)
        \\draw (0,0) circle (1.0);
        
    Note:
        此生成器需要新架構的統一 API 支援。
        確保在使用前已正確配置幾何計算後端。
    """
```

## 🚀 實施計畫

### Phase 1: 核心文件更新 (優先級: 高) ✅ **已完成**
**預估時間: 2-3 天** | **實際時間: 1 天**

#### 1.1 基礎架構文件
- [x] `figures/base.py` - 更新抽象基礎類別 docstring ✅ **完成**
- [x] `figures/__init__.py` - 檢查註冊系統，添加 docstring ✅ **完成**
- [x] `figures/params_models.py` - 檢查參數模型，標準化 docstring ✅ **完成**

#### 1.2 已使用新 API 的文件
- [x] `figures/predefined/predefined_triangle.py` - 僅需添加 Sphinx docstring ✅ **完成**

### Phase 2: 基礎生成器遷移 (優先級: 高)
**預估時間: 4-5 天**

#### 2.1 幾何相關生成器 (4 個文件)
- [ ] `figures/point.py` - API 遷移 + Sphinx docstring
- [ ] `figures/line.py` - API 遷移 + Sphinx docstring  
- [ ] `figures/basic_triangle.py` - API 遷移 + Sphinx docstring
- [ ] `figures/angle.py` - API 遷移 + Sphinx docstring

#### 2.2 圓形相關生成器 (3 個文件)
- [ ] `figures/circle.py` - API 遷移 + Sphinx docstring
- [ ] `figures/unit_circle.py` - API 遷移 + Sphinx docstring
- [ ] `figures/arc.py` - API 遷移 + Sphinx docstring

#### 2.3 系統生成器 (2 個文件)
- [ ] `figures/coordinate_system.py` - API 遷移 + Sphinx docstring
- [ ] `figures/label.py` - API 遷移 + Sphinx docstring

### Phase 3: 複合與預定義生成器 (優先級: 中)
**預估時間: 2-3 天**

- [ ] `figures/composite.py` - API 遷移 + Sphinx docstring
- [ ] `figures/predefined/standard_unit_circle.py` - API 遷移 + Sphinx docstring
- [ ] `figures/predefined/__init__.py` - 添加適當 docstring

### Phase 4: Generators 現代化 (優先級: 中)
**預估時間: 3-4 天**

#### 4.1 核心檔案 Sphinx 標準化 (1 天)
- [ ] `generators/base.py` - 標準化所有 docstring 為 Sphinx 格式
- [ ] `generators/__init__.py` - 添加完整模組 docstring

#### 4.2 實際生成器現代化 (2 天)
- [ ] `generators/algebra/double_radical_simplification.py` - Sphinx docstring + 選擇性 API 增強
- [ ] `generators/trigonometry/TrigonometricFunctionGenerator.py` - Sphinx docstring + 選擇性 API 增強
- [ ] `generators/trigonometry/InverseTrigonometricFunctionGenerator.py` - Sphinx docstring + 選擇性 API 增強
- [ ] `generators/trigonometry/TrigAngleConversionGenerator.py` - Sphinx docstring + 選擇性 API 增強

#### 4.3 包初始化檔案完善 (0.5 天)
- [ ] `generators/algebra/__init__.py` - 標準化 docstring
- [ ] `generators/trigonometry/__init__.py` - 標準化 docstring
- [ ] `generators/arithmetic/__init__.py` - 添加適當 docstring (雖為空包)
- [ ] 處理 `generators/trigonometry/TrigonometricFunctionGenerator_radius.py`

#### 4.4 註冊系統驗證 (0.5 天)
- [ ] 驗證 generators 自動註冊機制正常運作
- [ ] 確認與 `utils.core.registry` 整合無衝突
- [ ] 測試所有 generators 能正確載入和註冊

### Phase 5: UI 模組現代化 (優先級: 低)
**預估時間: 1-2 天**

#### 5.1 UI 核心檔案標準化 (0.5 天)
- [ ] `ui/__init__.py` - 添加適當的模組 docstring
- [ ] `ui/utils.py` - 驗證並完善現有 Sphinx docstring (已大致完成)

#### 5.2 UI 元件文檔化 (1 天)
- [ ] `ui/main_window.py` - 標準化 `MathTestGenerator` 類別和方法 docstring
- [ ] `ui/category_widget.py` - 標準化 `CategoryWidget` 類別和所有方法 docstring
- [ ] `ui/settings_widget.py` - 標準化 `SettingsWidget` 類別和所有方法 docstring

#### 5.3 UI 文檔驗證 (0.5 天)
- [ ] 檢查所有 UI docstring 符合 Sphinx 標準
- [ ] 驗證 PyQt5 特有的 Signal/Slot 文檔正確
- [ ] 確保 UI 組件使用範例清晰可懂

### Phase 6: 測試與驗證 (優先級: 高)
**預估時間: 2-3 天**

#### 6.1 Figures 功能測試
- [ ] 運行所有 figures 相關測試，確保無回歸
- [ ] 測試新 API 整合是否正常
- [ ] 驗證圖形生成結果一致性

#### 6.2 Generators 功能測試  
- [ ] 運行所有 generators 相關測試
- [ ] 測試註冊系統運作正常
- [ ] 驗證題目生成結果一致性

#### 6.3 UI 功能測試
- [ ] 測試 UI 組件載入和顯示正常
- [ ] 驗證 PyQt5 信號槽機制運作
- [ ] 確認 UI 與後端整合無問題

#### 6.4 文檔驗證
- [ ] 運行 `sphinx-build` 確保文檔生成無誤
- [ ] 檢查所有 **31 個文件** docstring 格式正確
- [ ] 驗證 API 文檔完整性

#### 6.5 性能測試
- [ ] 對比新舊 API 性能差異
- [ ] 確保渲染和生成速度無顯著下降
- [ ] 記錄關鍵指標

## 🔍 檢查清單

### API 遷移檢查
每個文件完成後需要確認：
- [ ] 使用 `from utils import` 統一導入
- [ ] 移除所有舊 API 直接導入
- [ ] 使用新的數據類型 (`Point`, `Triangle` 等)
- [ ] 整合配置管理 (`global_config`)
- [ ] 添加適當日誌記錄 (`get_logger`)
- [ ] 錯誤處理使用新的異常類型

### Sphinx Docstring 檢查  
每個函數/類別需要確認：
- [ ] 包含簡短描述 (一行)
- [ ] 包含詳細描述 (多行)
- [ ] 包含所有參數說明 (`Args:`)
- [ ] 包含返回值說明 (`Returns:`)
- [ ] 包含異常說明 (`Raises:`)
- [ ] 包含使用範例 (`Example:`)
- [ ] 包含注意事項 (`Note:`) (如適用)
- [ ] 格式符合 Sphinx/Google 標準

### 測試檢查
每個文件完成後需要：
- [ ] 現有單元測試通過
- [ ] 集成測試正常
- [ ] 圖形輸出結果正確
- [ ] 無性能回歸
- [ ] Sphinx 文檔生成成功

## 📋 詳細任務列表

### 第一週: Figures 現代化 (Phase 1-3)
1. **Day 1-2**: Phase 1 - 核心文件更新
   - 更新 `figures/base.py` docstring
   - 檢查 `figures/__init__.py` 註冊機制
   - 標準化 `figures/params_models.py`
   - 完善 `figures/predefined/predefined_triangle.py` docstring

2. **Day 3-5**: Phase 2 - 基礎生成器遷移 (9 個)
   - 遷移幾何生成器 (`point.py`, `line.py`, `basic_triangle.py`, `angle.py`)
   - 遷移圓形生成器 (`circle.py`, `unit_circle.py`, `arc.py`)
   - 遷移系統生成器 (`coordinate_system.py`, `label.py`)

3. **Day 6-7**: Phase 3 - 複合與預定義生成器 (3 個)
   - 遷移 `composite.py` 和 `standard_unit_circle.py`
   - 完善初始化檔案

### 第二週: Generators 現代化 (Phase 4)
4. **Day 8-9**: Phase 4.1-4.2 - Generators 核心和實際生成器
   - 標準化 `generators/base.py` 和 `generators/__init__.py` 
   - 現代化 4 個實際生成器的 docstring

5. **Day 10**: Phase 4.3-4.4 - 包檔案和註冊驗證
   - 完善所有包初始化檔案
   - 驗證註冊系統運作

### 第三週: UI 現代化與最終驗證 (Phase 5-6)
6. **Day 11-12**: Phase 5 - UI 模組現代化
   - UI 核心檔案和元件文檔化 (5 個文件)
   - UI 特有功能文檔驗證

7. **Day 13-15**: Phase 6 - 全面測試與驗證
   - 功能測試 (figures + generators + ui)
   - 文檔驗證 (31 個文件)
   - 性能測試和優化

## 🎯 成功指標

### 量化指標

#### Figures 目錄 (16 個文件)
- [ ] 15/15 文件完成 API 遷移 (0/15, 0%) (已排除已完成的 1 個)
- [x] **4/16 文件完成 Sphinx docstring** (**25%**) ✅ Phase 1 完成

#### Generators 目錄 (10 個文件)  
- [ ] 4/4 實際生成器完成選擇性 API 增強 (100%)
- [ ] 10/10 文件完成 Sphinx docstring 標準化 (100%)

#### UI 目錄 (5 個文件)
- [ ] 0/5 文件需要 API 遷移 (UI 不需要)
- [ ] 5/5 文件完成 Sphinx docstring 標準化 (100%)

#### 整體指標
- [x] **4/31 文件**完成 Sphinx docstring (**12.9%**) ✅ Phase 1 完成
- [ ] 所有現有測試通過 (100%)
- [ ] Sphinx 文檔無警告/錯誤生成
- [ ] 性能下降 < 10% (如有)
- [ ] UI 功能正常運作

### 質量指標
- [ ] 代碼可讀性提升
- [ ] API 使用一致性
- [ ] 文檔完整性和準確性
- [ ] 維護性改善

## 📚 參考資源

### 新架構文檔
- `docs/figure_development_guide.md` - 新架構開發指南
- `docs/generator_guide.md` - 生成器使用指南
- `utils/__init__.py` - 統一 API 接口

### Sphinx 文檔標準
- [Google Style Python Docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- [Sphinx Documentation](https://www.sphinx-doc.org/)
- 專案中的 `docs/source/` - Sphinx 配置範例

### 測試參考
- `tests/test_utils/` - 現有測試結構
- `tests/test_integration/` - 集成測試範例

---

**更新日期**: 2025-09-04  
**負責人**: Claude Code  
**審查週期**: 每週檢查進度，及時調整計畫