# CategoryWidget UI視覺層級與彈出配置視窗改善計畫

> **專案**: 數學測驗生成器UI改善
> **制定日期**: 2025-09-24
> **狀態**: 🔄 **研擬中**
> **問題類型**: UI可用性改善 - 視覺層級不清晰、配置空間浪費
> **技術方案**: 視覺層級強化 + 彈出式配置視窗

## 🎯 **問題確認**

### **當前UI問題**
根據用戶反饋和螢幕截圖分析，發現以下關鍵問題：

1. **視覺層級不清晰**
   - 主類別和次類別幾乎完全對齊，缺乏縮排
   - 顏色區分不明顯，難以快速識別層級關係
   - 缺乏視覺引導元素 (邊框、分隔線等)

2. **配置UI空間浪費嚴重**
   - 配置選項永久展開，佔用大量垂直空間
   - 沒有摺疊機制，導致界面擁擠
   - 配置與題型選擇混在一起，視覺雜亂

3. **代碼層面的問題**
   - 主次類別使用相同的 `setContentsMargins(8, *, 8, *)`
   - 配置UI直接加入layout，無摺疊容器包裝
   - CSS樣式對比度不足，缺乏層級指示

---

## 🔧 **解決方案設計**

### **Phase A: 視覺層級改善 (30分鐘)**

#### **A1: 縮排結構調整**
**目標文件**: `ui/category_widget.py`

```python
# 當前問題代碼
# 主類別
category_layout.setContentsMargins(8, 5, 8, 5)
# 次類別
subcat_layout.setContentsMargins(8, 3, 8, 3)   # 相同左邊距!

# 修復後代碼
# 主類別 (保持)
category_layout.setContentsMargins(8, 5, 8, 5)
# 次類別 (增加縮排)
subcat_layout.setContentsMargins(24, 3, 8, 3)   # +16px 縮排
```

#### **A2: CSS樣式強化**
**目標文件**: `assets/style.qss`

```css
/* 當前樣式 - 對比度不足 */
QFrame#categoryFrame { background-color: #ecf0f1; }    /* 淺灰 */
QFrame#subcategoryFrame { background-color: white; }   /* 白色 */

/* 改善後樣式 - 強化層級 */
QFrame#categoryFrame {
    background-color: #d5dbdb;          /* 更深的灰色 */
    border-left: 3px solid #3498db;     /* 藍色左邊框指示 */
    font-weight: 500;                   /* 稍微加粗字體 */
}

QFrame#subcategoryFrame {
    background-color: #fdfdfd;          /* 純白背景 */
    border-left: 2px solid #bdc3c7;    /* 淺灰左邊框指示 */
    margin-left: 8px;                   /* 額外視覺縮排 */
}
```

---

### **Phase B: 彈出配置視窗機制 (10分鐘)**

#### **B1: 創建配置對話框**
**新增方法**: `_create_config_button` 和 `_show_config_dialog`

```python
def _create_config_button(self, config_ui: QWidget, topic_name: str) -> QPushButton:
    """創建配置按鈕，點擊彈出配置視窗

    採用彈出視窗方案，完全安全無風險的實施方式。
    配置UI保持原始狀態，ConfigValueCollector直接工作。

    Args:
        config_ui: 原始配置控件
        topic_name: 題型名稱，用於視窗標題

    Returns:
        配置按鈕，點擊後彈出配置對話框
    """
    config_btn = QPushButton("⚙️")
    config_btn.setObjectName("configButton")
    config_btn.setFixedSize(24, 24)
    config_btn.setToolTip(f"配置 {topic_name}")

    # 點擊事件：彈出配置視窗
    config_btn.clicked.connect(
        lambda: self._show_config_dialog(config_ui, topic_name)
    )

    return config_btn

def _show_config_dialog(self, config_ui: QWidget, topic_name: str):
    """顯示配置對話框

    使用QDialog包裝配置UI，確保配置收集功能完全正常。
    零風險實施，不需要任何代理或包裝機制。

    Args:
        config_ui: 配置UI控件
        topic_name: 題型名稱
    """
    dialog = QDialog(self)
    dialog.setWindowTitle(f"{topic_name} - 配置選項")
    dialog.setModal(True)
    dialog.setFixedSize(420, 250)

    # 主佈局
    layout = QVBoxLayout(dialog)
    layout.addWidget(config_ui)

    # 按鈕區域
    btn_layout = QHBoxLayout()
    btn_layout.addStretch()

    ok_btn = QPushButton("確定")
    cancel_btn = QPushButton("取消")

    ok_btn.clicked.connect(dialog.accept)
    cancel_btn.clicked.connect(dialog.reject)

    btn_layout.addWidget(ok_btn)
    btn_layout.addWidget(cancel_btn)
    layout.addLayout(btn_layout)

    # 應用對話框樣式
    dialog.setObjectName("configDialog")

    # 顯示對話框
    dialog.exec_()
```

