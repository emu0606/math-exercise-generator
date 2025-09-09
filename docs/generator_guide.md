# 數學測驗生成器 - 開發指南 (新架構版)

本文檔提供了如何在新 6 層模組化架構下為數學測驗生成器添加新題型的詳細指引。

> 🆕 **重要更新**：本指南已根據 **Phase 4 Generators 現代化完成** 的最新實踐全面更新，包括 Pydantic 參數驗證、統一註冊系統、新架構工具整合等。

## 🏗️ 新架構概述

數學測驗生成器採用 6 層模組化架構，提供完整的生成器生態系統：

### 核心架構層次
1. **生成器層** (`generators/`): 各類題目生成器實現
2. **渲染層** (`utils/rendering/`): 圖形和內容渲染
3. **協調層** (`utils/orchestration/`): PDF 生成流程管理
4. **LaTeX 層** (`utils/latex/`): 文件生成和編譯
5. **TikZ 層** (`utils/tikz/`): 數學圖形處理
6. **幾何層** (`utils/geometry/`): 數學計算核心
7. **核心層** (`utils/core/`): 配置、註冊、日誌

### 核心組件
1. **統一註冊系統** (`utils/core/registry.py`): 自動發現和管理所有生成器
2. **統一 API** (`utils/__init__.py`): 提供一致的幾何和渲染接口
3. **配置管理** (`utils/core/config.py`): 全域配置和設定
4. **日誌系統** (`utils/core/logging.py`): 統一日誌管理
5. **渲染系統** (`utils/rendering/`): 圖形和內容渲染協調

## 📝 Sphinx 友善文檔標準

**所有新生成器必須遵循 Sphinx 友善的 docstring 標準**，以確保 API 文檔的完整性。

### ✅ 標準 Docstring 格式

```python
class MyQuestionGenerator:
    """我的題目生成器
    
    詳細描述生成器的功能、適用範圍和特色。
    說明生成的題型類別、難度範圍和可配置選項。
    
    Attributes:
        category (str): 題目類別
        subcategory (str): 題目子類別
        difficulty_levels (List[str]): 支援的難度級別
        
    Example:
        >>> generator = MyQuestionGenerator()
        >>> question = generator.generate_question()
        >>> print(question['question'])
    """
    
    def generate_question(self) -> Dict[str, Any]:
        """生成一個數學題目
        
        根據配置的參數生成一個完整的數學題目，包含
        題目文字、答案、詳解和可選的圖形。
        
        Returns:
            Dict[str, Any]: 包含以下鍵值的字典
                - question (str): 題目文字 (支援 LaTeX)
                - answer (str): 正確答案
                - explanation (str): 詳細解答步驟
                - size (QuestionSize): 題目大小
                - difficulty (str): 題目難度
                - figure_data_question (dict, optional): 題目圖形
                - figure_data_explanation (dict, optional): 詳解圖形
                
        Raises:
            ValueError: 如果配置參數無效
            GenerationError: 如果題目生成失敗
            
        Example:
            >>> generator = MyQuestionGenerator()
            >>> question = generator.generate_question()
            >>> assert 'question' in question
            >>> assert 'answer' in question
        """
        pass
```

## 🔧 新架構開發步驟

### 1. 創建生成器檔案

在 `generators/` 目錄下選擇適當的子目錄創建新生成器：
- `generators/algebra/` - 代數題
- `generators/geometry/` - 幾何題  
- `generators/trigonometry/` - 三角函數題
- `generators/calculus/` - 微積分題

檔案命名應反映具體功能，例如：`quadratic_equations.py`、`triangle_problems.py`

### 2. 實現新架構生成器

使用新架構的統一 API 實現生成器：

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 我的新題型生成器

此模組在新 6 層模組化架構下實現了一個示範生成器，採用 Phase 4 最新實踐。
使用 Pydantic 參數驗證、統一註冊系統和新架構核心工具。

