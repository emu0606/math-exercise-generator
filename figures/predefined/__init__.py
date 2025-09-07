#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 預定義複合圖形生成器包

本包提供預先配置的複合圖形生成器，這些生成器將多個基礎圖形組合
成常用的數學教學圖形，例如標準單位圓、預定義三角形等。

預定義生成器的特點：
- 自動組合多個基礎圖形元素
- 智能處理子圖形之間的定位關係
- 提供豐富的配置選項和樣式控制
- 支援問題和說明兩種變體模式
- 使用 CompositeFigureGenerator 作為底層實現

可用的預定義生成器：
- StandardUnitCircleGenerator: 標準單位圓（包含角度、三角函數值等）
- PredefinedTriangleGenerator: 預定義三角形（各種類型的三角形配置）

Example:
    >>> from figures import get_figure_generator
    >>> 
    >>> # 獲取標準單位圓生成器
    >>> generator = get_figure_generator('standard_unit_circle')
    >>> params = {
    ...     'angle': 45,
    ...     'show_coordinates': True,
    ...     'show_angle': True,
    ...     'variant': 'explanation'
    ... }
    >>> tikz_code = generator.generate_tikz(params)
    
    >>> # 獲取預定義三角形生成器
    >>> triangle_gen = get_figure_generator('predefined_triangle')
    >>> triangle_params = {
    ...     'triangle_type': 'equilateral',
    ...     'side_length': 2.0,
    ...     'variant': 'question'
    ... }
    >>> triangle_tikz = triangle_gen.generate_tikz(triangle_params)

Note:
    預定義生成器是元生成器（meta-generators），它們不直接生成 TikZ 代碼，
    而是構建復合圖形的參數結構，然後委託給 CompositeFigureGenerator 
    進行實際的圖形生成。

    所有預定義生成器都遵循標準的 FigureGenerator 接口，確保與系統
    其他部分的兼容性。
"""

# 標記為 Python 包
# 預定義生成器通過 @register_figure_generator 裝飾器自動註冊