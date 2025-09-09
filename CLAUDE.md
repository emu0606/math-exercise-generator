# Claude Code 開發指南

> **專案**: 數學測驗生成器  
> **最後更新**: 2025-09-08  
> **當前階段**: 🏆 現代化完成，開始Debug與打磨階段

## 🎯 **專案現狀**

### **✅ 現代化重構完成**
所有重構工作已於2025-09-08完成：
- **Phase 1-3**: figures/ 現代化 (93.8%完成)
- **Phase 4**: generators/ 完全重建 (100%完成) 
- **Phase 5**: ui/ 零怪物檔案重構 (100%完成)

**成果**: 零怪物檔案、完全模組化、93% Sphinx文檔覆蓋

### **🔧 當前階段: Debug與打磨**
重點任務：
1. **功能驗證**: 確保所有模組正常運作
2. **集成測試**: 完整工作流程測試
3. **性能優化**: 提升用戶體驗
4. **Bug修復**: 解決發現的問題

---

## 🏗️ **專案架構概覽**

### **核心模組結構**
```
數學測驗生成器 (現代化架構)
├── ui/                     # PyQt5 使用者介面層
│   ├── main_window.py      # 主視窗
│   ├── components/base/    # 基礎UI組件 (182行+198行)
│   └── widgets/category/   # CategoryWidget (579行→5個模組)
├── generators/             # 題目生成器 (100%現代化)
│   ├── base.py            # 生成器基礎框架
│   ├── algebra/           # 代數生成器
│   └── trigonometry/      # 三角函數生成器  
├── figures/               # 圖形生成器 (93.8%現代化)
│   ├── params/           # 參數模型 (562行→12個模組)
│   ├── predefined/       # 預定義圖形
│   └── [基礎圖形].py    # point, circle, triangle等
├── utils/                # 核心服務層
│   ├── orchestration/    # PDF生成協調器
│   ├── core/            # 配置、註冊、日誌
│   ├── geometry/        # 數學幾何計算
│   ├── tikz/            # TikZ圖形處理
│   └── latex/           # LaTeX生成和編譯
└── tests/               # 測試套件 (51個幾何測試)
```

### **核心特色**
- **零怪物檔案**: 所有檔案 < 200行
- **新架構整合**: 充分應用 `get_logger`, `global_config`
- **Pydantic驗證**: 完整參數驗證和型別安全
- **完整文檔**: 93% Sphinx標準覆蓋

---

## 🔧 **開發與測試指南**

### **基礎測試命令**
```bash
# 應用程式啟動測試
python main.py

# 核心模組功能驗證
py -c "from utils import get_logger, global_config, Point; print('✅ 核心模組正常')"

# 生成器系統測試
py -c "from generators import QuestionGenerator; print('✅ 生成器系統正常')"

# 圖形系統測試  
py -c "from figures.params import PointParams, CircleParams; print('✅ 圖形系統正常')"

# UI系統測試
py -c "from ui import CategoryWidget; print('✅ UI系統正常')"
```

### **測試套件執行**
```bash
# 完整測試套件 (推薦)
py -m pytest tests/ --tb=short -v

# 幾何模組測試 (51個測試)
py -m pytest tests/test_utils/test_geometry/ -v

# 快速測試 (關鍵功能)
py -m pytest tests/test_utils/test_geometry/test_basic_ops.py -v

# 覆蓋率測試 (目標85%)
py -m pytest tests/ --cov=utils --cov-report=html
```

### **新架構工具使用**
```python
# 統一導入範例
from utils import (
    get_logger, global_config,          # 核心工具
    Point, Triangle, distance,          # 幾何工具
    tikz_coordinate, ArcRenderer        # TikZ工具
)

# 生成器開發範例
from generators.base import QuestionGenerator
from pydantic import BaseModel

class MyParams(BaseModel):
    difficulty: str = "MEDIUM"
    
class MyGenerator(QuestionGenerator):
    def __init__(self):
        super().__init__()
        self.logger = get_logger(self.__class__.__name__)
```

---

## 🐛 **Debug重點區域**

### **高優先級檢查項目**
1. **PDF生成流程**
   - 協調器工作流程: `utils/orchestration/pdf_orchestrator.py`
   - LaTeX編譯: `utils/latex/compiler.py`
   - 題目分配: `utils/orchestration/question_distributor.py`

