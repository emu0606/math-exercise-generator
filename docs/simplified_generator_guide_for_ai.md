# AI 輔助數學題目生成器 - 教師溝通指引 (LaTeX 輸出核心)

本指引旨在協助教師與 AI 溝通，創建符合教學需求的數學題目生成器。核心目標是生成結構清晰、可直接用於 LaTeX 排版的題目、答案和詳解。

> **適用對象**: 數學教師、教育工作者、AI 協作開發  
> **技術需求**: 無需程式背景，專注數學教學邏輯  
> **更新日期**: 2025-09-08 (最新現代化架構)

## 教師溝通要點

### **題目設計核心**
- **題型定義**: 每個數學題型都有專屬的生成器，負責創建該類型的所有題目
- **教學目標**: 每個生成器都應對應明確的教學目標和學習重點
- **自動生成**: 系統會根據您的設定自動生成無限多的同類型題目
- **LaTeX 數學格式**: 所有數學表達式都使用專業的 LaTeX 格式，確保印刷品質

### **教師需要描述的內容**
- **數學概念**: 這個題型要測試學生的哪個數學概念？
- **題目結構**: 題目通常包含哪些元素？（例如：三角形的三邊長、角度等）
- **參數範圍**: 數值應該在什麼範圍內？（例如：邊長 1-10、角度 30°-150°）
- **難度設定**: 這是基礎題、進階題還是挑戰題？
- **解題步驟**: 標準解法有哪些關鍵步驟？
- **常見錯誤**: 學生容易在哪裡出錯？

### **技術支援**
系統使用現代化的數學計算引擎，確保：
- **計算精確性**: 使用專業數學庫進行符號運算，避免浮點數誤差
- **LaTeX 轉換**: 自動將數學表達式轉為專業排版格式
- **智能驗證**: 自動檢查參數合理性，避免數學邏輯錯誤
- **穩定運行**: 完整的錯誤處理和日誌記錄系統

## 生成器範例程式碼範本

以下是一個現代化的生成器範本，整合了最新的教學設計理念和技術架構。教師可以專注於數學內容的描述，AI 會處理技術細節。

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - [請填寫題型名稱]生成器

教學目標：[請描述這個題型的教學目標]
適用年級：[請填寫適用年級]
數學概念：[請列出相關的數學概念]
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field, validator
import sympy
import numpy as np
import random

from generators.base import QuestionGenerator, QuestionSize, register_generator
from utils import get_logger, global_config

# 設定日誌
logger = get_logger(__name__)


class QuestionParams(BaseModel):
    """
    題目參數設定 - 教師可調整的選項
    
    這些參數讓教師可以控制題目的特性，無需理解程式技術細節。
    """
    # 數值範圍設定
    min_value: int = Field(default=1, description="最小數值")
    max_value: int = Field(default=100, description="最大數值")
    
    # 難度控制
    difficulty_level: str = Field(default="MEDIUM", description="難度等級：EASY/MEDIUM/HARD")
    
    # 題目特性
    include_decimals: bool = Field(default=False, description="是否包含小數")
    require_steps: bool = Field(default=True, description="是否需要詳細解題步驟")
    
    @validator('difficulty_level')
    def validate_difficulty(cls, v):
        """確保難度設定正確"""
        valid_levels = ['EASY', 'MEDIUM', 'HARD', 'CHALLENGE']
        if v not in valid_levels:
            raise ValueError(f"難度必須是 {valid_levels} 中的一個")
        return v
    
    @validator('min_value', 'max_value')
    def validate_range(cls, v):
        """確保數值範圍合理"""
        if v < 1 or v > 1000:
            raise ValueError("數值範圍應在 1-1000 之間")
        return v