特色：
- Pydantic 參數驗證系統
- 統一的註冊系統整合
- 新架構核心工具 (get_logger, global_config)
- 完整的 Sphinx docstring 支援
- 統一的幾何 API 整合
"""

import random
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, validator

# 導入新架構的統一 API（Phase 4 標準）
from utils import (
    construct_triangle, get_centroid, tikz_coordinate,
    global_config, get_logger, Point, Triangle
)

# 導入生成器基礎架構（Phase 4 統一註冊系統）
from ..base import QuestionGenerator, QuestionSize, register_generator

# 模組日誌器
logger = get_logger(__name__)


class QuestionParams(BaseModel):
    """題目參數 Pydantic 模型
    
    使用 Pydantic 進行參數驗證和類型檢查，這是 Phase 4 的標準實踐。
    提供智能參數驗證、類型轉換和錯誤處理。
    
    Attributes:
        min_value (int): 最小值範圍
        max_value (int): 最大值範圍
        difficulty (str): 題目難度
        include_decimals (bool): 是否包含小數
        
    Example:
        >>> params = QuestionParams(min_value=1, max_value=10)
        >>> params.min_value
        1
        >>> params = QuestionParams(min_value=10, max_value=5)  # 會觸發驗證錯誤
    """
    min_value: int = Field(
        default=1,
        ge=1,
        le=1000,
        description="數值範圍的最小值"
    )
    max_value: int = Field(
        default=100,
        ge=2,
        le=10000,
        description="數值範圍的最大值"
    )
    difficulty: str = Field(
        default="MEDIUM",
        description="題目難度級別"
    )
    include_decimals: bool = Field(
        default=False,
        description="是否包含小數運算"
    )
    
    @validator('difficulty')
    def validate_difficulty(cls, v):
        """驗證難度參數"""
        valid_difficulties = ['EASY', 'MEDIUM', 'HARD', 'CHALLENGE']
        if v not in valid_difficulties:
            raise ValueError(f"difficulty 必須是 {valid_difficulties} 中的一個")
        return v
        
    @validator('max_value')
    def validate_max_greater_than_min(cls, v, values):
        """驗證最大值大於最小值"""
        if 'min_value' in values and v <= values['min_value']:
            raise ValueError("max_value 必須大於 min_value")
        return v


@register_generator  # Phase 4 統一註冊系統
class MyQuestionGenerator(QuestionGenerator):
    """我的新題型生成器
    
    使用新 6 層模組化架構和 Phase 4 最新實踐生成數學題目。
    整合 Pydantic 參數驗證、新架構核心工具和統一註冊系統。
    
    此生成器展示 Phase 4 最佳實踐：
    1. 繼承 QuestionGenerator 基類
    2. 使用 @register_generator 裝飾器自動註冊
    3. 整合 Pydantic 參數驗證模型
    4. 使用新架構核心工具 (get_logger, global_config)
    5. 支援多種難度和智能參數驗證
    
    Attributes:
        params (QuestionParams): Pydantic 參數模型實例
        logger: 新架構日誌記錄器
        
    Example:
        >>> generator = MyQuestionGenerator()
        >>> question = generator.generate_question()
        >>> print(question['question'])
        
    Note:
        這是 Phase 4 現代化完成後的標準生成器範例，
        展示了完整的 Pydantic 整合和新架構工具使用。
    """
    
    def __init__(self, options: Optional[Dict[str, Any]] = None):
        """初始化題目生成器 (Phase 4 標準)
        
        使用 Pydantic 模型進行參數驗證和新架構核心工具進行初始化。
        
        Args:
            options (Dict[str, Any], optional): 配置選項字典，將轉換為 Pydantic 模型
                - min_value (int): 最小數值範圍
                - max_value (int): 最大數值範圍 
                - difficulty (str): 難度級別
                - include_decimals (bool): 是否包含小數
                
        Example:
            >>> generator = MyQuestionGenerator({
            ...     'min_value': 1,
            ...     'max_value': 50, 
            ...     'difficulty': 'HARD'
            ... })
            
        Note:
            Phase 4 使用 Pydantic 參數模型自動處理驗證和類型轉換。
        """
        super().__init__(options)
        
        # Phase 4: 使用 Pydantic 模型進行參數驗證
        self.params = QuestionParams(**(options or {}))
        
        # Phase 4: 新架構日誌系統
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
        self.logger.info(f"初始化 {self.__class__.__name__}，難度：{self.params.difficulty}")
        
        # Phase 4: 新架構配置系統整合
        self.precision = global_config.get('geometry.precision', 6)
        self.backend = global_config.get('geometry.backend', 'python')
        
        self.logger.debug(f"使用數學後端：{self.backend}，精度：{self.precision}")
    
    def generate_question(self) -> Dict[str, Any]:
        """生成一個完整的數學題目
        
        根據配置的參數生成一個完整的數學題目，
        包含題目文字、答案、詳解和可選的圖形。
        
        Returns:
            Dict[str, Any]: 包含以下鍵值的字典
                - question (str): 題目文字 (支援 LaTeX 格式)
                - answer (str): 正確答案
                - explanation (str): 詳細解答步驟
                - size (str): 題目大小 ('SMALL', 'MEDIUM', 'LARGE' 等)
                - difficulty (str): 題目難度
                - figure_data_question (dict, optional): 題目圖形數據
                - figure_data_explanation (dict, optional): 詳解圖形數據
                - figure_position (str, optional): 題目圖形位置
                - explanation_figure_position (str, optional): 詳解圖形位置
                
        Raises:
            ValueError: 如果配置參數無效
            GenerationError: 如果題目生成失敗
            
        Example:
            >>> generator = MyQuestionGenerator()
            >>> question = generator.generate_question()
            >>> assert 'question' in question
            >>> assert 'answer' in question
            >>> assert 'explanation' in question
        """
        self.logger.debug(f"開始生成題目，參數：{self.params}")
        
        try:
            # Phase 4: Pydantic 模型已在 __init__ 中完成驗證
            # 直接使用驗證後的參數
            num_a = random.randint(self.params.min_value, self.params.max_value)
            num_b = random.randint(self.params.min_value, self.params.max_value)
            
            # 使用統一幾何 API (示範用途)
            if self.params.difficulty == "HARD":
                # 高難度題目可能包含幾何元素
                triangle = construct_triangle("sss", side_a=3, side_b=4, side_c=5)
                centroid = get_centroid(triangle)
                
                # 創建圖形數據
                figure_data_question = {
                    'type': 'triangle_with_centroid',
                    'params': {
                        'triangle': {
                            'A': tikz_coordinate(triangle.A),
                            'B': tikz_coordinate(triangle.B), 
                            'C': tikz_coordinate(triangle.C)
                        },
                        'centroid': tikz_coordinate(centroid),
                        'variant': 'question'
                    },
                    'options': {'scale': 1.0}
                }
                
                figure_data_explanation = {
                    'type': 'triangle_with_centroid',
                    'params': {
                        'triangle': {
                            'A': tikz_coordinate(triangle.A),
                            'B': tikz_coordinate(triangle.B),
                            'C': tikz_coordinate(triangle.C)
                        },
                        'centroid': tikz_coordinate(centroid),
                        'variant': 'explanation',
                        'show_construction': True
                    },
                    'options': {'scale': 1.2}
                }
            else:
                figure_data_question = None
                figure_data_explanation = None
            
            # 構建題目內容
            answer = num_a + num_b
            
            question_text = f"計算：${num_a} + {num_b} = $ ？"
            answer_text = f"${answer}$"
            explanation_text = f"""**解題步驟：**

