#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 類別選擇元件
"""

import random
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame, 
                             QCheckBox, QPushButton, QSpinBox, QMessageBox, QDialog)
from PyQt5.QtCore import Qt, QSize, pyqtSignal

from ui.utils import load_icon
from utils.ui import ConfigUIFactory, ConfigValueCollector
from utils import get_logger
from utils.core.registry import registry

class CategoryWidget(QWidget):
    """類別選擇元件，用於顯示和管理題型類別和子類別"""
    
    # 自定義信號
    categoryChanged = pyqtSignal()  # 當類別選擇變更時發出
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 載入圖示
        self.load_icons()
        
        # 初始化 UI
        self.initUI()
        
        # 儲存參考
        self.category_widgets = []  # 儲存元組: (cat_frame, cat_checkbox, arrow_btn, subcat_container)
        self.subcategory_widgets = []  # 儲存元組: (subcat_frame, subcat_checkbox, subcat_spinbox, parent_checkbox)

        # 初始化配置UI工具
        self.logger = get_logger(self.__class__.__name__)
        self.config_factory = ConfigUIFactory()
        self.config_collector = ConfigValueCollector()
        self.config_widgets = {}  # 儲存配置UI控件: {topic_name: config_widget}
        self.config_values = {}   # 快取配置值: {topic_name: config_dict}
        
    def load_icons(self):
        """載入所有需要的圖示"""
        self.icon_down = load_icon('chevron-down.svg')
        self.icon_right = load_icon('chevron-right.svg')
        self.icon_select_all = load_icon('check-square.svg')
        self.icon_deselect_all = load_icon('square.svg')
        self.icon_expand_all = load_icon('chevrons-down.svg')
        self.icon_collapse_all = load_icon('chevrons-up.svg')
        
    def initUI(self):
        """初始化使用者介面"""
        # 主佈局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(2)
        
        # 類別佈局 - 將在 populate_categories 中填充
        self.categories_layout = QVBoxLayout()
        self.categories_layout.setContentsMargins(0, 5, 0, 0)
        self.categories_layout.setSpacing(2)
        
        # 控制按鈕區域
        btn_layout = QHBoxLayout()
        self.select_all_btn = QPushButton(" 全選")
        self.select_all_btn.setIcon(self.icon_select_all)
        self.deselect_all_btn = QPushButton(" 全取消")
        self.deselect_all_btn.setIcon(self.icon_deselect_all)
        self.expand_all_btn = QPushButton(" 全展開")
        self.expand_all_btn.setIcon(self.icon_expand_all)
        self.collapse_all_btn = QPushButton(" 全收折")
        self.collapse_all_btn.setIcon(self.icon_collapse_all)

        for btn in [self.select_all_btn, self.deselect_all_btn, self.expand_all_btn, self.collapse_all_btn]:
            btn.setObjectName("controlButton")
            btn.setFixedHeight(32)

        btn_layout.addWidget(self.select_all_btn)
        btn_layout.addWidget(self.deselect_all_btn)
        btn_layout.addWidget(self.expand_all_btn)
        btn_layout.addWidget(self.collapse_all_btn)
        
        # 添加到主佈局
        self.main_layout.addLayout(self.categories_layout)
        self.main_layout.addLayout(btn_layout)
        
        # 連接信號
        self.connect_signals()
        
    def connect_signals(self):
        """連接所有信號和槽"""
        self.select_all_btn.clicked.connect(self.select_all_categories)
        self.deselect_all_btn.clicked.connect(self.deselect_all_categories)
        self.expand_all_btn.clicked.connect(self.expand_all_categories)
        self.collapse_all_btn.clicked.connect(self.collapse_all_categories)
        
    def create_category_widget(self, category_name):
        """建立類別元件，確保 checkbox 可點擊
        
        Args:
            category_name (str): 類別名稱
            
        Returns:
            tuple: (類別框架, 類別勾選框, 箭頭按鈕)
        """
        category_frame = QFrame()
        category_frame.setObjectName("categoryFrame")
        
        category_layout = QHBoxLayout(category_frame)
        category_layout.setContentsMargins(8, 5, 8, 5)

        # 建立類別勾選框 - 明確設置初始狀態為未勾選
        checkbox = QCheckBox(category_name)
        checkbox.setObjectName("categoryCheckbox")
        checkbox.setTristate(True)
        checkbox.setCheckState(Qt.Unchecked)  # 明確設置初始狀態
        checkbox.setCursor(Qt.PointingHandCursor)
        
        # 確保勾選框能接收滑鼠事件
        checkbox.setAttribute(Qt.WA_TransparentForMouseEvents, False)

        # 建立箭頭按鈕
        arrow_btn = QPushButton()
        arrow_btn.setObjectName("iconButton")
        arrow_btn.setIcon(self.icon_down)
        arrow_btn.setIconSize(QSize(16, 16))
        arrow_btn.setCursor(Qt.PointingHandCursor)

        category_layout.addWidget(checkbox)
        category_layout.addStretch()
        category_layout.addWidget(arrow_btn)

        return category_frame, checkbox, arrow_btn

    def create_subcategory_widget(self, subcat_name):
        """建立子類別元件，確保 checkbox 可點擊
        
        Args:
            subcat_name (str): 子類別名稱
            
        Returns:
            tuple: (子類別框架, 子類別勾選框, 數量微調框)
        """
        subcat_frame = QFrame()
        subcat_frame.setObjectName("subcategoryFrame")

        subcat_layout = QHBoxLayout(subcat_frame)
        subcat_layout.setContentsMargins(24, 3, 8, 3)  # 增加左縮排，強化視覺層級

        # 建立子類別勾選框 - 明確設置初始狀態為未勾選
        checkbox = QCheckBox(subcat_name)
        checkbox.setObjectName("subcategoryCheckbox")
        checkbox.setChecked(False)  # 明確設置初始狀態
        checkbox.setCursor(Qt.PointingHandCursor)
        
        # 確保勾選框能接收滑鼠事件
        checkbox.setAttribute(Qt.WA_TransparentForMouseEvents, False)

        # 建立數量微調框
        spinbox = QSpinBox()
        spinbox.setRange(0, 999)
        spinbox.setValue(0)
        spinbox.setFixedWidth(60)
        spinbox.setAlignment(Qt.AlignCenter)
        spinbox.setEnabled(False)  # 初始時禁用，勾選後啟用

        subcat_layout.addWidget(checkbox)
        subcat_layout.addStretch()
        # 統一配置按鈕佔位 - 確保所有數量框對齊
        config_placeholder = QWidget()
        config_placeholder.setFixedSize(28, 28)
        config_placeholder.setObjectName("configPlaceholder")
        subcat_layout.addWidget(config_placeholder)

        subcat_layout.addWidget(spinbox)

        return subcat_frame, checkbox, spinbox, config_placeholder
        
    def populate_categories(self, categories_data):
        """填充類別和子類別數據
        
        Args:
            categories_data (list): 類別數據列表，格式為 [{"name": "類別名稱", "subcategories": ["子類別1", "子類別2", ...]}, ...]
        """
        # 清空現有數據
        self.clear_categories()
        
        # 填充新數據
        for index, category in enumerate(categories_data):
            cat_frame, cat_checkbox, arrow_btn = self.create_category_widget(category["name"])
            self.categories_layout.addWidget(cat_frame)

            subcat_container = QWidget()
            subcat_layout = QVBoxLayout(subcat_container)
            subcat_layout.setContentsMargins(0, 0, 0, 0)
            subcat_layout.setSpacing(1)

            # 儲存類別元件資訊
            cat_widget_info = (cat_frame, cat_checkbox, arrow_btn, subcat_container)
            self.category_widgets.append(cat_widget_info)

            # 填充子類別
            for subcat in category["subcategories"]:
                subcat_frame, subcat_checkbox, subcat_spinbox, config_placeholder = self.create_subcategory_widget(subcat)
                subcat_layout.addWidget(subcat_frame)

                # 檢測並創建配置UI - 替換佔位符為實際按鈕
                full_topic_name = f"{category['name']}/{subcat}"  # 使用完整格式與get_selected_data保持一致
                config_ui = self._create_config_ui_for_topic(full_topic_name)
                if config_ui:
                    config_btn = self._create_config_button(config_ui, full_topic_name)
                    # 替換佔位符為實際配置按鈕
                    subcat_frame_layout = subcat_frame.layout()
                    subcat_frame_layout.replaceWidget(config_placeholder, config_btn)
                    config_placeholder.deleteLater()  # 清理佔位符

                # 儲存子類別元件資訊，包含父類別勾選框的參考
                subcat_widget_info = (subcat_frame, subcat_checkbox, subcat_spinbox, cat_checkbox)
                self.subcategory_widgets.append(subcat_widget_info)

                # --- 連接子類別信號 ---
                subcat_checkbox.stateChanged.connect(
                    lambda state, scb=subcat_checkbox, ssb=subcat_spinbox, pcb=cat_checkbox:
                    self.handle_subcat_check(state, scb, ssb, pcb)
                )
                subcat_spinbox.valueChanged.connect(
                    lambda value, scb=subcat_checkbox, pcb=cat_checkbox:
                    self.handle_subcat_spinbox_change(value, scb, pcb)
                )

            self.categories_layout.addWidget(subcat_container)

            # --- 連接類別信號 ---
            # 只將展開/收起功能綁定到箭頭按鈕
            arrow_btn.clicked.connect(
                lambda checked, sc=subcat_container, btn=arrow_btn: 
                self.toggle_container(sc, btn)
            )
            
            # 連接勾選框的狀態變更信號
            cat_checkbox.stateChanged.connect(
                lambda state, cb=cat_checkbox: 
                self.handle_cat_check(state, cb)
            )

            # 預設只展開第一個類別
            if index > 0:
                subcat_container.setVisible(False)
                arrow_btn.setIcon(self.icon_right)

        # 確保所有勾選框初始狀態正確
        for _, cat_checkbox, _, _ in self.category_widgets:
            cat_checkbox.setCheckState(Qt.Unchecked)
            cat_checkbox.repaint()
            
        for _, sub_checkbox, sub_spinbox, _ in self.subcategory_widgets:
            sub_checkbox.setChecked(False)
            sub_spinbox.setValue(0)
            sub_spinbox.setEnabled(False)
            sub_checkbox.repaint()

        self.categories_layout.addStretch()
        
    def clear_categories(self):
        """清空所有類別和子類別"""
        # 清空類別元件列表
        self.category_widgets.clear()
        self.subcategory_widgets.clear()
        self.config_widgets.clear()  # 清理配置控件引用，避免記憶體洩漏
        
        # 清空佈局
        while self.categories_layout.count():
            item = self.categories_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
    def handle_subcat_check(self, state, subcat_checkbox, subcat_spinbox, parent_checkbox):
        """處理子類別勾選框狀態變化
        
        Args:
            state (Qt.CheckState): 勾選狀態
            subcat_checkbox (QCheckBox): 子類別勾選框
            subcat_spinbox (QSpinBox): 子類別數量微調框
            parent_checkbox (QCheckBox): 父類別勾選框
        """
        # 使用 blockSignals 暫時阻止信號傳遞，避免遞迴
        subcat_checkbox.blockSignals(True)
        
        if state == Qt.Checked:
            subcat_spinbox.setEnabled(True)
            if subcat_spinbox.value() == 0:
                subcat_spinbox.setValue(1)  # 勾選時預設為1
            subcat_checkbox.setChecked(True)  # 強制設置勾選狀態
        else:
            subcat_spinbox.setValue(0)
            subcat_spinbox.setEnabled(False)
            subcat_checkbox.setChecked(False)  # 強制設置未勾選狀態
        
        subcat_checkbox.blockSignals(False)
        
        # 強制更新視覺狀態
        subcat_checkbox.repaint()
        
        self.update_parent_checkbox_state(parent_checkbox)
        self.categoryChanged.emit()  # 發出信號通知變更

    def handle_subcat_spinbox_change(self, value, subcat_checkbox, parent_checkbox):
        """處理子類別數量微調框值變化
        
        Args:
            value (int): 新的數量值
            subcat_checkbox (QCheckBox): 子類別勾選框
            parent_checkbox (QCheckBox): 父類別勾選框
        """
        # 暫時阻止信號傳遞
        subcat_checkbox.blockSignals(True)
        
        # 數量 > 0 時確保勾選框被勾選，數量 = 0 時取消勾選
        if value > 0:
            subcat_checkbox.setChecked(True)
        else:
            subcat_checkbox.setChecked(False)
            
        subcat_checkbox.blockSignals(False)
        
        # 強制更新視覺狀態
        subcat_checkbox.repaint()
        
        self.update_parent_checkbox_state(parent_checkbox)
        self.categoryChanged.emit()  # 發出信號通知變更

    def handle_cat_check(self, state, category_checkbox):
        """處理父類別勾選框狀態變化（使用者點擊）
        
        Args:
            state (Qt.CheckState): 勾選狀態
            category_checkbox (QCheckBox): 父類別勾選框
        """
        # 暫時阻止信號傳遞
        category_checkbox.blockSignals(True)
        
        if state == Qt.Checked:
            # 選取此父類別下的所有子類別
            for _, sub_cb, sub_spin, parent_cb in self.subcategory_widgets:
                if parent_cb == category_checkbox:
                    sub_cb.blockSignals(True)
                    sub_cb.setChecked(True)
                    sub_cb.blockSignals(False)
                    sub_cb.repaint()  # 強制更新視覺狀態
                    sub_spin.setEnabled(True)
                    if sub_spin.value() == 0:
                        sub_spin.setValue(1)
        elif state == Qt.Unchecked:
            # 取消選取此父類別下的所有子類別
            for _, sub_cb, sub_spin, parent_cb in self.subcategory_widgets:
                if parent_cb == category_checkbox:
                    sub_cb.blockSignals(True)
                    sub_cb.setChecked(False)
                    sub_cb.blockSignals(False)
                    sub_cb.repaint()  # 強制更新視覺狀態
                    sub_spin.setValue(0)
                    sub_spin.setEnabled(False)
        
        category_checkbox.blockSignals(False)
        
        # 強制更新視覺狀態
        category_checkbox.repaint()
        
        # 部分選取狀態由 update_parent_checkbox_state 處理
        self.categoryChanged.emit()  # 發出信號通知變更

    def update_parent_checkbox_state(self, parent_checkbox):
        """根據子類別的勾選狀態更新父類別勾選框狀態
        
        Args:
            parent_checkbox (QCheckBox): 父類別勾選框
        """
        checked_count = 0
        total_count = 0
        
        # 計算此父類別下有多少子類別被勾選
        for _, sub_cb, _, p_cb in self.subcategory_widgets:
            if p_cb == parent_checkbox:
                total_count += 1
                if sub_cb.isChecked():
                    checked_count += 1
        
        # 暫時斷開信號以防止無限遞迴
        parent_checkbox.blockSignals(True)
        
        # 設置父類別勾選狀態 - 修正後的邏輯
        if checked_count == 0:
            # 沒有子類別勾選，父類別未勾選
            parent_checkbox.setCheckState(Qt.Unchecked)
        elif checked_count == total_count:
            # 所有子類別勾選，父類別勾選
            parent_checkbox.setCheckState(Qt.Checked)
        else:
            # 部分子類別勾選，父類別部分勾選
            parent_checkbox.setCheckState(Qt.PartiallyChecked)
        
        parent_checkbox.blockSignals(False)
        
        # 強制立即重繪
        parent_checkbox.repaint()

    def toggle_container(self, container, button):
        """切換子類別容器的可見性
        
        Args:
            container (QWidget): 子類別容器
            button (QPushButton): 箭頭按鈕
        """
        is_visible = container.isVisible()
        container.setVisible(not is_visible)
        button.setIcon(self.icon_right if is_visible else self.icon_down)

    def select_all_categories(self):
        """選取所有類別"""
        for _, cat_checkbox, _, _ in self.category_widgets:
            cat_checkbox.blockSignals(True)
            cat_checkbox.setCheckState(Qt.Checked)
            cat_checkbox.blockSignals(False)
            cat_checkbox.repaint()  # 強制更新視覺狀態
            self.handle_cat_check(Qt.Checked, cat_checkbox)  # 手動調用處理函數

    def deselect_all_categories(self):
        """取消選取所有類別"""
        for _, cat_checkbox, _, _ in self.category_widgets:
            cat_checkbox.blockSignals(True)
            cat_checkbox.setCheckState(Qt.Unchecked)
            cat_checkbox.blockSignals(False)
            cat_checkbox.repaint()  # 強制更新視覺狀態
            self.handle_cat_check(Qt.Unchecked, cat_checkbox)  # 手動調用處理函數

    def expand_all_categories(self):
        """展開所有類別"""
        for _, _, arrow_btn, container in self.category_widgets:
            container.setVisible(True)
            arrow_btn.setIcon(self.icon_down)

    def collapse_all_categories(self):
        """收折所有類別"""
        for _, _, arrow_btn, container in self.category_widgets:
            container.setVisible(False)
            arrow_btn.setIcon(self.icon_right)
            
    def filter_topics(self, text):
        """根據搜尋文字過濾題型
        
        Args:
            text (str): 搜尋文字
        """
        text = text.lower().strip()
        for cat_frame, cat_checkbox, _, subcat_container in self.category_widgets:
            cat_name = cat_checkbox.text().lower()
            cat_match = text in cat_name

            subcat_match_found = False
            subcat_container_visible = False

            # 遍歷屬於此類別的子類別
            for sub_frame, sub_cb, _, parent_cb in self.subcategory_widgets:
                if parent_cb == cat_checkbox:
                    subcat_name = sub_cb.text().lower()
                    sub_match = text in subcat_name
                    sub_frame.setVisible(sub_match or not text)  # 匹配或搜尋為空時顯示
                    if sub_match:
                        subcat_match_found = True
                        subcat_container_visible = True

            # 決定類別框架和容器的可見性
            show_category = cat_match or subcat_match_found or not text
            cat_frame.setVisible(show_category)

            if show_category:
                if not text:  # 搜尋為空時，尊重使用者的展開/收折狀態
                    pass
                else:
                    # 僅當子類別匹配時強制容器可見
                    subcat_container.setVisible(subcat_container_visible)
            else:
                subcat_container.setVisible(False)
                
    def randomly_check_subcategories(self, count):
        """隨機選擇指定數量的子類別
        
        Args:
            count (int): 要隨機選擇的子類別數量
            
        Returns:
            bool: 是否成功隨機選擇
        """
        all_subcat_checkboxes = [scb for _, scb, _, _ in self.subcategory_widgets]

        if count > len(all_subcat_checkboxes):
            QMessageBox.warning(self, "數量過多", f"最多只能選擇 {len(all_subcat_checkboxes)} 種題型。")
            count = len(all_subcat_checkboxes)

        if count <= 0:
            QMessageBox.warning(self, "數量無效", "請輸入大於 0 的數量。")
            return False

        # 1. 先取消全部選擇
        self.deselect_all_categories()

        # 2. 隨機選擇並勾選
        selected_checkboxes = random.sample(all_subcat_checkboxes, count)
        
        # 追蹤需要展開的類別
        categories_to_expand = set()
        
        for cb in selected_checkboxes:
            # 使用 blockSignals 防止信號衝突
            cb.blockSignals(True)
            cb.setChecked(True)
            cb.blockSignals(False)
            cb.repaint()  # 強制更新視覺狀態
            
            # 找出此勾選框的父類別
            for _, subcat_cb, subcat_spin, parent_cb in self.subcategory_widgets:
                if subcat_cb == cb:
                    # 啟用並設定 spinbox
                    subcat_spin.setEnabled(True)
                    if subcat_spin.value() == 0:
                        subcat_spin.setValue(1)
                    
                    # 更新父類別狀態
                    self.update_parent_checkbox_state(parent_cb)
                    
                    # 找出此父類別的容器
                    for _, cat_cb, arrow_btn, container in self.category_widgets:
                        if cat_cb == parent_cb:
                            categories_to_expand.add((container, arrow_btn))
        
        # 展開所有有勾選項目的類別
        for container, arrow_btn in categories_to_expand:
            container.setVisible(True)
            arrow_btn.setIcon(self.icon_down)
        
        self.categoryChanged.emit()  # 發出信號通知變更
        return True
        
    def distribute_evenly(self, total_questions):
        """將總題數平均分配給已勾選的子類別
        
        Args:
            total_questions (int): 總題數
            
        Returns:
            bool: 是否成功分配
        """
        checked_spinboxes = []
        for _, sub_cb, sub_spin, _ in self.subcategory_widgets:
            if sub_cb.isChecked():
                checked_spinboxes.append(sub_spin)

        num_checked = len(checked_spinboxes)

        if num_checked == 0:
            QMessageBox.warning(self, "未選題型", "請先勾選至少一種題型再進行分配。")
            return False

        if total_questions <= 0:
            QMessageBox.warning(self, "題數為零", "總題數為零，無法分配。")
            return False

        # 計算基本分配數和餘數
        base_questions = total_questions // num_checked
        remainder = total_questions % num_checked

        # 分配題數
        for i, spinbox in enumerate(checked_spinboxes):
            # 暫時斷開信號以避免遞迴更新
            spinbox.blockSignals(True)
            if i < remainder:
                spinbox.setValue(base_questions + 1)
            else:
                spinbox.setValue(base_questions)
            spinbox.blockSignals(False)

        self.categoryChanged.emit()  # 發出信號通知變更
        return True
        
    def _create_config_ui_for_topic(self, topic_name: str):
        """使用註冊系統統一查詢配置資訊

        利用註冊系統的配置資訊查詢，移除硬編碼的生成器匹配邏輯。
        topic_name格式已經是 "category/subcategory"，直接使用。

        Args:
            topic_name: 題型名稱，格式為 "category/subcategory"

        Returns:
            QWidget: 配置UI控件，或None（無配置需求或檢測失敗）
        """
        try:
            # 解析topic名稱：現有格式已經正確 "category/subcategory"
            if "/" not in topic_name:
                return None

            category, subcategory = topic_name.split("/", 1)

            # 使用註冊系統統一查詢：替代硬編碼匹配
            config_info = registry.get_generator_with_config_info(category, subcategory)
            if not config_info or not config_info['has_config']:
                return None

            # 使用ConfigUIFactory自動生成UI：維持現有工廠模式
            config_widget = self.config_factory.create_widget_from_schema(config_info['config_schema'])

            # 儲存配置控件的引用供後續值收集使用
            self.config_widgets[topic_name] = config_widget

            return config_widget

        except Exception as e:
            # 配置UI生成失敗不影響基本功能，但需要記錄錯誤
            self.logger.warning(f"為{topic_name}創建配置UI失敗: {e}")
            return None


    def _collect_config_for_topic(self, topic_name: str):
        """動態收集指定題型的配置值

        優先使用快取的配置值，解決QDialog widget生命週期問題。
        失敗時返回空字典，確保向後兼容性。

        Args:
            topic_name: 題型名稱

        Returns:
            Dict[str, Any]: 收集到的配置值，失敗時返回空字典
        """
        # 優先使用快取的配置值
        if topic_name in self.config_values:
            self.logger.debug(f"使用快取的{topic_name}配置")
            return self.config_values[topic_name]

        # 查找對應的配置UI控件 (兼容性回退)
        config_widget = self.config_widgets.get(topic_name)
        if not config_widget:
            return {}

        try:
            # 解析topic名稱並使用註冊系統查詢
            if "/" not in topic_name:
                return {}

            category, subcategory = topic_name.split("/", 1)
            config_info = registry.get_generator_with_config_info(category, subcategory)
            if not config_info or not config_info['has_config']:
                return {}

            schema = config_info['config_schema']

            # 使用ConfigValueCollector收集配置值
            return self.config_collector.collect_values(config_widget, schema)

        except Exception as e:
            self.logger.warning(f"收集{topic_name}配置失敗: {e}")
            return {}  # 返回空字典，不影響基本功能

    def _create_config_button(self, config_ui: QWidget, topic_name: str) -> QPushButton:
        """創建配置按鈕，點擊彈出配置視窗

        採用彈出視窗方案，完全安全無風險的實施方式。
        配置UI保持原始狀態，ConfigValueCollector直接工作。

        Args:
            config_ui: 原始配置控件
            topic_name: 題型名稱，用於視窗標題

        Returns:
            配置按鈕，點擊後彈出配置對話框
        """
        config_btn = QPushButton("⚙️")
        config_btn.setObjectName("configButton")
        config_btn.setFixedSize(28, 28)

        # 動態生成tooltip，顯示當前配置摘要
        tooltip_text = self._generate_config_tooltip(topic_name)
        config_btn.setToolTip(tooltip_text)

        # 點擊事件：彈出配置視窗
        config_btn.clicked.connect(
            lambda: self._show_config_dialog(config_ui, topic_name)
        )

        return config_btn

    def _generate_config_tooltip(self, topic_name: str) -> str:
        """生成動態配置tooltip

        從快取配置或預設配置生成tooltip文字，顯示當前配置摘要。

        Args:
            topic_name: 題型名稱

        Returns:
            str: tooltip文字
        """
        base_text = f"配置 {topic_name}"

        # 嘗試從快取獲取配置摘要
        if topic_name in self.config_values:
            config = self.config_values[topic_name]
            summary_parts = []

            # 根據常見配置項目生成摘要
            if 'function_scope' in config:
                summary_parts.append(f"函數範圍={config['function_scope']}")
            if 'angle_mode' in config:
                summary_parts.append(f"角度模式={config['angle_mode']}")
            if 'difficulty' in config:
                summary_parts.append(f"難度={config['difficulty']}")

            if summary_parts:
                return f"{base_text}\n當前：{', '.join(summary_parts)}"

        return f"{base_text}\n點擊設定配置選項"

    def _update_config_button_tooltip(self, topic_name: str):
        """更新配置按鈕的tooltip

        在配置更改後更新對應按鈕的tooltip內容。

        Args:
            topic_name: 題型名稱
        """
        # 查找對應的配置按鈕並更新tooltip
        new_tooltip = self._generate_config_tooltip(topic_name)

        # 遍歷找到對應的按鈕 (透過objectName和parent查找)
        for widget in self.findChildren(QPushButton):
            if widget.objectName() == "configButton":
                current_tooltip = widget.toolTip()
                if topic_name in current_tooltip:
                    widget.setToolTip(new_tooltip)
                    self.logger.debug(f"已更新{topic_name}按鈕tooltip")
                    break

    def _is_widget_valid(self, widget: QWidget) -> bool:
        """檢查widget是否仍然有效

        當Qt進行UI重建時，某些widget可能被刪除但Python引用仍存在。
        嘗試訪問已刪除widget的屬性會觸發RuntimeError。

        Args:
            widget: 要檢查的widget

        Returns:
            bool: True if widget is valid, False if deleted
        """
        try:
            # 嘗試訪問widget屬性，無效時會拋出RuntimeError
            _ = widget.objectName()
            return True
        except RuntimeError:
            return False

    def _recreate_config_ui(self, topic_name: str):
        """重新創建配置UI

        當原始config_ui被刪除時，使用現有的工廠方法重新創建。
        這確保了字體縮放等UI重建操作不會影響配置功能。

        Args:
            topic_name: 題型名稱，格式為 "category/subcategory"

        Returns:
            QWidget: 重新創建的配置UI控件，失敗時返回None
        """
        try:
            self.logger.debug(f"重新創建{topic_name}的配置UI")
            new_config_ui = self._create_config_ui_for_topic(topic_name)
            if new_config_ui:
                self.logger.debug(f"成功重新創建{topic_name}的配置UI")
            return new_config_ui
        except Exception as e:
            self.logger.error(f"重新創建{topic_name}配置UI失敗: {e}")
            return None

    def _show_config_dialog(self, config_ui: QWidget, topic_name: str):
        """顯示配置對話框

        使用QDialog包裝配置UI，在關閉前收集配置值以解決widget生命週期問題。
        添加widget有效性檢查，防範字體縮放等UI重建操作導致的RuntimeError。

        Args:
            config_ui: 配置UI控件
            topic_name: 題型名稱
        """
        # 檢查config_ui是否仍然有效
        if not self._is_widget_valid(config_ui):
            self.logger.debug(f"檢測到{topic_name}的config_ui已失效，嘗試重新創建")
            new_config_ui = self._recreate_config_ui(topic_name)
            if new_config_ui is None:
                self.logger.error(f"無法重新創建{topic_name}的配置UI，配置對話框無法顯示")
                QMessageBox.warning(self, "配置錯誤",
                                  f"無法顯示{topic_name}的配置選項，請重新載入程式。")
                return
            config_ui = new_config_ui

        dialog = QDialog(self)
        dialog.setWindowTitle(f"{topic_name} - 配置選項")
        dialog.setModal(True)
        dialog.setFixedSize(420, 250)

        # 主佈局
        layout = QVBoxLayout(dialog)
        layout.addWidget(config_ui)

        # 按鈕區域
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        ok_btn = QPushButton("確定")
        cancel_btn = QPushButton("取消")

        # 修改確定按鈕邏輯：關閉前收集配置
        def on_accept():
            try:
                # 使用註冊系統查詢配置schema
                if "/" in topic_name:
                    category, subcategory = topic_name.split("/", 1)
                    config_info = registry.get_generator_with_config_info(category, subcategory)
                    if config_info and config_info['has_config']:
                        schema = config_info['config_schema']
                        # 收集並快取配置值
                        config_values = self.config_collector.collect_values(config_ui, schema)
                        self.config_values[topic_name] = config_values
                    self.logger.debug(f"已快取{topic_name}配置: {config_values}")

                    # 更新按鈕tooltip以反映新配置
                    self._update_config_button_tooltip(topic_name)
            except Exception as e:
                self.logger.warning(f"快取{topic_name}配置失敗: {e}")
            finally:
                dialog.accept()

        ok_btn.clicked.connect(on_accept)
        cancel_btn.clicked.connect(dialog.reject)

        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(ok_btn)
        layout.addLayout(btn_layout)

        # 應用對話框樣式
        dialog.setObjectName("configDialog")

        # 顯示對話框
        dialog.exec_()

    def get_selected_data(self):
        """獲取已選擇的題型數據
        
        Returns:
            tuple: (已選題型數, 總題數, 選定的題型數據)
        """
        selected_count = 0
        total_questions = 0
        selected_data = []
        
        for _, sub_cb, sub_spin, parent_cb in self.subcategory_widgets:
            if sub_cb.isChecked() and sub_spin.value() > 0:
                selected_count += 1
                total_questions += sub_spin.value()
                
                topic_name = f"{parent_cb.text()}/{sub_cb.text()}"
                count = sub_spin.value()
                # 建立基本數據
                topic_data = {"topic": topic_name, "count": count}

                # 動態收集配置，替代硬編碼配置邏輯
                config = self._collect_config_for_topic(topic_name)
                if config:
                    topic_data["config"] = config

                selected_data.append(topic_data)
                
        return selected_count, total_questions, selected_data
