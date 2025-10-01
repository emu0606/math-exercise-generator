# AI 生成器開發速查指南

> **目標讀者**: AI 助手（Claude、GPT 等）
> **使用場景**: 與人類教師協作開發數學題目生成器
> **最後更新**: 2025-10-01

---

## 🚀 5 秒速覽

### 核心 4 步驟
1. **繼承基類**: `class YourGenerator(QuestionGenerator)`
2. **實作方法**: `_generate_core_question()` 返回標準 dict
3. **配置讀取**: 用 `options.get(key, default)` 簡潔處理
4. **LaTeX 格式**: 所有數學符號用 LaTeX（`^\\circ` 不是 `°`）

### 關鍵 2 禁忌（AI 真正容易犯的錯誤）
- ❌ **Unicode 數學符號**: `°` `×` `√` `±` 會導致 PDF 編譯失敗
- ❌ **HTML 標籤**: `<br>` 要用 LaTeX `\\\\` 換行

---

## ⚠️ 如何使用本決策流程

**這是思考框架，不是問卷調查**

下面的 Q1-Q11 不是要你逐一詢問的清單，而是幫助你理解「需要確認哪些資訊」的思考框架。

**正確做法**:
1. 快速評估人類提供了哪些資訊
2. 綜合詢問 2-4 個**關鍵的未確認資訊**
3. 如果資訊完整，直接開始實作

**錯誤做法**:
- ❌ 機械式逐一詢問 Q1→Q2→Q3...Q11
- ❌ 重複詢問人類已經說過的資訊
- ❌ 問太多細節而不開始寫代碼

**範例對比**:

❌ **過度詢問（機器人式）**:
```
人類: 「寫一個多項式展開生成器」
AI: Q1 核心數學概念是什麼？
AI: Q2 能舉 2-3 個例題嗎？
AI: Q3 學生做這類題目時，什麼數字範圍合適？
AI: Q4 有沒有給定一組例題？
...（人類開始不耐煩）
```

✅ **智能確認（自然對話）**:
```
人類: 「寫一個多項式展開生成器」
AI: 「我理解您需要 (x+a)(x+b) 展開為 x²+...x+... 的練習題。
    建議係數範圍 a, b ∈ [1, 10]，分類為『數與式』→『多項式展開』(G9S2)。
    不需配置和圖形，對嗎？」
人類: 「對，開始寫吧」
AI: 「好的，開始實作...」
```

---

## 🤝 人機協作決策流程

### 階段 1: 理解題型結構 (與人類對話)

**Q1: 這個題型的核心數學概念是什麼？**
```
人類可能回答：
「計算三角反函數」
「化簡雙重根號」
「求等差數列第 n 項」

AI 行動：理解核心概念，準備相關數學工具
```

**Q2: 能舉 2-3 個具體例題嗎？**
```
人類提供範例：
例題 1: sin⁻¹(1/2) = ?
例題 2: sin⁻¹(√3/2) = ?
例題 3: cos⁻¹(0) = ?

AI 行動：分析例題，提取共同模式
- 識別：都是特殊角的三角函數值
- 識別：答案都是角度（需要 ^\\circ）
- 識別：涉及分數、根號的 LaTeX 格式化
```

**Q3: 學生做這類題目時，什麼數字範圍合適？**
```
與人類討論：
- 「應該用 30°、45°、60° 這些特殊角」
- 「避免複雜角度，學生難以計算」
- 「可以包含負角和鈍角，增加變化」

AI 行動：確定參數範圍和選取策略
```

**Q4: 這個題型有沒有給定一組例題？**
```
如果人類說：
「我有 10 題現成的題目，想要系統隨機出這些題」

AI 行動：
→ 改用「題庫模式」，直接從清單隨機選取
→ 不需要複雜的生成邏輯
```

---

### 階段 2: 數學邏輯設計 (共同決定策略)

**Q5: 這個題型有數學約束條件嗎？**
```
決策樹：

├─ 無約束（如：簡單加減法）
│   → 直接隨機生成
│   → 參考：InverseTrigonometricFunctionGenerator.py L86-132
│
├─ 簡單約束（如：分母不能為 0）
│   → 隨機生成 + 單次驗證
│   → 用 if 語句排除無效情況
│
└─ 複雜約束（如：雙重根號要求內外都是完全平方數）
    → 使用預篩選策略
    → 在 __init__ 建立 valid_combinations
    → 從清單隨機選取保證成功
    → 參考：double_radical_simplification.py L50-70
```

**Q6: 需要預篩選嗎？判斷標準：**
```
需要預篩選的情況：
✅ 隨機生成很難滿足條件（成功率 < 50%）
✅ 需要多個參數互相配合（如：a² + b = c²）
✅ 有教學意義的「特定組合」（如：勾股數 3-4-5）

不需要預篩選的情況：
❌ 參數獨立，無相互約束
❌ 條件簡單，容易隨機滿足
❌ 範圍夠大，碰撞機率低
```

