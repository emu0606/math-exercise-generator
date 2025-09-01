# 工作計畫

## 目標
將 `LaTeXGenerator` 的職責拆分到 `LaTeXStructure` 和 `FigureRenderer` 兩個新類別中，以提高程式碼的可讀性、可維護性和可測試性。

## 步驟 1: 創建 `LaTeXStructure` 類別
- **任務:** 建立新檔案 `utils/latex_structure.py`。
- **任務:** 在此檔案中定義 `LaTeXStructure` 類別。
- **任務:** 將以下方法從 `LaTeXGenerator` 中移動到 `LaTeXStructure`：
  - `_get_preamble` -> `get_preamble(self, title)`
  - `_generate_page_header` -> `generate_page_header(self, round_num)`
  - `_generate_page_footer` -> `generate_page_footer(self)`
  - `_format_latex_content` -> `format_latex_content(self, content)`
- **任務:** 確保這些方法接收必要的參數並返回正確的結果。

## 步驟 2: 創建 `FigureRenderer` 類別
- **任務:** 建立新檔案 `utils/figure_renderer.py`。
- **任務:** 在此檔案中定義 `FigureRenderer` 類別。
- **任務:** 將 `_render_figure` 方法的邏輯從 `LaTeXGenerator` 中移動到 `FigureRenderer` 的新公開方法 `render(self, figure_data: Dict[str, Any]) -> str`。
- **任務:** 確保 `FigureRenderer` 能夠正確導入並使用 `figures` 模組中的圖形生成器。

## 步驟 3: 重構 `LaTeXGenerator` 類別
- **任務:** 修改 `LaTeXGenerator` 類別，讓它依賴 `LaTeXStructure` 和 `FigureRenderer`。
- **任務:** 在 `__init__` 方法中，創建 `LaTeXStructure` 和 `FigureRenderer` 的實例。
- **任務:** 更新 `generate_question_tex`, `generate_answer_tex`, `generate_explanation_tex` 方法，使用 `LaTeXStructure` 和 `FigureRenderer` 的方法來生成 LaTeX 內容。
- **任務:** 移除已被移動的方法，保持 `LaTeXGenerator` 的介面不變。

## 步驟 4: 驗證與測試
- **任務:** 確保 `utils/pdf_generator.py` 仍然可以正常運作，並且生成的 PDF 文件與之前一致。
- **任務:** 執行現有的測試或手動測試，確保重構後的程式碼能夠正常工作。

## 計畫示意圖 (Mermaid Sequence Diagram - 簡化流程)

```mermaid
sequenceDiagram
    participant PDFGen as pdf_generator.py
    participant TexGen as LaTeXGenerator (重構後)
    participant Structure as LaTeXStructure
    participant Renderer as FigureRenderer
    participant Figures as figures module

    PDFGen->>TexGen: __init__()
    activate TexGen
    TexGen->>Structure: __init__()
    activate Structure
    TexGen->>Renderer: __init__()
    activate Renderer
    deactivate TexGen

    PDFGen->>TexGen: generate_question_tex(data, title, ...)
    activate TexGen
    TexGen->>Structure: get_preamble(title)
    activate Structure
    Structure-->>TexGen: preamble_str
    deactivate Structure
    loop 對於每個題目/佈局元素
        alt 包含圖形
            TexGen->>Renderer: render(figure_data)
            activate Renderer
            Renderer->>Figures: get_figure_generator(type)
            activate Figures
            Figures-->>Renderer: generator_cls
            deactivate Figures
            Renderer->>Figures: generator.generate_tikz(params)
            activate Figures
            Figures-->>Renderer: tikz_content
            deactivate Figures
            Renderer-->>TexGen: figure_latex_code
            deactivate Renderer
        end
        TexGen->>Structure: format_latex_content(content)
        activate Structure
        Structure-->>TexGen: formatted_content
        deactivate Structure
    end
    TexGen->>Structure: generate_page_header(...)
    activate Structure
    Structure-->>TexGen: header_str
    deactivate Structure
    TexGen->>Structure: generate_page_footer()
    activate Structure
    Structure-->>TexGen: footer_str
    deactivate Structure
    TexGen-->>PDFGen: final_latex_string
    deactivate TexGen