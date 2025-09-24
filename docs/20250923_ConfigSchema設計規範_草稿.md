# ConfigSchema設計規範 (草稿)

> **文檔**: 數學測驗生成器配置Schema設計規範
> **創建日期**: 2025-09-23
> **狀態**: 📝 **草稿**
> **目的**: 為動態配置UI系統建立統一的Schema格式標準

## 🎯 **設計目標**

### **核心原則**
- **嚴格驗證**: 所有Schema必須符合規範，錯誤格式立即拋出異常
- **可擴展性**: 支援未來新增控件類型和複雜配置場景
- **開發者友善**: 清晰的規範和豐富的範例
- **向後兼容**: 基礎控件保持穩定，擴展控件漸進式加入

---

## 📋 **Schema基礎格式**

### **頂層結構**
```python
@classmethod
def get_config_schema(cls) -> Dict[str, Dict[str, Any]]:
    """返回配置項描述字典"""
    return {
        "config_field_name": {
            # 配置項定義
        }
    }
```

### **配置項必需欄位**
| 欄位 | 類型 | 必需 | 說明 |
|------|------|------|------|
| `type` | str | ✅ | 控件類型，決定UI生成方式 |
| `label` | str | ✅ | 用戶界面顯示的標籤文字 |
| `default` | Any | ✅ | 預設值，必須與控件類型兼容 |

### **配置項可選欄位**
| 欄位 | 類型 | 說明 |
|------|------|------|
| `description` | str | 詳細說明文字，顯示為提示 |
| `help_url` | str | 說明文檔連結 |

---

## 🔧 **支援的控件類型**

### **1. select - 下拉選擇框**

#### **格式定義**
```python
{
    "type": "select",
    "label": "顯示標籤",
    "default": "預設選項",
    "options": ["選項1", "選項2", "選項3"],  # 必需
    "description": "可選的詳細說明"
}
```

#### **驗證規則**
- ✅ `options` 必需，且為非空列表
- ✅ `default` 必需，且必須在 `options` 中
- ✅ `options` 中不能有重複項目

#### **範例**
```python
"function_scope": {
    "type": "select",
    "label": "函數範圍",
    "default": "basic",
    "options": ["basic", "extended"],
    "description": "basic(sin,cos,tan) vs extended(+cot,sec,csc)"
}
```

---

### **2. number - 數字輸入框**

#### **格式定義**
```python
{
    "type": "number",
    "label": "顯示標籤",
    "default": 數字值,
    "min": 最小值,                    # 可選
    "max": 最大值,                    # 可選
    "datatype": "int" | "float",      # 可選，預設 "int"
    "suffix": "單位符號",              # 可選，如 "%"
    "description": "可選的詳細說明"
}
```

#### **驗證規則**
- ✅ `default` 必需，且為數字類型
- ✅ 如指定 `min`/`max`，`default` 必須在範圍內
- ✅ `datatype` 如指定，必須為 "int" 或 "float"
- ✅ `default` 類型必須與 `datatype` 一致

#### **範例**
```python
"max_questions": {
    "type": "number",
    "label": "最大題數",
    "default": 10,
    "min": 1,
    "max": 100,
    "datatype": "int",
    "description": "每次生成的最大題目數量"
}
```

---

### **3. checkbox - 勾選框**

#### **格式定義**
```python
{
    "type": "checkbox",
    "label": "顯示標籤",
    "default": True | False,
    "description": "可選的詳細說明"
}
```

#### **驗證規則**
- ✅ `default` 必需，且為布林值

#### **範例**
```python
"show_steps": {
    "type": "checkbox",
    "label": "顯示解題步驟",
    "default": True,
    "description": "在解釋中包含詳細的計算步驟"
}
```

---

### **4. percentage_group - 百分比組合控件**

#### **設計理念**
- 處理多個數值必須滿足特定數學關係的場景
- 前N-1個可編輯，最後一個自動計算確保總和=100%
- 支援2個以上的項目（不限制為3個）

#### **格式定義**
```python
{
    "type": "percentage_group",
    "label": "組合標籤",
    "description": "詳細說明",
    "validation": {
        "total_target": 100,          # 總和目標值
        "auto_adjust": True          # 超過目標時是否自動調整
    },
    "items": {
        "item1_name": {
            "type": "number",
            "label": "項目1標籤",
            "default": 數字值,
            "min": 0,
            "max": 100,
            "datatype": "int",
            "editable": True          # 可編輯
        },
        "item2_name": {
            "type": "number",
            "label": "項目2標籤",
            "default": 數字值,
            "min": 0,
            "max": 100,
            "datatype": "int",
            "editable": True          # 可編輯
        },
        "itemN_name": {
            "type": "number",
            "label": "項目N標籤",
            "default": 數字值,
            "min": 0,
            "max": 100,
            "datatype": "int",
            "editable": False,        # 自動計算，不可編輯
            "computed": True          # 標記為計算欄位
        }
    }
}
```

#### **驗證規則**
- ✅ `items` 必需，且至少包含2個項目
- ✅ 必須有且僅有一個項目的 `editable` 為 `False` 且 `computed` 為 `True`
- ✅ 計算項目必須是最後一個項目（保持UI邏輯一致）
- ✅ 所有項目的 `default` 總和必須等於 `total_target`
- ✅ 所有項目必須為 `number` 類型且有相同的 `datatype`