**Q7: 答案格式是什麼？如何格式化？**
```
與人類確認答案類型，選擇 LaTeX 格式化方式：

├─ 整數：直接 f"${value}$"
├─ 角度：f"${value}^\\circ$"（注意雙反斜線）
├─ 分數：用 sympy.latex(Rational(a, b))
├─ 根號：用 sympy.latex(sqrt(n))
└─ 複雜表達式：一律用 sympy.latex() 避免錯誤
```

---

### 階段 3: 配置與圖形 (確認靈活性需求)

**Q8: 這個生成器需要哪些配置？**
```
與人類討論**這個特定生成器**需要的配置：
「你希望教師能調整什麼參數？」
「哪些應該固定，哪些應該可變？」

實際範例（三角反函數生成器）：
- functions: 可選的函數類型 ["sin", "cos", "tan"]

實際範例（雙重根號生成器）：
- max_outer_sqrt: 外根號數值上限

**重點**：配置是**專屬的**，不同生成器有不同需求。
參考典範代碼的 __init__ 方法學習配置模式。
```

**Q9: 這個題型需要配圖嗎？**
```
需要配圖的題型：
✅ 幾何題（三角形、圓形）
✅ 三角函數（單位圓）
✅ 座標幾何（直線、拋物線）
✅ 向量（向量圖示）

不需要配圖：
❌ 純代數運算
❌ 數列計算
❌ 簡單三角函數值

如需配圖，詢問人類：
「需要什麼類型的圖？（三角形/單位圓/座標平面）」
「題目圖和解答圖要一樣嗎？」
```

---

### 階段 4: 解題步驟設計 (教學重點)

**Q10: 標準解法有幾個關鍵步驟？**
```
與人類討論解題流程：

人類：「這題要先判斷象限，再查特殊角表，最後確認值域」

AI 生成 explanation：
f"**第一步**：判斷象限...\\\\ "
f"**第二步**：查特殊角表...\\\\ "
f"**第三步**：確認值域...\\\\ "
f"**答案**：......"

注意：用 \\\\ 換行，不是 <br>
```

**Q11: 有常見錯誤需要提醒嗎？**
```
人類可能說：
「學生常忘記 arcsin 值域是 [-90°, 90°]」
「學生容易算錯根號化簡」

AI 在 explanation 加入提示：
f"**注意**：arcsin 的值域為 [-90°, 90°]，因此答案需調整到此範圍。"
```

---

## 📖 典範代碼導讀

### 推薦學習路徑

#### **入門級（必讀）**: InverseTrigonometricFunctionGenerator.py
**路徑**: `generators/trigonometry/InverseTrigonometricFunctionGenerator.py`

**關鍵理解點**：
```python
# L47-58: options.get() 簡潔配置模式
def __init__(self, options=None):
    options = options or {}
    self.functions = options.get("functions", ["sin", "cos", "tan"])
    self.difficulty = options.get("difficulty", "MEDIUM")
    # 無需 Pydantic，簡單直接

# L86-132: _generate_core_question() 核心結構
def _generate_core_question(self):
    # 1. 選擇參數
    func_name = random.choice(self.functions)
    angle_deg = random.choice(self.special_angles)

    # 2. 計算數學邏輯
    angle_rad = sympy.rad(angle_deg)
    value = trig_func(angle_rad)

    # 3. LaTeX 格式化
    value_latex = latex(value)
    answer = f"${adjusted_angle}^\\circ$"

    # 4. 返回標準格式
    return {
        "question": question_text,
        "answer": answer,
        "explanation": explanation,
        **self._get_standard_metadata()
    }

# L149-167: 數學邏輯範例（值域調整）
def _adjust_angle_to_range(self, angle_deg, func_name):
    # 確保答案在反三角函數值域內
    if func_name == "sin":
        # arcsin 值域 [-90°, 90°]
    elif func_name == "cos":
        # arccos 值域 [0°, 180°]
    # ...
```

**學到什麼**：
- ✅ 簡潔的配置處理（不用 Pydantic）
- ✅ 清晰的數學邏輯分段
- ✅ 正確的 LaTeX 格式化
- ✅ 標準的返回格式

---

#### **中級（預篩選範例）**: DoubleRadicalSimplificationGenerator.py
**路徑**: `generators/algebra/double_radical_simplification.py`

**關鍵理解點**：
```python
# L50-70: __init__ 中建立 valid_combinations
def __init__(self, options=None):
    # 預先建立所有有效組合，避免隨機失敗
    self.valid_combinations = []
    for a in range(1, max_outer + 1):
        for b in range(1, max_inner + 1):
            if self._is_valid_combination(a, b):
                self.valid_combinations.append((a, b))

# L100-120: 從預篩選清單隨機選取
def _generate_core_question(self):
    # 直接從 valid_combinations 隨機選，保證 100% 成功
    a, b = random.choice(self.valid_combinations)
    # ...
```

