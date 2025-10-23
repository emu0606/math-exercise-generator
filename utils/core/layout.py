"""
佈局引擎

提供智能化的題目佈局算法：
1. 動態網格佈局系統
2. 自動分頁邏輯
3. 題目大小適配
4. 回合制佈局支援
5. 統一的日誌記錄

使用方式：
    from utils.core.layout import LayoutEngine
    
    # 創建佈局引擎
    layout_engine = LayoutEngine()
    
    # 執行佈局
    layout_results = layout_engine.layout(questions)
"""

from typing import Dict, List, Any, Tuple, Optional, Union
from enum import IntEnum
from .logging import get_logger

# 模組專用日誌器
logger = get_logger(__name__)


class QuestionSize(IntEnum):
    """題目尺寸枚舉
    
    定義標準化的題目尺寸選項。
    """
    SMALL = 1   # 小題 (1x1)
    WIDE = 2    # 寬題 (2x1)
    SQUARE = 3  # 方題 (1x2)
    MEDIUM = 4  # 中題 (2x2)
    LARGE = 5   # 大題 (3x2)
    EXTRA = 6   # 超大題 (4x2)


class LayoutError(Exception):
    """佈局系統專用異常類
    
    用於佈局相關的錯誤情況。
    """
    pass


class GridManager:
    """網格管理器
    
    負責管理多頁面的網格狀態，追蹤每個位置的佔用情況。
    """
    
    def __init__(self, grid_width: int = 4, grid_height: int = 10):
        """初始化網格管理器
        
        Args:
            grid_width: 網格寬度（列數）
            grid_height: 網格高度（行數）
        """
        self.grid_width = grid_width
        self.grid_height = grid_height
        
        # 多頁面網格狀態: {page_number: [[bool]]}
        # True 表示該位置已被佔用
        self._grids: Dict[int, List[List[bool]]] = {}

        # 行高度鎖定狀態追蹤 {page: [row_heights]}
        # -1表示未鎖定，1表示height=1鎖定，2表示height=2鎖定
        self._row_locked_heights: Dict[int, List[int]] = {}

        logger.debug(f"初始化網格管理器: {grid_width}x{grid_height}")
    
    def create_page(self, page_number: int) -> None:
        """創建新頁面的網格
        
        Args:
            page_number: 頁碼
        """
        self._grids[page_number] = [
            [False for _ in range(self.grid_width)]
            for _ in range(self.grid_height)
        ]

        # 初始化行高度鎖定狀態
        self._row_locked_heights[page_number] = [-1] * self.grid_height
        logger.debug(f"創建頁面 {page_number}")
    
    def can_place_at(self, page: int, row: int, col: int, 
                    width_cells: int, height_cells: int) -> bool:
        """檢查是否可以在指定位置放置題目
        
        Args:
            page: 頁碼
            row: 起始行
            col: 起始列
            width_cells: 寬度（格子數）
            height_cells: 高度（格子數）
            
        Returns:
            是否可以放置
        """
        # 檢查頁面是否存在
        if page not in self._grids:
            return False
        
        # 檢查是否超出網格範圍
        if (row + height_cells > self.grid_height or 
            col + width_cells > self.grid_width):
            return False
        
        # 檢查是否與已有題目重疊
        for r in range(height_cells):
            for c in range(width_cells):
                if self._grids[page][row + r][col + c]:
                    return False
        
        return True
    
    def place_at(self, page: int, row: int, col: int, 
                width_cells: int, height_cells: int) -> None:
        """在指定位置放置題目
        
        Args:
            page: 頁碼
            row: 起始行
            col: 起始列
            width_cells: 寬度（格子數）
            height_cells: 高度（格子數）
            
        Raises:
            LayoutError: 如果無法放置
        """
        if not self.can_place_at(page, row, col, width_cells, height_cells):
            raise LayoutError(
                f"無法在頁面 {page} 的位置 ({row}, {col}) "
                f"放置大小為 {width_cells}x{height_cells} 的題目"
            )
        
        # 標記佔用
        for r in range(height_cells):
            for c in range(width_cells):
                self._grids[page][row + r][col + c] = True

        # 更新行鎖定狀態
        if page in self._row_locked_heights:
            for r in range(row, row + height_cells):
                if r < len(self._row_locked_heights[page]):
                    self._row_locked_heights[page][r] = height_cells

        logger.debug(f"放置題目：頁面 {page}, 位置 ({row}, {col}), 大小 {width_cells}x{height_cells}")
        logger.debug(f"行高度鎖定更新：頁面 {page}, 行 {row}-{row+height_cells-1} 鎖定為 height={height_cells}")
    
    def get_page_occupancy(self, page: int) -> float:
        """計算頁面佔用率
        
        Args:
            page: 頁碼
            
        Returns:
            佔用率（0.0 到 1.0）
        """
        if page not in self._grids:
            return 0.0
        
        total_cells = self.grid_width * self.grid_height
        occupied_cells = sum(
            sum(row) for row in self._grids[page]
        )
        
        return occupied_cells / total_cells
    
    def has_page(self, page: int) -> bool:
        """檢查頁面是否存在
        
        Args:
            page: 頁碼
            
        Returns:
            頁面是否存在
        """
        return page in self._grids

    def get_row_locked_height(self, page: int, row: int) -> int:
        """獲取指定行的已鎖定高度

        Args:
            page: 頁碼
            row: 行號

        Returns:
            已鎖定的高度，-1表示未鎖定
        """
        if (page in self._row_locked_heights and
            0 <= row < len(self._row_locked_heights[page])):
            return self._row_locked_heights[page][row]
        return -1

    def can_place_with_height_check(self, page: int, row: int, col: int,
                                   width_cells: int, height_cells: int) -> bool:
        """檢查是否可以放置（包含行高度鎖定檢查）

        Args:
            page: 頁碼
            row: 起始行
            col: 起始列
            width_cells: 寬度
            height_cells: 高度

        Returns:
            是否可以放置
        """
        # 基本空間檢查
        if not self.can_place_at(page, row, col, width_cells, height_cells):
            return False

        # 高度相容性檢查
        for r in range(row, row + height_cells):
            existing_height = self.get_row_locked_height(page, r)
            if existing_height != -1 and existing_height != height_cells:
                logger.debug(f"高度衝突：行 {r} 已鎖定為 height={existing_height}，無法放置 height={height_cells}")
                return False

        return True


