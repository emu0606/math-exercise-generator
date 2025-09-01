# 數學測驗生成器 - 開發指南

本文檔提供了如何為數學測驗生成器添加新題型的詳細指引。

## 架構概述

數學測驗生成器使用註冊模式來管理不同的題型生成器。主要組件包括：

1. **中央註冊系統**：管理所有生成器的註冊和查詢。
2. **生成器基類**：定義所有生成器必須實現的接口。
3. **具體生成器**：實現特定題型的生成邏輯。

## 添加新生成器的步驟

### 1. 創建生成器文件

首先，根據題型的類別創建一個新的 Python 文件。例如，如果要添加一個新的代數題型，可以在 `generators/algebra/` 目錄下創建一個新文件。

文件命名應該反映題型的特性，例如 `quadratic_equation.py`。

### 2. 實現生成器類

在新文件中，實現一個繼承自 `QuestionGenerator` 的生成器類：

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - [題型名稱]生成器
"""

from typing import Dict, Any

from ..base import QuestionGenerator, QuestionSize, register_generator


@register_generator
class MyNewGenerator(QuestionGenerator):
    """[題型名稱]生成器
    
    [簡短描述]
    """
    
    def __init__(self, options: Dict[str, Any] = None):
        """初始化生成器
        
        Args:
            options: 其他選項，如特定範圍、特定運算符等
        """
        super().__init__(options)
        
    def generate_question(self) -> Dict[str, Any]:
        """生成一個題目
        
        Returns:
            包含題目資訊的字典
        """
        # 實現題目生成邏輯
        # ...
        
        return {
            "question": "題目文字",
            "answer": "答案",
            "explanation": "解析",
            "size": self.get_question_size(),
            "difficulty": "MEDIUM"  # 或其他難度
        }
    
    def get_question_size(self) -> int:
        """獲取題目大小
        
        Returns:
            題目大小（使用 QuestionSize 枚舉值）
        """
        return QuestionSize.MEDIUM  # 或其他大小
    
    def get_category(self) -> str:
        """獲取題目類別
        
        Returns:
            題目類別名稱
        """
        return "類別名稱"  # 例如："代數"、"幾何"等
    
    def get_subcategory(self) -> str:
        """獲取題目子類別
        
        Returns:
            題目子類別名稱
        """
        return "子類別名稱"  # 例如："二次方程"、"三角函數"等
```

### 3. 實現生成邏輯

在 `generate_question` 方法中實現具體的題目生成邏輯。這通常包括：

1. 生成隨機參數
2. 構建題目文字
3. 計算答案
4. 生成解析步驟

確保返回的字典包含以下鍵：
- `question`：題目文字
- `answer`：答案
- `explanation`：解析
- `size`：題目大小
- `difficulty`：題目難度
- `figure_data_question`：（可選）題目圖形數據
- `figure_data_explanation`：（可選）詳解圖形數據
- `figure_position`：（可選）**題目**圖形相對於文字的位置。預設為 `'right'`。可選值：`'right'`（右側）, `'left'`（左側）, `'bottom'`（下方）, `'none'`（不顯示圖形，即使有 `figure_data_question`）。此選項僅影響**題目頁**的圖形佈局。
- `explanation_figure_position`：（可選）**詳解**圖形相對於文字的位置。預設為 `'right'`。可選值：`'right'`（圖文並排，圖在右）, `'bottom'`（圖在文字下方）。此選項僅影響**詳解頁**的圖形佈局。生成器應根據詳解圖形的大小和複雜度決定是否設置為 `'bottom'`。

### 4. 更新模組的 `__init__.py`

在相應模組的 `__init__.py` 文件中導入新的生成器類：

```python
from .my_new_generator import MyNewGenerator

__all__ = [..., 'MyNewGenerator']
```

### 5. 測試新生成器

創建一個測試文件來測試新生成器的功能：

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
測試 [題型名稱] 生成器
"""

import unittest
from generators.module.my_new_generator import MyNewGenerator