**學到什麼**：
- ✅ 確定性生成設計（預篩選策略）
- ✅ 避免隨機失敗的重試機制
- ✅ 適用於複雜數學約束的場景

---

### 抽象結構速查

```python
from generators.base import QuestionGenerator, register_generator
from utils import get_logger
import random
import sympy

@register_generator
class YourGenerator(QuestionGenerator):
    """你的生成器描述

    教學目標：...
    適用年級：...

    Args:
        options: 配置選項（可選）
            key1: 說明
            key2: 說明
    """

    def __init__(self, options=None):
        super().__init__(options)
        self.logger = get_logger(self.__class__.__name__)

        # [1] 讀取配置
        options = options or {}
        self.param1 = options.get('param1', default_value)
        self.param2 = options.get('param2', default_value)

        # [2] 預建資料（如需預篩選）
        # self.valid_combinations = self._build_combinations()

    def _generate_core_question(self):
        """核心生成邏輯"""

        # [3] 參數生成/選取
        # ⚠️ 以下是常見模式範例，需根據你的題型調整，不要直接複製！

        # 模式1：從預建清單選取（參考 InverseTrigonometricFunctionGenerator）
        angle = random.choice(self.special_angles)  # 你需在 __init__ 建立 self.special_angles = [0, 30, 45, ...]

        # 模式2：直接隨機整數（適合簡單計算題）
        coefficient = random.randint(1, 10)  # 直接指定合理範圍

        # 模式3：從預篩選組合選取（參考 DoubleRadicalSimplificationGenerator）
        # a, b = random.choice(self.valid_combinations)  # 你需在 __init__ 呼叫 _build_valid_combinations()

        # 🚨 重要：使用有意義的變數名（angle, coefficient），不要用 value1, value2

        # [4] 數學計算（根據你的題型實作）
        result = sympy.sin(angle)  # 範例：使用 sympy 計算

        # [5] LaTeX 格式化
        question_text = f"計算 ${sympy.latex(expr)}$"
        answer = f"${sympy.latex(result)}$"
        explanation = self._generate_explanation(...)

        # [6] 返回標準格式
        return {
            "question": question_text,
            "answer": answer,
            "explanation": explanation,
            **self._get_standard_metadata()
        }

    def _get_standard_metadata(self):
        """標準元數據"""
        return {
            "size": self.get_question_size(),
            "difficulty": self.difficulty,
            "grade": "G10S2",  # 年級格式
            "category": "主類別",
            "subcategory": "子類別"
        }
```

---

## 📦 結構速查表

### 必需方法

| 方法 | 簽名 | 說明 |
|------|------|------|
| `__init__` | `(self, options=None)` | 初始化，讀取配置 |
| `_generate_core_question` | `(self) -> Dict[str, Any]` | 核心生成邏輯 |
| `_get_standard_metadata` | `(self) -> Dict[str, Any]` | 返回元數據 |

### 標準返回格式（7 個必需欄位）

```python
{
    "question": str,        # 題目文字（LaTeX 格式）
    "answer": str,          # 答案（LaTeX 格式）
    "explanation": str,     # 詳解（LaTeX 格式，用 \\\\ 換行）
    "size": int,            # 版面大小（QuestionSize.MEDIUM）
    "difficulty": str,      # 難度（"EASY"/"MEDIUM"/"HARD"）
    "grade": str,           # 年級（"G10S2" 格式）
    "category": str,        # 主類別
    "subcategory": str      # 子類別
}
```

### 可選欄位（圖形相關）

```python
{
    "figure_data_question": dict | None,      # 題目圖形
    "figure_data_explanation": dict | None,   # 解答圖形
    "figure_position": str,                   # 題目圖形位置: "right"(預設)/"left"/"bottom"/"none"
    "explanation_figure_position": str        # 解答圖形位置: "right"(預設)/"bottom"/"none" (無"left")
}
```

---

### LaTeX 符號速查

| Unicode ❌ | LaTeX ✅ | 說明 |
|-----------|---------|------|
| `°` | `^\\circ` | 角度（注意雙反斜線）|
| `×` | `\\times` | 乘號 |
| `÷` | `\\div` | 除號 |
| `√` | `\\sqrt{}` | 根號 |
| `±` | `\\pm` | 正負號 |
| `≤` | `\\leq` | 小於等於 |
| `≥` | `\\geq` | 大於等於 |
| `π` | `\\pi` | 圓周率 |
| `<br>` | `\\\\` | 換行（4 個反斜線）|

