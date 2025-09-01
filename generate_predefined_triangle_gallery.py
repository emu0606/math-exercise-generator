#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
生成一個包含 PredefinedTriangleGenerator 示例輸出的 LaTeX 文件，
用於視覺化測試不同的參數配置。
"""

import os
import math
import re
from figures import get_figure_generator
from utils.latex_config import LaTeXConfig # 假設此路徑和類存在且可用

# --- LaTeX 模板常量 ---
LATEX_POSTAMBLE = r"""
\end{document}
"""

TIKZ_ENVIRONMENT_START = r"""
\begin{tikzpicture}[scale=0.8] % 調整 scale 以適應頁面
"""

TIKZ_ENVIRONMENT_END = r"""
\end{tikzpicture}
"""

# --- 輔助函數 ---
def escape_latex(text: str) -> str:
    """簡單地轉義 LaTeX 特殊字符"""
    if not isinstance(text, str):
        text = str(text)
    return re.sub(r'([_&%$#{}])', r'\\\1', text)

def generate_latex_preamble(config: LaTeXConfig, title: str) -> str:
    """根據配置生成 LaTeX 前導碼"""
    font_path = config.font_path.replace('\\', '/')
    preamble_template = r"""\documentclass[a4paper,11pt]{{article}}
\usepackage{{xeCJK}}
\usepackage[margin=1.8cm]{{geometry}}
\usepackage{{tikz}}
\usetikzlibrary{{positioning, shadows, calc, arrows.meta, angles, quotes}}
\usepackage{{amsmath,amssymb}}
\usepackage{{multicol}}
\usepackage{{enumitem}}
\usepackage{{fancyhdr}}
\usepackage{{xcolor}}
\usepackage[most]{{tcolorbox}}
\usepackage{{fontspec}}
\usepackage{{lmodern}}

% 設定字體
\setCJKmainfont[
  Path={{{font_path}}},
  Extension=.otf, % 假設字體是 .otf, 根據實際情況調整
  BoldFont=SourceHanSansTC-Bold, % 確保這些字體文件名存在於指定路徑
  ItalicFont=SourceHanSansTC-Regular, % 示例，可能沒有斜體
  BoldItalicFont=SourceHanSansTC-Bold % 示例
]{{SourceHanSansTC-Regular}}
\setmainfont[
  Path={{{font_path}}},
  Extension=.otf,
  BoldFont=SourceHanSansTC-Bold
]{{SourceHanSansTC-Regular}}
\setmonofont[
  Path={{{font_path}}},
  Extension=.otf
]{{SourceHanSansTC-Regular}}

% 全局字體設置
\renewcommand{{\normalsize}}{{\fontsize{{10pt}}{{14pt}}\selectfont}} % 稍小一點以容納更多圖形
\pagestyle{{fancy}}
\fancyhf{{}}
\renewcommand{{\headrulewidth}}{{0pt}}
\fancyfoot[C]{{\thepage}}
\setlength{{\parskip}}{{0.5em}}
\setlength{{\parindent}}{{0em}}
\setlist[enumerate]{{leftmargin=*,labelsep=0.5em,topsep=0.3em,itemsep=0.2em}}
\definecolor{{sectioncolor}}{{rgb}}{{0.2,0.4,0.6}}
\usepackage{{titlesec}}
\titleformat{{\subsection}}[block]{{\large\bfseries\color{{sectioncolor}}}}{{\thesubsection}}{{1em}}{{\centering}}
\titlespacing*{{\subsection}}{{0pt}}{{3.5ex plus 1ex minus .2ex}}{{2.3ex plus .2ex}}

\title{{\Huge {title}}}
\author{{}}
\date{{}}