@register_generator
class YourNewGeneratorName(QuestionGenerator):  # 請將 YourNewGeneratorName 改為有意義的名稱
    """
    [請填寫題型的教學描述]
    
    教學目標：[例如：讓學生熟練運用餘弦定理解三角形問題]
    適用情境：[例如：已知三邊求角度，或已知兩邊夾角求第三邊]
    學習重點：[例如：餘弦定理公式應用、三角函數計算]
    
    Parameters:
        params: QuestionParams - 教師可調整的參數設定
    """
    
    def __init__(self, params: QuestionParams = None):
        """初始化生成器
        
        Args:
            params: 教師設定的參數，如果未提供則使用預設值
        """
        super().__init__()
        self.params = params or QuestionParams()
        logger.info(f"初始化 {self.__class__.__name__}，難度：{self.params.difficulty_level}")
        
    def generate_question(self) -> Dict[str, Any]:
        """生成一個題目及其相關資訊
        
        這個方法會根據教師設定的參數，自動生成符合教學需求的題目。
        AI 會處理以下教學設計流程：
        
        1. **參數生成**: 根據教師設定的範圍生成合適的數值
        2. **題目構建**: 建立符合教學目標的題目文字
        3. **答案計算**: 使用精確的數學運算得出正確答案
        4. **解題步驟**: 提供清晰的解題過程，幫助學生理解
        5. **教學重點**: 強調關鍵概念和常見錯誤預防
        
        Returns:
            包含完整題目資訊的字典
        """
        logger.debug(f"開始生成題目，參數：{self.params.dict()}")
        
        # --- 教師描述的數學邏輯轉換區 ---
        # 在這裡，AI 會根據教師的數學描述來實現具體的題目生成邏輯
        
        try:
            # 範例：根據參數範圍生成數值
            num1 = random.randint(self.params.min_value, self.params.max_value)
            num2 = random.randint(self.params.min_value, self.params.max_value)
            
            # 轉換為 sympy 物件以確保精確計算
            sym_num1 = sympy.Integer(num1)
            sym_num2 = sympy.Integer(num2)
            
            # 建立題目文字（LaTeX 格式）
            question_text = f"計算 ${sympy.latex(sym_num1)} + {sympy.latex(sym_num2)}$ 的值。"
            
            # 計算精確答案
            answer_value = sym_num1 + sym_num2
            answer_text = f"${sympy.latex(answer_value)}$"
            
            # 生成教學導向的解題步驟
            if self.params.require_steps:
                explanation_text = (
                    f"**解題思路**：這是基本的加法運算。\\\\ "
                    f"**第一步**：識別要相加的兩個數：${sympy.latex(sym_num1)}$ 和 ${sympy.latex(sym_num2)}$。\\\\ "
                    f"**第二步**：進行加法計算：${sympy.latex(sym_num1)} + {sympy.latex(sym_num2)} = {sympy.latex(answer_value)}$。\\\\ "
                    f"**答案**：${sympy.latex(answer_value)}$"
                )
            else:
                explanation_text = f"${sympy.latex(sym_num1)} + {sympy.latex(sym_num2)} = {sympy.latex(answer_value)}$"
            
            logger.info(f"成功生成題目：{num1} + {num2} = {answer_value}")
            
        except Exception as e:
            logger.error(f"題目生成失敗：{e}")
            raise
        
        # --- 圖形設定區（根據教學需求選用）---
        figure_data_q = None  # 題目圖形：如不需要圖形輔助說明，設為 None
        figure_data_e = None  # 解析圖形：如不需要圖形輔助解釋，設為 None
        
        # 教師如需圖形輔助教學，可參考以下結構：
        # 
        # 適用情境：幾何題、三角函數、座標系統等需要視覺化的題型
        # 
        # figure_data_q = {
        #     'type': 'triangle',  # 圖形類型：triangle, unit_circle, coordinate_plane 等
        #     'params': {
        #         'variant': 'question',    # 題目用圖形
        #         'sides': [3, 4, 5],      # 教師指定的三角形邊長
        #         'labels': True,          # 是否標示邊長
        #         'angles': False          # 是否顯示角度
        #     },
        #     'options': {
        #         'scale': 1.0,            # 圖形大小
        #         'style': 'clean'         # 圖形風格：clean, detailed
        #     }
        # }
        # 
        # figure_data_e = {
        #     'type': 'triangle',
        #     'params': {
        #         'variant': 'explanation', # 解析用圖形，通常更詳細
        #         'sides': [3, 4, 5],
        #         'labels': True,          
        #         'angles': True,          # 解析圖顯示角度
        #         'calculations': True     # 顯示計算過程
        #     },
        #     'options': {
        #         'scale': 1.2,           # 解析圖稍大一些
        #         'style': 'detailed'     # 更詳細的風格
        #     }
        # }
        
        # --- 結束您的題目生成邏輯 ---
        
        return {
            "question": question_text,                    # 題目文字（專業 LaTeX 格式）
            "answer": answer_text,                      # 答案（LaTeX 格式）
            "explanation": explanation_text,            # 解析（LaTeX 格式，含教學重點）
            "size": self.get_question_size(),           # 版面大小（系統自動決定）
            "difficulty": self.params.difficulty_level, # 難度等級（按教師設定）
            "figure_data_question": figure_data_q,      # 題目輔助圖形（可選）
            "figure_data_explanation": figure_data_e,   # 解析輔助圖形（可選）
            "figure_position": "right",                 # 圖形位置（right/left/bottom）
            "explanation_figure_position": "right"      # 解析圖形位置
        }
    
    def get_question_size(self) -> int:
        """自動決定題目版面大小
        
        系統會根據題目內容和複雜度自動選擇適當的版面大小：
        - SMALL: 簡短題目，適合單行顯示
        - MEDIUM: 標準題目，適合大部分情況（預設）
        - WIDE: 橫向較寬的題目，如長算式
        - LARGE: 需要更多空間的複雜題目
        
        教師通常不需要調整這個設定。
        """
        return QuestionSize.MEDIUM
    
    def get_category(self) -> str:
        """設定題目的主要數學領域
        
        請從以下教學大綱中選擇最符合的類別：
        
        **高中數學主要類別**：
        - "數與式" - 基礎數學運算、代數式
        - "多項式函數" - 一次、二次、高次函數
        - "指數與對數函數" - 指數、對數運算與函數
        - "三角比" - 基本三角函數、三角恆等式
        - "直線與圓" - 解析幾何基礎
        - "平面向量" - 向量運算與應用
        - "數列與級數" - 等差、等比數列
        - "排列組合" - 計數原理
        - "機率" - 機率計算與統計
        - "極限" - 微積分預備
        - "微分" - 導數與應用
        - "積分" - 積分與應用
        
        **進階類別**：
        - "空間向量"、"矩陣"、"二次曲線"、"複數" 等
        
        Returns:
            主類別名稱（字串）
        """
        return "[請選擇一個主類別]"  # 例如: "三角比"
    
    def get_subcategory(self) -> str:
        """設定題目的具體教學重點
        
        請根據具體的教學目標定義子類別名稱，幫助題庫分類和檢索。
        
        **命名建議**：
        - 突出教學重點："餘弦定理應用"、"特殊角計算"
        - 明確題型特色："已知三邊求角"、"分式化簡"
        - 反映解題方法："配方法"、"因式分解"
        
        **實例參考**：
        - "特殊角三角函數值" （三角比類別下）
        - "一元二次方程解法" （數與式類別下）
        - "導數的幾何意義" （微分類別下）
        
        Returns:
            子類別名稱（字串）
        """
        return "[請填寫具體的教學重點]"  # 例如: "餘弦定理解三角形"

