#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - LaTeX 結構類別
負責生成 LaTeX 文檔的結構部分，如前導區、頁首、頁尾等
"""

from typing import Dict, List, Any, Optional
from utils.latex_config import LaTeXConfig

class LaTeXStructure:
    """LaTeX 結構類別
    
    負責生成 LaTeX 文檔的結構部分，如前導區、頁首、頁尾等。
    使用 LaTeXConfig 獲取配置參數。
    """
    
    def __init__(self, config: Optional[LaTeXConfig] = None, current_date: Optional[str] = None):
        """初始化 LaTeX 結構類別
        
        Args:
            config: LaTeX 配置對象，如果為 None，則創建一個新的配置對象
            current_date: 當前日期字符串，如果為 None，則從配置對象獲取
        """
        self.config = config or LaTeXConfig()
        self.current_date = current_date or self.config.get_current_date()
    
    def get_preamble(self, title: str) -> str:
        """獲取 LaTeX 文檔的前導區
        
        Args:
            title: 文檔標題
            
        Returns:
            LaTeX 前導區內容
        """
        font_path = self.config.font_path
        
        preamble = r"""\documentclass[a4paper,11pt]{article}
\usepackage{xeCJK}
\usepackage[margin=1.8cm]{geometry}
\usepackage{tikz}
\usetikzlibrary{positioning, shadows, calc, arrows.meta, angles, quotes} % Added angles and quotes
\usepackage{amsmath,amssymb}
\usepackage{multicol}
\usepackage{enumitem}
\usepackage{fancyhdr}
\usepackage{xcolor}
\usepackage{mdframed} % mdframed 可能不再需要，但暫時保留以防萬一
\usepackage[most]{tcolorbox} % 確保 tcolorbox 加載
\usepackage{fontspec}
\usepackage{lmodern}
% \usepackage{wrapfig} % 移除 wrapfig

% 設定字體
\setCJKmainfont[
  Path=""" + font_path + r""",
  Extension=.otf,
  BoldFont=SourceHanSansTC-Bold
]{SourceHanSansTC-Regular}

% 設定英文和數字字體
\setmainfont[
  Path=""" + font_path + r""",
  Extension=.otf,
  BoldFont=SourceHanSansTC-Bold
]{SourceHanSansTC-Regular}

% 設定等寬字體 (如果有)
\setmonofont[
  Path=""" + font_path + r""",
  Extension=.otf
]{SourceHanSansTC-Regular}


% 全局字體設置
\renewcommand{\normalsize}{\fontsize{11pt}{15pt}\selectfont}
\renewcommand{\large}{\fontsize{14pt}{18pt}\selectfont}
\renewcommand{\Large}{\fontsize{16pt}{20pt}\selectfont}
\renewcommand{\huge}{\fontsize{20pt}{24pt}\selectfont}


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

% 定義顏色
\definecolor{answerframe}{RGB}{120,120,120}
\definecolor{answerback}{RGB}{248,248,248}
\definecolor{explanationframe}{RGB}{70,130,180} % 保持顏色定義
\definecolor{explanationback}{RGB}{240,248,255} % 保持顏色定義
\definecolor{roundtitle}{RGB}{50,50,50}
\definecolor{accent6}{RGB}{52,73,94} % Added accent color for question number box


% Command for shadowed rounded rectangle question number
\newcommand{\qnumShadowBox}[1]{%
  \tikz[remember picture]{
    \node[rectangle, rounded corners=3pt, fill=white, draw=accent6, drop shadow, inner sep=2pt] (qnum) {\bfseries #1};
  }
}

% 設計5: 簡潔分隔線設計 (來自 testlatex5.tex) - 用於簡答頁
\newcommand{\numberedAnswerLine}[2]{%
  \begin{minipage}{0.3\textwidth} % 調整寬度以適應頁面
    \begin{tikzpicture}
      % 題號小方框
      \draw[fill=lightgray, draw=darkgray!70] (0,0) rectangle (0.55,0.55);
      \node[font=\small\bfseries] at (0.275,0.275) {#1};

      % 答案與下劃線
      \node[font=\large, anchor=west] at (0.8,0.275) {#2};
      % 調整下劃線長度以匹配 minipage 寬度減去題號框和間距
      \pgfmathsetlengthmacro{\linewidthcalc}{\linewidth - 0.8cm - 0.55cm} % 估算可用寬度
      \draw[darkgray, line width=0.8pt] (0.8,-.2) -- +(\linewidthcalc,0); % 從答案左側開始繪製
    \end{tikzpicture}
    \vspace{0.6cm} % 項目之間的垂直間距
  \end{minipage}%
}

% 設計5分隔線行 (來自 testlatex5.tex) - 用於簡答頁
\newenvironment{answerRow}{%
  \noindent\begin{minipage}{\textwidth} % 使用完整寬度
    \centering % 讓 minipage 內的內容居中（如果 minipage 總寬度小於 textwidth）
    \setlength{\lineskip}{1pt} % 調整行間距，根據需要
    \setlength{\parskip}{0pt} % 移除段落間距
    \raggedright % 讓 minipage 內的內容靠左對齊
}{%
  \end{minipage}
  \vspace{0.2cm} % 行之間的垂直間距
}

% *** 修改：定義 explanationbox 樣式和命令 ***
\tcbset{
    explanationstyle/.style={
        enhanced,
        breakable=true, % 允許盒子跨欄/頁
        colback=explanationback, % 使用預定義顏色
        colframe=explanationframe, % 使用預定義顏色
        arc=2mm,
        boxrule=0.5pt,
        fontupper=\fontsize{9pt}{11pt}\selectfont, % 設定內容字體
        % 使用 tcolorbox 的標準間距，或根據需要調整
        % before skip=1em, % 可選
        % after skip=1em, % 可選
        left=2mm, right=2mm, top=2mm, bottom=2mm % 內邊距
    }
}
% 定義 explanationbox 命令以使用樣式
\newcommand{\explanationbox}[2][]{% #1 for optional tcolorbox options
  \begin{tcolorbox}[explanationstyle, #1]
    #2
  \end{tcolorbox}
}

% 回標題樣式
\newcommand{\roundtitle}[1]{%
    \begin{center}
        \colorbox{roundtitle!10}{%
            \begin{minipage}{0.95\textwidth}
                \centering\large\textbf{\textcolor{roundtitle}{#1}}
            \end{minipage}
        }
    \end{center}
    \vspace{0.5em}
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
    
    def generate_page_header(self, round_num: int) -> str:
        """生成頁首
        
        Args:
            round_num: 回數
            
        Returns:
            頁首 LaTeX 內容
        """
        header = r"\noindent 第" + str(round_num) + r"回 \hfill \_\_\_月\_\_\_\_日 \hfill 姓名：\_\_\_\_\_\_\_\_\_" + "\n\n"
        return header
    
    def generate_page_footer(self) -> str:
        """生成頁尾
        
        Returns:
            頁尾 LaTeX 內容
        """
        footer = r"\vfill" + "\n"
        footer += r"\begin{center}" + "\n"
        footer += r"\small{生成日期：" + self.current_date + r"}" + "\n"
        footer += r"\end{center}" + "\n"
        return footer
    
    def format_latex_content(self, content: str) -> str:
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