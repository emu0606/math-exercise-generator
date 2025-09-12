# UI字體縮放控制實施計畫

> **專案**: 數學測驗生成器  
> **建立日期**: 2025-09-11  
> **類型**: UI增強功能  
> **預估時間**: 2-2.5小時

## 📋 **計畫概述**

### **背景**
當前UI字體大小固定，用戶無法根據個人需求或螢幕大小調整字體顯示。

### **目標**
- ✅ 在主視窗狀態列添加字體縮放控制按鈕
- ✅ 提供50%-200%的字體縮放範圍
- ✅ 實時生效，無需重啟應用程式
- ✅ 設定持久化，記住用戶偏好
- ✅ 仿文書編輯器的操作體驗

### **範圍**
- **包含**: PyQt5 UI元件字體大小動態調整、狀態列UI、設定持久化
- **不包含**: 鍵盤快速鍵、PDF生成字體、LaTeX渲染字體

---

## 🚀 **實施階段**

### **Phase 1: 狀態列基礎架構 (45分鐘)**

#### **Step 1.1: 修改主視窗佈局**
```python
# ui/main_window.py - 在 initUI() 方法末尾添加
def initUI(self):
    # ... 現有代碼 ...
    main_layout.addWidget(splitter)
    
    # === 新增：狀態列 ===
    self.create_status_bar()

def create_status_bar(self):
    """建立狀態列，包含字體縮放控制"""
    statusbar = self.statusBar()
    
    # 左側：狀態資訊
    self.status_label = QLabel("準備就緒")
    statusbar.addWidget(self.status_label)
    
    # 右側：字體縮放控制
    zoom_widget = self.create_zoom_controls()
    statusbar.addPermanentWidget(zoom_widget)
```

#### **Step 1.2: 縮放控制UI元件**
```python
def create_zoom_controls(self):
    """建立字體縮放控制元件"""
    widget = QWidget()
    layout = QHBoxLayout(widget)
    layout.setContentsMargins(0, 0, 5, 0)
    layout.setSpacing(3)
    
    # 縮小按鈕
    self.zoom_out_btn = QPushButton()
    self.zoom_out_btn.setIcon(load_icon('zoom-out.svg'))
    self.zoom_out_btn.setObjectName("iconButton")
    self.zoom_out_btn.setToolTip("縮小字體")
    self.zoom_out_btn.setFixedSize(24, 24)
    
    # 字體大小標籤
    self.font_size_label = QLabel("100%")
    self.font_size_label.setMinimumWidth(45)
    self.font_size_label.setAlignment(Qt.AlignCenter)
    self.font_size_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
    
    # 放大按鈕
    self.zoom_in_btn = QPushButton()
    self.zoom_in_btn.setIcon(load_icon('zoom-in.svg'))
    self.zoom_in_btn.setObjectName("iconButton")
    self.zoom_in_btn.setToolTip("放大字體")
    self.zoom_in_btn.setFixedSize(24, 24)
    
    # 重置按鈕
    self.reset_zoom_btn = QPushButton("重置")
    self.reset_zoom_btn.setObjectName("iconButton")
    self.reset_zoom_btn.setToolTip("重置為預設大小")
    self.reset_zoom_btn.setMaximumWidth(40)
    
    layout.addWidget(QLabel("字體:"))
    layout.addWidget(self.zoom_out_btn)
    layout.addWidget(self.font_size_label)
    layout.addWidget(self.zoom_in_btn)
    layout.addWidget(self.reset_zoom_btn)
    
    return widget
```

#### **Step 1.3: 狀態列樣式**
```css
/* assets/style.qss - 新增狀態列樣式 */

/* 狀態列樣式 */
QStatusBar {
    border-top: 1px solid #bdc3c7;
    background-color: #f8f9fa;
    font-size: 11px;
    color: #7f8c8d;
}

QStatusBar QLabel {
    padding: 2px 5px;
}

/* 縮放控制區域樣式 */
QStatusBar QWidget {
    background-color: transparent;
}

QStatusBar QPushButton#iconButton {
    border: 1px solid #bdc3c7;
    border-radius: 3px;
    background-color: white;
    padding: 2px;
}

QStatusBar QPushButton#iconButton:hover {
    background-color: #ecf0f1;
    border-color: #95a5a6;
}

QStatusBar QPushButton#iconButton:pressed {
    background-color: #d5dbdb;
}
```