```

## 教師與 AI 協作流程

### **第一步：明確教學需求**
教師需要向 AI 描述以下內容：

1. **教學目標**：這個題型要達成什麼教學目標？
2. **數學概念**：涉及哪些數學概念和公式？
3. **題目結構**：典型的題目包含哪些元素？
4. **參數設定**：數值範圍、難度等級、特殊要求
5. **解題流程**：標準解法的關鍵步驟
6. **教學重點**：需要強調的概念和常見錯誤

### **第二步：AI 技術實現**
AI 會根據教師的描述：

1. **創建參數模型**：定義教師可調整的題目參數設定
2. **實現生成邏輯**：將數學教學邏輯轉換為程式邏輯
3. **設定分類資訊**：建立題目的分類和標籤系統
4. **整合現代架構**：使用專業的數學計算引擎和穩定的系統框架

### **第三步：測試與調整**

1. **功能測試**：驗證題目生成的正確性
2. **教學測試**：確認符合教學需求
3. **參數調整**：根據實際使用情況優化設定

### **範本使用說明**

1. **複製範本**：AI 會基於上述程式範本創建新的生成器
2. **自訂命名**：將 `YourNewGeneratorName` 改為描述性的名稱（如 `CosineLawGenerator`）
3. **填寫描述**：在 docstring 中詳細描述教學目標和適用情境
4. **參數設定**：根據教學需求調整 `QuestionParams` 的預設值
5. **分類設定**：選擇適當的主類別和子類別

## 圖形輔助教學說明

### **何時需要圖形？**
以下題型通常需要圖形輔助教學：
- **幾何題目**：三角形、圓形、多邊形等
- **三角函數**：單位圓、三角函數圖形
- **座標幾何**：直線、拋物線、圓的方程式
- **向量問題**：向量圖示、平行四邊形法則
- **統計圖表**：直方圖、散佈圖等

### **圖形設定結構**
如果題目需要圖形輔助，可以在 `generate_question` 方法中設定 `figure_data_question` 和 `figure_data_explanation`：

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

### **圖形參數說明**

- **`type`**: 圖形類型，常用選項：
  - `triangle` - 三角形圖形（適用幾何、三角函數題目）
  - `unit_circle` - 單位圓（適用三角函數題目）
  - `coordinate_plane` - 座標平面（適用解析幾何題目）
  - `function_graph` - 函數圖形（適用函數題目）

- **`params`**: 圖形的數學參數
  - `variant` - 圖形用途：`'question'`（題目用）或 `'explanation'`（解析用）
  - 其他參數依圖形類型而定，如邊長、角度、座標等

- **`options`**: 圖形的顯示選項
  - `scale` - 圖形大小（1.0 為標準大小）
  - `style` - 圖形風格（`'clean'` 簡潔，`'detailed'` 詳細）

### **教師指導原則**

1. **題目圖形**：提供必要資訊，不透露答案
2. **解析圖形**：詳細標示，協助理解解題過程
3. **圖形複雜度**：配合學生程度，避免過度複雜
4. **教學重點**：突出關鍵概念，淡化次要資訊

**注意**：圖形系統會自動處理 LaTeX 格式和版面配置，教師只需專注於教學內容的設計。

---

## 開始使用這份指引

### **教師準備工作**
1. **明確教學目標**：確定要創建哪種類型的題目
2. **分析學生需求**：了解適當的難度和範圍
3. **收集教材範例**：準備幾個典型題目作為參考
4. **思考常見錯誤**：列出學生容易犯的錯誤

### **與 AI 協作建議**
1. **具體描述**：儘量具體地描述題目特徵和教學要求
2. **提供範例**：給出 2-3 個理想的題目範例
3. **逐步驗證**：先測試基本功能，再調整細節
4. **持續優化**：根據實際使用情況不斷改進

### **成功案例分享**
- **三角函數生成器**：從特殊角計算到一般角應用
- **二次函數生成器**：從基本圖形到實際應用問題
- **機率生成器**：從簡單事件到複合機率問題

現在，您可以根據這份指引，開始與 AI 協作創建符合教學需求的數學題目生成器了！

---

> **技術特色**：採用現代化數學計算架構，確保計算精確性和系統穩定性  
> **持續改進**：隨教學需求和技術發展不斷優化功能  
> **教師回饋**：歡迎提供使用心得，協助改進系統以更好服務教學需求