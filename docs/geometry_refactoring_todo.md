# Utils 模組全面重構 Todo List

## 專案概述
全面重構 `utils/` 模組，從單一巨大的 `geometry_utils.py` 分離為現代化的模組架構，同時清理整個 utils 目錄的代碼品質問題。

**預估總時間**：20-26 天  
**重構策略**：乾淨重構，不保留向後相容接口  
**主要影響**：`figures/predefined/predefined_triangle.py` 需同步更新  

---

## 🏗️ 階段一：基礎設施建立 (3-4 天)

### 📁 任務 1.1：創建新架構目錄結構
- [ ] 創建 `utils/core/` 目錄及 `__init__.py`
- [ ] 創建 `utils/geometry/` 目錄及 `__init__.py`  
- [ ] 創建 `utils/tikz/` 目錄及 `__init__.py`
- [ ] 創建 `utils/latex/` 目錄及 `__init__.py`
- [ ] 創建 `utils/rendering/` 目錄及 `__init__.py`
- [ ] 創建 `utils/orchestration/` 目錄及 `__init__.py`

### ⚙️ 任務 1.2：統一基礎設施建立

#### 任務 1.2.1：統一配置管理
- [ ] **創建 `utils/core/config.py`**
  ```python
  class GlobalConfig:
      def __init__(self):
          self.debug_mode = False
          self.log_level = "INFO"
          self.math_backend_default = "numpy"
          self.tikz_precision = 7
          self.latex_font_path = "./assets/fonts/"
          self.pdf_compiler_timeout = 120
  ```

#### 任務 1.2.2：統一日誌系統  
- [ ] **創建 `utils/core/logging.py`**
  ```python
  import logging
  from typing import Optional
  
  def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
      logger = logging.getLogger(name)
      if not logger.handlers:  # 避免重複添加 handler
          handler = logging.StreamHandler()
          formatter = logging.Formatter(
              '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
          )
          handler.setFormatter(formatter)
          logger.addHandler(handler)
          logger.setLevel(getattr(logging, level.upper()))
      return logger
  ```

#### 任務 1.2.3：清理現有代碼品質問題
- [ ] **修復 `utils/registry.py`**
  - [ ] 移除第 42, 65-68 行的調試 print 語句
  - [ ] 替換為統一日誌系統
  - [ ] 實現線程安全的單例模式
  
- [ ] **修復 `utils/layout_engine.py`**  
  - [ ] 移除第 25 行的臨時註釋「暫時改行八行試試看四月二十四日」
  - [ ] 移除第 79 行的調試 print 語句
  - [ ] 提取重複的放置邏輯（第 94-147 行）
  
- [ ] **清理 `utils/pdf_generator.py`**
  - [ ] 修復第 159-161 行的空白行和縮排問題
  - [ ] 清理格式不一致的地方

### 🧪 任務 1.3：建立測試框架
- [ ] 創建 `tests/test_utils/` 目錄結構
  ```
  tests/test_utils/
  ├── test_core/
  ├── test_geometry/  
  ├── test_tikz/
  ├── test_latex/
  ├── test_rendering/
  └── test_orchestration/
  ```
- [ ] 設置 `pytest.ini` 配置文件
- [ ] 創建測試工具函數 `tests/test_utils/conftest.py`
- [ ] 建立基準測試數據集

---

## 🧮 階段二：核心模組重構 (4-5 天)

### 📐 任務 2.1：幾何計算模組實施

#### 任務 2.1.1：數學後端集成
- [ ] **創建 `utils/geometry/math_backend.py`**
  ```python
  import math
  import numpy as np
  import sympy
  from typing import Tuple, Union, Literal
  from .types import Point
  
  BackendType = Literal['numpy', 'sympy', 'python']
  
  class MathBackend:
      @staticmethod
      def distance(p1: Point, p2: Point, backend: BackendType = 'numpy') -> float:
          if backend == 'numpy':
              return np.linalg.norm(np.array(p2) - np.array(p1))
          elif backend == 'sympy':
              sp1 = sympy.geometry.Point(p1)
              sp2 = sympy.geometry.Point(p2)
              return float(sp1.distance(sp2))
          else:  # python
              return math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)
  ```

#### 任務 2.1.2：類型和異常定義
- [ ] **創建 `utils/geometry/types.py`**
  ```python
  from typing import Tuple, NamedTuple
  
  Point = Tuple[float, float]
  Vector = Tuple[float, float]
  
  class Triangle(NamedTuple):
      p1: Point
      p2: Point  
      p3: Point
      
  class Circle(NamedTuple):
      center: Point
      radius: float
  ```

