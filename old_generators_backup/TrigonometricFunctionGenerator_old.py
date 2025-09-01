import sympy
from sympy import sin, cos, tan, cot, csc, sec, pi, simplify, latex
import random
from typing import Dict, Any
from ..base import QuestionGenerator, QuestionSize, register_generator

@register_generator
class TrigonometricFunctionGenerator(QuestionGenerator):
    def __init__(self, options: Dict[str, Any] = None):
        super().__init__(options)
        self.options = options or {}

        self.functions = [sin, cos, tan, cot, sec, csc]
        if self.options.get("functions"):
            self.functions = self.options.get("functions")

        self.angles = [0, 30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 240, 270, 300, 315, 330, 360]
        if self.options.get("angles"):
            self.angles = self.options.get("angles")

        self.difficulty = self.options.get("difficulty", "MEDIUM")

    def generate_question(self) -> Dict[str, Any]:
        angle = random.choice(self.angles)
        func = random.choice(self.functions)
        angle_rad = angle * pi / 180
        func_name = func.__name__
        cos_value = float(sympy.cos(angle_rad).evalf())
        sin_value = float(sympy.sin(angle_rad).evalf())

        tikz_diagram = self._generate_unit_circle_diagram(angle, angle_rad, cos_value, sin_value)
        tikz_wrapped = f"\\resizebox{{!}}{{2cm}}{{%s}}" % tikz_diagram

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

        if (func, angle) in special_cases:
            value_latex = special_cases[(func, angle)]
            explanation = f"""
            計算 {func_name}({angle}^\\circ) 的值：

            {func_name}({angle}^\\circ) 是未定義的值，但可以表示為 {value_latex}

            在數學上，當 {func_name}({angle}^\\circ) 趨近於無限大時，我們記作 {value_latex}

            {tikz_wrapped}
            """
            return {
                "question": f"{tikz_wrapped} \\ {func_name}({angle}^\\circ) = ?",
                "answer": value_latex,
                "explanation": explanation,
                "size": self.get_question_size(),
                "difficulty": self.difficulty
            }

        try:
            value = simplify(func(angle_rad))
            answer = latex(value)
            explanation = f"""
            計算 {func_name}({angle}^\\circ) 的值：

            將角度轉換為弧度：{angle}^\\circ = {latex(angle_rad)} \\text{{ rad}}

            利用特殊角公式計算 {func_name}({latex(angle_rad)}) = {answer}

            {tikz_wrapped}
            """
            return {
                "question": f"{tikz_wrapped} \\ {func_name}({angle}^\\circ) = ?",
                "answer": answer,
                "explanation": explanation,
                "size": QuestionSize.MEDIUM,
                "difficulty": self.difficulty
            }
        except Exception:
            angle = 45
            angle_rad = angle * pi / 180
            value = simplify(func(angle_rad))
            cos_value = float(sympy.cos(angle_rad).evalf())
            sin_value = float(sympy.sin(angle_rad).evalf())
            tikz_diagram = self._generate_unit_circle_diagram(angle, angle_rad, cos_value, sin_value)
            tikz_wrapped = f"\\resizebox{{!}}{{2cm}}{{%s}}" % tikz_diagram
            answer = latex(value)
            explanation = f"""
            計算 {func_name}({angle}^\\circ) 的值：

            將角度轉換為弧度：{angle}^\\circ = {latex(angle_rad)} \\text{{ rad}}

            利用特殊角公式計算 {func_name}({latex(angle_rad)}) = {answer}

            {tikz_wrapped}
            """
            return {
                "question": f"{tikz_wrapped} \\ {func_name}({angle}^\\circ) = ?",
                "answer": answer,
                "explanation": explanation,
                "size": QuestionSize.MEDIUM,
                "difficulty": self.difficulty
            }

    def _generate_unit_circle_diagram(self, angle, angle_rad, cos_value, sin_value):
        cos_expr = simplify(cos(angle_rad))
        sin_expr = simplify(sin(angle_rad))
        cos_latex = latex(cos_expr)
        sin_latex = latex(sin_expr)

        return r"""
        \begin{{tikzpicture}}[scale=2]
            \draw[->] (-1.2,0) -- (1.2,0) node[right] {{$x$}};
            \draw[->] (0,-1.2) -- (0,1.2) node[above] {{$y$}};
            \draw (0,0) circle (1);
            \fill (0,0) circle (0.03) node[below left] {{$O$}};
            \fill ({cos_value},{sin_value}) circle (0.03) node[{self._get_label_position(angle)}] {{$P({cos_latex},{sin_latex})$}};
            \draw[thick,red] (0,0) -- ({cos_value},{sin_value});
            \draw[blue,->] (0.3,0) arc (0:{angle}:0.3) node[midway,{self._get_angle_label_position(angle)}] {{${angle}^\circ$}};
        \end{{tikzpicture}}
        """

    def _get_label_position(self, angle):
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
