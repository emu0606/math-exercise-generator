#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 基礎模板類別
"""

import os
import datetime
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Tuple, Optional, Union

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from data.quotes import get_random_quote

class PDFTemplate(ABC):
    """PDF 模板基礎類別
    
    所有具體 PDF 模板都應該繼承此類別並實現其抽象方法。
    """
    
    def __init__(self, output_path: str, title: str, options: Dict[str, Any] = None):
        """初始化模板
        
        Args:
            output_path: 輸出 PDF 檔案的完整路徑
            title: 測驗標題
            options: 其他選項，如頁面大小、字體等
        """
        self.output_path = output_path
        self.title = title
        self.options = options or {}
        self.page_size = self.options.get('page_size', A4)
        self.width, self.height = self.page_size
        self.canvas = None
        self.current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # 註冊字體
        self._register_fonts()
        
    def _register_fonts(self):
        """註冊所需的字體"""
        try:
            assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'assets')
            fonts_dir = os.path.join(assets_dir, 'fonts')
            
            pdfmetrics.registerFont(TTFont('NotoSansTC', os.path.join(fonts_dir, 'NotoSansTC-Regular.ttf')))
            pdfmetrics.registerFont(TTFont('NotoSansTC-Bold', os.path.join(fonts_dir, 'NotoSansTC-Bold.ttf')))
        except Exception as e:
            print(f"警告: 無法註冊字體: {e}")
            
    def generate(self, questions: List[Dict[str, Any]], rounds: int, questions_per_round: int) -> bool:
        """生成 PDF 測驗檔案
        
        Args:
            questions: 題目列表，每個題目是一個字典，至少包含 'question', 'answer', 'explanation' 鍵
            rounds: 回數
            questions_per_round: 每回題數
            
        Returns:
            是否成功生成 PDF
        """
        try:
            # 創建 PDF
            self.canvas = canvas.Canvas(self.output_path, pagesize=self.page_size)
            
            # 處理生成多回測驗
            for round_num in range(1, rounds + 1):
                # 為當前回次選擇題目
                start_idx = (round_num - 1) * questions_per_round
                end_idx = start_idx + questions_per_round
                round_questions = questions[start_idx:end_idx]
                
                # 如果題目不夠，重複使用現有題目
                while len(round_questions) < questions_per_round:
                    round_questions.extend(questions)
                    round_questions = round_questions[:questions_per_round]
                
                # 生成題目頁
                self.generate_question_page(round_num, round_questions)
                
                # 生成答案頁
                self.generate_answer_page(round_num, round_questions)
                
                # 如果不是最後一回，添加新頁
                if round_num < rounds:
                    self.canvas.showPage()
            
            # 保存 PDF
            self.canvas.save()
            return True
        except Exception as e:
            print(f"生成 PDF 時發生錯誤: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    @abstractmethod
    def generate_question_page(self, round_num: int, questions: List[Dict[str, Any]]) -> None:
        """生成題目頁
        
        Args:
            round_num: 回數
            questions: 題目列表
        """
        pass
        
    @abstractmethod
    def generate_answer_page(self, round_num: int, questions: List[Dict[str, Any]]) -> None:
        """生成答案頁
        
        Args:
            round_num: 回數
            questions: 題目列表
        """
        pass
        
    def draw_header(self, round_num: int) -> None:
        """繪製頁首
        
        Args:
            round_num: 回數
        """
        # 大標題
        self.canvas.setFont('NotoSansTC-Bold', 20)
        self.canvas.drawCentredString(self.width/2, self.height - 30, self.title)
        
        # 回數、日期、姓名欄位
        self.canvas.setFont('NotoSansTC', 12)
        date_y = self.height - 50
        round_text = f"第 {round_num} 回"
        self.canvas.drawRightString(self.width - 30, date_y, round_text)
        self.canvas.drawRightString(self.width - 30, date_y - 20, f"日期：_________________")
        self.canvas.drawRightString(self.width - 30, date_y - 40, f"姓名：_________________")
        
    def draw_footer(self, is_answer_page: bool = False) -> None:
        """繪製頁尾
        
        Args:
            is_answer_page: 是否為答案頁
        """
        self.canvas.setFont('NotoSansTC', 9)
        quote = get_random_quote()
        self.canvas.drawCentredString(self.width/2, 20, f"{quote}")
        self.canvas.drawCentredString(self.width/2, 10, f"生成日期：{self.current_date}")
        
    def draw_question_box(self, x: float, y: float, width: float, height: float, 
                          question_num: int, question_text: str) -> None:
        """繪製題目框
        
        Args:
            x: 左上角 x 座標
            y: 左上角 y 座標
            width: 寬度
            height: 高度
            question_num: 題號
            question_text: 題目文字
        """
        # 繪製圓角四邊形
        self.canvas.setStrokeColor(colors.black)
        self.canvas.setFillColor(colors.white)
        self.canvas.roundRect(x, y - height, width, height, 5, stroke=1, fill=1)
        
        # 題號和題目內容
        self.canvas.setFont('NotoSansTC-Bold', 10)
        self.canvas.setFillColor(colors.black)
        self.canvas.drawString(x + 5, y - 15, f"{question_num}.")
        
        # 檢查是否包含LaTeX格式的數學公式（$符號）
        if '$' in question_text:
            try:
                from templates.latex_utils import render_latex_to_image
                
                # 提取LaTeX公式
                import re
                latex_pattern = r'\$(.*?)\$'
                matches = re.findall(latex_pattern, question_text)
                
                if matches:
                    # 替換LaTeX公式為佔位符
                    placeholder = "[LATEX]"
                    for match in matches:
                        question_text = question_text.replace(f"${match}$", placeholder)
                    
                    # 分割文本
                    parts = question_text.split(placeholder)
                    
                    # 繪製文本和LaTeX公式
                    current_y = y - 15
                    current_x = x + 20
                    
                    for i, part in enumerate(parts):
                        # 繪製普通文本
                        if part:
                            self.canvas.setFont('NotoSansTC', 9)
                            self.canvas.drawString(current_x, current_y, part)
                            current_x += self.canvas.stringWidth(part, 'NotoSansTC', 9)
                        
                        # 繪製LaTeX公式（如果不是最後一部分）
                        if i < len(matches):
                            latex_img = render_latex_to_image(matches[i], fontsize=10)
                            img_width, img_height = latex_img.getSize()
                            
                            # 檢查是否需要換行
                            if current_x + img_width > x + width - 10:
                                current_x = x + 20
                                current_y -= 15
                            
                            self.canvas.drawImage(latex_img, current_x, current_y - img_height * 0.7, width=img_width, height=img_height)
                            current_x += img_width
                            
                            # 檢查是否需要換行
                            if current_x > x + width - 50:
                                current_x = x + 20
                                current_y -= 15
                    
                    return
            except Exception as e:
                print(f"渲染LaTeX時發生錯誤: {e}")
                # 如果發生錯誤，回退到普通文本渲染
        
        # 普通文本渲染（如果沒有LaTeX或渲染失敗）
        self.canvas.setFont('NotoSansTC', 9)
        # 簡單的文本換行邏輯
        text_width = width - 15
        chars_per_line = int(text_width / 5)  # 估計每行可容納的字元數
        
        lines = []
        for i in range(0, len(question_text), chars_per_line):
            lines.append(question_text[i:i+chars_per_line])
        
        for i, line in enumerate(lines):
            if i < 5:  # 限制行數
                self.canvas.drawString(x + 20, y - 15 - (i+1)*12, line)