${num_a} + {num_b} = {answer}$

**答案**：{answer}"""
            
            result = {
                "question": question_text,
                "answer": answer_text,
                "explanation": explanation_text,
                "size": self.get_question_size(),
                "difficulty": self.params.difficulty
            }
            
            # 添加圖形數據 (如果有)
            if figure_data_question:
                result["figure_data_question"] = figure_data_question
                result["figure_position"] = "right"
                
            if figure_data_explanation:
                result["figure_data_explanation"] = figure_data_explanation
                result["explanation_figure_position"] = "right"
            
            self.logger.info(f"成功生成題目，難度：{self.params.difficulty}")
            return result
            
        except Exception as e:
            self.logger.error(f"題目生成失敗：{e}")
            raise
    
    def _get_question_size(self) -> str:
        """獲取題目大小
        
        根據題目的複雜度和內容量決定適當的大小。
        
        Returns:
            str: 題目大小 ('SMALL', 'MEDIUM', 'LARGE', 'EXTRA')
        """
        # 根據難度和是否有圖形決定大小
        if self.params.difficulty == 'HARD':
            return QuestionSize.MEDIUM
        return QuestionSize.SMALL
    
    def get_category(self) -> str:
        """獲取題目主類別
        
        為保持UI顯示的一致性，建議從以下標準分類中選擇：
        - "數與式" - 數與代數運算
        - "指數、對數" - 指數與對數函數  
        - "多項式函數" - 多項式相關題型
        - "直線與圓" - 解析幾何
        - "數列與級數" - 數列級數計算
        - "數據分析" - 統計與數據處理
        - "排列組合" - 排列組合計算
        - "機率" - 機率計算
        - "三角函數" - 三角函數圖形與性質
        - "平面向量" - 二維向量運算
        - "空間向量" - 三維向量運算
        - "空間中的平面與直線" - 立體幾何
        - "矩陣" - 矩陣運算
        - "極限" - 極限概念
        - "微分" - 微分計算
        - "積分" - 積分計算
        - "二次曲線" - 圓錐曲線
        - "複數" - 複數運算
        - "統計機率" - 進階統計
        
        當然，如有特殊需求也可使用其他分類名稱。
        
        Returns:
            str: 題目主類別名稱
        """
        return "數與式"
    
    def get_subcategory(self) -> str:
        """獲取題目子類別
        
        Returns:
            str: 題目子類別名稱
        """
        return "示範子類別"
    
    def get_supported_difficulties(self) -> List[str]:
        """獲取支援的難度級別
        
        Returns:
            List[str]: 支援的難度級別列表
        """
        return ["EASY", "MEDIUM", "HARD", "CHALLENGE"]
    
    def get_parameter_info(self) -> Dict[str, Any]:
        """獲取可配置參數資訊
        
        提供參數的詳細說明，用於 UI 生成和文檔。
        
        Returns:
            Dict[str, Any]: 參數資訊字典，包含類型、預設值、說明等
        """
        # Phase 4: 可以從 Pydantic 模型自動生成參數資訊
        return {
            "min_value": {
                "type": "int",
                "default": self.params.min_value,
                "min": 1,
                "max": 1000,
                "description": "數值範圍的最小值"
            },
            "max_value": {
                "type": "int",
                "default": self.params.max_value,
                "min": 2,
                "max": 10000,
                "description": "數值範圍的最大值"
            },
            "difficulty": {
                "type": "choice",
                "choices": ["EASY", "MEDIUM", "HARD", "CHALLENGE"],
                "default": self.params.difficulty,
                "description": "題目難度級別"
            },
            "include_decimals": {
                "type": "bool",
                "default": self.params.include_decimals,
                "description": "是否包含小數運算"
            }
        }

# Phase 4: 使用裝飾器自動註冊，無需手動調用
# @register_generator 裝飾器已自動註冊此生成器

logger.debug(f"已註冊生成器：{MyQuestionGenerator.__name__}")
```

### 3. Phase 4 統一註冊系統

Phase 4 使用統一的註冊系統，透過 `@register_generator` 裝飾器自動註冊：

```python
# generators/__init__.py - Phase 4 自動導入系統
"""
生成器模組統一入口 (Phase 4 版本)

