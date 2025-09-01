# 重構計畫：新一代三角形生成器 (v2.1)

## 1. 總體目標與原則

*   完全重做三角形生成器 (`triangle_generator`) 和三角形標籤增強 (`triangle_label_enhancement`) 功能。
*   嚴格遵循 `docs/figure_development_guide.md` 的架構和最佳實踐。
*   核心原則是**關注點分離**：將複雜的幾何計算與圖形渲染邏輯徹底分開。

## 2. 核心組件及其職責

### 2.1. `GeometryUtils` (`utils/geometry_utils.py`) - 強化的幾何計算與定位決策引擎

*   **職責：** 負責所有核心的幾何計算、特殊點（內心、中點、垂心等）的定位，以及為標籤和角弧生成精確的定位與繪製參數。
*   **API 設計重點：**
    *   提供一組**清晰、通用且易於使用**的函數接口。
    *   輸入參數應直觀，返回值應明確且易於下游組件使用（例如，返回標準化的座標元組、包含 TikZ 選項的字典等）。
    *   內部實現應高度模塊化，例如：
        *   `get_vertices(definition_mode: str, **kwargs) -> Tuple[Point, Point, Point]`: 根據不同定義方式計算並返回標準化頂點座標。
        *   `get_special_point(point_type: str, p1, p2, p3, **kwargs) -> Point`: 計算如內心、垂心、中點等。
        *   `get_label_placement_params(element_type: str, target_coords, reference_coords, user_prefs) -> Dict`: 為頂點、邊、角度標籤計算最佳定位參數。
        *   `get_arc_render_params(vertex, adj_point1, adj_point2, arc_config) -> Dict`: 計算角弧繪製所需的參數。
*   **產出：** 精確的座標數據、定位建議（可能直接是 TikZ 可用的選項字符串或結構化數據）、繪圖參數。

### 2.2. 基礎圖形生成器 (位於 `figures/` 目錄下)

*   **`BasicTriangleGenerator` (`figures/basic_triangle.py` - 新建):**
    *   輸入：三個頂點座標及基本樣式。
    *   職責：繪製三角形的基本輪廓。
*   **`ArcGenerator` (`figures/arc.py` - 新建):**
    *   輸入：由 `GeometryUtils` 計算出的角弧繪製參數 (圓心、半徑、起止角度、是否直角符號等)。
    *   職責：繪製角弧或直角符號。
*   **`LabelGenerator` (`figures/label.py` - 現有，可能需審查/增強):**
    *   輸入：文本內容、由 `GeometryUtils` 計算出的精確定位參數及樣式。
    *   職責：在指定位置繪製文本標籤。

### 2.3. `PredefinedTriangleGenerator` (`figures/predefined/triangle.py` - 新建，集成單一入口)

*   **職責：** 作為用戶與三角形生成功能的主要接口，負責協調和裝配。
*   接收 `PredefinedTriangleParams` (Pydantic 模型，定義用戶的輸入：三角形如何定義、需要哪些標籤、樣式等)。
*   **工作流程：**
    1.  解析 `PredefinedTriangleParams`。
    2.  調用 `GeometryUtils` 的各個接口，獲取所有必要的計算結果（標準化頂點座標、特殊點座標、標籤定位參數、角弧繪製參數等）。
    3.  基於從 `GeometryUtils` 獲取的精確參數，調用 `BasicTriangleGenerator`, `LabelGenerator`, `ArcGenerator` 來創建對應的 `SubFigureParams` 實例。
    4.  處理 `variant` (`question` vs `explanation`) 的差異化邏輯（例如，詳解中顯示更多輔助線或標註）。
    5.  將所有 `SubFigureParams` 收集到一個 `CompositeParams` 實例中。
    6.  調用 `CompositeFigureGenerator` 生成最終的 TikZ 圖形代碼。

## 3. 參數模型 (`figures/params_models.py`)

*   為上述所有生成器（`BasicTriangleParams`, `ArcParams`, `LabelParams` (如果修改), `PredefinedTriangleParams`）定義清晰、類型安全的 Pydantic 模型。
*   `PredefinedTriangleParams` 將是最核心和複雜的模型，需要精心設計其結構，以支持多種定義方式和豐富的自訂選項，同時保持易用性。

## 4. 開發步驟與測試