\begin{{document}}
\maketitle
\thispagestyle{{empty}}
\centering
"""
    safe_title = escape_latex(title)
    preamble = preamble_template.format(font_path=font_path, title=safe_title)
    return preamble

# --- PredefinedTriangleGenerator 測試用例定義 ---
# 每個 case 是一個字典，包含 'title' 和 'params' (用於 PredefinedTriangleGenerator)
PREDEFINED_TRIANGLE_TEST_CASES = [
    {
        "title": "SSS (3-4-5) - 僅輪廓和頂點名",
        "params": {
            "variant": "question",
            "definition_mode": "sss", "side_a": 3, "side_b": 4, "side_c": 5,
            "vertex_p1_display_config": {"show_label": True},
            "vertex_p2_display_config": {"show_label": True},
            "vertex_p3_display_config": {"show_label": True},
            "triangle_draw_options": "blue, thick",
            # 其他元素默認不顯示
        }
    },
    {
        "title": "座標定義 - 顯示邊長和P1角",
        "params": {
            "variant": "question",
            "definition_mode": "coordinates", 
            "p1": [0,0], "p2": [4,0], "p3": [1,3],
            "vertex_p1_display_config": {"show_label": True, "label_style": {"text_override": "O"}},
            "vertex_p2_display_config": {"show_label": True, "label_style": {"text_override": "X"}},
            "vertex_p3_display_config": {"show_label": True, "label_style": {"text_override": "Y"}},
            "side_p1p2_display_config": {"show_label": True, "label_text_type": "length"},
            "side_p2p3_display_config": {"show_label": True, "label_text_type": "length"},
            "side_p3p1_display_config": {"show_label": True, "label_text_type": "length"},
            "angle_at_p1_display_config": {"show_arc": True, "show_label": True, "label_text_type": "value"},
            "triangle_fill_color": "yellow!30"
        }
    },
    {
        "title": "SAS (4, 60deg, 3) - 顯示所有角和質心",
        "params": {
            "variant": "question",
            "definition_mode": "sas", 
            "sas_side1": 4, "sas_angle_rad": math.pi/3, "sas_side2": 3,
            "angle_at_p1_display_config": {"show_arc": True, "show_label": True},
            "angle_at_p2_display_config": {"show_arc": True, "show_label": True},
            "angle_at_p3_display_config": {"show_arc": True, "show_label": True},
            "display_centroid": {
                "show_point": True, "point_style": {"color":"red"},
                "show_label": True,
                "label_style": {"text_override": "G_centroid", "color": "red"} # Moved text to text_override
            },
            "global_angle_arc_radius_config": 0.4
        }
    },
    {
        "title": "ASA (30deg, 5, 70deg) - 顯示邊名和內心",
        "params": {
            "variant": "question",
            "definition_mode": "asa",
            "asa_angle1_rad": math.radians(30),
            "asa_side_length": 5,
            "asa_angle2_rad": math.radians(70),
            "default_side_names": ["AB", "BC", "CA"],
            "side_p1p2_display_config": {"show_label": True, "label_text_type": "default_name"},
            "side_p2p3_display_config": {"show_label": True, "label_text_type": "default_name"},
            "side_p3p1_display_config": {"show_label": True, "label_text_type": "default_name"},
            "display_incenter": { # Will use default label "I" from PredefinedTriangleParams
                "show_point": True,
                "show_label": True,
                "label_style": {"color": "blue"}
            },
        }
    },
    {
        "title": "AAS (45deg, 60deg, side opp A = 4) - 顯示自定義標籤",
        "params": {
            "variant": "question",
            "definition_mode": "aas",
            "aas_angle1_rad": math.radians(45), # Angle A at P1
            "aas_angle2_rad": math.radians(60), # Angle B at P2
            "aas_side_a_opposite_p1": 4,        # Side a (P2P3)
            "vertex_p1_display_config": {"show_label": True, "label_style": {"text_override": "$P_1 (45^\\circ)$"}},
            "side_p2p3_display_config": {"show_label": True, "label_text_type": "custom", "custom_label_text": "a=4 (given)"},
            "angle_at_p3_display_config": {"show_label": True, "label_text_type": "value", "value_format": "C={value:.0f}°"},
        }
    },
    # TODO: 添加更多測試用例，例如包含外心、垂心，測試不同的樣式覆蓋等。
]

def main():
    """主函數，生成包含 PredefinedTriangleGenerator 示例的 LaTeX 文件"""
    try:
        config = LaTeXConfig()
    except Exception as e:
        print(f"錯誤：無法初始化 LaTeXConfig: {e}")
        print("請確保 utils.latex_config.py 和相關字體配置正確。")
        return

    title = "PredefinedTriangleGenerator 畫廊"
    latex_preamble = generate_latex_preamble(config, title)
    
    latex_content = [latex_preamble]
    
    try:
        generator_cls = get_figure_generator("predefined_triangle")
        generator = generator_cls()
    except ValueError as e:
        print(f"錯誤：找不到 'predefined_triangle' 生成器: {e}")
        latex_content.append(f"\\subsection*{{錯誤}}\n找不到 'predefined_triangle' 生成器: {escape_latex(str(e))}\n\n")
        latex_content.append(LATEX_POSTAMBLE)
        # ... (write to file and exit) ...
        output_filename_error = "predefined_triangle_gallery_error.tex"
        with open(output_filename_error, "w", encoding="utf-8") as f_err:
            f_err.write("\n".join(latex_content))
        print(f"已生成錯誤文件: {output_filename_error}")
        return

    for i, case in enumerate(PREDEFINED_TRIANGLE_TEST_CASES):
        case_title = case.get("title", f"測試用例 {i+1}")
        params = case.get("params", {})
        
        safe_case_title = escape_latex(case_title)
        print(f"處理案例: {case_title}")
        latex_content.append(f"\\subsection*{{{safe_case_title}}}\n")
        
        try:
            # 確保 variant 存在，如果 params 中沒有，則從 PredefinedTriangleParams 的默認值獲取
            if 'variant' not in params:
                params['variant'] = 'question' # 或者從模型獲取默認值

            tikz_code = generator.generate_tikz(params)
            
            latex_content.append(TIKZ_ENVIRONMENT_START)
            latex_content.append(tikz_code)
            latex_content.append(TIKZ_ENVIRONMENT_END)
            latex_content.append("\\newpage\n" if i < len(PREDEFINED_TRIANGLE_TEST_CASES) - 1 else "\\vspace{1cm}\n")
            
        except Exception as e:
            print(f"  生成 \"{case_title}\" 時出錯: {e}")
            safe_error_message = escape_latex(str(e))
            latex_content.append(f"生成時出錯: {safe_error_message}\n\n")

    latex_content.append(LATEX_POSTAMBLE)
    
    output_filename = "predefined_triangle_gallery.tex"
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write("\n".join(latex_content))
        print(f"\n成功生成 LaTeX 文件: {output_filename}")
        print("您需要使用 XeLaTeX 編譯此文件以查看結果。")
    except IOError as e:
        print(f"\n錯誤：無法寫入文件 {output_filename}: {e}")

if __name__ == "__main__":
    main()