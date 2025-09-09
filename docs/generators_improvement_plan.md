# Generators 模組改進計畫

> **文檔狀態**: 未來改善計畫 📋 (Phase 4 已完成，此為進一步改善建議)  
> **建立日期**: 2025-09-06  
> **參考基礎**: Day 2 params_models 重構完成後的架構分析  
> **優先級**: 長期改善目標 (Phase 4 重建已完成，此為進階優化)  
> **備註**: Phase 4已完成generators完全重建，此計畫可作為未來進階改善參考

## 📊 **現況分析**

### **檢查範圍**
經深度分析以下生成器文件：
- `generators/base.py` - 基礎架構 (237 行)
- `generators/algebra/double_radical_simplification.py` - 代數生成器 (161 行)
- `generators/trigonometry/TrigonometricFunctionGenerator.py` - 三角函數生成器 (241 行)
- `generators/trigonometry/TrigAngleConversionGenerator.py` - 角度變換生成器 (445 行)

### **架構優點** ✅
1. **統一的基礎架構**
   - `QuestionGenerator` 抽象基類設計良好
   - `@register_generator` 自動註冊機制運作正常
   - `QuestionSize` 枚舉提供標準版面規格
   - 標準化方法介面：`generate_question()`, `get_category()`, `get_subcategory()`

2. **豐富的工具方法**
   - `random_int()`, `random_float()` 提供排除功能
   - `format_latex()`, `format_question()` 格式化工具
   - `get_param_range()` 參數範圍管理
   - `generate_batch()` 批量生成支援

## 🔍 **發現的問題**

### **1. 圖形整合不一致** ⚠️
**問題描述**: 
- 部分生成器 (如 `TrigonometricFunctionGenerator`) 使用新圖形架構
- 部分生成器缺乏圖形支援或使用不一致的格式
- 與新完成的 `figures.params` 架構整合程度不一

**現況示例**:
```python
# TrigonometricFunctionGenerator.py 中：
figure_data_question = {
    'type': 'standard_unit_circle',  # ✅ 使用新架構
    'params': {'variant': 'question', 'angle': angle, ...}
}

# 但 TrigAngleConversionGenerator 中：
"figure_data_question": None,  # ❌ 缺乏圖形支援
```

### **2. 複雜度管理需要改善** 📋
**問題描述**:
- `TrigAngleConversionGenerator.py` 高達 445 行，單一文件過於複雜
- `_generate_narrow_angle_explanation()` 方法超過 90 行
- 複雜的解釋生成邏輯混雜在主要生成邏輯中

**複雜度熱點**:
```python
# TrigAngleConversionGenerator.py
class EnhancedTrigAngleConversionGenerator:
    def _generate_narrow_angle_explanation(self, ...):  # 90+ 行
        # 複雜的模板系統和象限轉換邏輯
        quadrant_templates = { ... }  # 大型字典
        # 複雜的條件分支處理
```

### **3. 配置標準化缺失** 🔧
**問題描述**:
- 各生成器的 `options` 處理方式不統一
- 缺乏配置驗證和類型安全
- 沒有標準化的配置文檔

**不一致示例**:
```python
# DoubleRadicalSimplificationGenerator
max_value = self.options.get('max_value', 25)

# TrigonometricFunctionGenerator  
self.difficulty = self.options.get("difficulty", "MEDIUM")
self.functions = self.options.get("functions") # 可能為 None
```

### **4. 測試覆蓋不足** 🧪
**問題描述**:
- 缺乏系統性的單元測試
- 沒有圖形整合測試
- 批量生成穩定性未經充分驗證

## 🚀 **改進建議**

### **階段 1: 配置系統標準化** (高優先級)

#### **1.1 建立標準配置架構**
建議創建 `generators/config/` 模組：

