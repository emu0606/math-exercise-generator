#!/usr/bin/env python

# -*- coding: utf-8 -*-



"""

數學測驗生成器 - 主視窗類別

"""



import sys
import os
import json
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QSplitter, QScrollArea, QFrame, QMessageBox,
                             QLineEdit, QPushButton, QFileDialog)
from PyQt5.QtCore import Qt


from ui.utils import load_icon

from ui.category_widget import CategoryWidget

from ui.settings_widget import SettingsWidget

from utils.orchestration.pdf_orchestrator import generate_pdf_with_progress
from utils.core.registry import registry



# --- 常數定義 ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
STYLE_SHEET_PATH = os.path.join(ASSETS_DIR, 'style.qss')
DATA_DIR = os.path.join(BASE_DIR, 'data')
CATEGORIES_PATH = os.path.join(DATA_DIR, 'categories.json')


class MathTestGenerator(QMainWindow):

    """數學測驗生成器主視窗類別"""

    

    def __init__(self):

        super().__init__()

        

        # 套用外部樣式表

        self.load_stylesheet()

        

        # 初始化 UI

        self.initUI()

        

        # 填充範例資料

        self.populate_sample_data()

        

        # 連接信號

        self.connect_signals()

        

    def load_stylesheet(self):

        """載入並套用樣式表"""

        try:

            with open(STYLE_SHEET_PATH, "r", encoding="utf-8") as f:

                css = f.read()

                

            # 確保勾選框樣式正確設置

            css = css.replace("QCheckBox::indicator:unchecked {", 

                             """QCheckBox::indicator:unchecked {

                                 image: url(assets/icons/square.svg);""")

            css = css.replace("QCheckBox::indicator:checked {", 

                             """QCheckBox::indicator:checked {

                                 image: url(assets/icons/check-square.svg);""")

            css = css.replace("QCheckBox::indicator:partially-checked {", 

                             """QCheckBox::indicator:indeterminate {

                                 image: url(assets/icons/minus-square.svg);""")

            

            self.setStyleSheet(css)

        except FileNotFoundError:

            print(f"警告: {STYLE_SHEET_PATH} 未找到，使用預設樣式。")



    def initUI(self):

        """初始化使用者介面"""

        # --- 基本視窗設定 ---

        self.setWindowTitle('數學測驗生成器')

        self.setGeometry(100, 100, 1250, 750)



        # --- 中央元件和主佈局 ---

        central_widget = QWidget()

        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        main_layout.setContentsMargins(10, 10, 10, 10)



        # --- 分隔器 ---

        splitter = QSplitter(Qt.Horizontal)



        # --- 左側面板 (題型選擇) ---

        left_panel = QWidget()

        left_layout = QVBoxLayout(left_panel)

        left_layout.setContentsMargins(0, 0, 0, 0)

        

        # 搜尋欄

        search_layout = QHBoxLayout()

        self.search_input = QLineEdit()

        self.search_input.setPlaceholderText("搜尋題型...")

        search_btn = QPushButton()

        search_btn.setIcon(load_icon('search.svg'))

        search_btn.setObjectName("iconButton")

        search_btn.setToolTip("搜尋題型")

        search_layout.addWidget(self.search_input)

        search_layout.addWidget(search_btn)

        left_layout.addLayout(search_layout)

        

        # 類別選擇元件

        scroll_area = QScrollArea()

        scroll_area.setWidgetResizable(True)

        scroll_area.setFrameShape(QFrame.NoFrame)

        

        self.category_widget = CategoryWidget()

        scroll_area.setWidget(self.category_widget)

        left_layout.addWidget(scroll_area)



        # --- 右側面板 (測驗設定) ---

        right_panel = QWidget()

        right_layout = QVBoxLayout(right_panel)

        right_layout.setContentsMargins(0, 0, 0, 0)

        

        self.settings_widget = SettingsWidget()

        right_layout.addWidget(self.settings_widget)



        # --- 添加面板到分隔器 ---

        splitter.addWidget(left_panel)

        splitter.addWidget(right_panel)



        # 設定初始分隔器大小

        total_width = self.width() - 40

        left_width = int(total_width * 0.45)

        right_width = total_width - left_width

        splitter.setSizes([left_width, right_width])



        main_layout.addWidget(splitter)

        

    def load_categories(self):
        """從註冊器加載分類數據"""
        categories_data = registry.get_categories()
        return categories_data

        

    def populate_sample_data(self):
        """填充分類資料"""
        # 從註冊器加載分類
        categories_data = self.load_categories()

        # 轉換為 UI 需要的格式
        categories = []
        for category, subcategories in categories_data.items():
            categories.append({
                "name": category,
                "subcategories": subcategories
            })

        self.category_widget.populate_categories(categories)

        

    def connect_signals(self):

        """連接所有信號和槽"""

        # 搜尋欄

        self.search_input.textChanged.connect(self.category_widget.filter_topics)

        

        # 類別選擇元件信號

        self.category_widget.categoryChanged.connect(self.update_statistics)

        

        # 設定元件信號

        self.settings_widget.settingsChanged.connect(self.update_statistics)

        self.settings_widget.generatePdfRequested.connect(self.generate_pdf)

        

        # 隨機勾選和平均分配按鈕

        self.settings_widget.random_check_btn.clicked.connect(self.randomly_check_subcategories)

        self.settings_widget.distribute_even_btn.clicked.connect(self.distribute_evenly)

        

    def update_statistics(self):

        """更新統計資訊和按鈕狀態"""

        selected_count, total_questions, _ = self.category_widget.get_selected_data()

        self.settings_widget.update_statistics(selected_count, total_questions)

        

    def randomly_check_subcategories(self):

        """隨機選擇指定數量的子類別"""

        count = self.settings_widget.get_random_check_count()

        success = self.category_widget.randomly_check_subcategories(count)

        if success:

            QMessageBox.information(self, "隨機勾選完成", f"已隨機勾選 {count} 種題型。")

            

    def distribute_evenly(self):

        """將總題數平均分配給已勾選的子類別"""

        total_questions = self.settings_widget.get_total_questions()

        success = self.category_widget.distribute_evenly(total_questions)

        if success:

            selected_count, _, _ = self.category_widget.get_selected_data()

            QMessageBox.information(self, "分配完成", f"已將 {total_questions} 題平均分配給 {selected_count} 種題型。")

            

    def generate_pdf(self, output_path, test_title, _, rounds, questions_per_round):

        """生成 PDF 測驗檔案"""

        # 獲取選定的題型數據

        _, _, selected_data = self.category_widget.get_selected_data()

        

        # 調用 PDF 生成函數

        try:

            success = generate_pdf_with_progress(output_path, test_title, selected_data, 
                                               rounds, questions_per_round, 
                                               progress_callback=None, template_name="standard")
            
            if success:
                QMessageBox.information(self, "生成成功", f"PDF 測驗已成功生成！\n路徑: {output_path}")
            else:
                QMessageBox.critical(self, "生成失敗", "PDF 生成過程中發生未知錯誤")

        except Exception as e:

            QMessageBox.critical(self, "生成失敗", f"生成 PDF 時發生錯誤：\n{e}")

            import traceback

            traceback.print_exc()  # 在控制台印出詳細錯誤訊息
