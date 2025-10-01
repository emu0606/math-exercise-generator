# 數學測驗生成器

基於 PyQt5 的數學測驗自動生成系統，採用現代化模組架構，支援多種數學題型和 TikZ 圖形，輸出專業的 LaTeX PDF 文件。

## ✨ 核心特色

- 🏗️ **現代化架構**: 完全模組化設計，零怪物檔案
- 🎨 **豐富圖形**: TikZ 圖形系統，支援幾何圖形自動生成
- ⚡ **智能配置**: Pydantic 參數驗證，動態 UI 配置系統
- 📚 **完整文檔**: 93% Sphinx 文檔覆蓋，詳細開發指南
- 🧪 **品質保證**: 完整單元測試，型別安全設計

## 🚀 快速開始

### 系統需求
- Python 3.8+
- PyQt5, sympy, numpy, pydantic
- LaTeX 環境（XeLaTeX）
- Noto Sans TC 字體

### 安裝依賴
```bash
pip install -r requirements.txt
```

### 執行程式
```bash
python main.py
```

## 📚 開發文檔

### 開發新的題目生成器
請參考完整的開發指南體系：

- **入口**: [docs/開發指南索引.md](docs/開發指南索引.md) - 按角色提供導航路徑
- **主要指南**: [docs/生成器開發指南.md](docs/生成器開發指南.md) - 完整開發流程
- **開發規範**: [CLAUDE.md](CLAUDE.md) - 專案開發規範和注意事項

### 系統架構與工作流程
- [docs/workflow.md](docs/workflow.md) - 完整系統架構和工作流程說明

### API 文檔
Sphinx 文檔系統位於 [docs/](docs/) 目錄，包含完整 API 參考。

## 🏗️ 專案結構

```
math/
├── main.py                 # 應用程式入口
├── generators/             # 題目生成器（業務邏輯層）
│   ├── base.py            # 生成器基礎框架
│   ├── algebra/           # 代數生成器
│   └── trigonometry/      # 三角函數生成器
├── figures/               # 圖形生成器（視覺化層）
│   ├── params/           # 參數模型（Pydantic）
│   └── predefined/       # 預定義圖形
├── ui/                    # PyQt5 使用者介面
│   ├── main_window.py    # 主視窗
│   └── widgets/          # UI 組件
├── utils/                 # 核心服務層
│   ├── core/             # 配置、日誌、註冊系統
│   ├── geometry/         # 幾何計算
│   ├── tikz/             # TikZ 圖形處理
│   ├── latex/            # LaTeX 生成和編譯
│   └── orchestration/    # PDF 生成協調器
├── tests/                 # 單元測試
├── docs/                  # 文檔系統
└── CLAUDE.md             # 開發規範
```

## 🔧 LaTeX 環境配置

### Windows
安裝 [MiKTeX](https://miktex.org/download) 或 [TeX Live](https://tug.org/texlive/)

### macOS
安裝 [MacTeX](https://tug.org/mactex/)

### Linux
```bash
sudo apt-get install texlive-full
sudo apt-get install fonts-noto-cjk
```

### 必要字體
從 [Google Fonts](https://fonts.google.com/noto/specimen/Noto+Sans+TC) 下載安裝 Noto Sans TC

## 📖 使用說明

### PDF 生成流程
1. 選擇題型和配置參數
2. 系統自動生成題目內容
3. 智能佈局引擎計算排版
4. LaTeX 編譯為 PDF

### 輸出文件
- `[prefix]_question.pdf` - 題目卷
- `[prefix]_answer.pdf` - 簡答卷
- `[prefix]_explanation.pdf` - 詳解卷

## 🎓 開發指南

### 添加新題型生成器
1. 參考 [docs/生成器開發指南.md](docs/生成器開發指南.md)
2. 查看典範生成器範例:
   - `generators/trigonometry/InverseTrigonometricFunctionGenerator.py`（入門級）
   - `generators/algebra/double_radical_simplification.py`（預篩選範例）
3. 遵循 [docs/生成器檔案結構規範.md](docs/生成器檔案結構規範.md)

### 開發者資源
- 完整文檔導航: [docs/開發指南索引.md](docs/開發指南索引.md)
- 開發規範: [CLAUDE.md](CLAUDE.md)
- 系統架構: [docs/workflow.md](docs/workflow.md)

## 🤝 貢獻

歡迎提交 Pull Request 或 Issue 來改進本專案。

## 📄 授權

MIT License
