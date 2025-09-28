#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""百分比配置對話框模組

提供極簡的百分比配置對話框，支援動態N項百分比分配和文字進度條視覺化。
採用基礎招式設計理念：簡潔實用勝過華麗複雜，確保教師使用友善。

主要功能：
- PercentageConfigDialog: 彈出式百分比配置對話框
- 文字進度條即時預覽：使用Unicode字符顯示比例
- 嚴格100%總和驗證：確保配置邏輯正確性
- 跨平台等寬字體支援：提供一致的視覺體驗
- 完整的FontManager整合：支援50%-200%字體縮放

設計理念：
- 該用基礎招式的時候用基礎招式：避免過度華麗的視覺效果
- 教師友善：直觀的數值輸入，一目了然的視覺反饋
- 零依賴實現：純Unicode字符，無需額外圖形庫

使用範例：
    >>> from utils.ui.percentage_dialog import PercentageConfigDialog
    >>>
    >>> schema = {
    ...     "type": "percentage_group",
    ...     "label": "題型比例分配",
    ...     "items": {
    ...         "original": {"label": "第一象限轉換", "default": 70},
    ...         "formula": {"label": "公式問答", "default": 10}
    ...     }
    ... }
    >>>
    >>> dialog = PercentageConfigDialog(parent_widget, schema)
    >>> if dialog.exec_() == QDialog.Accepted:
    ...     values = dialog.get_values()
    ...     print(values)  # {"original": 75, "formula": 25}