**重要**: 在 f-string 中，`\\` 會被解釋為單個 `\`，所以：
- `f"${value}^\\circ$"` → 正確（單個 `\` 在字串中）
- `f"step1 \\\\ step2"` → 正確（兩個 `\\` 變成 LaTeX 的 `\\`）

---

## ⚠️ 關鍵禁忌與檢查清單

### 禁忌 1: Unicode 數學符號

```python
# ❌ 錯誤：PDF 編譯會失敗
question = f"求 sin(30°) 的值"
answer = f"90°"

# ✅ 正確：使用 LaTeX
question = f"求 $\\sin(30^\\circ)$ 的值"
answer = f"$90^\\circ$"
```

### 禁忌 2: HTML 標籤

```python
# ❌ 錯誤：PDF 中會顯示 <br> 文字
explanation = "步驟1<br>步驟2<br>答案"

# ✅ 正確：使用 LaTeX 換行
explanation = "步驟1 \\\\ 步驟2 \\\\ 答案"
```

### 禁忌 3: 忘記雙反斜線

```python
# ❌ 錯誤：單個 \ 在 Python 字串中需要轉義
text = f"${a} \circ$"  # 會出錯

# ✅ 正確：雙反斜線
text = f"${a}^\\circ$"
```

---

## ✅ 開發檢查清單

在提交代碼給人類前，檢查：

### 基礎結構
- [ ] 繼承 `QuestionGenerator`
- [ ] 使用 `@register_generator` 裝飾器
- [ ] 實作 `_generate_core_question()`
- [ ] 實作 `_get_standard_metadata()`

### LaTeX 格式
- [ ] 所有數學符號用 LaTeX（無 Unicode）
- [ ] 角度用 `^\\circ`（雙反斜線）
- [ ] 換行用 `\\\\`（四個反斜線）
- [ ] 複雜表達式用 `sympy.latex()`

### 返回格式
- [ ] 包含 7 個必需欄位
- [ ] `question`, `answer`, `explanation` 都是 LaTeX 格式
- [ ] `grade` 格式正確（如 "G10S2"）

### 配置處理
- [ ] 用 `options.get(key, default)` 讀取配置
- [ ] 所有配置都有合理預設值
- [ ] 參考典範代碼的配置模式

### 數學邏輯
- [ ] 確定性設計（避免隨機失敗）
- [ ] 複雜約束用預篩選
- [ ] 數學計算正確

---

## 🔗 快速參考

### 典範生成器路徑

```
入門級:
generators/trigonometry/InverseTrigonometricFunctionGenerator.py

中級（預篩選）:
generators/algebra/double_radical_simplification.py

進階（多模式）:
generators/trigonometry/TrigAngleConversionGenerator.py
```

### 常用工具導入

```python
from generators.base import QuestionGenerator, QuestionSize, register_generator
from utils import get_logger
import random
import sympy
from sympy import latex, sqrt, Rational
```

### 年級格式對照

| 年級 | 格式 | 說明 |
|------|------|------|
| 高一上 | G10S1 | Grade 10 Semester 1 |
| 高一下 | G10S2 | Grade 10 Semester 2 |
| 高二上 | G11S1 | Grade 11 Semester 1 |
| 高二下 | G11S2 | Grade 11 Semester 2 |

### 相關文檔

- **人類開發者指南**: [生成器開發指南.md](生成器開發指南.md)
- **檔案結構規範**: [生成器檔案結構規範.md](生成器檔案結構規範.md)
- **完整文檔導航**: [開發指南索引.md](開發指南索引.md)

---

## 🎯 實戰演練範例

### 場景：人類說「幫我寫一個等差數列通項公式的生成器」

#### AI 的回應流程：

```
✅ 1. 理解題型
「好的，我理解這是等差數列通項公式 an = a1 + (n-1)d 的計算題。」

✅ 2. 詢問範例
「能給我 2-3 個具體例題嗎？例如：
- 等差數列首項 a1=3，公差 d=2，求第 10 項？
這樣的格式嗎？」

✅ 3. 確認參數範圍
「數值範圍建議：
- 首項 a1: 1~20
- 公差 d: -5~5（包含負數）
- 項數 n: 5~20
這樣合適嗎？」

✅ 4. 討論約束
「這題沒有複雜約束，可以直接隨機生成。」

✅ 5. 確認配置
「需要讓教師調整參數範圍嗎？」

✅ 6. 詢問圖形
「這題不需要配圖，對吧？」

✅ 7. 討論解題步驟
「標準解法：
1. 代入通項公式 an = a1 + (n-1)d
2. 計算 (n-1)d
3. 加上首項得答案
這樣對嗎？」

✅ 8. 開始編寫代碼
[根據決策結果，參考 InverseTrigonometricFunctionGenerator.py 的結構編寫]
```

---

**指南結束** - 開始與人類協作，創造優質的數學題目生成器！
