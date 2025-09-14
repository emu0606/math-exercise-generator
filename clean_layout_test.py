#!/usr/bin/env python3
"""
乾淨的小型佈局引擎測試版

專注實現方案A（行高度鎖定機制），避免原項目的複雜Bug。
重點測試六種尺寸混排情況，輸出HTML視覺化結果。

設計原則：
1. 行狀態追蹤：每行記錄鎖定高度
2. 簡單規則：空行接受任何高度，已鎖定行只接受相同高度
3. 視覺化驗證：HTML網格清晰展示佈局效果

作者：Claude Code
日期：2025-09-14
"""

from enum import IntEnum
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime


class QuestionSize(IntEnum):
    """題目尺寸枚舉"""
    SMALL = 1   # 小題 (1x1) - 1格
    WIDE = 2    # 寬題 (2x1) - 2格
    SQUARE = 3  # 方題 (1x2) - 2格
    MEDIUM = 4  # 中題 (2x2) - 4格
    LARGE = 5   # 大題 (3x2) - 6格
    EXTRA = 6   # 超大題 (4x2) - 8格


class Question:
    """題目類別"""
    def __init__(self, label: str, size: QuestionSize):
        self.label = label
        self.size = size
        self.width, self.height = self._get_dimensions()

    def _get_dimensions(self) -> Tuple[int, int]:
        """獲取題目的寬度和高度"""
        dimensions = {
            QuestionSize.SMALL: (1, 1),   # 1x1
            QuestionSize.WIDE: (2, 1),    # 2x1
            QuestionSize.SQUARE: (1, 2),  # 1x2
            QuestionSize.MEDIUM: (2, 2),  # 2x2
            QuestionSize.LARGE: (3, 2),   # 3x2
            QuestionSize.EXTRA: (4, 2),   # 4x2
        }
        return dimensions.get(self.size, (1, 1))

    def get_cell_count(self) -> int:
        """獲取佔用格子數"""
        return self.width * self.height

    def __repr__(self):
        return f"{self.label}({self.width}x{self.height})"


class CleanGrid:
    """乾淨的網格管理器"""

    def __init__(self, width: int = 4, height: int = 8):
        self.width = width
        self.height = height

        # 網格狀態：None表示空格，存儲題目標籤
        self.grid = [[None for _ in range(width)] for _ in range(height)]

        # 行狀態追蹤：-1表示空行，其他值表示該行鎖定的高度
        self.row_locked_heights = [-1] * height

        # 統計信息
        self.placed_questions = []

    def is_position_free(self, row: int, col: int, width: int, height: int) -> bool:
        """檢查指定位置是否可以放置題目"""
        # 檢查邊界
        if row + height > self.height or col + width > self.width:
            return False

        # 檢查佔用情況
        for r in range(row, row + height):
            for c in range(col, col + width):
                if self.grid[r][c] is not None:
                    return False

        return True

    def is_row_height_compatible(self, row: int, question_height: int) -> bool:
        """檢查行高度相容性（方案A核心邏輯）"""
        for r in range(row, row + question_height):
            if r >= self.height:
                return False

            # 如果行未鎖定（-1），可以接受任何高度
            if self.row_locked_heights[r] == -1:
                continue

            # 如果行已鎖定，必須高度匹配
            if self.row_locked_heights[r] != question_height:
                return False

        return True

    def place_question(self, question: Question, row: int, col: int) -> bool:
        """放置題目到指定位置"""
        # 檢查是否可以放置
        if not self.is_position_free(row, col, question.width, question.height):
            return False

        if not self.is_row_height_compatible(row, question.height):
            return False

        # 執行放置
        for r in range(row, row + question.height):
            for c in range(col, col + question.width):
                self.grid[r][c] = question.label

        # 鎖定相關行的高度
        for r in range(row, row + question.height):
            self.row_locked_heights[r] = question.height

        # 記錄放置信息
        self.placed_questions.append({
            'question': question,
            'row': row,
            'col': col,
            'width': question.width,
            'height': question.height
        })

        return True

    def get_occupancy_rate(self) -> float:
        """計算佔用率"""
        total_cells = self.width * self.height
        occupied_cells = sum(
            1 for row in self.grid for cell in row if cell is not None
        )
        return occupied_cells / total_cells if total_cells > 0 else 0

    def print_debug_info(self):
        """打印調試信息"""
        print("=== 網格狀態 ===")
        for r, row in enumerate(self.grid):
            row_str = " ".join(f"[{cell:2}]" if cell else "[ ]" for cell in row)
            lock_status = f"鎖定高度={self.row_locked_heights[r]}" if self.row_locked_heights[r] != -1 else "未鎖定"
            print(f"行{r}: {row_str} ({lock_status})")
        print()


