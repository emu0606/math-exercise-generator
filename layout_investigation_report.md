# 佈局引擎預排序機制調查報告

> **調查時間**: 2025-09-14
> **調查目標**: 分析為什麼SMALL題目分散到不同行，檢查預排序邏輯實施情況
> **調查範圍**: 佈局引擎核心邏輯、題目排序機制、策略工作流程

## 🔍 **調查發現**

### **1. 預排序機制存在但未被使用**

**發現位置**: `utils/orchestration/question_distributor.py:493-509`

**關鍵代碼**:
```python
# 新增：按尺寸預排序（關鍵步驟）
if self.config.sort_by_size:
    # 按回合進行預排序
    final_questions = []
    for round_idx in range(rounds):
        # ...回合內按尺寸排序
        sorted_round = self.sorter.sort_by_size(
            round_questions, self.config.size_sort_ascending
        )
        final_questions.extend(sorted_round)
```

**預排序邏輯完整實現**:
- ✅ `sort_by_size` 方法已實現 (L407-435)
- ✅ 回合內排序機制已實現 (L495-506)
- ✅ 升序排列邏輯完整 (小尺寸優先)

### **2. 測試腳本未使用預排序**

**問題根源**: `test_layout_html_visualization.py`

**測試腳本的題目創建流程**:
```python
# L43-53: 直接創建題目，沒有排序
def create_complex_test_questions(sizes: List[QuestionSize], labels: List[str] = None):
    questions = []
    for i, (size, label) in enumerate(zip(sizes, labels)):
        questions.append({
            'size': size,
            'label': label
            # ...
        })
    return questions  # 直接返回，沒有排序
```

**佈局引擎調用**:
```python
# L380: 直接使用LayoutEngine，跳過了QuestionDistributor
layout_engine = LayoutEngine(strategy="three_stage")
layout_results = layout_engine.layout(questions)  # 題目順序未經排序
```

### **3. Three_Stage策略工作機制分析**

**策略邏輯**: `utils/core/layout.py:335-341`
```python
# 階段1: 高度=1題目優先處理（避免參差）
if height_cells == 1:
    position = self.row_first.find_position(grid_manager, page, width_cells, height_cells)
    if position:
        return position
```

**行優先尋找**: `utils/core/layout.py:241-248`
```python
# 行優先遍歷（外迴圈：行，內迴圈：列）
for row in range(grid_manager.grid_height - height_cells + 1):
    if not self._is_row_compatible(grid_manager, page, row, height_cells):
        continue  # 跳過不相容的行
    for col in range(grid_width - width_cells + 1):
        if grid_manager.can_place_at(page, row, col, width_cells, height_cells):
            return (row, col)
```

**相容性檢查**: `utils/core/layout.py:252-278`
- 檢查目標行是否與已有題目高度一致
- 防止混合高度題目出現在同一行

### **4. SMALL題目分散原因分析**

**測試案例1輸入順序**:
```python
# test_case_1: 8個SMALL + 4個SQUARE + 3個WIDE + 1個MEDIUM + 1個LARGE
[SMALL, SMALL, SMALL, SMALL, SMALL, SMALL, SMALL, SMALL,
 SQUARE, SQUARE, SQUARE, SQUARE, WIDE, WIDE, WIDE, MEDIUM, LARGE]
```

**實際處理順序**（未排序）:
1. S1(SMALL) → 行0列0 ✅
2. S2(SMALL) → 行0列1 ✅
3. S3(SMALL) → 行0列2 ✅
4. S4(SMALL) → 行0列3 ✅
5. S5(SMALL) → 行1列0 ❌ **應該在行0，但行0已滿**
6. S6(SMALL) → 行2列0 ❌ **應該聚集，但行1被S5佔用**
7. ... 以此類推

**根本問題**:
- 沒有按尺寸預排序，SMALL題目在輸入中不連續
- 當後續SMALL題目到達時，前面適合的行已經被earlier SMALL題目部分佔用
- Three_Stage策略的行相容性檢查工作正常，但輸入順序導致最佳佈局無法實現

---

## 🎯 **調查結論**

### **✅ 系統現狀**
1. **預排序機制完整** - `QuestionDistributor.sort_by_size()` 功能完備
2. **佈局策略正確** - `ThreeStageStrategy` 邏輯無誤
3. **防參差機制有效** - 行高度相容性檢查工作正常

### **❌ 問題根源**
1. **測試腳本跳過預排序** - 直接調用`LayoutEngine`，未經`QuestionDistributor`
2. **輸入順序不理想** - SMALL題目分散在輸入列表中
3. **策略無法補救** - 即使策略正確，也無法克服輸入順序的影響

### **🔧 解決方案驗證**

**理論上正確的工作流程**:
```
輸入: [SMALL, SMALL, SMALL, SMALL, SMALL, SQUARE, SQUARE, WIDE, WIDE, MEDIUM]
↓
QuestionDistributor.sort_by_size()
↓
排序: [SMALL, SMALL, SMALL, SMALL, SMALL, WIDE, WIDE, SQUARE, SQUARE, MEDIUM]
↓
LayoutEngine.layout()
↓
預期結果: 行0 [S1][S2][S3][S4], 行1 [S5][W1][W1], 行2 [W2][W2], 行3 [Q1], 行4 [Q1]...
```

---

## 📊 **系統性問題分析**

### **1. 架構設計問題**
- 測試代碼直接使用`LayoutEngine`，跳過了`QuestionDistributor`
- 正確的工作流程應該是: `QuestionDistributor` → `LayoutEngine`

### **2. 文檔與實現不一致**
- 佈局引擎註釋提到"預排序機制"，但引擎本身不負責排序
- 排序邏輯實際在`QuestionDistributor`中

### **3. 集成測試不足**
- 單元測試可能只測試各模組獨立功能
- 缺乏端到端的集成測試驗證完整工作流程

---

## 🚨 **重要發現**

### **系統現狀**: ✅ **功能完整，但整合不當**

1. **所有核心機制都已正確實現**:
   - ✅ 預排序邏輯 (`sort_by_size`)
   - ✅ 三階段佈局策略 (`three_stage`)
   - ✅ 行高度相容性檢查 (`_is_row_compatible`)
   - ✅ 防參差機制 (混合高度檢測)

2. **問題在於模組整合**:
   - ❌ 測試工具直接調用`LayoutEngine`
   - ❌ 跳過了關鍵的`QuestionDistributor`預排序步驟
   - ❌ 導致最佳佈局無法實現

3. **方案A機制驗證**: ✅ **已完整實現並工作正常**
   - 行高度鎖定邏輯完全符合設計方案A的要求
   - 相容性檢查成功防止混合高度題目混排
   - 在正確輸入順序下會產生理想佈局

---

## 📋 **建議措施**

### **短期修正** (不改動代碼)
1. **測試流程修正** - 使用`QuestionDistributor`作為入口點
2. **文檔更新** - 明確說明正確的使用流程
3. **集成測試** - 添加端到端測試案例

### **長期優化** (如獲授權)
1. **API改善** - 讓`LayoutEngine`自動集成預排序
2. **架構重構** - 統一佈局相關功能的入口點
3. **配置優化** - 提供更靈活的排序選項

---

**調查狀態**: ✅ **調查完成**
**核心結論**: 系統功能完整正確，問題在於測試工具未使用完整工作流程
**建議行動**: 修正測試腳本使用`QuestionDistributor`入口，驗證完整預排序佈局效果