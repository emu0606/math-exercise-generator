# 數學測驗生成器 - 圖形生成器開發指南

本文檔提供了如何為數學測驗生成器開發新的圖形生成器的詳細指引。

## 架構概述

數學測驗生成器的圖形系統使用模組化架構，主要組件包括：

1. **`FigureGenerator` 抽象基類**：定義所有圖形生成器必須實現的接口。
2. **基礎圖形生成器**：實現基本圖形元素的生成，如點、線、圓等。
3. **複合圖形生成器**：組合多個基礎圖形，處理命名空間和定位問題。
4. **預定義複合圖形生成器**：提供常用複合圖形的簡化接口。
5. **參數模型**：使用 Pydantic 定義和驗證圖形參數。

## 開發新的基礎圖形生成器

### 1. 創建參數模型

首先，在 `figures/params_models.py` 中定義新圖形的參數模型：

```python
class MyNewFigureParams(BaseFigureParams):
    """我的新圖形參數模型"""
    param1: float = 1.0
    param2: str = 'default'
    param3: bool = True
    # 其他參數...
```

確保繼承 `BaseFigureParams`，以包含 `variant` 參數。

### 2. 創建生成器類

創建一個新的 Python 文件（例如 `figures/my_new_figure.py`），實現一個繼承自 `FigureGenerator` 的生成器類：

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 我的新圖形生成器
"""

from typing import Dict, Any
from pydantic import ValidationError

from .base import FigureGenerator
from .params_models import MyNewFigureParams
from . import register_figure_generator

@register_figure_generator
class MyNewFigureGenerator(FigureGenerator):
    """我的新圖形生成器
    
    [簡短描述]
    """
    
    @classmethod
    def get_name(cls) -> str:
        """獲取圖形類型唯一標識符"""
        return 'my_new_figure'
    
    def generate_tikz(self, params: Dict[str, Any]) -> str:
        """生成 TikZ 圖形內容
        
        Args:
            params: 圖形參數字典，應符合 MyNewFigureParams 模型
            
        Returns:
            TikZ 圖形內容（不包含 tikzpicture 環境）
            
        Raises:
            ValidationError: 如果參數驗證失敗
        """
        # 使用 Pydantic 模型驗證參數
        try:
            validated_params = MyNewFigureParams(**params)
        except ValidationError as e:
            raise ValidationError(f"參數驗證失敗: {str(e)}", e.raw_errors)
        
        # 提取參數
        param1 = validated_params.param1
        param2 = validated_params.param2
        param3 = validated_params.param3
        variant = validated_params.variant
        
        # 生成 TikZ 代碼
        tikz_content = "% 我的新圖形\n"
        
        # 根據變體生成不同的內容
        if variant == 'question':
            # 生成題目變體
            tikz_content += f"\\draw (0,0) circle ({param1});\n"
        else:  # 'explanation'
            # 生成詳解變體（通常包含更多信息）
            tikz_content += f"\\draw[red] (0,0) circle ({param1});\n"
            tikz_content += f"\\node at (0,0) {{{param2}}};\n"
        
        return tikz_content
```

### 3. 更新 `figures/__init__.py`

在 `figures/__init__.py` 中導入新的生成器類：

```python
# 基礎圖形生成器
from .my_new_figure import MyNewFigureGenerator
```

## 開發預定義複合圖形生成器

預定義複合圖形生成器是一種特殊的生成器，它不直接生成 TikZ 代碼，而是構建一個 `CompositeParams` 實例，然後使用 `CompositeFigureGenerator` 生成最終的 TikZ 代碼。

### 1. 創建參數模型

首先，在 `figures/params_models.py` 中定義新的預定義複合圖形參數模型：

```python
class MyPredefinedCompositeParams(BaseFigureParams):
    """我的預定義複合圖形參數模型"""
    param1: float = 1.0
    param2: str = 'default'
    # 其他參數...
```

### 2. 創建生成器類

創建一個新的 Python 文件（例如 `figures/predefined/my_predefined.py`），實現一個繼承自 `FigureGenerator` 的生成器類：

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 我的預定義複合圖形生成器
"""

from typing import Dict, Any, List
from pydantic import ValidationError

from ..base import FigureGenerator
from ..params_models import MyPredefinedCompositeParams, CompositeParams, SubFigureParams, AbsolutePosition
from .. import register_figure_generator, get_figure_generator

