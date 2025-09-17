#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 主程式
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QFile, QTextStream
from ui.main_window import MathTestGenerator

# 導入生成器模組，這將自動註冊所有生成器
import generators

def main():
    """主程式入口點"""
    # 創建應用程式
    app = QApplication(sys.argv)
    
    # 設置應用程式樣式（改用 open() 幫助除錯）
    try:
        with open("assets/style.qss", "r", encoding="utf-8") as f:
            qss = f.read()
            app.setStyleSheet(qss)
    except Exception as e:
        print("❌ 載入樣式表失敗:", e)
    
    # 設置字體目錄
    font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets/fonts")
    if os.path.exists(font_dir):
        from PyQt5.QtGui import QFontDatabase
        for font_file in os.listdir(font_dir):
            if font_file.endswith(".ttf") or font_file.endswith(".otf"):
                font_path = os.path.join(font_dir, font_file)
                QFontDatabase.addApplicationFont(font_path)
    
    # 創建主視窗
    window = MathTestGenerator()
    window.show()
    
    # 執行應用程式
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