class SchemeALayoutEngine:
    """方案A佈局引擎（行高度鎖定機制）"""

    def __init__(self, grid_width: int = 4, grid_height: int = 8):
        self.grid_width = grid_width
        self.grid_height = grid_height

    def layout_questions(self, questions: List[Question]) -> CleanGrid:
        """執行佈局算法"""
        grid = CleanGrid(self.grid_width, self.grid_height)

        print(f"開始佈局 {len(questions)} 道題目")
        print("=" * 50)

        for i, question in enumerate(questions):
            print(f"\n處理題目 {question}")

            # 方案A核心：行優先遍歷 + 高度相容性檢查
            placed = False
            for row in range(self.grid_height - question.height + 1):
                # 檢查行高度相容性
                if not grid.is_row_height_compatible(row, question.height):
                    print(f"  行{row}: 高度不相容 (鎖定高度={grid.row_locked_heights[row]})")
                    continue

                # 在該行內尋找位置（列優先）
                for col in range(self.grid_width - question.width + 1):
                    if grid.is_position_free(row, col, question.width, question.height):
                        if grid.place_question(question, row, col):
                            print(f"  ✅ 成功放置在 行{row}, 列{col}")
                            placed = True
                            break

                if placed:
                    break

            if not placed:
                print(f"  ❌ 無法放置題目 {question}")

            # 顯示當前狀態（僅前幾步）
            if i < 5:
                grid.print_debug_info()

        print(f"\n佈局完成！佔用率: {grid.get_occupancy_rate():.1%}")
        return grid


