#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 基礎生成器類別

本模組提供題目生成系統的核心基礎類別和枚舉定義，包括抽象基礎類別 
QuestionGenerator 和題目大小枚舉 QuestionSize。所有具體的題目生成器
都應該繼承 QuestionGenerator 並實現其抽象方法。
"""

import random
from abc import ABC, abstractmethod
from enum import IntEnum
from typing import Dict, List, Any, Tuple, Optional, Union, Type, ClassVar

from utils import global_config, get_logger

logger = get_logger(__name__)



class QuestionSize(IntEnum):
    """題目大小枚舉
    
    定義六種不同的題目顯示大小空間，用於控制題目在 UI 中的
    布局和空間佔用。每個值對應不同的寬高比例配置。
    
    Attributes:
        SMALL: 一單位大小（1x1）
        WIDE: 左右兩單位，上下一單位（2x1）
        SQUARE: 左右一單位，上下兩單位（1x2）
        MEDIUM: 左右兩單位，上下兩單位（2x2）
        LARGE: 左右三單位，上下兩單位（3x2）
        EXTRA: 左右四單位，上下兩單位（4x2）
        
    Example:
        >>> size = QuestionSize.MEDIUM
        >>> size.value
        4
        >>> size.name
        'MEDIUM'
        
    Note:
        這些大小值會影響題目在 UI 顯示時的版面配置，
        較大的題目需要更多空間來正確顯示。
    """
    SMALL = 1   # 一單位大小（1x1）
    WIDE = 2    # 左右兩單位，上下一單位（2x1）
    SQUARE = 3  # 左右一單位，上下兩單位（1x2）
    MEDIUM = 4  # 左右兩單位，上下兩單位（2x2）
    LARGE = 5   # 左右三單位，上下兩單位（3x2）
    EXTRA = 6   # 左右四單位，上下兩單位（4x2）




class QuestionGenerator(ABC):
    """題目生成器抽象基礎類別
    
    所有具體的題目生成器都應該繼承此類別並實現其抽象方法。
    此類別提供了題目生成的統一接口，包括題目生成、批量生成、
    參數設定和格式化等功能。使用新架構的統一 API，
    整合配置管理和日誌系統。
    
    Attributes:
        auto_register (ClassVar[bool]): 類別屬性，控制是否自動註冊生成器
        options (Dict[str, Any]): 生成器選項配置
        logger: 模組日誌記錄器
        config: 全域配置物件
        
    Abstract Methods:
        generate_question: 生成一個題目
        get_question_size: 獲取題目大小
        get_category: 獲取題目類別
        get_subcategory: 獲取題目子類別
        
    Example:
        >>> class MyGenerator(QuestionGenerator):
        ...     def generate_question(self):
        ...         return {
        ...             'question': '1 + 1 = ?',
        ...             'answer': '2',
        ...             'explanation': '基本加法',
        ...             'size': QuestionSize.SMALL
        ...         }
        ...     def get_question_size(self):
        ...         return QuestionSize.SMALL.value
        ...     def get_category(self):
        ...         return 'arithmetic'
        ...     def get_subcategory(self):
        ...         return 'addition'
        >>> 
        >>> generator = MyGenerator()
        >>> result = generator.generate_question()
        >>> result['question']
        '1 + 1 = ?'
        
    Note:
        所有繼承此類別的生成器會自動註冊到中央註冊系統中，
        除非明確設定 auto_register = False。
    """
    
    # 類別屬性，用於自動註冊
    auto_register: ClassVar[bool] = True
    
    def __init__(self, options: Dict[str, Any] = None):
        """初始化題目生成器
        
        設定生成器的初始配置選項和日誌系統，
        使用新架構的配置管理和日誌記錄。
        
        Args:
            options (Dict[str, Any], optional): 生成器選項配置字典，
                可包含特定範圍、運算符限制、難度設定等。
                預設為 None，會設定為空字典。
                
        Example:
            >>> # 基本初始化
            >>> generator = MyGenerator()
            >>> generator.options
            {}
            
            >>> # 帶選項初始化
            >>> options = {
            ...     'min_value': 1,
            ...     'max_value': 100,
            ...     'operators': ['+', '-']
            ... }
            >>> generator = MyGenerator(options)
            >>> generator.options['min_value']
            1
            
        Note:
            options 參數將用於後續的題目生成過程中，
            可透過 set_options() 方法動態更新。
        """
        self.options = options or {}
        logger.debug(f"初始化題目生成器: {self.__class__.__name__}, 選項={self.options}")
        
    @abstractmethod
    def generate_question(self) -> Dict[str, Any]:
        """生成一個完整的題目
        
        此為抽象方法，所有子類別必須實現此方法以生成
        包含完整題目資訊的字典結構。
        
        Returns:
            Dict[str, Any]: 包含題目資訊的字典，必須包含以下鍵值：
                - question (str): 題目文字內容
                - answer (str): 標準答案
                - explanation (str): 詳細解析說明
                - size (QuestionSize): 題目顯示大小
                
        Raises:
            NotImplementedError: 如果子類別未實現此方法
            
        Example:
            >>> class SimpleGenerator(QuestionGenerator):
            ...     def generate_question(self):
            ...         return {
            ...             'question': '計算 2 + 3',
            ...             'answer': '5',
            ...             'explanation': '2 + 3 = 5，基本加法運算',
            ...             'size': QuestionSize.SMALL
            ...         }
            >>> generator = SimpleGenerator()
            >>> result = generator.generate_question()
            >>> result['answer']
            '5'
            
        Note:
            返回的字典可以包含其他額外的鍵值對，
            但上述四個必要鍵值必須存在。
        """
        pass
    
    @abstractmethod
    def get_question_size(self) -> int:
        """獲取題目顯示大小
        
        返回此生成器產生的題目所需的顯示空間大小，
        用於 UI 布局計算。
        
        Returns:
            int: 題目大小數值，應為 QuestionSize 枚舉的 value
            
        Raises:
            NotImplementedError: 如果子類別未實現此方法
            
        Example:
            >>> class MediumGenerator(QuestionGenerator):
            ...     def get_question_size(self):
            ...         return QuestionSize.MEDIUM.value
            >>> generator = MediumGenerator()
            >>> size = generator.get_question_size()
            >>> size
            4
            
        Note:
            返回值應該對應 QuestionSize 枚舉中的其中一個值，
            以確保 UI 能正確處理布局。
        """
        pass
    
    @abstractmethod
    def get_category(self) -> str:
        """獲取題目主類別
        
        返回此生成器所屬的主要數學領域類別，
        用於題目分類和組織管理。
        
        Returns:
            str: 題目類別名稱，如 'algebra', 'geometry', 'arithmetic' 等
            
        Raises:
            NotImplementedError: 如果子類別未實現此方法
            
        Example:
            >>> class AlgebraGenerator(QuestionGenerator):
            ...     def get_category(self):
            ...         return 'algebra'
            >>> generator = AlgebraGenerator()
            >>> category = generator.get_category()
            >>> category
            'algebra'
            
        Note:
            類別名稱應該使用小寫英文，保持一致性，
            常見的類別包括：algebra, geometry, arithmetic, trigonometry 等。
        """
        pass
    
    @abstractmethod
    def get_subcategory(self) -> str:
        """獲取題目子類別
        
        返回此生成器所屬的具體子類別，
        提供比主類別更詳細的分類資訊。
        
        Returns:
            str: 題目子類別名稱，如 'linear_equations', 'quadratic', 'addition' 等
            
        Raises:
            NotImplementedError: 如果子類別未實現此方法
            
        Example:
            >>> class LinearEquationGenerator(QuestionGenerator):
            ...     def get_category(self):
            ...         return 'algebra'
            ...     def get_subcategory(self):
            ...         return 'linear_equations'
            >>> generator = LinearEquationGenerator()
            >>> subcategory = generator.get_subcategory()
            >>> subcategory
            'linear_equations'
            
        Note:
            子類別名稱應該使用小寫英文和底線分隔，
            與主類別形成清晰的層次結構。
        """
        pass
    
    def generate_batch(self, count: int) -> List[Dict[str, Any]]:
        """生成一批題目
        
        批量生成指定數量的題目，每個題目都是獨立生成，
        適合用於產生題目集合或測驗卷。
        
        Args:
            count (int): 要生成的題目數量，必須大於 0
            
        Returns:
            List[Dict[str, Any]]: 題目字典的列表，每個字典
                包含完整的題目資訊
                
        Raises:
            ValueError: 如果 count 小於或等於 0
            
        Example:
            >>> generator = MyGenerator()
            >>> questions = generator.generate_batch(3)
            >>> len(questions)
            3
            >>> all('question' in q for q in questions)
            True
            
        Note:
            此方法使用 generate_question() 方法逐一生成題目，
            因此生成時間與題目數量成正比。
        """
        if count <= 0:
            raise ValueError(f"題目數量必須大於 0，得到: {count}")
        
        logger.debug(f"批量生成題目: 數量={count}")
        batch = [self.generate_question() for _ in range(count)]
        logger.debug(f"批量生成完成: 已產生 {len(batch)} 個題目")
        return batch
    
    def set_options(self, options: Dict[str, Any]) -> None:
        """設置生成器選項
        
        更新生成器的配置選項，會完全替換現有的選項設定。
        新的選項將影響後續所有題目的生成過程。
        
        Args:
            options (Dict[str, Any]): 新的選項配置字典，
                可包含任何生成器特定的配置參數
                
        Example:
            >>> generator = MyGenerator()
            >>> generator.options
            {}
            >>> new_options = {'difficulty': 'hard', 'range': (1, 100)}
            >>> generator.set_options(new_options)
            >>> generator.options['difficulty']
            'hard'
            
        Note:
            此方法會完全替換現有選項，如需合併選項，
            請先獲取現有選項再進行合併後設置。
        """
        logger.debug(f"更新生成器選項: 舊選項={self.options}, 新選項={options}")
        self.options = options
        logger.debug(f"選項更新完成: {self.options}")
        
    def get_param_range(self, param_name: str, default_range: Tuple[int, int]) -> Tuple[int, int]:
        """獲取參數範圍設定
        
        從生成器選項中查找指定參數的範圍設定，
        如果找不到則使用預設範圍。
        
        Args:
            param_name (str): 要查找的參數名稱
            default_range (Tuple[int, int]): 預設範圍的最小值和最大值
            
        Returns:
            Tuple[int, int]: 參數範圍 (min_value, max_value)
            
        Example:
            >>> generator = MyGenerator({'num_range': (1, 50)})
            >>> range_val = generator.get_param_range('num_range', (1, 10))
            >>> range_val
            (1, 50)
            >>> default_range = generator.get_param_range('missing_param', (5, 15))
            >>> default_range
            (5, 15)
            
        Note:
            這是一個工具方法，幫助子類別獲取配置參數，
            提供統一的參數管理方式。
        """
        # 檢查 options 中是否有指定範圍
        if param_name in self.options:
            logger.debug(f"使用配置範圍: {param_name}={self.options[param_name]}")
            return self.options[param_name]
        
        # 使用預設範圍
        logger.debug(f"使用預設範圍: {param_name}={default_range}")
        return default_range
    
    def format_question(self, template: str, **kwargs) -> str:
        """格式化題目文字內容
        
        使用給定的模板和參數生成最終的題目文字，
        支援 Python 標準的字串格式化語法。
        
        Args:
            template (str): 題目模板字串，包含格式化占位符
            **kwargs: 模板參數，用於替換模板中的占位符
            
        Returns:
            str: 格式化完成的題目文字
            
        Raises:
            KeyError: 如果模板中的占位符在 kwargs 中找不到
            
        Example:
            >>> generator = MyGenerator()
            >>> template = '計算 {a} + {b} = ?'
            >>> result = generator.format_question(template, a=3, b=5)
            >>> result
            '計算 3 + 5 = ?'
            
        Note:
            這是一個工具方法，幫助統一進行題目文字格式化，
            確保所有生成器使用相同的格式化標準。
        """
        try:
            formatted = template.format(**kwargs)
            logger.debug(f"題目文字格式化成功: {template[:50]}... -> {formatted[:50]}...")
            return formatted
        except KeyError as e:
            logger.error(f"題目格式化失敗，缺少參數: {e}")
            raise
    
    def format_latex(self, expression: str) -> str:
        """格式化 LaTeX 數學表達式
        
        將數學表達式包裝在 LaTeX 數學模式中，
        使其能在渲染時正確顯示數學符號。
        
        Args:
            expression (str): 要格式化的 LaTeX 數學表達式
            
        Returns:
            str: 包裝在 $ $ 中的 LaTeX 表達式
            
        Example:
            >>> generator = MyGenerator()
            >>> latex_expr = generator.format_latex('x^2 + y^2 = r^2')
            >>> latex_expr
            '$x^2 + y^2 = r^2$'
            >>> fraction = generator.format_latex(r'\frac{a}{b}')
            >>> fraction
            '$\\frac{a}{b}$'
            
        Note:
            這是一個工具方法，用於統一處理 LaTeX 格式，
            確保所有數學表達式使用正確的標記。
        """
        if not expression:
            logger.warning("空的 LaTeX 表達式")
            return "$$"
        
        formatted = f"${expression}$"
        logger.debug(f"LaTeX 表達式格式化: {expression} -> {formatted}")
        return formatted
    
    def random_int(self, min_val: int, max_val: int, exclude: List[int] = None) -> int:
        """生成排除指定值的隨機整數
        
        在給定範圍內生成隨機整數，可以排除不希望出現的值。
        適合用於生成題目中的隨機參數。
        
        Args:
            min_val (int): 隨機數的最小值（包含）
            max_val (int): 隨機數的最大值（包含）
            exclude (List[int], optional): 要排除的整數列表，預設為 None
            
        Returns:
            int: 符合條件的隨機整數
            
        Raises:
            ValueError: 如果排除的值太多，導致無法生成隨機數
            
        Example:
            >>> generator = MyGenerator()
            >>> # 生成 1-10 之間的隨機數
            >>> num = generator.random_int(1, 10)
            >>> 1 <= num <= 10
            True
            >>> # 生成不為 5 的 1-10 隨機數
            >>> num = generator.random_int(1, 10, exclude=[5])
            >>> num != 5
            True
            
        Note:
            如果 min_val > max_val，會自動交換兩值。
            排除列表不應該包含範圍內的所有可能值。
        """
        if exclude is None:
            exclude = []
            
        if min_val > max_val:
            min_val, max_val = max_val, min_val
            logger.debug(f"交換 min_val 和 max_val: 新範圍=({min_val}, {max_val})")
            
        available_count = max_val - min_val + 1 - len([x for x in exclude if min_val <= x <= max_val])
        if available_count <= 0:
            raise ValueError(f"排除的值太多，無法生成隨機數: 範圍({min_val}, {max_val}), 排除{exclude}")
            
        while True:
            num = random.randint(min_val, max_val)
            if num not in exclude:
                logger.debug(f"生成隨機整數: {num} (範圍: {min_val}-{max_val}, 排除: {exclude})")
                return num
                
    def random_float(self, min_val: float, max_val: float, precision: int = 2, exclude: List[float] = None) -> float:
        """生成排除指定值的隨機浮點數
        
        在給定範圍內生成指定精度的隨機浮點數，
        可以排除不希望出現的值。
        
        Args:
            min_val (float): 隨機數的最小值（包含）
            max_val (float): 隨機數的最大值（包含）
            precision (int): 小數點後的位數，預設為 2
            exclude (List[float], optional): 要排除的浮點數列表，預設為 None
            
        Returns:
            float: 符合條件的隨機浮點數
            
        Example:
            >>> generator = MyGenerator()
            >>> # 生成 0.5-2.5 之間的隨機浮點數（保留 2 位小數）
            >>> num = generator.random_float(0.5, 2.5)
            >>> 0.5 <= num <= 2.5
            True
            >>> # 生成不為 1.0 的隨機數
            >>> num = generator.random_float(0.0, 2.0, exclude=[1.0])
            >>> num != 1.0
            True
            
        Note:
            如果 min_val > max_val，會自動交換兩值。
            precision 精度參數決定返回值的小數位數。
        """
        if exclude is None:
            exclude = []
            
        if min_val > max_val:
            min_val, max_val = max_val, min_val
            logger.debug(f"交換 min_val 和 max_val: 新範圍=({min_val}, {max_val})")
            
        # 防止無限迴圈，設定最大嘗試次數
        max_attempts = 10000
        attempts = 0
        
        while attempts < max_attempts:
            num = round(random.uniform(min_val, max_val), precision)
            if num not in exclude:
                logger.debug(f"生成隨機浮點數: {num} (範圍: {min_val}-{max_val}, 精度: {precision})")
                return num
            attempts += 1
            
        raise ValueError(f"無法在 {max_attempts} 次嘗試內生成不在排除列表中的隨機浮點數")

    @classmethod
    def get_config_schema(cls) -> Dict[str, Any]:
        """取得生成器配置描述

        返回此生成器支援的配置選項描述，預設為無配置。
        子類別可覆寫此方法以描述其支援的配置選項。

        Returns:
            Dict[str, Any]: 配置描述字典，預設為空字典

        Example:
            >>> class MyGenerator(QuestionGenerator):
            ...     @classmethod
            ...     def get_config_schema(cls):
            ...         return {
            ...             "difficulty": {
            ...                 "type": "select",
            ...                 "options": ["easy", "hard"],
            ...                 "default": "easy"
            ...             }
            ...         }
        """
        return {}

    @classmethod
    def has_config(cls) -> bool:
        """檢查生成器是否需要配置

        Returns:
            bool: 如果生成器支援配置則返回 True，否則返回 False

        Example:
            >>> QuestionGenerator.has_config()
            False
            >>> # 假設 MyGenerator 有配置
            >>> MyGenerator.has_config()
            True
        """
        return bool(cls.get_config_schema())

    @classmethod
    def register(cls) -> None:
        """註冊生成器到中央系統
        
        將此生成器類別註冊到中央註冊系統中，
        使其能夠被主系統發現和使用。
        
        Raises:
            Exception: 如果註冊過程中發生錯誤
            
        Example:
            >>> class MyGenerator(QuestionGenerator):
            ...     def get_category(self):
            ...         return 'test'
            ...     def get_subcategory(self):
            ...         return 'example'
            >>> MyGenerator.register()
            # 生成器被註冊到 'test/example' 分類下
            
        Note:
            此方法通常由 @register_generator 裝飾器自動調用，
            不需要手動呼叫。
        """
        from utils.core.registry import registry
        
        logger.info(f"正在註冊生成器: {cls.__name__}")
        
        try:
            # 創建一個臨時實例以獲取類別和子類別
            temp_instance = cls()
            category = temp_instance.get_category()
            subcategory = temp_instance.get_subcategory()
            
            logger.debug(f"生成器 {cls.__name__} 的類別: '{category}', 子類別: '{subcategory}'")
            
            # 註冊到中央系統
            registry.register(cls, category, subcategory)
            logger.info(f"生成器 {cls.__name__} 註冊成功: {category}/{subcategory}")
            
        except Exception as e:
            logger.error(f"註冊生成器 {cls.__name__} 失敗: {str(e)}")
            raise


# 裝飾器：用於註冊生成器
def register_generator(cls):
    """註冊生成器裝飾器
    
    用於自動註冊繼承 QuestionGenerator 的生成器類別。
    只有在 auto_register 為 True 時才會實際註冊。
    
    Args:
        cls: 要註冊的生成器類別
        
    Returns:
        type: 原始的生成器類別（不修改）
        
    Example:
        >>> @register_generator
        ... class AdditionGenerator(QuestionGenerator):
        ...     auto_register = True
        ...     def get_category(self):
        ...         return 'arithmetic'
        ...     def get_subcategory(self):
        ...         return 'addition'
        # AdditionGenerator 會自動註冊到系統中
        
        >>> @register_generator  
        ... class DisabledGenerator(QuestionGenerator):
        ...     auto_register = False  # 禁用自動註冊
        # DisabledGenerator 不會被註冊
        
    Note:
        此裝飾器是新架構的核心組件，確保所有生成器
        能夠被中央註冊系統正確管理。
    """
    logger.debug(f"裝飾器被調用: {cls.__name__}")
    
    try:
        # 如果設置了自動註冊，則註冊生成器
        if getattr(cls, 'auto_register', True):
            logger.debug(f"自動註冊已啟用，正在註冊 {cls.__name__}")
            cls.register()
        else:
            logger.debug(f"自動註冊已禁用，不註冊 {cls.__name__}")
    except Exception as e:
        logger.error(f"裝飾器處理 {cls.__name__} 時出錯: {str(e)}")
        # 不拋出異常，以免影響類別定義
    
    return cls
