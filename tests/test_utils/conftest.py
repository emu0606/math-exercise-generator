#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
測試工具函數和固定裝置
提供測試所需的共用函數、數據和配置
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any, Tuple
import numpy as np
import sympy

# 測試數據
TEST_POINTS = {
    "origin": (0, 0),
    "unit_x": (1, 0),
    "unit_y": (0, 1),
    "diagonal": (1, 1),
    "negative": (-1, -1),
    "triangle_345": [(0, 0), (3, 0), (0, 4)],  # 3-4-5 直角三角形
    "equilateral": [(0, 0), (1, 0), (0.5, np.sqrt(3)/2)],  # 正三角形
    "isosceles": [(0, 0), (2, 0), (1, 2)]  # 等腰三角形
}

TEST_TRIANGLES = {
    "right_345": {
        "vertices": [(0, 0), (3, 0), (0, 4)],
        "expected_area": 6.0,
        "expected_perimeter": 12.0,
        "expected_angles": [90, 53.13, 36.87]  # 度數
    },
    "equilateral": {
        "vertices": [(0, 0), (1, 0), (0.5, np.sqrt(3)/2)],
        "expected_area": np.sqrt(3)/4,
        "expected_perimeter": 3.0,
        "expected_angles": [60, 60, 60]
    },
    "isosceles": {
        "vertices": [(0, 0), (2, 0), (1, 2)],
        "expected_area": 2.0,
        "expected_perimeter": 2 + 2*np.sqrt(5),
        "expected_angles": [90, 45, 45]  # 近似
    }
}

@pytest.fixture
def temp_dir():
    """創建臨時目錄用於測試"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def test_points():
    """提供測試用的點坐標"""
    return TEST_POINTS

@pytest.fixture
def test_triangles():
    """提供測試用的三角形數據"""
    return TEST_TRIANGLES

@pytest.fixture
def sample_question_data():
    """提供測試用的題目數據"""
    return [
        {
            "question": "計算 2 + 2 = ?",
            "answer": "4",
            "explanation": "這是基本的加法運算",
            "size": 1,
            "difficulty": "EASY",
            "topic": "算術 - 基本加法"
        },
        {
            "question": "求解 x^2 = 16",
            "answer": "x = ±4",
            "explanation": "平方根的計算",
            "size": 2,
            "difficulty": "MEDIUM",
            "topic": "代數 - 二次方程"
        },
        {
            "question": "三角形的面積公式是什麼？",
            "answer": "面積 = 1/2 × 底 × 高",
            "explanation": "三角形面積的基本公式",
            "size": 1,
            "difficulty": "EASY",
            "topic": "幾何 - 面積計算"
        }
    ]

@pytest.fixture
def sample_selected_data():
    """提供測試用的選定題型數據"""
    return [
        {"topic": "算術 - 基本加法", "count": 5},
        {"topic": "代數 - 二次方程", "count": 3},
        {"topic": "幾何 - 面積計算", "count": 2}
    ]

@pytest.fixture(scope="session")
def math_backends():
    """提供可用的數學後端列表"""
    backends = ["python"]
    
    try:
        import numpy
        backends.append("numpy")
    except ImportError:
        pass
    
    try:
        import sympy
        backends.append("sympy")
    except ImportError:
        pass
    
    return backends

@pytest.fixture
def precision_tolerance():
    """提供數值精度容忍度"""
    return {
        "default": 1e-10,
        "medium": 1e-6,
        "low": 1e-3
    }

class TestHelper:
    """測試輔助工具類"""
    
    @staticmethod
    def assert_points_equal(p1: Tuple[float, float], p2: Tuple[float, float], 
                          tolerance: float = 1e-10):
        """斷言兩個點坐標相等（在容忍度內）"""
        assert abs(p1[0] - p2[0]) < tolerance, f"X coordinates differ: {p1[0]} vs {p2[0]}"
        assert abs(p1[1] - p2[1]) < tolerance, f"Y coordinates differ: {p1[1]} vs {p2[1]}"
    
    @staticmethod
    def assert_angles_equal(angle1: float, angle2: float, tolerance: float = 1e-6):
        """斷言兩個角度相等（考慮角度標準化）"""
        from utils.geometry.basic_ops import normalize_angle
        norm1 = normalize_angle(angle1)
        norm2 = normalize_angle(angle2)
        assert abs(norm1 - norm2) < tolerance, f"Angles differ: {norm1} vs {norm2}"
    
    @staticmethod
    def assert_triangles_equal(t1: List[Tuple[float, float]], 
                             t2: List[Tuple[float, float]], 
                             tolerance: float = 1e-10):
        """斷言兩個三角形相等（點的順序可能不同）"""
        assert len(t1) == 3 and len(t2) == 3, "Triangles must have exactly 3 vertices"
        
        # 嘗試找到對應的頂點匹配
        for p1 in t1:
            found_match = False
            for p2 in t2:
                if abs(p1[0] - p2[0]) < tolerance and abs(p1[1] - p2[1]) < tolerance:
                    found_match = True
                    break
            assert found_match, f"No matching vertex found for {p1} in {t2}"
    
    @staticmethod
    def create_test_latex_content() -> str:
        """創建測試用的 LaTeX 內容"""
        return r"""
        \documentclass{article}
        \usepackage{tikz}
        \begin{document}
        \begin{tikzpicture}
        \draw (0,0) -- (1,1);
        \end{tikzpicture}
        \end{document}
        """
    
    @staticmethod
    def create_test_tikz_content() -> str:
        """創建測試用的 TikZ 內容"""
        return r"""
        \draw (0,0) circle (1cm);
        \draw (0,0) -- (1,1) node[midway, above] {$\sqrt{2}$};
        """

@pytest.fixture
def test_helper():
    """提供測試輔助工具類實例"""
    return TestHelper