class HTMLVisualizer:
    """HTML視覺化輸出器"""

    def __init__(self):
        self.colors = [
            '#FFE6E6', '#E6F3FF', '#E6FFE6', '#FFF0E6', '#F0E6FF',
            '#FFE6F0', '#E6FFFF', '#FFFFE6', '#F5F5DC', '#E6E6FA',
            '#FFE4E1', '#F0FFF0', '#FFF8DC', '#E0FFFF', '#FFEFD5'
        ]

    def generate_html(self, grid: CleanGrid, test_name: str) -> str:
        """生成HTML視覺化"""
        # 收集題目信息
        question_info = {}
        color_map = {}

        for placement in grid.placed_questions:
            question = placement['question']
            label = question.label
            if label not in question_info:
                question_info[label] = {
                    'size': question.size,
                    'width': question.width,
                    'height': question.height,
                    'cells': question.get_cell_count()
                }
                color_map[label] = self.colors[len(color_map) % len(self.colors)]

        # 生成HTML
        html = self._get_html_template(test_name)

        # 網格表格
        grid_html = '<table class="grid-table">\n'
        grid_html += '<tr><th>行\\列</th>'
        for col in range(grid.width):
            grid_html += f'<th>列{col}</th>'
        grid_html += '<th>行狀態</th></tr>\n'

        for row in range(grid.height):
            grid_html += f'<tr><th>行{row}</th>'
            for col in range(grid.width):
                cell_content = grid.grid[row][col]
                if cell_content:
                    color = color_map.get(cell_content, '#f0f0f0')
                    grid_html += f'<td style="background-color: {color}; color: #2c3e50; font-weight: bold;">{cell_content}</td>'
                else:
                    grid_html += '<td></td>'

            # 顯示行鎖定狀態
            lock_status = grid.row_locked_heights[row]
            lock_text = f"🔒{lock_status}" if lock_status != -1 else "🔓"
            grid_html += f'<td class="row-status">{lock_text}</td>'
            grid_html += '</tr>\n'

        grid_html += '</table>\n'

        # 題目規格列表
        specs_html = '<div class="specs-section">\n<h2>📋 題目規格</h2>\n'
        size_names = {
            QuestionSize.SMALL: "小題 (1×1)",
            QuestionSize.WIDE: "寬題 (2×1)",
            QuestionSize.SQUARE: "方題 (1×2)",
            QuestionSize.MEDIUM: "中題 (2×2)",
            QuestionSize.LARGE: "大題 (3×2)",
            QuestionSize.EXTRA: "超大題 (4×2)"
        }

        for label, info in question_info.items():
            size_desc = size_names.get(info['size'], f"未知尺寸")
            color = color_map[label]
            specs_html += f'''
            <div class="question-spec">
                <div class="color-indicator" style="background-color: {color};"></div>
                <div><strong>{label}:</strong> {size_desc} ({info['cells']}格)</div>
            </div>
            '''

        # 分析報告
        analysis_html = self._generate_analysis(grid)
        specs_html += analysis_html + '</div>'

        # 組合完整HTML
        html = html.replace('{GRID_CONTENT}', grid_html)
        html = html.replace('{SPECS_CONTENT}', specs_html)
        html = html.replace('{TEST_NAME}', test_name)

        return html

    def _generate_analysis(self, grid: CleanGrid) -> str:
        """生成分析報告"""
        analysis = '<h2>🔍 方案A分析報告</h2>\n'

        # 檢查混合高度問題
        mixed_height_rows = []
        for row in range(grid.height):
            heights_in_row = set()
            for col in range(grid.width):
                if grid.grid[row][col]:
                    # 找到該題目的實際高度
                    for placement in grid.placed_questions:
                        if (placement['row'] <= row < placement['row'] + placement['height'] and
                            placement['col'] <= col < placement['col'] + placement['width']):
                            heights_in_row.add(placement['height'])
                            break

            if len(heights_in_row) > 1:
                mixed_height_rows.append((row, heights_in_row))

        if mixed_height_rows:
            analysis += '<div class="warning">\n'
            analysis += '<strong>⚠️ 發現混合高度問題:</strong><br>\n'
            for row, heights in mixed_height_rows:
                analysis += f'• 行{row}: 混合高度 {sorted(list(heights))}<br>\n'
            analysis += '</div>\n'
        else:
            analysis += '<div class="success">\n'
            analysis += '<strong>✅ 行高度鎖定機制正常工作</strong><br>\n'
            analysis += '所有行內題目高度一致，成功避免參差排列\n'
            analysis += '</div>\n'

        # 空間利用統計
        total_questions = len(grid.placed_questions)
        total_cells = sum(p['width'] * p['height'] for p in grid.placed_questions)
        grid_cells = grid.width * grid.height
        occupancy = grid.get_occupancy_rate()

        analysis += '<div class="stats">\n'
        analysis += '<strong>📊 空間利用統計:</strong><br>\n'
        analysis += f'• 放置題目: {total_questions} 道<br>\n'
        analysis += f'• 佔用格子: {total_cells}/{grid_cells} ({occupancy:.1%})<br>\n'
        analysis += f'• 剩餘空間: {grid_cells - total_cells} 格子<br>\n'

        # 行利用分析
        used_rows = len([h for h in grid.row_locked_heights if h != -1])
        analysis += f'• 使用行數: {used_rows}/{grid.height}<br>\n'
        analysis += '</div>\n'

        return analysis

    def _get_html_template(self, test_name: str) -> str:
        """HTML模板"""
        return f'''
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>方案A測試: {test_name}</title>
    <style>
        body {{
            font-family: 'Courier New', monospace;
            margin: 20px;
            background-color: #f8f9fa;
        }}
        .container {{
            display: flex;
            gap: 30px;
            max-width: 1200px;
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            margin-bottom: 20px;
        }}
        .grid-table {{
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .grid-table td, .grid-table th {{
            width: 50px;
            height: 35px;
            border: 2px dashed #bdc3c7;
            text-align: center;
            vertical-align: middle;
            font-weight: bold;
            font-size: 11px;
        }}
        .grid-table th {{
            background-color: #ecf0f1;
            border: 1px solid #bdc3c7;
        }}
        .row-status {{
            background-color: #f8f9fa !important;
            border-left: 3px solid #3498db !important;
            font-size: 12px;
        }}
        .specs-section {{
            flex: 0 0 350px;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .question-spec {{
            display: flex;
            align-items: center;
            margin: 8px 0;
            padding: 8px;
            border-radius: 4px;
            background: #f8f9fa;
        }}
        .color-indicator {{
            width: 20px;
            height: 20px;
            border-radius: 3px;
            margin-right: 10px;
            border: 1px solid #666;
        }}
        .stats {{
            background: #e8f4fd;
            padding: 15px;
            border-radius: 6px;
            margin: 20px 0;
        }}
        .success {{
            background: #d4edda;
            border-left: 4px solid #28a745;
            padding: 15px;
            border-radius: 6px;
            margin: 10px 0;
        }}
        .warning {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            border-radius: 6px;
            margin: 10px 0;
        }}
    </style>
</head>
<body>
    <h1>🧪 方案A佈局引擎測試版</h1>
    <h2 style="text-align: center; color: #7f8c8d;">{{TEST_NAME}}</h2>
    <div class="container">
        <div class="grid-section">
            {{GRID_CONTENT}}
        </div>
        {{SPECS_CONTENT}}
    </div>
    <div style="text-align: center; margin-top: 20px; color: #6c757d; font-size: 12px;">
        生成時間: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    </div>
</body>
</html>
        '''