- [ ] **創建 `utils/geometry/exceptions.py`**
  ```python
  class GeometryError(Exception):
      """幾何計算基礎異常"""
      pass
      
  class TriangleConstructionError(GeometryError):
      """三角形構造異常"""
      pass
      
  class InvalidGeometryError(GeometryError):
      """無效幾何異常"""
      pass
  ```

#### 任務 2.1.3：基礎運算模組
- [ ] **創建 `utils/geometry/basic_ops.py`**
  - [ ] `distance(p1: Point, p2: Point, backend: str = 'numpy') -> float`
  - [ ] `get_midpoint(p1: Point, p2: Point) -> Point`
  - [ ] `angle_between_points(p1: Point, vertex: Point, p2: Point) -> float`
  - [ ] `normalize_angle(angle_rad: float) -> float`
  - [ ] `degrees_to_radians(degrees: float) -> float`
  - [ ] `radians_to_degrees(radians: float) -> float`

#### 任務 2.1.4：三角形構造模組
- [ ] **創建 `utils/geometry/triangle_construction.py`**
  - [ ] `construct_triangle_sss(side_a: float, side_b: float, side_c: float) -> Triangle`
    - [ ] 實現三角形不等式驗證
    - [ ] 使用餘弦定理計算第三個頂點
    - [ ] 使用 NumPy 向量運算提升精度
  - [ ] `construct_triangle_sas(side1: float, angle_rad: float, side2: float) -> Triangle`
  - [ ] `construct_triangle_asa(angle1_rad: float, side_length: float, angle2_rad: float) -> Triangle`
  - [ ] `construct_triangle_aas(angle1_rad: float, angle2_rad: float, side_opposite_angle1: float) -> Triangle`
  - [ ] `construct_triangle_coordinates(p1: Point, p2: Point, p3: Point) -> Triangle`
  - [ ] **統一接口 `construct_triangle(mode: str, **kwargs) -> Triangle`**

#### 任務 2.1.5：三角形特殊點模組
- [ ] **創建 `utils/geometry/triangle_centers.py`**
  - [ ] `get_centroid(triangle: Triangle, backend: str = 'sympy') -> Point`
  - [ ] `get_incenter(triangle: Triangle, backend: str = 'sympy') -> Point`
  - [ ] `get_circumcenter(triangle: Triangle, backend: str = 'sympy') -> Point`
  - [ ] `get_orthocenter(triangle: Triangle, backend: str = 'sympy') -> Point`
  - [ ] `get_all_centers(triangle: Triangle) -> Dict[str, Point]` (便利函數)

#### 任務 2.1.6：向量運算模組 (新增)
- [ ] **創建 `utils/geometry/vector_ops.py`**
  - [ ] `vector_from_points(p1: Point, p2: Point) -> Vector`
  - [ ] `vector_magnitude(v: Vector) -> float`
  - [ ] `vector_normalize(v: Vector) -> Vector`
  - [ ] `vector_dot(v1: Vector, v2: Vector) -> float`
  - [ ] `vector_cross_2d(v1: Vector, v2: Vector) -> float`
  - [ ] `vector_rotate(v: Vector, angle_rad: float) -> Vector`
  - [ ] `vector_perpendicular(v: Vector) -> Vector`

#### 任務 2.1.7：圓運算模組 (新增)
- [ ] **創建 `utils/geometry/circle_ops.py`**
  - [ ] `circle_from_center_radius(center: Point, radius: float) -> Circle`
  - [ ] `circle_from_three_points(p1: Point, p2: Point, p3: Point) -> Circle`
  - [ ] `point_on_circle(circle: Circle, angle_rad: float) -> Point`
  - [ ] `circle_intersection(c1: Circle, c2: Circle) -> List[Point]`

#### 任務 2.1.8：統一導入接口
- [ ] **創建 `utils/geometry/__init__.py`**
  ```python
  # 基礎運算
  from .basic_ops import distance, get_midpoint, angle_between_points
  
  # 三角形構造 (統一接口)
  from .triangle_construction import construct_triangle
  
  # 三角形特殊點
  from .triangle_centers import get_centroid, get_incenter, get_circumcenter, get_orthocenter
  
  # 類型和異常
  from .types import Point, Triangle, Circle
  from .exceptions import GeometryError, TriangleConstructionError
  ```

