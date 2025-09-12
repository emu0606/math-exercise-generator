#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 佈局引擎
實現支持分頁的佈局算法，根據題目大小動態計算格子位置
"""

from typing import Dict, List, Any, Tuple, Optional
from generators.base import QuestionSize
from pprint import pprint

class LayoutEngine:
    """佈局引擎
    
    實現支持分頁的佈局算法，根據題目大小動態計算格子位置。
    基於 4x10 網格，根據題目生成器返回的 QuestionSize 動態計算格子大小和位置。
    當題目無法在當前頁面剩餘空間放置時，自動結束當前頁並在新頁面繼續佈局。
    """
    
    def __init__(self):
        """初始化佈局引擎"""
        # 網格定義
        self.grid_width = 4  # 列數
        self.grid_height = 8  # 行數 
        
        # 尺寸映射: QuestionSize -> (width_cells, height_cells)
        self.size_map = {
            QuestionSize.SMALL: (1, 1),   # 一單位大小
            QuestionSize.WIDE: (2, 1),    # 左右兩單位，上下一單位
            QuestionSize.SQUARE: (1, 2),  # 左右一單位，上下兩單位
            QuestionSize.MEDIUM: (2, 2),  # 左右兩單位，上下兩單位
            QuestionSize.LARGE: (3, 2),   # 左右三單位，上下兩單位
            QuestionSize.EXTRA: (4, 2),   # 左右四單位，上下兩單位
        }
        
    def layout(self, questions: List[Dict[str, Any]], questions_per_round: int = 0) -> List[Dict[str, Any]]:
        """佈局算法
        
        根據題目大小和佈局策略，計算每個題目在 PDF 頁面網格中的位置。
        當題目無法在當前頁面剩餘空間放置時，自動結束當前頁並在新頁面繼續佈局。
        如果指定了 questions_per_round，則在處理完每回的題目後強制換頁。
        
        Args:
            questions: 題目列表，每個題目是一個字典，至少包含 'question', 'answer', 'explanation', 'size' 鍵
                      'size' 可以是 QuestionSize 枚舉值或對應的整數值
            questions_per_round: 每回題數，如果大於0，則在處理完每回的題目後強制換頁
                      
        Returns:
            包含佈局信息的題目列表，每個題目字典增加了 'page', 'row', 'col', 'width_cells', 'height_cells',
            'round_num', 'question_num_in_round' 鍵
        """
        # 初始化結果列表
        layout_results = []
        
        # 初始化頁面計數器
        current_page = 1
        
        # 初始化網格狀態記錄矩陣 (每頁一個)
        # grid[page][row][col] = True 表示該位置已被佔用
        grids = {current_page: [[False for _ in range(self.grid_width)] for _ in range(self.grid_height)]}
        
        # 處理每個題目
        for i, question in enumerate(questions):
            # 計算回數和回內題號
            if questions_per_round > 0:
                round_num = (i // questions_per_round) + 1
                question_num_in_round = (i % questions_per_round) + 1
            else:
                # 如果沒有指定每回題數，則所有題目都屬於第一回
                round_num = 1
                question_num_in_round = i + 1
            
            # 檢查是否需要按回次強制換頁
            if questions_per_round > 0 and i > 0 and i % questions_per_round == 0:
                # 強制換頁
                current_page += 1
                grids[current_page] = [[False for _ in range(self.grid_width)] for _ in range(self.grid_height)]
                print(f"按回次強制換頁：第 {i // questions_per_round + 1} 回開始，頁碼 {current_page}")
            
            # 獲取題目大小
            size = question.get('size', 1)
            # 如果 size 是整數，轉換為 QuestionSize 枚舉
            if isinstance(size, int):
                size = QuestionSize(size)
            
            # 獲取對應的格子尺寸
            width_cells, height_cells = self.size_map.get(size, (1, 1))
            
            # 尋找放置位置
            placed = False
            
            # 優先放置高度為 1 的格子
            if height_cells == 1:
                # 從第一行開始嘗試放置
                for row in range(self.grid_height - height_cells + 1):
                    if placed:
                        break
                    for col in range(self.grid_width - width_cells + 1):
                        if self.can_place_at(current_page, row, col, width_cells, height_cells, grids):
                            # 標記佔用
                            for r in range(height_cells):
                                for c in range(width_cells):
                                    grids[current_page][row + r][col + c] = True
                            
                            # 添加佈局信息
                            layout_results.append({
                                **question,
                                'page': current_page,
                                'row': row,
                                'col': col,
                                'width_cells': width_cells,
                                'height_cells': height_cells,
                                'round_num': round_num,
                                'question_num_in_round': question_num_in_round
                            })
                            
                            placed = True
                            break
            
            # 如果高度為 1 的格子無法放置，或者本身就是高度為 2 的格子
            if not placed:
                # 從第一行開始嘗試放置
                for row in range(self.grid_height - height_cells + 1):
                    if placed:
                        break
                    for col in range(self.grid_width - width_cells + 1):
                        if self.can_place_at(current_page, row, col, width_cells, height_cells, grids):
                            # 標記佔用
                            for r in range(height_cells):
                                for c in range(width_cells):
                                    grids[current_page][row + r][col + c] = True
                            
                            # 添加佈局信息
                            layout_results.append({
                                **question,
                                'page': current_page,
                                'row': row,
                                'col': col,
                                'width_cells': width_cells,
                                'height_cells': height_cells,
                                'round_num': round_num,
                                'question_num_in_round': question_num_in_round
                            })
                            
                            placed = True
                            break
            
            # 如果當前頁無法放置，創建新頁面
            if not placed:
                current_page += 1
                grids[current_page] = [[False for _ in range(self.grid_width)] for _ in range(self.grid_height)]
                
                # 在新頁面嘗試放置
                for row in range(self.grid_height - height_cells + 1):
                    if placed:
                        break
                    for col in range(self.grid_width - width_cells + 1):
                        if self.can_place_at(current_page, row, col, width_cells, height_cells, grids):
                            # 標記佔用
                            for r in range(height_cells):
                                for c in range(width_cells):
                                    grids[current_page][row + r][col + c] = True
                            
                            # 添加佈局信息
                            layout_results.append({
                                **question,
                                'page': current_page,
                                'row': row,
                                'col': col,
                                'width_cells': width_cells,
                                'height_cells': height_cells,
                                'round_num': round_num,
                                'question_num_in_round': question_num_in_round
                            })
                            
                            placed = True
                            break
            
            # 如果仍然無法放置，這是一個錯誤情況
            if not placed:
                raise ValueError(f"無法放置題目，尺寸過大: {width_cells}x{height_cells}")
		
        return layout_results
    
    def can_place_at(self, page: int, row: int, col: int, width_cells: int, height_cells: int, 
                     grids: Dict[int, List[List[bool]]]) -> bool:
        """檢查是否可以在指定位置放置格子
        
        Args:
            page: 頁碼
            row: 行索引
            col: 列索引
            width_cells: 寬度（格子數）
            height_cells: 高度（格子數）
            grids: 網格狀態記錄
            
        Returns:
            是否可以放置
        """
        # 檢查是否超出網格範圍
        if row + height_cells > self.grid_height or col + width_cells > self.grid_width:
            return False
        
        # 檢查是否與已有格子重疊
        for r in range(height_cells):
            for c in range(width_cells):
                if grids[page][row + r][col + c]:
                    return False
        
        return True