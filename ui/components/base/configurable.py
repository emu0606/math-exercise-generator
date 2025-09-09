#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 可配置UI組件基類

提供高級配置管理能力的UI組件基類，支援動態配置更新、
配置驗證和配置持久化等功能。
"""

from typing import Dict, Any, Callable, Optional
from PyQt5.QtCore import pyqtSignal

from .base_widget import BaseWidget

class ConfigurableWidget(BaseWidget):
    """
    可配置UI組件基類
    
    在BaseWidget基礎上添加高級配置管理功能，包括：
    - 配置變更監聽和自動更新
    - 配置驗證和錯誤處理
    - 配置持久化支援
    - 動態配置重載
    
    適用於需要複雜配置管理的組件，如設定面板、主題管理器等。
    
    Signals:
        config_changed: 配置變更時發出，包含變更的鍵和新值
        config_validation_failed: 配置驗證失敗時發出
        
    Example:
        >>> class ThemeSelector(ConfigurableWidget):
        ...     def _setup_ui(self):
        ...         self.combo = QComboBox()
        ...         # UI建置邏輯...
        ...         
        ...     def _validate_config(self, key, value):
        ...         if key == 'theme' and value not in ['light', 'dark']:
        ...             return False, "主題必須是 'light' 或 'dark'"
        ...         return True, None
        ...         
        ...     def _on_config_changed(self, key, old_value, new_value):
        ...         if key == 'theme':
        ...             self._apply_new_theme(new_value)
    """
    
    # 配置相關信號
    config_changed = pyqtSignal(str, object, object)  # key, old_value, new_value
    config_validation_failed = pyqtSignal(str, str)   # key, error_message
    
    def __init__(self, parent=None, config=None):
        """
        初始化可配置組件
        
        Args:
            parent: 父組件
            config: 初始配置字典
        """
        self._config_validators = {}  # 配置驗證器字典
        self._config_watchers = {}    # 配置監聽器字典
        
        super().__init__(parent, config)
    
    def add_config_validator(self, key: str, validator: Callable[[Any], tuple[bool, Optional[str]]]) -> None:
        """
        添加配置驗證器
        
        Args:
            key: 配置鍵名
            validator: 驗證函數，返回 (is_valid, error_message)
            
        Example:
            >>> def validate_max_items(value):
            ...     if not isinstance(value, int) or value <= 0:
            ...         return False, "最大項目數必須是正整數"
            ...     return True, None
            >>> 
            >>> widget.add_config_validator('max_items', validate_max_items)
        """
        self._config_validators[key] = validator
        self.logger.debug(f"已添加配置驗證器: {key}")
    
    def add_config_watcher(self, key: str, callback: Callable[[str, Any, Any], None]) -> None:
        """
        添加配置變更監聽器
        
        Args:
            key: 配置鍵名
            callback: 回調函數，參數為 (key, old_value, new_value)
            
        Example:
            >>> def on_theme_change(key, old, new):
            ...     print(f"主題從 {old} 變更為 {new}")
            >>> 
            >>> widget.add_config_watcher('theme', on_theme_change)
        """
        if key not in self._config_watchers:
            self._config_watchers[key] = []
        self._config_watchers[key].append(callback)
        self.logger.debug(f"已添加配置監聽器: {key}")
    
    def set_config_value(self, key: str, value: Any, validate: bool = True) -> bool:
        """
        設定配置值（重寫父類方法，添加驗證和監聽）
        
        Args:
            key: 配置鍵名
            value: 新值
            validate: 是否進行驗證
            
        Returns:
            設定是否成功
        """
        old_value = self.get_config_value(key)
        
        # 配置驗證
        if validate and key in self._config_validators:
            is_valid, error_msg = self._config_validators[key](value)
            if not is_valid:
                self.logger.warning(f"配置驗證失敗: {key} = {value}, 錯誤: {error_msg}")
                self.config_validation_failed.emit(key, error_msg or "驗證失敗")
                return False
        
        # 設定新值
        super().set_config_value(key, value)
        
        # 觸發監聽器
        if key in self._config_watchers:
            for callback in self._config_watchers[key]:
                try:
                    callback(key, old_value, value)
                except Exception as e:
                    self.logger.error(f"配置監聽器執行失敗: {key}, 錯誤: {e}")
        
        # 發送信號
        self.config_changed.emit(key, old_value, value)
        
        # 調用子類處理方法
        self._on_config_changed(key, old_value, value)
        
        return True
    
    def update_config(self, config_dict: Dict[str, Any], validate: bool = True) -> Dict[str, str]:
        """
        批量更新配置
        
        Args:
            config_dict: 配置字典
            validate: 是否進行驗證
            
        Returns:
            驗證失敗的項目字典 {key: error_message}
        """
        errors = {}
        
        for key, value in config_dict.items():
            if not self.set_config_value(key, value, validate):
                errors[key] = f"設定 {key} 失敗"
        
        if errors:
            self.logger.warning(f"批量配置更新有 {len(errors)} 項失敗")
        else:
            self.logger.info(f"批量配置更新成功: {len(config_dict)} 項")
        
        return errors
    
    def reset_config_to_default(self, keys: Optional[list] = None) -> None:
        """
        重置配置到預設值
        
        Args:
            keys: 要重置的配置鍵列表，None 表示重置全部
        """
        try:
            # 獲取預設配置
            default_config = global_config.get(f'ui.{self.__class__.__name__.lower()}', {})
            
            if keys is None:
                keys = list(self.config.keys())
            
            reset_count = 0
            for key in keys:
                if key in default_config:
                    self.set_config_value(key, default_config[key])
                    reset_count += 1
            
            self.logger.info(f"配置重置完成: {reset_count} 項")
            
        except Exception as e:
            self.logger.error(f"配置重置失敗: {e}")
    
    def export_config(self) -> Dict[str, Any]:
        """
        導出當前配置
        
        Returns:
            配置字典副本
        """
        return dict(self.config)
    
    def _on_config_changed(self, key: str, old_value: Any, new_value: Any) -> None:
        """
        配置變更處理方法
        
        子類可重寫此方法來處理特定配置的變更。
        
        Args:
            key: 變更的配置鍵
            old_value: 舊值
            new_value: 新值
            
        Example:
            def _on_config_changed(self, key, old_value, new_value):
                if key == 'theme':
                    self._apply_theme()
                elif key == 'language':
                    self._update_ui_text()
        """
        pass
    
    def _validate_config(self, key: str, value: Any) -> tuple[bool, Optional[str]]:
        """
        配置驗證方法
        
        子類可重寫此方法來實現自定義驗證邏輯。
        
        Args:
            key: 配置鍵
            value: 配置值
            
        Returns:
            (是否有效, 錯誤訊息)
            
        Example:
            def _validate_config(self, key, value):
                if key == 'max_items' and (not isinstance(value, int) or value <= 0):
                    return False, "最大項目數必須是正整數"
                return True, None
        """
        return True, None