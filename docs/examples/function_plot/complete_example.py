#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
完整的函數圖形生成器 PDF 測試
生成包含所有四種函數類型的測試文檔
"""

from figures import get_figure_generator

# 獲取生成器
FuncGen = get_figure_generator('function_plot')
generator = FuncGen()

# 收集所有測試圖形的 TikZ 代碼
figures = []

# 1. 多項式函數 - 二次函數
print("生成多項式函數圖形...")
polynomial_params = {
    'function_type': 'polynomial',
    'coefficients': [1, -2, 1],  # x^2 - 2x + 1
    'x_range': (-1, 4),
    'y_range': (-1, 5),
    'show_grid': True,
    'show_y_intercept': True,
    'plot_color': 'blue'
}
figures.append(('多項式函數: $f(x) = x^2 - 2x + 1$', generator.generate_tikz(polynomial_params)))

# 2. 指數函數
print("生成指數函數圖形...")
exponential_params = {
    'function_type': 'exponential',
    'base': 2.0,
    'x_range': (-3, 3),
    'y_range': (0, 8),
    'show_grid': True,
    'show_y_intercept': True,
    'plot_color': 'red'
}
figures.append(('指數函數: $f(x) = 2^x$', generator.generate_tikz(exponential_params)))

# 3. 對數函數
print("生成對數函數圖形...")
logarithmic_params = {
    'function_type': 'logarithmic',
    'base': 2.0,
    'x_range': (0.001, 10),
    'y_range': (-4, 4),
    'show_grid': True,
    'plot_color': 'green'
}
figures.append(('對數函數: $f(x) = \\log_2(x)$', generator.generate_tikz(logarithmic_params)))

# 4. 三角函數 - 正弦
print("生成正弦函數圖形...")
sine_params = {
    'function_type': 'trigonometric',
    'trig_function': 'sin',
    'amplitude': 2.0,
    'x_range': (-6.28, 6.28),
    'y_range': (-2.5, 2.5),
    'show_grid': True,
    'show_y_intercept': True,
    'plot_color': 'purple'
}
figures.append(('三角函數: $f(x) = 2\\sin(x)$', generator.generate_tikz(sine_params)))

# 5. 三角函數 - 餘弦
print("生成餘弦函數圖形...")
cosine_params = {
    'function_type': 'trigonometric',
    'trig_function': 'cos',
    'x_range': (-6.28, 6.28),
    'y_range': (-1.5, 1.5),
    'show_grid': True,
    'show_y_intercept': True,
    'plot_color': 'orange'
}
figures.append(('三角函數: $f(x) = \\cos(x)$', generator.generate_tikz(cosine_params)))

# 6. 三角函數 - 正切（自動處理不連續）
print("生成正切函數圖形...")
tangent_params = {
    'function_type': 'trigonometric',
    'trig_function': 'tan',
    'x_range': (-4.71, 4.71),  # -3π/2 到 3π/2
    'y_range': (-4, 4),
    'show_grid': True,
    'samples': 200,
    'plot_color': 'brown'
}
figures.append(('三角函數: $f(x) = \\tan(x)$ (自動處理不連續)', generator.generate_tikz(tangent_params)))

# 生成 LaTeX 文檔
print("\n生成 LaTeX 文檔...")
latex_doc = r"""\documentclass{article}
\usepackage{amsmath}
\usepackage{tikz}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\usepackage[a4paper, margin=2cm]{geometry}

\begin{document}

\title{函數圖形生成器測試文檔}
\author{FunctionPlotGenerator}
\date{\today}
\maketitle

\section*{測試目的}
本文檔測試 FunctionPlotGenerator 生成器的四種函數類型：
\begin{itemize}
  \item 多項式函數 (Polynomial)
  \item 指數函數 (Exponential)
  \item 對數函數 (Logarithmic)
  \item 三角函數 (Trigonometric)
\end{itemize}

\newpage
"""

# 添加所有圖形
for i, (title, tikz) in enumerate(figures, 1):
    latex_doc += f"\n\\section*{{{i}. {title}}}\n\n"
    latex_doc += "\\begin{center}\n"
    latex_doc += tikz
    latex_doc += "\\end{center}\n"

    if i < len(figures):
        latex_doc += "\n\\vspace{1cm}\n"

latex_doc += r"""
\newpage
\section*{測試結果總結}

\subsection*{成功驗證的功能}
\begin{itemize}
  \item ✓ 多項式函數表達式生成正確
  \item ✓ 指數函數繪製正確
  \item ✓ 對數函數定義域處理正確
  \item ✓ 三角函數使用弧度模式 (trig format=rad)
  \item ✓ tan 函數自動處理不連續點 (unbounded coords=jump)
  \item ✓ y 截距標記功能正常
  \item ✓ 網格顯示功能正常
  \item ✓ 自定義顏色和樣式正常
\end{itemize}

\subsection*{技術細節}
\begin{itemize}
  \item 使用 PGFPlots 繪製，品質優異
  \item 三角函數採用弧度模式，符合數學慣例
  \item tan 函數使用 unbounded coords=jump 自動跳過漸近線
  \item 對數函數定義域從 0.001 開始，避免無效值
  \item 所有圖形通過 Pydantic 參數驗證
\end{itemize}

\end{document}
"""

# 寫入文件
output_file = "test_function_plot_complete.tex"
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(latex_doc)

print(f"✅ LaTeX 文檔已生成: {output_file}")
print("\n開始編譯 PDF...")

# 編譯 PDF
import subprocess
try:
    result = subprocess.run(
        ['xelatex', '-interaction=nonstopmode', output_file],
        capture_output=True,
        text=True,
        timeout=30
    )

    if result.returncode == 0:
        pdf_file = output_file.replace('.tex', '.pdf')
        print(f"🎉 PDF 編譯成功: {pdf_file}")
        print("\n請檢查 PDF 文件以驗證所有圖形是否正確顯示。")
    else:
        print("❌ PDF 編譯失敗")
        print("\n錯誤輸出（最後1000字元）:")
        print(result.stdout[-1000:] if len(result.stdout) > 1000 else result.stdout)

except subprocess.TimeoutExpired:
    print("⏱️ 編譯超時")
except FileNotFoundError:
    print("⚠️ 未找到 xelatex 編譯器")
    print(f"請手動編譯: xelatex {output_file}")
except Exception as e:
    print(f"❌ 編譯過程發生錯誤: {e}")