### 🔧 任務 2.2：佈局引擎重構

#### 任務 2.2.1：重構 `utils/core/layout_engine.py`
- [ ] **提取重複的放置邏輯**
  ```python
  def _try_place_item(self, item_data, current_page, grids, width_cells, height_cells):
      """提取的通用放置方法"""
      for row in range(self.grid_height - height_cells + 1):
          for col in range(self.grid_width - width_cells + 1):
              if self.can_place_at(current_page, row, col, width_cells, height_cells, grids):
                  return self._mark_and_create_result(item_data, current_page, row, col, width_cells, height_cells, grids)
      return None
      
  def _mark_and_create_result(self, item_data, page, row, col, width_cells, height_cells, grids):
      """標記佔用並創建佈局結果"""
      # 標記佔用
      for r in range(height_cells):
          for c in range(width_cells):
              grids[page][row + r][col + c] = True
      
      # 創建結果
      return self._create_layout_result(item_data, page, row, col, width_cells, height_cells)
  ```

- [ ] **改善可讀性和可測試性**
- [ ] **添加配置選項支持**

### 🗂️ 任務 2.3：註冊系統改進

#### 任務 2.3.1：重構 `utils/core/registry.py`
- [ ] **實現線程安全的單例模式**
  ```python
  import threading
  
  class GeneratorRegistry:
      _instance = None
      _lock = threading.Lock()
      
      def __new__(cls):
          if cls._instance is None:
              with cls._lock:
                  if cls._instance is None:  # Double-check locking
                      cls._instance = super().__new__(cls)
                      cls._instance._generators = {}
                      cls._instance._category_map = {}
          return cls._instance
  ```

- [ ] **使用日誌替代 print 語句**
- [ ] **添加註冊驗證機制**
- [ ] **改進錯誤處理**

---

## 🎨 階段三：TikZ 與 LaTeX 模組重構 (5-6 天)

### 🏷️ 任務 3.1：TikZ 輔助模組實施

#### 任務 3.1.1：TikZ 類型定義
- [ ] **創建 `utils/tikz/types.py`**
  ```python
  from typing import Dict, Any, Optional, NamedTuple
  from utils.geometry.types import Point
  
  class LabelPosition(NamedTuple):
      reference_point: Point
      anchor: Optional[str]
      rotation: Optional[float]
      offset: float
      
  class ArcParams(NamedTuple):
      center: Point
      radius: float
      start_angle_rad: float
      end_angle_rad: float
      type: str  # 'arc' or 'right_angle'
  ```

#### 任務 3.1.2：座標轉換模組
- [ ] **創建 `utils/tikz/coordinate_transform.py`**
  - [ ] `tikz_coordinate(point: Point, precision: int = 7) -> str`
  - [ ] `tikz_angle_degrees(radians: float) -> float`
  - [ ] `tikz_distance(value: float, unit: str = "cm") -> str`
  - [ ] `tikz_color_normalize(color: str) -> str`
  - [ ] `tikz_options_format(options: Dict[str, Any]) -> str`

#### 任務 3.1.3：角弧參數模組
- [ ] **創建 `utils/tikz/arc_parameters.py`**
  - [ ] **重構 `get_arc_render_params()` → `calculate_arc_params()`**
    ```python
    def calculate_arc_params(vertex: Point, arm1: Point, arm2: Point, 
                           radius_config="auto") -> ArcParams:
        """計算角弧渲染參數，使用 NumPy 向量運算簡化邏輯"""
    ```
  - [ ] `calculate_right_angle_params(vertex: Point, arm1: Point, arm2: Point, size: float) -> Dict`
  - [ ] `format_tikz_arc(arc_params: ArcParams) -> str` (直接生成 TikZ 代碼)

#### 任務 3.1.4：標籤定位模組
- [ ] **創建 `utils/tikz/label_positioning.py`**

**基礎定位器類：**
- [ ] **`LabelPositioner` 基類**
  ```python
  class LabelPositioner:
      def __init__(self, config=None):
          self.config = config or {}
          
      def _calculate_outward_direction(self, vertex: Point, adjacent_vertices: List[Point]) -> Vector:
          """計算向外的方向向量"""
          
      def _avoid_collision(self, position: LabelPosition, existing_positions: List[LabelPosition]) -> LabelPosition:
          """避免標籤碰撞"""
  ```