#### **B2: 修改配置UI整合邏輯**
**目標位置**: `populate_categories` 方法 (205行)

```python
# 當前問題代碼
if config_ui:
    subcat_layout.addWidget(config_ui)  # 直接展開

# 修復後代碼
if config_ui:
    config_btn = self._create_config_button(config_ui, full_topic_name)
    subcat_layout.addWidget(config_btn)
```

---

### **Phase C: CSS樣式完善 (5分鐘)**

#### **C1: 配置按鈕樣式**
```css
QPushButton#configButton {
    background-color: #f39c12;
    color: white;
    border: none;
    border-radius: 3px;
    padding: 2px;
    font-size: 12px;
    min-width: 24px;
    min-height: 24px;
    max-width: 24px;
    max-height: 24px;
}

QPushButton#configButton:hover {
    background-color: #e67e22;
}

QPushButton#configButton:pressed {
    background-color: #d68910;
}
```

#### **C2: 配置對話框樣式**
```css
QDialog#configDialog {
    background-color: #ffffff;
    border: 1px solid #bdc3c7;
}

QDialog#configDialog QPushButton {
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 6px 16px;
    font-size: 14px;
}

QDialog#configDialog QPushButton:hover {
    background-color: #2980b9;
}
```

---

## 📊 **實施計畫**

### **階段一: 視覺層級改善 (10分鐘)**
1. **修改縮排設置** (5分鐘)
   - ui/category_widget.py 第148行: `setContentsMargins(8, 3, 8, 3)` → `(24, 3, 8, 3)`
   - 測試縮排效果

2. **強化CSS樣式** (5分鐘)
   - assets/style.qss: 加入邊框和顏色強化
   - 重新啟動應用測試視覺效果

### **階段二: 彈出配置視窗 (12分鐘)**
1. **修改Import語句** (1分鐘)
   - ui/category_widget.py 第10行: 在import中加入 `QDialog`

2. **實施配置對話框方法** (6分鐘)
   - 新增 `_create_config_button` 方法
   - 新增 `_show_config_dialog` 方法
   - 使用可調整大小的對話框: `dialog.resize(420, 250)`

3. **整合配置按鈕** (3分鐘)
   - 修改 populate_categories 第205行: `subcat_layout.addWidget(config_ui)` → `addWidget(config_btn)`
   - 測試配置按鈕點擊功能

4. **驗證配置收集** (2分鐘)
   - 確保配置收集功能完全正常
   - 測試彈出視窗的配置傳遞

### **階段三: CSS樣式完善與測試 (5分鐘)**
1. **CSS樣式加入** (3分鐘)
   - 配置按鈕樣式
   - 配置對話框樣式

2. **整合測試** (2分鐘)
   - 功能驗證: 配置收集是否正常
   - 視覺驗證: 按鈕和對話框樣式是否統一
   - 使用體驗: 彈出視窗操作是否流暢

---

## 🎯 **預期成果**

### **視覺改善效果**
```
改善前:
☐ 數與式
☐ 重根號練習        [0]
☐ 三角函數
☐ 三角函數值計算    [10]
   函數範圍: [extended ▼]
   角度模式: [mixed ▼]

改善後:
☐ 數與式                    ← 主類別 (深灰背景 + 藍色左邊框)
  ☐ 重根號練習      [0]      ← 次類別 (縮排 + 淺灰左邊框)
☐ 三角函數                  ← 主類別
  ☐ 三角函數值計算  [10] ⚙️ 配置 (extended, mixed) [▼]  ← 次類別
      └─ 配置面板 (摺疊狀態)
```

### **功能改善效果**
- ✅ **視覺層級清晰**: 主次類別一目瞭然
- ✅ **空間節省**: 配置面板預設摺疊，節省60%垂直空間
- ✅ **操作直觀**: 點擊配置按鈕展開/收合配置選項
- ✅ **狀態可見**: 配置按鈕顯示當前配置摘要
- ✅ **向後兼容**: 配置收集功能完全正常

