# 三角形圖形生成器開發計劃

## 1. 目標

開發一套預定義複合圖形生成器，用於根據不同的幾何條件（SSS, SAS, ASA, AAS, RHS, 三點座標）生成三角形的 TikZ 圖形。這些生成器應能處理無效輸入，並允許用戶自定義頂點、邊長和角度的標註（可顯示數值或問號）。

## 2. 整體策略

為每種三角形的定義方式創建一個獨立的預定義複合圖形生成器。例如：

*   `PredefinedTriangleSSSGenerator`
*   `PredefinedTriangleSASGenerator`
*   `PredefinedTriangleASAGenerator`
*   `PredefinedTriangleAASGenerator`
*   `PredefinedTriangleRHSGenerator`
*   `PredefinedTriangleCoordinatesGenerator`

這些生成器將利用 `sympy.geometry` 模塊進行核心的幾何計算、屬性提取和有效性驗證。然後，它們會使用基礎圖形元件（如 `line`, `point`, `label`, `angle`）來構建最終的 TikZ 圖形。

未來可以考慮在這些核心生成器上逐步擴展功能，以支持常見的額外幾何元素（如中線、高線、內外接圓等），通過可選參數控制其顯示。

## 3. 核心組件與實現細節

### 3.1. 參數模型 (Pydantic Models)

每個 `PredefinedTriangle<Method>Generator` 都將有其專屬的 Pydantic 參數模型，繼承自 `BaseFigureParams`。

**通用標註參數示例（存在於每個模型中）：**

*   `variant: Literal['question', 'explanation']` (來自 `BaseFigureParams`)
*   `show_vertex_labels: bool = True`
*   `vertex_A_label: str = "A"`
*   `vertex_B_label: str = "B"`
*   `vertex_C_label: str = "C"`
*   `show_side_a_label: bool = False`
*   `side_a_label_value: Union[float, str] = "?"` (對應邊 BC)
*   `show_side_b_label: bool = False`
*   `side_b_label_value: Union[float, str] = "?"` (對應邊 AC)
*   `show_side_c_label: bool = False`
*   `side_c_label_value: Union[float, str] = "?"` (對應邊 AB)
*   `show_angle_A_label: bool = False`
*   `angle_A_label_value: Union[float, str] = "?"` (角度單位默認為度)
*   `angle_A_notation: Optional[Literal["arc", "right_angle"]] = "arc"`
*   `show_angle_B_label: bool = False`
*   `angle_B_label_value: Union[float, str] = "?"`
*   `angle_B_notation: Optional[Literal["arc", "right_angle"]] = "arc"`
*   `show_angle_C_label: bool = False`
*   `angle_C_label_value: Union[float, str] = "?"`
*   `angle_C_notation: Optional[Literal["arc", "right_angle"]] = "arc"`
*   `angle_unit: Literal['deg', 'rad'] = 'deg'` (用於輸入角度值的單位)

**特定方法的幾何參數：**

*   **`PredefinedTriangleSSSParams`**:
    *   `side_a: float` (長度)
    *   `side_b: float`
    *   `side_c: float`
*   **`PredefinedTriangleSASParams`**:
    *   `side_b: float`
    *   `angle_A: float` (角度值，單位由 `angle_unit` 指定)
    *   `side_c: float`
*   **`PredefinedTriangleASAParams`**:
    *   `angle_A: float`
    *   `side_c: float`
    *   `angle_B: float`
*   **`PredefinedTriangleAASParams`**:
    *   `angle_A: float`
    *   `angle_B: float`
    *   `side_a: float` (或其他非夾邊)
*   **`PredefinedTriangleRHSParams`**:
    *   `right_angle_vertex: Literal['A', 'B', 'C'] = 'C'`
    *   `hypotenuse: float` (斜邊長度)
    *   `one_leg: float` (一條直角邊長度)
*   **`PredefinedTriangleCoordinatesParams`**:
    *   `point_A: Tuple[float, float]` (例如 `(0,0)`)
    *   `point_B: Tuple[float, float]`
    *   `point_C: Tuple[float, float]`

### 3.2. `_build_composite_params` 方法

此方法是每個預定義複合圖形生成器的核心。

