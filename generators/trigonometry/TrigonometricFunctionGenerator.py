#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 三角函數值計算題目生成器

本模組提供三角函數值計算題目的生成功能，生成各種角度的
三角函數求值題目，包括 sin, cos, tan, cot, sec, csc 等。
使用新架構的統一 API，整合配置管理和日誌系統。

支援的功能：
- 完整的六種三角函數計算
- 特殊角度的精確值計算
- 智能的函數定義域檢查
- 詳細的單位圓解析過程
- LaTeX 格式化的專業數學表達式
- 可配置的角度範圍和函數選擇

Example:
    >>> from generators.trigonometry import TrigonometricFunctionGenerator
    >>> generator = TrigonometricFunctionGenerator()
    >>> question = generator.generate_question()
    >>> question['question']
    '求 $\\sin 60°$ 的值'
    >>> question['answer']
    '$\\frac{\\sqrt{3}}{2}$'
    
Note:
    此生成器使用 sympy 進行精確的符號運算，確保特殊角度
    的三角函數值以最簡根式形式表示。所有計算都經過定義域
    驗證，避免產生無意義的題目。
"""

import random
from typing import Dict, Any, List, Tuple, Optional, Callable, Union
from enum import Enum

import sympy as sp
from sympy import sin, cos, tan, cot, sec, csc, pi, sqrt, simplify, latex
from pydantic import BaseModel, Field, validator

from utils import global_config, get_logger
from ..base import QuestionGenerator, QuestionSize, register_generator

logger = get_logger(__name__)


class TrigFunction(str, Enum):
    """三角函數類型枚舉
    
    定義支援的六種基本三角函數類型，提供統一的函數識別和管理。
    
    Attributes:
        SIN: 正弦函數
        COS: 餘弦函數  
        TAN: 正切函數
        COT: 餘切函數
        SEC: 正割函數
        CSC: 餘割函數
    """
    SIN = "sin"
    COS = "cos" 
    TAN = "tan"
    COT = "cot"
    SEC = "sec"
    CSC = "csc"


class TrigonometricParams(BaseModel):
    """三角函數計算參數模型
    
    定義生成三角函數計算題目時的所有配置參數，
    使用 Pydantic 進行參數驗證和型別安全。
    
    Attributes:
        functions (List[TrigFunction]): 允許使用的三角函數列表
        angles (List[int]): 允許使用的角度列表（度）
        include_special_angles (bool): 是否包含特殊角度 (30°, 45°, 60° 等)
        include_quadrantal_angles (bool): 是否包含象限角 (0°, 90°, 180°, 270°)
        difficulty (str): 題目難度等級
        show_unit_circle (bool): 是否在解析中顯示單位圓說明
        show_definition (bool): 是否在解析中顯示函數定義
        
    Example:
        >>> params = TrigonometricParams(
        ...     functions=[TrigFunction.SIN, TrigFunction.COS],
        ...     angles=[30, 45, 60]
        ... )
        >>> params.functions
        [<TrigFunction.SIN: 'sin'>, <TrigFunction.COS: 'cos'>]
    """
    functions: List[TrigFunction] = Field(
        default=[TrigFunction.SIN, TrigFunction.COS, TrigFunction.TAN],
        description="允許使用的三角函數列表"
    )
    angles: List[int] = Field(
        default=[0, 30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 240, 270, 300, 315, 330],
        description="允許使用的角度列表（度）"
    )
    include_special_angles: bool = Field(
        default=True,
        description="是否包含特殊角度"
    )
    include_quadrantal_angles: bool = Field(
        default=True, 
        description="是否包含象限角"
    )
    difficulty: str = Field(
        default="MEDIUM",
        pattern="^(EASY|MEDIUM|HARD)$",
        description="題目難度等級"
    )
    show_unit_circle: bool = Field(
        default=True,
        description="是否在解析中顯示單位圓說明"
    )
    show_definition: bool = Field(
        default=False,
        description="是否在解析中顯示函數定義"
    )
    
    @validator('functions')
    def functions_not_empty(cls, v):
        """確保至少選擇一個三角函數"""
        if not v:
            raise ValueError('必須至少選擇一個三角函數')
        return v
    
    @validator('angles')
    def angles_valid_range(cls, v):
        """驗證角度範圍的有效性"""
        if not v:
            raise ValueError('必須至少提供一個角度')
        
        for angle in v:
            if not (0 <= angle <= 360):
                raise ValueError(f'角度必須在 0° 到 360° 範圍內，得到: {angle}°')
        return v


@register_generator
class TrigonometricFunctionGenerator(QuestionGenerator):
    """三角函數值計算題目生成器
    
    生成各種角度的三角函數求值題目，支援六種基本三角函數的計算。
    此生成器採用新架構的完整重建，充分利用 sympy 的符號運算能力，
    提供精確的數學計算和專業的教學解析。
    
    使用新架構的核心特性：
    - 完整的 Pydantic 參數驗證系統
    - 統一的日誌記錄和錯誤處理  
    - 智能的定義域檢查和邊界處理
    - 專業的 LaTeX 數學表達式格式化
    - 詳細的單位圓幾何解析
    - 符號運算確保的計算精確性
    
    Attributes:
        logger: 模組日誌記錄器
        config: 全域配置物件
        params: 經過驗證的生成參數
        function_map: 三角函數名稱到 sympy 函數的映射
        
    Example:
        >>> generator = TrigonometricFunctionGenerator({
        ...     'functions': ['sin', 'cos'],
        ...     'angles': [30, 45, 60],
        ...     'show_unit_circle': True
        ... })
        >>> question = generator.generate_question()
        >>> question['question']
        '求 $\\cos 45°$ 的值'
        >>> question['answer'] 
        '$\\frac{\\sqrt{2}}{2}$'
        
    Note:
        此生成器特別注重數學教學的準確性和完整性，所有特殊角度
        的三角函數值都以最簡根式形式呈現，並提供完整的幾何推導。
    """
    
    def __init__(self, options: Dict[str, Any] = None):
        """初始化三角函數計算題目生成器
        
        使用新架構的參數驗證和配置系統，建立三角函數計算的
        完整數學框架，包括函數映射、值查詢表和幾何解析系統。
        
        Args:
            options (Dict[str, Any], optional): 生成器配置選項，
                將透過 TrigonometricParams 進行驗證。支援的選項包括：
                - functions: 三角函數類型選擇
                - angles: 角度範圍設定
                - difficulty: 難度等級控制
                - show_unit_circle/definition: 解析詳細程度
                
        Raises:
            ValidationError: 如果配置參數不符合要求
            
        Example:
            >>> # 基本初始化
            >>> generator = TrigonometricFunctionGenerator()
            >>> 
            >>> # 進階配置初始化
            >>> advanced_options = {
            ...     'functions': ['sin', 'cos', 'tan'],
            ...     'angles': [0, 30, 45, 60, 90],
            ...     'show_unit_circle': True,
            ...     'difficulty': 'HARD'
            ... }
            >>> generator = TrigonometricFunctionGenerator(advanced_options)
        """
        super().__init__(options)
        
        # 使用新架構的參數驗證系統
        try:
            # 處理字符串格式的函數名稱
            if 'functions' in self.options and self.options['functions']:
                self.options['functions'] = [
                    TrigFunction(f) if isinstance(f, str) else f 
                    for f in self.options['functions']
                ]
            
            self.params = TrigonometricParams(**self.options)
            logger.debug(f"三角函數生成器初始化成功: 函數={len(self.params.functions)}個, 角度={len(self.params.angles)}個")
        except Exception as e:
            logger.error(f"參數驗證失敗: {str(e)}")
            # 使用預設參數
            self.params = TrigonometricParams()
            logger.info("使用預設參數初始化三角函數生成器")
        
        # 建立函數映射表
        self.function_map = {
            TrigFunction.SIN: sin,
            TrigFunction.COS: cos,
            TrigFunction.TAN: tan,
            TrigFunction.COT: cot,
            TrigFunction.SEC: sec,
            TrigFunction.CSC: csc
        }
        
        # 建立函數中文名稱映射
        self.function_names = {
            TrigFunction.SIN: "正弦",
            TrigFunction.COS: "餘弦", 
            TrigFunction.TAN: "正切",
            TrigFunction.COT: "餘切",
            TrigFunction.SEC: "正割",
            TrigFunction.CSC: "餘割"
        }
        
        # 建立函數定義映射
        self.function_definitions = {
            TrigFunction.SIN: "\\frac{y}{r}",
            TrigFunction.COS: "\\frac{x}{r}",
            TrigFunction.TAN: "\\frac{y}{x}",
            TrigFunction.COT: "\\frac{x}{y}",
            TrigFunction.SEC: "\\frac{r}{x}",
            TrigFunction.CSC: "\\frac{r}{y}"
        }
        
        # 預計算三角函數值表
        self.trig_values = self._build_trig_value_table()
        
        logger.info("三角函數生成器初始化完成")
    
    def generate_question(self) -> Dict[str, Any]:
        """生成一個三角函數計算題目
        
        使用新架構的智能生成算法，創建數學上有效且教育價值高的
        三角函數計算題目。所有題目都經過定義域驗證。
        
        Returns:
            Dict[str, Any]: 包含完整題目資訊的字典，包含以下鍵值：
                - question (str): LaTeX 格式的題目文字
                - answer (str): LaTeX 格式的標準答案
                - explanation (str): HTML 格式的詳細解析步驟
                - size (QuestionSize): 題目顯示大小
                - difficulty (str): 題目難度等級
                - category (str): 數學領域分類
                - subcategory (str): 具體題型分類
                
        Example:
            >>> generator = TrigonometricFunctionGenerator()
            >>> result = generator.generate_question()
            >>> result['question']
            '求 $\\sin 30°$ 的值'
            >>> result['answer']
            '$\\frac{1}{2}$'
            >>> 'explanation' in result
            True
            
        Note:
            生成過程包含定義域檢查，自動跳過無定義的情況
            （如 tan 90°, cot 0° 等）。
        """
        logger.info("開始生成三角函數計算題目")
        
        # 最大嘗試次數
        max_attempts = 50
        
        for attempt in range(max_attempts):
            try:
                # 隨機選擇函數和角度
                func_enum = random.choice(self.params.functions)
                angle = random.choice(self.params.angles)
                
                # 檢查定義域
                if not self._is_function_defined(func_enum, angle):
                    logger.debug(f"跳過無定義情況: {func_enum.value} {angle}°")
                    continue
                
                # 生成題目
                result = self._generate_single_question(func_enum, angle)
                if result:
                    logger.info(f"成功生成三角函數題目（第 {attempt + 1} 次嘗試）")
                    return result
                    
            except Exception as e:
                logger.warning(f"生成嘗試 {attempt + 1} 失敗: {str(e)}")
                continue
        
        # 如果無法生成有效題目，使用預設題目
        logger.warning("達到最大嘗試次數，使用預設題目")
        return self._get_default_question()
    
    def _generate_single_question(self, func_enum: TrigFunction, angle: int) -> Optional[Dict[str, Any]]:
        """生成單一題目的內部方法
        
        Args:
            func_enum: 三角函數類型
            angle: 角度值
            
        Returns:
            Optional[Dict[str, Any]]: 成功時返回題目字典，失敗時返回 None
        """
        func_sympy = self.function_map[func_enum]
        func_name = func_enum.value
        
        # 生成題目文字
        question = f"求 $\\{func_name} {angle}°$ 的值"
        
        # 計算答案
        angle_rad = angle * pi / 180
        try:
            value = simplify(func_sympy(angle_rad))
            answer = f"${latex(value)}$"
        except Exception as e:
            logger.warning(f"計算 {func_name} {angle}° 時出錯: {str(e)}")
            return None
        
        # 生成詳細解析
        explanation = self._generate_explanation(func_enum, angle, value)
        
        # 評估難度
        difficulty = self._assess_difficulty(func_enum, angle)
        
        return {
            "question": question,
            "answer": answer,
            "explanation": explanation,
            "size": self.get_question_size(),
            "difficulty": difficulty,
            "category": self.get_category(),
            "subcategory": self.get_subcategory()
        }
    
    def _is_function_defined(self, func_enum: TrigFunction, angle: int) -> bool:
        """檢查三角函數在給定角度是否有定義
        
        Args:
            func_enum: 三角函數類型
            angle: 角度值
            
        Returns:
            bool: 是否有定義
        """
        # 檢查各函數的定義域限制
        if func_enum == TrigFunction.TAN:
            # tan 在 90°, 270° 等處無定義
            return angle % 180 != 90
        elif func_enum == TrigFunction.COT:
            # cot 在 0°, 180°, 360° 等處無定義  
            return angle % 180 != 0
        elif func_enum == TrigFunction.SEC:
            # sec 在 90°, 270° 等處無定義
            return angle % 180 != 90
        elif func_enum == TrigFunction.CSC:
            # csc 在 0°, 180°, 360° 等處無定義
            return angle % 180 != 0
        
        # sin 和 cos 在所有角度都有定義
        return True
    
    def _build_trig_value_table(self) -> Dict[Tuple[TrigFunction, int], sp.Expr]:
        """建立三角函數值查詢表
        
        Returns:
            Dict: 函數和角度到計算值的映射表
        """
        logger.debug("開始建立三角函數值查詢表")
        table = {}
        
        for func_enum in self.params.functions:
            func_sympy = self.function_map[func_enum]
            for angle in self.params.angles:
                if self._is_function_defined(func_enum, angle):
                    try:
                        angle_rad = angle * pi / 180
                        value = simplify(func_sympy(angle_rad))
                        table[(func_enum, angle)] = value
                    except Exception as e:
                        logger.debug(f"計算 {func_enum.value} {angle}° 時出錯: {str(e)}")
        
        logger.debug(f"三角函數值查詢表建立完成: {len(table)} 個值")
        return table
    
    def _generate_explanation(self, func_enum: TrigFunction, angle: int, value: sp.Expr) -> str:
        """生成詳細的解析步驟
        
        Args:
            func_enum: 三角函數類型
            angle: 角度值
            value: 計算結果
            
        Returns:
            str: HTML 格式的解析步驟
        """
        steps = []
        func_name = func_enum.value
        
        # 添加題目重述
        steps.append(f"求 $\\{func_name} {angle}°$ 的值")
        
        # 添加單位圓說明（如果啟用）
        if self.params.show_unit_circle:
            x, y = self._get_unit_circle_coordinates(angle)
            steps.append(f"在單位圓上，{angle}° 對應的點坐標為 $({latex(x)}, {latex(y)})$")
        
        # 添加函數定義（如果啟用）
        if self.params.show_definition:
            definition = self.function_definitions[func_enum]
            chinese_name = self.function_names[func_enum]
            steps.append(f"{chinese_name}函數的定義：$\\{func_name} \\theta = {definition}$")
        
        # 添加計算過程
        if self._is_special_angle(angle):
            steps.append(f"{angle}° 是特殊角，其{self.function_names[func_enum]}值為已知值")
        
        # 添加最終答案
        steps.append(f"因此，$\\{func_name} {angle}° = {latex(value)}$")
        
        return "<br>".join(steps)
    
    def _get_unit_circle_coordinates(self, angle: int) -> Tuple[sp.Expr, sp.Expr]:
        """獲取單位圓上指定角度的坐標
        
        Args:
            angle: 角度值
            
        Returns:
            Tuple[sp.Expr, sp.Expr]: (x, y) 坐標
        """
        angle_rad = angle * pi / 180
        x = simplify(cos(angle_rad))
        y = simplify(sin(angle_rad))
        return (x, y)
    
    def _is_special_angle(self, angle: int) -> bool:
        """檢查是否為特殊角度
        
        Args:
            angle: 角度值
            
        Returns:
            bool: 是否為特殊角度
        """
        special_angles = [0, 30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 240, 270, 300, 315, 330]
        return angle in special_angles
    
    def _assess_difficulty(self, func_enum: TrigFunction, angle: int) -> str:
        """評估題目難度
        
        Args:
            func_enum: 三角函數類型  
            angle: 角度值
            
        Returns:
            str: 難度等級
        """
        # 基於函數類型評估基礎難度
        if func_enum in [TrigFunction.SIN, TrigFunction.COS]:
            base_difficulty = "EASY"
        elif func_enum == TrigFunction.TAN:
            base_difficulty = "MEDIUM"
        else:  # COT, SEC, CSC
            base_difficulty = "HARD"
        
        # 基於角度調整難度
        if angle in [0, 90, 180, 270]:
            # 象限角較簡單
            pass
        elif angle in [30, 45, 60]:
            # 特殊角中等
            if base_difficulty == "EASY":
                base_difficulty = "MEDIUM"
        else:
            # 其他角度較難
            if base_difficulty != "HARD":
                base_difficulty = "HARD"
        
        logger.debug(f"評估難度: {func_enum.value} {angle}° -> {base_difficulty}")
        return base_difficulty
    
    def _get_default_question(self) -> Dict[str, Any]:
        """獲取預設題目
        
        Returns:
            Dict[str, Any]: 預設題目字典
        """
        logger.info("使用預設三角函數題目")
        
        return {
            "question": "求 $\\sin 30°$ 的值",
            "answer": "$\\frac{1}{2}$",
            "explanation": (
                "求 $\\sin 30°$ 的值<br>"
                "30° 是特殊角，其正弦值為已知值<br>"  
                "因此，$\\sin 30° = \\frac{1}{2}$"
            ),
            "size": self.get_question_size(),
            "difficulty": "EASY",
            "category": self.get_category(),
            "subcategory": self.get_subcategory()
        }
    
    def get_question_size(self) -> int:
        """獲取題目顯示大小
        
        三角函數計算題目通常需要標準顯示空間。
        
        Returns:
            int: QuestionSize.MEDIUM 的數值
        """
        return QuestionSize.MEDIUM.value
    
    def get_category(self) -> str:
        """獲取題目主類別
        
        Returns:
            str: 主要數學領域分類
        """
        return "三角函數"
    
    def get_subcategory(self) -> str:
        """獲取題目子類別
        
        Returns:
            str: 具體的三角函數題型分類
        """
        return "三角函數值練習_角度"