#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - LaTeX 生成器
生成 LaTeX 格式的題目、簡答和詳解頁面
"""

from typing import Dict, List, Any, Optional
from .config import LaTeXConfig
from .structure import LaTeXStructure
from ..rendering.figure_renderer import FigureRenderer

class LaTeXGenerator:
    """LaTeX 生成器
    
    生成 LaTeX 格式的題目、簡答和詳解頁面。
    使用 TikZ 繪製題目框，使用 xeCJK 處理中文。
    
    重構後的版本使用 LaTeXConfig、LaTeXStructure 和 FigureRenderer 類別
    來分離關注點，提高可讀性、可維護性和可測試性。
    """
    
    def __init__(self, config: Optional[LaTeXConfig] = None):
        """初始化 LaTeX 生成器
        
        Args:
            config: LaTeX 配置對象，如果為 None，則創建一個新的配置對象
        """
        # 創建或使用配置對象
        self.config = config or LaTeXConfig()
        
        # 當前日期
        self.current_date = self.config.get_current_date()
        
        # 創建依賴的類別實例
        self.latex_structure = LaTeXStructure(self.config, self.current_date)
        self.figure_renderer = FigureRenderer(self.config)
        
        # 為了向後兼容，保留一些配置參數的引用
        self.page_width = self.config.page_width
        self.page_height = self.config.page_height
        self.margin = self.config.margin
        self.usable_width = self.config.usable_width
        self.grid_width = self.config.grid_width
        self.grid_height = self.config.grid_height
        self.gap = self.config.gap
        self.unit_width = self.config.unit_width
        self.unit_height = self.config.unit_height
    
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
        content = self.latex_structure.get_preamble(test_title)
        content += r"\begin{document}" + "\n"
        
        # 生成每一頁
        for page in range(1, max_page + 1):
            if page > 1:
                content += r"\newpage" + "\n"
            
            # 頁首 - 獲取回次
            first_item_on_page = next((item for item in layout_results if item['page'] == page), None)
            if first_item_on_page:
                round_num = first_item_on_page['round_num']
            else:
                round_num = 1
                
            content += self.latex_structure.generate_page_header(round_num) # 傳遞回次
            
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
                    if figure_data_question:
                        figure_content = self.figure_renderer.render(figure_data_question)
                    
                    # 繪製圓角矩形和題目內容
                    content += f"  % 題目 {question_num}\n"
                    content += f"  \\draw[rounded corners=3pt, thick] ({x}, {y}) rectangle ({x+w}, {y-h});\n"
                    # 使用 overlay 繪製題號
                    content += f"  \\node[overlay, anchor=north west, inner sep=0] at ({{ {x} }}, {{ {y} }}) {{\\qnumShadowBox{{{question_num}}}}};\n"

                    # 獲取圖形位置，預設為右側
                    figure_position = item.get('figure_position', 'right')
                    formatted_question = self.latex_structure.format_latex_content(question_text)
                    question_body = formatted_question # 移除題號，只留題目文字

                    # 根據寬度調整文字/圖形比例
                    if width_cells == 1: # Small 或 Square
                        text_width_ratio = 0.6
                        figure_width_ratio = 0.4
                    else: # Wide, Medium, Large, Extra
                        text_width_ratio = 0.6
                        figure_width_ratio = 0.35
                        
                    text_w = round(text_width_ratio * w, 3)
                    figure_w = round(figure_width_ratio * w, 3)
                    content_width = round(w - 2 * 0.1, 3) # 無圖形時內容寬度 (假設 text_x_offset=0.1)

                    # 計算調整後的位置/寬度
                    node_inner_sep = "0.2cm" # 節點內邊距
                    text_x_offset = 0.1 # 距離左邊緣的小水平偏移
                    text_y_offset = -0.5 # 距離頂部邊緣的垂直偏移（在題號下方）
                    figure_y_offset = -0.1 # 圖形的垂直偏移（頂部略低於框頂）

                    if figure_content and figure_position != 'none':
                        # *** 修改：強制使用 resizebox 包裹圖形 ***
                        if figure_position == 'right':
                            resized_figure = f"\\resizebox{{{figure_w}cm}}{{!}}{{{figure_content}}}"
                            content += f"  \\node[anchor=north west, text width={text_w}cm, inner sep={node_inner_sep}] at ({{ {x}+{text_x_offset} }}, {{ {y}+{text_y_offset} }}) {{{question_body}}};\n"
                            content += f"  \\node[anchor=north east, text width={figure_w}cm, inner sep={node_inner_sep}, align=center] at ({{ {x+w} }}, {{ {y}+{figure_y_offset} }}) {{{resized_figure}}};\n"
                        elif figure_position == 'left':
                            resized_figure = f"\\resizebox{{{figure_w}cm}}{{!}}{{{figure_content}}}"
                            content += f"  \\node[anchor=north west, text width={figure_w}cm, inner sep={node_inner_sep}, align=center] at ({{ {x} }}, {{ {y}+{figure_y_offset} }}) {{{resized_figure}}};\n"
                            content += f"  \\node[anchor=north east, text width={text_w}cm, inner sep={node_inner_sep}] at ({{ {x+w}-{text_x_offset} }}, {{ {y}+{text_y_offset} }}) {{{question_body}}};\n"
                        elif figure_position == 'bottom':
                            resized_figure = f"\\resizebox{{{content_width}cm}}{{!}}{{{figure_content}}}"
                            content += f"  \\node[anchor=north west, text width={content_width}cm, inner sep={node_inner_sep}] (textnode) at ({{ {x}+{text_x_offset} }}, {{ {y}+{text_y_offset} }}) {{{question_body}}};\n"
                            content += f"  \\node[anchor=north west, text width={content_width}cm, inner sep={node_inner_sep}, align=center, below=0.3cm of textnode] at (textnode.south west) {{{resized_figure}}};\n"
                        else: # 預設或無法識別的位置，視為無圖形處理
                            content += f"  \\node[anchor=north west, text width={content_width}cm, inner sep={node_inner_sep}] at ({{ {x}+{text_x_offset} }}, {{ {y}+{text_y_offset} }}) {{{question_body}}};\n"
                    else:
                        # 無圖形或 position 為 'none'，文字填滿
                        content += f"  \\node[anchor=north west, text width={content_width}cm, inner sep={node_inner_sep}] at ({{ {x}+{text_x_offset} }}, {{ {y}+{text_y_offset} }}) {{{question_body}}};\n"

                    content += "\n" # 添加換行符
            
            content += r"\end{tikzpicture}" + "\n"
            content += r"\end{center}" + "\n"
            
            # 頁尾
            content += self.latex_structure.generate_page_footer()
        
        content += r"\end{document}" + "\n"
        
        return content
    
    def generate_answer_tex(self, layout_results: List[Dict[str, Any]], test_title: str, questions_per_round: int = 0) -> str:
        """生成簡答頁 LaTeX 內容

        Args:
            layout_results: 佈局結果列表
            test_title: 測驗標題
            questions_per_round: 每回題數
            
        Returns:
            簡答頁 LaTeX 內容
        """
        # 生成 LaTeX 內容
        content = self.latex_structure.get_preamble(test_title)
        content += r"\begin{document}" + "\n"
        
        # 標題
        content += r"\begin{center}" + "\n"
        content += r"{\Large \textbf{" + test_title + r" - 簡答}}" + "\n"
        content += r"\end{center}" + "\n\n"
        
        # 生成日期
        content += r"\noindent 生成日期：" + self.current_date + r"\hfill" + "\n\n"
        
        # 簡答列表，分回展示
        current_round = -1
        items_in_current_row = 0 # 修改變數名以反映其用途
        items_per_row = 3 # 每行顯示的項目數

        for i, question in enumerate(layout_results):
            # 計算回數和回內題號
            if questions_per_round > 0:
                round_num = (i // questions_per_round) + 1
                question_num_in_round = (i % questions_per_round) + 1
            else:
                round_num = 1
                question_num_in_round = i + 1
            
            # 如果換到新的一回，新增回標題和分隔線
            if round_num != current_round:
                # 如果不是第一回，且上一回有內容，則結束上一回的最後一行（如果需要）
                if current_round != -1 and items_in_current_row > 0:
                    content += r"\end{answerRow}" + "\n\n"
                    items_in_current_row = 0 # 重置行計數器

                # 若不是第一回，添加垂直間距（取代分隔線）
                if current_round != -1 and round_num > 1:
                    content += r"\vspace{1.5em}" + "\n\n" # 回次之間的間距

                # 開始新的一回
                content += f"\\roundtitle{{第{round_num}回}}\n\n"
                current_round = round_num
                items_in_current_row = 0 # 新回次，重置行計數器

            # 開始新的一行（如果需要）
            if items_in_current_row == 0:
                content += r"\begin{answerRow}" + "\n"

            # 獲取答案
            answer = question.get('answer', '')

            # 添加 numberedAnswerLine
            content += f"  \\numberedAnswerLine{{{question_num_in_round}}}{{{self.latex_structure.format_latex_content(answer)}}}\n"
            items_in_current_row += 1

            # 結束當前行（如果已滿）
            if items_in_current_row == items_per_row:
                content += r"\end{answerRow}" + "\n"
                items_in_current_row = 0

        # 結束最後一個回次的最後一行（如果未滿）
        if current_round != -1 and items_in_current_row > 0:
            content += r"\end{answerRow}" + "\n"
        
        # 頁尾
        content += self.latex_structure.generate_page_footer()
        
        content += r"\end{document}" + "\n"
        
        return content
    
    def generate_explanation_tex(self, layout_results: List[Dict[str, Any]], test_title: str, questions_per_round: int = 0) -> str:
        """生成詳解頁 LaTeX 內容

        Args:
            layout_results: 佈局結果列表
            test_title: 測驗標題
            questions_per_round: 每回題數
            
        Returns:
            詳解頁 LaTeX 內容
        """
        # 生成 LaTeX 內容
        content = self.latex_structure.get_preamble(test_title)
        content += r"\begin{document}" + "\n"
        
        # 標題
        content += r"\begin{center}" + "\n"
        content += r"{\Large \textbf{" + test_title + r" - 詳解}}" + "\n"
        content += r"\end{center}" + "\n\n"
        
        # 生成日期
        content += r"\noindent 生成日期：" + self.current_date + r"\hfill" + "\n\n"
        
        # 詳解內容，按回分組
        current_round = -1
        
        for i, question in enumerate(layout_results):
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
                    # 結束上一回的 multicols
                    content += r"\end{multicols}" + "\n\n" 
                    content += r"\begin{center}\rule{0.9\linewidth}{0.5pt}\end{center}" + "\n\n"
                
                # 開始新的一回
                content += f"\\subsection*{{第{round_num}回詳解}}\n\n"
                content += r"\begin{multicols}{2}" + "\n" # 開始新的 multicols
                current_round = round_num
            
            explanation = question.get('explanation', '')
            
            # 檢查是否有圖形數據
            figure_data_explanation = question.get('figure_data_explanation')
            figure_content = ""
            if figure_data_explanation:
                figure_content = self.figure_renderer.render(figure_data_explanation)
            
            # 格式化詳解內容
            formatted_explanation = self.latex_structure.format_latex_content(explanation)
            
            # *** 修正：使用單個 tcolorbox，內部處理佈局 (Plan C.1) ***
            explanation_figure_position = question.get('explanation_figure_position', 'right') # 預設 'right'
            explanation_text_only = f"\\textbf{{{question_num_in_round}.}} {formatted_explanation}"
            
            inner_content = "" # 用於構建 tcolorbox 的內部內容
            if figure_content:
                if explanation_figure_position == 'right':
                    # 圖片置右：在 tcolorbox 內部使用 minipage
                    left_mp = f"\\begin{{minipage}}[c]{{0.58\\linewidth}}\n  {explanation_text_only}\n\\end{{minipage}}"
                    # 圖形在右側 minipage 內部 resize
                    right_figure = f"\\resizebox{{\\linewidth}}{{!}}{{{figure_content}}}" # \linewidth = minipage width
                    right_mp = f"\\begin{{minipage}}[c]{{0.38\\linewidth}}\n  \\centering\n  {right_figure}\n\\end{{minipage}}"
                    inner_content = f"{left_mp}\\hfill{right_mp}"
                    
                elif explanation_figure_position == 'bottom':
                    # 圖片置下：在 tcolorbox 內部上下排列
                    bottom_figure = f"\\resizebox{{\\linewidth}}{{!}}{{{figure_content}}}" # \linewidth = tcolorbox width
                    inner_content = f"{explanation_text_only}\n\\par\\medskip\\centering\n{bottom_figure}"
                    
                else: # 無法識別的位置或 'none'，視為只有文字
                    inner_content = explanation_text_only

            else:
                # 無圖形：內部只有文字
                inner_content = explanation_text_only

            # 輸出單個 tcolorbox，包含計算好的內部內容
            content += f"\\explanationbox{{{inner_content}}}\n\n"
        
        # 確保最後一個回次的 multicols 環境已關閉
        if current_round != -1:
             # 檢查最後幾行是否包含 \end{multicols}
             last_lines = content.splitlines()[-5:] # 檢查最後5行
             if not any(r"\end{multicols}" in line for line in last_lines):
                 content += r"\end{multicols}" + "\n\n"

        # 頁尾
        content += self.latex_structure.generate_page_footer()
        
        content += r"\end{document}" + "\n"
        
        return content
    
    # 以下方法保留為向後兼容的適配方法
    
    def _get_preamble(self, title: str) -> str:
        """獲取 LaTeX 文檔的前導區（向後兼容的適配方法）
        
        Args:
            title: 文檔標題
            
        Returns:
            LaTeX 前導區內容
        """
        return self.latex_structure.get_preamble(title)
    
    def _generate_page_header(self, round_num: int) -> str:
        """生成頁首（向後兼容的適配方法）
        
        Args:
            round_num: 回數
            
        Returns:
            頁首 LaTeX 內容
        """
        return self.latex_structure.generate_page_header(round_num)
    
    def _generate_page_footer(self) -> str:
        """生成頁尾（向後兼容的適配方法）
        
        Returns:
            頁尾 LaTeX 內容
        """
        return self.latex_structure.generate_page_footer()
    
    def _format_latex_content(self, content: str) -> str:
        """格式化 LaTeX 內容（向後兼容的適配方法）
        
        Args:
            content: 原始內容
            
        Returns:
            格式化後的 LaTeX 內容
        """
        return self.latex_structure.format_latex_content(content)
    
    def _render_figure(self, figure_data: Dict[str, Any]) -> str:
        """渲染圖形（向後兼容的適配方法）
        
        Args:
            figure_data: 圖形數據字典
            
        Returns:
            TikZ 圖形代碼
        """
        return self.figure_renderer.render(figure_data)