class TestCases:
    """測試案例設計器"""

    @staticmethod
    def _sort_by_height_then_size(questions):
        """按高度優先、尺寸次要排序（方案A的預排序邏輯）"""
        def sort_key(q):
            return (q.height, q.size.value, q.label)  # height優先、size次要、label最後
        return sorted(questions, key=sort_key)

    @staticmethod
    def create_basic_small_test():
        """基礎SMALL題目測試 - 應該緊湊排列"""
        questions = []
        for i in range(8):
            questions.append(Question(f"S{i+1}", QuestionSize.SMALL))
        # SMALL全是height=1，排序不會改變
        return questions, "8個SMALL題目緊湊測試"

    @staticmethod
    def create_six_sizes_basic():
        """六種尺寸基礎混排測試"""
        questions = [
            Question("S1", QuestionSize.SMALL),   # height=1
            Question("W1", QuestionSize.WIDE),    # height=1
            Question("Q1", QuestionSize.SQUARE),  # height=2
            Question("M1", QuestionSize.MEDIUM),  # height=2
            Question("L1", QuestionSize.LARGE),   # height=2
            Question("E1", QuestionSize.EXTRA)    # height=2
        ]
        # 方案A預排序：height=1優先
        sorted_questions = TestCases._sort_by_height_then_size(questions)
        return sorted_questions, "六種尺寸基礎混排（預排序）"

    @staticmethod
    def create_six_sizes_intensive():
        """六種尺寸高密度測試"""
        questions = [
            # SMALL群 (6格) - height=1
            Question("S1", QuestionSize.SMALL),
            Question("S2", QuestionSize.SMALL),
            Question("S3", QuestionSize.SMALL),
            Question("S4", QuestionSize.SMALL),
            Question("S5", QuestionSize.SMALL),
            Question("S6", QuestionSize.SMALL),

            # WIDE群 (6格) - height=1
            Question("W1", QuestionSize.WIDE),
            Question("W2", QuestionSize.WIDE),
            Question("W3", QuestionSize.WIDE),

            # SQUARE群 (6格) - height=2
            Question("Q1", QuestionSize.SQUARE),
            Question("Q2", QuestionSize.SQUARE),
            Question("Q3", QuestionSize.SQUARE),

            # MEDIUM (4格) - height=2
            Question("M1", QuestionSize.MEDIUM),

            # LARGE (6格) - height=2
            Question("L1", QuestionSize.LARGE),

            # EXTRA (8格) - height=2
            Question("E1", QuestionSize.EXTRA)
        ]
        # 方案A預排序：height=1優先
        sorted_questions = TestCases._sort_by_height_then_size(questions)
        return sorted_questions, "六種尺寸高密度混排（預排序32格挑戰）"

    @staticmethod
    def create_extreme_contrast():
        """極端尺寸對比測試"""
        questions = [
            # 故意打亂順序測試預排序效果
            Question("E1", QuestionSize.EXTRA),   # height=2
            Question("S1", QuestionSize.SMALL),   # height=1
            Question("L1", QuestionSize.LARGE),   # height=2
            Question("W1", QuestionSize.WIDE),    # height=1
            Question("S2", QuestionSize.SMALL),   # height=1
            Question("M1", QuestionSize.MEDIUM),  # height=2
            Question("S3", QuestionSize.SMALL),   # height=1
            Question("Q1", QuestionSize.SQUARE),  # height=2
            Question("S4", QuestionSize.SMALL)    # height=1
        ]
        # 方案A預排序：height=1優先
        sorted_questions = TestCases._sort_by_height_then_size(questions)
        return sorted_questions, "極端尺寸對比（預排序：小題優先聚集）"

    @staticmethod
    def create_order_sensitivity_test():
        """順序敏感性測試 - 對比預排序vs無排序"""
        questions_raw = [
            Question("S1", QuestionSize.SMALL),   # height=1
            Question("Q1", QuestionSize.SQUARE),  # height=2
            Question("S2", QuestionSize.SMALL),   # height=1
            Question("W1", QuestionSize.WIDE),    # height=1
            Question("S3", QuestionSize.SMALL)    # height=1
        ]

        # 方案A：預排序版本
        questions_sorted = TestCases._sort_by_height_then_size(questions_raw)

        return [
            (questions_raw, "順序A: 原始交錯排列（未排序）"),
            (questions_sorted, "順序B: 方案A預排序（height=1優先）")
        ]

    @staticmethod
    def create_boundary_test():
        """邊界條件測試 - 剛好32格"""
        questions = [
            # 故意打亂順序
            Question("M1", QuestionSize.MEDIUM),    # height=2, 4格
            Question("S1", QuestionSize.SMALL),     # height=1, 1格
            Question("M2", QuestionSize.MEDIUM),    # height=2, 4格
            Question("W1", QuestionSize.WIDE),      # height=1, 2格
            Question("L1", QuestionSize.LARGE),     # height=2, 6格
            Question("S2", QuestionSize.SMALL),     # height=1, 1格
            Question("Q1", QuestionSize.SQUARE),    # height=2, 2格
            Question("S3", QuestionSize.SMALL),     # height=1, 1格
            Question("Q2", QuestionSize.SQUARE),    # height=2, 2格
            Question("W2", QuestionSize.WIDE),      # height=1, 2格
            Question("Q3", QuestionSize.SQUARE),    # height=2, 2格
            Question("S4", QuestionSize.SMALL),     # height=1, 1格
            Question("S5", QuestionSize.SMALL),     # height=1, 1格
            Question("S6", QuestionSize.SMALL),     # height=1, 1格
            Question("S7", QuestionSize.SMALL),     # height=1, 1格
            Question("S8", QuestionSize.SMALL)      # height=1, 1格 = 總計32格
        ]
        # 方案A預排序：height=1優先
        sorted_questions = TestCases._sort_by_height_then_size(questions)
        return sorted_questions, "邊界測試 - 精確32格（預排序）"


