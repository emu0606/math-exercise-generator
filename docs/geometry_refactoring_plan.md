# Utils 模組全面重構工作計畫

## 專案背景

當前 `utils/` 模組存在多重問題：
1. **`geometry_utils.py` 過於龐大**（969 行），功能混雜且未完工
2. **代碼品質問題**：調試輸出洩漏、重複代碼、臨時註釋
3. **架構設計問題**：職責不明、依賴混亂、耦合度高
4. **缺乏統一標準**：日誌系統不一致、配置管理分散

## 重構目標

1. **分離職責**：將純數學計算與渲染輔助分離
2. **提升品質**：統一代碼標準、日誌系統、錯誤處理
3. **模組化設計**：清晰的依賴關係、可測試的架構
4. **引入專業工具**：使用 NumPy/SymPy 提升計算能力
5. **保持相容性**：確保現有功能正常運作

## 新架構設計

```
utils/
├── __init__.py                    # 統一入口，向後相容接口
├── core/                         # 核心功能模組
│   ├── __init__.py
│   ├── registry.py               # 清理後的註冊系統
│   ├── layout_engine.py          # 重構的佈局引擎  
│   ├── config.py                 # 統一配置管理
│   └── logging.py                # 統一日誌系統
├── geometry/                     # 純數學幾何計算
│   ├── __init__.py
│   ├── basic_ops.py              # 基礎運算
│   ├── triangle_construction.py  # 三角形構造
│   ├── triangle_centers.py       # 三角形特殊點
│   ├── vector_ops.py             # 向量運算
│   ├── circle_ops.py             # 圓相關計算
│   ├── math_backend.py           # NumPy/SymPy 集成
│   ├── types.py                  # 幾何類型定義
│   └── exceptions.py             # 幾何異常
├── tikz/                         # TikZ/LaTeX 渲染輔助
│   ├── __init__.py
│   ├── label_positioning.py      # 標籤定位策略
│   ├── arc_parameters.py         # 角弧參數計算
│   ├── coordinate_transform.py   # 座標轉換
│   ├── layout_helpers.py         # 佈局輔助
│   ├── types.py                  # TikZ 類型定義
│   └── exceptions.py             # TikZ 異常
├── latex/                        # LaTeX 文檔生成
│   ├── __init__.py
│   ├── generator.py              # 重構的 LaTeX 生成器
│   ├── compiler.py               # 改進的 PDF 編譯器
│   ├── structure.py              # 清理的文檔結構
│   ├── config.py                 # LaTeX 配置
│   └── escape.py                 # 轉義工具
├── rendering/                    # 圖形渲染
│   ├── __init__.py
│   └── figure_renderer.py        # 解耦的圖形渲染器
└── orchestration/                # 業務協調層
    ├── __init__.py
    └── pdf_generator.py          # 重構的 PDF 生成協調器
```

## 數學庫集成策略

### 核心數學庫選擇
- **NumPy**：高效數值計算、向量運算
- **SymPy**：符號數學、精確幾何計算
- **Math**：基礎數學函數

### 集成原則
1. **性能優先**：數值密集計算使用 NumPy
2. **精度優先**：符號計算和精確結果使用 SymPy
3. **選擇性使用**：提供後端選擇，避免過度依賴
4. **統一接口**：封裝不同後端的差異

### 實現策略
```python
# utils/geometry/math_backend.py
class MathBackend:
    @staticmethod
    def distance(p1, p2, backend='numpy'):
        if backend == 'numpy':
            return np.linalg.norm(np.array(p2) - np.array(p1))
        elif backend == 'sympy':
            return sympy.geometry.Point(p1).distance(sympy.geometry.Point(p2))
        else:  # Pure Python fallback
            return math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)
```

## 重構策略

### 乾淨重構原則
基於分析發現影響範圍有限（主要是 `figures/predefined/predefined_triangle.py`），採用：
- **不保留向後相容層**，避免產生新的技術債務
- **一次性替換**，同步更新調用方
- **完整測試覆蓋**，確保功能正確性

### 關鍵遷移映射

