# LaTeX 圖形系統模組化重構計畫 (v6 - 整合預定義類型與詳細文檔)

## 1. 目標

重構現有的圖形生成系統，解決因直接傳遞和嵌套 TikZ 代碼導致的編譯錯誤和格式問題。目標是建立一個模組化、可擴展、可維護的圖形生成架構，能夠處理單一圖形的不同變體（如題目 vs. 詳解版本）、由多個基礎形狀組成的複合圖形，使用 Pydantic 實現標準化的參數驗證，自動處理複合圖形內部的命名空間衝突，提供詳細的相對與絕對定位機制，並**引入預定義複合圖形類型以簡化常用圖形的定義**。實現職責分離，提高代碼的可重用性、健壯性和易用性。

## 2. 背景

目前，部分 `QuestionGenerator` 直接生成包含 `\begin{tikzpicture}` 環境的完整 TikZ 代碼字串。`LaTeXGenerator` 將其嵌入頁面級 `tikzpicture` 環境，導致嵌套錯誤。此外，缺乏處理圖形變體、組合圖形、標準化參數驗證、複合圖形內部命名衝突、精確控制複合圖形內部佈局以及簡化常用複合圖形定義的方法。

## 3. 核心重構方案

### 3.1. 創建 `figures` 包

建立 `figures` 包集中管理圖形生成邏輯。

*   **`figures/base.py`**:
    *   定義 `FigureGenerator` 抽象基類：
        *   `generate_tikz(self, params: Dict[str, Any]) -> str`: 生成 TikZ 圖形**內容**。應首先使用 Pydantic 模型驗證 `params`。需能根據驗證後的參數生成不同變體。
        *   `get_name(cls) -> str`: 返回圖形類型唯一標識符。
*   **`figures/params_models.py` (建議新增)**:
    *   集中定義所有圖形生成器使用的 Pydantic `BaseModel`。
    *   **模型設計原則：**
        *   模型應為大多數參數提供**合理且一致的預設值**，以簡化 `QuestionGenerator` 中 `figure_data` 的構建。
        *   與圖形**樣式**相關的參數（如顏色 `line_color`, `fill_color`、線型 `line_style` 等）應定義在對應的**基礎圖形參數模型**中（例如 `TriangleParams`），使其與應用的元素緊密耦合。
    *   **詳細定義定位結構:**
        ```python
        from pydantic import BaseModel, Field, validator
        from typing import List, Dict, Any, Literal, Optional, Union

        # --- TikZ 常用錨點 ---
        TikzAnchor = Literal[
            'center', 'north', 'south', 'east', 'west',
            'north east', 'north west', 'south east', 'south west',
            'mid', 'mid east', 'mid west', 'base', 'base east', 'base west'
        ]

        # --- TikZ positioning 庫常用放置位置 ---
        TikzPlacement = Literal[
            'right', 'left', 'above', 'below',
            'above left', 'above right', 'below left', 'below right'
        ]

        class AbsolutePosition(BaseModel):
            mode: Literal['absolute'] = 'absolute'
            x: float = 0.0
            y: float = 0.0
            anchor: TikzAnchor = 'center' # 子圖形的哪個錨點對齊到 (x, y)

        class RelativePosition(BaseModel):
            mode: Literal['relative'] = 'relative'
            relative_to: str # 相對於哪個子圖形的 id
            placement: TikzPlacement = 'right' # 放置方向
            distance: str = '1cm' # 距離 (TikZ 單位)
            my_anchor: Optional[TikzAnchor] = None # 當前子圖形用於對齊的錨點
            target_anchor: Optional[TikzAnchor] = None # 相對目標用於對齊的錨點

        class BaseFigureParams(BaseModel):
            variant: Literal['question', 'explanation'] = 'question'

        class UnitCircleParams(BaseFigureParams): # 基礎圖形參數
            angle: float = Field(..., ge=0, le=360)
            show_coordinates: bool = True

        class TriangleParams(BaseFigureParams): pass # 基礎圖形參數 - 添加具體參數

        class SubFigureParams(BaseModel):
            id: Optional[str] = None # 用於相對定位的引用 ID
            type: str # 基礎圖形類型
            params: Dict[str, Any] # 基礎圖形的參數 (需匹配其 Pydantic 模型)
            # position 可以是絕對或相對定位，預設為絕對定位在原點
            position: Union[AbsolutePosition, RelativePosition] = Field(default_factory=AbsolutePosition)

        class CompositeParams(BaseFigureParams):
            sub_figures: List[SubFigureParams] = Field(..., min_items=1)
            # 注意：需要確保 sub_figures 中 id 的唯一性（如果提供的話）
            # 注意：相對定位的 'relative_to' 必須引用列表中較早定義的子圖形的 id

        # --- 新增：預定義複合圖形參數模型 ---
        class StandardUnitCircleParams(BaseFigureParams): # 繼承 BaseFigureParams 以包含 variant
             angle: float = Field(..., ge=0, le=360)
             show_coordinates: bool = True
             # ... 其他控制標準單位圓外觀的參數 ...
        ```
