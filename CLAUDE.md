# Claude Code 開發指南

> **專案**: 數學測驗生成器
> **最後更新**: 2025-09-17
> **當前階段**: 🌟 典範生成器建立階段 - 供未來開發者和教師參考

## 🎯 **專案現狀**

### **✅ 現代化重構完成**
所有重構工作已於2025-09-08完成：
- **Phase 1-3**: figures/ 現代化 (93.8%完成)
- **Phase 4**: generators/ 完全重建 (100%完成) 
- **Phase 5**: ui/ 零怪物檔案重構 (100%完成)

**成果**: 合理檔案大小、完全模組化、93% Sphinx文檔覆蓋

### **🌟 當前階段: 典範生成器建立**
重點任務：
1. **建立開發典範**: 以雙重根號生成器為範例，建立可複製的開發模式
2. **經驗法則整理**: 整理過度工程化識別和修正的系統性方法
3. **技術選擇指南**: 場景適配原則 - 基礎招式vs華麗大招的使用時機
4. **LaTeX標準化**: 防範Unicode誤用，確保PDF輸出品質
5. **教師友善設計**: 降低學習和維護成本，提升可用性

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
├── figures/               # 圖形生成器 (93.8%現代化) [惰性導入]
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
- **合理檔案大小**: 一般檔案 < 200行，範本生成器可達300行（含完整註解）
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
py -c "from generators.base import QuestionGenerator; print('✅ 生成器系統正常')"

# 圖形系統測試
py -c "from figures.params import PointParams, CircleParams; print('✅ 圖形系統正常')"

# UI系統測試
py -c "from ui.components.base import BaseWidget; print('✅ UI系統正常')"

# 佈局引擎測試 (當前重點)
py -c "from utils.core.layout import LayoutEngine; print('✅ 佈局引擎正常')"
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

## 🌟 **典範開發準則**

### **數學生成器開發核心準則**

#### **技術選擇原則: 場景適配**
- **基礎招式** (f字串): 簡單字串拼接，變化點<3個
  ```python
  question = f"計算：$\\sin^{{-1}}({value})$"
  answer = f"${result}^\\circ$"
  ```
- **華麗大招** (模板系統): 複雜多變格式，>5種變化
  ```python
  EXPLANATION_TEMPLATES = {
      'arcsin_special': """詳細解法模板...""",
      'arcsin_general': """一般解法模板..."""
  }
  ```

#### **過度工程化識別標準**
- ❌ **代碼膨脹**: 超過2倍行數增長
- ❌ **Pydantic濫用**: 處理2-3個簡單參數用67行代碼
- ❌ **不必要枚舉**: 簡單字串選擇用複雜枚舉類
- ❌ **過度分割**: 將5行邏輯拆成3個私有方法

#### **LaTeX標準化 - 防範Unicode誤用**
```python
# ✅ 正確做法
angle = f"${degrees}^\\circ$"        # LaTeX度數符號
times = f"$a \\times b$"             # LaTeX乘號

# ❌ 絕對禁止
angle = f"${degrees}°$"              # Unicode會在PDF中顯示錯誤
times = f"$a × b$"                   # Unicode會在PDF中顯示錯誤
```

### **已知注意事項**
```python
# 1. 模組導入路徑 - 現代化架構
from figures.params import PointParams, CircleParams  # ✅ 新架構 (主要使用)
from utils import get_logger, global_config            # ✅ 核心工具統一導入

# 2. 日誌系統使用
logger = get_logger(__name__)          # ✅ 模組級日誌器
logger.info("任務開始")                # 詳細資訊
logger.error(f"錯誤: {error}")         # 錯誤記錄

# 3. 配置管理 - 統一使用 global_config
debug_mode = global_config.debug_mode                    # ✅ 基本配置
precision = global_config.tikz_precision                 # ✅ TikZ精度
compiler = global_config.pdf_compiler                    # ✅ PDF編譯器
```

### **性能監控重點**
- **啟動時間**: 目標 < 2秒
- **題目生成**: 目標 < 100ms/題
- **PDF編譯**: 目標 2-5秒 (依題目數量)
- **記憶體使用**: 按需載入優化

### **🔄 模組導入機制設計**

#### **惰性導入策略 (Lazy Import)**

系統採用差異化的導入策略以優化性能：

**generators 模組 - 主動導入**
- **時機**: main.py 啟動時立即導入
- **原因**: UI 需要顯示題型列表給用戶選擇
- **註冊**: 6 個題目生成器立即註冊
- **影響**: 啟動時間約增加 0.3 秒

