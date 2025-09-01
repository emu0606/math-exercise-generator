# 數學測驗生成器

一個用於生成數學測驗的 Python 應用程式，支援多種題型和 LaTeX PDF 輸出。

## 功能特點

- 支援多種數學題型（四則運算、代數、幾何等）
- 可自定義測驗難度和題目數量
- 使用 LaTeX 生成高品質 PDF 格式的測驗卷、簡答卷和詳解卷
- 支援 LaTeX 數學公式的原生渲染
- 智能佈局引擎，支援自動換頁
- 友好的圖形使用者介面
- 包含激勵性名言、數學小知識和公式庫

## 系統需求

- Python 3.6 或更高版本
- 依賴套件：PyQt5, sympy, numpy, matplotlib
- LaTeX 環境：需安裝 XeLaTeX 和相關宏包（xeCJK, tikz, geometry, multicol 等）
- 字體：需安裝 Noto Sans TC 字體

## 安裝方法

1. 克隆或下載本專案
2. 安裝依賴套件：

```bash
pip install -r requirements.txt
```

## 使用方法

執行主程式：

```bash
python main.py
```

## LaTeX 環境配置

### Windows

1. 安裝 MiKTeX 或 TeX Live：
   - MiKTeX: https://miktex.org/download
   - TeX Live: https://tug.org/texlive/acquire-netinstall.html

2. 安裝 Noto Sans TC 字體：
   - 從 Google Fonts 下載：https://fonts.google.com/noto/specimen/Noto+Sans+TC
   - 安裝下載的字體文件

### macOS

1. 安裝 MacTeX：
   - 從 https://tug.org/mactex/ 下載並安裝

2. 安裝 Noto Sans TC 字體：
   - 從 Google Fonts 下載：https://fonts.google.com/noto/specimen/Noto+Sans+TC
   - 安裝下載的字體文件

### Linux

1. 安裝 TeX Live：
   ```bash
   sudo apt-get install texlive-full
   ```

2. 安裝 Noto Sans TC 字體：
   ```bash
   sudo apt-get install fonts-noto-cjk
   ```

## 專案結構

```
MathGenerator/
├── assets/                # 靜態資源
│   ├── fonts/            # 字體文件
│   ├── icons/            # 圖示文件
│   └── style.qss         # 樣式表
├── data/                  # 資料庫和資源
│   ├── question_bank/    # 題庫
│   ├── emojis.py         # 表情符號庫
│   ├── formulas.py       # 公式庫
│   ├── quotes.py         # 名言佳句庫
│   └── trivia.py         # 數學小知識庫
├── generators/            # 題目生成器
│   ├── arithmetic/       # 四則運算題目
│   ├── algebra/          # 代數題目
│   ├── geometry/         # 幾何題目
│   └── ...
├── templates/             # PDF 模板
│   ├── standard.py       # 標準模板
│   ├── compact.py        # 緊湊模板
│   └── ...
├── ui/                    # 使用者介面
│   ├── components/       # UI 元件
│   └── main_window.py    # 主視窗
├── utils/                 # 工具函數
│   ├── layout_engine.py  # 佈局引擎
│   ├── latex_generator.py # LaTeX 生成器
│   ├── pdf_compiler.py   # PDF 編譯器
│   ├── pdf_generator.py  # PDF 生成工具
│   └── registry.py       # 生成器註冊表
├── main.py                # 主程式
├── requirements.txt       # 依賴套件
└── README.md              # 說明文件
```

## 擴展功能

### 添加新題型

1. 在 `generators/` 目錄下創建新的生成器類別
2. 繼承 `QuestionGenerator` 基礎類別
3. 實現 `generate_question()` 方法
4. 在 `generators/__init__.py` 中導出新的生成器類別
### PDF 生成流程

新版本使用 LaTeX 生成 PDF，流程如下：

1. 生成題目內容
2. 使用佈局引擎計算題目位置
3. 生成 LaTeX 文件內容
4. 使用 XeLaTeX 編譯生成 PDF

生成的 PDF 文件包括：
- `[prefix]_question.pdf`：題目頁
- `[prefix]_answer.pdf`：簡答頁
- `[prefix]_explanation.pdf`：詳解頁

### 自動換頁功能

佈局引擎支援自動換頁，當題目無法在當前頁面剩餘空間放置時，會自動結束當前頁並在新頁面繼續佈局。
4. 在 `templates/__init__.py` 中導出新的模板類別

## 貢獻指南

歡迎提交 Pull Request 或 Issue 來改進本專案。

## 授權協議

本專案採用 MIT 授權協議。
