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
- 處理多個數值必須總和=100%的場景
- 使用彈出對話框提供充足的配置空間
- 支援2個以上的項目（不限制為3個）
- 採用極簡設計，避免過度工程化

#### **實施方式**
- **UI實現**：彈出式配置對話框，而非內嵌複雜控件
- **字體規範**：遵循FontManager系統，支援動態縮放
- **視覺化**：文字進度條即時預覽，5行代碼實現

#### **格式定義（簡化版）**
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
        },
        "itemN_name": {
            "label": "項目N標籤",
            "default": 數字值
        }
    }
}
```

#### **驗證規則（簡化）**
- ✅ `items` 必需，且至少包含2個項目
- ✅ 所有項目的 `default` 總和必須等於100
- ✅ 所有項目必須包含 `label` 和 `default`
- ✅ `default` 值必須為正整數

#### **範例（基於實際使用）**
```python
"mode_weights": {
    "type": "percentage_group",
    "label": "題型比例分配",
    "description": "調整三種題型的出現頻率，總和會自動正規化為100%",
    "items": {
        "original": {
            "label": "第一象限轉換(%)",
            "default": 70
        },
        "formula": {
            "label": "公式問答(%)",
            "default": 10
        },
        "narrow_angle": {
            "label": "窄角轉換(%)",
            "default": 20
        }
    }
}
```

#### **對話框實施詳情**
```python
# 實際產生的彈出對話框包含：
# - 標題：使用18px bold字體
# - 說明文字：14px #3498db顏色
# - N個數值輸入框：QSpinBox (0-100範圍)
# - 文字進度條：12px等寬字體即時預覽
# - 總和驗證：嚴格=100%才能確定
# - 確定/取消按鈕：14px預設字體
```

---

## ✅ **Schema驗證器設計（簡化版）**

### **驗證器介面**
```python
# utils/ui/schema_validator.py
class ConfigSchemaValidator:
    def validate_schema(self, schema: Dict[str, Any]) -> None:
        """驗證schema格式，配合Phase 4實施方案"""

    def validate_field(self, field_name: str, field_config: Dict[str, Any]) -> None:
        """驗證單個配置項，支援四種基礎控件類型"""

    def _validate_select_field(self, config: Dict[str, Any]) -> None:
        """驗證select類型：options必需，default在options中"""

    def _validate_number_field(self, config: Dict[str, Any]) -> None:
        """驗證number類型：default為數字，支援min/max範圍"""

    def _validate_checkbox_field(self, config: Dict[str, Any]) -> None:
        """驗證checkbox類型：default為布林值"""

    def _validate_percentage_group_field(self, config: Dict[str, Any]) -> None:
        """驗證percentage_group類型：items必需，總和=100"""

class ConfigSchemaError(Exception):
    """Schema格式錯誤異常"""
    pass
```

### **簡化版驗證規則**
```python
def _validate_percentage_group_field(self, config: Dict[str, Any]) -> None:
    """專為Phase 4彈出對話框設計的驗證邏輯"""

    # 基本欄位檢查
    if 'items' not in config:
        raise ConfigSchemaError("percentage_group必須包含items欄位")

    items = config['items']
    if len(items) < 2:
        raise ConfigSchemaError("percentage_group至少需要2個項目")

    # 簡化驗證：只檢查label和default
    total = 0
    for item_name, item_config in items.items():
        if 'label' not in item_config:
            raise ConfigSchemaError(f"項目{item_name}缺少label欄位")
        if 'default' not in item_config:
            raise ConfigSchemaError(f"項目{item_name}缺少default欄位")

        default_val = item_config['default']
        if not isinstance(default_val, int) or default_val < 0:
            raise ConfigSchemaError(f"項目{item_name}的default必須為正整數")

        total += default_val

    # 總和必須=100
    if total != 100:
        raise ConfigSchemaError(f"所有項目default總和必須=100，當前={total}")
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

## 📋 **Phase 4實施檢查清單**

### **ConfigSchema規範標準**
- [x] 四種基礎控件類型定義（select, number, checkbox, percentage_group）
- [x] percentage_group簡化設計（彈出對話框實施）
- [x] 簡化版驗證規則和錯誤處理
- [x] 實際使用範例和開發者指南
- [ ] 字體規範與FontManager整合說明

### **與Phase 4實施方案對齊**
- [x] percentage_group採用彈出對話框實施
- [x] 移除過度工程化設計（editable, computed, validation巢狀）
- [x] 符合「基礎招式」設計理念
- [x] 支援文字進度條視覺化需求
- [ ] ConfigUIFactory整合方式說明

### **驗證器實現標準（簡化版）**
- [ ] 四種控件類型驗證邏輯
- [ ] percentage_group總和=100%驗證
- [ ] 清晰的ConfigSchemaError錯誤信息
- [ ] 與ConfigUIFactory整合測試

### **實際使用測試**
- [ ] 三角函數生成器配置schema驗證
- [ ] 角度轉換生成器複雜配置測試
- [ ] 彈出對話框UI生成測試
- [ ] 配置值收集和傳遞測試

---

## 🎯 **與Phase 4工作計畫的整合**

### **ConfigUIFactory擴展需求**
基於此Schema規範，Phase 4需要實現：

1. **percentage_group控件生成**：
   ```python
   def _create_percentage_group_widget(self, config: Dict[str, Any]) -> QPushButton:
       """創建百分比配置按鈕，點擊開啟PercentageConfigDialog"""
   ```

2. **對話框實施**：
   ```python
   class PercentageConfigDialog(QDialog):
       """根據schema['items']動態生成N個數值輸入框"""
   ```

3. **配置值收集**：
   ```python
   def collect_percentage_group_values(self, button: QPushButton) -> Dict[str, int]:
       """從按鈕屬性收集百分比配置值"""
   ```

### **字體規範整合**
- **對話框標題**：18px bold（title字體）
- **描述文字**：14px #3498db（與ConfigUIFactory一致）
- **進度條文字**：12px等寬字體（Consolas回退）
- **輸入框標籤**：14px預設（widget字體）

---

**狀態**: ✅ **Phase 4實施規範完成 - 已簡化並對齊實際方案**
**核心調整**: 移除過度工程化，採用彈出對話框極簡設計
**下一步**: 基於此規範開始Phase 4的ConfigUIFactory擴展實施
**重點**: 簡化的percentage_group格式 + 字體系統整合