### **Phase 2: 字體縮放核心邏輯 (1小時)**

#### **Step 2.1: 字體管理類別**
```python
# ui/font_manager.py - 新建檔案
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
字體縮放管理器
"""

import os
from utils import get_logger

class FontManager:
    """字體縮放管理器"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.logger = get_logger(self.__class__.__name__)
        
        # 基礎字體大小 (從style.qss提取)
        self.base_font_sizes = {
            'widget': 12,
            'title': 16,
            'button': 14,
            'generate_btn': 14
        }
        
        # 縮放設定
        self.current_scale = 1.0  # 100%
        self.scale_steps = [0.5, 0.75, 0.9, 1.0, 1.1, 1.25, 1.5, 2.0]  # 50%-200%
        self.min_scale = 0.5
        self.max_scale = 2.0
        
        # 載入用戶偏好
        self.load_user_preference()
        
    def get_current_scale_index(self):
        """取得目前縮放比例的索引"""
        try:
            return self.scale_steps.index(self.current_scale)
        except ValueError:
            # 如果當前縮放不在預設步驟中，找最接近的
            closest_index = 0
            min_diff = abs(self.scale_steps[0] - self.current_scale)
            for i, scale in enumerate(self.scale_steps):
                diff = abs(scale - self.current_scale)
                if diff < min_diff:
                    min_diff = diff
                    closest_index = i
            return closest_index
            
    def apply_font_scale(self, scale_factor):
        """套用字體縮放"""
        if scale_factor < self.min_scale or scale_factor > self.max_scale:
            self.logger.warning(f"縮放比例 {scale_factor} 超出範圍，已限制在 {self.min_scale}-{self.max_scale}")
            scale_factor = max(self.min_scale, min(scale_factor, self.max_scale))
            
        self.current_scale = scale_factor
        
        # 生成動態CSS
        dynamic_css = f"""
        
        /* === 動態字體縮放樣式 === */
        QWidget {{
            font-size: {int(self.base_font_sizes['widget'] * scale_factor)}px;
        }}
        
        QLabel#title {{
            font-size: {int(self.base_font_sizes['title'] * scale_factor)}px;
        }}
        
        QPushButton {{
            font-size: {int(self.base_font_sizes['button'] * scale_factor)}px;
        }}
        
        QPushButton#generateBtn {{
            font-size: {int(self.base_font_sizes['generate_btn'] * scale_factor)}px;
        }}
        
        QCheckBox {{
            font-size: {int(self.base_font_sizes['widget'] * scale_factor)}px;
        }}
        
        QLineEdit {{
            font-size: {int(self.base_font_sizes['widget'] * scale_factor)}px;
        }}
        
        QSpinBox {{
            font-size: {int(self.base_font_sizes['widget'] * scale_factor)}px;
        }}
        """
        
        # 重新載入樣式表
        self.main_window.load_stylesheet_with_zoom(dynamic_css)
        
        # 更新UI顯示
        if hasattr(self.main_window, 'font_size_label'):
            self.main_window.font_size_label.setText(f"{int(scale_factor * 100)}%")
            
        # 更新按鈕狀態
        self.update_button_states()
        
        # 儲存偏好設定
        self.save_user_preference()
        
        self.logger.info(f"字體縮放已套用: {int(scale_factor * 100)}%")
        
    def update_button_states(self):
        """更新按鈕啟用/停用狀態"""
        current_index = self.get_current_scale_index()
        
        # 更新按鈕狀態
        if hasattr(self.main_window, 'zoom_out_btn'):
            self.main_window.zoom_out_btn.setEnabled(current_index > 0)
        if hasattr(self.main_window, 'zoom_in_btn'):
            self.main_window.zoom_in_btn.setEnabled(current_index < len(self.scale_steps) - 1)
            
    def increase_font_size(self):
        """放大字體"""
        current_index = self.get_current_scale_index()
        if current_index < len(self.scale_steps) - 1:
            new_scale = self.scale_steps[current_index + 1]
            self.apply_font_scale(new_scale)
            return True
        return False
            
    def decrease_font_size(self):
        """縮小字體"""
        current_index = self.get_current_scale_index()
        if current_index > 0:
            new_scale = self.scale_steps[current_index - 1]
            self.apply_font_scale(new_scale)
            return True
        return False
            
    def reset_font_size(self):
        """重置字體大小"""
        self.apply_font_scale(1.0)
        
    def save_user_preference(self):
        """儲存用戶字體偏好設定"""
        import json
        os.makedirs("data", exist_ok=True)
        config_path = "data/user_preferences.json"
        
        try:
            # 讀取現有設定
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    prefs = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                prefs = {}
            
            # 更新字體縮放設定
            prefs['font_scale'] = self.current_scale
            
            # 寫入檔案
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(prefs, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"儲存字體偏好設定失敗: {e}")

    def load_user_preference(self):
        """載入用戶字體偏好設定"""
        try:
            with open("data/user_preferences.json", 'r', encoding='utf-8') as f:
                prefs = json.load(f)
                scale = prefs.get('font_scale', 1.0)
                
                # 驗證範圍
                if self.min_scale <= scale <= self.max_scale:
                    self.current_scale = scale
                else:
                    self.logger.warning(f"載入的字體縮放比例 {scale} 超出範圍，使用預設值")
                    self.current_scale = 1.0
                    
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.logger.info("未找到字體偏好設定檔案，使用預設值")
            self.current_scale = 1.0
        except Exception as e:
            self.logger.error(f"載入字體偏好設定失敗: {e}")
            self.current_scale = 1.0
```

