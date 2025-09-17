# 舊架構參數模型歷史存檔

> **存檔日期**: 2025-09-16
> **存檔原因**: 參數模型架構統一，移除雙軌制
> **原文件位置**: `figures/params_models.py`

## 📋 **存檔內容**

### **主要文件**
- `params_models_archived_20250916.py`: 原始的單文件參數模型架構

### **歷史背景**
在2025-09-08的現代化重構中，引入了新的模組化參數模型架構 (`figures/params/`)，但未完全移除舊的單文件架構 (`figures/params_models.py`)，導致雙軌制並存問題。

### **新舊架構對比**

#### **舊架構特點** (已存檔)
- **單文件設計**: 所有參數類集中在 `params_models.py`
- **參數類數量**: 11個參數類
- **主要參數類**:
  - `UnitCircleParams`, `StandardUnitCircleParams`
  - `CompositeParams`, `SubFigureParams`
  - `PredefinedTriangleParams`, `BasicTriangleParams`
  - `ArcParams` (使用 `start_angle_rad`)

#### **新架構特點** (當前使用)
- **模組化設計**: 參數類分散在 `figures/params/` 目錄下
- **參數類數量**: 19個參數類
- **改進功能**:
  - 更細緻的參數控制
  - 統一的命名規範
  - 更好的模組化組織

### **API變更對照表**

| 功能 | 舊架構 | 新架構 | 變更說明 |
|------|--------|--------|----------|
| 弧度角度 | `start_angle_rad` | `start_angle` | 統一使用度數 |
| 座標範圍 | `x_min, x_max` | `x_range` | 使用tuple格式 |
| 填充屬性 | `fill` | `fill_color` | 更明確的屬性名 |
| 導入路徑 | `from .params_models import` | `from .params import` | 模組化導入 |

### **遷移影響**
- **複合生成器**: `StandardUnitCircleGenerator`, `PredefinedTriangleGenerator` 已遷移
- **參數屬性**: 所有不一致的參數定義已統一
- **導入語句**: 所有生成器已更新為新架構導入

### **技術債務清理**
通過這次架構統一，解決了：
1. **雙軌制維護負擔**: 不再需要同時維護兩套參數模型
2. **定義不一致**: 所有參數類使用統一的屬性定義
3. **生成器故障**: 參數模型不匹配導致的生成器故障問題

---

**注意**: 此存檔僅供歷史參考，不應再用於開發。所有新開發都應使用 `figures/params/` 新架構。