```python
# generators/config/base.py
from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class GeneratorConfig(BaseModel):
    """生成器標準配置基類
    
    所有生成器配置都應繼承此類，確保基本配置的一致性。
    """
    difficulty: Literal['EASY', 'MEDIUM', 'HARD'] = Field(
        default='MEDIUM',
        description="題目難度等級"
    )
    batch_size: int = Field(default=10, gt=0, description="批量生成數量")
    max_attempts: int = Field(default=100, gt=0, description="最大嘗試次數")
    enable_figure: bool = Field(default=True, description="是否啟用圖形")
    
    class Config:
        """Pydantic 配置"""
        extra = 'forbid'  # 禁止額外欄位
        use_enum_values = True

# generators/config/trigonometry.py  
class TrigConfig(GeneratorConfig):
    """三角函數生成器專用配置"""
    functions: List[Literal['sin', 'cos', 'tan', 'cot', 'sec', 'csc']] = Field(
        default=['sin', 'cos', 'tan'],
        description="可用的三角函數"
    )
    angles: List[int] = Field(
        default=[0, 30, 45, 60, 90, 120, 135, 150, 180],
        description="可用的角度列表"
    )
    show_unit_circle: bool = Field(default=True, description="是否顯示單位圓")
    angle_unit: Literal['degree', 'radian'] = Field(
        default='degree',
        description="角度單位"
    )

# generators/config/algebra.py
class AlgebraConfig(GeneratorConfig):
    """代數生成器專用配置"""
    max_value: int = Field(default=25, gt=0, description="最大數值")
    allow_negative: bool = Field(default=True, description="是否允許負數")
    complexity_level: Literal[1, 2, 3, 4, 5] = Field(
        default=3,
        description="複雜度等級 (1=最簡單, 5=最複雜)"
    )
```

#### **1.2 更新基礎生成器類**
```python
# generators/base.py 修改建議
from typing import TypeVar, Generic
from .config.base import GeneratorConfig

ConfigType = TypeVar('ConfigType', bound=GeneratorConfig)

class QuestionGenerator(ABC, Generic[ConfigType]):
    """題目生成器基礎類別 (泛型版本)"""
    
    def __init__(self, config: Optional[ConfigType] = None):
        """初始化生成器
        
        Args:
            config: 類型安全的配置物件
        """
        self.config = config or self.get_default_config()
        
    @abstractmethod
    def get_default_config(self) -> ConfigType:
        """獲取預設配置"""
        pass
        
    def validate_config(self) -> None:
        """驗證配置合法性"""
        # Pydantic 自動驗證
        pass
```

### **階段 2: 圖形整合統一化** (高優先級)

#### **2.1 標準圖形介面**
```python
# generators/mixins/figure_mixin.py
from typing import Dict, Any, Optional
from figures.params import *

class FigureMixin:
    """圖形支援混入類別"""
    
    def create_figure(self, 
                     figure_type: str, 
                     variant: Literal['question', 'explanation'],
                     **params) -> Dict[str, Any]:
        """統一的圖形創建方法
        
        Args:
            figure_type: 圖形類型 ('unit_circle', 'triangle', 'coordinate_system')
            variant: 圖形變體
            **params: 圖形特定參數
            
        Returns:
            標準化的圖形數據字典
        """
        return {
            'type': figure_type,
            'params': {
                'variant': variant,
                **params
            },
            'options': {
                'scale': 1.0
            }
        }
    
    def create_unit_circle_figure(self, 
                                 angle: float, 
                                 variant: str = 'question') -> Dict[str, Any]:
        """創建單位圓圖形的便利方法"""
        return self.create_figure(
            'standard_unit_circle',
            variant,
            angle=angle,
            show_coordinates=True,
            show_angle=True,
            show_point=True,
            show_radius=True
        )
    
    def create_triangle_figure(self, 
                              points: List[List[float]], 
                              variant: str = 'question') -> Dict[str, Any]:
        """創建三角形圖形的便利方法"""
        return self.create_figure(
            'triangle',
            variant,
            points=points,
            show_labels=True,
            label_names=['A', 'B', 'C']
        )
```