#### **Step 2.2: 整合到主視窗**
```python
# ui/main_window.py - 修改現有方法和新增方法

# 在類別頂部新增導入
from ui.font_manager import FontManager

class MathTestGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # === 新增：字體管理器 ===
        self.font_manager = FontManager(self)
        
        # 套用外部樣式表
        self.load_stylesheet()
        
        # 初始化 UI
        self.initUI()
        
        # 套用用戶字體偏好
        self.font_manager.apply_font_scale(self.font_manager.current_scale)
        
        # 填充範例資料
        self.populate_sample_data()
        
        # 連接信號
        self.connect_signals()

    def load_stylesheet_with_zoom(self, dynamic_css=""):
        """載入樣式表並套用動態縮放CSS"""
        try:
            with open(STYLE_SHEET_PATH, "r", encoding="utf-8") as f:
                base_css = f.read()
                
            # 處理勾選框圖示路徑 (現有邏輯)
            base_css = base_css.replace("QCheckBox::indicator:unchecked {", 
                                     """QCheckBox::indicator:unchecked {
                                         image: url(assets/icons/square.svg);""")
            base_css = base_css.replace("QCheckBox::indicator:checked {", 
                                     """QCheckBox::indicator:checked {
                                         image: url(assets/icons/check-square.svg);""")
            base_css = base_css.replace("QCheckBox::indicator:partially-checked {", 
                                     """QCheckBox::indicator:indeterminate {
                                         image: url(assets/icons/minus-square.svg);""")
            
            # 合併動態CSS
            combined_css = base_css + dynamic_css
            self.setStyleSheet(combined_css)
            
        except FileNotFoundError:
            print(f"警告: {STYLE_SHEET_PATH} 未找到，使用預設樣式。")

    def connect_signals(self):
        """連接所有信號和槽"""
        # ... 現有信號連接 ...
        
        # === 新增：字體縮放信號 ===
        self.zoom_in_btn.clicked.connect(self.font_manager.increase_font_size)
        self.zoom_out_btn.clicked.connect(self.font_manager.decrease_font_size)
        self.reset_zoom_btn.clicked.connect(self.font_manager.reset_font_size)
```

### **Phase 3: 設定持久化優化 (30分鐘)**

#### **Step 3.1: 設定檔案結構**
```json
// data/user_preferences.json - 目標格式
{
  "font_scale": 1.25,
  "window_geometry": {
    "width": 1250,
    "height": 750,
    "x": 100,
    "y": 100
  },
  "last_output_dir": "C:/Users/username/Documents",
  "version": "1.0"
}
```