@register_figure_generator
class MyPredefinedCompositeGenerator(FigureGenerator):
    """我的預定義複合圖形生成器
    
    [簡短描述]
    """
    
    @classmethod
    def get_name(cls) -> str:
        """獲取圖形類型唯一標識符"""
        return 'my_predefined_composite'
    
    def generate_tikz(self, params: Dict[str, Any]) -> str:
        """生成 TikZ 圖形內容
        
        Args:
            params: 圖形參數字典，應符合 MyPredefinedCompositeParams 模型
            
        Returns:
            TikZ 圖形內容（不包含 tikzpicture 環境）
            
        Raises:
            ValidationError: 如果參數驗證失敗
        """
        # 使用 Pydantic 模型驗證參數
        try:
            validated_params = MyPredefinedCompositeParams(**params)
        except ValidationError as e:
            raise ValidationError(f"參數驗證失敗: {str(e)}", e.raw_errors)
        
        # 構建 CompositeParams 實例
        composite_params = self._build_composite_params(validated_params)
        
        # 獲取 CompositeFigureGenerator 實例
        composite_generator = get_figure_generator('composite')()
        
        # 使用 CompositeFigureGenerator 生成 TikZ 代碼
        return composite_generator.generate_tikz(composite_params.dict())
    
    def _build_composite_params(self, params: MyPredefinedCompositeParams) -> CompositeParams:
        """構建 CompositeParams 實例
        
        Args:
            params: 驗證後的 MyPredefinedCompositeParams 實例
            
        Returns:
            CompositeParams 實例
        """
        # 提取參數
        param1 = params.param1
        param2 = params.param2
        variant = params.variant
        
        # 創建子圖形列表
        sub_figures: List[SubFigureParams] = []
        
        # 添加第一個子圖形
        sub_figures.append(
            SubFigureParams(
                id="figure1",
                type="circle",
                params={
                    "radius": param1,
                    "center_x": 0,
                    "center_y": 0,
                    "variant": variant
                },
                position=AbsolutePosition(x=0, y=0)
            )
        )
        
        # 添加第二個子圖形
        sub_figures.append(
            SubFigureParams(
                id="figure2",
                type="label",
                params={
                    "x": 0,
                    "y": 0,
                    "text": param2,
                    "variant": variant
                },
                position=AbsolutePosition(x=0, y=0)
            )
        )
        
        # 創建 CompositeParams 實例
        return CompositeParams(
            variant=variant,
            sub_figures=sub_figures
        )
```

### 3. 更新 `figures/__init__.py`

在 `figures/__init__.py` 中導入新的生成器類：

```python
# 預定義複合圖形生成器
from .predefined.my_predefined import MyPredefinedCompositeGenerator
```

## 處理命名空間衝突

在複合圖形中，可能會出現命名空間衝突，例如多個子圖形使用相同的節點名稱。`CompositeFigureGenerator` 通過以下方式處理這個問題：

1. 為每個子圖形分配一個唯一的前綴（例如 `sf0_`, `sf1_` 等）。
2. 在子圖形的 TikZ 代碼中，將所有命名（如 `\coordinate`, `\node`, `\path` 等）替換為帶前綴的版本。
3. 使用 TikZ 的 `scope` 環境隔離每個子圖形。

開發者不需要手動處理這些問題，只需確保每個基礎圖形生成器生成的 TikZ 代碼使用標準的命名方式。

## 處理定位

複合圖形中的子圖形可以使用絕對定位或相對定位：

### 絕對定位

```python
'position': {
    'mode': 'absolute',
    'x': 0,
    'y': 0,
    'anchor': 'center'  # 子圖形的哪個錨點對齊到 (x, y)
}
```

### 相對定位

```python
'position': {
    'mode': 'relative',
    'relative_to': 'figure1',  # 相對於哪個子圖形的 id
    'placement': 'right',      # 放置方向
    'distance': '1cm',         # 距離
    'my_anchor': 'center',     # 當前子圖形用於對齊的錨點
    'target_anchor': 'east'    # 相對目標用於對齊的錨點
}
```

## 測試新的圖形生成器

創建一個測試文件來測試新的圖形生成器：

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
測試我的新圖形生成器
"""

import unittest
from figures import get_figure_generator

class TestMyNewFigureGenerator(unittest.TestCase):
    """測試我的新圖形生成器"""
    
    def setUp(self):
        """設置測試環境"""
        self.generator_cls = get_figure_generator('my_new_figure')
        self.generator = self.generator_cls()
    
    def test_generate_tikz(self):
        """測試生成 TikZ 代碼"""
        params = {
            'variant': 'question',
            'param1': 1.0,
            'param2': 'test',
            'param3': True
        }
        
        tikz_content = self.generator.generate_tikz(params)
        
        # 檢查 TikZ 代碼是否包含預期的內容
        self.assertIn('circle', tikz_content)
        self.assertIn('1.0', tikz_content)
        
        # 測試詳解變體
        params['variant'] = 'explanation'
        tikz_content = self.generator.generate_tikz(params)
        
        self.assertIn('red', tikz_content)
        self.assertIn('test', tikz_content)

if __name__ == "__main__":
    unittest.main()
```

## 最佳實踐

1. **參數驗證**：始終使用 Pydantic 模型驗證參數。
2. **變體處理**：根據 `variant` 參數生成不同的內容，詳解變體通常包含更多信息。
3. **代碼註釋**：添加足夠的註釋，解釋生成邏輯。
4. **錯誤處理**：提供清晰的錯誤信息，幫助用戶診斷問題。
5. **測試**：為每個生成器編寫單元測試。
6. **文檔**：在類和方法的文檔字符串中提供詳細的說明。
7. **尺寸控制**：圖形生成器 **不應** 處理最終的絕對尺寸（例如通過 `options` 中的 `width` 或 `height`）。最終尺寸由佈局函數 (`utils/latex_generator.py`) 使用 `\resizebox` 在容器 (`node` 或 `tcolorbox`) 內部進行控制。生成器可以處理 `options` 中的 `scale` 參數，以調整圖形內部的相對比例或大小。

## 示例

請參考以下文件作為示例：

- 基礎圖形生成器：`figures/unit_circle.py`
- 複合圖形生成器：`figures/composite.py`
- 預定義複合圖形生成器：`figures/predefined/standard_unit_circle.py`