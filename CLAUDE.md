# Claude Code 開發指南

> **專案**: 數學測驗生成器現代化  
> **最後更新**: 2025-09-07 (Phase 4 開始)  
> **當前階段**: Phase 4 Generators 現代化 🚀

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
  - **狀態**: 🚀 Phase 4 進行中 (基礎框架完成 ✅)

- **`utils/`** - 核心工具函數
  - `geometry/` - 幾何計算
  - `core/` - 註冊系統、配置管理

- **`ui/`** - 使用者介面
- **`tests/`** - 測試套件  
- **`docs/`** - 技術文檔

## 🎯 **當前現代化狀態**

### **✅ 已完成階段**
```
✅ params_models 重構完成 (Day 1-4)
✅ Phase 1-3: figures/ 目錄現代化完成
✅ Phase 4.1: generators 基礎框架現代化完成
```

### **🚀 進行中 - Phase 4: Generators 現代化**
**當前重點**: 完全重建 generators 系統，**不考慮向後兼容性**

#### **新架構核心思維**
- **🔥 推倒重建**: 完全拋棄舊架構束縛
- **⚡ 新架構優先**: 充分發揮新工具優勢  
- **🏆 品質至上**: 建立新架構的典範案例
- **🚫 零技術債務**: 不被舊 API 和設計限制

#### **Phase 4 成果**
- [x] **generators/base.py** - 完全重建基礎生成器類別 ✅
- [x] **generators/__init__.py** - 新架構註冊系統建立 ✅
- [ ] **generators/algebra/** - 代數生成器完全重建 (進行中)
- [ ] **generators/arithmetic/** - 算術生成器重建
- [ ] **其他數學領域** - 三角函數等生成器重建

### **📋 新架構重建原則**
1. **完全應用新工具**: `from utils import Point, global_config, get_logger`
2. **Pydantic 參數驗證**: 充分利用型別安全和資料驗證
3. **完整 Sphinx 文檔**: Google Style 標準，包含數學概念準確性
4. **性能優化**: 利用新架構的效能優勢
5. **設計自由度**: 不受舊 API 束縛，設計最佳接口

### **⚡ 新架構專注執行策略**

#### **🎯 核心策略**
- **推倒重建思維**: 完全摒棄舊系統束縛，以新架構最佳實踐為準
- **品質典範建設**: 讓每個重建的生成器成為新架構應用典範
- **技術債務零容忍**: 不繼承任何舊架構的設計問題
- **充分工具應用**: 最大化利用新架構提供的所有優勢工具

#### **🚨 新架構風險管理**
**高優先級風險**:
- **數學邏輯正確性**: 重建時確保數學計算邏輯完全正確
- **新架構整合**: 充分發揮新架構工具的整合優勢

**轉為機會項目**:
- **全新 API 設計**: 設計完全符合新架構理念的最佳 API
- **典範案例建設**: 建立新架構在複雜數學應用中的標準範例

#### **🛡️ 簡化應急策略**
遇到困難時的解決思路：
1. **深入理解新架構** - 可能是尚未充分發揮新工具優勢
2. **重新設計而非修補** - 既然推倒重建，就徹底重新設計  
3. **新架構最佳解決方案** - 不被舊思維和舊實作限制

## 🔧 **開發最佳實踐**

### **新架構測試命令**
```bash
# 新架構模組功能測試
py -c "from figures.params import PointParams, CircleParams; print('✅ 新架構模組正常')"

# 新架構生成器測試
py -c "from generators import QuestionGenerator, QuestionSize; print('✅ 新架構生成器正常')"

# 完整的新架構工具測試
py -c "from utils import Point, global_config, get_logger; print('✅ 新架構工具集正常')"

# 幾何計算新架構測試
py -m pytest tests/test_utils/test_geometry/ -v

# 完整測試套件
py -m pytest tests/ --tb=line -q

# 新重建模組的功能驗證
py -c "from generators.base import QuestionGenerator; print('✅ 重建基礎類別正常')"
```

### **新架構驗證重點**
```bash
# 驗證新架構整合是否成功
py -c "
from generators.base import QuestionGenerator
from utils import get_logger
logger = get_logger('test')
logger.info('新架構整合測試成功')
print('✅ 新架構整合正常')
"
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

## 🚀 **新架構重建宣言**

**此專案採取完全重建策略**，目標是建立現代化、高品質的數學測驗生成系統：

### **✨ 重建優勢**
- **🔥 零技術債務**: 完全摒棄舊架構的設計問題
- **⚡ 新工具充分應用**: 最大化利用新架構的所有優勢  
- **🏆 品質典範**: 每個模組都是新架構應用的最佳範例
- **📚 完整文檔**: 所有模組都有完整的 Sphinx 標準化文檔
- **🧪 徹底測試**: 新架構下的完整功能驗證

### **🎯 當前重點**
**Phase 4: Generators 完全重建** - 不考慮向後兼容，專注於建立新架構的典範應用

**核心思維**: **推倒重建 > 修補維護**，**新架構優勢 > 舊系統包袱**