#### **Step 3.2: 設定管理增強**
```python
# ui/font_manager.py - 增強設定管理
class FontManager:
    def get_preferences_file_path(self):
        """取得偏好設定檔案路徑"""
        return os.path.join("data", "user_preferences.json")
        
    def ensure_data_directory(self):
        """確保data目錄存在"""
        data_dir = "data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            self.logger.info(f"建立設定目錄: {data_dir}")
            
    def validate_scale_value(self, scale):
        """驗證縮放值的有效性"""
        if not isinstance(scale, (int, float)):
            return False
        return self.min_scale <= scale <= self.max_scale
```

### **Phase 4: UI打磨和測試 (30分鐘)**

#### **Step 4.1: 狀態更新優化**
```python
# ui/main_window.py - 狀態回報
def update_status(self, message):
    """更新狀態列訊息"""
    if hasattr(self, 'status_label'):
        self.status_label.setText(message)

# 在相關操作中加入狀態更新
def generate_pdf(self, output_path, test_title, _, rounds, questions_per_round):
    """生成 PDF 測驗檔案"""
    self.update_status("正在生成PDF...")
    
    # ... 現有代碼 ...
    
    if success:
        self.update_status("PDF生成完成")
        # ...
    else:
        self.update_status("PDF生成失敗")
```

#### **Step 4.2: 工具提示增強**
```python
def create_zoom_controls(self):
    # ... 現有代碼 ...
    
    # 增強工具提示
    self.zoom_out_btn.setToolTip("縮小字體\n目前可用範圍: 50%-200%")
    self.zoom_in_btn.setToolTip("放大字體\n目前可用範圍: 50%-200%")
    self.reset_zoom_btn.setToolTip("重置為預設字體大小 (100%)")
    
    # 字體大小標籤工具提示
    self.font_size_label.setToolTip("目前字體縮放比例\n點擊可重置為100%")
    
    # 讓字體標籤可點擊重置
    from PyQt5.QtCore import pyqtSignal
    from PyQt5.QtWidgets import QLabel
    
    class ClickableLabel(QLabel):
        clicked = pyqtSignal()
        def mousePressEvent(self, event):
            self.clicked.emit()
            super().mousePressEvent(event)
    
    # 替換為可點擊標籤 (在create_zoom_controls中)
    self.font_size_label = ClickableLabel("100%")
    # ... 其他設定 ...
    self.font_size_label.clicked.connect(self.font_manager.reset_font_size)
```

---

## 🧪 **測試計畫**

### **測試項目**

| 測試項目 | 驗證重點 | 通過標準 |
|----------|----------|----------|
| **基礎功能** | 縮放按鈕正常工作 | 點擊有反應，字體確實變化 |
| **範圍限制** | 50%-200%範圍控制 | 不能超出範圍，按鈕正確停用 |
| **UI響應** | 所有元件同步縮放 | 標題、按鈕、輸入框等統一縮放 |
| **設定持久化** | 重啟後記住設定 | 關閉重開應用程式，字體大小不變 |
| **狀態顯示** | 百分比正確顯示 | 標籤顯示的百分比與實際縮放一致 |

### **測試腳本**
```python
# tests/test_font_scaling.py
def test_font_scaling_basic():
    """測試基礎字體縮放功能"""
    app = QApplication([])
    window = MathTestGenerator()
    
    # 測試放大
    initial_scale = window.font_manager.current_scale
    window.font_manager.increase_font_size()
    assert window.font_manager.current_scale > initial_scale
    
    # 測試縮小
    window.font_manager.decrease_font_size()
    assert window.font_manager.current_scale == initial_scale
    
    # 測試重置
    window.font_manager.apply_font_scale(1.5)
    window.font_manager.reset_font_size()
    assert window.font_manager.current_scale == 1.0

def test_font_preferences_persistence():
    """測試字體偏好設定持久化"""
    # 設定特定縮放比例
    app = QApplication([])
    window1 = MathTestGenerator()
    window1.font_manager.apply_font_scale(1.25)
    
    # 模擬重啟 - 建立新視窗
    window2 = MathTestGenerator()
    assert window2.font_manager.current_scale == 1.25
```

