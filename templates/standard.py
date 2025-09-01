#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 標準測驗模板
"""

from typing import Dict, List, Any

from reportlab.lib import colors
from reportlab.lib.units import cm, mm

from templates.base import PDFTemplate

class StandardTemplate(PDFTemplate):
    """標準測驗模板
    
    標準的測驗模板，包含題目頁和答案頁。
    題目頁：每頁最多 10 題，每題一個框。
    答案頁：簡答區和詳解區。
    """
    
    def generate_question_page(self, round_num: int, questions: List[Dict[str, Any]]) -> None:
        """生成題目頁
        
        Args:
            round_num: 回數
            questions: 題目列表
        """
        # 繪製頁首
        self.draw_header(round_num)
        
        # 題目空欄位設計
        # 計算每個欄位的尺寸和位置
        box_width = (self.width - 60) / 2
        box_height = (self.height - 150) / 5
        
        for q_idx, question in enumerate(questions):
            q_num = q_idx + 1
            row = (q_num - 1) // 2
            col = (q_num - 1) % 2
            
            x = 30 + col * (box_width + 5)
            y = self.height - 100 - row * (box_height + 5)
            
            self.draw_question_box(x, y, box_width, box_height, q_num, question['question'])
        
        # 繪製頁尾
        self.draw_footer()
        
        # 添加新頁
        self.canvas.showPage()
        
    def generate_answer_page(self, round_num: int, questions: List[Dict[str, Any]]) -> None:
        """生成答案頁
        
        Args:
            round_num: 回數
            questions: 題目列表
        """
        # 標題資訊
        self.canvas.setFont('NotoSansTC-Bold', 12)
        self.canvas.drawString(30, self.height - 30, f"第 {round_num} 回 答案")
        self.canvas.setFont('NotoSansTC', 10)
        self.canvas.drawString(30, self.height - 50, f"生成日期：{self.current_date}")
        
        # 簡答區
        self.canvas.setFont('NotoSansTC-Bold', 12)
        self.canvas.drawString(30, self.height - 80, "簡答：")
        self.canvas.setFont('NotoSansTC', 10)
        
        # 將簡答排成多列
        items_per_row = 5
        for q_idx, question in enumerate(questions):
            q_num = q_idx + 1
            row = (q_num - 1) // items_per_row
            col = (q_num - 1) % items_per_row
            
            x = 30 + col * 100
            y = self.height - 100 - row * 20
            
            answer_text = f"{q_num}. {question.get('answer', '_______')}"
            self.canvas.drawString(x, y, answer_text)
        
        # 詳解區
        self.canvas.setFont('NotoSansTC-Bold', 12)
        self.canvas.drawString(30, self.height - 160, "詳解：")
        
        # 為每個題目提供詳解
        explanation_space = self.height - 180
        items_per_page = min(len(questions), 5)  # 每頁最多顯示5個詳解
        explanation_height = explanation_space / items_per_page
        
        for q_idx, question in enumerate(questions):
            q_num = q_idx + 1
            
            if q_num > items_per_page and q_num % items_per_page == 1:
                # 新增一頁用於更多詳解
                self.canvas.showPage()
                self.canvas.setFont('NotoSansTC-Bold', 12)
                self.canvas.drawString(30, self.height - 30, f"第 {round_num} 回 答案 (續)")
                self.canvas.drawString(30, self.height - 60, "詳解 (續)：")
            
            # 計算當前頁面上的位置
            page_q = ((q_num - 1) % items_per_page) + 1
            y_pos = self.height - 180 - (page_q - 1) * explanation_height
            
            # 題號
            self.canvas.setFont('NotoSansTC-Bold', 10)
            self.canvas.drawString(30, y_pos - 15, f"{q_num}.")
            
            # 寫入詳解內容
            explanation_text = question.get('explanation', '')
            if explanation_text:
                self.canvas.setFont('NotoSansTC', 9)
                
                # 簡單換行處理
                text_width = self.width - 70
                chars_per_line = int(text_width / 5)
                
                lines = []
                for i in range(0, len(explanation_text), chars_per_line):
                    lines.append(explanation_text[i:i+chars_per_line])
                
                for i, line in enumerate(lines):
                    if i < 10:  # 限制行數
                        self.canvas.drawString(45, y_pos - 15 - (i+1)*12, line)
        
        # 繪製頁尾
        self.draw_footer(is_answer_page=True)