def run_test_case(test_name: str, questions: List[Question]) -> str:
    """執行單個測試案例"""
    print(f"\n{'='*60}")
    print(f"🧪 執行測試: {test_name}")
    print(f"題目數量: {len(questions)}")
    total_cells = sum(q.get_cell_count() for q in questions)
    print(f"總格子數: {total_cells}/32")

    # 顯示題目組成
    size_count = {}
    height_count = {}
    for q in questions:
        size_name = q.size.name
        size_count[size_name] = size_count.get(size_name, 0) + 1
        height_count[f"height={q.height}"] = height_count.get(f"height={q.height}", 0) + 1

    print(f"題目組成: {', '.join(f'{k}×{v}' for k, v in size_count.items())}")
    print(f"高度分布: {', '.join(f'{k}×{v}' for k, v in height_count.items())}")

    # 顯示處理順序（驗證預排序）
    print(f"處理順序: {' → '.join(q.label for q in questions)}")

    # 執行佈局
    engine = SchemeALayoutEngine()
    grid = engine.layout_questions(questions)

    # 生成HTML
    visualizer = HTMLVisualizer()
    html_content = visualizer.generate_html(grid, test_name)

    return html_content


def main():
    """主測試函數"""
    print("🚀 方案A佈局引擎測試版")
    print("專注測試行高度鎖定機制，避免原項目Bug干擾")

    # 測試案例1: 基礎SMALL題目
    questions1, name1 = TestCases.create_basic_small_test()
    html1 = run_test_case(name1, questions1)
    with open("test_clean_1_small_basic.html", "w", encoding="utf-8") as f:
        f.write(html1)
    print(f"✅ 生成: test_clean_1_small_basic.html")

    # 測試案例2: 六種尺寸基礎
    questions2, name2 = TestCases.create_six_sizes_basic()
    html2 = run_test_case(name2, questions2)
    with open("test_clean_2_six_basic.html", "w", encoding="utf-8") as f:
        f.write(html2)
    print(f"✅ 生成: test_clean_2_six_basic.html")

    # 測試案例3: 六種尺寸高密度
    questions3, name3 = TestCases.create_six_sizes_intensive()
    html3 = run_test_case(name3, questions3)
    with open("test_clean_3_six_intensive.html", "w", encoding="utf-8") as f:
        f.write(html3)
    print(f"✅ 生成: test_clean_3_six_intensive.html")

    # 測試案例4: 極端尺寸對比
    questions4, name4 = TestCases.create_extreme_contrast()
    html4 = run_test_case(name4, questions4)
    with open("test_clean_4_extreme.html", "w", encoding="utf-8") as f:
        f.write(html4)
    print(f"✅ 生成: test_clean_4_extreme.html")

    # 測試案例5: 順序敏感性測試
    order_tests = TestCases.create_order_sensitivity_test()
    for i, (questions, name) in enumerate(order_tests):
        html = run_test_case(name, questions)
        filename = f"test_clean_5_{i+1}_order.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"✅ 生成: {filename}")

    # 測試案例6: 邊界條件
    questions6, name6 = TestCases.create_boundary_test()
    html6 = run_test_case(name6, questions6)
    with open("test_clean_6_boundary.html", "w", encoding="utf-8") as f:
        f.write(html6)
    print(f"✅ 生成: test_clean_6_boundary.html")

    print(f"\n🎯 所有測試完成！")
    print("請開啟HTML檔案查看方案A的純淨佈局效果")


if __name__ == "__main__":
    main()