自動導入所有生成器模組並觸發註冊系統。
使用新架構的統一註冊機制，支援熱重載和動態發現。

Phase 4 特色：
- 統一的 @register_generator 裝飾器
- 自動模組掃描和註冊
- 完整的錯誤處理和日誌記錄
"""

from utils import get_logger

logger = get_logger(__name__)

# Phase 4: 自動導入所有生成器模組
try:
    # 代數類生成器
    from .algebra import *
    
    # 三角函數類生成器  
    from .trigonometry import *
    
    # 你的新生成器模組
    from .my_new_generator import MyQuestionGenerator
    
    logger.info("所有生成器模組載入完成")
    
except ImportError as e:
    logger.warning(f"部分生成器載入失敗：{e}")

# Phase 4: 驗證註冊狀態
logger.info("generators 模組初始化完成")
```

### 4. 添加單元測試

為新生成器編寫完整的單元測試：

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
測試我的新題型生成器

使用 pytest 框架進行完整的單元測試，含盶各種邊界情況和錯誤處理。
"""

import pytest
from typing import Dict, Any

from generators.my_new_generator import MyQuestionGenerator, QuestionParams
from pydantic import ValidationError


class TestMyQuestionGenerator:
    """我的題型生成器測試類別
    
    測試生成器的所有功能，包括基本生成、錯誤處理和邊界情況。
    """
    
    def setup_method(self):
        """每個測試方法執行前的設置"""
        self.generator = MyQuestionGenerator()
        self.test_options = {
            'min_value': 1,
            'max_value': 10,
            'difficulty': 'MEDIUM'
        }
    
    def test_basic_generation(self):
        """測試基本題目生成"""
        question = self.generator.generate_question()
        
        # 檢查必要的鍵
        required_keys = ['question', 'answer', 'explanation', 'size', 'difficulty']
        for key in required_keys:
            assert key in question, f"缺少必要的鍵: {key}"
        
        # 檢查內容類型
        assert isinstance(question['question'], str)
        assert isinstance(question['answer'], str) 
        assert isinstance(question['explanation'], str)
        assert question['size'] in ['SMALL', 'MEDIUM', 'LARGE', 'EXTRA']
        assert question['difficulty'] in ['EASY', 'MEDIUM', 'HARD', 'CHALLENGE']
    
    def test_with_options(self):
        """測試帶配置選項的生成"""
        generator = MyQuestionGenerator(self.test_options)
        question = generator.generate_question()
        
        assert question['difficulty'] == 'MEDIUM'
        # 檢查是否遵循數值範圍 (這裡可能需要解析題目內容)
    
    def test_different_difficulties(self):
        """測試不同難度級別"""
        difficulties = ['EASY', 'MEDIUM', 'HARD', 'CHALLENGE']
        
        for difficulty in difficulties:
            generator = MyQuestionGenerator({'difficulty': difficulty})
            question = generator.generate_question()
            assert question['difficulty'] == difficulty
    
    def test_parameter_validation(self):
        """測試 Phase 4 Pydantic 參數驗證"""
        # 測試無效參數組合
        with pytest.raises(ValidationError):
            QuestionParams(min_value=10, max_value=5)  # max < min
        
        with pytest.raises(ValidationError):
            QuestionParams(min_value=0, max_value=10)  # min <= 0
            
        with pytest.raises(ValidationError):
            QuestionParams(difficulty="INVALID")  # 無效難度
        
        # 測試有效參數
        valid_params = QuestionParams(min_value=1, max_value=100, difficulty="MEDIUM")
        assert valid_params.min_value == 1
        assert valid_params.max_value == 100
        assert valid_params.difficulty == "MEDIUM"
    
    def test_registration(self):
        """測試 Phase 4 生成器註冊"""
        # Phase 4: 透過導入模組測試註冊
        import generators
        # 生成器應該已通過 @register_generator 裝飾器自動註冊
        # 具體的註冊驗證可以透過實際運行來確認
    
    def test_metadata_methods(self):
        """測試元數據方法"""
        assert isinstance(self.generator.get_category(), str)
        assert isinstance(self.generator.get_subcategory(), str)
        assert isinstance(self.generator.get_supported_difficulties(), list)
        assert isinstance(self.generator.get_parameter_info(), dict)
    
    def test_figure_generation_hard_mode(self):
        """測試高難度模式的圖形生成"""
        generator = MyQuestionGenerator({'difficulty': 'HARD'})
        question = generator.generate_question()
        
        # 高難度應該包含圖形
        if 'figure_data_question' in question:
            assert isinstance(question['figure_data_question'], dict)
            assert 'type' in question['figure_data_question']
            assert 'params' in question['figure_data_question']
    
    def test_multiple_generations(self):
        """測試多次生成的一致性"""
        questions = []
        for _ in range(10):
            question = self.generator.generate_question()
            questions.append(question)
        
        # 檢查所有題目都有必要的結構
        for question in questions:
            assert 'question' in question
            assert 'answer' in question
            assert 'explanation' in question
    
    def test_error_handling(self):
        """測試錯誤處理"""
        # 測試極端參數
        try:
            generator = MyQuestionGenerator({
                'min_value': 999999,
                'max_value': 1000000
            })
            question = generator.generate_question()
            # 應該能正常處理大數值
            assert 'question' in question
        except Exception as e:
            pytest.fail(f"無法處理大數值參數: {e}")