1.  **參數轉換與 SymPy 對象創建**：
    *   接收 Pydantic 驗證後的參數。
    *   如果輸入角度單位是 'deg'，轉換為弧度供 SymPy 使用。
    *   使用 `sympy.geometry.Point` 和 `sympy.geometry.Triangle` 等來表示和計算幾何實體。
    *   **SSS**: `sympy.geometry.Triangle(sss=(a,b,c))` 或通過計算頂點。
    *   **SAS**: 計算第三點座標。例如，A=(0,0), C=(b,0), B=(c\*cos(A_rad), c\*sin(A_rad)).
    *   **ASA**: 計算第三角 C = pi - A_rad - B_rad. 使用正弦定理計算另外兩邊 a, b。然後轉為 SAS。
    *   **AAS**: 計算第三角 C. 使用正弦定理計算另外兩邊。然後轉為 SAS。
    *   **RHS**: 假設直角在 C。C=(0,0)。若給定斜邊 h (AB) 和直角邊 a (BC)，則 B=(a,0), A=(0, sqrt(h^2-a^2))。
    *   **Coordinates**: 直接使用 `sympy.geometry.Point` 創建三頂點。

2.  **有效性驗證 (使用 SymPy)**：
    *   **SSS**: 檢查三角形不等式 (SymPy 的 `Triangle` 構造函數可能會自動處理)。
    *   **Coordinates**: 檢查三點是否共線 (`Triangle.area == 0`)。
    *   **RHS**: 檢查斜邊是否大於直角邊。
    *   其他方法：確保計算出的邊長為正，角度有效。

3.  **錯誤處理**：
    *   如果輸入無效或無法構成三角形，則準備一個 `CompositeParams` 實例，其子圖形只包含一個 `label`，顯示錯誤訊息 "無法構成三角形"。同時，在控制台 `print` 詳細的調試錯誤信息。

4.  **提取幾何數據**：
    *   從 SymPy `Triangle` 對象中提取三個頂點的最終數值座標 (`triangle.vertices`)。
    *   如果需要標註計算出的邊長或角度，從 `triangle.sides` 或 `triangle.angles` 提取（注意角度單位轉換回 'deg'）。

5.  **構建子圖形 (`SubFigureParams` 列表)**：
    *   **邊**: 使用 `line` 基礎圖形生成器繪製三條邊。
    *   **頂點標註**: 如果 `show_vertex_labels` 為 `True`，使用 `point` (可選，用於顯示點本身) 和 `label` 基礎圖形生成器在頂點位置標註 A, B, C。
    *   **邊長標註**: 如果 `show_side_x_label` 為 `True`，使用 `label` 在對應邊的中點附近標註 `side_x_label_value` (數值或 "?")。
    *   **角度標註**:
        *   如果 `show_angle_X_label` 為 `True`，使用 `label` 標註角度值。
        *   根據 `angle_X_notation`：
            *   `"arc"`: 使用 `angle` 基礎圖形生成器繪製角度弧線。
            *   `"right_angle"`: 使用特定的 TikZ 命令繪製直角符號 (例如 `\draw (V_prev) -- (V_curr) -- (V_next); \draw (V_curr)+(-0.2,0) -- +(-0.2,0.2) -- +(0,0.2);` 假設 V_curr 是直角頂點，需要調整大小和方向)。

6.  **返回 `CompositeParams`**：包含所有子圖形定義。

### 3.3. `generate_tikz` 方法

標準實現，調用 `_build_composite_params` 並使用 `CompositeFigureGenerator` 生成最終的 TikZ 代碼。

### 3.4. 文件結構與註冊

*   新的生成器類將位於 `figures/predefined/triangle_xxx.py` (例如 `figures/predefined/triangle_sss.py`)。
*   在 `figures/params_models.py` 中定義對應的 Pydantic 參數模型。
*   在 `figures/__init__.py` 中導入並使用 `@register_figure_generator` 裝飾器註冊所有新的三角形生成器。

## 4. 開發步驟