class TestMyNewGenerator(unittest.TestCase):
    """測試 [題型名稱] 生成器"""
    
    def setUp(self):
        """設置測試環境"""
        self.generator = MyNewGenerator()
    
    def test_generate_question(self):
        """測試生成題目"""
        question = self.generator.generate_question()
        
        # 檢查題目是否包含所有必要的鍵
        self.assertIn("question", question)
        self.assertIn("answer", question)
        self.assertIn("explanation", question)
        self.assertIn("size", question)
        self.assertIn("difficulty", question)
        
        # 其他特定於題型的測試
        # ...


if __name__ == "__main__":
    unittest.main()
```

## 註冊機制說明

生成器的註冊是通過裝飾器 `@register_generator` 自動完成的。這個裝飾器會在類定義時將生成器註冊到中央系統。

如果不希望自動註冊，可以設置類屬性 `auto_register = False`：

```python
@register_generator
class MyNewGenerator(QuestionGenerator):
    auto_register = False
    # ...
```

然後可以在需要時手動註冊：

```python
MyNewGenerator.register()
```

## 生成器選項

生成器可以接受一個選項字典，用於自定義生成行為。例如：

```python
generator = MyNewGenerator({
    'min_value': 1,
    'max_value': 100,
    'include_fractions': True
})
```

在生成器中，可以通過 `self.options` 訪問這些選項：

```python
min_value = self.options.get('min_value', 1)  # 預設值為 1
```

## 題目大小

題目大小使用 `QuestionSize` 枚舉定義，包括：

- `SMALL`：一單位大小
- `WIDE`：左右兩單位，上下一單位
- `SQUARE`：左右一單位，上下兩單位
- `MEDIUM`：左右兩單位，上下兩單位
- `LARGE`：左右三單位，上下兩單位
- `EXTRA`：左右四單位，上下兩單位

根據題目的複雜度和空間需求選擇適當的大小。

## 題目難度

題目難度通常使用以下字符串之一：

- `"EASY"`
- `"MEDIUM"`
- `"HARD"`
- `"CHALLENGE"`

或者使用 `"LEVEL_1"` 到 `"LEVEL_5"` 等級別。根據題目的難度級別選擇適當的難度。

## 最佳實踐

1. **參數隨機化**：確保生成的題目具有足夠的變化性。
2. **難度控制**：根據選項調整題目的難度。
3. **解析詳細**：提供清晰、詳細的解析步驟。
4. **邊界情況**：處理可能的邊界情況和特殊情況。
5. **代碼註釋**：添加足夠的註釋，解釋生成邏輯。
6. **單元測試**：為每個生成器編寫單元測試。

## 示例

以下是一個完整的生成器示例：

```
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 三角函數值計算題生成器（改進的詳解）
"""

import sympy
from sympy import sin, cos, tan, cot, csc, sec, pi, simplify, latex
import random
from typing import Dict, Any, List, Tuple, Union, Callable

from ..base import QuestionGenerator, QuestionSize, register_generator

@register_generator
class TrigonometricFunctionGenerator(QuestionGenerator):
    """三角函數值計算題生成器
    
    生成計算三角函數值的題目，使用新的圖形架構並提供簡潔明瞭的詳解。
    """
    
    def __init__(self, options: Dict[str, Any] = None):
        super().__init__(options)
        self.options = options or {}
        
        # 設定可用的三角函數
        self.functions = [sin, cos, tan, cot, sec, csc]
        if self.options.get("functions"):
            self.functions = self.options.get("functions")
        
        # 設定可用的角度
        self.angles = [0, 30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 240, 270, 300, 315, 330, 360]
        if self.options.get("angles"):
            self.angles = self.options.get("angles")
        
        self.difficulty = self.options.get("difficulty", "MEDIUM")
        
        # 創建三角函數值查詢表
        self.trig_values = self._build_trig_value_table()
        
        # 函數定義與幾何意義
        self.definitions = {
            "sin": "\\frac{y}{r}",
            "cos": "\\frac{x}{r}",
            "tan": "\\frac{y}{x}",
            "cot": "\\frac{1}{\\tan \\theta} = \\frac{x}{y}",
            "sec": "\\frac{1}{\\cos \\theta} = \\frac{r}{x}",
            "csc": "\\frac{1}{\\sin \\theta} = \\frac{r}{y}"
        }
        
        self.geometric_meanings = {
            "sin": "單位圓上點的y座標值",
            "cos": "單位圓上點的x座標值",
            "tan": "y座標除以x座標",
            "cot": "x座標除以y座標", 
            "sec": "半徑除以x座標",
            "csc": "半徑除以y座標"
        }
    
    def _build_trig_value_table(self) -> Dict[Tuple[Callable, int], Union[str, sympy.Expr]]:
        """構建三角函數值查詢表，包含所有角度的所有函數值和對應的坐標"""
        table = {}
        
        # 填充表格
        for func in self.functions:
            for angle in self.angles:
                key = (func, angle)
                
                # 計算角度對應的弧度
                angle_rad = angle * pi / 180
                
                try:
                    # 嘗試使用sympy計算值
                    value = simplify(func(angle_rad))
                    table[key] = value
                except Exception:
                    # 標記為錯誤
                    table[key] = "ERROR"
        
        return table
    
    def _get_unit_circle_coordinates(self, angle: int) -> Tuple[sympy.Expr, sympy.Expr]:
        """獲取單位圓上指定角度的坐標點
        
        Args:
            angle: 角度值（度）
            
        Returns:
            (x, y): 坐標點的x和y值
        """
        angle_rad = angle * pi / 180
        x = simplify(cos(angle_rad))
        y = simplify(sin(angle_rad))
        return (x, y)
    
    def generate_question(self) -> Dict[str, Any]:
        """生成一個題目"""
        # 隨機選擇角度和函數
        angle = random.choice(self.angles)
        func = random.choice(self.functions)
        func_name = func.__name__
        
        # 從查詢表獲取值
        value = self.trig_values.get((func, angle))
        
        # 如果值是錯誤標記，重新選擇一組
        while value == "ERROR":
            angle = random.choice(self.angles)
            func = random.choice(self.functions)
            func_name = func.__name__
            value = self.trig_values.get((func, angle))
        
        # 創建圖形數據
        figure_data_question = {
            'type': 'standard_unit_circle',
            'params': {
                'variant': 'question',
                'angle': angle,
                'show_coordinates': True,
                'show_angle': True,
                'show_point': True,
                'label_point': False,
                'show_radius': True
            },
            'options': {
                'scale': 1.0
            }
        }
        
        figure_data_explanation = {
            'type': 'standard_unit_circle',
            'params': {
                'variant': 'explanation',
                'angle': angle,
                'show_coordinates': True,
                'show_angle': True,
                'show_point': True,
                'show_radius': True
            },
            'options': {
                'scale': 1.2 # 'width' is removed as per refactoring plan
            }
        }
        
        # 生成題目文字
        question_text = f"${func_name}({angle}^\\circ)$ \\\\ $= $"

        # 生成答案（使用latex輸出）
        answer = f"${latex(value)}$"
        
        # 生成解析
        explanation = self._generate_explanation(func_name, angle, value)
        
        return {
            "question": question_text,
            "answer": answer,
            "explanation": explanation,
            "size": self.get_question_size(),
            "difficulty": self.difficulty,
            "figure_data_question": figure_data_question,
            "figure_data_explanation": figure_data_explanation,
            "figure_position": "right", # Controls question figure position
            "explanation_figure_position": "right" # Controls explanation figure position
        }
    
    def _generate_explanation(self, func_name: str, angle: int, value: Union[sympy.Expr, str]) -> str:
        """生成三角函數值計算的詳解，添加更清晰的換行符號
        
        Args:
            func_name: 三角函數名稱
            angle: 角度值（度）
            value: 函數值（sympy表達式）
            
        Returns:
            詳解文字，含有適當的LaTeX換行符號
        """
        # 獲取單位圓上的坐標
        x, y = self._get_unit_circle_coordinates(angle)
        
        # 函數定義和幾何意義
        definition = self.definitions.get(func_name, "")
        meaning = self.geometric_meanings.get(func_name, "")
        
        # 生成坐標說明
        coords = f"當 $\\theta = {angle}^\\circ$ 時，\\\\ 點的座標為 $({latex(x)}, {latex(y)})$"
        
        # 根據函數類型生成計算過程
        is_infinity = isinstance(value, sympy.core.numbers.Infinity) or isinstance(value, sympy.core.numbers.NegativeInfinity)
        
        if is_infinity:
            # 對於無窮大的情況，提供更詳細的說明
            if func_name == "tan" and (angle == 90 or angle == 270):
                reason = f"因為 $\\cos({angle}^\\circ) = {latex(x)} = 0$，\\\\ 所以分母為零"
                calc = f"\\frac{{{latex(y)}}}{{0}} = {latex(value)}"
            elif func_name == "cot" and (angle == 0 or angle == 180 or angle == 360):
                reason = f"因為 $\\sin({angle}^\\circ) = {latex(y)} = 0$，\\\\ 所以分母為零"
                calc = f"\\frac{{{latex(x)}}}{{0}} = {latex(value)}"
            elif func_name == "sec" and (angle == 90 or angle == 270):
                reason = f"因為 $\\cos({angle}^\\circ) = {latex(x)} = 0$，\\\\ 所以分母為零"
                calc = f"\\frac{{1}}{{0}} = {latex(value)}"
            elif func_name == "csc" and (angle == 0 or angle == 180 or angle == 360):
                reason = f"因為 $\\sin({angle}^\\circ) = {latex(y)} = 0$，\\\\ 所以分母為零"
                calc = f"\\frac{{1}}{{0}} = {latex(value)}"
            else:
                reason = "分母為零"
                calc = f"{latex(value)}"
            
            explanation = f"""因為 ${func_name} \\theta = {definition}$，\\\\ 即{meaning} \\\\ {coords} \\\\ {reason} \\\\ 所以 ${func_name}({angle}^\\circ) = {calc}$"""
        else:
            # 對於一般值，顯示計算過程
            if func_name == "sin":
                calc = f"{latex(y)}"
            elif func_name == "cos":
                calc = f"{latex(x)}"
            elif func_name == "tan":
                calc = f"\\frac{{{latex(y)}}}{{{latex(x)}}} = {latex(value)}"
            elif func_name == "cot":
                calc = f"\\frac{{{latex(x)}}}{{{latex(y)}}} = {latex(value)}"
            elif func_name == "sec":
                calc = f"\\frac{{1}}{{{latex(x)}}} = {latex(value)}"
            elif func_name == "csc":
                calc = f"\\frac{{1}}{{{latex(y)}}} = {latex(value)}"
            else:
                calc = f"{latex(value)}"
            
            explanation = f"""因為 ${func_name} \\theta = {definition}$，\\\\ 即{meaning} \\\\ {coords} \\\\ 所以 ${func_name}({angle}^\\circ) = {calc}$"""
        
        return explanation

    
    def get_question_size(self) -> int:
        """獲取題目大小"""
        return QuestionSize.SMALL
    
    def get_category(self) -> str:
        """獲取題目類別"""
        return "三角比"
    
    def get_subcategory(self) -> str:
        """獲取題目子類別"""
        return "三角函數值計算"	
```

## 使用註冊系統

在 PDF 生成器中，可以使用以下方式獲取生成器：

```python
from utils.registry import registry

# 獲取生成器類
generator_class = registry.get_generator("代數", "二次方程")

if generator_class:
    # 創建生成器實例
    generator = generator_class()
    
    # 生成題目
    question = generator.generate_question()
```

## 獲取所有類別和子類別

可以使用以下方式獲取所有已註冊的類別和子類別：

```python
from utils.registry import registry

# 獲取所有類別和子類別
categories = registry.get_categories()

# 獲取特定類別的所有子類別
subcategories = registry.get_subcategories("代數")
```

這對於構建用戶界面非常有用，可以顯示所有可用的題型。

## 使用圖形架構

數學測驗生成器提供了一個模組化的圖形生成架構，用於生成 TikZ 圖形。這個架構解決了直接嵌套 TikZ 代碼導致的編譯錯誤和格式問題。

### 圖形數據結構

在 `generate_question` 方法中，可以返回 `figure_data_question` 和 `figure_data_explanation` 字段，分別用於題目和詳解中的圖形：

```python
def generate_question(self) -> Dict[str, Any]:
    # 生成題目邏輯...
    
    # 創建圖形數據
    figure_data_question = {
        'type': 'standard_unit_circle',  # 圖形類型
        'params': {                      # 圖形參數
            'variant': 'question',       # 變體（'question' 或 'explanation'）
            'angle': 45,                 # 特定於圖形類型的參數
            'show_coordinates': True
        },
        'options': {                     # 渲染選項
            'width': '4cm',              # 圖形寬度
            'height': '4cm'              # 圖形高度
        }
    }
    
    figure_data_explanation = {
        'type': 'standard_unit_circle',
        'params': {
            'variant': 'explanation',    # 詳解變體通常包含更多信息
            'angle': 45,
            'show_coordinates': True
        },
        'options': {
            'width': '5cm',
            'height': '5cm'
        }
    }
    
    return {
        "question": "題目文字",
        "answer": "答案",
        "explanation": "解析",
        "size": self.get_question_size(),
        "difficulty": "MEDIUM",
        "figure_data_question": figure_data_question,     # 題目圖形
        "figure_data_explanation": figure_data_explanation, # 詳解圖形
        "figure_position": "right",                         # (可選) 題目圖形位置 ('right', 'left', 'bottom', 'none')
        "explanation_figure_position": "right"              # (可選) 詳解圖形位置 ('right', 'bottom')
    }
```

**注意：** `figure_position` 鍵是用於控制 **題目頁面** 中圖形相對於文字的佈局。它會被 `LaTeXGenerator` 的
 `generate_question_tex` 方法讀取。預設情況下，如果題目有圖形數據 (`figure_data_question`) 
 但未提供 `figure_position`，圖形將顯示在文字的右側。如果設置為 `'none'`，即使提供了 `figure_data_question`，
 圖形也不會顯示在題目頁面中。
 
 **新增：** `explanation_figure_position` 鍵用於控制 **詳解頁面** 中圖形相對於文字的佈局。預設為 `'right'`（圖文並排），可設置為 `'bottom'`（圖在文字下方，通常用於較大的圖形）。此選項會被 `LaTeXGenerator` 的 `generate_explanation_tex` 方法讀取。

### 可用的圖形類型

系統提供了以下基礎圖形類型：

1. **`unit_circle`**：單位圓，包含角度、點等
2. **`circle`**：一般圓形
3. **`coordinate_system`**：坐標系
4. **`point`**：點
5. **`line`**：線段
6. **`angle`**：角度
7. **`label`**：文字標籤

還提供了以下預定義複合圖形類型：

1. **`standard_unit_circle`**：標準單位圓，包含坐標軸、圓、點、角度等

### 使用複合圖形

對於複雜的圖形，可以使用 `composite` 類型組合多個基礎圖形：

```python
figure_data = {
    'type': 'composite',
    'params': {
        'variant': 'question',
        'sub_figures': [
            {
                'id': 'circle1',  # 用於相對定位的 ID
                'type': 'circle',
                'params': {
                    'radius': 1.0,
                    'center_x': 0,
                    'center_y': 0
                },
                'position': {  # 絕對定位
                    'mode': 'absolute',
                    'x': 0,
                    'y': 0
                }
            },
            {
                'id': 'point1',
                'type': 'point',
                'params': {
                    'x': 1.0,
                    'y': 0,
                    'label': 'P'
                },
                'position': {  # 相對定位
                    'mode': 'relative',
                    'relative_to': 'circle1',  # 相對於 circle1
                    'placement': 'right',      # 放置在 circle1 的右側
                    'distance': '2cm'          # 距離
                }
            }
        ]
    },
    'options': {
        'width': '6cm',
        'height': '4cm'
    }
}
```

### 示例：改造現有生成器

以下是將現有的 `TrigonometricFunctionGenerator` 改造為使用新圖形架構的示例：

```python
def generate_question(self) -> Dict[str, Any]:
    # 原有的生成邏輯...
    angle = random.choice(self.angles)
    func = random.choice(self.functions)
    func_name = func.__name__
    
    # 創建圖形數據
    figure_data_question = {
        'type': 'standard_unit_circle',
        'params': {
            'variant': 'question',
            'angle': angle,
            'show_coordinates': True
        },
        'options': {
            'width': '4cm',
            'height': '4cm'
        }
    }
    
    # 返回結果
    return {
        "question": f"{func_name}({angle}^\\circ) = ?",
        "answer": answer,
        "explanation": explanation,
        "size": self.get_question_size(),
        "difficulty": self.difficulty,
        "figure_data_question": figure_data_question,
        "figure_data_explanation": figure_data_explanation
    }
```

完整示例可參考 `generators/trigonometry/TrigonometricFunctionGenerator.py`。