**專門定位器：**
- [ ] **`VertexLabelPositioner(LabelPositioner)`**
  ```python
  def position(self, vertex: Point, adjacent_vertices: List[Point], offset: float = 0.15) -> LabelPosition:
      """頂點標籤定位：角平分線外側方向"""
  ```

- [ ] **`SideLabelPositioner(LabelPositioner)`**
  ```python
  def position(self, p_start: Point, p_end: Point, triangle_vertices: List[Point], 
               offset: float = 0.15) -> LabelPosition:
      """邊標籤定位：垂直方向偏移，自動選擇內側/外側"""
  ```

- [ ] **`AngleLabelPositioner(LabelPositioner)`**
  ```python
  def position(self, vertex: Point, arm1: Point, arm2: Point, 
               offset: float = 0.15) -> LabelPosition:
      """角標籤定位：角平分線方向，考慮與角弧協調"""
  ```

**統一接口函數：**
- [ ] `position_vertex_label(**kwargs) -> LabelPosition`
- [ ] `position_side_label(**kwargs) -> LabelPosition`
- [ ] `position_angle_label(**kwargs) -> LabelPosition`

#### 任務 3.1.5：佈局輔助模組 (新增)
- [ ] **創建 `utils/tikz/layout_helpers.py`**
  - [ ] `calculate_bounding_box(elements: List) -> BoundingBox`
  - [ ] `avoid_overlap(label_positions: List[LabelPosition]) -> List[LabelPosition]`
  - [ ] `optimize_spacing(elements: List) -> LayoutResult`
  - [ ] `align_elements(elements: List, alignment: str) -> List`

#### 任務 3.1.6：TikZ 統一接口
- [ ] **創建 `utils/tikz/__init__.py`**
  ```python
  # 標籤定位
  from .label_positioning import position_vertex_label, position_side_label, position_angle_label
  
  # 角弧參數
  from .arc_parameters import calculate_arc_params
  
  # 座標轉換
  from .coordinate_transform import tikz_coordinate, tikz_angle_degrees
  
  # 類型
  from .types import LabelPosition, ArcParams
  ```

### 📄 任務 3.2：LaTeX 模組改進

#### 任務 3.2.1：LaTeX 配置分離
- [ ] **創建 `utils/latex/config.py`**
  - [ ] 從 `latex_config.py` 遷移配置邏輯
  - [ ] 增強配置選項（字體、樣式、版面）
  - [ ] 提供配置驗證機制

#### 任務 3.2.2：PDF 編譯器改進
- [ ] **重構 `utils/latex/compiler.py`**
  - [ ] **添加編譯快取機制**
    ```python
    import hashlib
    from pathlib import Path
    
    class PDFCompiler:
        def __init__(self):
            self._cache_dir = Path("./.latex_cache")
            self._cache_dir.mkdir(exist_ok=True)
            
        def compile_with_cache(self, tex_content: str, cache_key: str):
            content_hash = hashlib.md5(tex_content.encode()).hexdigest()
            cache_file = self._cache_dir / f"{cache_key}_{content_hash}.pdf"
            if cache_file.exists():
                return str(cache_file)
            # ... 正常編譯流程
    ```
  - [ ] 改進錯誤處理和日誌記錄
  - [ ] 優化臨時文件管理
  - [ ] 添加編譯進度回報

#### 任務 3.2.3：LaTeX 生成器重構
- [ ] **重構 `utils/latex/generator.py`**
  - [ ] 分解過長的 `generate_question_tex()` 方法
  - [ ] 分離圖形處理邏輯到獨立方法
  - [ ] 改善配置管理和依賴注入
  - [ ] 提升代碼可測試性

#### 任務 3.2.4：文檔結構清理
- [ ] **重構 `utils/latex/structure.py`**
  - [ ] 減少硬編碼的 LaTeX 樣式
  - [ ] 提供可配置的樣式選項
  - [ ] 模板化常用結構
  - [ ] 支持自定義樣式主題

### 🖼️ 任務 3.3：圖形渲染改進

#### 任務 3.3.1：圖形渲染器解耦
- [ ] **重構 `utils/rendering/figure_renderer.py`**
  - [ ] 解耦與 `figures` 模組的直接依賴
    ```python
    class FigureRenderer:
        def __init__(self, figure_registry=None):
            self.figure_registry = figure_registry or self._default_registry()
            
        def _default_registry(self):
            # 延遲導入，避免循環依賴
            import figures
            return figures
    ```
  - [ ] 改進錯誤處理和日誌
  - [ ] 添加渲染結果快取
  - [ ] 支持渲染中間件（pre/post processing）

