#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
編碼安全的 Python UTF-8 設置檢查
"""

import sys
import os

def safe_print(text):
    """編碼安全的打印函數"""
    try:
        print(text)
    except UnicodeEncodeError:
        safe_text = text.encode('ascii', errors='replace').decode('ascii')
        print(safe_text)

def check_encoding():
    safe_print("=== Python UTF-8 編碼檢查 ===")
    safe_print(f"Python 版本: {sys.version}")
    safe_print(f"平台: {sys.platform}")
    safe_print("")
    
    safe_print("=== 編碼設置 ===")
    safe_print(f"stdout 編碼: {sys.stdout.encoding}")
    safe_print(f"stderr 編碼: {sys.stderr.encoding}")
    safe_print(f"文件系統編碼: {sys.getfilesystemencoding()}")
    safe_print(f"預設編碼: {sys.getdefaultencoding()}")
    safe_print("")
    
    safe_print("=== 環境變數 ===")
    safe_print(f"PYTHONIOENCODING: {os.environ.get('PYTHONIOENCODING', '未設置')}")
    safe_print(f"PYTHONUTF8: {os.environ.get('PYTHONUTF8', '未設置')}")
    safe_print("")
    
    safe_print("=== UTF-8 測試 ===")
    try:
        test_chars = "繁體中文 UTF-8 測試"
        safe_print(f"UTF-8 字符測試: {test_chars}")
        utf8_ok = True
    except UnicodeEncodeError as e:
        safe_print(f"UTF-8 編碼錯誤: {e}")
        utf8_ok = False
    
    safe_print("")
    safe_print("=== 結果 ===")
    stdout_ok = sys.stdout.encoding.lower() == 'utf-8'
    env_ok = (os.environ.get('PYTHONIOENCODING') == 'utf-8' and 
              os.environ.get('PYTHONUTF8') == '1')
    
    safe_print(f"stdout 編碼正確: {'OK' if stdout_ok else 'FAIL'}")
    safe_print(f"環境變數正確: {'OK' if env_ok else 'FAIL'}")  
    safe_print(f"UTF-8 輸出正常: {'OK' if utf8_ok else 'FAIL'}")
    
    all_ok = stdout_ok and utf8_ok
    safe_print(f"\n總體狀態: {'所有編碼設置正確！' if all_ok else '需要修復編碼設置'}")
    
    if not all_ok:
        safe_print("\n修復建議:")
        if not env_ok:
            safe_print("  1. 運行 setup_permanent_utf8.bat 設置環境變數")
        if not stdout_ok:
            safe_print("  2. 重啟命令提示符或 IDE")
        if not utf8_ok:
            safe_print("  3. 檢查控制台是否支援 UTF-8")
    
    return all_ok

if __name__ == "__main__":
    success = check_encoding()
    sys.exit(0 if success else 1)