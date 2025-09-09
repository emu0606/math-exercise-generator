#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - UI 工具函數
"""

import os
from PyQt5.QtGui import QIcon

# --- 常數定義 ---
ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'assets')
ICON_DIR = os.path.join(ASSETS_DIR, 'icons')

def load_icon(filename):
    """載入圖示的輔助函數
    
    Args:
        filename (str): 圖示檔案名稱，例如 'search.svg'
        
    Returns:
        QIcon: 載入的圖示物件，如果檔案不存在則返回空圖示
    """
    path = os.path.join(ICON_DIR, filename)
    if not os.path.exists(path):
        print(f"警告: 圖示檔案未找到，路徑: {path}")
        return QIcon()
    return QIcon(path)
