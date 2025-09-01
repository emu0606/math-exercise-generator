# test_render_integration.py
import traceback
import figures # 假設 figures/__init__.py 正確設置了導入
from generators.trigonometry import TrigonometricFunctionGenerator # 直接導入題目生成器

def render_figure_logic(figure_data: dict) -> str:
    """
    直接應用 _render_figure 的核心邏輯。
    注意：這是一個簡化版本，用於測試，可能缺少原函數的某些細節。
    """
    if not figure_data:
        return ""

    figure_type = figure_data.get('type')
    params = figure_data.get('params', {})
    options = figure_data.get('options', {})

    if not figure_type:
        raise ValueError("圖形數據缺少 'type' 字段")

    try:
        # 獲取圖形生成器
        generator_cls = figures.get_figure_generator(figure_type)
        generator = generator_cls()

        # 生成 TikZ 圖形內容 (核心)
        print(f"DEBUG: [render_figure_logic] Calling {figure_type}.generate_tikz with params: {params}")
        tikz_content = generator.generate_tikz(params)
        print(f"DEBUG: [render_figure_logic] Raw tikz_content from {figure_type}: {repr(tikz_content)}")

        # 處理選項
        scale = options.get('scale', 1.0)
        width = options.get('width', None)
        height = options.get('height', None)

        # 構建 tikzpicture 環境選項
        tikz_options = []
        if scale != 1.0:
            tikz_options.append(f"scale={scale}")

        # 構建 tikzpicture 環境 (使用字串拼接)
        options_str = ", ".join(tikz_options)
        if tikz_options:
             tikz_code = "\\begin{tikzpicture}[" + options_str + "]\n" + tikz_content + "\n\\end{tikzpicture}"
        else:
             tikz_code = "\\begin{tikzpicture}\n" + tikz_content + "\n\\end{tikzpicture}"
        print(f"DEBUG: [render_figure_logic] After wrapping tikzpicture: {repr(tikz_code)}")

        # 如果提供了寬度或高度，使用 resizebox (使用字串拼接)
        if width or height:
            width_str = width if width else "!"
            height_str = height if height else "!"
            tikz_code = "\\resizebox{" + width_str + "}{" + height_str + "}{" + tikz_code + "}"
            print(f"DEBUG: [render_figure_logic] After wrapping resizebox: {repr(tikz_code)}")

        print(f"DEBUG: [render_figure_logic] Final tikz_code returned: {repr(tikz_code)}")
        return tikz_code

    except Exception as e:
        print(f"ERROR: [render_figure_logic] Exception occurred while rendering figure (type: {figure_type}): {str(e)}")
        traceback.print_exc()
        return f"\\textbf{{圖形渲染錯誤: {str(e)}}}"

# --- 主測試邏輯 ---
print("--- Testing TrigonometricFunctionGenerator with integrated render logic ---")
try:
    # 1. 生成題目數據
    trig_gen = TrigonometricFunctionGenerator()
    question_data = trig_gen.generate_question()
    print(f"DEBUG: Generated question_data: {question_data}")

    question_text = question_data.get('question', '題目缺失')
    figure_data_question = question_data.get('figure_data_question')

    # 2. 直接渲染圖形 (如果存在)
    figure_content = ""
    if figure_data_question:
        print("DEBUG: figure_data_question found, attempting to render...")
        figure_content = render_figure_logic(figure_data_question)
    else:
        print("DEBUG: No figure_data_question found.")

    # 3. 組合最小 LaTeX 文檔
    # 提取可能的庫指令 (從渲染後的內容中)
    libraries = ""
    if figure_content:
        tikz_lines = figure_content.splitlines()
        library_lines = [line for line in tikz_lines if line.strip().startswith("\\usetikzlibrary")]
        if library_lines:
            libraries = "\n".join(library_lines)
            # 從 figure_content 中移除庫指令以避免重複
            figure_content = "\n".join(line for line in tikz_lines if not line.strip().startswith("\\usetikzlibrary"))


    latex_doc = f"""
\\documentclass{{article}}
\\usepackage{{tikz}}
\\usepackage{{xeCJK}}
\\setCJKmainfont{{Noto Sans TC}}
{libraries} % 插入可能的庫指令
\\begin{{document}}

\\textbf{{題目:}} {question_text}

\\vspace{{1cm}}

\\textbf{{圖形:}}
\\begin{{center}}
{figure_content}
\\end{{center}}

\\end{{document}}
"""
    print("\n--- Generated Minimal LaTeX Document ---")
    print(latex_doc)

    # 4. 寫入文件
    output_filename = "test_render_output.tex"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(latex_doc)
    print(f"\nWritten to {output_filename}")

except Exception as e:
    print(f"\nERROR in main test logic: {e}")
    traceback.print_exc()