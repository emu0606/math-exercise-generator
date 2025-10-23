#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - LaTeX 結構類別
負責生成 LaTeX 文檔的結構部分，如前導區、頁首、頁尾等
"""

from typing import Dict, List, Any, Optional
from .config import LaTeXConfig

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

    def get_question_preamble(self, title: str) -> str:
        """獲取題目頁完整 preamble（完全獨立）

        包含題目頁所需的所有 LaTeX 套件、命令定義和配置。
        此方法完全獨立，不依賴任何共用方法。

        Args:
            title: 文檔標題

        Returns:
            題目頁 LaTeX 前導區內容（完整）

        Note:
            修改此方法不會影響簡答頁或詳解頁
        """
        font_path = self.config.font_path
        # 轉換日期為八碼格式 (YYYY-MM-DD -> YYYYMMDD)
        date_str = self.current_date.replace('-', '')

        return r"""\documentclass[a4paper,11pt]{article}

% 基礎套件
\usepackage{xeCJK}
\usepackage[margin=1.8cm, footskip=1cm]{geometry}
\usepackage{amsmath,amssymb}
\usepackage{enumitem}
\usepackage{fancyhdr}
\usepackage{xcolor}
\usepackage{fontspec}
\usepackage{lmodern}
\usepackage{titlesec}

% 題目頁專屬：TikZ 完整庫 + PGFPlots
\usepackage{tikz}
\usetikzlibrary{positioning, shadows, calc, arrows.meta, angles, quotes}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}  % 啟用 PGFPlots 最新特性

% 字體設定
\setCJKmainfont[
  Path=""" + font_path + r""",
  Extension=.otf,
  BoldFont=SourceHanSansTC-Bold
]{SourceHanSansTC-Regular}

\setmainfont[
  Path=""" + font_path + r""",
  Extension=.otf,
  BoldFont=SourceHanSansTC-Bold
]{SourceHanSansTC-Regular}

\setmonofont[
  Path=""" + font_path + r""",
  Extension=.otf
]{SourceHanSansTC-Regular}

% 全局字體大小
\renewcommand{\normalsize}{\fontsize{11pt}{15pt}\selectfont}
\renewcommand{\large}{\fontsize{14pt}{18pt}\selectfont}
\renewcommand{\Large}{\fontsize{16pt}{20pt}\selectfont}
\renewcommand{\huge}{\fontsize{20pt}{24pt}\selectfont}

% 頁面樣式
\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}
\fancyfoot[C]{\small{\thepage}}
\fancyfoot[R]{\small{""" + date_str + r"""}}

% 段落和列表樣式
\setlength{\parskip}{0.5em}
\setlength{\parindent}{0em}
\setlist[enumerate]{leftmargin=*,labelsep=0.5em,topsep=0.3em,itemsep=0.2em}

% 題目頁顏色定義
\definecolor{accent6}{RGB}{52,73,94}

% 題目頁專屬命令：題號陰影框
\newcommand{\qnumShadowBox}[1]{%
  \tikz[remember picture]{
    \node[rectangle, rounded corners=3pt, fill=white, draw=accent6, drop shadow, inner sep=2pt] (qnum) {\bfseries #1};
  }
}

% 設定標題樣式
\titleformat{\subsection}
  {\normalfont\large\bfseries}{\thesubsection}{1em}{}
\titlespacing*{\subsection}{0pt}{2em}{1em}

% 設定標題
\title{\huge """ + title + r"""}
\author{\large 數學測驗生成器}
\date{\large \today}

"""

    def get_answer_preamble(self, title: str) -> str:
        """獲取簡答頁完整 preamble（完全獨立）

        包含簡答頁所需的所有 LaTeX 套件、命令定義和配置。
        此方法完全獨立，不依賴任何共用方法。
        包含四種動態寬度卡片和四色系輪換機制。

        Args:
            title: 文檔標題

        Returns:
            簡答頁 LaTeX 前導區內容（完整）

        Note:
            修改此方法不會影響題目頁或詳解頁
        """
        font_path = self.config.font_path
        # 轉換日期為八碼格式 (YYYY-MM-DD -> YYYYMMDD)
        date_str = self.current_date.replace('-', '')

        return r"""\documentclass[a4paper,11pt]{article}

% 基礎套件
\usepackage{xeCJK}
\usepackage[margin=1.8cm, footskip=1cm]{geometry}
\usepackage{amsmath,amssymb}
\usepackage{enumitem}
\usepackage{fancyhdr}
\usepackage{xcolor}
\usepackage{fontspec}
\usepackage{lmodern}
\usepackage{titlesec}

% 簡答頁專屬：基本 TikZ + tcolorbox + PGFPlots
\usepackage{tikz}
\usepackage[most]{tcolorbox}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}  % 啟用 PGFPlots 最新特性

