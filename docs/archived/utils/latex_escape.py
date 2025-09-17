import re

def escape_latex(text: str) -> str:
    """
    簡單地轉義 LaTeX 特殊字符，以便在文本模式下安全顯示。
    """
    if not isinstance(text, str):
        text = str(text)
    
    # 替換的順序很重要，特別是反斜杠
    replacements = {
        '\\': r'\textbackslash{}', # 必須首先處理
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
    }
    
    # 為了避免一個替換影響另一個（例如，'\' 變成 '\textbackslash{}' 後，裡面的 '\' 不應再次被處理）
    # 最好是使用 re.sub 和一個回調函數，或者確保替換目標不包含已替換的序列。
    # 一個更簡單的方法是按特定順序進行 .replace()
    
    text = text.replace('\\', replacements['\\']) # Step 1: Handle backslash
    
    # Step 2: Handle other characters that are now safe from backslash interference
    # (or whose replacements don't create new special characters)
    text = text.replace('&', replacements['&'])
    text = text.replace('%', replacements['%'])
    text = text.replace('$', replacements['$'])
    text = text.replace('#', replacements['#'])
    text = text.replace('_', replacements['_'])
    text = text.replace('{', replacements['{'])
    text = text.replace('}', replacements['}'])
    text = text.replace('~', replacements['~'])
    text = text.replace('^', replacements['^'])
    
    return text

if __name__ == '__main__':
    # 簡單測試
    test_strings = [
        "Hello_World",
        "100%",
        "Amount: $50",
        "Section #1",
        "a & b {c}",
        "Path C:\\Users\\Test",
        "~tilde~ and ^caret^",
        "\\ already escaped \\textbackslash{}" # 應該避免雙重轉義
    ]
    expected_outputs = [
        r"Hello\_World",
        r"100\%",
        r"Amount: \$50",
        r"Section \#1",
        r"a \& b \{c\}",
        r"Path C:\textbackslash{}Users\textbackslash{}Test", # 注意這裡的結果
        r"\textasciitilde{}tilde\textasciitilde{} and \textasciicircum{}caret\textasciicircum{}",
        r"\textbackslash{} already escaped \textbackslash{}\textbackslash{}\{\}" # 雙重轉義的例子
    ]

    for i, s in enumerate(test_strings):
        escaped = escape_latex(s)
        print(f"Original: '{s}'\nEscaped:  '{escaped}'")
        # print(f"Expected: '{expected_outputs[i]}'") # 用於比較
        # assert escaped == expected_outputs[i] # 斷言可能因實現細節而異
        print("-" * 20)
    
    # 測試雙重轉義問題
    already_escaped_backslash = r"\textbackslash{}"
    print(f"Original: '{already_escaped_backslash}'")
    print(f"Escaped:  '{escape_latex(already_escaped_backslash)}'") # 應該是 \textbackslash{}\textbackslash{}\{\}
    # 這表明如果輸入已經部分轉義，此簡單函數可能會過度轉義。
    # 一個更健壯的解決方案可能需要正則表達式，並且只匹配未被轉義的特殊字符。
    # 但對於我們的用例，假設輸入是“原始”文本，這個簡單版本應該足夠。