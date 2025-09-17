#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 設定面板
"""

import os
import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QGroupBox, QFormLayout, 
                             QSpinBox, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal

from ui.utils import load_icon

class SettingsWidget(QWidget):
    """設定面板，用於配置測驗的基本設定"""
    
    # 自定義信號
    settingsChanged = pyqtSignal()  # 當設定變更時發出
    generatePdfRequested = pyqtSignal(str, str, list, int, int)  # 請求生成 PDF
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 載入圖示
        self.load_icons()
        
        # 初始化 UI
        self.initUI()
        
    def load_icons(self):
        """載入所有需要的圖示"""
        self.icon_folder = load_icon('folder.svg')
        self.icon_shuffle = load_icon('shuffle.svg')
        self.icon_distribute = load_icon('bar-chart-2.svg')
        self.icon_generate = load_icon('file-text.svg')
        
    def initUI(self):
        """初始化使用者介面"""
        # 主佈局
        self.main_layout = QVBoxLayout(self)
        
        # 標題
        title = QLabel("測驗設定")
        title.setObjectName("title")
        self.main_layout.addWidget(title)
        
        # --- 基本資訊群組 ---
        self.create_basic_info_group()
        
        # --- 測驗生成設定群組 ---
        self.create_generation_settings_group()
        
        # --- 統計和生成按鈕區域 ---
        self.create_stats_and_generate_area()
        
        # 添加彈性空間
        self.main_layout.addStretch()
        
        # 連接信號
        self.connect_signals()
        
    def create_basic_info_group(self):
        """創建基本資訊群組"""
        basic_group = QGroupBox("基本資訊")
        basic_layout = QFormLayout()
        basic_layout.setVerticalSpacing(12)

        # 設定測驗標題預設值
        self.test_title = QLineEdit()
        self.test_title.setPlaceholderText("例：國小三年級下學期數學測驗")
        self.test_title.setText("數學計算練習")
        
        # 設定PDF檔案名稱預設值，使用當前日期和時間（不含年份）
        now = datetime.datetime.now()
        default_filename = f"{now.strftime('%m%d_%H%M')}practice.pdf"
        self.file_name = QLineEdit()
        self.file_name.setPlaceholderText("例：三年級數學測驗_20250330")
        self.file_name.setText(default_filename)

        path_layout = QHBoxLayout()
        self.output_path = QLineEdit()
        self.output_path.setPlaceholderText("選擇保存位置...")
        self.output_path.setText(os.getcwd())  # 設定輸出路徑預設為工作區
        self.browse_btn = QPushButton()
        self.browse_btn.setIcon(self.icon_folder)
        self.browse_btn.setToolTip("瀏覽輸出路徑")
        path_layout.addWidget(self.output_path)
        path_layout.addWidget(self.browse_btn)

        basic_layout.addRow("測驗標題:", self.test_title)
        basic_layout.addRow("PDF檔案名稱:", self.file_name)
        basic_layout.addRow("輸出路徑:", path_layout)
        basic_group.setLayout(basic_layout)
        self.main_layout.addWidget(basic_group)
        
    def create_generation_settings_group(self):
        """創建測驗生成設定群組"""
        gen_group = QGroupBox("測驗生成設定")
        gen_outer_layout = QVBoxLayout(gen_group)

        # 行1: 回數和每回題數
        rounds_layout = QHBoxLayout()
        rounds_layout.setSpacing(10)

        # 回數標籤和微調框
        rounds_label = QLabel("回數:")
        self.num_rounds = QSpinBox()
        self.num_rounds.setRange(1, 100)
        self.num_rounds.setValue(1)
        self.num_rounds.setFixedWidth(80)

        # 每回題數標籤和微調框
        ques_label = QLabel("每回題數:")
        self.ques_per_round = QSpinBox()
        self.ques_per_round.setRange(1, 50)
        self.ques_per_round.setValue(1)
        self.ques_per_round.setFixedWidth(80)

        rounds_layout.addWidget(rounds_label)
        rounds_layout.addWidget(self.num_rounds)
        rounds_layout.addStretch(1)
        rounds_layout.addWidget(ques_label)
        rounds_layout.addWidget(self.ques_per_round)

        gen_outer_layout.addLayout(rounds_layout)

        # 隨機選擇佈局
        random_check_layout = QHBoxLayout()
        random_check_label = QLabel("隨機選擇題型數:")
        self.random_check_count = QSpinBox()
        self.random_check_count.setRange(1, 500)
        self.random_check_count.setValue(5)
        self.random_check_count.setFixedWidth(80)
        self.random_check_count.setToolTip("要隨機勾選的題型數量")
        self.random_check_btn = QPushButton(" 隨機勾選")
        self.random_check_btn.setIcon(self.icon_shuffle)
        self.random_check_btn.setToolTip("從所有題型中隨機勾選指定數量\n(會先取消所有已選項目)")
        random_check_layout.addWidget(random_check_label)
        random_check_layout.addWidget(self.random_check_count)
        random_check_layout.addStretch(1)
        random_check_layout.addWidget(self.random_check_btn)
        gen_outer_layout.addLayout(random_check_layout)

        # 平均分配按鈕
        self.distribute_even_btn = QPushButton(" 平均分配題數")
        self.distribute_even_btn.setIcon(self.icon_distribute)
        self.distribute_even_btn.setToolTip("將總題數平均分配給目前已勾選的題型")
        self.distribute_even_btn.setEnabled(False)
        gen_outer_layout.addWidget(self.distribute_even_btn)

        self.main_layout.addWidget(gen_group)
        
    def create_stats_and_generate_area(self):
        """創建統計和生成按鈕區域"""
        stats_layout = QHBoxLayout()
        stats_group = QGroupBox("測驗統計")
        stats_inner = QHBoxLayout()
        stats_inner.setSpacing(15)
        self.selected_topics_label = QLabel("已選題型：0 種")
        self.total_questions_label = QLabel("總題數：0 題")
        stats_inner.addWidget(self.selected_topics_label)
        stats_inner.addWidget(self.total_questions_label)
        stats_group.setLayout(stats_inner)

        self.generate_btn = QPushButton(" 生成 PDF")
        self.generate_btn.setIcon(self.icon_generate)
        self.generate_btn.setObjectName("generateBtn")
        self.generate_btn.setEnabled(False)
        self.generate_btn.setMinimumHeight(50)

        stats_layout.addWidget(stats_group, 1)
        stats_layout.addWidget(self.generate_btn, 1)
        self.main_layout.addLayout(stats_layout)
        
    def connect_signals(self):
        """連接所有信號和槽"""
        self.browse_btn.clicked.connect(self.browse_output_path)
        self.test_title.textChanged.connect(self.settingsChanged.emit)
        self.file_name.textChanged.connect(self.settingsChanged.emit)
        self.output_path.textChanged.connect(self.settingsChanged.emit)
        self.num_rounds.valueChanged.connect(self.settingsChanged.emit)
        self.ques_per_round.valueChanged.connect(self.settingsChanged.emit)
        self.generate_btn.clicked.connect(self.request_generate_pdf)
        
    def browse_output_path(self):
        """瀏覽並選擇輸出路徑"""
        directory = QFileDialog.getExistingDirectory(self, "選擇輸出目錄")
        if directory:
            self.output_path.setText(directory)
            
    def update_statistics(self, selected_count, total_questions):
        """更新統計資訊和按鈕狀態
        
        Args:
            selected_count (int): 已選題型數
            total_questions (int): 總題數
        """
        self.selected_topics_label.setText(f"已選題型：{selected_count} 種")
        self.total_questions_label.setText(f"總題數：{total_questions} 題")

        # 更新按鈕啟用狀態
        can_distribute = selected_count > 0 and (self.num_rounds.value() * self.ques_per_round.value()) > 0
        self.distribute_even_btn.setEnabled(can_distribute)

        can_generate = (selected_count > 0 and
                        total_questions > 0 and  # 確保題數 > 0
                        self.output_path.text().strip() != "" and
                        self.file_name.text().strip() != "")
        self.generate_btn.setEnabled(can_generate)
        
    def get_total_questions(self):
        """獲取總題數設定
        
        Returns:
            int: 總題數 (回數 * 每回題數)
        """
        return self.num_rounds.value() * self.ques_per_round.value()
        
    def get_random_check_count(self):
        """獲取隨機勾選數量
        
        Returns:
            int: 隨機勾選數量
        """
        return self.random_check_count.value()
        
    def request_generate_pdf(self):
        """請求生成 PDF"""
        # 檢查輸出路徑是否存在
        output_dir = self.output_path.text().strip()
        if not os.path.isdir(output_dir):
            QMessageBox.critical(self, "路徑錯誤", f"指定的輸出路徑不存在：\n{output_dir}")
            return
            
        # 檢查檔案名稱
        file_name_base = self.file_name.text().strip()
        if not file_name_base:
            QMessageBox.warning(self, "無法生成", "請輸入有效的 PDF 檔案名稱。")
            return
            
        # 添加 .pdf 副檔名（如果缺少）
        if not file_name_base.lower().endswith(".pdf"):
            file_name = file_name_base + ".pdf"
        else:
            file_name = file_name_base
            
        full_path = os.path.join(output_dir, file_name)
        
        # 發出信號請求生成 PDF
        self.generatePdfRequested.emit(
            full_path,
            self.test_title.text(),
            [],  # 選定的題型數據，將由主視窗填充
            self.num_rounds.value(),
            self.ques_per_round.value()
        )