if __name__ == "__main__":
    pytest.main([__file__])
```

### 5. 新架構最佳實踐

#### ✅ 必須遵循的標準

1. **Sphinx Docstring 標準**
   - 所有類別、方法必須包含完整 docstring
   - 使用 Google Style 格式 (`Args:`, `Returns:`, `Raises:`)
   - 包含使用範例和重要說明

2. **統一 API 优先**
   - 使用 `from utils import ...` 導入功能
   - 優先使用統一的數據類型 (`Point`, `Triangle` 等)
   - 整合新的幾何計算 API

3. **自動註冊**
   - 使用 `registry.register_generator()` 自動註冊
   - 遵循模組化載入模式
   - 支援動態發現和管理

4. **配置和日誌**
   - 使用 `global_config` 獲取全域設定
   - 使用 `get_logger(__name__)` 獲取模組日誌器
   - 記錄重要操作和錯誤資訊

5. **強健的錯誤處理**
   - 全面的參數驗證 (`dataclass` 或自定義驗證)
   - 提供清晰的錯誤訊息
   - 正確的異常類型和傳遞

#### 📋 題目內容標準

- **question**: LaTeX 格式的題目文字
- **answer**: 簡潔的正確答案
- **explanation**: 詳細的解題步驟
- **size**: 題目大小 ('SMALL', 'MEDIUM', 'LARGE', 'EXTRA')
- **difficulty**: 難度級別 ('EASY', 'MEDIUM', 'HARD', 'CHALLENGE')

#### 🎨 圖形支援

- **figure_data_question**: 題目圖形數據
- **figure_data_explanation**: 詳解圖形數據
- **figure_position**: 題目圖形位置 ('right', 'left', 'bottom', 'none')
- **explanation_figure_position**: 詳解圖形位置 ('right', 'bottom')

#### ⚙️ 效能考量

- 使用適當的數學後端 (numpy/sympy/python)
- 避免重複計算，快取結果
- 記錄效能指標和生成時間

## 🚀 快速開始檢查清單

創建新生成器時，確保完成以下項目：

- [ ] **完整 Sphinx Docstring** - 所有類別和方法
- [ ] **統一 API 導入** - 使用 `from utils import ...`
- [ ] **參數驗證** - 使用 dataclass 或自定義驗證
- [ ] **配置和日誌** - 整合 `global_config` 和 `get_logger`
- [ ] **自動註冊** - 使用 `registry.register_generator()`
- [ ] **元數據方法** - 實現 `get_category()`, `get_subcategory()` 等
- [ ] **單元測試** - pytest 測試文件，涵蓋各種情況
- [ ] **範例代碼** - docstring 中的使用範例
- [ ] **錯誤處理** - 適當的異常類型和訊息
- [ ] **圖形支援** - 如需要，添加圖形數據

完成開發後的驗證步驟：

```bash
# Phase 4 驗證命令