*   **`figures/__init__.py`**:
    *   實現註冊表、註冊/獲取函數。
    *   導入所有具體生成器模組。
*   **`figures/unit_circle.py` (及其他基礎形狀生成器)**:
    *   導入對應 Pydantic 模型。
    *   實現 `FigureGenerator` 子類，使用 `@register_figure_generator` 註冊。
    *   在 `generate_tikz` 開頭使用 Pydantic 模型驗證 `params`。
    *   根據驗證後的參數繪製不同變體。
*   **`figures/composite.py`**:
    *   導入 `CompositeParams` 模型。
    *   實現 `CompositeFigureGenerator` (類型 `'composite'`)。
    *   在 `generate_tikz` 開頭驗證 `params`。
    *   根據驗證後的 `validated_params.sub_figures` 列表執行組合邏輯（加載庫、遍歷、獲取基礎生成器、調用 `generate_tikz`、使用 `scope` 和 `name prefix`、應用定位、組合結果）。
    *   包含佈局策略提醒。
*   **`figures/predefined/standard_unit_circle.py` (及其他預定義複合圖形生成器 - 建議放在子目錄)**:
    *   導入 `StandardUnitCircleParams` 模型和 `CompositeParams` 模型。
    *   實現一個新的 `FigureGenerator` 子類，例如 `StandardUnitCircleMetaGenerator`。
    *   **註冊類型：** 使用 `@register_figure_generator` 註冊一個簡潔的類型名稱，例如 `'standard_unit_circle'`。
    *   **不直接繪製 TikZ：** 其 `generate_tikz` 方法**不**生成 TikZ 代碼。
    *   **核心職責：**
        1.  在 `generate_tikz` 開頭使用 `StandardUnitCircleParams` 驗證傳入的 `params`。
        2.  根據驗證後的參數（如 `angle`, `variant`），**構建**一個詳細的 `CompositeParams` 實例，其中包含定義標準單位圓所需的所有 `sub_figures`（坐標軸、圓、弧、點等及其定位）。
        3.  獲取通用的 `CompositeFigureGenerator` 的實例（例如通過 `figures.get_figure_generator('composite')`）。
        4.  調用 `CompositeFigureGenerator` 實例的 `generate_tikz` 方法，將構建好的 `CompositeParams` 轉換為字典傳遞給它。
        5.  返回 `CompositeFigureGenerator` 的結果。
    *   **目的：** 提供一個簡單接口 (`type: 'standard_unit_circle'`) 來生成常用的複合圖形，將構建 `sub_figures` 的複雜性封裝起來。

### 3.2. 修改 `QuestionGenerator`

*   **移除圖形生成邏輯：** (同前)
*   **返回 `figure_data` 結構：**
    *   對於常用圖形，可以使用簡化的預定義類型：
        ```python
        'figure_data_question': {
            'type': 'standard_unit_circle', # 使用預定義類型
            'params': { # 匹配 StandardUnitCircleParams
                'variant': 'question',
                'angle': 30.0,
                'show_coordinates': False
            },
            'options': { ... }
        }
        ```
    *   對於自定義或不常見的組合，仍然使用通用的 `'composite'` 類型並提供詳細的 `sub_figures`：
        ```python
        'figure_data_explanation': {
            'type': 'composite',
            'params': {
                'variant': 'explanation',
                'sub_figures': [ ...詳細列表... ]
            },
            'options': { ... }
        }
        ```
*   **更新基類文檔：** (同前)

### 3.3. 修改 `utils/latex_generator.py` (`LaTeXGenerator`)