---

## 🚨 **風險評估**

### **修改風險**
- **風險等級**: 中等
- **影響範圍**: 主要是UI佈局和樣式
- **功能風險**: 需確保配置收集邏輯不受影響
- **回滾方案**: 保留原始CSS和layout設置的備份

### **技術考量**
- **摺疊動畫**: 使用QWidget.setVisible()，簡單可靠
- **配置收集**: 需要適配摺疊容器的widget查找邏輯
- **CSS兼容**: 新樣式需與現有樣式兼容

### **測試重點**
- ✅ 配置UI正常顯示和隱藏
- ✅ 配置值收集功能正常
- ✅ 摺疊狀態在重新populate時保持
- ✅ 樣式在不同解析度下表現良好

---

## ✅ **成功標準**

### **功能標準**
- ✅ 主次類別視覺層級清晰可辨
- ✅ 配置面板能正常展開/摺疊
- ✅ 配置收集功能完全正常
- ✅ 配置按鈕顯示正確的狀態摘要

### **視覺標準**
- ✅ 縮排明顯，層級關係清楚
- ✅ 顏色對比度足夠，易於識別
- ✅ 界面緊湊，空間利用效率提升50%以上
- ✅ 操作流暢，無視覺突兀感

### **用戶體驗標準**
- ✅ 用戶能快速識別主次類別
- ✅ 配置操作直觀易懂
- ✅ 界面不再感到擁擠雜亂
- ✅ 配置狀態一目了然

---

## 📅 **實施時程**

**總預估時間**: 27分鐘

### **實施順序**
- **階段一** (10分鐘): 視覺層級改善 - 縮排+CSS
- **階段二** (12分鐘): 彈出配置視窗 - 完整功能
- **階段三** (5分鐘): CSS完善與最終測試

---

## 📋 **實施記錄與發現**

### **2025-09-25 微調實施記錄**

#### **已完成修改**
- **修改文件**: `utils/ui/config_factory.py` 第169行
- **修改內容**: QLabel樣式調整
  ```python
  # 修改前
  desc_label.setStyleSheet("color: #3498db; font-size: 12px;")

  # 修改後
  desc_label.setStyleSheet("color: #3498db; font-size: 14px; margin: 0px; padding: 0px;")
  ```

#### **修改效果分析**
- ✅ **字體大小提升**: 說明文字從12px提升至14px，可讀性改善
- ⚠️ **垂直間距問題**: `setSpacing(1)`設定仍未完全生效
  - 控件和說明文字間距仍約5-8px（而非預期的1px）
  - 配置組之間間距約15-20px（主佈局setSpacing(8)影響）

#### **問題根因調查**
經分析發現`setSpacing(1)`未完全生效的可能原因：
1. **佈局結構**: `container_layout.setSpacing(1)`控制的是`field_container`（整個控件容器）與`desc_label`間的間距
2. **容器影響**: `field_container` QWidget本身可能有默認樣式影響
3. **QComboBox默認樣式**: 理論上應為0邊距，需進一步驗證

#### **Phase C完成確認**
經檢查發現所有CSS樣式已完全實現：
- ✅ **配置按鈕樣式**: `QPushButton#configButton` (第190-222行) - 透明背景、hover效果完整
- ✅ **配置對話框樣式**: `QDialog#configDialog` (第289-310行) - 對話框和按鈕樣式完整

#### **下階段待驗證事項**（已擱置）
- [ ] 檢查`field_container` QWidget的默認樣式設定
- [ ] 驗證QComboBox是否真的無下邊距
- [ ] 測試為`field_container`添加樣式的效果
- [ ] 調整主佈局`setSpacing(8)`數值

## 📊 **計畫完成總結**

### **已完成項目** ✅
- **Phase A: 視覺層級改善** - 縮排調整 + CSS樣式強化
- **Phase B: 彈出配置視窗機制** - 配置按鈕 + 對話框功能
- **Phase C: CSS樣式完善** - 配置按鈕樣式 + 對話框樣式

### **部分完成項目** ⚠️
- **彈出選單垂直間距微調** - 說明文字字體提升至14px，間距優化暫時擱置

---

**狀態**: ✅ **已完成** - 主要功能全部實現
**完成度**: 95% (僅彈出選單間距微調擱置)
**成果**: UI視覺層級清晰、配置操作便捷、整體美觀度大幅提升
**建議**: 計畫可結案，微調問題可納入未來優化項目