#### **範例**
```python
"mode_weights": {
    "type": "percentage_group",
    "label": "題型比例分配",
    "description": "調整各種題型的出現頻率，總和自動保持100%",
    "validation": {
        "total_target": 100,
        "auto_adjust": True
    },
    "items": {
        "original": {
            "type": "number",
            "label": "第一象限轉換(%)",
            "default": 70,
            "min": 0,
            "max": 100,
            "datatype": "int",
            "editable": True
        },
        "formula": {
            "type": "number",
            "label": "公式問答(%)",
            "default": 10,
            "min": 0,
            "max": 100,
            "datatype": "int",
            "editable": True
        },
        "narrow_angle": {
            "type": "number",
            "label": "窄角轉換(%)",
            "default": 20,
            "min": 0,
            "max": 100,
            "datatype": "int",
            "editable": False,
            "computed": True
        }
    }
}
```

---

## ✅ **Schema驗證器設計**

### **驗證器介面**
```python
# utils/ui/schema_validator.py
class ConfigSchemaValidator:
    def validate_schema(self, schema: Dict[str, Any]) -> None:
        """嚴格驗證schema格式，發現問題立即拋出異常"""

    def validate_field(self, field_name: str, field_config: Dict[str, Any]) -> None:
        """驗證單個配置項"""

    def _validate_select_field(self, config: Dict[str, Any]) -> None:
        """驗證select類型欄位"""

    def _validate_number_field(self, config: Dict[str, Any]) -> None:
        """驗證number類型欄位"""

    def _validate_percentage_group_field(self, config: Dict[str, Any]) -> None:
        """驗證percentage_group類型欄位"""

class ConfigSchemaError(Exception):
    """Schema格式錯誤異常"""
    pass
```

### **錯誤處理策略**
- **立即失敗**: 發現任何格式錯誤立即拋出 `ConfigSchemaError`
- **詳細錯誤信息**: 明確指出哪個欄位的哪個規則違反
- **開發者友善**: 提供修正建議和正確範例連結

### **錯誤信息範例**
```
ConfigSchemaError:
欄位 'function_scope' 驗證失敗:
- 缺少必需欄位 'options'
- 預設值 'invalid' 不在選項 ['basic', 'extended'] 中

修正建議: 請參考文檔第X節的select控件範例
```

---

## 🧪 **測試器設計**

### **自動化測試**
```python
# tests/test_config_schema.py
class TestConfigSchema:
    def test_all_generators_have_valid_schema(self):
        """掃描所有生成器並驗證schema格式"""

    def test_percentage_group_validation(self):
        """測試percentage_group的各種邊界情況"""

    def test_schema_error_messages(self):
        """測試錯誤信息的清晰度"""
```

### **開發工具**
```python
# tools/check_schema.py
def check_generator_schema(generator_class):
    """手動檢查指定生成器的schema"""

def validate_all_schemas():
    """檢查所有生成器的schema"""
```

---

## 📚 **開發者指南**

### **最佳實踐**
1. **簡單優先**: 能用select就不用percentage_group
2. **清晰標籤**: label要讓教師一看就懂
3. **合理預設值**: default應該是最常用的選項
4. **適當描述**: description解釋選項的實際影響

### **常見錯誤**
❌ **缺少options**: select類型沒有提供選項列表
❌ **預設值錯誤**: default不在options範圍內
❌ **percentage_group設計錯誤**: 多個computed項目或computed項目不在最後

### **範例模板**
```python
@classmethod
def get_config_schema(cls):
    """標準配置描述模板"""
    return {
        # 簡單選擇
        "mode": {
            "type": "select",
            "label": "模式選擇",
            "default": "normal",
            "options": ["easy", "normal", "hard"],
            "description": "選擇題目難度級別"
        },

        # 數字輸入
        "count": {
            "type": "number",
            "label": "題目數量",
            "default": 10,
            "min": 1,
            "max": 50,
            "datatype": "int"
        },

        # 開關選項
        "show_hint": {
            "type": "checkbox",
            "label": "顯示提示",
            "default": False
        }
    }
```

---

## 🔄 **未來擴展預留**

### **計劃支援的控件類型**
- **range**: 範圍選擇（min-max組合）
- **conditional**: 條件配置（基於其他欄位值顯示/隱藏）
- **text**: 文字輸入框
- **color**: 顏色選擇器（圖形配置）

### **擴展原則**
- 每個新類型都要有完整的驗證規則
- 保持向後兼容，舊schema繼續有效
- 新功能漸進式推出，先實現基礎控件

---

## 📋 **實施檢查清單**

### **Schema規範完成標準**
- [ ] 四種基礎控件類型完整定義
- [ ] percentage_group通用設計（支援N個項目）
- [ ] 嚴格驗證規則和錯誤處理
- [ ] 完整的開發者指南和範例
- [ ] 自動化測試設計方案

### **驗證器實現標準**
- [ ] 所有驗證規則正確實現
- [ ] 清晰的錯誤信息和修正建議
- [ ] 完整的單元測試覆蓋
- [ ] 與ConfigUIFactory整合

### **測試工具標準**
- [ ] 自動掃描所有生成器
- [ ] 邊界情況和錯誤情況測試
- [ ] 開發時即時驗證工具
- [ ] CI/CD集成

---

**狀態**: 📝 **草稿完成，等待審核和確認**
**下一步**: 基於此規範更新動態配置UI工作計畫
**重點**: percentage_group的通用設計和嚴格驗證策略