---

## ⚠️ **風險評估與緩解**

### **潛在風險**

| 風險 | 影響程度 | 發生機率 | 緩解措施 |
|------|----------|----------|----------|
| **CSS樣式衝突** | 中 | 中 | 使用CSS優先級，充分測試 |
| **效能影響** | 低 | 低 | 限制縮放範圍，避免過度運算 |
| **設定檔損壞** | 低 | 低 | 異常處理，自動重建預設設定 |
| **UI佈局破壞** | 中 | 低 | 限制縮放範圍，測試極端情況 |

### **回退計畫**
1. **CSS載入失敗**: 自動降級到原始樣式表
2. **設定檔問題**: 重建為預設設定，記錄錯誤
3. **縮放異常**: 自動重置為100%，禁用縮放功能

---

## 📅 **實施時程**

### **預估時程**
- **Phase 1**: 45分鐘 - 狀態列基礎架構
- **Phase 2**: 1小時 - 字體縮放核心邏輯  
- **Phase 3**: 30分鐘 - 設定持久化優化
- **Phase 4**: 30分鐘 - UI打磨和測試

**總計**: **2.5小時**

### **里程碑檢查點**
- [ ] Phase 1完成：狀態列顯示，按鈕可點擊
- [ ] Phase 2完成：字體可正常縮放，範圍控制正確
- [ ] Phase 3完成：設定可儲存和載入
- [ ] Phase 4完成：所有測試通過，UI體驗良好

### **完成標準**
- ✅ 字體縮放功能完全正常
- ✅ UI響應流暢，無明顯延遲
- ✅ 設定持久化穩定運作
- ✅ 所有測試項目通過
- ✅ 無回歸問題

---

## 📚 **相關檔案**

### **需要修改的檔案**
- `ui/main_window.py` - 主視窗增加狀態列和縮放控制
- `assets/style.qss` - 新增狀態列樣式
- `data/user_preferences.json` - 用戶偏好設定 (新建)

### **需要新建的檔案**
- `ui/font_manager.py` - 字體縮放管理器
- `tests/test_font_scaling.py` - 字體縮放測試 (可選)

### **相關資源**
- `assets/icons/zoom-in.svg` - 放大圖示 (已存在)
- `assets/icons/zoom-out.svg` - 縮小圖示 (已存在)

---

---

## 📊 **實施進度**

### **✅ Phase 1: 狀態列基礎架構 - 已完成** 
**實施時間**: 35分鐘 (預估45分鐘)  
**完成日期**: 2025-09-11 09:48

#### **實施成果**
1. **✅ 主視窗佈局修改**
   - 在 `ui/main_window.py` 第242行成功添加 `create_status_bar()` 調用
   - 狀態列正確顯示在主視窗底部

2. **✅ 字體縮放控制UI元件**
   - 縮小按鈕：使用 `zoom-out.svg` 圖示，24x24px
   - 放大按鈕：使用 `zoom-in.svg` 圖示，24x24px  
   - 百分比標籤：顯示當前縮放比例，預設100%
   - 重置按鈕：文字按鈕，最大寬度40px
   - 所有按鈕使用 `iconButton` 樣式

3. **✅ 狀態列專用樣式**
   - 添加到 `assets/style.qss` 第217-248行
   - 邊框、背景色、字體大小、hover效果完整定義
   - 與現有UI樣式風格一致

4. **✅ 基礎功能測試**
   - 應用程式正常啟動，無報錯或警告
   - UI載入完成，狀態列正確顯示
   - 按鈕點擊測試機制已設置（臨時）

#### **程式碼修改記錄**
```diff
# ui/main_window.py
+ def create_status_bar(self):
+ def create_zoom_controls(self):  
+ def update_status(self, message):
+ # 臨時測試按鈕響應機制

# assets/style.qss  
+ /* 狀態列樣式 */ (32行新增樣式定義)
```

#### **驗證結果**
- ✅ 狀態列正確顯示在視窗底部
- ✅ 縮放控制按鈕排列整齊，圖示載入正常
- ✅ 工具提示正確顯示
- ✅ 樣式與整體UI風格統一
- ✅ 無回歸問題，原有功能正常

