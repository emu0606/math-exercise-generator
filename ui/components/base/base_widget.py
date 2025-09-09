#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - UI 組件基礎類別

定義所有 UI 組件的抽象基類，建立統一的組件開發標準。
整合新架構核心工具，提供完整的日誌、配置和事件管理能力。
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal

from utils import get_logger, global_config

class BaseWidget(QWidget, ABC):
    """
    UI 組件抽象基類
    
    所有自定義 UI 組件都應繼承此基類，提供統一的初始化流程、
    配置管理、日誌記錄和錯誤處理能力。
    
    設計模式：Template Method Pattern
    - 定義標準化的初始化流程
    - 子類實現具體的UI建置和信號連接邏輯
    - 提供統一的生命週期管理
    
    Attributes:
        logger: 組件專用日誌記錄器
        config: 組件配置字典
        widget_initialized: 組件初始化完成信號
        widget_error: 組件錯誤信號
        
    Example:
        >>> class SearchBox(BaseWidget):
        ...     def _setup_ui(self):
        ...         self.line_edit = QLineEdit()
        ...         layout = QHBoxLayout(self)
        ...         layout.addWidget(self.line_edit)
        ...     
        ...     def _connect_signals(self):
        ...         self.line_edit.textChanged.connect(self._on_text_changed)
        ...         
        ...     def _on_text_changed(self, text):
        ...         self.logger.debug(f"搜尋文字變更: {text}")
    """
    
    # 標準信號定義
    widget_initialized = pyqtSignal()
    widget_error = pyqtSignal(str)
    
    def __init__(self, parent: Optional[QWidget] = None, config: Optional[Dict[str, Any]] = None):
        """
        初始化 UI 組件基類
        
        Args:
            parent: 父組件
            config: 組件配置字典，會與全域配置合併
            
        Raises:
            RuntimeError: 當組件初始化失敗時
        """
        super().__init__(parent)
        
        # 初始化新架構工具
        self.logger = get_logger(f"ui.{self.__class__.__name__}")
        self.config = self._merge_config(config or {})
        
        try:
            # 標準化初始化流程
            self._apply_theme()
            self._setup_ui()
            self._connect_signals()
            
            self.logger.info(f"{self.__class__.__name__} 初始化完成")
            self.widget_initialized.emit()
            
        except Exception as e:
            error_msg = f"{self.__class__.__name__} 初始化失敗: {e}"
            self.logger.error(error_msg)
            self.widget_error.emit(error_msg)
            raise RuntimeError(error_msg) from e
    
    def _merge_config(self, local_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        合併本地配置和全域配置
        
        Args:
            local_config: 本地配置字典
            
        Returns:
            合併後的配置字典
        """
        try:
            # 獲取全域UI配置
            global_ui_config = global_config.get('ui', {})
            widget_config = global_ui_config.get(self.__class__.__name__.lower(), {})
            
            # 合併配置: 本地配置優先
            merged_config = {}
            merged_config.update(widget_config)
            merged_config.update(local_config)
            
            self.logger.debug(f"配置合併完成: {len(merged_config)} 個配置項")
            return merged_config
            
        except Exception as e:
            self.logger.warning(f"配置合併失敗，使用本地配置: {e}")
            return local_config
    
    def _apply_theme(self) -> None:
        """
        應用主題樣式
        
        從全域配置讀取主題設定並應用到組件上。
        子類可重寫此方法實現自定義主題邏輯。
        """
        try:
            theme = self.config.get('theme', 'light')
            if hasattr(self, 'setObjectName'):
                self.setObjectName(f"{self.__class__.__name__}_{theme}")
            self.logger.debug(f"主題應用完成: {theme}")
        except Exception as e:
            self.logger.warning(f"主題應用失敗: {e}")
    
    @abstractmethod
    def _setup_ui(self) -> None:
        """
        建置組件UI
        
        子類必須實現此方法，定義組件的UI結構和佈局。
        此方法在初始化流程中被調用，應包含所有UI元素的創建。
        
        Example:
            def _setup_ui(self):
                self.button = QPushButton("Click Me")
                layout = QVBoxLayout(self)
                layout.addWidget(self.button)
        """
        pass
    
    @abstractmethod  
    def _connect_signals(self) -> None:
        """
        連接組件信號
        
        子類必須實現此方法，定義組件內部和對外的信號連接。
        此方法在UI建置完成後被調用。
        
        Example:
            def _connect_signals(self):
                self.button.clicked.connect(self._on_button_clicked)
                self.my_signal.connect(self.parent().on_child_signal)
        """
        pass
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """
        獲取配置值
        
        Args:
            key: 配置鍵名，支援點號分隔的嵌套鍵
            default: 預設值
            
        Returns:
            配置值或預設值
            
        Example:
            >>> value = widget.get_config_value('search.max_results', 50)
        """
        try:
            keys = key.split('.')
            value = self.config
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            self.logger.debug(f"配置鍵 '{key}' 不存在，使用預設值: {default}")
            return default
    
    def set_config_value(self, key: str, value: Any) -> None:
        """
        設定配置值
        
        Args:
            key: 配置鍵名，支援點號分隔的嵌套鍵
            value: 配置值
            
        Example:
            >>> widget.set_config_value('search.enabled', True)
        """
        try:
            keys = key.split('.')
            config = self.config
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            config[keys[-1]] = value
            self.logger.debug(f"配置已更新: {key} = {value}")
        except Exception as e:
            self.logger.error(f"設定配置失敗: {key} = {value}, 錯誤: {e}")
    
    def cleanup(self) -> None:
        """
        清理組件資源
        
        在組件銷毀前調用，用於清理資源、斷開連接等。
        子類可重寫此方法實現自定義清理邏輯。
        """
        try:
            self.logger.info(f"{self.__class__.__name__} 清理完成")
        except Exception as e:
            self.logger.error(f"組件清理失敗: {e}")