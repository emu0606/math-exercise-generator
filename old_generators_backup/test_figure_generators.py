# test_figure_generators.py
import figures # 假設 figures/__init__.py 正確設置了導入
import traceback

# --- 測試 PointGenerator ---
print("--- Testing PointGenerator ---")
try:
    point_gen = figures.get_figure_generator('point')()
    point_params = {'x': 1, 'y': 1, 'label': 'A', 'label_position': 'above right'}
    point_tikz = point_gen.generate_tikz(point_params)

    latex_doc_point = f"""
\\documentclass{{article}}
\\usepackage{{tikz}}
\\usepackage{{xeCJK}} % 添加 xeCJK 以支持可能的中文標籤
\\setCJKmainfont{{Noto Sans TC}} % 設置字體
\\begin{{document}}
\\begin{{tikzpicture}}
{point_tikz}
\\end{{tikzpicture}}
\\end{{document}}
"""
    print("Generated LaTeX for Point:")
    print(latex_doc_point)
    # Optional: Write to file
    with open("test_point_output.tex", "w", encoding="utf-8") as f:
        f.write(latex_doc_point)
    print("Written to test_point_output.tex")

except Exception as e:
    print(f"Error testing PointGenerator: {e}")
    traceback.print_exc()

print("\n" + "="*20 + "\n")

# --- 測試 StandardUnitCircleGenerator ---
print("--- Testing StandardUnitCircleGenerator ---")
try:
    suc_gen = figures.get_figure_generator('standard_unit_circle')()
    # 使用一個之前有問題的角度，例如 300 度
    suc_params = {'angle': 300, 'variant': 'question', 'show_coordinates': True, 'show_angle': True, 'show_point': True, 'show_radius': True}
    suc_tikz = suc_gen.generate_tikz(suc_params)

    # 注意：StandardUnitCircleGenerator 返回的內容可能已包含 \usetikzlibrary
    # 我們需要稍微調整模板

    # 提取庫（如果存在）
    libraries = ""
    tikz_lines = suc_tikz.splitlines()
    # 查找庫指令行，可能不在第一行
    library_lines = [line for line in tikz_lines if line.strip().startswith("\\usetikzlibrary")]
    if library_lines:
        libraries = "\n".join(library_lines)
        # 移除所有庫指令行來獲取純內容
        suc_tikz_content = "\n".join(line for line in tikz_lines if not line.strip().startswith("\\usetikzlibrary"))
    else:
        suc_tikz_content = suc_tikz

    latex_doc_suc = f"""
\\documentclass{{article}}
\\usepackage{{tikz}}
\\usepackage{{xeCJK}} % 添加 xeCJK
\\setCJKmainfont{{Noto Sans TC}} % 設置字體
{libraries} % 插入提取的庫指令
\\begin{{document}}
\\begin{{tikzpicture}}[scale=1] % 添加一個 scale 選項
{suc_tikz_content}
\\end{{tikzpicture}}
\\end{{document}}
"""
    print("Generated LaTeX for Standard Unit Circle:")
    print(latex_doc_suc)
    # Optional: Write to file
    with open("test_suc_output.tex", "w", encoding="utf-8") as f:
        f.write(latex_doc_suc)
    print("Written to test_suc_output.tex")

except Exception as e:
    print(f"Error testing StandardUnitCircleGenerator: {e}")
    traceback.print_exc()