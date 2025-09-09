# Debug與打磨階段 - 問題修復計畫

> **計畫目標**: 系統性修復Debug階段發現的問題  
> **實施日期**: 2025-09-09  
> **階段**: Debug與打磨階段  
> **優先級**: 高

## 🏆 **已完成的修復**

### **✅ PDF生成模組導入錯誤** 
**問題**: `No module named 'utils.pdf_generator'`  
**原因**: 重構後模組路徑未更新  
**修復**: 更正 `pdf_orchestrator.py` 中的導入路徑  
**狀態**: 已解決 ✅

### **✅ Registry方法名稱錯誤**
**問題**: `'GeneratorRegistry' object has no attribute 'is_registered'`  
**原因**: 調用了不存在的方法名稱  
**修復**: 將 `is_registered()` 改為 `has_generator()`  
**狀態**: 需要重新修復 ⚠️

---

## 🚨 **當前待修復問題**

### **📋 PDF生成數據格式不匹配**

#### **問題描述**
PDF生成流程中，UI傳遞的 `topic` 格式與Registry系統期望的格式不匹配：

**UI實際格式**: 
```json
{"topic": "代數 - 重根式的化簡", "count": 5}
```

**Registry期望格式**:
```python
registry.has_generator("代數", "重根式的化簡")  # 需要分離的category和subcategory
```

#### **流程分析**
1. **UI層**: `category_widget.get_selected_data()` → `"代數 - 重根式的化簡"`
2. **傳遞**: `main_window.generate_pdf()` → `selected_data`
3. **協調器**: `PDFOrchestrator.generate_pdfs()` → 接收數據
4. **問題點**: `question_distributor.py` → 無法正確解析topic格式

#### **根本原因**
```python
# question_distributor.py 第575行 (UI層)
topic_name = f"{parent_cb.text()} - {sub_cb.text()}"  # "代數 - 重根式的化簡"

# question_distributor.py 第110-137行 (處理層)  
if '/' in topic:  # ❌ 錯誤：尋找'/'分隔符
    category, subcategory = topic.split('/', 1)
# 應該是:
if ' - ' in topic:  # ✅ 正確：尋找' - '分隔符
    category, subcategory = topic.split(' - ', 1)
```

#### **修復計畫**
1. **更正分隔符解析**: 將 `'/'` 改為 `' - '`
2. **驗證數據格式**: 確認UI與Registry的數據對接
3. **測試完整流程**: 從UI按鈕到PDF生成

---

## 📋 **計畫概述**

### **背景**
當前UI字體大小固定在 `assets/style.qss` 中定義，未能響應Windows系統的字體縮放設定，在高DPI顯示器或系統字體放大設定下可能顯示過小。

### **目標**
- ✅ UI字體自動適應Windows系統DPI設定
- ✅ 保持UI元件比例協調
- ✅ 無需用戶手動配置
- ✅ 向後兼容現有字體設定

### **範圍**
- **包含**: PyQt5 UI元件字體大小調整
- **不包含**: PDF生成字體、LaTeX渲染字體、用戶自定義字體選項

---

## 🚀 **Phase 1: DPI感知設定 (優先實施)**

### **實施策略**
使用PyQt5內建的高DPI支援機制，讓系統自動處理字體縮放。

### **技術實施**

#### **Step 1.1: 修改 main.py**
```python
# 在 main.py 開頭加入 (第15行左右)
if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import Qt
    
    # === 新增: DPI感知設定 ===
    # 啟用高DPI支援 (必須在QApplication創建前)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # 創建應用程式
    app = QApplication(sys.argv)
    
    # === 新增: 字體DPI感知策略 ===
    # 設定縮放因子處理策略
    app.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # 現有的字體載入代碼...
    font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets/fonts")
    # ...其餘不變
```

#### **Step 1.2: 驗證設定**
```python
# 在 main.py 中加入調試資訊 (可選，完成後移除)
def log_dpi_info():
    """記錄DPI資訊用於調試"""
    from utils import get_logger
    logger = get_logger(__name__)
    
    screen = app.primaryScreen()
    dpr = screen.devicePixelRatio()
    logical_dpi = screen.logicalDotsPerInch()
    physical_dpi = screen.physicalDotsPerInch()
    
    logger.info(f"DPI資訊 - 設備像素比: {dpr}, 邏輯DPI: {logical_dpi}, 物理DPI: {physical_dpi}")

# 在應用程式創建後調用 (調試用)
log_dpi_info()
```

### **預期效果**
- 在Windows縮放125%時，UI元件自動放大25%
- 在Windows縮放150%時，UI元件自動放大50%
- 字體清晰度保持最佳狀態

### **測試驗證**
1. **標準DPI (100%)**: 確認UI正常顯示，無回歸問題
2. **放大DPI (125%, 150%, 200%)**: 確認UI元件等比例縮放
3. **多螢幕**: 驗證不同DPI螢幕間的表現

---

## 🔄 **Phase 2: 動態字體縮放 (備選方案)**

### **觸發條件**
如果Phase 1實施後發現以下問題，則啟動Phase 2：
- UI元件縮放不均勻
- 字體模糊或像素化
- 特定Windows版本兼容性問題

### **實施策略**
程式化讀取Windows字體設定，動態調整QSS樣式表。

### **技術實施**