# 1. 測試生成器功能
py -m pytest tests/test_generators/ -v

# 2. 檢查生成器註冊和初始化
py -c "import generators; print('✅ 生成器模組初始化成功')"

# 3. 測試題目生成
py -c "from generators.my_generator import MyQuestionGenerator; g = MyQuestionGenerator(); print(g.generate_question())"

# 4. 檢查 Pydantic 參數驗證
py -c "from generators.my_generator import QuestionParams; p = QuestionParams(min_value=1, max_value=10); print('✅ Pydantic 驗證正常')"

# 5. 檢查新架構工具整合
py -c "from utils import get_logger, global_config; print('✅ 新架構工具正常')"
```

## 🔍 Phase 4 統一註冊系統

Phase 4 採用統一的自動註冊系統，透過裝飾器簡化生成器管理。

### Phase 4 註冊機制

```python
# Phase 4 統一註冊方式
from ..base import QuestionGenerator, register_generator

@register_generator  # Phase 4 統一裝飾器
class MyQuestionGenerator(QuestionGenerator):
    """繼承 QuestionGenerator 並使用裝飾器自動註冊"""
    pass

# 自動註冊完成，無需手動調用任何函數
```

### Phase 4 註冊系統特色

```python
# Phase 4: 模組導入即觸發註冊
import generators  # 所有生成器自動註冊