2. **UI互動功能**
   - CategoryWidget模組化組件互動
   - 設定面板資料傳遞
   - 進度回報系統

3. **生成器系統**
   - 自動註冊機制: `generators/__init__.py`
   - Pydantic參數驗證
   - 圖形數據整合

4. **圖形渲染系統**
   - TikZ代碼生成正確性
   - 參數模型驗證
   - 複雜圖形渲染

### **已知注意事項**
```python
# 1. 模組導入路徑 - 新舊並存
from figures.params import PointParams        # ✅ 新架構 (推薦)
from figures.params_models import PointParams # ✅ 向後兼容

# 2. 日誌系統使用
logger = get_logger(self.__class__.__name__)  # ✅ 標準做法
logger.info("任務開始")                        # 詳細資訊
logger.error(f"錯誤: {error}")                 # 錯誤記錄

# 3. 配置管理
config = global_config.get_generator_config('trig')  # ✅ 統一配置
```

### **性能監控重點**
- **啟動時間**: 目標 < 2秒
- **題目生成**: 目標 < 100ms/題
- **PDF編譯**: 目標 2-5秒 (依題目數量)
- **記憶體使用**: 按需載入優化

---

## 📚 **重要文檔參考**

### **系統理解**
- [`docs/workflow.md`](docs/workflow.md) - 完整工作流程說明 (現代化版本)
- [`docs/generators_improvement_plan.md`](docs/generators_improvement_plan.md) - 未來改善計畫

### **歷史記錄**
- [`docs/history/`](docs/history/) - 重構過程完整記錄
- [`docs/history/20250908_modernization_final_summary.md`](docs/history/20250908_modernization_final_summary.md) - 重構成果總結

### **開發參考**
- [`docs/figure_development_guide.md`](docs/figure_development_guide.md) - 圖形開發指南
- [`pytest.ini`](pytest.ini) - 測試配置 (必需保留)

---

## 🚨 **常見問題與解決**

### **模組導入問題**
```bash
# 確認Python路徑
py -c "import sys; print('\\n'.join(sys.path))"

# 重新安裝依賴 (如需要)
pip install -r requirements.txt

# 驗證關鍵模組
py -c "import generators, figures, utils, ui; print('✅ 所有主要模組可導入')"
```

### **測試失敗排查**
```bash
# 詳細錯誤資訊
py -m pytest tests/test_utils/test_geometry/ -v --tb=long

# 特定測試調試
py -m pytest tests/test_utils/test_geometry/test_basic_ops.py::TestBasicOperations::test_distance_calculation -v -s
```

### **UI運行問題**
```bash
# 檢查PyQt5環境
py -c "from PyQt5.QtWidgets import QApplication; print('✅ PyQt5正常')"

# 檢查資源檔案
ls assets/style.qss data/categories.json
```

---

## 🎯 **Debug與打磨目標**

### **功能完整性**
- [ ] PDF生成完整流程測試
- [ ] 所有UI組件功能驗證
- [ ] 生成器系統穩定性測試
- [ ] 圖形渲染品質檢查

### **性能優化**
- [ ] 應用程式啟動優化
- [ ] 大批量題目生成測試
- [ ] 記憶體使用優化
- [ ] UI響應性改善

### **用戶體驗**
- [ ] 錯誤處理友善化
- [ ] 進度回報完整性
- [ ] 介面交互流暢性
- [ ] 輸出品質檢驗

---

## 📞 **Debug階段協助指南**

1. **問題重現**: 詳細記錄操作步驟和錯誤資訊
2. **日誌檢查**: 檢查控制台輸出和錯誤訊息  
3. **測試驗證**: 執行相關測試確認問題範圍
4. **模組隔離**: 使用單元測試隔離問題模組
5. **參考文檔**: 查閱 `docs/workflow.md` 了解系統設計

## 🚨 **重要開發原則**

**形成完整計畫檔案並確認前不修改代碼**

- 所有程式碼修改必須先制定詳細計畫
- 計畫必須包含問題分析、修復策略、風險評估
- 計畫確認後才能開始執行修改
- 避免盲目修改造成更多問題

---

**專案狀態**: 🏆 現代化重構完成，進入穩定化階段  
**開發重點**: Debug、優化、完善用戶體驗  
**品質目標**: 生產就緒的高品質數學測驗生成系統