**figures 模組 - 惰性導入** ⭐ 關鍵設計
- **時機**: 首次 PDF 生成時由 FigureRenderer 觸發
- **原因**: UI 不需要圖形生成器，只在 PDF 階段使用
- **註冊**: 13 個圖形生成器延遲註冊
- **優勢**:
  - UI 啟動時間減少 15% (約 0.2-0.3 秒)
  - 節省記憶體 5-10 MB
  - 首次 PDF 生成時才載入

**導入流程對比**

```python
# 應用程式啟動
main.py
  ├─ import generators     ✅ 立即導入 (6個生成器註冊)
  ├─ from ui.main_window   ✅ UI 啟動完成
  └─ figures 模組          ❌ 不導入 (尚未註冊)

# 首次 PDF 生成
用戶點擊「生成PDF」
  └─ FigureRenderer.render()
       └─ import figures   ⭐ 此時才導入 (13個圖形生成器註冊)
```

**設計考量**
1. **時機選擇**: generators 需要 UI 展示，figures 只需生成時使用
2. **性能優化**: 將圖形載入延遲到實際需要時
3. **用戶體驗**: 更快的啟動時間提升使用感受
4. **記憶體效率**: 按需載入減少資源消耗

**開發注意事項**
- ⚠️ figures/__init__.py 的手動導入代碼是註冊機制核心，不可移除
- ⚠️ 新增圖形生成器時必須添加到 __init__.py 的導入列表
- ✅ 惰性導入是有意設計，不是缺陷
- 📄 詳見 figures/__init__.py 頂部的模組文檔說明

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

### **典範生成器設計標準**

#### **Sphinx友善文檔格式**
```python
"""三角反函數題目生成器

生成形如 arcsin(a), arccos(b), arctan(c) 的三角反函數計算題目。

Args:
    options (Dict[str, Any], optional): 生成器配置選項
        max_value (int): 函數輸入值最大範圍，預設10
        allow_arcsin (bool): 是否允許arcsin題型，預設True

Returns:
    Dict[str, Any]: 包含題目、答案、解釋等完整資訊

Example:
    >>> generator = InverseTrigonometricFunctionGenerator()
    >>> question = generator.generate_question()
    >>> print(question['question'])
    計算：$\\sin^{-1}(0.5)$
"""
```

#### **年級分類系統**
```python
def _get_standard_metadata(self):
    return {
        'grade': 'G10S2',  # 高一下學期格式
        'category': self.category,
        'subcategory': self.subcategory,
        'difficulty': self.difficulty
    }
```

## 🎯 **典範開發目標**

### **生成器品質標準**
- [ ] 代碼行數合理：一般檔案 < 200行，範本生成器可達300行（含完整註解）
- [ ] 使用f字串處理簡單LaTeX格式化
- [ ] 完整Sphinx文檔格式
- [ ] 年級分類系統整合
- [ ] 數學邏輯正確性

### **教師友善設計**
- [ ] 參數設置簡單直觀
- [ ] 代碼易讀易維護
- [ ] 錯誤訊息清楚明確
- [ ] 輸出格式標準一致

### **開發者參考價值**
- [ ] 可複製的設計模式
- [ ] 詳盡的設計理念註解
- [ ] 技術選擇的明確說明
- [ ] 避免過度工程化的示範

## 🚨 **核心開發原則**

### **🔒 Git操作安全規範（情境化許可版本）** (最高優先級)

#### **Git操作分類與權限**

**Level 0 - 單次安全查看** (需說明目的，無需許可)
**適用情境**：了解當前狀態、檢查特定信息
**操作清單**：
- `git status` - 查看工作區狀態
- `git log --oneline -N` - 查看最近N次提交
- `git show [commit]` - 查看特定提交
- `git diff [specific scope]` - 查看特定範圍差異

**執行要求**：
- 必須說明目的：「我將執行 `git status` 來查看當前修改狀態，準備評估commit內容」
- 一次只能執行一個指令
- 不能連續批量執行

**Level 1 - 批量查看操作** (需要整體許可)
**適用情境**：commit準備、全面狀態評估、問題診斷
**操作清單**：
- 同時執行多個查看指令
- `git diff` 無範圍限制的完整差異
- `git log` 複雜查詢或長歷史

