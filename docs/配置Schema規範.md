# 配置Schema規範

> **目標**: 為生成器配置UI系統建立統一的Schema格式標準
> **建立日期**: 2025-09-23
> **更新日期**: 2025-09-30
> **狀態**: 正式規範

## 🎯 **設計原則**

- **嚴格驗證**: ConfigFactory會驗證所有Schema格式，錯誤格式立即拋出異常
- **開發者友善**: 清晰的規範和豐富的範例
- **教師友善**: 標籤和說明使用易懂的中文術語
- **職責分離**: UI層驗證輸入，生成器信任配置值

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
| `type` | str | ✅ | 控件類型（select, number_input, checkbox, percentage_group） |
| `label` | str | ✅ | 用戶界面顯示的標籤文字 |
| `default` | Any | ✅ | 預設值，必須與控件類型兼容 |

### **配置項可選欄位**
| 欄位 | 類型 | 說明 |
|------|------|------|
| `description` | str | 詳細說明文字，顯示為提示 |

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
    "description": "basic包含sin,cos,tan；extended額外包含cot,sec,csc"
}
```

---

### **2. number_input - 數字輸入框**

#### **格式定義**
```python
{
    "type": "number_input",
    "label": "顯示標籤",
    "default": 數字值,
    "min": 最小值,                    # 可選
    "max": 最大值,                    # 可選
    "description": "可選的詳細說明"
}
```

#### **驗證規則**
- ✅ `default` 必需，且為整數類型
- ✅ 如指定 `min`/`max`，`default` 必須在範圍內

#### **範例**
```python
"max_value": {
    "type": "number_input",
    "label": "數值上限",
    "default": 25,
    "min": 5,
    "max": 100,
    "description": "控制生成答案數字的最大值"
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
"allow_negative": {
    "type": "checkbox",
    "label": "允許負數",
    "default": False,
    "description": "是否允許生成負數答案"
}
```

---

### **4. percentage_group - 百分比分配控件**

#### **設計理念**
- 處理多個數值必須總和=100%的場景
- 使用彈出對話框提供充足的配置空間
- UI層強制驗證總和=100%，生成器直接使用

#### **格式定義**
```python
{
    "type": "percentage_group",
    "label": "組合標籤",
    "description": "詳細說明",
    "items": {
        "item1_name": {
            "label": "項目1標籤",
            "default": 數字值
        },
        "item2_name": {
            "label": "項目2標籤",
            "default": 數字值
        }
        # ... 可以有N個項目
    }
}
```

#### **驗證規則**
- ✅ `items` 必需，且至少包含2個項目
- ✅ 所有項目的 `default` 總和必須等於100
- ✅ 所有項目必須包含 `label` 和 `default`
- ✅ `default` 值必須為正整數

#### **範例**
```python
"mode_weights": {
    "type": "percentage_group",
    "label": "題型比例分配",
    "description": "調整三種題型的出現頻率，總和自動保持為100%",
    "items": {
        "original": {
            "label": "0~90°轉換",
            "default": 70
        },
        "formula": {
            "label": "公式問答",
            "default": 10
        },
        "narrow_angle": {
            "label": "銳角計算",
            "default": 20
        }
    }
}
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
❌ **percentage總和錯誤**: 所有項目default總和不等於100

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
        "max_value": {
            "type": "number_input",
            "label": "數值上限",
            "default": 10,
            "min": 1,
            "max": 50
        },

        # 開關選項
        "show_steps": {
            "type": "checkbox",
            "label": "顯示解題步驟",
            "default": True
        }
    }
```

---

## 🔗 **相關文檔**

- [生成器開發指南.md](生成器開發指南.md) - 完整的生成器開發流程
- [配置控件擴展指南.md](配置控件擴展指南.md) - ConfigFactory實現細節

**典範生成器參考**:
- `generators/algebra/double_radical_simplification.py` - number_input範例
- `generators/trigonometry/TrigAngleConversionGenerator.py` - percentage_group範例
- `generators/trigonometry/TrigonometricFunctionGenerator.py` - select範例

---

**注意**: ConfigFactory會在UI層完成所有驗證，生成器只需使用簡單的 `options.get(key, default)` 模式讀取配置值，無需重複驗證。
