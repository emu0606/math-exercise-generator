#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - LaTeX 生成器
生成 LaTeX 格式的題目、簡答和詳解頁面
"""

import re
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime

# 導入圖形生成器
import figures

class LaTeXGenerator:
    """LaTeX 生成器
    
    生成 LaTeX 格式的題目、簡答和詳解頁面。
    使用 TikZ 繪製題目框，使用 xeCJK 處理中文。
    """
    
    def __init__(self):
        """初始化 LaTeX 生成器"""
        # A4 紙大小: 21.0 x 29.7厘米
        self.page_width = 21.0  # 厘米
        self.page_height = 29.7  # 厘米
        self.margin = 2.0  # 邊距（厘米）
        
        # 計算可用寬度
        self.usable_width = self.page_width - 2 * self.margin  # 可用寬度(厘米)
        
        # 網格定義
        self.grid_width = 4  # 列數
        self.grid_height = 10  # 行數
        
        # 計算單元格尺寸
        self.gap = 0.4  # 間隔（厘米）
        total_gap_width = (self.grid_width - 1) * self.gap
        self.unit_width = (self.usable_width - total_gap_width) / self.grid_width
        self.unit_height = self.unit_width * 0.5 # 高寬比約為0.618（黃金比例）可能得放棄
        
        # 當前日期
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        #確認真的是在執行這個檔案
        print("***** EXECUTING THIS LaTeXGenerator __init__ *****")
		
		
    def generate_question_tex(self, layout_results: List[Dict[str, Any]], test_title: str, questions_per_round: int = 0) -> str:
        """生成題目頁 LaTeX 內容
        
        Args:
            layout_results: 佈局結果，包含每個題目的頁碼、位置和尺寸
            test_title: 測驗標題
            questions_per_round: 每回題數
            
        Returns:
            題目頁 LaTeX 內容
        """
        # 獲取最大頁碼
        max_page = max(item['page'] for item in layout_results)
        
        # 按頁碼分組
        pages = {}
        for item in layout_results:
            page = item['page']
            if page not in pages:
                pages[page] = []
            pages[page].append(item)
        
        # 生成 LaTeX 內容
        content = self._get_preamble(test_title)
        content += r"\begin{document}" + "\n"
        
        # 生成每一頁
        for page in range(1, max_page + 1):
            if page > 1:
                content += r"\newpage" + "\n"
            
            # 頁首 - 獲取回次
            # 直接從 layout_results 中獲取回次信息
            first_item_on_page = next((item for item in layout_results if item['page'] == page), None)
            if first_item_on_page:
                round_num = first_item_on_page['round_num']
            else:
                # 如果頁面為空（理論上不應發生），預設為第一回
                round_num = 1
                
            content += self._generate_page_header(round_num) # 傳遞回次
            
            # 使用 TikZ 繪製題目框
            content += r"\begin{center}" + "\n"
            content += r"\begin{tikzpicture}" + "\n"
            
            # 繪製當前頁的題目框
            if page in pages:
                for item in pages[page]:
                    # 計算位置和尺寸
                    row = item['row']
                    col = item['col']
                    width_cells = item['width_cells']
                    height_cells = item['height_cells']
                    
                    # 計算 TikZ 座標
                    x = col * (self.unit_width + self.gap)
                    y = -row * (self.unit_height + self.gap)
                    w = width_cells * self.unit_width + (width_cells - 1) * self.gap
                    h = height_cells * self.unit_height + (height_cells - 1) * self.gap
                    
                    # 題號 - 使用回內題號
                    question_num = item['question_num_in_round']
                    
                    # 題目內容
                    question_text = item.get('question', '')
                    
                    # 檢查是否有圖形數據
                    figure_data_question = item.get('figure_data_question')
                    figure_content = ""
                    print(f"DEBUG: [generate_question_tex] Found figure_data for question {question_num}") # DEBUG PRINT infrontof ifsection
                    if figure_data_question:
                        print(f"DEBUG: [generate_question_tex] Found figure_data for question {question_num}. Data: {repr(figure_data_question)}") # DEBUG PRINT A
                        print(f"DEBUG: [generate_question_tex] Attempting to call _render_figure for question {question_num}...") # DEBUG PRINT B
                        try:
                            figure_content = self._render_figure(figure_data_question)
                            print(f"DEBUG: [generate_question_tex] _render_figure successfully returned for question {question_num}. Content: {repr(figure_content)}") # DEBUG PRINT C
                        except Exception as e:
                            import traceback
                            print(f"ERROR: [generate_question_tex] Exception occurred while calling _render_figure for question {question_num}: {str(e)}") # DEBUG PRINT D
                            traceback.print_exc() # Print full traceback
                            figure_content = f"\\textbf{{圖形渲染錯誤: {str(e)}}}" # Provide error message in LaTeX
                    
                    # 繪製圓角矩形和題目內容
                    content += f"  % 題目 {question_num}\n"
                    content += f"  \\draw[rounded corners=3pt, thick] ({x}, {y}) rectangle ({x+w}, {y-h});\n"
                    content += f"  \\node[anchor=north west, text width={w-0.4}cm, inner sep=0.2cm] at ({x}, {y}) {{\n"
                    
                    # 添加題號和題目文字
                    formatted_question = self._format_latex_content(question_text)
                    content += f"    \\textbf{{{question_num}.}} {formatted_question}\n"
                    
                    # 如果有圖形，添加到題目中
                    if figure_content:
                        # Use string concatenation instead of f-string to insert figure_content
                        content += "    \n    \\vspace{0.3cm}\n    \\begin{center}\n    " + figure_content + "\n    \\end{center}\n"
                    
                    content += f"  }};\n\n"
            
            content += r"\end{tikzpicture}" + "\n"
            content += r"\end{center}" + "\n"
            
            # 頁尾
            content += self._generate_page_footer()
        
        content += r"\end{document}" + "\n"
        
        return content
    
    def generate_answer_tex(self, questions: List[Dict[str, Any]], test_title: str, questions_per_round: int = 0) -> str:
        """生成簡答頁 LaTeX 內容
        
        Args:
            questions: 題目列表
            test_title: 測驗標題
            questions_per_round: 每回題數
            
        Returns:
            簡答頁 LaTeX 內容
        """
        # 生成 LaTeX 內容
        content = self._get_preamble(test_title)
        content += r"\begin{document}" + "\n"
        
        # 標題
        content += r"\begin{center}" + "\n"
        content += r"{\Large \textbf{" + test_title + r" - 簡答}}" + "\n"
        content += r"\end{center}" + "\n\n"
        
        # 生成日期
        content += r"\noindent 生成日期：" + self.current_date + r"\hfill" + "\n\n"
        
        # 簡答列表，分回展示
        current_round = -1
        
        for i, question in enumerate(questions):
            # 計算回數和回內題號
            if questions_per_round > 0:
                round_num = (i // questions_per_round) + 1
                question_num_in_round = (i % questions_per_round) + 1
            else:
                round_num = 1
                question_num_in_round = i + 1
            
            # 如果換到新的一回，新增回標題和分隔線
            if round_num != current_round:
                # 如果不是第一回，先結束上一個 enumerate 環境
                if current_round != -1:
                    content += r"\end{enumerate}" + "\n\n"
                
                # 若不是第一回，添加分隔線
                if current_round != -1 and round_num > 1:
                    content += r"\begin{center}\rule{0.9\linewidth}{0.5pt}\end{center}" + "\n\n"
                
                # 開始新的一回
                content += f"\\subsection*{{第{round_num}回}}\n\n"
                content += r"\begin{enumerate}[label=\textbf{\arabic*.}]" + "\n"
                current_round = round_num
            
            answer = question.get('answer', '')
            content += f"  \\item \\answerbox{{{self._format_latex_content(answer)}}}\n"
        
        # 結束最後一個 enumerate 環境
        if current_round != -1:
            content += r"\end{enumerate}" + "\n"
        
        # 頁尾
        content += self._generate_page_footer()
        
        content += r"\end{document}" + "\n"
        
        return content
    
    def generate_explanation_tex(self, questions: List[Dict[str, Any]], test_title: str, questions_per_round: int = 0) -> str:
        """生成詳解頁 LaTeX 內容
        
        Args:
            questions: 題目列表
            test_title: 測驗標題
            questions_per_round: 每回題數
            
        Returns:
            詳解頁 LaTeX 內容
        """
        # 生成 LaTeX 內容
        content = self._get_preamble(test_title)
        content += r"\begin{document}" + "\n"
        
        # 標題
        content += r"\begin{center}" + "\n"
        content += r"{\Large \textbf{" + test_title + r" - 詳解}}" + "\n"
        content += r"\end{center}" + "\n\n"
        
        # 生成日期
        content += r"\noindent 生成日期：" + self.current_date + r"\hfill" + "\n\n"
        
        # 詳解內容，按回分組
        current_round = -1
        
        for i, question in enumerate(questions):
            # 計算回數和回內題號
            if questions_per_round > 0:
                round_num = (i // questions_per_round) + 1
                question_num_in_round = (i % questions_per_round) + 1
            else:
                round_num = 1
                question_num_in_round = i + 1
            
            # 如果換到新的一回，新增回標題和分隔線
            if round_num != current_round:
                # 若不是第一回，添加分隔線
                if current_round != -1 and round_num > 1:
                    content += r"\begin{center}\rule{0.9\linewidth}{0.5pt}\end{center}" + "\n\n"
                
                # 開始新的一回
                content += f"\\subsection*{{第{round_num}回詳解}}\n\n"
                content += r"\begin{multicols}{2}" + "\n"
                current_round = round_num
            
            explanation = question.get('explanation', '')
            
            # 檢查是否有圖形數據
            figure_data_explanation = question.get('figure_data_explanation')
            figure_content = ""
            if figure_data_explanation:
                try:
                    figure_content = self._render_figure(figure_data_explanation)
                except Exception as e:
                    print(f"警告：渲染詳解圖形時出錯: {str(e)}")
            
            # 格式化詳解內容
            formatted_explanation = self._format_latex_content(explanation)
            
            # 構建詳解內容
            explanation_content = f"\\textbf{{{question_num_in_round}.}} {formatted_explanation}"
            
            # 如果有圖形，添加到詳解中
            if figure_content:
                explanation_content += f"\n\n\\vspace{{0.3cm}}\n\\begin{{center}}\n{figure_content}\n\\end{{center}}"
            
            # 添加到詳解框中
            content += f"\\explanationbox{{{explanation_content}}}\n\n"
            content += r"\vspace{1em}" + "\n\n"  # 題目間空一行，不用分隔線

            # 如果是當前回的最後一題，結束 multicols
            next_question_round = -1
            if i + 1 < len(questions):
                if questions_per_round > 0:
                    next_question_round = ((i + 1) // questions_per_round) + 1
                else:
                    next_question_round = 1
            
            if next_question_round != current_round:
                content += r"\end{multicols}" + "\n\n"
        
        # 確保所有 multicols 環境都已關閉
        if r"\begin{multicols}" in content.splitlines()[-10:] and r"\end{multicols}" not in content.splitlines()[-5:]:
            content += r"\end{multicols}" + "\n\n"
        
        # 頁尾
        content += self._generate_page_footer()
        
        content += r"\end{document}" + "\n"
        
        return content
    
    def _get_preamble(self, title: str) -> str:
        """獲取 LaTeX 文檔的前導區
        
        Args:
            title: 文檔標題
            
        Returns:
            LaTeX 前導區內容
        """
        preamble = r"""\documentclass[a4paper,11pt]{article}
