#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 數線圖形生成器

此模組提供數線視覺化工具，用於對數內插法等數學概念的圖形展示。
數線由水平線段、三個刻度點和對應的標籤組成，支援上下雙層標註。

主要功能：
1. 繪製水平數線和刻度標記
2. 支援雙層標籤（上方數值、下方數值）
3. 自動計算中間點的線性比例位置
4. 靈活的參數配置（長度、高度、標籤文字）

設計理念：
- 不使用複雜的參數模型，直接接受字典參數
- 不依賴 Composite 系統，直接生成 TikZ 代碼
- 本質上是基礎幾何元素（線段 + 刻度 + 標籤）的簡單組合

Example:
    基本使用範例::

        from figures import get_figure_generator

        generator = get_figure_generator('number_line')()
        params = {
            'lower_value': 2,
            'upper_value': 3,
            'middle_value': 2.5,
            'lower_label': '0.3010',
            'upper_label': '0.4771',
            'middle_label': '?',
            'lower_bottom': '2',
            'upper_bottom': '3',
            'middle_bottom': '2.5',
            'line_length': 6.0,
            'tick_height': 0.2
        }
        tikz_code = generator.generate_tikz(params)

Note:
    - 此生成器設計為輕量級工具，不需要複雜的參數驗證
    - 中間點位置根據數值的線性比例自動計算
    - 適用於各種需要數線展示的數學概念
