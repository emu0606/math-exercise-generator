# TrigonometricFunctionGenerator 圖形修復重構計畫

> **創建日期**: 2025-09-28
> **狀態**: 📋 研擬中 → 等待執行命令
> **目標**: 修復圖形數據問題，統一新架構，提升代碼品質

## 🎯 **問題分析**

### **核心問題**
TrigonometricFunctionGenerator 的圖形數據被錯誤覆蓋為 `None`：

```python
# Line 452-453: 直接設置圖形數據
"figure_data_question": self._build_figure_data(angle_deg, func.__name__),
"figure_data_explanation": self._build_explanation_figure(angle_deg, func.__name__),

# Line 456: 基類metadata覆蓋上述設置
**self._get_standard_metadata()  # 這裡的圖形方法返回None，覆蓋了上面的設置
```

### **測試確認**
```bash
py -c "測試結果: figure_data_question: None, figure_data_explanation: None"
```

## 🔧 **解決方案設計**

### **架構修復原則**
1. **符合新基類架構**: 使用統一的 `_get_standard_metadata()` 系統
2. **方法override**: 實現 `get_figure_data_question()` 和 `get_figure_data_explanation()`
3. **狀態管理**: 保存當前生成參數供圖形方法使用
4. **向後兼容**: 保持所有現有功能正常

### **修改策略**
- **低風險優先**: 先新增方法，再修改現有邏輯
- **分階段執行**: 每步驗證後再進行下一步
- **完整文檔**: 所有修改都有完整Sphinx註解

## 📋 **詳細執行計畫**

### **Phase 1: 新增基類方法override (高優先級)**

#### **新增方法 1: get_figure_data_question()**
```python
def get_figure_data_question(self) -> Optional[Dict[str, Any]]:
    """獲取題目圖形數據

    根據當前生成的角度和函數參數建構單位圓圖形配置。
    圖形包含角度標記、函數高亮和基礎視覺元素。

    Returns:
        Optional[Dict[str, Any]]: 圖形配置字典，包含以下鍵值：
            type (str): 圖形類型 'standard_unit_circle'
            params (Dict): 圖形參數，包含角度、顯示選項等
            options (Dict): 渲染選項，如縮放比例

        如果當前無生成參數則返回None確保系統穩定性。

    Note:
        依賴 generate_question() 過程中設置的 _current_angle 和 _current_func。
        圖形系統直接接受度數參數，無需角度轉換。

    Example:
        >>> gen = TrigonometricFunctionGenerator()
        >>> gen._current_angle = 30
        >>> gen._current_func = 'sin'
        >>> figure_data = gen.get_figure_data_question()
        >>> figure_data['params']['angle']
        30
    """
    if hasattr(self, '_current_angle') and hasattr(self, '_current_func'):
        return self._build_figure_data(self._current_angle, self._current_func)
    return None
```

#### **新增方法 2: get_figure_data_explanation()**
```python
def get_figure_data_explanation(self) -> Optional[Dict[str, Any]]:
    """獲取解釋圖形數據

    返回詳解專用的單位圓圖形，含更豐富的視覺元素。
    比題目圖形增加座標顯示、點標記、半徑線等。

    Returns:
        Optional[Dict[str, Any]]: 詳解圖形配置字典，包含：
            type (str): 'standard_unit_circle'
            params (Dict): 詳解模式參數，variant='explanation'
            options (Dict): 渲染選項，scale=1.2

    Note:
        依賴當前生成狀態，若無則返回None。
        詳解圖形比題目圖形提供更多視覺資訊。
    """
    if hasattr(self, '_current_angle') and hasattr(self, '_current_func'):
        return self._build_explanation_figure(self._current_angle, self._current_func)
    return None
```

**執行位置**: 在 `get_grade()` 方法後插入

### **Phase 2: 修改 _generate_core_logic() (高優先級)**

#### **修改點 1: 新增狀態保存**
```python
# 在方法開始處新增
def _generate_core_logic(self, angle_deg: int, func: Any, value: Union[Any, str]) -> Dict[str, Any]:
    """建構完整的題目回應數據

    設置當前生成參數並建構題目，圖形數據由基類統一處理。

    設計變更:
        - 移除直接圖形設置，避免與基類metadata衝突
        - 新增狀態保存機制，供圖形方法使用
        - 簡化返回邏輯，依賴基類統一處理

    Args:
        angle_deg (int): 角度值（度數）
        func (Any): sympy三角函數物件
        value (Union[Any, str]): 計算結果或"ERROR"

    Returns:
        Dict[str, Any]: 題目數據字典，圖形由基類metadata處理
    """
    # 設置當前參數供圖形方法使用
    self._current_angle = angle_deg
    self._current_func = func.__name__

    # ... 其他邏輯保持不變 ...
```

#### **修改點 2: 移除直接圖形設置**
```python
# 移除 Line 452-455
# 原代碼:
"figure_data_question": self._build_figure_data(angle_deg, func.__name__),
"figure_data_explanation": self._build_explanation_figure(angle_deg, func.__name__),
"figure_position": "right",
"explanation_figure_position": "right",

# 改為: (這些由基類_get_standard_metadata()統一處理)
# 移除，不再直接設置
```

