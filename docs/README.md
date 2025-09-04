# Math Exercise Generator 文檔系統

這是 Math Exercise Generator 的完整 Sphinx 文檔系統，提供專業的 API 文檔和使用指南。

## 🚀 快速開始

### 安裝依賴

```bash
# 安裝 Sphinx 和相關依賴
pip install sphinx sphinx-rtd-theme myst-parser
```

### 生成文檔

```bash
# 方法 1: 使用 Makefile (推薦)
cd docs
make html

# 方法 2: 直接使用 Sphinx
cd docs
py -m sphinx -b html source build
```

### 查看文檔

生成完成後，打開 `docs/build/index.html` 即可查看完整文檔。

```bash
# 自動在瀏覽器中打開
make serve
```

## 📁 文檔結構

```
docs/
├── source/                  # 源文件
│   ├── index.rst           # 主頁
│   ├── conf.py             # Sphinx 配置
│   ├── api/                # API 文檔
│   │   ├── utils.rst
│   │   ├── geometry.rst
│   │   ├── tikz.rst
│   │   ├── latex.rst
│   │   ├── core.rst
│   │   └── orchestration.rst
│   └── guides/             # 使用指南
│       ├── quickstart.rst
│       ├── architecture.rst
│       └── migration.rst
├── build/                  # 生成的文檔
├── Makefile               # 構建工具
└── README.md             # 這個文件
```

## 📚 包含的文檔

### API 參考
- **Utils 模組**: 統一入口和核心功能
- **Geometry 模組**: 幾何計算核心 (多後端支持)
- **TikZ 模組**: 專業圖形渲染
- **LaTeX 模組**: 文檔生成系統
- **Core 模組**: 核心基礎設施
- **Orchestration 模組**: 業務流程協調

### 使用指南
- **快速入門**: 5分鐘上手指南
- **系統架構**: 6層架構詳細說明
- **遷移指南**: 舊 API → 新 API 對應表

## 🛠️ 開發者工具

### 常用 Makefile 命令

```bash
# 生成 HTML 文檔
make html

# 清理構建目錄
make clean

# 重新生成 API 文檔
make apidoc

# 檢查連結
make linkcheck

# 構建並在瀏覽器中打開
make serve

# 監視文件變化自動重建 (需要 watchdog)
make watch
```

### 自動 API 文檔

文檔系統會自動從 Python docstring 生成 API 文檔：

```python
def example_function(param1: int, param2: str) -> bool:
    """
    這是一個示例函數。
    
    Args:
        param1: 整數參數
        param2: 字符串參數
        
    Returns:
        bool: 返回布爾值
        
    Raises:
        ValueError: 當參數無效時
    """
    pass
```

## 🎨 主題和樣式

使用 **Read the Docs** 主題，特色：
- 📱 響應式設計，支持移動設備
- 🔍 全文搜索功能
- 🏷️ 自動生成 API 索引
- 🔗 交叉引用和超連結
- 🌙 支持深色模式

## 🔧 自定義配置

### Sphinx 配置 (`conf.py`)

主要配置項：
- **自動文檔生成**: `sphinx.ext.autodoc`
- **Google 風格 docstring**: `sphinx.ext.napoleon`  
- **Markdown 支持**: `myst_parser`
- **中文支持**: `language = 'zh_TW'`

### 擴展功能

- **Intersphinx**: 鏈接到 Python, NumPy, SymPy 官方文檔
- **代碼高亮**: 自動語法高亮
- **數學公式**: MathJax 支持
- **GitHub Pages**: 準備好的 GitHub Pages 部署

## 📊 文檔統計

當前文檔包含：
- **10個 RST 文件** 
- **6個 API 模組** 詳細文檔
- **3個使用指南**
- **完整的架構說明**
- **詳細的遷移指南**

## 🚀 部署

### 本地服務

```bash
# 使用 Python 內建服務器
cd docs/build
python -m http.server 8000
```

### GitHub Pages

文檔已準備好部署到 GitHub Pages：
1. 推送到 `docs` 分支
2. 在 GitHub 設置中啟用 Pages
3. 選擇 `docs/build` 目錄作為源

## 🤝 貢獻

### 添加新文檔

1. 在 `docs/source/` 創建新的 `.rst` 文件
2. 添加到相應的 `toctree` 中
3. 運行 `make html` 重新生成

### 改進 API 文檔

直接在 Python 代碼中改進 docstring，文檔會自動更新。

### 報告問題

如發現文檔問題，請在 GitHub Issues 中報告。

---

📖 **完整的專業文檔系統，讓 API 使用更簡單！**