**執行要求**：
1. 說明批量查看計畫：「我需要執行以下查看指令來準備commit：」
2. 列出所有要執行的指令和目的
3. 評估影響：「這些都是查看操作，對代碼庫無風險」
4. 等待明確許可：用戶說「允許」、「執行」或「同意」

**Level 2 - 修改操作** (嚴格許可流程)
**適用情境**：所有會改變git狀態的操作
**操作清單**：
- `git add`, `git commit`, `git checkout`, `git reset`
- `git merge`, `git rebase`, `git stash`, `git clean`
- 任何其他修改性指令

**執行要求**：
1. 詳細說明指令動作：「git add . 會將所有修改文件加入暫存區」
2. 風險評估：「這會改變git狀態，但可以用git reset撤銷」
3. 明確許可：必須等待「允許」、「執行」、「同意」等授權詞語
4. 一次只能申請一個修改指令

#### **特殊情境規則**

**情境1：緊急查看**
當用戶要求立即了解狀態時，可以直接執行單次 `git status`，但仍需說明：
「應您要求立即查看git狀態」

**情境2：工作流程查看**
commit、分析問題等工作流程中的查看操作，歸類為批量查看，需要整體許可。

**情境3：違規處理**
- **Level 0違規**（忘記說明目的）：提醒即可
- **Level 1違規**（批量查看未許可）：記點1次
- **Level 2違規**（修改操作未許可）：記點2次

#### **標準執行模板**

**單次查看模板**：
「我將執行 `[指令]` 來 [目的]」

**批量查看模板**：
```
我需要執行以下查看指令來[總體目的]：
- git status - 查看修改狀態
- git diff - 查看具體修改內容
- git log --oneline -5 - 查看最近提交記錄

這些都是查看操作，對代碼庫無風險。請允許執行。
```

**修改操作模板**：
```
我請求執行 `[指令]`：
- 動作說明：[詳細說明這個指令會做什麼]
- 風險評估：[可能的影響和撤銷方法]
- 請明確授權此操作
```

### **⛔ 代碼修改鎖定機制**

#### **🔒 絕對禁止未授權代碼修改**

**代碼修改三步驟強制流程**
1. **STOP** - 發現問題時立即停止，不得直接修改
2. **ANALYZE** - 分析問題並制定計畫文檔
3. **ASK** - 明確獲得用戶授權後才能執行

**修改前必須滿足的條件**
- [ ] 已完成問題分析文檔
- [ ] 已制定詳細修復計畫
- [ ] 用戶明確說出「開始修改」、「獲得授權」、「開始實施」
- [ ] 計畫中明確列出所有將修改的文件

**絕對禁止的行為**
❌ 看到錯誤立即修改
❌ 「順便」修復發現的問題
❌ 「小修改不需要討論」的想法
❌ 任何形式的「我覺得這個改一下比較好」
❌ 「這只是導入問題」等藉口式修改

**違反處罰機制**
- 第一次違反：立即停止，制定補救計畫
- 再次違反：用戶有權要求重新開始會話

#### **🛡️ 強制檢查點機制**

**在使用任何修改工具前，必須確認：**
1. ✅ 用戶是否明確授權這次修改？
2. ✅ 這個修改是否在已批准的計畫內？
3. ✅ 我是否已經制定了完整的修復計畫？
4. ✅ 用戶是否說了「開始」、「執行」、「修改」等授權詞語？

**如果任何答案是「否」，立即停止並要求授權。**

#### **📋 發現問題時的標準回應模板**

```
我發現了 [具體問題]，但遵循開發原則，我不會立即修改代碼。

讓我先：
1. 分析問題的根本原因
2. 制定詳細的修復計畫
3. 列出所有需要修改的文件
4. 獲得您的明確授權

請問您希望我先制定修復計畫，還是有其他指示？
```

### **1️⃣ 先討論計畫再修改程式原則**

**絕對禁止盲目修改代碼**
- 先討論計畫再修改程式，論證完成、鎖定真實問題前絕不亂改
- 免得愈改愈錯，造成更多問題
- 所有程式碼修改必須先制定詳細計畫
- 計畫必須包含問題分析、修復策略、風險評估
- 計畫確認後才能開始執行修改

### **2️⃣ 工作計畫文檔命名規範**

**中文檔名 + 前後綴格式**
- 前綴：日期 (格式: YYYYMMDD)
- 主檔名：中文具體命名，清楚描述計畫內容
- 後綴：進度狀態 (研擬中/執行中/已完成/已暫停)
- 文檔一律存放進docs/中，
**範例**:
- `20250915_防參差佈局修復計畫_研擬中.md`
- `20250916_UI組件重構方案_執行中.md`
- `20250917_性能優化實施策略_已完成.md`

