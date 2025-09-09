#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 分類事件處理管理器

負責統一管理分類選擇器的所有事件處理邏輯，從原始 category_widget.py 
中分離出的複雜事件處理方法。這是重構中最關鍵的模組，處理21個方法中
最複雜的事件邏輯。

從原始怪物檔案分離的功能：
- connect_signals() - 信號連接管理
- handle_subcat_check() - 子分類勾選處理
- handle_subcat_spinbox_change() - 數量變更處理
- handle_cat_check() - 分類勾選處理
- update_parent_checkbox_state() - 父節點狀態更新

重構收益：
- 事件集中管理: 所有事件處理邏輯統一管理
- 狀態一致性: 確保UI狀態同步和一致性
- 可測試性: 複雜邏輯獨立，便於單元測試
- 可維護性: 事件流程清晰，易於除錯和維護
"""

from typing import Dict, List, Any, Optional, Callable, Tuple
from PyQt5.QtWidgets import QCheckBox, QSpinBox
from PyQt5.QtCore import Qt, pyqtSignal, QObject

from utils import get_logger, global_config
from ui.components.base import BaseWidget

class EventManager(BaseWidget):
    """
    分類事件處理管理器
    
    統一管理分類選擇器的所有事件處理，包括勾選狀態變更、
    數量調整、父子關係維護等複雜邏輯。使用新架構確保
    事件處理的可靠性和效率。
    
    主要功能：
    - 統一的事件註冊和管理
    - 勾選狀態同步處理
    - 父子節點關係維護
    - 數量變更邏輯處理
    - 事件流程監控和調試
    
    Signals:
        category_selection_changed: 分類選擇變更 (category_id, checked, item_count)
        subcategory_selection_changed: 子分類選擇變更 (subcategory_id, checked, count)
        parent_state_updated: 父分類狀態更新 (parent_id, new_state)
        selection_statistics_changed: 選擇統計變更 (total_selected, total_questions)
        event_processing_error: 事件處理錯誤 (event_type, error_message)
    
    Example:
        >>> manager = EventManager()
        >>> manager.register_category_widget(cat_checkbox, subcat_widgets)
        >>> manager.register_subcategory_widget(subcat_checkbox, spinbox, parent_checkbox)
        >>> 
        >>> # 監聽選擇變更
        >>> manager.category_selection_changed.connect(on_category_changed)
    """
    
    # 事件相關信號
    category_selection_changed = pyqtSignal(str, bool, int)        # category_id, checked, item_count
    subcategory_selection_changed = pyqtSignal(str, bool, int)     # subcategory_id, checked, count
    parent_state_updated = pyqtSignal(str, int)                    # parent_id, new_state (Qt.CheckState)
    selection_statistics_changed = pyqtSignal(int, int)            # total_selected, total_questions
    event_processing_error = pyqtSignal(str, str)                  # event_type, error_message
    
    def __init__(self, parent=None, config=None):
        """
        初始化事件管理器
        
        Args:
            parent: 父組件
            config: 配置字典，支援以下選項：
                - auto_sync_parent: 是否自動同步父節點狀態 (預設: True)
                - validate_state: 是否驗證狀態一致性 (預設: True)
                - debug_events: 是否啟用事件調試 (預設: False)
        """
        self._category_widgets = {}      # 分類組件字典 {category_id: (checkbox, subcategory_list)}
        self._subcategory_widgets = {}   # 子分類組件字典 {subcategory_id: (checkbox, spinbox, parent_checkbox)}
        self._event_handlers = {}        # 事件處理器字典
        self._connection_map = {}        # 連接映射表
        
        super().__init__(parent, config)
        
        # 應用配置
        self.auto_sync_parent = self.get_config_value('auto_sync_parent', True)
        self.validate_state = self.get_config_value('validate_state', True)
        self.debug_events = self.get_config_value('debug_events', False)
        
        self.logger.info("事件管理器初始化完成")
    
    def _setup_ui(self):
        """建立UI結構 - 事件管理器不需要可視UI"""
        pass
    
    def _connect_signals(self):
        """連接信號 - 主要邏輯在 register 方法中處理"""
        pass
    
    def register_category_widget(self, category_id: str, checkbox: QCheckBox, 
                                subcategory_widgets: List[Tuple]) -> bool:
        """
        註冊分類組件
        
        Args:
            category_id: 分類ID
            checkbox: 分類勾選框
            subcategory_widgets: 子分類組件列表 [(subcat_id, subcat_checkbox, spinbox)]
            
        Returns:
            註冊是否成功
        """
        try:
            self.logger.debug(f"註冊分類組件: {category_id}")
            
            # 儲存組件資訊
            self._category_widgets[category_id] = {
                'checkbox': checkbox,
                'subcategories': subcategory_widgets
            }
            
            # 連接分類勾選框信號
            checkbox.stateChanged.connect(
                lambda state, cid=category_id: self._handle_category_check(cid, state)
            )
            
            # 記錄連接
            self._connection_map[f"category_{category_id}"] = checkbox
            
            self.logger.info(f"分類組件註冊成功: {category_id}, {len(subcategory_widgets)} 個子分類")
            return True
            
        except Exception as e:
            self.logger.error(f"註冊分類組件失敗: {category_id}, 錯誤: {e}")
            self.event_processing_error.emit("register_category", str(e))
            return False
    
    def register_subcategory_widget(self, subcategory_id: str, checkbox: QCheckBox, 
                                  spinbox: QSpinBox, parent_checkbox: QCheckBox) -> bool:
        """
        註冊子分類組件
        
        Args:
            subcategory_id: 子分類ID
            checkbox: 子分類勾選框
            spinbox: 數量選擇框
            parent_checkbox: 父分類勾選框
            
        Returns:
            註冊是否成功
        """
        try:
            self.logger.debug(f"註冊子分類組件: {subcategory_id}")
            
            # 儲存組件資訊
            self._subcategory_widgets[subcategory_id] = {
                'checkbox': checkbox,
                'spinbox': spinbox,
                'parent_checkbox': parent_checkbox
            }
            
            # 連接子分類勾選框信號
            checkbox.stateChanged.connect(
                lambda state, sid=subcategory_id: self._handle_subcategory_check(sid, state)
            )
            
            # 連接數量選擇框信號
            spinbox.valueChanged.connect(
                lambda value, sid=subcategory_id: self._handle_spinbox_change(sid, value)
            )
            
            # 記錄連接
            self._connection_map[f"subcategory_{subcategory_id}"] = (checkbox, spinbox)
            
            self.logger.debug(f"子分類組件註冊成功: {subcategory_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"註冊子分類組件失敗: {subcategory_id}, 錯誤: {e}")
            self.event_processing_error.emit("register_subcategory", str(e))
            return False
    
    def _handle_category_check(self, category_id: str, state: int) -> None:
        """
        處理分類勾選狀態變更
        
        Args:
            category_id: 分類ID
            state: 新的勾選狀態 (Qt.CheckState)
        """
        try:
            if self.debug_events:
                self.logger.debug(f"處理分類勾選: {category_id}, 狀態: {state}")
            
            if category_id not in self._category_widgets:
                self.logger.warning(f"未找到分類組件: {category_id}")
                return
            
            category_info = self._category_widgets[category_id]
            subcategories = category_info['subcategories']
            
            # 根據分類狀態更新子分類
            if state == Qt.Checked:
                # 全選子分類
                self._select_all_subcategories(subcategories)
            elif state == Qt.Unchecked:
                # 取消全選子分類
                self._deselect_all_subcategories(subcategories)
            # Qt.PartiallyChecked 狀態不改變子分類
            
            # 計算總項目數
            total_items = self._calculate_category_items(subcategories)
            
            # 發送事件信號
            is_checked = state != Qt.Unchecked
            self.category_selection_changed.emit(category_id, is_checked, total_items)
            
            # 更新統計
            self._update_selection_statistics()
            
        except Exception as e:
            self.logger.error(f"處理分類勾選失敗: {category_id}, 錯誤: {e}")
            self.event_processing_error.emit("category_check", str(e))
    
    def _handle_subcategory_check(self, subcategory_id: str, state: int) -> None:
        """
        處理子分類勾選狀態變更
        
        Args:
            subcategory_id: 子分類ID
            state: 新的勾選狀態 (Qt.CheckState)
        """
        try:
            if self.debug_events:
                self.logger.debug(f"處理子分類勾選: {subcategory_id}, 狀態: {state}")
            
            if subcategory_id not in self._subcategory_widgets:
                self.logger.warning(f"未找到子分類組件: {subcategory_id}")
                return
            
            widget_info = self._subcategory_widgets[subcategory_id]
            checkbox = widget_info['checkbox']
            spinbox = widget_info['spinbox']
            parent_checkbox = widget_info['parent_checkbox']
            
            # 更新數量選擇框狀態
            is_checked = state == Qt.Checked
            spinbox.setEnabled(is_checked)
            
            if is_checked and spinbox.value() == 0:
                # 勾選時如果數量為0，設定為預設值
                spinbox.setValue(self.get_config_value('default_question_count', 1))
            elif not is_checked:
                # 取消勾選時重置數量為0
                spinbox.setValue(0)
            
            # 更新父分類狀態
            if self.auto_sync_parent:
                self._update_parent_state(parent_checkbox)
            
            # 發送事件信號
            current_count = spinbox.value() if is_checked else 0
            self.subcategory_selection_changed.emit(subcategory_id, is_checked, current_count)
            
            # 更新統計
            self._update_selection_statistics()
            
        except Exception as e:
            self.logger.error(f"處理子分類勾選失敗: {subcategory_id}, 錯誤: {e}")
            self.event_processing_error.emit("subcategory_check", str(e))
    
    def _handle_spinbox_change(self, subcategory_id: str, value: int) -> None:
        """
        處理數量選擇框變更
        
        Args:
            subcategory_id: 子分類ID
            value: 新的數量值
        """
        try:
            if self.debug_events:
                self.logger.debug(f"處理數量變更: {subcategory_id}, 數量: {value}")
            
            if subcategory_id not in self._subcategory_widgets:
                self.logger.warning(f"未找到子分類組件: {subcategory_id}")
                return
            
            widget_info = self._subcategory_widgets[subcategory_id]
            checkbox = widget_info['checkbox']
            parent_checkbox = widget_info['parent_checkbox']
            
            # 根據數量值更新勾選狀態
            if value > 0 and not checkbox.isChecked():
                # 數量>0時自動勾選
                checkbox.setChecked(True)
            elif value == 0 and checkbox.isChecked():
                # 數量=0時自動取消勾選
                checkbox.setChecked(False)
            
            # 更新父分類狀態
            if self.auto_sync_parent:
                self._update_parent_state(parent_checkbox)
            
            # 發送事件信號（通過子分類勾選事件間接發送）
            
            # 更新統計
            self._update_selection_statistics()
            
        except Exception as e:
            self.logger.error(f"處理數量變更失敗: {subcategory_id}, 錯誤: {e}")
            self.event_processing_error.emit("spinbox_change", str(e))
    
    def _update_parent_state(self, parent_checkbox: QCheckBox) -> None:
        """
        更新父分類勾選狀態
        
        Args:
            parent_checkbox: 父分類勾選框
        """
        try:
            # 找到所有子分類
            child_checkboxes = []
            for widget_info in self._subcategory_widgets.values():
                if widget_info['parent_checkbox'] == parent_checkbox:
                    child_checkboxes.append(widget_info['checkbox'])
            
            if not child_checkboxes:
                return
            
            # 統計子分類狀態
            checked_count = sum(1 for cb in child_checkboxes if cb.isChecked())
            total_count = len(child_checkboxes)
            
            # 更新父分類狀態
            if checked_count == 0:
                new_state = Qt.Unchecked
            elif checked_count == total_count:
                new_state = Qt.Checked
            else:
                new_state = Qt.PartiallyChecked
            
            # 防止循環信號
            parent_checkbox.blockSignals(True)
            parent_checkbox.setCheckState(new_state)
            parent_checkbox.blockSignals(False)
            
            # 發送父狀態更新信號
            parent_id = self._get_parent_id(parent_checkbox)
            if parent_id:
                self.parent_state_updated.emit(parent_id, new_state)
            
        except Exception as e:
            self.logger.error(f"更新父分類狀態失敗: {e}")
    
    def _select_all_subcategories(self, subcategories: List[Tuple]) -> None:
        """
        選中所有子分類
        
        Args:
            subcategories: 子分類列表 [(subcat_id, checkbox, spinbox)]
        """
        try:
            for subcat_id, checkbox, spinbox in subcategories:
                if not checkbox.isChecked():
                    checkbox.setChecked(True)
                    
        except Exception as e:
            self.logger.error(f"全選子分類失敗: {e}")
    
    def _deselect_all_subcategories(self, subcategories: List[Tuple]) -> None:
        """
        取消選中所有子分類
        
        Args:
            subcategories: 子分類列表 [(subcat_id, checkbox, spinbox)]
        """
        try:
            for subcat_id, checkbox, spinbox in subcategories:
                if checkbox.isChecked():
                    checkbox.setChecked(False)
                    
        except Exception as e:
            self.logger.error(f"取消全選子分類失敗: {e}")
    
    def _calculate_category_items(self, subcategories: List[Tuple]) -> int:
        """
        計算分類的總項目數
        
        Args:
            subcategories: 子分類列表 [(subcat_id, checkbox, spinbox)]
            
        Returns:
            總項目數
        """
        try:
            total = 0
            for subcat_id, checkbox, spinbox in subcategories:
                if checkbox.isChecked():
                    total += spinbox.value()
            return total
            
        except Exception as e:
            self.logger.error(f"計算分類項目數失敗: {e}")
            return 0
    
    def _update_selection_statistics(self) -> None:
        """更新選擇統計"""
        try:
            total_selected = 0
            total_questions = 0
            
            for widget_info in self._subcategory_widgets.values():
                checkbox = widget_info['checkbox']
                spinbox = widget_info['spinbox']
                
                if checkbox.isChecked():
                    total_selected += 1
                    total_questions += spinbox.value()
            
            self.selection_statistics_changed.emit(total_selected, total_questions)
            
        except Exception as e:
            self.logger.error(f"更新選擇統計失敗: {e}")
    
    def _get_parent_id(self, parent_checkbox: QCheckBox) -> Optional[str]:
        """
        獲取父分類ID
        
        Args:
            parent_checkbox: 父分類勾選框
            
        Returns:
            父分類ID或None
        """
        for category_id, widget_info in self._category_widgets.items():
            if widget_info['checkbox'] == parent_checkbox:
                return category_id
        return None
    
    def clear_all_registrations(self) -> None:
        """清除所有組件註冊"""
        try:
            self.logger.info("清除所有事件註冊")
            
            self._category_widgets.clear()
            self._subcategory_widgets.clear()
            self._connection_map.clear()
            
        except Exception as e:
            self.logger.error(f"清除事件註冊失敗: {e}")
    
    def get_selection_data(self) -> Dict[str, Any]:
        """
        獲取當前選擇數據
        
        Returns:
            選擇數據字典
        """
        try:
            selected_categories = []
            selected_subcategories = []
            total_questions = 0
            
            # 統計子分類選擇
            for subcategory_id, widget_info in self._subcategory_widgets.items():
                checkbox = widget_info['checkbox']
                spinbox = widget_info['spinbox']
                
                if checkbox.isChecked() and spinbox.value() > 0:
                    selected_subcategories.append({
                        'id': subcategory_id,
                        'name': checkbox.text(),
                        'count': spinbox.value()
                    })
                    total_questions += spinbox.value()
            
            # 統計分類選擇
            for category_id, widget_info in self._category_widgets.items():
                checkbox = widget_info['checkbox']
                if checkbox.checkState() != Qt.Unchecked:
                    selected_categories.append({
                        'id': category_id,
                        'name': checkbox.text(),
                        'state': checkbox.checkState()
                    })
            
            return {
                'selected_categories': selected_categories,
                'selected_subcategories': selected_subcategories,
                'total_selected': len(selected_subcategories),
                'total_questions': total_questions
            }
            
        except Exception as e:
            self.logger.error(f"獲取選擇數據失敗: {e}")
            return {
                'selected_categories': [],
                'selected_subcategories': [],
                'total_selected': 0,
                'total_questions': 0
            }