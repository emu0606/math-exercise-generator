# 20250903 - Windows 環境 UTF-8 編碼解決方案

> **文檔類型**: 歷史檔案 - 技術設定指南  
> **創建時間**: 2025-09-03  
> **狀態**: 歷史參考文檔  
> **歸檔原因**: 編碼問題已解決，保留作為技術參考

## 問題說明
在 Windows cp950 環境下使用 UTF-8 繁體中文時，可能遇到編碼衝突問題。

## 解決方案

### 方案1: 環境變數設置（推薦）
```batch
# 在命令提示符中設置
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

# 然後運行 Python 腳本
py your_script.py
```

### 方案2: 使用提供的批次檔
```batch
# 運行測試
run_tests_utf8.bat

# 設置開發環境
set_encoding.bat
```

### 方案3: 程式碼中處理
```python
import sys
import io

# 強制 UTF-8 編碼
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# 或使用包裝器
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
```

## 驗證方法
```python
import sys
print('stdout encoding:', sys.stdout.encoding)
print('filesystem encoding:', sys.getfilesystemencoding())
```

期望輸出：
```
stdout encoding: utf-8
filesystem encoding: utf-8
```

## 文件說明
- `tests/test_integration/test_encoding_safe.py` - 編碼安全的測試腳本
- `run_tests_utf8.bat` - UTF-8 環境測試運行器
- `set_encoding.bat` - 開發環境編碼設置

## 最佳實踐
1. 始終在腳本開頭添加 `# -*- coding: utf-8 -*-`
2. 使用環境變數設置而不是程式碼修改
3. 測試時使用編碼安全的打印函數
4. 避免在輸出中使用特殊 Unicode 符號（✓ ❌ 🎉 等）

## 開發工具配置
### VS Code
```json
{
    "python.terminal.activateEnvironment": true,
    "terminal.integrated.env.windows": {
        "PYTHONIOENCODING": "utf-8",
        "PYTHONUTF8": "1"
    }
}
```

### PyCharm
File → Settings → Build, Execution, Deployment → Console → Python Console
Environment variables: 
- PYTHONIOENCODING=utf-8
- PYTHONUTF8=1