"""

from typing import Dict, Any
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox,
    QPushButton, QWidget, QFrame
)
from PyQt5.QtCore import Qt

from utils import get_logger

logger = get_logger(__name__)


class PercentageConfigDialog(QDialog):
    """極簡百分比配置對話框

    彈出式對話框實現N項百分比分配配置，提供文字進度條即時預覽和
    嚴格的100%總和驗證。採用極簡設計避免介面過於複雜。

    核心特性：
    - 動態項目生成：根據schema自動創建2-N個數值輸入框
    - 文字進度條視覺化：使用Unicode■□字符顯示比例
    - 即時更新：數值變化立即更新進度條和總和驗證
    - 嚴格驗證：只有總和=100%時才能確定
    - 跨平台字體：等寬字體回退機制確保一致顯示

    Example:
        >>> schema = {
        ...     "type": "percentage_group",
        ...     "label": "題型比例",
        ...     "items": {"A": {"label": "類型A", "default": 60},
        ...               "B": {"label": "類型B", "default": 40}}
        ... }
        >>> dialog = PercentageConfigDialog(parent, schema)
        >>> if dialog.exec_() == QDialog.Accepted:
        ...     print(dialog.get_values())  # {"A": 60, "B": 40}
    """

    def __init__(self, parent: QWidget, schema: Dict[str, Any]):
        """初始化百分比配置對話框

        Args:
            parent: 父widget，用於對話框定位
            schema: 配置描述，必須包含type、label和items

        Raises:
            ValueError: schema格式錯誤時拋出異常
        """
        super().__init__(parent)

        self.logger = get_logger(self.__class__.__name__)
        self.schema = schema
        self.spinboxes = {}  # 存儲各項目的數值輸入框
        self.progress_labels = {}  # 存儲各項目的進度條標籤
        self.total_label = None  # 總和顯示標籤
        self.ok_button = None  # 確定按鈕

        # 驗證schema格式：確保必要欄位存在，避免運行時錯誤
        self._validate_schema()

        # 設定對話框基本屬性
        self._setup_dialog_properties()

        # 建立UI界面
        self._setup_ui()

        # 連接信號：數值變化時即時更新視覺化
        self._connect_signals()

        # 初始更新：顯示預設值的進度條
        self._update_progress_display()

    def _validate_schema(self):
        """驗證配置描述格式

        確保schema包含必需欄位並格式正確，失敗時直接拋異常
        讓開發者立即發現配置問題。

        Raises:
            ValueError: schema格式錯誤
        """
        if not isinstance(self.schema, dict):
            raise ValueError("schema必須為字典類型")

        # 驗證必需欄位：type必須為percentage_group
        if self.schema.get('type') != 'percentage_group':
            raise ValueError("對話框只支援type='percentage_group'的schema")

        # 驗證標籤和項目定義：label用於對話框標題顯示
        if 'label' not in self.schema:
            raise ValueError("schema必須包含label欄位")

        # 驗證items結構：items必須為非空字典，包含至少2個項目
        if 'items' not in self.schema or not isinstance(self.schema['items'], dict):
            raise ValueError("schema必須包含items字典")

        items = self.schema['items']
        if len(items) < 2:
            raise ValueError("percentage_group至少需要2個項目")

        # 驗證每個項目的格式：確保有label和default
        total_default = 0
        for item_key, item_config in items.items():
            if not isinstance(item_config, dict):
                raise ValueError(f"項目'{item_key}'配置必須為字典")
            if 'label' not in item_config:
                raise ValueError(f"項目'{item_key}'必須包含label")
            if 'default' not in item_config:
                raise ValueError(f"項目'{item_key}'必須包含default值")
            if not isinstance(item_config['default'], (int, float)):
                raise ValueError(f"項目'{item_key}'的default必須為數值")

            total_default += item_config['default']

        # 驗證預設值總和：必須為100%，確保配置邏輯正確
        if abs(total_default - 100) > 0.01:  # 允許浮點誤差
            raise ValueError(f"預設值總和必須為100%，當前為{total_default}%")

    def _setup_dialog_properties(self):
        """設定對話框基本屬性

        配置視窗標題、大小、模態等基本屬性，確保良好的用戶體驗。
        """
        # 設定標題：使用schema的label作為對話框標題
        dialog_title = f"{self.schema['label']} - 配置"
        self.setWindowTitle(dialog_title)

        # 設定對話框大小：根據控件數量自適應計算高度
        item_count = len(self.schema['items'])
        dialog_height = 184 + (item_count * 49) - 12  # 基礎184px + 每控件49px
        self.setFixedSize(480, dialog_height)

        # 設定為模態對話框：確保用戶專注於配置任務
        self.setModal(True)

        # 設定為工具對話框：在工作列中不顯示獨立圖標
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)

    def _setup_ui(self):
        """建立對話框UI界面

        根據FontManager規範設定字體和佈局，建立標題、配置項、
        進度條預覽和按鈕等所有UI元素。
        """
        # 建立主佈局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)  # 適中間距避免控件被壓縮
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 建立配置輸入區域
        self._create_config_section(main_layout)

        # 建立進度條預覽區域
        self._create_progress_section(main_layout)

        # 建立總和驗證區域
        self._create_validation_section(main_layout)

        # 建立按鈕區域
        self._create_button_section(main_layout)


    def _create_config_section(self, parent_layout: QVBoxLayout):
        """建立配置輸入區域

        動態根據schema.items創建數值輸入框，支援2-N個項目的
        百分比配置。每行包含標籤、輸入框和進度條。

        Args:
            parent_layout: 父佈局，用於添加配置元素
        """
        # 動態創建每個項目的配置行
        items = self.schema['items']
        for item_key, item_config in items.items():
            config_row = self._create_config_row(item_key, item_config)
            parent_layout.addWidget(config_row)

    def _create_config_row(self, item_key: str, item_config: Dict[str, Any]) -> QWidget:
        """創建單個配置項的行

        包含標籤、數值輸入框和進度條的水平佈局，
        採用等寬佈局確保視覺對齊。

        Args:
            item_key: 項目鍵值，用於內部識別
            item_config: 項目配置，包含label和default

        Returns:
            QWidget: 包含完整配置行的容器
        """
        # 建立行容器
        row_container = QWidget()
        row_layout = QHBoxLayout(row_container)
        row_layout.setSpacing(12)
        row_layout.setContentsMargins(0, 4, 0, 4)

        # 建立項目標籤：固定寬度確保對齊
        item_label = QLabel(f"{item_config['label']}(%):")
        item_label.setMinimumWidth(120)  # 設定最小寬度確保標籤對齊
        item_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        # 讓標籤使用FontManager的全域字體樣式
        row_layout.addWidget(item_label)

        # 建立數值輸入框：支援0-100範圍，預設值來自schema
        spinbox = QSpinBox()
        spinbox.setRange(0, 100)  # 百分比範圍限制
        spinbox.setValue(int(item_config['default']))
        spinbox.setSuffix("%")  # 顯示百分比符號
        spinbox.setMinimumWidth(80)
        spinbox.setMinimumHeight(29)  # 確保spinbox有足夠高度
        row_layout.addWidget(spinbox)

        # 建立進度條標籤：使用等寬字體顯示視覺化比例
        progress_label = QLabel()
        progress_label.setStyleSheet(self._get_monospace_font_style())
        progress_label.setMinimumWidth(240)  # 確保20格進度條完整顯示
        row_layout.addWidget(progress_label)

        # 存儲控件參考：供後續更新和值收集使用
        self.spinboxes[item_key] = spinbox
        self.progress_labels[item_key] = progress_label

        # 設定最小高度保護：確保配置行不被壓縮
        row_container.setMinimumHeight(32)

        return row_container

    def _create_progress_section(self, parent_layout: QVBoxLayout):
        """建立進度條預覽區域

        顯示所有項目的文字進度條總覽，提供直觀的比例視覺化。
        使用等寬字體確保進度條對齊。
        """
        # 建立說明文字：幫助用戶理解進度條含義
        progress_desc = QLabel("■ 代表已分配比例，□ 代表未分配比例")
        progress_desc.setAlignment(Qt.AlignCenter)
        progress_desc.setStyleSheet("color: #7f8c8d; margin-bottom: 8px;")
        parent_layout.addWidget(progress_desc)

    def _create_validation_section(self, parent_layout: QVBoxLayout):
        """建立總和驗證區域

        顯示當前總和並提供視覺化的驗證狀態，
        確保用戶了解配置的有效性。

        Args:
            parent_layout: 父佈局，用於添加驗證元素
        """
        # 建立分隔線：分隔配置區域和總和驗證
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("color: #bdc3c7; margin: 8px 0px;")
        parent_layout.addWidget(separator)

        # 建立總和顯示標籤
        self.total_label = QLabel()
        self.total_label.setAlignment(Qt.AlignCenter)
        self.total_label.setStyleSheet("font-weight: bold; margin: 8px 0px;")
        parent_layout.addWidget(self.total_label)

    def _create_button_section(self, parent_layout: QVBoxLayout):
        """建立按鈕區域

        包含確定和取消按鈕，確定按鈕只有在總和=100%時才啟用。

        Args:
            parent_layout: 父佈局，用於添加按鈕元素
        """
        # 建立按鈕容器
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 12, 0, 0)

        # 添加彈性空間讓按鈕居中
        button_layout.addStretch()

        # 建立取消按鈕
        cancel_button = QPushButton("取消")
        cancel_button.setMinimumWidth(80)
        cancel_button.clicked.connect(self.reject)  # 連接拒絕信號
        button_layout.addWidget(cancel_button)

        # 建立確定按鈕
        self.ok_button = QPushButton("確定")
        self.ok_button.setMinimumWidth(80)
        self.ok_button.setDefault(True)  # 設為預設按鈕
        self.ok_button.clicked.connect(self.accept)  # 連接接受信號
        button_layout.addWidget(self.ok_button)

        # 添加彈性空間讓按鈕居中
        button_layout.addStretch()

        parent_layout.addWidget(button_container)

    def _get_monospace_font_style(self) -> str:
        """取得等寬字體樣式字串

        提供跨平台的等寬字體回退機制，確保進度條在不同系統上
        都能保持一致的視覺效果。支援FontManager的縮放功能。

        Returns:
            str: CSS樣式字串，包含等寬字體和大小設定
        """
        # 等寬字體回退序列：優先使用常見的高品質等寬字體
        monospace_fonts = [
            "Consolas",           # Windows預設，最佳選擇
            "Monaco",             # macOS預設
            "DejaVu Sans Mono",   # Linux常見
            "Courier New",        # 跨平台備選
            "monospace"           # 系統通用等寬字體
        ]

        # 組合字體家族字串：讓FontManager控制字體大小
        font_family = ", ".join([f"'{font}'" for font in monospace_fonts])

        return f"font-family: {font_family};"

    def _connect_signals(self):
        """連接信號和槽

        當數值輸入框的值改變時，即時更新進度條顯示和總和驗證，
        提供即時的視覺反饋。
        """
        # 為每個數值輸入框連接值變化信號
        for spinbox in self.spinboxes.values():
            # 連接valueChanged信號：數值改變時即時更新顯示
            spinbox.valueChanged.connect(self._update_progress_display)

    def _update_progress_display(self):
        """更新進度條顯示和總和驗證

        計算當前各項目的值並更新文字進度條，同時驗證總和是否為100%，
        控制確定按鈕的啟用狀態。這是整個對話框的核心更新邏輯。
        """
        # 收集當前所有輸入值
        current_values = {}
        total_value = 0

        for item_key, spinbox in self.spinboxes.items():
            value = spinbox.value()
            current_values[item_key] = value
            total_value += value

        # 更新每個項目的進度條顯示
        for item_key, value in current_values.items():
            progress_text = self._create_progress_bar(value, 100)
            self.progress_labels[item_key].setText(progress_text)

        # 更新總和顯示和驗證狀態
        self._update_total_display(total_value)

        # 控制確定按鈕啟用狀態：只有總和=100%時才能確定
        self.ok_button.setEnabled(total_value == 100)

    def _create_progress_bar(self, value: int, max_value: int, bar_length: int = 20) -> str:
        """創建文字進度條

        使用Unicode字符■和□創建視覺化的進度條，
        這是整個對話框最具特色的視覺元素。

        Args:
            value: 當前值
            max_value: 最大值（通常為100）
            bar_length: 進度條總長度（字符數）

        Returns:
            str: 格式化的進度條字串，如 "■■■□□□□□□□ 30%"
        """
        # 計算填充的格數：按比例計算需要填充多少格
        if max_value <= 0:
            filled_length = 0
        else:
            filled_length = int((value / max_value) * bar_length)

        # 確保填充長度在有效範圍內
        filled_length = max(0, min(filled_length, bar_length))

        # 計算空白的格數
        empty_length = bar_length - filled_length

        # 創建進度條字串：■代表已填充，□代表未填充
        filled_part = "■" * filled_length
        empty_part = "□" * empty_length
        percentage_text = f"{value}%"

        # 組合完整的進度條：進度條（移除右側百分比以避免與SpinBox重複）
        return f"{filled_part}{empty_part}"

    def _update_total_display(self, total_value: int):
        """更新總和顯示

        顯示當前總和並提供視覺化的驗證狀態，
        讓用戶清楚了解配置是否有效。

        Args:
            total_value: 當前總和值
        """
        # 根據總和值設定不同的顯示樣式和提示
        if total_value == 100:
            # 總和正確：綠色顯示，顯示勾選符號
            display_text = f"總和: {total_value}% ✓"
            style = "color: #27ae60; font-weight: bold;"
        elif total_value < 100:
            # 總和不足：橙色顯示，顯示向上箭頭
            shortage = 100 - total_value
            display_text = f"總和: {total_value}% (還需 +{shortage}%)"
            style = "color: #f39c12; font-weight: bold;"
        else:
            # 總和超出：紅色顯示，顯示向下箭頭
            excess = total_value - 100
            display_text = f"總和: {total_value}% (超出 -{excess}%)"
            style = "color: #e74c3c; font-weight: bold;"

        # 更新標籤顯示
        self.total_label.setText(display_text)
        self.total_label.setStyleSheet(style)

    def get_values(self) -> Dict[str, int]:
        """取得當前配置的值

        收集所有數值輸入框的當前值，返回標準的配置字典格式。
        這個方法在對話框被接受後調用，提供最終的配置結果。

        Returns:
            Dict[str, int]: 各項目的百分比值字典

        Example:
            >>> dialog = PercentageConfigDialog(parent, schema)
            >>> if dialog.exec_() == QDialog.Accepted:
            ...     values = dialog.get_values()
            ...     # 返回類似: {"original": 70, "formula": 10, "narrow_angle": 20}
        """
        values = {}

        # 收集每個項目的當前值
        for item_key, spinbox in self.spinboxes.items():
            values[item_key] = spinbox.value()

        # 記錄配置結果：有助於調試和監控
        self.logger.info(f"百分比配置完成: {values}")

        return values