#### 函數名稱對應
| 舊模組/函數 | 新模組/函數 | 變更說明 |
|------------|------------|----------|
| `utils.geometry_utils.get_vertices()` | `utils.geometry.construct_triangle()` | 統一三角形構造接口 |
| `utils.geometry_utils.get_label_placement_params()` | `utils.tikz.position_vertex_label()` 等 | 按元素類型分離函數 |
| `utils.geometry_utils.get_arc_render_params()` | `utils.tikz.calculate_arc_params()` | 語義更清晰的命名 |
| `utils.geometry_utils._distance()` | `utils.geometry.distance()` | 公開 API，去除私有前綴 |
| `utils.geometry_utils.TriangleDefinitionError` | `utils.geometry.TriangleConstructionError` | 更準確的異常命名 |

#### 導入語句變更
```python
# 舊的導入 (predefined_triangle.py)
from utils.geometry_utils import (
    get_vertices, TriangleDefinitionError,
    get_midpoint, get_centroid, get_incenter, get_circumcenter, get_orthocenter,
    get_arc_render_params, get_label_placement_params, _distance
)

# 新的導入 (重構後)
from utils.geometry import (
    construct_triangle, TriangleConstructionError,
    get_midpoint, get_centroid, get_incenter, get_circumcenter, get_orthocenter,
    distance
)
from utils.tikz import (
    calculate_arc_params, position_vertex_label, position_side_label, position_angle_label
)
```

## 詳細實施計畫

### 階段一：基礎設施建立（3-4 天）

#### 任務 1.1：創建新架構目錄結構
- [ ] 創建所有新模組目錄
- [ ] 建立各模組的 `__init__.py` 文件
- [ ] 設置基礎的導入結構

#### 任務 1.2：統一基礎設施
- [ ] **`utils/core/config.py`** - 統一配置管理
  ```python
  class GlobalConfig:
      def __init__(self):
          self.debug_mode = False
          self.log_level = "INFO"
          self.math_backend_default = "numpy"
          self.tikz_precision = 7  # decimal places
  ```

- [ ] **`utils/core/logging.py`** - 統一日誌系統
  ```python
  import logging
  
  def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
      logger = logging.getLogger(name)
      # 統一的日誌格式和處理器
      return logger
  ```

- [ ] **清理現有代碼品質問題**
  - 移除 `registry.py` 中的調試 print 語句
  - 修復 `layout_engine.py` 的臨時註釋
  - 清理 `pdf_generator.py` 的格式問題

#### 任務 1.3：建立測試框架
- [ ] 設置 pytest 測試環境
- [ ] 創建測試工具函數
- [ ] 建立基準測試數據

### 階段二：核心模組重構（4-5 天）

#### 任務 2.1：幾何計算模組
- [ ] **`utils/geometry/math_backend.py`**
  - NumPy/SymPy 集成層
  - 類型轉換工具
  - 統一數學運算接口

- [ ] **`utils/geometry/basic_ops.py`**
  ```python
  def distance(p1: Point, p2: Point, backend: str = 'numpy') -> float
  def get_midpoint(p1: Point, p2: Point) -> Point
  def angle_between_points(p1: Point, vertex: Point, p2: Point) -> float
  def normalize_angle(angle_rad: float) -> float
  ```

- [ ] **`utils/geometry/triangle_construction.py`**
  ```python
  def construct_triangle_sss(side_a: float, side_b: float, side_c: float) -> Triangle
  def construct_triangle_sas(side1: float, angle_rad: float, side2: float) -> Triangle
  def construct_triangle_asa(angle1_rad: float, side_length: float, angle2_rad: float) -> Triangle
  def construct_triangle_aas(angle1_rad: float, angle2_rad: float, side_opposite_angle1: float) -> Triangle
  
  # 統一接口
  def construct_triangle(mode: str, **kwargs) -> Triangle
  ```

- [ ] **`utils/geometry/triangle_centers.py`**
  - 使用 SymPy.geometry 重寫特殊點計算
  - 提供高精度和高性能兩種模式
  ```python
  def get_centroid(triangle: Triangle, backend: str = 'sympy') -> Point
  def get_incenter(triangle: Triangle, backend: str = 'sympy') -> Point
  def get_circumcenter(triangle: Triangle, backend: str = 'sympy') -> Point
  def get_orthocenter(triangle: Triangle, backend: str = 'sympy') -> Point
  def get_all_centers(triangle: Triangle) -> Dict[str, Point]
  ```

#### 任務 2.2：佈局引擎重構
- [ ] **重構 `utils/core/layout_engine.py`**
  - 提取重複的放置邏輯
  - 改善可讀性和可測試性
  ```python
  def _try_place_item(self, item_data, page, grids, dimensions):
      """提取的通用放置方法"""
      
  def _create_layout_result(self, item, page, row, col, dimensions):
      """創建佈局結果的統一方法"""
  ```