#### **Step 2.1: 建立字體管理模組**
```python
# 建立 ui/font_manager.py
import winreg
from PyQt5.QtWidgets import QApplication
from utils import get_logger

logger = get_logger(__name__)

class FontManager:
    """Windows字體設定管理器"""
    
    def __init__(self):
        self.base_font_sizes = {
            'widget': 12,
            'title': 16, 
            'button': 14
        }
    
    def get_windows_font_scale(self) -> float:
        """獲取Windows系統字體縮放比例"""
        try:
            # 方法1: 讀取DPI設定
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                               r"Control Panel\Desktop")
            dpi_value, _ = winreg.QueryValueEx(key, "LogPixels")
            winreg.CloseKey(key)
            scale = dpi_value / 96.0  # 96 DPI = 100%
            
            logger.info(f"Windows字體縮放比例: {scale}")
            return scale
            
        except Exception as e:
            logger.warning(f"無法讀取Windows字體設定: {e}")
            # 備用方法: 使用PyQt5檢測
            screen = QApplication.primaryScreen()
            return screen.devicePixelRatio()
    
    def generate_scaled_qss(self) -> str:
        """生成縮放後的QSS樣式"""
        scale = self.get_windows_font_scale()
        
        return f"""
        QWidget {{
            font-size: {int(self.base_font_sizes['widget'] * scale)}px;
        }}
        
        QLabel#title {{
            font-size: {int(self.base_font_sizes['title'] * scale)}px;
        }}
        
        QPushButton#generateBtn {{
            font-size: {int(self.base_font_sizes['button'] * scale)}px;
        }}
        """
```

#### **Step 2.2: 整合到主視窗**
```python
# 修改 ui/main_window.py 的 load_stylesheet 方法
def load_stylesheet(self):
    """載入並套用樣式表"""
    try:
        # 讀取基礎樣式表
        with open(STYLE_SHEET_PATH, "r", encoding="utf-8") as f:
            base_css = f.read()
        
        # === Phase 2: 動態字體縮放 ===
        from ui.font_manager import FontManager
        font_manager = FontManager()
        scaled_css = font_manager.generate_scaled_qss()
        
        # 合併樣式表
        combined_css = base_css + "\n" + scaled_css
        
        # 應用樣式
        self.setStyleSheet(combined_css)
        
    except Exception as e:
        logger.error(f"載入樣式表失敗: {e}")
        # 降級到原有實作
        # ...原有代碼
```

### **測試驗證**
1. **註冊表讀取**: 確認能正確讀取Windows DPI設定
2. **動態縮放**: 驗證不同縮放比例下的字體大小
3. **錯誤處理**: 確認讀取失敗時的降級行為

---

## 🧪 **測試計畫**

### **測試環境**
- **Windows版本**: Windows 10/11 各版本
- **顯示器**: 標準DPI、高DPI顯示器
- **縮放設定**: 100%, 125%, 150%, 200%

### **測試項目**

| 測試項目 | 驗證重點 | 通過標準 |
|----------|----------|----------|
| **基礎功能** | 應用程式正常啟動 | 無錯誤訊息 |
| **100% DPI** | UI顯示正常 | 與目前版本相同 |
| **125% DPI** | 字體放大25% | 清晰可讀，無模糊 |
| **150% DPI** | 字體放大50% | 比例協調 |
| **200% DPI** | 字體放大100% | 不超出視窗邊界 |
| **多螢幕** | 跨螢幕拖拽 | 自動適應不同DPI |

### **驗證方法**
```python
# 測試腳本: tests/test_font_scaling.py
def test_font_scaling():
    """測試字體縮放功能"""
    app = QApplication([])
    
    # 模擬不同DPI設定
    test_dpis = [96, 120, 144, 192]  # 100%, 125%, 150%, 200%
    
    for dpi in test_dpis:
        # 設定測試環境
        window = MathTestGenerator()
        window.show()
        
        # 驗證字體大小
        widget = window.findChild(QWidget)
        font = widget.font()
        expected_size = 12 * (dpi / 96)
        
        assert abs(font.pointSize() - expected_size) < 1
```

---

## ⚠️ **風險評估與緩解**

### **潛在風險**

| 風險 | 影響程度 | 發生機率 | 緩解措施 |
|------|----------|----------|----------|
| **DPI設定失效** | 中 | 低 | 提供Phase 2備選方案 |
| **字體模糊** | 中 | 中 | 調整縮放策略 |
| **視窗佈局破壞** | 高 | 低 | 充分測試，提供回退機制 |
| **性能影響** | 低 | 低 | 監控啟動時間 |

### **回退計畫**
如果實施後出現嚴重問題：
1. **立即回退**: 移除DPI設定代碼
2. **降級方案**: 使用固定字體大小
3. **問題修復**: 根據日誌分析具體原因

---

## 📅 **實施時程**

### **Phase 1 (預計1-2小時)**
- [ ] 修改 `main.py` 加入DPI感知設定
- [ ] 基礎功能測試
- [ ] 多DPI環境驗證
- [ ] 性能回歸測試

### **Phase 2 (如需要，預計2-3小時)**
- [ ] 實作 `ui/font_manager.py`
- [ ] 整合到主視窗載入流程
- [ ] 進階測試驗證
- [ ] 文檔更新

### **完成標準**
- ✅ 所有測試項目通過
- ✅ 無性能回歸
- ✅ 代碼審查完成
- ✅ 更新相關文檔

---

## 📚 **參考資料**

### **技術文檔**
- [Qt High DPI Documentation](https://doc.qt.io/qt-5/highdpi.html)
- [Windows DPI Registry Settings](https://docs.microsoft.com/en-us/windows/win32/hidpi/)

### **相關檔案**
- `main.py` - 應用程式入口點
- `assets/style.qss` - UI樣式表
- `ui/main_window.py` - 主視窗類別

---

**建立日期**: 2025-09-08  
**負責人**: Claude Code Assistant  
**狀態**: 待實施