# PDF 生成工作流程 (LaTeX 版本)

本文件描述了使用 LaTeX 生成 PDF 測驗卷的工作流程。

## 流程概述

使用者透過 UI 介面觸發 PDF 生成，`pdf_generator` 模組負責協調題目生成、佈局、LaTeX 內容創建和 PDF 編譯等步驟，最終產生三個獨立的 PDF 檔案（題目卷、簡答卷、詳解卷）。

## 詳細步驟

1.  **UI (使用者介面)**
    *   收集使用者輸入的參數：題型、數量、回數 (`rounds`)、每回題數 (`questions_per_round`)、測驗標題 (`test_title`)、輸出位置等。
    *   調用 `utils.pdf_generator.generate_pdf` 函數，傳遞參數（通常包含一個完整的輸出路徑 `output_path`）。

2.  **`utils.pdf_generator.generate_pdf` (兼容函數)**
    *   **輸入**: `output_path`, `test_title`, `selected_data`, `rounds`, `questions_per_round` 等。
    *   從 `output_path` 解析出輸出目錄 `output_dir` 和文件名前綴 `filename_prefix`。
    *   **輸出**: 調用核心函數 `generate_latex_pdfs`，傳遞解析後的參數。

3.  **`utils.pdf_generator.generate_latex_pdfs` (核心協調函數)**
    *   **輸入**: `output_dir`, `filename_prefix`, `test_title`, `selected_data`, `rounds`, `questions_per_round`。
    *   **步驟 3.1**: 調用 `_generate_raw_questions`，根據 `selected_data` 從各個題目生成器 (`generators/`) 獲取原始題目列表 `raw_questions`。
    *   **步驟 3.2**: 調用 `_distribute_questions`，對 `raw_questions` 進行題型分佈處理和回內排序，得到有序題目列表 `ordered_questions`。
    *   **步驟 3.3**: 實例化 `LayoutEngine` (`utils/layout_engine.py`)。
    *   **步驟 3.4**: 調用 `layout_engine.layout`，傳入 `ordered_questions` 和 `questions_per_round`，計算題目佈局，得到 `layout_results` (包含頁碼 `page` 和位置 `row`, `col`)。
    *   **步驟 3.5**: 實例化 `LaTeXGenerator` (`utils/latex_generator.py`)。
    *   **步驟 3.6**: 調用 `latex_generator.generate_question_tex`，傳入 `layout_results`, `test_title`, `questions_per_round`，生成題目卷的 `.tex` 內容字串。
    *   **步驟 3.7**: 調用 `latex_generator.generate_answer_tex`，傳入 `ordered_questions`, `test_title`，生成簡答卷的 `.tex` 內容字串。
    *   **步驟 3.8**: 調用 `latex_generator.generate_explanation_tex`，傳入 `ordered_questions`, `test_title`，生成詳解卷的 `.tex` 內容字串。
    *   **步驟 3.9**: 實例化 `PDFCompiler` (`utils/pdf_compiler.py`)。
    *   **步驟 3.10**: 調用 `pdf_compiler.compile_tex_to_pdf` 三次，分別編譯三個 `.tex` 字串，生成三個 PDF 檔案 (`*_question.pdf`, `*_answer.pdf`, `*_explanation.pdf`) 到 `output_dir`。
    *   **輸出**: 返回布林值，表示所有 PDF 是否成功生成。

4.  **UI 顯示結果**
    *   根據 `generate_pdf` 返回的結果，向使用者顯示成功或失敗訊息。

## Mermaid 流程圖

```mermaid
graph TD
    A[UI: 收集參數] --> B(pdf_generator.generate_pdf - 兼容函數);
    B -- 解析參數 --> C(pdf_generator.generate_latex_pdfs - 核心函數);
    C --> D[_generate_raw_questions];
    D -- raw_questions --> E[_distribute_questions];
    E -- ordered_questions --> F{LayoutEngine.layout};
    C -- questions_per_round --> F;
    F -- layout_results --> G{LaTeXGenerator};
    E -- ordered_questions --> G;
    C -- test_title, questions_per_round --> G;
    G -- tex_question --> H{PDFCompiler.compile};
    G -- tex_answer --> H;
    G -- tex_explanation --> H;
    C -- output_dir, filename_prefix --> H;
    H -- PDF Files --> I[輸出目錄];
    H -- Success/Fail --> C;
    C -- Success/Fail --> B;
    B -- Success/Fail --> J[UI: 顯示結果];

    subgraph "PDF Generator"
        B
        C
        D
        E
    end

    subgraph "Layout Engine"
        F
    end

    subgraph "LaTeX Generator"
        G
    end

    subgraph "PDF Compiler"
        H
    end