#### 任務 2.3：註冊系統改進
- [ ] **改進 `utils/core/registry.py`**
  - 線程安全的單例實現
  - 使用日誌替代 print 語句
  - 添加註冊驗證機制

### 階段三：TikZ 與 LaTeX 模組重構（5-6 天）

#### 任務 3.1：TikZ 輔助模組
- [ ] **`utils/tikz/coordinate_transform.py`**
  ```python
  def tikz_coordinate(point: Point, precision: int = 7) -> str
  def tikz_angle_degrees(radians: float) -> float
  def tikz_distance(value: float, unit: str = "cm") -> str
  ```

- [ ] **`utils/tikz/arc_parameters.py`**
  - 重構 `get_arc_render_params()` 為 `calculate_arc_params()`
  - 簡化角度計算邏輯
  - 使用 NumPy 向量運算

- [ ] **`utils/tikz/label_positioning.py`**
  - 分解巨大的 `get_label_placement_params()` 函數
  ```python
  class LabelPositioner:
      def position_vertex_label(self, vertex, adjacent_vertices, config)
      def position_side_label(self, p_start, p_end, triangle_vertices, config)
      def position_angle_label(self, vertex, arm1, arm2, config)
  ```

#### 任務 3.2：LaTeX 模組改進
- [ ] **`utils/latex/compiler.py`**
  - 添加編譯快取機制
  - 改進錯誤處理和日誌記錄
  - 清理臨時文件管理

- [ ] **`utils/latex/generator.py`**
  - 重構過長的生成方法
  - 分離圖形處理邏輯
  - 改善配置管理

- [ ] **`utils/latex/structure.py`**
  - 減少硬編碼的 LaTeX 樣式
  - 提供可配置的樣式選項
  - 模板化常用結構

#### 任務 3.3：圖形渲染改進
- [ ] **`utils/rendering/figure_renderer.py`**
  - 解耦與 `figures` 模組的直接依賴
  - 改進錯誤處理
  - 添加渲染快取

### 階段四：業務協調層重構（3-4 天）

#### 任務 4.1：PDF 生成器重構
- [ ] **`utils/orchestration/pdf_generator.py`**
  - 簡化 `_distribute_questions()` 複雜邏輯
  - 分離題目生成和分配邏輯
  - 改進錯誤處理和進度回報
  
  ```python
  class PDFOrchestrator:
      def __init__(self, config: GlobalConfig):
          self.config = config
          self.layout_engine = LayoutEngine()
          self.latex_generator = LaTeXGenerator()
          
      def generate_pdfs(self, output_config, content_config) -> PDFResult
  ```

#### 任務 4.2：統一 API 設計
- [ ] **`utils/__init__.py`**
  - 設計清晰的模組導入接口
  - 建立一致的 API 風格指南
  - 文檔化最佳使用方式
  ```python
  # 推薦的導入方式
  from utils.geometry import distance, construct_triangle, get_centroid
  from utils.tikz import position_vertex_label, calculate_arc_params
  from utils.orchestration import generate_pdf
  ```

### 階段五：測試與集成（3-4 天）

#### 任務 5.1：全面測試
- [ ] **單元測試**
  - 所有新模組的單元測試
  - 測試覆蓋率 > 90%
  - 邊界情況和錯誤處理測試

- [ ] **集成測試**
  - 與 `figures/predefined/predefined_triangle.py` 的集成測試
  - 完整的 PDF 生成流程測試
  - 性能基準測試

- [ ] **相容性測試**
  - 確保所有現有功能正常
  - 對比重構前後的輸出
  - 回歸測試

#### 任務 5.2：遷移與清理
- [ ] **代碼遷移**
  - 更新 `figures/predefined/predefined_triangle.py`
  - 檢查其他潛在調用方
  - 全局搜索確認完整遷移

- [ ] **最終清理**
  - 刪除舊的 `geometry_utils.py`
  - 清理未使用的導入和依賴
  - 更新文檔和示例

### 階段六：文檔與優化（2-3 天）

#### 任務 6.1：文檔完善
- [ ] API 文檔生成
- [ ] 使用指南和遷移指南
- [ ] 架構設計文檔
- [ ] 性能對比報告

#### 任務 6.2：性能優化
- [ ] 基於測試結果的性能調優
- [ ] 記憶體使用優化
- [ ] 編譯快取實現
- [ ] 並發處理改進（如適用）