---

## 🎭 階段四：業務協調層重構 (3-4 天)

### 📊 任務 4.1：PDF 生成器重構

#### 任務 4.1.1：重構 PDF 生成協調器
- [ ] **創建 `utils/orchestration/pdf_generator.py`**

**主要協調器類：**
```python
from utils.core.config import GlobalConfig
from utils.core.layout_engine import LayoutEngine
from utils.latex.generator import LaTeXGenerator
from utils.latex.compiler import PDFCompiler

class PDFOrchestrator:
    def __init__(self, config: GlobalConfig = None):
        self.config = config or GlobalConfig()
        self.layout_engine = LayoutEngine()
        self.latex_generator = LaTeXGenerator(self.config.latex)
        self.pdf_compiler = PDFCompiler()
        
    def generate_pdfs(self, output_config: OutputConfig, content_config: ContentConfig) -> PDFResult:
        """統一的 PDF 生成接口"""
```

**具體重構任務：**
- [ ] **簡化 `_distribute_questions()` 複雜邏輯**
  - [ ] 分離題目生成邏輯 → `QuestionGenerator`
  - [ ] 分離題目分配邏輯 → `QuestionDistributor`  
  - [ ] 分離排序邏輯 → `QuestionSorter`

- [ ] **改進錯誤處理和進度回報**
  ```python
  def generate_pdfs_with_progress(self, config, progress_callback=None):
      """支持進度回報的 PDF 生成"""
      stages = ['生成題目', '計算佈局', '生成 LaTeX', '編譯 PDF']
      for i, stage in enumerate(stages):
          if progress_callback:
              progress_callback(stage, i / len(stages))
          # ... 執行對應階段
  ```

- [ ] **模組化依賴注入**
- [ ] **統一結果類型定義**

### 🔌 任務 4.2：統一 API 設計

#### 任務 4.2.1：設計清晰的導入接口
- [ ] **重寫 `utils/__init__.py`**
  ```python
  """Utils 模組統一接口
  
  推薦的導入方式：
  
  # 幾何計算
  from utils.geometry import distance, construct_triangle, get_centroid
  
  # TikZ 輔助  
  from utils.tikz import position_vertex_label, calculate_arc_params
  
  # PDF 生成
  from utils.orchestration import generate_pdf
  
  # 配置管理
  from utils.core.config import GlobalConfig
  """
  
  # 便利導入（可選）
  from .orchestration.pdf_generator import PDFOrchestrator as generate_pdf
  ```

#### 任務 4.2.2：建立 API 風格指南
- [ ] 制定一致的命名規範
- [ ] 定義參數傳遞模式
- [ ] 建立錯誤處理標準
- [ ] 設計日誌記錄規範

#### 任務 4.2.3：文檔化最佳使用方式
- [ ] 編寫 API 使用範例
- [ ] 創建常見用法模式文檔
- [ ] 建立故障排除指南

---

## 🧪 階段五：測試與集成 (3-4 天)

### ✅ 任務 5.1：全面測試實施

#### 任務 5.1.1：單元測試
**所有新模組的單元測試，目標覆蓋率 > 90%**

- [ ] **`tests/test_utils/test_geometry/`**
  - [ ] `test_basic_ops.py` - 基礎運算精度測試
    ```python
    def test_distance_accuracy():
        # 測試已知距離：3-4-5 直角三角形
        p1, p2 = (0, 0), (3, 4)
        assert abs(distance(p1, p2) - 5.0) < 1e-10
    ```
  - [ ] `test_triangle_construction.py` - 各種構造方法測試
  - [ ] `test_triangle_centers.py` - 特殊點精度測試
  - [ ] `test_math_backend.py` - 不同後端對比測試

- [ ] **`tests/test_utils/test_tikz/`**
  - [ ] `test_label_positioning.py` - 標籤定位邏輯測試
  - [ ] `test_coordinate_transform.py` - TikZ 格式轉換測試
  - [ ] `test_arc_parameters.py` - 角弧參數計算測試

- [ ] **`tests/test_utils/test_latex/`**
  - [ ] `test_compiler.py` - PDF 編譯功能測試
  - [ ] `test_generator.py` - LaTeX 生成邏輯測試