% 字體設定
\setCJKmainfont[
  Path=""" + font_path + r""",
  Extension=.otf,
  BoldFont=SourceHanSansTC-Bold
]{SourceHanSansTC-Regular}

\setmainfont[
  Path=""" + font_path + r""",
  Extension=.otf,
  BoldFont=SourceHanSansTC-Bold
]{SourceHanSansTC-Regular}

\setmonofont[
  Path=""" + font_path + r""",
  Extension=.otf
]{SourceHanSansTC-Regular}

% 全局字體大小
\renewcommand{\normalsize}{\fontsize{11pt}{15pt}\selectfont}
\renewcommand{\large}{\fontsize{14pt}{18pt}\selectfont}
\renewcommand{\Large}{\fontsize{16pt}{20pt}\selectfont}

% 頁面樣式
\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}
\fancyfoot[C]{\small{\thepage}}
\fancyfoot[R]{\small{""" + date_str + r"""}}}

% 段落樣式
\setlength{\parskip}{0.5em}
\setlength{\parindent}{0em}

% 四色系定義
\definecolor{cardback1}{RGB}{240,248,255}    % 藍灰 - 淡藍底
\definecolor{cardborder1}{RGB}{100,149,237}
\definecolor{numback1}{RGB}{70,130,180}

\definecolor{cardback2}{RGB}{240,255,240}    % 綠 - 淡綠底
\definecolor{cardborder2}{RGB}{60,179,113}
\definecolor{numback2}{RGB}{46,139,87}

\definecolor{cardback3}{RGB}{248,240,255}    % 紫 - 淡紫底
\definecolor{cardborder3}{RGB}{147,112,219}
\definecolor{numback3}{RGB}{106,90,205}

\definecolor{cardback4}{RGB}{255,248,240}    % 橙 - 淡橙底
\definecolor{cardborder4}{RGB}{255,140,0}
\definecolor{numback4}{RGB}{255,99,71}

% 回標題顏色
\definecolor{roundtitle}{RGB}{50,50,50}

% 動態顏色切換命令
\newcommand{\setColorScheme}[1]{%
  \ifnum#1=1
    \colorlet{cardback}{cardback1}%
    \colorlet{cardborder}{cardborder1}%
    \colorlet{numback}{numback1}%
  \else\ifnum#1=2
    \colorlet{cardback}{cardback2}%
    \colorlet{cardborder}{cardborder2}%
    \colorlet{numback}{numback2}%
  \else\ifnum#1=3
    \colorlet{cardback}{cardback3}%
    \colorlet{cardborder}{cardborder3}%
    \colorlet{numback}{numback3}%
  \else
    \colorlet{cardback}{cardback4}%
    \colorlet{cardborder}{cardborder4}%
    \colorlet{numback}{numback4}%
  \fi\fi\fi
}

% 四種寬度卡片命令（使用動態顏色）