1.  **環境準備**：確保已安裝 SymPy (`pip install sympy`)。
2.  **參數模型定義**：在 `figures/params_models.py` 中為所有六種三角形定義方式創建 Pydantic 參數模型，包含幾何參數和詳細的標註選項。
3.  **逐個實現生成器**：
    *   建議從最簡單的 `PredefinedTriangleCoordinatesGenerator` 開始，然後是 `PredefinedTriangleSSSGenerator`，再到其他需要更複雜計算的類型。
    *   對於每個生成器：
        *   創建對應的 Python 文件 (例如 `figures/predefined/triangle_coordinates.py`)。
        *   實現生成器類，繼承自 `FigureGenerator`。
        *   實現 `get_name()` 方法。
        *   重點實現 `_build_composite_params()` 方法：
            *   集成 SymPy 進行座標計算和驗證。
            *   處理無效輸入和錯誤情況。
            *   根據參數構建 `SubFigureParams` 列表，以繪製三角形和標註。
        *   實現標準的 `generate_tikz()` 方法。
4.  **註冊生成器**：在 `figures/__init__.py` 中導入並註冊所有新的生成器。
5.  **編寫單元測試**：
    *   為每個生成器創建測試文件 (例如 `tests/test_figure_triangle_coordinates.py`)。
    *   測試有效的參數輸入，驗證生成的 TikZ 代碼片段是否符合預期（例如，是否包含特定座標、線段、標籤文本）。
    *   測試無效的參數輸入，驗證是否返回了 "無法構成三角形" 的提示。
    *   測試各種標註選項的組合。
6.  **文檔編寫**：更新 `docs/available_figures.md`，添加新的三角形生成器的說明、參數列表和使用示例。

## 5. Mermaid 流程圖

```mermaid
graph TD
    A[開始: 生成三角形圖形] --> B{選擇三角形定義方式};
    B -- SSS --> C1[PredefinedTriangleSSSGenerator];
    B -- SAS --> C2[PredefinedTriangleSASGenerator];
    B -- ASA --> C3[PredefinedTriangleASAGenerator];
    B -- AAS --> C4[PredefinedTriangleAASGenerator];
    B -- RHS --> C5[PredefinedTriangleRHSGenerator];
    B -- Coordinates --> C6[PredefinedTriangleCoordinatesGenerator];

    C1 --> D1[Params: PredefinedTriangleSSSParams];
    C2 --> D2[Params: PredefinedTriangleSASParams];
    C3 --> D3[Params: PredefinedTriangleASAParams];
    C4 --> D4[Params: PredefinedTriangleAASParams];
    C5 --> D5[Params: PredefinedTriangleRHSParams];
    C6 --> D6[Params: PredefinedTriangleCoordinatesParams];

    subgraph GenericPredefinedGeneratorLogic
        E[generate_tikz(params)] --> F{Pydantic 參數驗證};
        F -- 有效 --> G[_build_composite_params(validated_params)];
        F -- 無效 --> H_ErrorTikZ[返回錯誤提示TikZ];
        
        subgraph BuildCompositeParamsInternal
            direction LR
            G_Input[validated_params] --> G_SymPy{1. SymPy 計算與驗證};
            G_SymPy -- 有效幾何 --> G_ExtractCoords[2. 提取頂點座標/屬性];
            G_SymPy -- 無效幾何 (e.g., SSS不等式不成立) --> G_ErrorParams[準備錯誤提示CompositeParams];
            G_ExtractCoords --> G_BuildSubFigures[3. 構建SubFigureParams (Lines, Points, Labels, Angles)];
            G_BuildSubFigures --> G_OutputParams[CompositeParams];
            G_ErrorParams --> G_OutputParams;
        end
        G --> G_OutputParams_Ref;

        G_OutputParams_Ref -- 正常CompositeParams --> K_CompositeGen[CompositeFigureGenerator.generate_tikz()];
        G_OutputParams_Ref -- 錯誤提示CompositeParams --> K_CompositeGen;
        
        K_CompositeGen --> L[輸出最終TikZ代碼];
    end

    D1 --> E; D2 --> E; D3 --> E; D4 --> E; D5 --> E; D6 --> E;
    L --> M[結束: 獲得三角形TikZ];
    H_ErrorTikZ --> M;
```

## 6. 未來擴展（不在本次計劃範圍內）

*   在核心三角形生成器中加入對常見額外幾何元素（如中線、高線、角平分線、內切圓、外接圓）的可選支持，通過布林參數控制其顯示。
*   為這些額外元素提供有限的樣式自定義選項。
*   在生成的 TikZ 中為關鍵幾何點（如頂點、中心點）定義 `coordinate`，方便用戶進行更高級的 `composite` 組合。