- [ ] **`tests/test_utils/test_core/`**
  - [ ] `test_layout_engine.py` - 佈局算法測試
  - [ ] `test_registry.py` - 註冊系統測試

#### 任務 5.1.2：邊界情況和錯誤處理測試
- [ ] **測試退化情況**
  - [ ] 共線三點的三角形處理
  - [ ] 零長度邊的處理
  - [ ] 無效角度的處理

- [ ] **測試錯誤恢復**
  - [ ] LaTeX 編譯失敗的處理
  - [ ] 圖形生成錯誤的處理
  - [ ] 記憶體不足的處理

- [ ] **測試性能邊界**
  - [ ] 大量題目的佈局性能
  - [ ] 複雜幾何計算的時間限制
  - [ ] 記憶體使用監控

### 🔗 任務 5.2：集成測試

#### 任務 5.2.1：與現有代碼的集成測試
- [ ] **與 `figures/predefined/predefined_triangle.py` 的集成測試**
  - [ ] 測試所有參數組合的圖形生成
  - [ ] 驗證生成的 TikZ 代碼語法正確性
  - [ ] 對比重構前後的渲染結果

- [ ] **完整 PDF 生成流程測試**
  - [ ] 端到端測試：從題目配置到 PDF 輸出
  - [ ] 測試各種題目組合和佈局情況
  - [ ] 驗證 PDF 文件的完整性

#### 任務 5.2.2：性能基準測試
- [ ] **建立性能基準**
  ```python
  # 使用 pytest-benchmark
  def test_distance_performance(benchmark):
      p1, p2 = (0, 0), (1000, 1000)
      result = benchmark(distance, p1, p2)
      assert result > 0
  ```

- [ ] **對比測試**
  - [ ] NumPy vs SymPy vs 純 Python 後端性能
  - [ ] 新舊實現的性能對比
  - [ ] 記憶體使用量對比

#### 任務 5.2.3：回歸測試
- [ ] **確保所有現有功能正常**
- [ ] **對比重構前後的輸出一致性**
- [ ] **建立自動化回歸測試套件**

### 🔄 任務 5.3：遷移與清理

#### 任務 5.3.1：代碼遷移
- [ ] **更新 `figures/predefined/predefined_triangle.py`**
  ```python
  # 舊的導入
  from utils.geometry_utils import (
      get_vertices, TriangleDefinitionError,
      get_midpoint, get_centroid, get_incenter, get_circumcenter, get_orthocenter,
      get_arc_render_params, get_label_placement_params, _distance
  )
  
  # 新的導入
  from utils.geometry import (
      construct_triangle, TriangleConstructionError,
      get_midpoint, get_centroid, get_incenter, get_circumcenter, get_orthocenter,
      distance
  )
  from utils.tikz import (
      calculate_arc_params, position_vertex_label, position_side_label, position_angle_label
  )
  ```

- [ ] **具體函數調用更新**
  - [ ] `get_vertices(**params)` → `construct_triangle(mode, **params)`
  - [ ] `get_label_placement_params(element_type='vertex', ...)` → `position_vertex_label(...)`
  - [ ] `get_label_placement_params(element_type='side', ...)` → `position_side_label(...)`
  - [ ] `get_label_placement_params(element_type='angle_value', ...)` → `position_angle_label(...)`
  - [ ] `get_arc_render_params(...)` → `calculate_arc_params(...)`
  - [ ] `_distance(...)` → `distance(...)`

- [ ] **檢查其他潛在調用方**
  - [ ] 全局搜索 `from utils.geometry_utils import`
  - [ ] 全局搜索 `import utils.geometry_utils`
  - [ ] 確認所有調用點都已更新

#### 任務 5.3.2：最終清理
- [ ] **刪除舊文件**
  - [ ] 備份原始 `utils/geometry_utils.py` 到 `backup/` 目錄
  - [ ] 刪除 `utils/geometry_utils.py`

- [ ] **清理依賴**
  - [ ] 移除未使用的導入語句
  - [ ] 更新 `requirements.txt`（如有新依賴）
  - [ ] 清理臨時文件和測試數據

- [ ] **最終驗證**
  - [ ] 運行完整的測試套件
  - [ ] 確保所有測試通過
  - [ ] 驗證 PDF 生成功能完整性
  - [ ] 檢查日誌輸出的正確性

---

## 📚 階段六：文檔與優化 (2-3 天)