*   **實現 `_render_figure` 方法：** (邏輯不變，它透明地處理基礎類型、複合類型和預定義複合類型)
*   **修改 `generate_question_tex`：** (同前)
*   **修改 `generate_explanation_tex`：** (同前)
*   **調整 `_format_latex_content`：** (同前)

## 4. 架構示意圖

(Mermaid 圖更新以反映預定義生成器)

```mermaid
graph LR
    subgraph UI; A[UI/主程式]; end
    subgraph Generators; B(QuestionGenerator) -- generates --> QData{Question Data}; QData -- contains --> FData{Figure Data}; end
    subgraph Figures;
        Reg[(Figure Registry)];
        FG_Base(FigureGenerator) <|-- SpecificGen(BaseShapeGenerator);
        FG_Base <|-- CompGen(CompositeFigureGenerator);
        FG_Base <|-- PredefinedGen(PredefinedMetaGenerator);
        SpecificGen -- registers --> Reg;
        CompGen -- registers & uses --> Reg;
        PredefinedGen -- registers & uses --> CompGen;
    end
    subgraph Utils; LG(LaTeXGenerator) -- uses --> Reg; LG -- creates & calls --> FG_Instance; FG_Instance -- returns --> TikZ_Content; LG -- wraps & options --> TikZ_Env; LG -- embeds --> FinalLaTeX; end
    A --> B; B --> QData; QData --> LG; LG --> Reg; Reg --> LG; LG --> FG_Instance; FG_Instance --> TikZ_Content; LG --> TikZ_Env; LG --> FinalLaTeX;
    style Reg fill:#f9f,stroke:#333,stroke-width:2px; style FG_Base fill:#ccf,stroke:#333,stroke-width:1px; style QData fill:#ffc,stroke:#333,stroke-width:1px; style FData fill:#ffc,stroke:#333,stroke-width:1px; style TikZ_Content fill:#cfc,stroke:#333,stroke-width:1px; style TikZ_Env fill:#cfc,stroke:#333,stroke-width:1px;
```

## 5. 後續步驟與考量

*   **依賴管理：** 添加 `pydantic` 到 `requirements.txt`。
*   **參數模型定義：** 定義 Pydantic 模型，包括基礎、複合和預定義複合圖形的參數。
*   **生成器實現：** 實現基礎生成器、`CompositeFigureGenerator`（含命名空間和定位處理）以及至少一個預定義複合圖形生成器（如 `StandardUnitCircleMetaGenerator`）。
*   **文檔更新：**
    *   **更新 `docs/generator_guide.md`:** (面向題目生成器開發者) 詳細說明如何準備 `figure_data`，包括使用基礎類型、`'composite'` 類型和預定義複合類型。
    *   **新增 `docs/figure_development_guide.md`:** (面向圖形生成器開發者) 詳細說明如何創建新的基礎 `FigureGenerator`、如何定義其 Pydantic 參數模型、如何實現 `generate_tikz`（包括處理 `variant`），以及如何創建和註冊「預定義複合圖形」元生成器。
    *   **新增 `docs/available_figures.md`:** (面向題目生成器開發者) 列出所有已註冊的圖形類型（基礎和預定義複合），說明它們的用途、預期的 `params`（引用 Pydantic 模型）和 `options`。
*   **錯誤處理：** (同前)
*   **現有代碼排查：** (同前)
*   **測試：**
    *   為 Pydantic 模型添加測試。
    *   為基礎 `FigureGenerator` 添加單元測試。
    *   為 `CompositeFigureGenerator` 添加單元測試。
    *   為預定義複合圖形生成器添加單元測試（驗證其是否正確構建了 `CompositeParams`）。
    *   更新/添加 `LaTeXGenerator` 的整合測試。

## 6. 驗收標準

1.  `pydantic` 已添加。
2.  所有 `FigureGenerator` 使用 Pydantic 驗證。
3.  `CompositeFigureGenerator` 使用 `name prefix` 處理命名空間，並能根據 `position` 佈局。
4.  至少實現一個預定義複合圖形類型（如 `'standard_unit_circle'`）並能正常工作。
5.  所有相關測試通過。
6.  題目和詳解能正確顯示圖形，LaTeX 編譯無錯誤。
7.  圖形縮放、對齊、變體、複合佈局、命名空間隔離按預期工作。
8.  **文檔已按要求更新和創建 (`generator_guide.md`, `figure_development_guide.md`, `available_figures.md`)。**
9.  代碼風格一致，易於理解和維護。

