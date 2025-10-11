#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""配置UI工廠模組

提供動態配置UI生成功能，根據生成器的配置描述自動創建PyQt5控件。
實現零重複代碼的配置UI系統，支援多種控件類型的自動生成和值收集。

主要功能：
- ConfigUIFactory: 根據配置描述自動生成UI控件
- ConfigValueCollector: 收集UI控件的配置值
- 支援控件類型：select(下拉框)、checkbox(勾選框)、percentage_group(百分比分配)、number_input(數字輸入框)
- 完整的配置驗證和錯誤處理機制

使用範例：
    >>> from utils.ui.config_factory import ConfigUIFactory, ConfigValueCollector
    >>>
    >>> # 創建UI控件
    >>> factory = ConfigUIFactory()
    >>> schema = {"mode": {"type": "select", "options": ["A", "B"], "default": "A"}}
    >>> widget = factory.create_widget_from_schema(schema)
    >>>
    >>> # 收集配置值
    >>> collector = ConfigValueCollector()
    >>> values = collector.collect_values(widget, schema)
    >>> print(values)  # {"mode": "A"}
"""

from typing import Dict, Any, Optional
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QCheckBox, QPushButton, QSpinBox
from PyQt5.QtCore import Qt

from utils import get_logger

logger = get_logger(__name__)


class ConfigUIFactory:
    """配置UI工廠類

    根據生成器提供的配置描述自動生成PyQt5控件，實現零重複代碼的
    動態配置UI系統。支援多種控件類型，失敗時直接拋出異常。

    支援的控件類型：
    - select: 下拉選擇框（QComboBox）
    - checkbox: 勾選框（QCheckBox）
    - percentage_group: 百分比分配對話框（QPushButton + PercentageConfigDialog）
    - number_input: 數字輸入框（QSpinBox）

    Example:
        >>> factory = ConfigUIFactory()
        >>> schema = {
        ...     "difficulty": {
        ...         "type": "select",
        ...         "label": "難度",
        ...         "options": ["easy", "hard"],
        ...         "default": "easy"
        ...     }
        ... }
        >>> widget = factory.create_widget_from_schema(schema)
    """

    def __init__(self):
        """初始化配置UI工廠"""
        self.logger = get_logger(self.__class__.__name__)

    def create_widget_from_schema(self, schema: Dict[str, Dict[str, Any]]) -> QWidget:
        """根據配置描述自動生成UI控件

        將生成器的配置需求轉換為PyQt5控件，實現零重複代碼目標。
        失敗時直接拋出異常，讓開發者立即發現配置問題。

        Args:
            schema: 配置描述字典，包含各配置項的控件定義

        Returns:
            QWidget: 包含所有配置控件的容器widget

        Raises:
            ValueError: 配置格式錯誤時拋出異常

        Example:
            >>> schema = {
            ...     "mode": {"type": "select", "options": ["A"], "default": "A"},
            ...     "enabled": {"type": "checkbox", "default": True}
            ... }
            >>> widget = factory.create_widget_from_schema(schema)
        """
        # 驗證schema基本格式：必須為非空字典
        if not isinstance(schema, dict) or not schema:
            raise ValueError("配置描述必須為非空字典")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(8)  # 控件間距設定，提升視覺體驗
        layout.setContentsMargins(10, 10, 10, 10)

        # 為每個配置項創建對應的UI控件
        for field_name, field_config in schema.items():
            try:
                field_widget = self._create_field_widget(field_name, field_config)
                layout.addWidget(field_widget)
            except Exception as e:
                # 單一控件創建失敗不影響其他控件，但需記錄錯誤
                self.logger.error(f"創建配置項 '{field_name}' 失敗: {e}")
                raise ValueError(f"配置項 '{field_name}' 格式錯誤: {e}")

        return container

    def _create_field_widget(self, field_name: str, config: Dict[str, Any]) -> QWidget:
        """為單一配置項創建UI控件

        根據配置類型創建對應的控件，包含標籤和控件的組合。
        支援各種控件類型的統一處理邏輯。

        Args:
            field_name: 配置項名稱，用於控件標識
            config: 配置項描述，包含type、label等資訊

        Returns:
            QWidget: 包含標籤和控件的容器

        Raises:
            ValueError: 不支援的控件類型或配置錯誤
        """
        # 驗證基本欄位：type和label是必需的
        if 'type' not in config:
            raise ValueError(f"配置項 '{field_name}' 缺少必需欄位 'type'")
        if 'label' not in config:
            raise ValueError(f"配置項 '{field_name}' 缺少必需欄位 'label'")

        control_type = config['type']
        label_text = config['label']

        # 創建控件容器：標籤和控件水平排列
        field_container = QWidget()
        field_layout = QHBoxLayout(field_container)
        field_layout.setSpacing(8)
        field_layout.setContentsMargins(0, 0, 0, 0)

        # 創建標籤
        label = QLabel(label_text)
        label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        label.setMinimumWidth(80)  # 設定標籤最小寬度確保對齊
        field_layout.addWidget(label)

        # 根據控件類型創建對應的控件
        if control_type == "select":
            control = self._create_select_widget(config)
        elif control_type == "checkbox":
            control = self._create_checkbox_widget(config)
        elif control_type == "percentage_group":
            control = self._create_percentage_group_widget(config)
        elif control_type == "number_input":
            control = self._create_number_input_widget(config)
        else:
            raise ValueError(f"不支援的控件類型: {control_type}")

        # 設定控件的objectName供後續值收集使用
        control.setObjectName(f"config_{field_name}")
        field_layout.addWidget(control)

        # 添加彈性空間讓控件不會過度拉伸
        field_layout.addStretch()

        # 添加描述文字（如果有）- 放到新行
        container_with_desc = QWidget()
        container_layout = QVBoxLayout(container_with_desc)
        container_layout.setSpacing(1)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(field_container)

        if 'description' in config:
            desc_label = QLabel(config['description'])
            desc_label.setStyleSheet("color: #3498db; font-size: 14px; margin: 0px; padding: 0px;")
            desc_label.setWordWrap(True)
            container_layout.addWidget(desc_label)

        return container_with_desc

    def _create_select_widget(self, config: Dict[str, Any]) -> QComboBox:
        """創建下拉選擇控件

        Args:
            config: 必須包含 options 列表和 default 值

        Returns:
            QComboBox: 配置好預設值的下拉選擇框

        Raises:
            ValueError: options為空或default值不在options中
        """
        # 驗證配置格式：options必須存在且為非空列表
        if 'options' not in config or not config['options']:
            raise ValueError("select控件必須提供非空的options列表")
        if 'default' not in config:
            raise ValueError("select控件必須提供default預設值")

        options = config['options']
        default_value = config['default']

        # 驗證預設值：default必須在options中，避免運行時錯誤
        if default_value not in options:
            raise ValueError(f"預設值'{default_value}'不在選項{options}中")

        combo = QComboBox()
        combo.addItems(options)

        # 設定預設選中項：前面已驗證default_value在options中
        default_index = options.index(default_value)
        combo.setCurrentIndex(default_index)

        return combo

    def _create_checkbox_widget(self, config: Dict[str, Any]) -> QCheckBox:
        """創建勾選框控件

        Args:
            config: 必須包含 default 布林值

        Returns:
            QCheckBox: 配置好預設狀態的勾選框

        Raises:
            ValueError: default值不是布林類型
        """
        if 'default' not in config:
            raise ValueError("checkbox控件必須提供default預設值")

        default_value = config['default']

        # 驗證預設值：default必須為布林值
        if not isinstance(default_value, bool):
            raise ValueError(f"checkbox的default值必須為布林類型，收到: {type(default_value)}")

        checkbox = QCheckBox()
        checkbox.setChecked(default_value)

        return checkbox

    def _create_number_input_widget(self, config: Dict[str, Any]) -> QSpinBox:
        """創建數字輸入控件

        Args:
            config: 必須包含 default 數值參數，min, max 為可選參數

        Returns:
            QSpinBox: 配置好範圍和預設值的數字輸入框

        Raises:
            ValueError: 配置參數缺失或格式錯誤
        """
        # 驗證必需參數
        if 'default' not in config:
            raise ValueError("number_input控件必須提供default參數")

        default_value = config['default']
        min_value = config.get('min')
        max_value = config.get('max')

        # 驗證數值類型
        if not isinstance(default_value, (int, float)):
            raise ValueError(f"default參數必須為數值類型，收到: {type(default_value)}")
        if min_value is not None and not isinstance(min_value, (int, float)):
            raise ValueError(f"min參數必須為數值類型，收到: {type(min_value)}")
        if max_value is not None and not isinstance(max_value, (int, float)):
            raise ValueError(f"max參數必須為數值類型，收到: {type(max_value)}")

        # 創建 QSpinBox
        spinbox = QSpinBox()

        # 僅在min和max都提供時，才設定範圍和驗證邏輯
        if min_value is not None and max_value is not None:
            if min_value >= max_value:
                raise ValueError(f"min({min_value})必須小於max({max_value})")
            if not (min_value <= default_value <= max_value):
                raise ValueError(f"default({default_value})必須在min({min_value})和max({max_value})之間")
            spinbox.setRange(int(min_value), int(max_value))
        else:
            # 如果沒有範圍，設定一個較大的默認範圍以允許自由輸入
            spinbox.setRange(-999999, 999999)

        spinbox.setValue(int(default_value))

        # 參考 category_widget.py 的樣式設定
        spinbox.setFixedWidth(80)  # 比原始60稍寬，適合較大數值
        spinbox.setAlignment(Qt.AlignCenter)

        return spinbox

    def _create_percentage_group_widget(self, config: Dict[str, Any]) -> QPushButton:
        """創建百分比分配控件

        創建配置按鈕，點擊時彈出PercentageConfigDialog對話框。
        使用按鈕屬性存儲配置值，避免複雜的事件系統。

        Args:
            config: 必須包含 type='percentage_group'、label 和 items

        Returns:
            QPushButton: 配置按鈕，內部存儲配置值

        Raises:
            ValueError: 配置格式錯誤或缺少必需欄位
        """
        # 驗證percentage_group特定欄位：items用於對話框生成
        if 'items' not in config or not isinstance(config['items'], dict):
            raise ValueError("percentage_group控件必須包含items字典")

        if len(config['items']) < 2:
            raise ValueError("percentage_group控件至少需要2個項目")

        # 計算預設值總和：確保配置邏輯正確，避免運行時錯誤
        items = config['items']
        total_default = 0
        default_values = {}

        for item_key, item_config in items.items():
            if not isinstance(item_config, dict):
                raise ValueError(f"項目'{item_key}'配置必須為字典")
            if 'default' not in item_config:
                raise ValueError(f"項目'{item_key}'必須包含default值")
            if not isinstance(item_config['default'], (int, float)):
                raise ValueError(f"項目'{item_key}'的default必須為數值")

            default_value = int(item_config['default'])
            default_values[item_key] = default_value
            total_default += default_value

        # 驗證預設值總和：必須為100%，確保配置邏輯正確
        if abs(total_default - 100) > 0.01:  # 允許浮點誤差
            raise ValueError(f"percentage_group預設值總和必須為100%，當前為{total_default}%")

        # 創建配置按鈕：顯示當前配置狀態
        config_button = QPushButton()
        self._update_button_display(config_button, default_values)

        # 存儲配置值到按鈕屬性：使用屬性存儲避免複雜的值持久化
        config_button._saved_values = default_values
        config_button._config_schema = config

        # 連接按鈕點擊事件：點擊時彈出配置對話框
        config_button.clicked.connect(
            lambda: self._open_percentage_dialog(config_button)
        )

        return config_button

    def _update_button_display(self, button: QPushButton, values: Dict[str, int]):
        """更新配置按鈕的顯示文字

        根據當前配置值生成簡潔的按鈕顯示文字，
        讓用戶快速了解當前配置狀態。

        Args:
            button: 要更新的配置按鈕
            values: 當前配置值字典
        """
        # 生成簡潔的配置摘要：顯示前2-3個主要項目
        value_pairs = list(values.items())
        if len(value_pairs) <= 3:
            # 項目少於等於3個：顯示全部
            summary_parts = [f"{value}%" for value in values.values()]
            display_text = f"配置: {' / '.join(summary_parts)}"
        else:
            # 項目超過3個：顯示前2個 + 總數
            first_two = [f"{value}%" for _, value in value_pairs[:2]]
            remaining_count = len(value_pairs) - 2
            display_text = f"配置: {' / '.join(first_two)} + {remaining_count}項..."

        button.setText(display_text)
        button.setToolTip("點擊配置百分比分配")  # 提供操作提示

    def _open_percentage_dialog(self, config_button: QPushButton):
        """開啟百分比配置對話框

        彈出PercentageConfigDialog讓用戶調整配置，
        確認後更新按鈕顯示和存儲值。

        Args:
            config_button: 觸發的配置按鈕，包含schema和當前值
        """
        # 導入對話框類：延遲導入避免循環依賴
        from .percentage_dialog import PercentageConfigDialog

        try:
            # 準備對話框schema：使用按鈕存儲的配置資訊
            dialog_schema = config_button._config_schema.copy()

            # 設定當前值為對話框的預設值：保持用戶之前的配置
            current_values = getattr(config_button, '_saved_values', {})
            for item_key, current_value in current_values.items():
                if item_key in dialog_schema['items']:
                    dialog_schema['items'][item_key]['default'] = current_value

            # 創建並顯示對話框：使用當前控件的父widget作為parent
            parent_widget = config_button.parent()
            dialog = PercentageConfigDialog(parent_widget, dialog_schema)

            # 處理對話框結果：只有確認時才更新配置
            if dialog.exec_() == dialog.Accepted:
                # 獲取新配置值並更新按鈕
                new_values = dialog.get_values()
                config_button._saved_values = new_values
                self._update_button_display(config_button, new_values)

                # 記錄配置更新：有助於調試和監控
                self.logger.info(f"百分比配置已更新: {new_values}")

        except Exception as e:
            # 對話框開啟失敗不影響基本功能，但需記錄錯誤
            self.logger.error(f"開啟百分比配置對話框失敗: {e}")
            # 可以在此處添加用戶友善的錯誤提示


class ConfigValueCollector:
    """配置值收集器類

    從UI控件中收集用戶配置的值，根據原始配置描述確定數據格式。
    支援各種控件類型的值提取，失敗時返回空字典確保系統穩定。

    Example:
        >>> collector = ConfigValueCollector()
        >>> schema = {"mode": {"type": "select", "default": "A"}}
        >>> values = collector.collect_values(config_widget, schema)
        >>> print(values)  # {"mode": "B"}  # 用戶選擇的值
    """

    def __init__(self):
        """初始化配置值收集器"""
        self.logger = get_logger(self.__class__.__name__)

    def collect_values(self, config_widget: QWidget, schema: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """動態收集配置UI的值

        根據schema描述遍歷UI控件並提取配置值，替代硬編碼配置邏輯。
        失敗時返回空字典，確保向後兼容性。

        Args:
            config_widget: 包含配置控件的容器widget
            schema: 原始配置描述，用於確定數據格式

        Returns:
            Dict[str, Any]: 收集到的配置值字典

        Example:
            >>> values = collector.collect_values(widget, schema)
            >>> # 返回類似: {"function_scope": "basic", "angle_mode": "degree"}
        """
        if not config_widget or not schema:
            return {}

        collected_values = {}

        for field_name, field_config in schema.items():
            try:
                control_value = self._extract_field_value(config_widget, field_name, field_config)
                if control_value is not None:
                    collected_values[field_name] = control_value
            except Exception as e:
                # 單一欄位收集失敗不影響其他欄位，使用預設值
                self.logger.warning(f"收集配置項 '{field_name}' 失敗: {e}")
                if 'default' in field_config:
                    collected_values[field_name] = field_config['default']

        return collected_values

    def _extract_field_value(self, container: QWidget, field_name: str, config: Dict[str, Any]) -> Any:
        """從UI控件提取單一欄位的值

        根據控件類型使用對應的值提取邏輯，確保數據格式正確。

        Args:
            container: 包含目標控件的容器
            field_name: 配置項名稱
            config: 配置項描述

        Returns:
            Any: 提取到的配置值

        Raises:
            ValueError: 找不到控件或控件類型不匹配
        """
        # 根據objectName查找對應的控件
        control_name = f"config_{field_name}"
        control = container.findChild(QWidget, control_name)

        if not control:
            raise ValueError(f"找不到名為 '{control_name}' 的控件")

        control_type = config.get('type')

        # 根據控件類型提取值
        if control_type == "select" and isinstance(control, QComboBox):
            return control.currentText()
        elif control_type == "checkbox" and isinstance(control, QCheckBox):
            return control.isChecked()
        elif control_type == "percentage_group" and isinstance(control, QPushButton):
            # 從按鈕屬性提取配置值：使用屬性存儲避免複雜的值查詢
            saved_values = getattr(control, '_saved_values', None)
            if saved_values is None:
                # 沒有存儲值時使用預設值：確保向後兼容性
                return self._get_percentage_group_defaults(config)
            return saved_values
        elif control_type == "number_input" and isinstance(control, QSpinBox):
            return control.value()
        else:
            raise ValueError(f"控件類型不匹配: 預期{control_type}，實際{type(control)}")

    def _get_percentage_group_defaults(self, config: Dict[str, Any]) -> Dict[str, int]:
        """取得percentage_group的預設值

        從配置描述中提取預設值，用於控件初始化或回退情況。
        確保返回的值格式與對話框輸出一致。

        Args:
            config: percentage_group配置描述，包含items和預設值

        Returns:
            Dict[str, int]: 各項目的預設百分比值

        Raises:
            ValueError: 配置格式錯誤
        """
        # 驗證配置格式：確保items存在
        if 'items' not in config or not isinstance(config['items'], dict):
            raise ValueError("percentage_group配置必須包含items字典")

        default_values = {}

        # 提取每個項目的預設值
        for item_key, item_config in config['items'].items():
            if not isinstance(item_config, dict) or 'default' not in item_config:
                raise ValueError(f"項目'{item_key}'必須包含default值")

            default_value = int(item_config['default'])
            default_values[item_key] = default_value

        return default_values