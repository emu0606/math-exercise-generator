#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 數學公式庫
"""

# 基礎數學公式
BASIC_FORMULAS = {
    "加法交換律": r"a + b = b + a",
    "加法結合律": r"(a + b) + c = a + (b + c)",
    "乘法交換律": r"a \times b = b \times a",
    "乘法結合律": r"(a \times b) \times c = a \times (b \times c)",
    "乘法分配律": r"a \times (b + c) = a \times b + a \times c",
    "平方差公式": r"a^2 - b^2 = (a+b)(a-b)",
    "完全平方公式": r"a^2 + 2ab + b^2 = (a+b)^2",
    "立方公式": r"a^3 + b^3 = (a+b)(a^2-ab+b^2)",
    "立方差公式": r"a^3 - b^3 = (a-b)(a^2+ab+b^2)",
}

# 代數公式
ALGEBRA_FORMULAS = {
    "二次方程式求根公式": r"x = \frac{-b \pm \sqrt{b^2-4ac}}{2a}",
    "韋達定理": r"x_1 + x_2 = -\frac{b}{a}, x_1 \times x_2 = \frac{c}{a}",
    "等比數列求和": r"S_n = \frac{a_1(1-q^n)}{1-q}, q \neq 1",
    "等差數列求和": r"S_n = \frac{n(a_1+a_n)}{2} = \frac{n(2a_1+(n-1)d)}{2}",
    "餘弦定理": r"c^2 = a^2 + b^2 - 2ab\cos C",
    "正弦定理": r"\frac{a}{\sin A} = \frac{b}{\sin B} = \frac{c}{\sin C} = 2R",
}

# 微積分公式
CALCULUS_FORMULAS = {
    "導數定義": r"f'(x) = \lim_{h \to 0} \frac{f(x+h) - f(x)}{h}",
    "積分定義": r"\int_a^b f(x) dx = \lim_{n \to \infty} \sum_{i=1}^{n} f(x_i) \Delta x",
    "冪函數求導": r"\frac{d}{dx}(x^n) = nx^{n-1}",
    "指數函數求導": r"\frac{d}{dx}(e^x) = e^x",
    "對數函數求導": r"\frac{d}{dx}(\ln x) = \frac{1}{x}",
    "三角函數求導": r"\frac{d}{dx}(\sin x) = \cos x, \frac{d}{dx}(\cos x) = -\sin x",
    "冪函數積分": r"\int x^n dx = \frac{x^{n+1}}{n+1} + C, n \neq -1",
    "指數函數積分": r"\int e^x dx = e^x + C",
    "對數函數積分": r"\int \frac{1}{x} dx = \ln|x| + C",
    "三角函數積分": r"\int \sin x dx = -\cos x + C, \int \cos x dx = \sin x + C",
}

# 幾何公式
GEOMETRY_FORMULAS = {
    "三角形面積": r"S = \frac{1}{2}ah = \frac{1}{2}ab\sin C",
    "圓面積": r"S = \pi r^2",
    "圓周長": r"C = 2\pi r",
    "球體積": r"V = \frac{4}{3}\pi r^3",
    "球表面積": r"S = 4\pi r^2",
    "圓柱體積": r"V = \pi r^2 h",
    "圓柱表面積": r"S = 2\pi r^2 + 2\pi rh",
    "圓錐體積": r"V = \frac{1}{3}\pi r^2 h",
    "圓錐表面積": r"S = \pi r^2 + \pi rl",
}

# 統計公式
STATISTICS_FORMULAS = {
    "算術平均數": r"\bar{x} = \frac{1}{n}\sum_{i=1}^{n}x_i",
    "樣本方差": r"s^2 = \frac{1}{n-1}\sum_{i=1}^{n}(x_i - \bar{x})^2",
    "標準差": r"s = \sqrt{\frac{1}{n-1}\sum_{i=1}^{n}(x_i - \bar{x})^2}",
    "變異係數": r"CV = \frac{s}{\bar{x}}",
    "相關係數": r"r = \frac{\sum_{i=1}^{n}(x_i-\bar{x})(y_i-\bar{y})}{\sqrt{\sum_{i=1}^{n}(x_i-\bar{x})^2\sum_{i=1}^{n}(y_i-\bar{y})^2}}",
}

# 所有公式的集合
ALL_FORMULAS = {}
ALL_FORMULAS.update(BASIC_FORMULAS)
ALL_FORMULAS.update(ALGEBRA_FORMULAS)
ALL_FORMULAS.update(CALCULUS_FORMULAS)
ALL_FORMULAS.update(GEOMETRY_FORMULAS)
ALL_FORMULAS.update(STATISTICS_FORMULAS)

def get_formula(name):
    """獲取指定名稱的公式
    
    Args:
        name (str): 公式名稱
        
    Returns:
        str: 公式的 LaTeX 表示式，如果找不到則返回 None
    """
    return ALL_FORMULAS.get(name)

def get_formulas_by_category(category):
    """獲取指定類別的所有公式
    
    Args:
        category (str): 公式類別，可以是 'basic', 'algebra', 'calculus', 'geometry', 'statistics'
        
    Returns:
        dict: 該類別的所有公式
    """
    categories = {
        'basic': BASIC_FORMULAS,
        'algebra': ALGEBRA_FORMULAS,
        'calculus': CALCULUS_FORMULAS,
        'geometry': GEOMETRY_FORMULAS,
        'statistics': STATISTICS_FORMULAS,
    }
    return categories.get(category, {})

def get_all_formulas():
    """獲取所有公式
    
    Returns:
        dict: 所有公式
    """
    return ALL_FORMULAS
