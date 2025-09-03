#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
測試基準數據
包含各種已知答案的測試案例，用於驗證計算正確性
"""

import math
import numpy as np

# 基礎幾何測試數據
GEOMETRY_TEST_CASES = {
    "distance": [
        # (點1, 點2, 預期距離)
        ((0, 0), (0, 0), 0.0),
        ((0, 0), (1, 0), 1.0),
        ((0, 0), (0, 1), 1.0),
        ((0, 0), (3, 4), 5.0),  # 3-4-5 直角三角形
        ((1, 1), (4, 5), 5.0),  # 平移的 3-4-5 三角形
        ((-1, -1), (2, 3), 5.0),  # 負坐標
    ],
    
    "midpoint": [
        # (點1, 點2, 預期中點)
        ((0, 0), (2, 0), (1, 0)),
        ((0, 0), (0, 2), (0, 1)),
        ((1, 1), (3, 3), (2, 2)),
        ((-1, -1), (1, 1), (0, 0)),
    ],
    
    "centroid": [
        # (三角形頂點, 預期質心)
        ([(0, 0), (3, 0), (0, 3)], (1, 1)),
        ([(0, 0), (6, 0), (0, 6)], (2, 2)),
        ([(-1, -1), (2, -1), (-1, 2)], (0, 0)),
    ],
    
    "triangle_area": [
        # (三角形頂點, 預期面積)
        ([(0, 0), (1, 0), (0, 1)], 0.5),
        ([(0, 0), (3, 0), (0, 4)], 6.0),  # 3-4-5 直角三角形
        ([(0, 0), (2, 0), (1, math.sqrt(3))], math.sqrt(3)),  # 正三角形
    ],
    
    "angles": [
        # (點1, 頂點, 點2, 預期角度弧度)
        ((1, 0), (0, 0), (0, 1), math.pi/2),  # 90度
        ((1, 0), (0, 0), (-1, 0), math.pi),   # 180度
        ((1, 0), (0, 0), (1, 0), 0),          # 0度
        ((1, 1), (0, 0), (-1, 1), math.pi/2), # 90度，不同方向
    ]
}

# TikZ 格式測試數據
TIKZ_TEST_CASES = {
    "coordinate_format": [
        # (點坐標, 精度, 預期格式)
        ((0, 0), 3, "(0.000,0.000)"),
        ((1.5, 2.7), 1, "(1.5,2.7)"),
        ((math.pi, math.e), 2, "(3.14,2.72)"),
        ((-1.234567, 5.678901), 4, "(-1.2346,5.6789)"),
    ],
    
    "angle_conversion": [
        # (弧度, 預期度數)
        (0, 0),
        (math.pi/2, 90),
        (math.pi, 180),
        (2*math.pi, 360),
        (-math.pi/2, -90),
    ],
    
    "distance_format": [
        # (數值, 單位, 預期格式)
        (1.0, "cm", "1.0cm"),
        (2.5, "mm", "2.5mm"),
        (0.123, "pt", "0.123pt"),
    ]
}

# LaTeX 測試數據
LATEX_TEST_CASES = {
    "escape_sequences": [
        # (原始字符串, 預期轉義後字符串)
        ("$", r"\$"),
        ("%", r"\%"),
        ("&", r"\&"),
        ("#", r"\#"),
        ("^", r"\textasciicircum{}"),
        ("_", r"\_"),
        ("~", r"\textasciitilde{}"),
        ("\\", r"\textbackslash{}"),
        ("{}", r"\{\}"),
    ],
    
    "math_expressions": [
        # (數學表達式, 預期 LaTeX 格式)
        ("x^2", r"$x^2$"),
        ("sqrt(x)", r"$\sqrt{x}$"),
        ("a/b", r"$\frac{a}{b}$"),
        ("pi", r"$\pi$"),
        ("alpha", r"$\alpha$"),
    ]
}

# 協調器測試數據
ORCHESTRATION_TEST_CASES = {
    "question_distribution": [
        {
            "questions": [{"size": 1, "type": "A"} for _ in range(6)],
            "rounds": 2,
            "questions_per_round": 3,
            "expected_distribution": [3, 3]  # 每回的題目數量
        },
        {
            "questions": [{"size": i, "type": f"T{i}"} for i in range(1, 9)],
            "rounds": 3,
            "questions_per_round": 2,
            "expected_distribution": [2, 2, 2]
        }
    ],
    
    "error_scenarios": [
        {
            "scenario": "invalid_output_dir",
            "config": {"output_dir": "/nonexistent/path"},
            "expected_error": "FileNotFoundError"
        },
        {
            "scenario": "empty_questions",
            "config": {"selected_data": []},
            "expected_error": "QuestionGenerationError"
        }
    ]
}

# 性能基準數據
PERFORMANCE_BENCHMARKS = {
    "geometry_operations": {
        "distance_calculation": {
            "small_dataset": 1000,    # 1000 次距離計算
            "medium_dataset": 10000,  # 10000 次距離計算
            "large_dataset": 100000   # 100000 次距離計算
        },
        "triangle_operations": {
            "small_dataset": 100,     # 100 個三角形
            "medium_dataset": 1000,   # 1000 個三角形
            "large_dataset": 5000     # 5000 個三角形
        }
    },
    
    "pdf_generation": {
        "small_test": {
            "rounds": 1,
            "questions_per_round": 5,
            "expected_time_seconds": 10
        },
        "medium_test": {
            "rounds": 3,
            "questions_per_round": 10,
            "expected_time_seconds": 30
        }
    }
}

def get_test_case(category: str, case_name: str = None):
    """獲取測試案例數據
    
    Args:
        category: 測試類別 ('geometry', 'tikz', 'latex', 'orchestration')
        case_name: 特定案例名稱，如果為 None 則返回整個類別
    
    Returns:
        測試案例數據
    """
    test_data_map = {
        "geometry": GEOMETRY_TEST_CASES,
        "tikz": TIKZ_TEST_CASES,
        "latex": LATEX_TEST_CASES,
        "orchestration": ORCHESTRATION_TEST_CASES,
        "performance": PERFORMANCE_BENCHMARKS
    }
    
    if category not in test_data_map:
        raise ValueError(f"Unknown test category: {category}")
    
    data = test_data_map[category]
    
    if case_name is None:
        return data
    
    if case_name not in data:
        raise ValueError(f"Unknown test case '{case_name}' in category '{category}'")
    
    return data[case_name]