### **✅ Phase 2: 字體縮放核心邏輯 - 已完成**
**實施時間**: 25分鐘 (預估1小時)  
**完成日期**: 2025-09-11 13:06

#### **實施成果**
1. **✅ 字體管理器建立**
   - 建立 `ui/font_manager.py` 完整功能類別
   - 支援 50%-200% 字體縮放範圍 (8個步驟)
   - 動態CSS生成系統完成

2. **✅ 主視窗整合**
   - `ui/main_window.py` 成功導入 FontManager
   - 新增 `load_stylesheet_with_zoom()` 方法
   - 初始化時自動套用用戶偏好

3. **✅ 按鈕信號連接**
   - 放大、縮小、重置按鈕功能完整
   - 按鈕狀態管理 (邊界禁用)
   - 即時百分比顯示更新

4. **✅ 設定持久化**
   - JSON格式用戶偏好儲存
   - 自動建立 `data/user_preferences.json`
   - 啟動時載入儲存的縮放設定

#### **測試驗證**
- ✅ 應用程式正常啟動，FontManager初始化成功
- ✅ 偏好設定檔案正確載入 (測試125%縮放)
- ✅ 日誌顯示 "字體縮放已套用: 125%" 
- ✅ 無錯誤或異常，系統穩定運行

### **✅ Phase 3: 設定持久化優化 - 已完成**
**實施時間**: 15分鐘 (預估30分鐘)  
**完成日期**: 2025-09-11 13:13

#### **實施成果**
1. **✅ 設定檔案結構增強**
   - 新增 `get_preferences_file_path()` 統一路徑管理
   - 新增 `ensure_data_directory()` 確保目錄存在
   - 新增 `get_default_preferences()` 完整預設設定結構

2. **✅ 輸入驗證機制**
   - 新增 `validate_scale_value()` 嚴格數值驗證
   - 改善 `apply_font_scale()` 輸入檢查
   - 新增 `reset_preferences_to_default()` 重置功能

3. **✅ 錯誤處理優化**
   - 全面try-catch錯誤處理，防止崩潰
   - 分層錯誤處理：WARNING用於非致命錯誤
   - 自動修復機制：無效設定自動重建為預設值

4. **✅ 穩定性測試通過**
   - **✅ 無設定檔**: 自動建立完整預設設定
   - **✅ 損壞檔案**: 正確識別並修復無效值
   - **✅ 錯誤恢復**: "invalid_value" → 警告 → 自動修正為1.0

### **✅ Phase 4: UI打磨和測試 - 已完成**
**實施時間**: 20分鐘 (預估30分鐘)  
**完成日期**: 2025-09-11 13:18

#### **實施成果**
1. **✅ 狀態更新優化**
   - 新增 `update_font_operation_status()` 專用字體操作回饋
   - 智能操作判斷：放大/縮小/重置/載入
   - FontManager整合狀態通知機制

2. **✅ 工具提示增強**
   - 詳細縮放範圍說明：50%-200%
   - 完整步驟顯示：50%, 75%, 90%, 100%, 110%, 125%, 150%, 200%
   - 互動式提示：標籤點擊重置說明

3. **✅ 可點擊標籤功能**
   - 建立 `ClickableLabel` 類別，支援點擊事件
   - 視覺回饋：滑鼠懸停變色效果 (#3498db)
   - 連接重置功能：標籤點擊直接重置為100%

4. **✅ 綜合測試通過**
   - **✅ 組件存在性**: 所有UI元件正確建立
   - **✅ 功能測試**: 放大(150%→200%)、縮小(200%→150%)、重置(→100%)
   - **✅ 狀態回饋**: "載入字體偏好設定: 150%" 正確顯示
   - **✅ 持久化**: 設定正確儲存和載入

### **🎉 專案完成**
字體縮放控制功能已全面實現並通過測試。

---

**建立日期**: 2025-09-11  
**負責人**: Claude Code Assistant  
**狀態**: **✅ 專案完成 - 所有階段均已實施完成**  
**優先級**: 中等 (UI體驗改善)