#### **2.2 更新現有生成器**
```python
# 使用示例：更新後的三角函數生成器
class TrigonometricFunctionGenerator(QuestionGenerator[TrigConfig], FigureMixin):
    """三角函數值計算題生成器 (更新版)"""
    
    def generate_question(self) -> Dict[str, Any]:
        # ... 原有邏輯 ...
        
        # 使用統一的圖形創建方法
        figure_question = self.create_unit_circle_figure(
            angle=angle,
            variant='question'
        ) if self.config.enable_figure else None
        
        figure_explanation = self.create_unit_circle_figure(
            angle=angle, 
            variant='explanation'
        ) if self.config.enable_figure else None
        
        return {
            "question": question_text,
            "answer": answer,
            "explanation": explanation,
            "size": self.get_question_size(),
            "difficulty": self.config.difficulty,
            "figure_data_question": figure_question,
            "figure_data_explanation": figure_explanation
        }
```

### **階段 3: 複雜度管理與模組化** (中優先級)

#### **3.1 解釋生成器系統**
```python
# generators/explanations/
class ExplanationBuilder(ABC):
    """解釋生成器基類"""
    
    @abstractmethod
    def build_explanation(self, context: Dict[str, Any]) -> str:
        """構建解釋文字"""
        pass

class TrigExplanationBuilder(ExplanationBuilder):
    """三角函數解釋生成器"""
    
    def build_angle_conversion_explanation(self, 
                                         func: str, 
                                         original_angle: int,
                                         target_angle: int,
                                         sign: int) -> str:
        """構建角度轉換解釋"""
        # 從 TrigAngleConversionGenerator 提取的邏輯
        pass
    
    def build_function_value_explanation(self, 
                                       func: str, 
                                       angle: int, 
                                       coordinates: Tuple[float, float]) -> str:
        """構建函數值計算解釋"""
        pass

class AlgebraExplanationBuilder(ExplanationBuilder):
    """代數解釋生成器"""
    
    def build_radical_simplification_explanation(self, 
                                                expression: str, 
                                                steps: List[str]) -> str:
        """構建根式化簡解釋"""
        pass
```

#### **3.2 大型生成器分解**
```python
# generators/trigonometry/angle_conversion/
class AngleConversionCore:
    """角度轉換核心邏輯"""
    
    def convert_to_first_quadrant(self, func: str, angle: int) -> Tuple[int, int]:
        """轉換為第一象限角"""
        pass
    
    def convert_to_narrow_angle(self, func: str, angle: int, sign: int) -> Tuple[int, int, str]:
        """轉換為0~45度角"""  
        pass

class AngleConversionQuestionTypes:
    """角度轉換題型管理"""
    
    def generate_formula_question(self) -> Dict[str, Any]:
        """生成公式問答題"""
        pass
    
    def generate_quadrant_question(self) -> Dict[str, Any]:  
        """生成象限轉換題"""
        pass
    
    def generate_narrow_angle_question(self) -> Dict[str, Any]:
        """生成窄角轉換題"""
        pass

# 主生成器變得簡潔
class TrigAngleConversionGenerator(QuestionGenerator[TrigConfig]):
    """三角函數角度轉換生成器 (重構版)"""
    
    def __init__(self, config: Optional[TrigConfig] = None):
        super().__init__(config)
        self.core = AngleConversionCore()
        self.question_types = AngleConversionQuestionTypes()
        self.explanation_builder = TrigExplanationBuilder()
    
    def generate_question(self) -> Dict[str, Any]:
        """生成問題 - 簡潔的協調邏輯"""
        question_type = self._select_question_type()
        return getattr(self.question_types, f"generate_{question_type}_question")()
```

### **階段 4: 測試與驗證系統** (中優先級)

#### **4.1 單元測試框架**
```python
# tests/generators/
class GeneratorTestBase:
    """生成器測試基類"""
    
    def test_basic_generation(self):
        """測試基本生成功能"""
        pass
    
    def test_batch_generation(self):
        """測試批量生成穩定性"""
        pass
    
    def test_config_validation(self):
        """測試配置驗證"""
        pass
    
    def test_figure_integration(self):
        """測試圖形整合"""
        pass

# tests/generators/test_trigonometry.py
class TestTrigGenerators(GeneratorTestBase):
    """三角函數生成器測試"""
    
    def test_function_value_generator(self):
        """測試函數值計算生成器"""
        generator = TrigonometricFunctionGenerator()
        
        for _ in range(100):  # 批量測試
            question = generator.generate_question()
            
            # 驗證基本結構
            assert 'question' in question
            assert 'answer' in question
            assert 'explanation' in question
            
            # 驗證圖形數據格式
            if question.get('figure_data_question'):
                self._validate_figure_format(question['figure_data_question'])
    
    def _validate_figure_format(self, figure_data: Dict[str, Any]):
        """驗證圖形數據格式"""
        assert 'type' in figure_data
        assert 'params' in figure_data
        assert 'variant' in figure_data['params']
```