"""

from typing import Dict, Any
from utils import get_logger
from ..base import FigureGenerator
from .. import register_figure_generator

@register_figure_generator
class NumberLineGenerator(FigureGenerator):
    """數線圖形生成器

    生成水平數線及其刻度和標籤，用於數學概念的視覺化展示。
    主要應用於對數內插法練習，但也可用於其他需要數線表示的場景。

    數線結構：
    - 水平主線：表示數值區間
    - 三個刻度點：左端點、中間點、右端點
    - 雙層標籤：上方標籤（如對數值）、下方標籤（如真數）

    Attributes:
        logger: 日誌記錄器實例

    Example:
        創建對數內插法數線::

            generator = NumberLineGenerator()
            params = {
                'lower_value': 2,      # 左端數值（用於計算比例）
                'upper_value': 3,      # 右端數值
                'middle_value': 2.5,   # 中間數值
                'lower_label': '0.3010',    # 左端上方標籤
                'upper_label': '0.4771',    # 右端上方標籤
                'middle_label': '?',        # 中間上方標籤
                'lower_bottom': '2',        # 左端下方標籤
                'upper_bottom': '3',        # 右端下方標籤
                'middle_bottom': '2.5',     # 中間下方標籤
                'line_length': 6.0,         # 數線總長度（TikZ單位）
                'tick_height': 0.2          # 刻度線高度
            }
            tikz = generator.generate_tikz(params)

    Note:
        - 中間點位置基於 (middle_value - lower_value) / (upper_value - lower_value) 的線性比例
        - 標籤可以包含 LaTeX 數學符號
        - 生成的 TikZ 代碼不包含 tikzpicture 環境
    """

    def __init__(self):
        """初始化數線圖形生成器"""
        self.logger = get_logger(self.__class__.__name__)

    @classmethod
    def get_name(cls) -> str:
        """獲取圖形類型唯一標識符

        Returns:
            str: 圖形類型名稱 'number_line'
        """
        return 'number_line'

    def generate_tikz(self, params: Dict[str, Any]) -> str:
        """生成數線 TikZ 代碼

        根據輸入參數生成完整的數線 TikZ 繪圖代碼，包括主線、刻度和標籤。

        Args:
            params (Dict[str, Any]): 數線參數字典，包含以下鍵值：
                - lower_value (float): 左端點數值，用於計算中間點位置比例
                - upper_value (float): 右端點數值
                - middle_value (float): 中間點數值
                - lower_label (str): 左端點上方標籤文字
                - upper_label (str): 右端點上方標籤文字
                - middle_label (str): 中間點上方標籤文字
                - lower_bottom (str): 左端點下方標籤文字
                - upper_bottom (str): 右端點下方標籤文字
                - middle_bottom (str): 中間點下方標籤文字
                - line_length (float, optional): 數線總長度，預設 6.0
                - tick_height (float, optional): 刻度線高度，預設 0.2

        Returns:
            str: TikZ 圖形內容，不包含 tikzpicture 環境

        Raises:
            KeyError: 當必要參數缺失時
            ZeroDivisionError: 當 upper_value 等於 lower_value 時

        Example:
            生成正向內插法數線（已知真數求對數）::

                params = {
                    'lower_value': 2, 'upper_value': 3, 'middle_value': 2.5,
                    'lower_label': '0.3010', 'upper_label': '0.4771', 'middle_label': '?',
                    'lower_bottom': '2', 'upper_bottom': '3', 'middle_bottom': '2.5'
                }
                # 輸出：上方顯示對數值（中間為?），下方顯示真數

            生成反向內插法數線（已知對數求真數）::

                params = {
                    'lower_value': 2, 'upper_value': 3, 'middle_value': 2.5,
                    'lower_label': '0.3010', 'upper_label': '0.4771', 'middle_label': '0.39',
                    'lower_bottom': '2', 'upper_bottom': '3', 'middle_bottom': '?'
                }
                # 輸出：上方顯示對數值，下方真數（中間為?）
        """
        # 提取參數，設定預設值
        line_length = params.get('line_length', 6.0)
        tick_height = params.get('tick_height', 0.2)

        # 計算中間點在數線上的位置（線性比例）
        lower_val = params['lower_value']
        upper_val = params['upper_value']
        middle_val = params['middle_value']

        # 計算比例：(中間值 - 左端值) / (右端值 - 左端值)
        ratio = (middle_val - lower_val) / (upper_val - lower_val)
        middle_pos = ratio * line_length

        self.logger.debug(f"數線生成: 區間[{lower_val}, {upper_val}], 中間值={middle_val}, 比例={ratio:.4f}, 位置={middle_pos:.4f}")

        # 判斷中間標籤是否需要偏移（避免與端點重疊）
        # 第一、二等分點（ratio < 0.25）或第八、九等分點（ratio > 0.75）
        # 上方標籤 → 向上偏移（遠離數線）
        # 下方標籤 → 向下偏移（遠離數線）
        # 問號也需要偏移
        label_offset_top = 0.0
        label_offset_bottom = 0.0

        if ratio < 0.25 or ratio > 0.75:
            label_offset_top = 0.3   # 上方標籤向上偏移（遠離數線）
            label_offset_bottom = 0.3  # 下方標籤向下偏移（遠離數線）

        # 構建 TikZ 代碼
        tikz_lines = []

        # 1. 主數線（水平線段）
        tikz_lines.append(f"% 對數內插法數線")
        tikz_lines.append(f"\\draw[thick] (0,0) -- ({line_length},0);")

        # 2. 三個刻度線（垂直短線段）
        tikz_lines.append(f"% 刻度線")
        tikz_lines.append(f"\\draw (0,{tick_height}) -- (0,-{tick_height});")
        tikz_lines.append(f"\\draw ({middle_pos},{tick_height}) -- ({middle_pos},-{tick_height});")
        tikz_lines.append(f"\\draw ({line_length},{tick_height}) -- ({line_length},-{tick_height});")

        # 3. 上方標籤（對數值）
        tikz_lines.append(f"% 上方標籤（對數值）")
        tikz_lines.append(f"\\node[above] at (0,{tick_height}) {{{params['lower_label']}}};")
        middle_top_y = tick_height + label_offset_top
        tikz_lines.append(f"\\node[above] at ({middle_pos},{middle_top_y}) {{{params['middle_label']}}};")
        tikz_lines.append(f"\\node[above] at ({line_length},{tick_height}) {{{params['upper_label']}}};")

        # 4. 下方標籤（真數）
        tikz_lines.append(f"% 下方標籤（真數）")
        tikz_lines.append(f"\\node[below] at (0,-{tick_height}) {{{params['lower_bottom']}}};")
        middle_bottom_y = -tick_height - label_offset_bottom
        tikz_lines.append(f"\\node[below] at ({middle_pos},{middle_bottom_y}) {{{params['middle_bottom']}}};")
        tikz_lines.append(f"\\node[below] at ({line_length},-{tick_height}) {{{params['upper_bottom']}}};")

        return '\n'.join(tikz_lines)
