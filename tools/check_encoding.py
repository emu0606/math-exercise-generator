#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
檢查 Python UTF-8 編碼設置是否正確
"""

import sys
import os

def check_encoding():
    print("=== Python UTF-8 編碼檢查 ===")
    print(f"Python 版本: {sys.version}")
    print(f"平台: {sys.platform}")
    print()
    
    print("=== 編碼設置 ===")
    print(f"stdout 編碼: {sys.stdout.encoding}")
    print(f"stderr 編碼: {sys.stderr.encoding}")
    print(f"文件系統編碼: {sys.getfilesystemencoding()}")
    print(f"預設編碼: {sys.getdefaultencoding()}")
    print()
    
    print("=== 環境變數 ===")
    print(f"PYTHONIOENCODING: {os.environ.get('PYTHONIOENCODING', '未設置')}")
    print(f"PYTHONUTF8: {os.environ.get('PYTHONUTF8', '未設置')}")
    print()
    
    print("=== UTF-8 測試 ===")
    try:
        test_chars = "繁體中文 UTF-8 測試：✓ ❌ 🎉"
        print(f"UTF-8 字符測試: {test_chars}")
        utf8_ok = True
    except UnicodeEncodeError as e:
        print(f"UTF-8 編碼錯誤: {e}")
        utf8_ok = False
    
    print()
    print("=== 結果 ===")
    stdout_ok = sys.stdout.encoding.lower() == 'utf-8'
    env_ok = (os.environ.get('PYTHONIOENCODING') == 'utf-8' and 
              os.environ.get('PYTHONUTF8') == '1')
    
    print(f"stdout 編碼正確: {'✓' if stdout_ok else '✗'}")
    print(f"環境變數正確: {'✓' if env_ok else '✗'}")  
    print(f"UTF-8 輸出正常: {'✓' if utf8_ok else '✗'}")
    
    all_ok = stdout_ok and utf8_ok
    print(f"\n總體狀態: {'所有編碼設置正確！' if all_ok else '需要修復編碼設置'}")
    
    if not all_ok:
        print("\n修復建議:")
        if not env_ok:
            print("  1. 運行 setup_permanent_utf8.bat 設置環境變數")
        if not stdout_ok:
            print("  2. 重啟命令提示符或 IDE")
        if not utf8_ok:
            print("  3. 檢查控制台是否支援 UTF-8")
    
    return all_ok

if __name__ == "__main__":
    success = check_encoding()
    sys.exit(0 if success else 1)