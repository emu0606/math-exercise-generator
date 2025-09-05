# Claude Code 開發指南

> **專案**: 數學測驗生成器現代化  
> **最後更新**: 2025-09-06 (Day 2 重構完成)  
> **當前階段**: params_models 重構 Day 2/4 ✅

## 🏗️ **專案架構概覽**

### **核心模組**
- **`figures/`** - 圖形生成系統 (TikZ 輸出)
  - `params/` - 參數模型系統 ✅ **重構完成**
  - `predefined/` - 預定義圖形生成器
  - Base classes 和註冊系統
  
- **`generators/`** - 題目生成器系統
  - `algebra/` - 代數題目生成器
  - `trigonometry/` - 三角函數生成器  
  - `arithmetic/` - 算術生成器
  - **狀態**: 📋 需要現代化 (見 `docs/generators_improvement_plan.md`)

- **`utils/`** - 核心工具函數
  - `geometry/` - 幾何計算
  - `core/` - 註冊系統、配置管理

- **`ui/`** - 使用者介面
- **`tests/`** - 測試套件  
- **`docs/`** - 技術文檔

## 🎯 **當前重構狀態**

### **✅ 已完成 - params_models 重構**
```
Day 1 ✅: 基礎架構 (types, base, __init__)
Day 2 ✅: 幾何參數 + 樣式系統 (geometry, shapes, composite, styles)
```

**成就**:
- 562 行巨型文件 → 10+ 模組化文件
- 100% 向後兼容性維持  
- 完整 Sphinx docstring 覆蓋
- 新舊模組並存測試通過

### **🔄 進行中 - Day 3 目標**
- 處理 162 行 `PredefinedTriangleParams` 怪物
- 建立 `figures/params/triangle/` 專用模組
- 完成最後的參數模型隔離

### **📋 計劃中**
- Day 4: Sphinx 文檔完善 + 最終驗證
- 後續: generators 系統現代化 (參考改進計畫)

## 🔧 **開發最佳實踐**

### **測試命令**
```bash
# 新模組功能測試
py -c "from figures.params import PointParams, CircleParams; print('✅ 新模組正常')"

# 向後兼容性測試  
py -c "from figures.params_models import UnitCircleParams; print('✅ 舊模組兼容')"

# 幾何工具測試
py -m pytest tests/test_utils/test_geometry/ -v

# 完整測試套件
py -m pytest tests/ --tb=line -q
```

### **Git 工作流程**
```bash
# 功能開發分支
git checkout -b feature/module-name

# 重構專用分支 (當前)
git checkout refactor-params-models

# 提交標準
git commit -m "模組: 簡要描述

詳細變更說明...

🤖 Generated with [Claude Code](https://claude.ai/code)
Co-Authored-By: Claude <noreply@anthropic.com>"
```

## 📖 **重要文檔引用**

### **重構計畫**
- [`docs/params_models_refactoring_plan.md`](docs/params_models_refactoring_plan.md) - 4天重構詳細計畫
- [`docs/figure_generator_modernization_plan.md`](docs/figure_generator_modernization_plan.md) - 完整現代化路線圖
- [`progress.md`](progress.md) - 即時進度追蹤

### **未來改善**  
- [`docs/generators_improvement_plan.md`](docs/generators_improvement_plan.md) - Generators 現代化計畫

### **開發指南**
- [`docs/figure_development_guide.md`](docs/figure_development_guide.md) - 圖形開發指南

## 🧪 **關鍵測試場景**

### **新架構驗證**
```python
# 基礎幾何參數
from figures.params import PointParams, CircleParams, TriangleParams

# 複合圖形系統  
from figures.params import CompositeParams, SubFigureParams
from figures.params import AbsolutePosition, RelativePosition

# 樣式配置系統
from figures.params.styles import LabelStyleConfig, ArcStyleConfig
```

### **圖形生成測試**
```python
# 使用新參數系統
from figures import get_figure_generator

generator = get_figure_generator('unit_circle')
tikz_code = generator.generate_tikz({
    'angle': 45,
    'show_coordinates': True,
    'variant': 'explanation'
})
```

## ⚡ **快速命令參考**

### **模組導入測試**
```bash
# 測試新模組
py -c "from figures.params import *; print('✅ 新架構')"

# 測試舊兼容
py -c "from figures.params_models import *; print('✅ 舊兼容')" 
```

### **文檔生成** (未來)
```bash
# Sphinx 文檔生成 (計劃中)
cd docs && make html

# API 文檔檢查
py -c "help(figures.params.geometry.PointParams)"
```

## 🚨 **已知問題與解決方案**

### **Import 錯誤**
如果遇到 `ModuleNotFoundError`：
```bash
# 確認 Python 路徑
py -c "import sys; print(sys.path)"

# 重新安裝依賴 (如需要)
pip install -r requirements.txt
```

### **Git 合併衝突**
重構期間常見於：
- `figures/__init__.py`
- `progress.md` 
- `.claude/settings.local.json`

優先保留重構分支的變更。

## 📞 **需要協助時**

1. **檢查文檔**: 優先查閱 `docs/` 下的相關計畫文檔
2. **執行測試**: 使用上述測試命令驗證功能  
3. **查看進度**: 檢查 `progress.md` 了解當前狀態
4. **Git 歷史**: 查看最近的提交了解變更脈絡

---

**提醒**: 此專案正在進行大規模重構，建議在進行新功能開發前先完成 params_models 重構 (Day 3-4)。