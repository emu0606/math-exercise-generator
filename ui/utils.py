#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - UI 工具函數模組

本模組提供 UI 相關的通用工具函數，主要負責資源載入和介面
操作的輔助功能。使用現代化架構設計，整合日誌系統和配置管理。

主要功能：
- 圖示資源載入和管理
- 路徑處理和檔案系統操作
- UI 元件輔助工具函數
- 錯誤處理和資源回退機制

Example:
    >>> from ui.utils import load_icon
    >>> 
    >>> # 載入搜尋圖示
    >>> search_icon = load_icon('search.svg')
    >>> 
    >>> # 載入不存在的圖示會返回空圖示並記錄警告
    >>> missing_icon = load_icon('nonexistent.svg')
    >>> print(missing_icon.isNull())  # True

Note:
    所有圖示載入函數都包含完整的錯誤處理機制，確保UI不會
    因為缺失的資源檔案而崩潰。支援 SVG 和 PNG 格式的圖示。
"""

import os
from typing import Optional
from PyQt5.QtGui import QIcon

from utils import get_logger, global_config

logger = get_logger(__name__)

# --- 路徑配置 ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
ICON_DIR = os.path.join(ASSETS_DIR, 'icons')

logger.debug(f"UI 工具模組初始化 - 資源目錄: {ASSETS_DIR}")

def load_icon(filename: str) -> QIcon:
    """載入圖示檔案的工具函數
    
    支援 SVG 和 PNG 格式的圖示載入，具備完整的錯誤處理和
    資源回退機制。當指定圖示不存在時，會返回空圖示物件。
    
    Args:
        filename: 圖示檔案名稱，例如 'search.svg' 或 'icon.png'
        
    Returns:
        載入的圖示物件。如果檔案不存在則返回空的 QIcon 物件
        
    Raises:
        無 - 所有錯誤都會被處理並記錄到日誌
        
    Example:
        >>> # 載入標準圖示
        >>> icon = load_icon('search.svg')
        >>> button.setIcon(icon)
        >>> 
        >>> # 檢查圖示是否成功載入
        >>> if not icon.isNull():
        ...     print("圖示載入成功")
    """
    if not filename:
        logger.warning("圖示檔案名稱為空，返回空圖示")
        return QIcon()
    
    icon_path = os.path.join(ICON_DIR, filename)
    
    if not os.path.exists(icon_path):
        logger.warning(f"圖示檔案不存在: {icon_path}")
        return QIcon()
    
    try:
        icon = QIcon(icon_path)
        if icon.isNull():
            logger.warning(f"圖示載入失敗，可能格式不支援: {filename}")
        else:
            logger.debug(f"圖示載入成功: {filename}")
        return icon
        
    except Exception as e:
        logger.error(f"載入圖示時發生錯誤 {filename}: {e}")
        return QIcon()

def get_ui_theme() -> str:
    """獲取當前 UI 主題設定
    
    從全域配置中讀取 UI 主題設定，支援明亮和暗色主題。
    
    Returns:
        主題名稱，預設為 'light'
        
    Example:
        >>> theme = get_ui_theme()
        >>> if theme == 'dark':
        ...     apply_dark_theme()
    """
    try:
        theme = global_config.get('ui.theme', 'light')
        logger.debug(f"當前 UI 主題: {theme}")
        return theme
    except Exception as e:
        logger.warning(f"無法讀取 UI 主題設定，使用預設值: {e}")
        return 'light'

def validate_asset_directory() -> bool:
    """驗證資源目錄是否存在且可訪問
    
    檢查所有必需的資源目錄是否正確設置，用於應用程式
    啟動時的環境驗證。
    
    Returns:
        True 如果所有資源目錄都存在且可訪問，否則 False
        
    Example:
        >>> if not validate_asset_directory():
        ...     print("警告：部分UI資源可能無法正常載入")
    """
    directories_to_check = [ASSETS_DIR, ICON_DIR]
    
    for directory in directories_to_check:
        if not os.path.exists(directory):
            logger.error(f"資源目錄不存在: {directory}")
            return False
        if not os.access(directory, os.R_OK):
            logger.error(f"資源目錄無法訪問: {directory}")
            return False
    
    logger.info("所有UI資源目錄驗證通過")
    return True

# 模組初始化時驗證資源目錄
if not validate_asset_directory():
    logger.warning("UI資源目錄驗證失敗，部分功能可能受到影響")