### 📖 任務 6.1：文檔完善

#### 任務 6.1.1：API 文檔生成
- [ ] 使用 Sphinx 建立自動化文檔生成
- [ ] 為所有公開 API 編寫 docstring
- [ ] 生成 HTML 格式的 API 參考文檔

#### 任務 6.1.2：使用指南編寫
- [ ] **重構後的使用指南**
  - [ ] 新架構概覽
  - [ ] 常用功能使用範例
  - [ ] 最佳實踐建議

- [ ] **遷移指南**
  - [ ] 舊 API → 新 API 對應表
  - [ ] 遷移步驟詳解
  - [ ] 常見問題解答

#### 任務 6.1.3：架構設計文檔
- [ ] 模組設計理念說明
- [ ] 依賴關係圖
- [ ] 擴展開發指南

### ⚡ 任務 6.2：性能優化

#### 任務 6.2.1：基於測試結果的性能調優
- [ ] 分析性能測試結果
- [ ] 識別性能瓶頸
- [ ] 實施針對性優化

#### 任務 6.2.2：記憶體使用優化
- [ ] 分析記憶體使用模式
- [ ] 優化大對象的生命週期
- [ ] 實施適當的快取策略

#### 任務 6.2.3：編譯快取實現
- [ ] **智能快取策略**
  ```python
  class CompilationCache:
      def __init__(self, max_size=100):
          self.cache = {}
          self.max_size = max_size
          self.access_times = {}
          
      def get_cache_key(self, tex_content, config):
          # 基於內容和配置生成快取鍵
          content_hash = hashlib.md5(tex_content.encode()).hexdigest()
          config_hash = hashlib.md5(str(config).encode()).hexdigest()
          return f"{content_hash}_{config_hash}"
  ```

#### 任務 6.2.4：並發處理改進
- [ ] 評估並發處理的可行性
- [ ] 實施安全的並行計算（如適用）
- [ ] 測試併發情況下的正確性

---

## 📊 品質檢查清單

### 代碼品質指標
- [ ] 單元測試覆蓋率 > 90%
- [ ] 集成測試覆蓋率 > 80%
- [ ] 單個模組文件行數 < 300 行
- [ ] 無調試輸出洩漏到生產環境
- [ ] 無循環依賴，依賴關係清晰
- [ ] 代碼重複率 < 5%
- [ ] 所有公開 API 都有完整 docstring
- [ ] 通過代碼風格檢查（flake8, black）

### 功能性指標
- [ ] 所有現有功能正常運作
- [ ] PDF 生成結果與重構前一致
- [ ] 所有圖形類型正確渲染  
- [ ] 錯誤處理機制完善
- [ ] 日誌輸出格式統一且有意義
- [ ] 配置系統運作正常

### 性能指標
- [ ] 基礎運算性能不低於原實現
- [ ] 複雜計算（三角形特殊點）性能提升 > 20%
- [ ] PDF 生成時間不增加 > 10%
- [ ] 記憶體使用增加 < 50%
- [ ] 編譯快取有效減少重複編譯時間

### 可維護性指標  
- [ ] 新增功能只需修改對應模組
- [ ] 清晰的錯誤信息和日誌
- [ ] API 設計直觀易用
- [ ] 文檔完整，示例清晰
- [ ] 模組間的耦合度低
- [ ] 易於進行單元測試

---

## 🚨 風險控制

### 每日檢查點
- [ ] **每日結束前**：運行完整測試套件，確保當日修改不破壞現有功能
- [ ] **每完成一個任務**：提交 git commit，打上適當標籤
- [ ] **每完成一個階段**：創建 git 分支標記，可以快速回滾

### 回滾準備
- [ ] **階段一完成前**：創建完整的項目備份
- [ ] **每階段完成**：標記穩定版本，可獨立回滾
- [ ] **緊急回滾計畫**：準備腳本快速恢復到任一階段

### 進度監控
- [ ] **每日進度報告**：記錄完成的任務和遇到的問題
- [ ] **每階段里程碑檢查**：評估是否達到階段目標
- [ ] **風險預警機制**：及時識別和應對潛在風險

---

**狀態：** 📋 Ready to Execute  
**創建日期：** 2025-09-01  
**預計開始：** 待定  
**預計完成：** 開始後 20-26 天  
**優先級：** 🔥 High Priority

**下一步行動：** 執行階段一任務 1.1 - 創建新架構目錄結構