### **3️⃣ 工作計畫示例代碼抽象化原則**

**示例代碼要抽象化，不要太具體**
- 避免影響之後AI實作的彈性
- 提供概念性示例，保留實作細節的自由度
- 重點在於說明邏輯流程和架構設計
- 具體實作細節在執行階段再確定

### **4️⃣ 系統性問題解決方法論**

**八步驟問題解決流程**
1. **定位可能的問題**: 主動搜尋和識別潛在問題點
2. **論證問題**: 分析問題的根本原因和影響範圍
3. **確認問題**: 通過測試和驗證確定問題的具體表現
4. **提出解決方案**: 制定完整的修復策略
5. **確認方案可行性**: 評估解決方案不會造成新問題
6. **檢查類似問題**: 系統性檢查是否存在相同類型的其他問題
7. **建立防範制度**: 形成不會再產生類似問題的機制
8. **執行解決**: 最後才著手實際修復

### **5️⃣ 計畫驅動開發原則**

**形成完整計畫檔案並確認前不修改代碼**
- 計畫文檔必須詳細到可以指導具體實作
- 包含測試驗證方案和成功標準定義
- 風險評估和回滾機制準備
- 所有關鍵決策都要有明確的論證過程

---

---

## 🔒 **代碼修改權限控制**

### **權限分級制度**

#### **Level 0 - 完全禁止修改**
- 任何 `.py` 文件
- 配置文件 (.json, .yaml, .ini)
- 重要文檔文件 (.md, .rst, .txt)

#### **Level 1 - 僅限分析查看**
- ✅ 可以使用 Read, Grep, Glob 工具
- ✅ 可以執行測試命令 (Bash with pytest, python -c)
- ✅ 可以創建分析報告文檔
- ❌ 禁止使用 Edit, Write, MultiEdit 工具

#### **Level 2 - 計畫制定階段**
- ✅ 可以創建計畫文檔 (修復計畫、分析報告)
- ✅ 可以討論修改方案
- ✅ 可以制定詳細實施步驟
- ❌ 必須獲得明確授權才能進入 Level 3

#### **Level 3 - 授權修改執行**
- ✅ 用戶明確說「開始實施」、「獲得授權」後才能使用修改工具
- ✅ 每個修改必須在已批准計畫範圍內
- ✅ 超出計畫範圍需要重新停止並獲得授權
- ⚠️ 修改完成後立即回到 Level 1

### **授權關鍵詞識別**

**明確授權詞語 (進入 Level 3)**
- "開始實施"
- "開始修改"
- "獲得授權"
- "執行修復"
- "開始執行"

**非授權詞語 (保持 Level 1-2)**
- "檢查一下"
- "看看問題"
- "分析一下"
- "制定計畫"
- "你覺得呢"

---

---

## 📚 **重要參考文檔**

### **典範參考**
- `generators/algebra/double_radical_simplification.py` - 已完成的典範生成器範例
- `docs/20250916_雙重根號生成器典範重寫工作計畫.md` - 成功的重寫方法論

### **開發指南**
- [`docs/figure_development_guide.md`](docs/figure_development_guide.md) - 圖形開發指南
- [`pytest.ini`](pytest.ini) - 測試配置

---

---

## 🚨 **Claude Code 違規記錄**

### **違規計點系統**
- **Git違規操作**: 未經許可執行git指令
- **代碼修改違規**: 未經計畫修改代碼
- **累計上限**: 10點 → 不續訂Claude，改用Gemini試用

### **違規記錄**
| 日期 | 違規類型 | 描述 | 當前點數 |
|------|---------|------|----------|
| 2025-09-25 | Git違規操作 | 未經授權執行 git add 操作 | 1/10 |
| 2025-09-29 | 代碼修改違規 | 未經計畫和授權直接修改 double_radical_simplification.py | 2/10 |
| 2025-10-10 | Git違規操作 | 未說明目的直接執行 git status | 3/10 |

---

**專案狀態**: 🌟 典範生成器建立階段 - 雙重根號生成器已完成典範化
**開發重點**: 建立可複製的開發模式，供未來開發者和教師參考
**品質目標**: 教師友善、開發者友善的高品質數學測驗生成系統
**核心理念**: 該用基礎招式的時候用基礎招式，該用華麗大招的時候用華麗大招
**代碼保護**: Level 1 - 僅限分析查看模式