\usepackage{xeCJK}
\usepackage[margin=1.8cm]{geometry}
\usepackage{tikz}
\usepackage{amsmath,amssymb}
\usepackage{multicol}
\usepackage{enumitem}
\usepackage{fancyhdr}
\usepackage{xcolor}
\usepackage{mdframed}
\usepackage{tcolorbox}
\usepackage{fontspec}

% 設定字體
% \setCJKmainfont[BoldFont={Noto Sans TC Bold}]{Noto Sans TC}
% \setmainfont[BoldFont={Noto Sans Bold}]{Noto Sans}
% \setmonofont{Noto Sans Mono}
\setCJKmainfont{Noto Sans TC}
\setmainfont{Noto Sans TC}
\setmonofont{Noto Sans TC}




% 全局字體設置
\renewcommand{\normalsize}{\fontsize{11pt}{15pt}\selectfont}
\renewcommand{\large}{\fontsize{14pt}{18pt}\selectfont}
\renewcommand{\Large}{\fontsize{16pt}{20pt}\selectfont}
\renewcommand{\huge}{\fontsize{20pt}{24pt}\selectfont}

% 數學字體設置與正文一致
\everymath{\mathsf{\xdef\mysf{\mathgroup\the\mathgroup\relax}}\mysf}

% 設定頁面樣式
\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}
\fancyfoot[C]{\thepage}