# Phase 4: 驗證註冊狀態
# 透過實際運行檢查生成器是否成功註冊：
from generators.trigonometry import TrigonometricFunctionGenerator
generator = TrigonometricFunctionGenerator()
question = generator.generate_question()
print("✅ 生成器註冊和運行正常")

# Phase 4: 支援的操作
# - 自動模組掃描
# - 統一裝飾器註冊
# - 完整錯誤處理和日誌記錄
# - 熱重載支援
```

### Phase 4 最佳實踐

1. **統一裝飾器**：只使用 `@register_generator`
2. **繼承基類**：所有生成器繼承 `QuestionGenerator`
3. **模組化組織**：按數學領域組織生成器
4. **自動初始化**：透過 `import generators` 觸發註冊

## ⚙️ 新架構配置管理

新架構提供統一的配置管理系統，支援全域和局部配置。

### 全域配置

```python
from utils.core.config import global_config

class MyQuestionGenerator:
    def __init__(self, options=None):
        self.options = options or {}
        
        # 獲取全域配置
        self.precision = global_config.get('geometry.precision', 6)
        self.backend = global_config.get('geometry.backend', 'python')
        self.debug_mode = global_config.get('debug', False)
        
        # 結合局部選項
        self.difficulty = self.options.get('difficulty', 'MEDIUM')
        self.custom_range = self.options.get('range', (1, 100))
```

### 可配置選項系統

```python
def get_parameter_info(self) -> Dict[str, Any]:
    """提供結構化的參數資訊供 UI 使用"""
    return {
        "difficulty": {
            "type": "choice",
            "choices": ["EASY", "MEDIUM", "HARD"],
            "default": "MEDIUM",
            "description": "題目難度級別"
        },
        "number_range": {
            "type": "range", 
            "min": 1,
            "max": 1000,
            "default": [1, 100],
            "description": "數字範圍設定"
        },
        "include_fractions": {
            "type": "boolean",
            "default": False,
            "description": "是否包含分數運算"
        }
    }
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

## 🔗 在 PDF 生成流程中使用

新架構下的生成器會自動整合到 PDF 生成流程中：

### PDF 協調器整合