1.  **階段一：`GeometryUtils` 的設計與實現 (最高優先級)**
    *   詳細設計 `GeometryUtils` 的公共 API 接口。
    *   逐個實現其內部計算模塊 (頂點計算、特殊點計算、定位參數計算等)。
    *   為 `GeometryUtils` 的每個功能編寫詳盡的單元測試，確保計算的準確性。以下是詳細的測試策略：
        *   **測試案例設計與選擇：**
            *   **基準案例 (Known Good Cases):** 使用教科書經典例子（如3-4-5直角三角形、等邊三角形）進行驗證，這些案例的幾何屬性已知。
            *   **邊界與特殊條件測試：** 包括退化三角形、極端比例的三角形、以及零值/非法值輸入（預期拋出異常）。
            *   **參數化測試：** 利用測試框架（如 `pytest`）的參數化功能，使用多組輸入和預期輸出來測試同一個計算函數。
        *   **結果驗證方法：**
            *   **座標精確比較 (有容差):** 計算出的座標與預期座標比較時，必須使用小容差（epsilon）處理浮點數誤差（如 `pytest.approx` 或 `unittest.assertAlmostEqual`）。
            *   **幾何屬性逆向驗證:** 這是關鍵。例如，根據SSS輸入計算出頂點後，反向計算邊長是否與輸入一致；驗證內心到三邊距離相等；驗證外心到三頂點距離相等；驗證直角邊向量點積為零等。
            *   **不變性測試:** 驗證圖形在平移、旋轉（如果適用）後，其內在幾何屬性（邊長、角度）保持不變。
        *   **直觀驗證輔助：**
            *   **小型可視化輔助腳本 (強烈推薦):** 開發時編寫簡單 Python 腳本，使用 `matplotlib.pyplot` 等庫將 `GeometryUtils` 計算出的點、線、特殊點繪製出來，進行直觀檢查。這有助於快速反饋、調試複雜問題和理解定位邏輯。此腳本為開發者輔助工具，非單元測試的一部分。
            *   **詳細日誌輸出:** 在測試中選擇性打印關鍵中間步驟和最終結果，輔助人工核對。
            *   **與第三方工具交叉驗證:** 使用可靠的幾何軟體或線上計算器輸入相同參數，比較結果。
        *   **測試框架的運用：**
            *   使用 `pytest` 或 `unittest` 組織和運行測試。
            *   測試用例按 `GeometryUtils` 功能模塊組織 (e.g., `test_vertex_locators.py`, `test_special_points.py`)。

2.  **階段二：基礎圖形生成器的實現/審查**
    *   實現 `BasicTriangleGenerator` 及其參數模型和測試。
    *   實現 `ArcGenerator` 及其參數模型和測試。
    *   審查現有的 `LabelGenerator`，根據需要進行增強，並確保其參數模型能接收 `GeometryUtils` 輸出的定位參數。
3.  **階段三：預定義三角形生成器的設計與實現**
    *   詳細設計 `PredefinedTriangleParams` Pydantic 模型。
    *   實現 `PredefinedTriangleGenerator`，重點是其協調邏輯。
    *   編寫全面的集成測試，覆蓋不同的三角形定義方式、標籤組合和 `variant`。

## 5. Mermaid 流程圖

```mermaid
graph TD
    A[使用者提供 PredefinedTriangleParams<br>(定義方式, 數據, 標籤/樣式選項)] --> B{PredefinedTriangleGenerator};
    
    subgraph GeometryUtils_Core ["核心: GeometryUtils (utils/geometry_utils.py)"]
        direction TB
        GU_Vertices["1. get_vertices(mode, data)<br>   (返回 p1,p2,p3)"]
        GU_SpecialPoints["2. get_incenter/midpoint等<br>   (返回 特殊點座標)"]
        GU_PlacementLogic["3. get_vertex/side/angle_label_placement<br>   (返回 標籤定位參數)"]
        GU_ArcLogic["4. get_angle_arc_params<br>   (返回 角弧繪製參數)"]
    end

    B -- 調用 --> GU_Vertices;
    B -- 調用 --> GU_SpecialPoints;
    B -- 調用 --> GU_PlacementLogic;
    B -- 調用 --> GU_ArcLogic;
    
    GU_Vertices -- p1,p2,p3 --> B;
    GU_SpecialPoints -- 特殊點座標 --> B;
    GU_PlacementLogic -- 標籤定位參數 --> B;
    GU_ArcLogic -- 角弧繪製參數 --> B;

    subgraph FigureAssembly ["PredefinedTriangleGenerator 進行圖形裝配"]
        direction LR
        Assemble_Triangle["調用 BasicTriangleGenerator<br>使用 p1,p2,p3"]
        Assemble_Labels["調用 LabelGenerator<br>使用 標籤內容 + 定位參數"]
        Assemble_Arcs["調用 ArcGenerator<br>使用 角弧繪製參數"]
    end
    
    B --> Assemble_Triangle;
    B --> Assemble_Labels;
    B --> Assemble_Arcs;

    FigureAssembly -- 生成各 SubFigureParams --> CompositeCreation["組合為 CompositeParams"];
    CompositeCreation --> FinalComposite["調用 CompositeFigureGenerator"];
    FinalComposite -- 生成最終 TikZ --> K[TikZ 輸出];

    classDef core_util fill:#a8e6cf,stroke:#333,stroke-width:3px;
    class GeometryUtils_Core core_util;
    classDef coordinator_mod fill:#dcedc1,stroke:#333,stroke-width:2px;
    class B coordinator_mod;