#### **修改點 3: 簡化return語句**
```python
# 簡化返回邏輯
return {
    "question": question,
    "answer": answer,
    "explanation": self._generate_explanation(func.__name__, angle_deg, value, display_as_radian),
    **self._get_standard_metadata()  # 統一metadata處理，包含圖形數據
}
```

### **Phase 3: 文檔標準化 (中優先級)**

#### **類級別註解改寫**
```python
class TrigonometricFunctionGenerator(QuestionGenerator):
    """三角函數值計算題目生成器

    生成特殊角度的三角函數計算題目，支援度數/弧度/混合模式。
    使用預計算查詢表提升性能，sympy確保數學精確性。

    Attributes:
        functions (List[Any]): 根據配置選擇的三角函數列表
        angles_degrees (List[int]): 預定義特殊角度列表
        angle_mode (str): 角度顯示模式 'degree'/'radian'/'mixed'
        trig_values (Dict): 預建構的函數值查詢表

    Example:
        >>> # 基本使用
        >>> gen = TrigonometricFunctionGenerator()
        >>> question = gen.generate_question()
        >>> print(question['question'])
        $\\sin(30^\\circ) = $

        >>> # 弧度模式
        >>> gen = TrigonometricFunctionGenerator({'angle_mode': 'radian'})
        >>> question = gen.generate_question()
        >>> print(question['question'])
        $\\cos(\\frac{\\pi}{6}) = $
    """
```

#### **關鍵方法補充完整docstring**
重點方法需要補充：
- `_build_unified_trig_table()`: 添加Performance和Algorithm說明
- `get_config_schema()`: 添加Config Options詳細說明
- `generate_question()`: 補充完整流程說明

### **Phase 4: 驗證測試 (必須)**

#### **測試 1: 圖形數據修復驗證**
```bash
py -c "
from generators.trigonometry.TrigonometricFunctionGenerator import TrigonometricFunctionGenerator
gen = TrigonometricFunctionGenerator()
q = gen.generate_question()
print(f'題目圖形: {q.get(\"figure_data_question\") is not None}')
print(f'詳解圖形: {q.get(\"figure_data_explanation\") is not None}')
print(f'題目圖形類型: {q.get(\"figure_data_question\", {}).get(\"type\", \"None\")}')
"
```
**預期結果**:
```
題目圖形: True
詳解圖形: True
題目圖形類型: standard_unit_circle
```

#### **測試 2: 功能完整性驗證**
```bash
py -c "
gen = TrigonometricFunctionGenerator()
q = gen.generate_question()
print(f'題目: {q[\"question\"][:30]}...')
print(f'答案: {q[\"answer\"]}')
print(f'年級: {q.get(\"grade\")}')
print(f'科目: {q.get(\"subject\")}')
"
```

#### **測試 3: 配置系統驗證**
```bash
py -c "
schema = TrigonometricFunctionGenerator.get_config_schema()
print(f'配置選項: {list(schema.keys())}')
print(f'角度模式選項: {schema[\"angle_mode\"][\"options\"]}')
"
```

## 📊 **預期效果**

### **功能修復**
- ✅ `figure_data_question`: None → 正確的圖形配置字典
- ✅ `figure_data_explanation`: None → 正確的詳解圖形配置
- ✅ 題目和詳解圖形正常顯示

### **架構統一**
- 🏗️ 符合新基類 `_get_standard_metadata()` 架構
- 🔄 使用方法override而非直接設置
- 📐 遵循單一職責原則

### **程式碼品質提升**
- 📖 **可讀性**: 職責分離清晰，邏輯流程明確
- 🔧 **維護性**: 符合新架構，未來修改容易
- 📚 **文檔完整**: Sphinx標準註解，開發者友善
- 🧪 **可測試性**: 狀態管理清楚，容易單元測試

## ⚠️ **風險評估與緩解**

### **風險分析**
- **低風險**: 新增方法override (不影響現有邏輯)
- **中風險**: 修改核心邏輯 `_generate_core_logic()`
- **零風險**: 文檔註解更新

### **緩解措施**
- 🛡️ **分階段執行**: 每步驗證後再進行下一步
- 🛡️ **向後兼容**: 保留所有現有功能
- 🛡️ **快速回滾**: 工作區修改，`git checkout .` 可完全恢復

### **成功標準**
- [ ] 圖形數據不再是None
- [ ] 所有現有功能正常運作
- [ ] 通過完整功能測試
- [ ] 符合新架構標準
- [ ] 文檔完整標準化

## 🎯 **執行準備就緒**

所有分析、設計、測試方案都已完成，可以開始執行修復工作。
修改將在工作區進行，不會影響git歷史，隨時可以回滾。

**等待執行指示**: 準備按Phase 1 → Phase 2 → Phase 3 → Phase 4順序執行。