## 依賴管理

### 新增依賴
```python
# requirements.txt 新增
numpy>=1.21.0        # 數值計算
sympy>=1.9.0         # 符號數學計算

# 開發依賴
pytest>=6.0.0        # 測試框架
pytest-cov>=2.12.0   # 測試覆蓋率
pytest-benchmark>=3.4.1  # 性能基準測試
```

### 依賴策略
- **核心功能不依賴重量級庫**：基礎幾何計算提供純 Python 備用
- **可選依賴**：NumPy/SymPy 作為可選的性能增強
- **版本鎖定**：確保依賴版本穩定性

## 風險評估與應對

### 主要風險
1. **重構範圍大**：涉及多個核心模組
   - **應對**：分階段實施，每階段都有完整測試
   
2. **性能影響**：新的抽象層可能影響性能
   - **應對**：建立性能基準，提供性能監控

3. **依賴風險**：新增 NumPy/SymPy 依賴
   - **應對**：提供純 Python 備用實現，依賴可選

4. **集成複雜**：多個模組同時變更
   - **應對**：強化集成測試，建立自動化驗證

### 回滾策略
1. **版本控制**：每個階段都有明確的 git 標籤
2. **備份機制**：保留所有原始文件的備份
3. **漸進部署**：可以階段性回滾到任意階段
4. **功能開關**：關鍵功能提供新舊實現切換

## 成功標準

### 代碼品質指標
- [ ] 單元測試覆蓋率 > 90%
- [ ] 集成測試覆蓋率 > 80%
- [ ] 單個模組文件行數 < 300 行
- [ ] 無調試輸出洩漏到生產環境
- [ ] 無循環依賴，依賴關係清晰
- [ ] 代碼重複率 < 5%

### 功能性指標
- [ ] 所有現有功能正常運作
- [ ] PDF 生成結果與重構前一致
- [ ] 所有圖形類型正確渲染
- [ ] 錯誤處理機制完善

### 性能指標
- [ ] 基礎運算性能不低於原實現
- [ ] 複雜計算（三角形特殊點）性能提升 > 20%
- [ ] PDF 生成時間不增加 > 10%
- [ ] 記憶體使用增加 < 50%

### 可維護性指標
- [ ] 新增功能只需修改對應模組
- [ ] 清晰的錯誤信息和日誌
- [ ] API 設計直觀易用
- [ ] 文檔完整，示例清晰

## 時間安排與資源分配

| 階段 | 主要任務 | 預估時間 | 關鍵風險 | 輸出物 |
|------|----------|----------|----------|--------|
| 1 | 基礎設施建立 | 3-4 天 | 架構設計風險 | 新目錄結構、基礎設施代碼 |
| 2 | 核心模組重構 | 4-5 天 | 數學計算精度風險 | 幾何計算模組、佈局引擎 |
| 3 | TikZ/LaTeX 重構 | 5-6 天 | LaTeX 相容性風險 | 渲染相關模組 |
| 4 | 業務協調層 | 3-4 天 | 功能集成風險 | PDF 生成協調器 |
| 5 | 測試與集成 | 3-4 天 | 測試覆蓋率風險 | 測試套件、遷移完成 |
| 6 | 文檔與優化 | 2-3 天 | 文檔完整性風險 | 文檔、性能報告 |

**總計：20-26 天**

## 後續改進規劃

重構完成後的持續改進方向：

### 短期改進（1-3 個月）
1. **性能監控系統**：建立性能指標收集和監控
2. **更多數學功能**：擴展幾何形狀支持（橢圓、多邊形）
3. **模板系統**：可配置的 LaTeX 樣式模板
4. **快取機制**：智能的計算和編譯快取

### 中期改進（3-6 個月）
1. **3D 幾何支持**：擴展到立體幾何計算
2. **並行處理**：大批量題目生成的並行化
3. **可視化工具**：幾何計算結果的即時預覽
4. **API 擴展**：提供 REST API 用於遠程調用

### 長期規劃（6-12 個月）
1. **多格式支持**：SVG、Canvas、WebGL 渲染器
2. **AI 集成**：智能的佈局優化和樣式建議
3. **雲端部署**：容器化和雲端服務支持
4. **插件系統**：第三方擴展機制

---

**文件版本**：2.0  
**創建日期**：2025-09-01  
**最後更新**：2025-09-01  
**狀態**：待執行  
**預估完成**：2025-09-27