# 數學生成器重寫建議指南

> **目標**: 回歸簡潔實用的生成器設計，捨棄過度工程化的Pydantic架構  
> **原則**: 教師友善、易於維護、專注核心功能  
> **日期**: 2025-09-12

## 📋 **重寫策略總覽**

### **核心設計原則**
1. **簡潔優先**: 每個生成器控制在150-250行內
2. **實用主義**: 只保留真正需要的功能，避免過度抽象
3. **教師友善**: 代碼易讀易修改，降低學習門檻
4. **PDF兼容**: 完全支援LaTeX格式，確保PDF生成正常

### **捨棄的過度工程**
- ❌ Pydantic參數驗證類
- ❌ 複雜的枚舉類定義
- ❌ 過度分割的私有方法
- ❌ HTML格式的數學表達式
- ❌ Unicode符號（如 °）

### **保留的優良實踐**
- ✅ 簡潔的參數處理
- ✅ 清晰的核心生成邏輯
- ✅ 標準的LaTeX格式
- ✅ 必要的PDF兼容欄位

---

## 🏗️ **標準生成器架構模板**

### **基礎框架結構**

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - [具體生成器名稱]

簡潔的生成器描述，說明主要功能和適用範圍。
避免過度詳細的docstring。
"""

import random
from typing import Dict, Any, List, Optional
import sympy
from sympy import latex

from ..base import QuestionGenerator, QuestionSize, register_generator

@register_generator
class [GeneratorName](QuestionGenerator):
    """[生成器名稱] - 簡潔描述
    
    主要功能說明，1-2句話即可。
    """
    
    # 如果需要LaTeX模板，使用類變量統一管理
    LATEX_TEMPLATES = {
        "question": "${func_name}({angle}) = $",
        "answer": "${result}$",
        "explanation": {
            "intro": "計算 ${func_name}({angle}) 的步驟：",
            "step1": "當 ${angle} 時，座標為 $({x}, {y})$",
            "result": "因此 ${func_name}({angle}) = {result}$"
        }
    }
    
    def __init__(self, options: Dict[str, Any] = None):
        """初始化生成器
        
        Args:
            options: 可選的配置選項
        """
        super().__init__(options)
        self.options = options or {}
        
        # 簡潔的參數處理，使用預設值
        self.functions = self.options.get("functions", ["sin", "cos", "tan"])
        self.difficulty = self.options.get("difficulty", "MEDIUM")
        self.angles = self.options.get("angles", [0, 30, 45, 60, 90])
        
        # 如果需要查詢表，建立簡潔版本
        self._build_lookup_tables()
    
    def generate_question(self) -> Dict[str, Any]:
        """生成一個數學題目
        
        Returns:
            Dict[str, Any]: 包含題目完整資訊的字典
        """
        # 核心生成邏輯，避免過度分割為私有方法
        # 最多分割為2-3個helper方法
        
        # 1. 選擇參數
        func = random.choice(self.functions)
        angle = random.choice(self.angles)
        
        # 2. 計算結果
        result = self._calculate_result(func, angle)
        
        # 3. 格式化輸出
        question = self._format_question(func, angle)
        answer = self._format_answer(result)
        explanation = self._format_explanation(func, angle, result)
        
        return {
            "question": question,
            "answer": answer,
            "explanation": explanation,
            "size": self.get_question_size(),
            "difficulty": self.difficulty,
            "category": self.get_category(),
            "subcategory": self.get_subcategory(),
            # PDF必需欄位
            "figure_data_question": None,  # 或適當的圖形數據
            "figure_data_explanation": None
        }
    
    def _calculate_result(self, func: str, angle: int) -> sympy.Expr:
        """計算數學結果的核心邏輯"""
        # 簡潔的計算邏輯
        pass
    
    def _format_question(self, func: str, angle: int) -> str:
        """格式化題目文字"""
        # 使用模板或簡潔的字符串格式化
        return f"${func}({angle}^\\circ) = $"
    
    def _format_answer(self, result: sympy.Expr) -> str:
        """格式化答案"""
        return f"${latex(result)}$"
    
    def _format_explanation(self, func: str, angle: int, result: sympy.Expr) -> str:
        """格式化詳解"""
        # 使用模板化方法，參考TrigEquationSolverGenerator
        return f"計算 ${func}({angle}^\\circ)$ 的步驟..."
    
    def _build_lookup_tables(self):
        """建立必要的查詢表（如果需要）"""
        # 只建立真正需要的查詢表
        pass
    
    # 標準方法，必須正確實現
    def get_question_size(self) -> int:
        """獲取題目大小"""
        return QuestionSize.SMALL.value  # 注意：使用.value避免bug
    
    def get_category(self) -> str:
        """獲取題目類別"""
        return "數學領域"
    
    def get_subcategory(self) -> str:
        """獲取題目子類別"""
        return "具體題型"
```

---

## 🎯 **關鍵實施要點**

### **1. 參數處理 - 簡潔方式**

```python
# ✅ 推薦：簡潔的參數處理
def __init__(self, options: Dict[str, Any] = None):
    super().__init__(options)
    self.options = options or {}
    
    # 直接使用預設值，無需複雜驗證
    self.functions = self.options.get("functions", ["sin", "cos", "tan"])
    self.difficulty = self.options.get("difficulty", "MEDIUM")
    self.use_degrees = self.options.get("use_degrees", True)

# ❌ 避免：Pydantic過度工程
class ComplexParams(BaseModel):
    functions: List[TrigFunction] = Field(default=[], description="...")
    difficulty: str = Field(pattern="^(EASY|MEDIUM|HARD)$", description="...")
    # ... 55行的參數定義
```

### **2. LaTeX處理 - 模板化方法**

```python
# ✅ 推薦：模板化LaTeX處理（基於TrigEquationSolverGenerator）
LATEX_TEMPLATES = {
    "question": "${func_name}({angle}^\\circ) = $",
    "basic_explanation": "因為 ${func_name} \\theta = {definition}$",
    "coordinates": "當 $\\theta = {angle}^\\circ$ 時，座標為 $({x}, {y})$",
    "result": "所以 ${func_name}({angle}^\\circ) = {calculation}$"
}

def format_latex_template(self, template_key: str, **kwargs) -> str:
    """統一的LaTeX格式化方法"""
    template = self.LATEX_TEMPLATES[template_key]
    # 確保數值經過latex()處理
    processed_kwargs = {}
    for key, value in kwargs.items():
        if isinstance(value, (sympy.Basic, int, float)):
            processed_kwargs[key] = latex(value)
        else:
            processed_kwargs[key] = str(value)
    return template.format(**processed_kwargs)

# ❌ 避免：內嵌字符串拼接
explanation = f"""因為 ${func_name} \\theta = {definition}$，\\\\ 
即{meaning} \\\\ {coords} \\\\ 所以 ${func_name}({angle}^\\circ) = {calc}$"""
```

### **3. 必須修復的Bug**

```python
# ✅ 正確：角度符號
"${angle}^\\circ$"          # LaTeX格式
"${\\sin}({angle}^\\circ)$" # 函數名也要正確

# ❌ 錯誤：Unicode符號
f"{angle}°"                 # 會在PDF中出問題

# ✅ 正確：Question Size
def get_question_size(self) -> int:
    return QuestionSize.SMALL.value  # 注意使用.value

# ❌ 錯誤：Question Size
return QuestionSize.SMALL    # 會返回enum對象
return QuestionSize.MEDIUM   # 4倍空間浪費

# ✅ 正確：必需PDF欄位
return {
    "question": question,
    "answer": answer,
    "explanation": explanation,
    "size": self.get_question_size(),
    "difficulty": self.difficulty,
    "category": self.get_category(),
    "subcategory": self.get_subcategory(),
    "figure_data_question": None,      # PDF必需
    "figure_data_explanation": None    # PDF必需
}
```

### **4. 代碼組織原則**

```python
# ✅ 推薦：2-3個helper方法，職責清晰
class SimpleGenerator(QuestionGenerator):
    def generate_question(self) -> Dict[str, Any]:
        # 主要邏輯
    
    def _calculate_core_math(self, ...):
        # 數學計算
    
    def _format_output(self, ...):
        # 格式化輸出

# ❌ 避免：過度分割的私有方法
class ComplexGenerator(QuestionGenerator):
    def _choose_parameters(self):
    def _validate_parameters(self):
    def _calculate_basic_result(self):
    def _apply_transformations(self):
    def _format_question_text(self):
    def _format_answer_text(self):
    def _generate_step1_explanation(self):
    def _generate_step2_explanation(self):
    def _assess_difficulty_level(self):
    # ... 15個私有方法
```

---

## 📊 **重寫優先級與策略**

### **立即重寫（高優先級）**

**1. InverseTrigonometricFunctionGenerator**
- **膨脹比例**: 2.8倍（190行 → 535行）
- **主要問題**: 大量Pydantic代碼、過度抽象
- **重寫策略**: 參考舊版簡潔邏輯，修復LaTeX格式

**2. DoubleRadicalSimplificationGenerator**
- **膨脹比例**: 2.4倍（212行 → 507行）
- **主要問題**: HTML格式、Pydantic過度工程
- **重寫策略**: 完全重寫為LaTeX格式

### **次優先級重寫**

**3. TrigonometricFunctionGenerator**
- **膨脹比例**: 1.7倍（243行 → 410行）
- **主要問題**: 雖無Pydantic但仍過度複雜
- **重寫策略**: 回歸舊版簡潔性，保留圖形整合

**4. TrigAngleConversionGenerator**
- **膨脹比例**: 1.3倍（445行 → 572行）
- **主要問題**: Pydantic和複雜抽象
- **重寫策略**: 保留優良的LaTeX模板系統，簡化參數處理

**5. 待確認的第五個生成器**

---

## ✅ **重寫檢查清單**

### **代碼結構檢查**
- [ ] 總行數控制在150-250行內
- [ ] 無Pydantic相關代碼
- [ ] 最多3-4個主要方法
- [ ] 清晰的類變量定義

### **LaTeX格式檢查**
- [ ] 所有數學表達式使用`${...}$`包裹
- [ ] 角度使用`^\\circ`而非`°`
- [ ] 函數名使用`\\sin`, `\\cos`, `\\tan`格式
- [ ] 使用`sympy.latex()`處理複雜表達式

### **PDF兼容性檢查**
- [ ] 包含`figure_data_question`欄位
- [ ] 包含`figure_data_explanation`欄位
- [ ] `get_question_size()`返回`.value`
- [ ] 完全捨棄HTML格式

### **功能完整性檢查**
- [ ] 生成的題目數學正確
- [ ] 答案格式規範
- [ ] 詳解邏輯清晰
- [ ] 錯誤處理適當

### **教師友善度檢查**
- [ ] 代碼易讀易理解
- [ ] 參數修改簡單直接
- [ ] 註釋適量不冗餘
- [ ] 無需額外學習成本

---

## 🎯 **成功標準**

重寫成功的生成器應該：

1. **代碼量減少**: 相較新版減少40-60%代碼量
2. **功能等價**: 保持與舊版相同的教學價值
3. **PDF兼容**: 完美支援LaTeX/PDF生成
4. **易於維護**: 教師可以輕鬆理解和修改
5. **無regression**: 不引入新bug或功能缺失

### **參考最佳實踐**
- **LaTeX處理**: 學習`TrigEquationSolverGenerator`的模板化方法
- **代碼結構**: 參考舊版的簡潔性
- **PDF集成**: 保留必要的圖形數據欄位
- **錯誤修復**: 確保所有已知bug都得到修復

---

## 📝 **總結**

這份指南的核心思想是**回歸簡潔實用**，捨棄過度工程化的設計，專注於教學需求。每個重寫的生成器都應該是教師友善、易於維護、功能完整的優質教學工具。

記住：**簡潔不是簡陋，而是精練和專注**。