class PlacementStrategy:
    """放置策略基類
    
    定義題目放置的策略介面。
    """
    
    def find_position(self, grid_manager: GridManager, page: int,
                     width_cells: int, height_cells: int) -> Optional[Tuple[int, int]]:
        """尋找合適的放置位置
        
        Args:
            grid_manager: 網格管理器
            page: 目標頁面
            width_cells: 題目寬度
            height_cells: 題目高度
            
        Returns:
            (row, col) 元組，如果找不到則返回 None
        """
        raise NotImplementedError


class TopLeftStrategy(PlacementStrategy):
    """左上優先放置策略
    
    從左上角開始，按行優先順序尋找第一個可用位置。
    """
    
    def find_position(self, grid_manager: GridManager, page: int,
                     width_cells: int, height_cells: int) -> Optional[Tuple[int, int]]:
        """從左上角開始尋找位置"""
        max_row = grid_manager.grid_height - height_cells + 1
        max_col = grid_manager.grid_width - width_cells + 1
        
        for row in range(max_row):
            for col in range(max_col):
                if grid_manager.can_place_with_height_check(page, row, col, width_cells, height_cells):
                    return (row, col)
        
        return None




class LayoutEngine:
    """佈局引擎
    
    提供智能化的題目佈局算法，支援多種佈局策略和自動分頁。
    
    特色功能：
    - 動態網格佈局
    - 自動分頁
    - 多種放置策略
    - 回合制支援
    - 完整的錯誤處理
    """
    
    def __init__(self, 
                grid_width: int = 4, 
                grid_height: int = 10,
                placement_strategy: Optional[PlacementStrategy] = None):
        """初始化佈局引擎
        
        Args:
            grid_width: 網格寬度（列數）
            grid_height: 網格高度（行數）
            placement_strategy: 放置策略，預設使用緊湊策略
        """
        self.grid_width = grid_width
        self.grid_height = grid_height
        
        # 設定放置策略
        self.placement_strategy = placement_strategy or TopLeftStrategy()
        
        # 網格管理器
        self.grid_manager = GridManager(grid_width, grid_height)
        
        # 題目尺寸映射: QuestionSize -> (width_cells, height_cells)
        self.size_map = {
            QuestionSize.SMALL: (1, 1),   # 小題：1x1
            QuestionSize.WIDE: (2, 1),    # 寬題：2x1
            QuestionSize.SQUARE: (1, 2),  # 方題：1x2
            QuestionSize.MEDIUM: (2, 2),  # 中題：2x2
            QuestionSize.LARGE: (3, 2),   # 大題：3x2
            QuestionSize.EXTRA: (4, 2),   # 超大題：4x2
        }
        
        logger.info(f"初始化佈局引擎: {grid_width}x{grid_height} 網格")
    
    def layout(self, 
              questions: List[Dict[str, Any]], 
              questions_per_round: int = 0) -> List[Dict[str, Any]]:
        """執行佈局算法
        
        根據題目大小和佈局策略，計算每個題目在PDF頁面網格中的位置。
        支援自動分頁和回合制佈局。
        
        Args:
            questions: 題目列表，每個題目需包含基本資訊和size屬性
            questions_per_round: 每回題數，0表示不按回分組
            
        Returns:
            包含佈局資訊的題目列表
            
        Raises:
            LayoutError: 佈局過程中的錯誤
        """
        logger.info(f"開始佈局 {len(questions)} 道題目")
        
        if not questions:
            logger.warning("題目列表為空")
            return []
        
        # 驗證輸入
        self._validate_questions(questions)
        
        # 初始化
        layout_results = []
        current_page = 1
        self.grid_manager.create_page(current_page)
        
        # 統計資訊
        page_stats = {}
        
        # 處理每個題目
        for i, question in enumerate(questions):
            try:
                # 計算回數和題號
                round_info = self._calculate_round_info(i, questions_per_round)
                
                # 檢查是否需要強制換頁
                if self._should_force_new_page(i, questions_per_round):
                    current_page = self._create_new_page(current_page, f"第 {round_info['round_num']} 回開始")
                
                # 獲取題目尺寸資訊
                size_info = self._get_size_info(question)
                
                # 嘗試放置題目
                placement_result = self._place_question(
                    current_page, size_info, question, round_info
                )
                
                if placement_result['placed']:
                    # 成功放置
                    layout_results.append(placement_result['question_data'])
                    logger.debug(f"題目 {i+1} 放置成功：頁面 {placement_result['question_data']['page']}")
                else:
                    # 當前頁無法放置，創建新頁面
                    current_page = self._create_new_page(current_page, "空間不足")
                    
                    # 在新頁面重新嘗試
                    placement_result = self._place_question(
                        current_page, size_info, question, round_info
                    )
                    
                    if placement_result['placed']:
                        layout_results.append(placement_result['question_data'])
                        logger.debug(f"題目 {i+1} 在新頁面放置成功：頁面 {current_page}")
                    else:
                        # 即使在新頁面也無法放置，這是錯誤情況
                        raise LayoutError(
                            f"題目 {i+1} 無法放置，尺寸過大: "
                            f"{size_info['width_cells']}x{size_info['height_cells']}"
                        )
            
            except Exception as e:
                logger.error(f"處理題目 {i+1} 時發生錯誤: {e}")
                raise LayoutError(f"佈局第 {i+1} 道題目失敗: {e}") from e
        
        # 收集統計資訊
        self._collect_layout_stats(layout_results, page_stats)

        # 根據佈局位置重新分配題號
        layout_results = self._reassign_question_numbers(layout_results, questions_per_round)

        logger.info(f"佈局完成：{len(layout_results)} 道題目，{current_page} 頁")

        return layout_results
    
    def _validate_questions(self, questions: List[Dict[str, Any]]) -> None:
        """驗證題目資料
        
        Args:
            questions: 題目列表
            
        Raises:
            LayoutError: 驗證失敗
        """
        for i, question in enumerate(questions):
            if not isinstance(question, dict):
                raise LayoutError(f"題目 {i+1} 不是字典格式")
            
            required_keys = ['question', 'answer', 'explanation']
            missing_keys = [key for key in required_keys if key not in question]
            if missing_keys:
                logger.warning(f"題目 {i+1} 缺少必要鍵值: {missing_keys}")
    
    def _calculate_round_info(self, question_index: int, questions_per_round: int) -> Dict[str, int]:
        """計算回合資訊
        
        Args:
            question_index: 題目索引
            questions_per_round: 每回題數
            
        Returns:
            包含回合資訊的字典
        """
        if questions_per_round > 0:
            round_num = (question_index // questions_per_round) + 1
            question_num_in_round = (question_index % questions_per_round) + 1
        else:
            round_num = 1
            question_num_in_round = question_index + 1
        
        return {
            'round_num': round_num,
            'question_num_in_round': question_num_in_round
        }
    
    def _should_force_new_page(self, question_index: int, questions_per_round: int) -> bool:
        """判斷是否應該強制換頁
        
        Args:
            question_index: 題目索引
            questions_per_round: 每回題數
            
        Returns:
            是否應該強制換頁
        """
        return (questions_per_round > 0 and 
                question_index > 0 and 
                question_index % questions_per_round == 0)
    
    def _create_new_page(self, current_page: int, reason: str) -> int:
        """創建新頁面
        
        Args:
            current_page: 目前頁碼
            reason: 換頁原因
            
        Returns:
            新頁碼
        """
        new_page = current_page + 1
        self.grid_manager.create_page(new_page)
        logger.debug(f"創建新頁面 {new_page}，原因: {reason}")
        return new_page
    
    def _get_size_info(self, question: Dict[str, Any]) -> Dict[str, int]:
        """獲取題目尺寸資訊
        
        Args:
            question: 題目字典
            
        Returns:
            尺寸資訊字典
        """
        size = question.get('size', QuestionSize.SMALL)
        
        # 處理不同類型的尺寸值
        if isinstance(size, int):
            try:
                size = QuestionSize(size)
            except ValueError:
                logger.warning(f"無效的題目尺寸: {size}，使用預設小尺寸")
                size = QuestionSize.SMALL
        
        # 獲取對應的格子尺寸
        width_cells, height_cells = self.size_map.get(size, (1, 1))
        
        return {
            'size': size,
            'width_cells': width_cells,
            'height_cells': height_cells
        }
    
    def _place_question(self, page: int, size_info: Dict[str, int], 
                       question: Dict[str, Any], round_info: Dict[str, int]) -> Dict[str, Any]:
        """嘗試放置題目
        
        Args:
            page: 目標頁面
            size_info: 尺寸資訊
            question: 題目資料
            round_info: 回合資訊
            
        Returns:
            放置結果字典
        """
        width_cells = size_info['width_cells']
        height_cells = size_info['height_cells']
        
        # 使用放置策略尋找位置
        position = self.placement_strategy.find_position(
            self.grid_manager, page, width_cells, height_cells
        )
        
        if position is None:
            return {'placed': False}
        
        row, col = position
        
        # 執行放置
        self.grid_manager.place_at(page, row, col, width_cells, height_cells)
        
        # 構建完整的題目資料
        question_data = {
            **question,
            'page': page,
            'row': row,
            'col': col,
            'width_cells': width_cells,
            'height_cells': height_cells,
            **round_info
        }
        
        return {
            'placed': True,
            'question_data': question_data
        }
    
    def _collect_layout_stats(self, layout_results: List[Dict[str, Any]], 
                            page_stats: Dict[int, Dict]) -> None:
        """收集佈局統計資訊
        
        Args:
            layout_results: 佈局結果
            page_stats: 頁面統計字典
        """
        if not layout_results:
            return
        
        max_page = max(result['page'] for result in layout_results)
        
        for page in range(1, max_page + 1):
            if self.grid_manager.has_page(page):
                occupancy = self.grid_manager.get_page_occupancy(page)
                page_questions = sum(1 for result in layout_results if result['page'] == page)
                
                page_stats[page] = {
                    'occupancy': occupancy,
                    'question_count': page_questions
                }
                
                logger.debug(f"頁面 {page}: {page_questions} 道題目, 佔用率 {occupancy:.1%}")
    
    def get_layout_stats(self) -> Dict[str, Any]:
        """獲取佈局統計資訊
        
        Returns:
            統計資訊字典
        """
        stats = {
            'grid_size': f"{self.grid_width}x{self.grid_height}",
            'strategy': self.placement_strategy.__class__.__name__,
            'size_mappings': dict(self.size_map)
        }
        
        return stats
    
    def _reassign_question_numbers(self, layout_results: List[Dict[str, Any]],
                                  questions_per_round: int = 0) -> List[Dict[str, Any]]:
        """根據佈局位置重新分配題號

        確保題號遵循左上到右下的自然順序：
        1. 頁面優先：第1頁 < 第2頁
        2. 行優先：同頁面內，上行 < 下行
        3. 列次要：同行內，左列 < 右列

        Args:
            layout_results: 佈局結果列表
            questions_per_round: 每回題數，0表示不分回

        Returns:
            重新分配題號後的佈局結果
        """
        if not layout_results:
            return layout_results

        logger.debug("開始根據佈局位置重新分配題號")

        # 按視覺位置排序：頁面 -> 行 -> 列
        sorted_results = sorted(layout_results, key=lambda x: (x['page'], x['row'], x['col']))

        # 重新分配題號
        for i, item in enumerate(sorted_results):
            if questions_per_round > 0:
                round_num = (i // questions_per_round) + 1
                question_num_in_round = (i % questions_per_round) + 1
            else:
                round_num = 1
                question_num_in_round = i + 1

            item['round_num'] = round_num
            item['question_num_in_round'] = question_num_in_round

        logger.info(f"題號重新分配完成：{len(sorted_results)} 道題目")
        return sorted_results

    def reset(self) -> None:
        """重置佈局引擎狀態

        清除所有頁面和統計資訊，準備進行新的佈局。
        """
        self.grid_manager = GridManager(self.grid_width, self.grid_height)
        logger.debug("佈局引擎狀態已重置")