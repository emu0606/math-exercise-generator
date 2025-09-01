# AI 輔助數學題目生成器 - 簡化開發指引 (LaTeX 輸出核心)

本指引旨在引導您（AI）創建一個新的數學題目生成器。核心目標是生成結構清晰、可直接用於 LaTeX 排版的題目、答案和詳解。

## 核心概念

- **生成器類 (Generator Class)**：每個題型都由一個繼承自 `QuestionGenerator` 的 Python 類別來實現。
- **註冊機制**: 使用 `@register_generator` 裝飾器自動註冊生成器。
- **核心方法**: `generate_question()` 是最重要的方法，負責生成題目的所有內容。
- **LaTeX 輸出**: 所有文字內容（題目、答案、詳解）最終都會被渲染成 LaTeX。因此，在生成這些內容時，請直接使用合法的 LaTeX 語法。
- **計算函式庫**:
    - **符號計算與 LaTeX 轉換**: 強烈建議使用 `sympy`。例如，`sympy.latex()` 可以將 `sympy` 表達式轉換為 LaTeX 字串。
    - **數值計算**: 強烈建議使用 `numpy`。
    - **避免使用**: 請避免使用 Python 內建的 `math` 模組，以確保計算精度和 LaTeX 相容性。

## 生成器範例程式碼骨架