```python
# 在 utils/orchestration/pdf_orchestrator.py 中
from utils.core.registry import registry

def _generate_raw_questions(selected_data):
    """生成原始題目列表"""
    questions = []
    
    for item in selected_data:
        category = item['category']
        subcategory = item['subcategory']
        count = item['count']
        options = item.get('options', {})
        
        # 使用註冊系統獲取生成器
        generator_class = registry.get_generator_by_category_and_subcategory(
            category, subcategory
        )
        
        if generator_class:
            generator = generator_class(options)
            
            for _ in range(count):
                try:
                    question = generator.generate_question()
                    questions.append(question)
                except Exception as e:
                    logger.error(f"生成題目失敗: {e}")
                    continue
    
    return questions
```

### UI 整合

```python
# 在 ui/main_window.py 中
from utils.core.registry import registry

def populate_generator_categories(self):
    """填充生成器類別到 UI"""
    categories = registry.get_all_categories()
    
    for category in categories:
        subcategories = registry.get_subcategories(category)
        
        for subcategory in subcategories:
            generators = registry.get_generators_by_category_and_subcategory(
                category, subcategory
            )
            
            # 獲取參數資訊用於 UI 生成
            if generators:
                generator = generators[0]()  # 取第一個生成器作為代表
                param_info = generator.get_parameter_info()
                # 產生 UI 控件...
```

## 📚 參考資源和範例

### 新架構範例文件
- 生成器範例：`generators/trigonometry/trigonometric_function.py`
- 註冊系統：`utils/core/registry.py`
- 配置管理：`utils/core/config.py`
- 日誌系統：`utils/core/logging.py`
- 統一 API：`utils/__init__.py`

### 測試範例
- 生成器測試：`tests/test_generators/`
- 整合測試：`tests/test_integration/`
- 註冊系統測試：`tests/test_utils/test_core/test_registry.py`

### 文檔資源
- API 文檔：`docs/build/html/` (經 `make html` 生成)
- 架構指南：`docs/source/guides/architecture.rst` 
- 工作流程：`docs/workflow.md`
- 圖形開發：`docs/figure_development_guide.md`

## 🎨 新架構圖形支援

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

完整的新架構示例可參考現有的生成器檔案。

---

## ✨ 新架構優勢

與舊版單一檔案架構相比，新架構提供：

- ✅ **完整 API 文檔** - Sphinx 自動生成專業文檔
- ✅ **統一數學 API** - 一致的幾何計算和渲柔接口
- ✅ **智能註冊系統** - 自動發現和管理生成器
- ✅ **強健錯誤處理** - 全面的異常管理和記錄
- ✅ **效能優化** - 多後端支援和智能快取
- ✅ **模組化設計** - 清晰的職責分離和可維護性
- ✅ **完整測試** - 全面的單元和整合測試覆蓋

## 📋 **長期維護計劃**

### **🔄 定期更新任務**

1. **文檔與代碼同步檢查** (每季度)
   - 檢查範例代碼是否與實際 API 一致
   - 更新最佳實踐指南
   - 驗證所有測試命令可正常執行

2. **實用性改善** (持續進行)
   - 收集開發者反饋，改善範例代碼實用性
   - 新增常見錯誤的除錯指南
   - 擴充 Phase 4 實際案例

3. **新功能整合** (隨新功能發布)
   - 當有新的架構改進時，及時更新指南
   - 整合新的 Pydantic 特性和最佳實踐
   - 更新測試和驗證流程

### **🎯 改善優先順序**

**高優先級**：
- 保持註冊系統範例的準確性
- 確保 Pydantic 參數驗證範例可運行
- 維護新架構工具導入的正確性

**中優先級**：
- 擴展實際可運行的小範例
- 改善測試指導的完整性
- 新增效能優化建議

**低優先級**：
- 美化文檔排版和格式
- 新增更多進階使用場景
- 建立視覺化的架構圖表

### **📞 維護聯絡**

當發現文檔問題時：
1. 優先檢查是否為代碼變更導致
2. 參考最新的 Phase 4 實際生成器代碼
3. 確保修正後的範例可以實際運行
4. 保持文檔的實用性和準確性