% 超短答案卡片 - 四欄
\newcommand{\tinyCard}[2]{%
  \noindent\begin{minipage}[t]{0.23\textwidth}
    \begin{tcolorbox}[
      enhanced,
      colback=cardback,
      colframe=cardborder,
      arc=3mm,
      boxrule=1.2pt,
      left=1mm, right=2mm, top=2.5mm, bottom=2.5mm,
      fontupper=\normalsize
    ]
    \tikz[baseline=(num.base)]{
      \node[rectangle, rounded corners=2mm, fill=numback, text=white, inner sep=2pt, minimum width=0.55cm, minimum height=0.5cm, font=\small\bfseries] (num) {#1};
    }\hspace{2mm}#2
    \end{tcolorbox}
    \vspace{3mm}
  \end{minipage}\hspace{0.015\textwidth}%
}

% 短答案卡片 - 三欄
\newcommand{\shortCard}[2]{%
  \noindent\begin{minipage}[t]{0.305\textwidth}
    \begin{tcolorbox}[
      enhanced,
      colback=cardback,
      colframe=cardborder,
      arc=3mm,
      boxrule=1.2pt,
      left=1mm, right=3mm, top=2.5mm, bottom=2.5mm,
      fontupper=\normalsize
    ]
    \tikz[baseline=(num.base)]{
      \node[rectangle, rounded corners=2mm, fill=numback, text=white, inner sep=2pt, minimum width=0.6cm, minimum height=0.5cm, font=\small\bfseries] (num) {#1};
    }\hspace{3mm}#2
    \end{tcolorbox}
    \vspace{3mm}
  \end{minipage}\hspace{0.02\textwidth}%
}

% 中等答案卡片 - 兩欄
\newcommand{\mediumCard}[2]{%
  \noindent\begin{minipage}[t]{0.47\textwidth}
    \begin{tcolorbox}[
      enhanced,
      colback=cardback,
      colframe=cardborder,
      arc=3mm,
      boxrule=1.2pt,
      left=1mm, right=3mm, top=2.5mm, bottom=2.5mm,
      fontupper=\normalsize
    ]
    \tikz[baseline=(num.base)]{
      \node[rectangle, rounded corners=2mm, fill=numback, text=white, inner sep=2pt, minimum width=0.6cm, minimum height=0.5cm, font=\small\bfseries] (num) {#1};
    }\hspace{3mm}#2
    \end{tcolorbox}
    \vspace{3mm}
  \end{minipage}\hspace{0.02\textwidth}%
}

% 長答案卡片 - 單欄
\newcommand{\longCard}[2]{%
  \noindent\begin{minipage}[t]{0.98\textwidth}
    \begin{tcolorbox}[
      enhanced,
      colback=cardback,
      colframe=cardborder,
      arc=3mm,
      boxrule=1.2pt,
      left=1mm, right=4mm, top=2.5mm, bottom=2.5mm,
      fontupper=\normalsize
    ]
    \tikz[baseline=(num.base)]{
      \node[rectangle, rounded corners=2mm, fill=numback, text=white, inner sep=2pt, minimum width=0.6cm, minimum height=0.5cm, font=\small\bfseries] (num) {#1};
    }\hspace{3mm}#2
    \end{tcolorbox}
    \vspace{3mm}
  \end{minipage}\par%
}

% 回標題命令
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

% 設定標題
\title{\huge """ + title + r"""}
\author{\large 數學測驗生成器}
\date{\large \today}

"""

    def get_explanation_preamble(self, title: str) -> str:
        """獲取詳解頁完整 preamble（完全獨立）

        包含詳解頁所需的所有 LaTeX 套件、命令定義和配置。
        此方法完全獨立，不依賴任何共用方法。

        Args:
            title: 文檔標題

        Returns:
            詳解頁 LaTeX 前導區內容（完整）

        Note:
            修改此方法不會影響題目頁或簡答頁
        """
        font_path = self.config.font_path
        # 轉換日期為八碼格式 (YYYY-MM-DD -> YYYYMMDD)
        date_str = self.current_date.replace('-', '')

        return r"""\documentclass[a4paper,11pt]{article}

% 基礎套件
\usepackage{xeCJK}
\usepackage[margin=1.8cm, footskip=1cm]{geometry}
\usepackage{amsmath,amssymb}
\usepackage{enumitem}
\usepackage{fancyhdr}
\usepackage{xcolor}
\usepackage{fontspec}
\usepackage{lmodern}
\usepackage{titlesec}

% 詳解頁專屬套件
\usepackage{tikz}
\usetikzlibrary{positioning, calc, arrows.meta}
\usepackage[most]{tcolorbox}
\usepackage{multicol}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}  % 啟用 PGFPlots 最新特性

% 字體設定
\setCJKmainfont[
  Path=""" + font_path + r""",
  Extension=.otf,
  BoldFont=SourceHanSansTC-Bold
]{SourceHanSansTC-Regular}

\setmainfont[
  Path=""" + font_path + r""",
  Extension=.otf,
  BoldFont=SourceHanSansTC-Bold
]{SourceHanSansTC-Regular}

\setmonofont[
  Path=""" + font_path + r""",
  Extension=.otf
]{SourceHanSansTC-Regular}

% 全局字體大小
\renewcommand{\normalsize}{\fontsize{11pt}{15pt}\selectfont}
\renewcommand{\large}{\fontsize{14pt}{18pt}\selectfont}
\renewcommand{\Large}{\fontsize{16pt}{20pt}\selectfont}

% 頁面樣式
\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}
\fancyfoot[C]{\small{\thepage}}
\fancyfoot[R]{\small{""" + date_str + r"""}}}

% 段落和欄位樣式
\setlength{\parskip}{0.5em}
\setlength{\parindent}{0em}
\setlength{\columnsep}{1.5em}

% 詳解頁顏色定義
\definecolor{explanationframe}{RGB}{70,130,180}
\definecolor{explanationback}{RGB}{240,248,255}
\definecolor{roundtitle}{RGB}{50,50,50}

% 回標題命令
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

% 詳解框樣式
\tcbset{
    explanationstyle/.style={
        enhanced,
        breakable=true,
        colback=explanationback,
        colframe=explanationframe,
        arc=2mm,
        boxrule=0.5pt,
        fontupper=\fontsize{9pt}{11pt}\selectfont,
        left=2mm, right=2mm, top=2mm, bottom=2mm
    }
}

% 詳解框命令
\newcommand{\explanationbox}[2][]{%
  \begin{tcolorbox}[explanationstyle, #1]
    #2
  \end{tcolorbox}
}

% 設定標題樣式
\titleformat{\subsection}
  {\normalfont\large\bfseries}{\thesubsection}{1em}{}
\titlespacing*{\subsection}{0pt}{2em}{1em}

% 設定標題
\title{\huge """ + title + r"""}
\author{\large 數學測驗生成器}
\date{\large \today}

"""

    def generate_page_header(self, round_num: int) -> str:
        """生成頁首

        Args:
            round_num: 回數

        Returns:
            頁首 LaTeX 內容（高度固定為 1.5cm）
        """
        # 頁首內容：第 X 回 + 手寫日期欄（同行空格分開）+ 姓名欄（左下）
        header_content = (
            r"{\small 第 " + str(round_num) + r" 回 \quad 日期：\_\_\_\_\_\_\_\_}\\[2pt]" + "\n" +
            r"{\large 姓名：\_\_\_\_\_\_\_\_\_\_\_\_}"
        )

        # 漸層裝飾線
        line_style = r"\tikz[overlay] \shade[left color=gray, right color=white] (0,0) rectangle (\linewidth, 1.2pt);%"

        # 使用 parbox 固定高度為 1.5cm
        header = (
            r"\noindent\parbox[t][1.5cm][c]{\textwidth}{%" + "\n" +
            r"  " + header_content + "\n" +
            r"  \vfill" + "\n" +
            r"  " + line_style + "\n" +
            r"}" + "\n\n"
        )

        return header
    
    def generate_page_footer(self) -> str:
        """生成頁尾

        Returns:
            空字串（頁尾已由 fancyhdr 接管）
        """
        return ""  # 返回空字串
    
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