以下是一個基礎的生成器類別範例。您可以複製此範本，並根據具體的題型需求進行修改和填充。

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - [請填寫題型名稱]生成器
"""

from typing import Dict, Any
import sympy # 建議用於符號運算和 LaTeX 輸出
import numpy # 建議用於數值運算

# 假設 QuestionGenerator, QuestionSize, register_generator 已從某處導入
# from ..base import QuestionGenerator, QuestionSize, register_generator
# 為了簡化，以下為示意，實際路徑需依專案結構調整
class QuestionGenerator: # pragma: no cover
    def __init__(self, options=None): # options 暫不使用
        pass
    def get_question_size(self):
        return QuestionSize.MEDIUM # 預設大小
class QuestionSize: # pragma: no cover
    SMALL = 1
    WIDE = 2
    SQUARE = 3
    MEDIUM = 4
    LARGE = 5
    EXTRA = 6

def register_generator(cls): # pragma: no cover
    # 示意註冊邏輯
    # print(f"Generator {cls.__name__} registered.")
    return cls
# --- 示意結束 ---

@register_generator
class YourNewGeneratorName(QuestionGenerator): # 請將 YourNewGeneratorName 改為有意義的名稱
    """[請填寫題型的簡短描述]
    
    例如：生成關於餘弦定理的計算題。
    """
    
    def __init__(self):
        """初始化生成器。
        目前不需要額外選項。
        """
        super().__init__()
        
    def generate_question(self) -> Dict[str, Any]:
        """生成一個題目及其相關資訊。
        
        您需要在此方法中實現以下邏輯：
        1. 生成隨機參數 (若有)。
        2. 構建題目文字 (LaTeX 格式)。
        3. 計算答案 (LaTeX 格式)。
        4. 生成解析步驟 (LaTeX 格式)。
        5. (可選) 準備圖形數據。
        
        Returns:
            包含題目資訊的字典。
        """
        # --- 開始您的題目生成邏輯 ---
        
        # 範例：生成一個簡單的加法題目
        num1 = sympy.Integer(numpy.random.randint(1, 100))
        num2 = sympy.Integer(numpy.random.randint(1, 100))
        
        question_text = f"計算 ${sympy.latex(num1)} + {sympy.latex(num2)}$ 的值。"
        
        answer_value = num1 + num2
        answer_text = f"${sympy.latex(answer_value)}$"
        
        explanation_text = (
            f"這是一個簡單的加法問題。\\\\ "
            f"我們需要計算 ${sympy.latex(num1)}$ 加上 ${sympy.latex(num2)}$。\\\\ "
            f"計算過程如下：\\\\ "
            f"${sympy.latex(num1)} + {sympy.latex(num2)} = {sympy.latex(answer_value)}$。"
        )
        
        # (可選) 圖形數據結構範例
        figure_data_q = None # 如果題目不需要圖形，設為 None
        figure_data_e = None # 如果詳解不需要圖形，設為 None
        
        # 如果需要圖形，可以參考以下結構 (詳細參數請參考完整指南)
        # figure_data_q = {
        #     'type': 'standard_unit_circle',  # 或其他圖形類型
        #     'params': {
        #         'variant': 'question',
        #         # ... 特定於圖形類型的參數 ...
        #         'angle': 45 # 範例參數
        #     },
        #     'options': {
        #         'scale': 1.0 # 範例選項
        #     }
        # }
        # figure_data_e = {
        #     'type': 'standard_unit_circle',
        #     'params': {
        #         'variant': 'explanation',
        #         # ... 特定於圖形類型的參數 ...
        #         'angle': 45,
        #         'show_coordinates': True # 範例參數
        #     },
        #     'options': {
        #         'scale': 1.2
        #     }
        # }
        
        # --- 結束您的題目生成邏輯 ---
        
        return {
            "question": question_text,          # 題目文字 (LaTeX 格式)
            "answer": answer_text,              # 答案 (LaTeX 格式)
            "explanation": explanation_text,    # 解析 (LaTeX 格式)
            "size": self.get_question_size(),   # 題目大小 (通常不需要修改)
            "difficulty": "MEDIUM",             # 題目難度 (EASY, MEDIUM, HARD, CHALLENGE, LEVEL_1~5)
            "figure_data_question": figure_data_q,      # (可選) 題目的圖形數據
            "figure_data_explanation": figure_data_e,   # (可選) 詳解的圖形數據
            "figure_position": "right",                 # (可選) 題目圖形位置 ('right', 'left', 'bottom', 'none')
            "explanation_figure_position": "right"      # (可選) 詳解圖形位置 ('right', 'bottom')
        }
    
    def get_question_size(self) -> int:
        """獲取題目大小。
        
        通常返回 QuestionSize.MEDIUM。可根據題目內容調整。
        """
        return QuestionSize.MEDIUM # 或 QuestionSize.SMALL, QuestionSize.WIDE 等
    
    def get_category(self) -> str:
        """獲取題目主類別。
        
        請從以下列表中選擇一個最合適的類別名稱：
        [ "數與式", "指數、對數", "多項式函數", "直線與圓", "數列與級數", 
          "數據分析", "排列組合", "機率", "三角比", "指數與對數函數", 
          "平面向量", "空間向量", "空間中的平面與直線", "矩陣", "極限", 
          "微分", "積分", "二次曲線", "複數", "統計機率" ]
        
        Returns:
            題目主類別名稱 (字串)。
        """
        return "[請從上述列表中選擇並填寫一個類別]" # 例如: "三角比"
    
    def get_subcategory(self) -> str:
        """獲取題目子類別。
        
        請根據題型特性自行定義一個明確的子類別名稱。
        例如："餘弦定理應用"、"特殊角三角函數值" 等。
        
        Returns:
            題目子類別名稱 (字串)。
        """
        return "[請填寫具體的子類別名稱]" # 例如: "餘弦定理解三角形"

```

## 您的任務

1.  **複製範本**：將上述範例程式碼骨架複製到一個新的 Python 檔案中 (例如 `my_cosine_law_generator.py`)。
2.  **修改類別名稱與描述**：
    *   將 `YourNewGeneratorName` 修改為能反映題型的具體名稱 (例如 `CosineLawProblemGenerator`)。
    *   在類別的 docstring 中填寫題型的簡短描述。
3.  **實現 `generate_question` 方法**：
    *   這是核心任務。您需要在此方法內編寫邏輯來生成題目、答案和詳解。
    *   **務必使用 LaTeX 格式** 處理所有文字輸出。
    *   **優先使用 `sympy` 和 `numpy`** 進行計算。
    *   如果題目需要圖形，請按照 `figure_data_question` 和 `figure_data_explanation` 的結構準備數據。如果不需要，將它們設為 `None`。
4.  **設定 `get_category`**：
    *   從提供的類別列表中選擇一個最符合您題型的類別，並修改 `get_category` 方法的回傳值。
5.  **設定 `get_subcategory`**：
    *   為您的題型定義一個清晰的子類別名稱，並修改 `get_subcategory` 方法的回傳值。
6.  **調整 `get_question_size` 和 `difficulty` (可選)**：
    *   根據題目內容的複雜度和篇幅，您可能需要調整 `get_question_size` 的回傳值。
    *   在 `generate_question` 回傳的字典中，根據題目難易程度設定 `difficulty` 的值。

## 圖形數據基本說明 (`figure_data_question` / `figure_data_explanation`)

如果您需要在題目或詳解中加入圖形，`generate_question` 方法回傳的字典中可以包含 `figure_data_question` 和 `figure_data_explanation` 兩個鍵。它們的值應該是一個字典，基本結構如下：

```python
{
    'type': 'figure_type_name',  # 例如: 'standard_unit_circle', 'triangle', 'custom_plot'
    'params': {                  # 傳遞給該圖形類型生成器的參數
        'variant': 'question',   # 或 'explanation'
        # ... 其他特定於 'figure_type_name' 的參數 ...
        # 例如: 'angle': 60, 'sides': [3, 4, 5]
    },
    'options': {                 # 控制圖形渲染的選項
        # 例如: 'scale': 1.0, 'width': '5cm'
    }
}
```

-   `type`: 指定要使用的圖形生成器類型。
-   `params`: 包含一個 `variant` ('question' 或 'explanation') 以及其他傳遞給特定圖形生成器的參數。
-   `options`: 控制圖形渲染的通用選項，如縮放比例、寬高等。

**注意**: 關於可用的圖形類型 (`figure_type_name`) 及其具體參數，請參考完整的開發指南或現有的生成器範例。本簡化指引僅提供基本結構。

---

現在，您可以根據這份簡化指引，開始引導 AI 創建您的餘弦定理練習題生成器了。