% 設定段落間距
\setlength{\parskip}{0.5em}
\setlength{\parindent}{0em}

% 設定列表樣式
\setlist[enumerate]{leftmargin=*,labelsep=0.5em,topsep=0.3em,itemsep=0.2em}

% 自定義環境
\newcommand{\answerbox}[1]{%
  \begin{tcolorbox}[colback=gray!5,colframe=gray!40,arc=2mm,boxrule=0.5pt]
    #1
  \end{tcolorbox}
}

\newcommand{\explanationbox}[1]{%
  \begin{tcolorbox}[colback=blue!5,colframe=blue!30,arc=2mm,boxrule=0.5pt]
    #1
  \end{tcolorbox}
}

% 設定標題樣式
\usepackage{titlesec}
\titleformat{\subsection}
  {\normalfont\large\bfseries}{\thesubsection}{1em}{}
\titlespacing*{\subsection}{0pt}{2em}{1em}

% 設定標題
\title{\huge """ + title + r"""}
\author{\large 數學測驗生成器}
\date{\large \today}

"""
        return preamble
    
    def _generate_page_header(self, round_num: int) -> str:
        """生成頁首
        
        Args:
            round_num: 回數 (由調用者計算好傳入)
            
        Returns:
            頁首 LaTeX 內容
        """
        header = r"\noindent 第" + str(round_num) + r"回 \hfill \_\_\_月\_\_\_\_日 \hfill 姓名：\_\_\_\_\_\_\_\_\_" + "\n\n"
        return header
    
    def _generate_page_footer(self) -> str:
        """生成頁尾
        
        Returns:
            頁尾 LaTeX 內容
        """
        footer = r"\vfill" + "\n"
        footer += r"\begin{center}" + "\n"
        footer += r"\small{生成日期：" + self.current_date + r"}" + "\n"
        footer += r"\end{center}" + "\n"
        return footer
    
    def _format_latex_content(self, content: str) -> str:
        """格式化 LaTeX 內容
        
        處理 HTML 標籤和其他格式化問題
        
        Args:
            content: 原始內容
            
        Returns:
            格式化後的 LaTeX 內容
        """
        if not content:
            return ""
        
        # 替換 HTML 換行標籤為 LaTeX 換行
        content = content.replace("<br>", r" \\ ")
        
        # 確保 LaTeX 數學公式正確
        # 如果內容中已經有 $ 符號，則不需要再添加
        if "$" not in content and "\\(" not in content and "\\[" not in content:
            # 檢查是否包含可能的數學符號
            math_symbols = ["+", "-", "=", "\\times", "\\div", "\\frac", "\\sqrt"]
            if any(symbol in content for symbol in math_symbols):
                content = f"${content}$"
        
        return content
        
    def _render_figure(self, figure_data: Dict[str, Any]) -> str:
        """渲染圖形
        
        根據 figure_data 生成 TikZ 圖形代碼
        
        Args:
            figure_data: 圖形數據字典，包含 'type', 'params' 和 'options'
            
        Returns:
            TikZ 圖形代碼（包含 tikzpicture 環境）
            
        Raises:
            ValueError: 如果找不到指定類型的圖形生成器或生成圖形時出錯
        """
        print("someonecallme_render_figure") # DEBUG PRINT
        if not figure_data:
            return ""
        
        # 提取圖形類型和參數
        figure_type = figure_data.get('type')
        params = figure_data.get('params', {})
        options = figure_data.get('options', {})
        
        if not figure_type:
            raise ValueError("圖形數據缺少 'type' 字段")
        
        try:
            # 獲取圖形生成器
            generator_cls = figures.get_figure_generator(figure_type)
            generator = generator_cls()
            
            # 生成 TikZ 圖形內容
            tikz_content = generator.generate_tikz(params)
            print(f"DEBUG: [latex_generator._render_figure] Raw tikz_content from {figure_type}: {repr(tikz_content)}") # DEBUG PRINT 1
            
            # 處理選項
            scale = options.get('scale', 1.0)
            width = options.get('width', None)
            height = options.get('height', None)
            
            # 構建 tikzpicture 環境選項
            tikz_options = []
            
            # 如果提供了 scale，添加到選項中
            if scale != 1.0:
                tikz_options.append(f"scale={scale}")
            
            # 構建 tikzpicture 環境
            if tikz_options:
                options_str = ", ".join(tikz_options)
                tikz_code = f"\\begin{{tikzpicture}}[{options_str}]\n{tikz_content}\n\\end{{tikzpicture}}"
            else:
                tikz_code = f"\\begin{{tikzpicture}}\n{tikz_content}\n\\end{{tikzpicture}}"
            print(f"DEBUG: [latex_generator._render_figure] After wrapping tikzpicture: {repr(tikz_code)}") # DEBUG PRINT 2
            
            # 如果提供了寬度或高度，使用 resizebox
            if width or height:
                width_str = width if width else "!"
                height_str = height if height else "!"
                # 確保使用正確的大括號格式
                # Use string concatenation instead of nested f-string for resizebox
                tikz_code = "\\resizebox{" + width_str + "}{" + height_str + "}{" + tikz_code + "}"
                print(f"DEBUG: [latex_generator._render_figure] After wrapping resizebox (concatenation): {repr(tikz_code)}") # DEBUG PRINT 3
            
            # 雖然使用者說這行無效，但保留打印以觀察
            original_code_before_replace = tikz_code
            tikz_code = tikz_code.replace("{{", "{").replace("}}", "}")
            if tikz_code != original_code_before_replace:
                 # Corrected f-string: escape literal braces with double braces
                 print(f"DEBUG: [latex_generator._render_figure] After replace('{{{{','{{'), replace('}}}}','}}'): {repr(tikz_code)}") # DEBUG PRINT 4 (Conditional)
            else:
                 # Corrected f-string: escape literal braces with double braces
                 print(f"DEBUG: [latex_generator._render_figure] replace('{{{{','{{'), replace('}}}}','}}') had no effect.") # DEBUG PRINT 4 (Conditional)

            print(f"DEBUG: [latex_generator._render_figure] Final tikz_code returned: {repr(tikz_code)}") # DEBUG PRINT 5
            return tikz_code
            
        except Exception as e:
            raise ValueError(f"渲染圖形時出錯 (類型: {figure_type}): {str(e)}")