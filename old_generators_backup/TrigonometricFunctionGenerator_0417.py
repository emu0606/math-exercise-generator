import sympy
from sympy import sin, cos, tan, cot, csc, sec, pi, simplify, latex
import random
from typing import Dict, Any, List, Tuple, Union, Callable
from ..base import QuestionGenerator, QuestionSize, register_generator

@register_generator
class TrigonometricFunctionGenerator(QuestionGenerator):
    def __init__(self, options: Dict[str, Any] = None):
        super().__init__(options)
        self.options = options or {}

        # 設定可用的三角函數
        self.functions = [sin, cos, tan, cot, sec, csc]
        if self.options.get("functions"):
            self.functions = self.options.get("functions")

        # 設定可用的角度
        self.angles = [0, 30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 240, 270, 300, 315, 330, 360]
        if self.options.get("angles"):
            self.angles = self.options.get("angles")

        self.difficulty = self.options.get("difficulty", "MEDIUM")
        
        # 創建三角函數值查詢表
        self.trig_values = self._build_trig_value_table()

    def _build_trig_value_table(self) -> Dict[Tuple[Callable, int], Union[str, sympy.Expr]]:
        """構建三角函數值查詢表，包含所有角度的所有函數值"""
        table = {}
        
        # 特殊無窮大情況
        special_cases = {
            (tan, 90): "\\infty",
            (tan, 270): "-\\infty",
            (cot, 0): "\\infty",
            (cot, 180): "-\\infty",
            (cot, 360): "\\infty",
            (sec, 90): "\\infty",
            (sec, 270): "-\\infty",
            (csc, 0): "\\infty",
            (csc, 180): "-\\infty",
            (csc, 360): "\\infty"
        }
        
        # 填充表格
        for func in self.functions:
            for angle in self.angles:
                key = (func, angle)
                
                # 檢查是否是特殊情況
                if key in special_cases:
                    table[key] = special_cases[key]
                else:
                    # 計算正常值
                    angle_rad = angle * pi / 180
                    try:
                        value = simplify(func(angle_rad))
                        table[key] = value
                    except Exception:
                        # 標記為錯誤，而不是默認到固定角度
                        table[key] = "ERROR"
        
        return table

    def generate_question(self) -> Dict[str, Any]:
        # 隨機選擇角度和函數
        angle = random.choice(self.angles)
        func = random.choice(self.functions)
        func_name = func.__name__
        angle_rad = angle * pi / 180
        
        # 從查詢表獲取值
        value = self.trig_values.get((func, angle))
        
        # 如果值是錯誤標記，重新選擇一組
        while value == "ERROR":
            angle = random.choice(self.angles)
            func = random.choice(self.functions)
            value = self.trig_values.get((func, angle))
        
        # 計算單位圓的點坐標
        cos_value = float(sympy.cos(angle_rad).evalf())
        sin_value = float(sympy.sin(angle_rad).evalf())
        
        # 生成單位圓圖
        tikz_diagram = self._generate_unit_circle_diagram(angle, angle_rad, cos_value, sin_value)
        tikz_wrapped = f"\\resizebox{{!}}{{2cm}}{{%s}}" % tikz_diagram
        
        # 判斷是否特殊值（無窮大）
        is_special = isinstance(value, str) and "\\infty" in value
        
        if is_special:
            explanation = self._generate_special_explanation(func_name, angle, value, tikz_wrapped)
        else:
            explanation = self._generate_normal_explanation(func_name, angle, angle_rad, latex(value), tikz_wrapped)
        
        return {
            "question": f"{tikz_wrapped} \\\\ ${func_name}({angle}^\\circ) = ?$",
            "answer": f"${latex(value)}$" if not is_special else f"${value}$",
            "explanation": explanation,
            "size": self.get_question_size(),
            "difficulty": self.difficulty
        }
    
    def _generate_special_explanation(self, func_name, angle, value, tikz_diagram):
        """生成特殊值的解釋"""
        return f"""
        計算 ${func_name}({angle}^\\circ)$ 的值：

        ${func_name}({angle}^\\circ)$ 是未定義的值，但可以表示為 ${value}$

        在數學上，當 ${func_name}({angle}^\\circ)$ 趨近於無限大時，我們記作 ${value}$

        {tikz_diagram}
        """
    
    def _generate_normal_explanation(self, func_name, angle, angle_rad, value_latex, tikz_diagram):
        """生成一般值的解釋"""
        return f"""
        計算 ${func_name}({angle}^\\circ)$ 的值：

        將角度轉換為弧度：${angle}^\\circ = {latex(angle_rad)} \\text{{ rad}}$

        利用特殊角公式計算 ${func_name}({latex(angle_rad)}) = {value_latex}$

        {tikz_diagram}
        """

    def _generate_unit_circle_diagram(self, angle, angle_rad, cos_value, sin_value):
        """生成單位圓TikZ圖"""
        cos_expr = simplify(cos(angle_rad))
        sin_expr = simplify(sin(angle_rad))
        cos_latex = latex(cos_expr)
        sin_latex = latex(sin_expr)

        return f"""
        \\begin{{tikzpicture}}[scale=2]
            \\draw[->] (-1.2,0) -- (1.2,0) node[right] {{$x$}};
            \\draw[->] (0,-1.2) -- (0,1.2) node[above] {{$y$}};
            \\draw (0,0) circle (1);
            \\fill (0,0) circle (0.03) node[below left] {{$O$}};
            \\fill ({cos_value},{sin_value}) circle (0.03) node[{self._get_label_position(angle)}] {{$P({cos_latex},{sin_latex})$}};
            \\draw[thick,red] (0,0) -- ({cos_value},{sin_value});
            \\draw[blue,->] (0.3,0) arc (0:{angle}:0.3) node[midway,{self._get_angle_label_position(angle)}] {{${angle}^\\circ$}};
        \\end{{tikzpicture}}
        """

    def _get_label_position(self, angle):
        """確定點標籤的位置"""
        if 0 <= angle < 45 or 315 <= angle <= 360:
            return "above right"
        elif 45 <= angle < 135:
            return "above"
        elif 135 <= angle < 225:
            return "above left"
        elif 225 <= angle < 315:
            return "below"
        else:
            return "right"

    def _get_angle_label_position(self, angle):
        """確定角度標籤的位置"""
        if 0 <= angle < 90:
            return "above right"
        elif 90 <= angle < 180:
            return "above left"
        elif 180 <= angle < 270:
            return "below left"
        else:
            return "below right"

    def get_question_size(self) -> int:
        return QuestionSize.SMALL

    def get_category(self) -> str:
        return "三角比"

    def get_subcategory(self) -> str:
        return "三角函數值計算"