### **階段 5: 文檔與範例完善** (低優先級)

#### **5.1 Sphinx 文檔標準化**
```python
# 為所有生成器添加完整的 docstring
class TrigonometricFunctionGenerator(QuestionGenerator[TrigConfig]):
    """三角函數值計算題生成器
    
    此生成器專門生成計算特定角度下三角函數值的題目，
    支援六種基本三角函數並提供視覺化的單位圓圖形輔助。
    
    主要功能：
    - 隨機選擇角度和三角函數
    - 自動計算精確的函數值  
    - 生成詳細的解題步驟
    - 整合單位圓視覺化圖形
    
    支援的三角函數：
    - sin, cos, tan (基本函數)
    - cot, sec, csc (互逆函數)
    
    支援的角度：
    - 標準角度: 0°, 30°, 45°, 60°, 90°, 120°, 135°, 150°, 180°...
    - 可通過配置自定義角度範圍
    
    Example:
        基本使用::
        
            from generators.trigonometry import TrigonometricFunctionGenerator
            from generators.config import TrigConfig
            
            config = TrigConfig(
                functions=['sin', 'cos', 'tan'],
                angles=[0, 30, 45, 60, 90],
                difficulty='MEDIUM'
            )
            
            generator = TrigonometricFunctionGenerator(config)
            question = generator.generate_question()
            
        批量生成::
        
            questions = generator.generate_batch(10)
    
    Note:
        - 所有角度使用度數制
        - 函數值使用 SymPy 精確計算
        - 圖形使用新的 figures.params 架構
        - 支援 question/explanation 雙變體模式
    """
```

#### **5.2 使用範例與教學文檔**
建立 `docs/generators/examples/` 包含：
- 各類生成器的使用範例
- 配置選項詳細說明  
- 圖形整合最佳實踐
- 自定義生成器開發指南

## 📈 **實施計畫**

### **時程安排**
- **階段 1**: 配置系統 (1-2 週) - 建立標準配置架構
- **階段 2**: 圖形整合 (1-2 週) - 統一圖形介面並更新現有生成器  
- **階段 3**: 複雜度管理 (2-3 週) - 大型生成器重構與解釋系統建立
- **階段 4**: 測試系統 (1 週) - 測試框架建立與現有生成器測試
- **階段 5**: 文檔完善 (1 週) - Sphinx 文檔與使用範例

### **相依性**
- ✅ **params_models 重構完成** - 已完成，可利用新架構
- ✅ **figures.params 系統穩定** - 已完成，可進行整合
- ⏳ **params 重構階段 3-4 完成** - Day 3-4 完成後再開始此計畫

### **風險評估**
- **低風險**: 配置系統和文檔改善 (向後兼容)
- **中風險**: 圖形整合 (需要仔細測試)
- **高風險**: 大型生成器重構 (可能影響現有功能)

## 🎯 **預期成果**

### **短期效益** (階段 1-2 完成後)
- 配置管理標準化和類型安全
- 圖形整合一致性提升
- 新生成器開發效率提升

### **中期效益** (階段 3-4 完成後)  
- 程式碼複雜度顯著降低
- 測試覆蓋率大幅提升
- 系統穩定性和可維護性改善

### **長期效益** (全部階段完成後)
- 生成器系統現代化達到與 figures.params 相同水準
- 開發新功能和生成器類型的門檻降低  
- 整體程式碼品質和開發體驗顯著提升

---

**備註**: 此計畫為未來改善建議，優先級位於 params_models 重構（Day 3-4）之後。實施時應根據具體情況調整時程和範圍。