#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 反三角函數值計算題目生成器

本模組提供反三角函數值計算題目的生成功能，生成 arcsin, arccos, arctan 
等反三角函數的計算題目。使用新架構的統一 API，整合配置管理和日誌系統，
確保數學計算的精確性和教學價值。

支援的功能：
- 三種主要反三角函數 (arcsin, arccos, arctan)
- 特殊值的精確計算
- 智能的定義域和值域檢查
- 詳細的計算步驟解析
- LaTeX 格式化的專業數學表達式
- 可配置的函數範圍和特殊角度

Example:
    >>> from generators.trigonometry import InverseTrigonometricFunctionGenerator
    >>> generator = InverseTrigonometricFunctionGenerator()
    >>> question = generator.generate_question()
    >>> question['question']
    '求 $\\arcsin\\left(\\frac{1}{2}\\right)$ 的值'
    >>> question['answer']
    '$30°$'
    
Note:
    此生成器使用 sympy 進行精確的反三角函數計算，確保特殊值
    以標準角度形式呈現。所有計算都經過定義域驗證，避免產生
    數學上無意義的題目。
"""

import random
from typing import Dict, Any, List, Tuple, Optional
from enum import Enum
import math

import sympy as sp
from sympy import asin, acos, atan, sin, cos, tan, pi, sqrt, simplify, latex, deg, rad
from pydantic import BaseModel, Field, validator

from utils import global_config, get_logger
from ..base import QuestionGenerator, QuestionSize, register_generator

logger = get_logger(__name__)


class InverseTrigFunction(str, Enum):
    """反三角函數類型枚舉
    
    定義支援的三種主要反三角函數類型，提供統一的函數識別和管理。
    
    Attributes:
        ARCSIN: 反正弦函數 (arcsin)
        ARCCOS: 反餘弦函數 (arccos)
        ARCTAN: 反正切函數 (arctan)
    """
    ARCSIN = "arcsin"
    ARCCOS = "arccos"
    ARCTAN = "arctan"


class InverseTrigParams(BaseModel):
    """反三角函數計算參數模型
    
    定義生成反三角函數計算題目時的所有配置參數，
    使用 Pydantic 進行參數驗證和型別安全。
    
    Attributes:
        functions (List[InverseTrigFunction]): 允許使用的反三角函數列表
        use_degrees (bool): 是否使用度數制，預設 True（弧度制為 False）
        include_negative_values (bool): 是否包含負值輸入
        include_special_values (bool): 是否僅使用特殊值（如 1/2, √2/2 等）
        show_unit_circle (bool): 是否在解析中顯示單位圓說明
        difficulty (str): 題目難度等級
        
    Example:
        >>> params = InverseTrigParams(
        ...     functions=[InverseTrigFunction.ARCSIN],
        ...     use_degrees=True,
        ...     include_negative_values=False
        ... )
        >>> params.use_degrees
        True
    """
    functions: List[InverseTrigFunction] = Field(
        default=[InverseTrigFunction.ARCSIN, InverseTrigFunction.ARCCOS, InverseTrigFunction.ARCTAN],
        description="允許使用的反三角函數列表"
    )
    use_degrees: bool = Field(
        default=True,
        description="是否使用度數制（False 為弧度制）"
    )
    include_negative_values: bool = Field(
        default=True,
        description="是否包含負值輸入"
    )
    include_special_values: bool = Field(
        default=True,
        description="是否僅使用特殊值"
    )
    show_unit_circle: bool = Field(
        default=False,
        description="是否在解析中顯示單位圓說明"
    )
    difficulty: str = Field(
        default="MEDIUM",
        pattern="^(EASY|MEDIUM|HARD)$",
        description="題目難度等級"
    )
    
    @validator('functions')
    def functions_not_empty(cls, v):
        """確保至少選擇一個反三角函數"""
        if not v:
            raise ValueError('必須至少選擇一個反三角函數')
        return v


@register_generator
class InverseTrigonometricFunctionGenerator(QuestionGenerator):
    """反三角函數值計算題目生成器
    
    生成各種反三角函數值計算題目，支援 arcsin, arccos, arctan 等函數的計算。
    此生成器採用新架構的完整重建，充分利用 sympy 的精確計算能力，
    提供準確的反三角函數值和專業的教學解析。
    
    使用新架構的核心特性：
    - 完整的 Pydantic 參數驗證系統
    - 統一的日誌記錄和錯誤處理
    - 智能的定義域和值域檢查
    - 專業的 LaTeX 數學表達式格式化
    - 特殊值的精確識別和計算
    - 符號運算確保的計算精確性
    
    Attributes:
        logger: 模組日誌記錄器
        config: 全域配置物件
        params: 經過驗證的生成參數
        function_map: 反三角函數名稱到 sympy 函數的映射
        special_values: 特殊三角函數值的查詢表
        
    Example:
        >>> generator = InverseTrigonometricFunctionGenerator({
        ...     'functions': ['arcsin', 'arccos'],
        ...     'use_degrees': True,
        ...     'include_negative_values': False
        ... })
        >>> question = generator.generate_question()
        >>> question['question']
        '求 $\\arccos\\left(\\frac{\\sqrt{2}}{2}\\right)$ 的值'
        >>> question['answer']
        '$45°$'
        
    Note:
        此生成器特別注重反三角函數的定義域限制，確保所有輸入值
        都在合理範圍內，避免產生無意義的題目。
    """
    
    def __init__(self, options: Dict[str, Any] = None):
        """初始化反三角函數計算題目生成器
        
        使用新架構的參數驗證和配置系統，建立反三角函數計算的
        完整數學框架，包括函數映射、特殊值表和定義域檢查。
        
        Args:
            options (Dict[str, Any], optional): 生成器配置選項，
                將透過 InverseTrigParams 進行驗證。支援的選項包括：
                - functions: 反三角函數類型選擇
                - use_degrees: 角度制/弧度制選擇
                - include_negative_values: 是否包含負值
                - show_unit_circle: 解析詳細程度控制
                
        Raises:
            ValidationError: 如果配置參數不符合要求
        """
        super().__init__(options)
        
        # 使用新架構的參數驗證系統
        try:
            # 處理字符串格式的函數名稱
            if 'functions' in self.options and self.options['functions']:
                self.options['functions'] = [
                    InverseTrigFunction(f) if isinstance(f, str) else f 
                    for f in self.options['functions']
                ]
            
            self.params = InverseTrigParams(**self.options)
            logger.debug(f"反三角函數生成器初始化成功: 函數={len(self.params.functions)}個")
        except Exception as e:
            logger.error(f"參數驗證失敗: {str(e)}")
            # 使用預設參數
            self.params = InverseTrigParams()
            logger.info("使用預設參數初始化反三角函數生成器")
        
        # 建立函數映射表
        self.function_map = {
            InverseTrigFunction.ARCSIN: asin,
            InverseTrigFunction.ARCCOS: acos,
            InverseTrigFunction.ARCTAN: atan
        }
        
        # 建立 LaTeX 格式映射
        self.latex_map = {
            InverseTrigFunction.ARCSIN: "\\arcsin",
            InverseTrigFunction.ARCCOS: "\\arccos",
            InverseTrigFunction.ARCTAN: "\\arctan"
        }
        
        # 建立中文名稱映射
        self.chinese_names = {
            InverseTrigFunction.ARCSIN: "反正弦",
            InverseTrigFunction.ARCCOS: "反餘弦",
            InverseTrigFunction.ARCTAN: "反正切"
        }
        
        # 建立特殊值表
        self.special_values = self._build_special_values_table()
        
        logger.info("反三角函數生成器初始化完成")
    
    def generate_question(self) -> Dict[str, Any]:
        """生成一個反三角函數計算題目
        
        使用新架構的智能生成算法，創建數學上有效且教育價值高的
        反三角函數計算題目。所有題目都經過定義域驗證。
        
        Returns:
            Dict[str, Any]: 包含完整題目資訊的字典
            
        Note:
            生成過程包含定義域檢查，確保所有輸入值都在函數的定義域內。
        """
        logger.info("開始生成反三角函數計算題目")
        
        # 最大嘗試次數
        max_attempts = 50
        
        for attempt in range(max_attempts):
            try:
                # 隨機選擇函數
                func_enum = random.choice(self.params.functions)
                
                # 選擇輸入值
                input_value = self._choose_input_value(func_enum)
                if input_value is None:
                    continue
                
                # 生成題目
                result = self._generate_single_question(func_enum, input_value)
                if result:
                    logger.info(f"成功生成反三角函數題目（第 {attempt + 1} 次嘗試）")
                    return result
                    
            except Exception as e:
                logger.warning(f"生成嘗試 {attempt + 1} 失敗: {str(e)}")
                continue
        
        # 如果無法生成有效題目，使用預設題目
        logger.warning("達到最大嘗試次數，使用預設題目")
        return self._get_default_question()
    
    def _build_special_values_table(self) -> Dict[Tuple[InverseTrigFunction, float], float]:
        """建立特殊值查詢表
        
        Returns:
            Dict: 函數和輸入值到輸出角度的映射表
        """
        logger.debug("開始建立反三角函數特殊值查詢表")
        table = {}
        
        # 常見特殊值
        special_inputs = {
            InverseTrigFunction.ARCSIN: [
                -1, -sp.sqrt(3)/2, -sp.sqrt(2)/2, -1/2, 0, 
                1/2, sp.sqrt(2)/2, sp.sqrt(3)/2, 1
            ],
            InverseTrigFunction.ARCCOS: [
                -1, -sp.sqrt(3)/2, -sp.sqrt(2)/2, -1/2, 0,
                1/2, sp.sqrt(2)/2, sp.sqrt(3)/2, 1
            ],
            InverseTrigFunction.ARCTAN: [
                -sp.sqrt(3), -1, -sp.sqrt(3)/3, 0,
                sp.sqrt(3)/3, 1, sp.sqrt(3)
            ]
        }
        
        for func_enum in self.params.functions:
            if func_enum in special_inputs:
                func_sympy = self.function_map[func_enum]
                for input_val in special_inputs[func_enum]:
                    try:
                        # 計算角度（弧度）
                        angle_rad = func_sympy(input_val)
                        # 轉換為度數
                        angle_deg = float(sp.deg(angle_rad))
                        table[(func_enum, float(input_val))] = angle_deg
                    except Exception as e:
                        logger.debug(f"計算 {func_enum.value}({input_val}) 時出錯: {str(e)}")
        
        logger.debug(f"特殊值查詢表建立完成: {len(table)} 個值")
        return table
    
    def _choose_input_value(self, func_enum: InverseTrigFunction) -> Optional[sp.Expr]:
        """選擇合適的輸入值
        
        Args:
            func_enum: 反三角函數類型
            
        Returns:
            Optional[sp.Expr]: 選擇的輸入值，失敗時返回 None
        """
        if self.params.include_special_values:
            # 使用特殊值
            special_inputs = {
                InverseTrigFunction.ARCSIN: [
                    1/2, sp.sqrt(2)/2, sp.sqrt(3)/2, 1, 0
                ],
                InverseTrigFunction.ARCCOS: [
                    1/2, sp.sqrt(2)/2, sp.sqrt(3)/2, 1, 0
                ],
                InverseTrigFunction.ARCTAN: [
                    sp.sqrt(3)/3, 1, sp.sqrt(3), 0
                ]
            }
            
            # 如果允許負值，添加負值
            if self.params.include_negative_values and func_enum != InverseTrigFunction.ARCCOS:
                base_values = special_inputs[func_enum]
                negative_values = [-v for v in base_values if v != 0]
                special_inputs[func_enum].extend(negative_values)
            
            if func_enum in special_inputs:
                return random.choice(special_inputs[func_enum])
        
        return None
    
    def _generate_single_question(self, func_enum: InverseTrigFunction, input_value: sp.Expr) -> Optional[Dict[str, Any]]:
        """生成單一題目的內部方法
        
        Args:
            func_enum: 反三角函數類型
            input_value: 輸入值
            
        Returns:
            Optional[Dict[str, Any]]: 成功時返回題目字典，失敗時返回 None
        """
        func_sympy = self.function_map[func_enum]
        func_latex = self.latex_map[func_enum]
        
        # 格式化輸入值
        input_latex = latex(input_value)
        
        # 生成題目文字
        if self.params.use_degrees:
            question = f"求 ${func_latex}\\left({input_latex}\\right)$ 的值（以度為單位）"
        else:
            question = f"求 ${func_latex}\\left({input_latex}\\right)$ 的值（以弧度為單位）"
        
        # 計算答案
        try:
            angle_rad = func_sympy(input_value)
            
            if self.params.use_degrees:
                angle_deg = simplify(sp.deg(angle_rad))
                answer = f"${latex(angle_deg)}°$"
            else:
                answer = f"${latex(angle_rad)}$"
                
        except Exception as e:
            logger.warning(f"計算 {func_latex}({input_latex}) 時出錯: {str(e)}")
            return None
        
        # 生成詳細解析
        explanation = self._generate_explanation(func_enum, input_value, angle_rad)
        
        # 評估難度
        difficulty = self._assess_difficulty(func_enum, input_value)
        
        return {
            "question": question,
            "answer": answer,
            "explanation": explanation,
            "size": self.get_question_size(),
            "difficulty": difficulty,
            "category": self.get_category(),
            "subcategory": self.get_subcategory()
        }
    
    def _generate_explanation(self, func_enum: InverseTrigFunction, input_value: sp.Expr, angle_rad: sp.Expr) -> str:
        """生成詳細的解析步驟
        
        Args:
            func_enum: 反三角函數類型
            input_value: 輸入值
            angle_rad: 計算結果（弧度）
            
        Returns:
            str: HTML 格式的解析步驟
        """
        steps = []
        func_latex = self.latex_map[func_enum]
        func_chinese = self.chinese_names[func_enum]
        input_latex = latex(input_value)
        
        # 添加題目重述
        steps.append(f"求 ${func_latex}\\left({input_latex}\\right)$ 的值")
        
        # 添加函數定義說明
        base_func = func_enum.value.replace("arc", "")
        steps.append(f"{func_chinese}函數是{base_func}函數的反函數")
        
        # 添加特殊值說明
        if self._is_special_input_value(func_enum, input_value):
            steps.append(f"{input_latex} 是{func_chinese}函數的特殊值")
        
        # 添加計算結果
        if self.params.use_degrees:
            angle_deg = simplify(sp.deg(angle_rad))
            steps.append(f"因此，${func_latex}\\left({input_latex}\\right) = {latex(angle_deg)}°$")
        else:
            steps.append(f"因此，${func_latex}\\left({input_latex}\\right) = {latex(angle_rad)}$")
        
        return "<br>".join(steps)
    
    def _is_special_input_value(self, func_enum: InverseTrigFunction, input_value: sp.Expr) -> bool:
        """檢查是否為特殊輸入值
        
        Args:
            func_enum: 反三角函數類型
            input_value: 輸入值
            
        Returns:
            bool: 是否為特殊值
        """
        # 檢查常見特殊值
        special_values = [0, 1/2, sp.sqrt(2)/2, sp.sqrt(3)/2, 1, sp.sqrt(3)/3, sp.sqrt(3)]
        
        for special in special_values:
            if abs(float(input_value) - float(special)) < 1e-10:
                return True
            if abs(float(input_value) + float(special)) < 1e-10:  # 負值
                return True
        
        return False
    
    def _assess_difficulty(self, func_enum: InverseTrigFunction, input_value: sp.Expr) -> str:
        """評估題目難度
        
        Args:
            func_enum: 反三角函數類型
            input_value: 輸入值
            
        Returns:
            str: 難度等級
        """
        # 基於函數類型評估基礎難度
        if func_enum == InverseTrigFunction.ARCSIN:
            base_difficulty = "EASY"
        elif func_enum == InverseTrigFunction.ARCCOS:
            base_difficulty = "MEDIUM"
        else:  # ARCTAN
            base_difficulty = "MEDIUM"
        
        # 基於輸入值調整難度
        input_float = float(input_value)
        
        if abs(input_float) in [0, 1]:
            # 最簡單的值
            pass
        elif abs(input_float) == 0.5:
            # 較簡單的特殊值
            if base_difficulty == "EASY":
                base_difficulty = "MEDIUM"
        else:
            # 複雜的特殊值
            if base_difficulty != "HARD":
                base_difficulty = "HARD"
        
        # 負值增加難度
        if input_float < 0 and base_difficulty == "EASY":
            base_difficulty = "MEDIUM"
        
        logger.debug(f"評估難度: {func_enum.value}({input_value}) -> {base_difficulty}")
        return base_difficulty
    
    def _get_default_question(self) -> Dict[str, Any]:
        """獲取預設題目
        
        Returns:
            Dict[str, Any]: 預設題目字典
        """
        logger.info("使用預設反三角函數題目")
        
        return {
            "question": "求 $\\arcsin\\left(\\frac{1}{2}\\right)$ 的值（以度為單位）",
            "answer": "$30°$",
            "explanation": (
                "求 $\\arcsin\\left(\\frac{1}{2}\\right)$ 的值<br>"
                "反正弦函數是正弦函數的反函數<br>"
                "$\\frac{1}{2}$ 是反正弦函數的特殊值<br>"
                "因此，$\\arcsin\\left(\\frac{1}{2}\\right) = 30°$"
            ),
            "size": self.get_question_size(),
            "difficulty": "EASY",
            "category": self.get_category(),
            "subcategory": self.get_subcategory()
        }
    
    def get_question_size(self) -> int:
        """獲取題目顯示大小
        
        反三角函數計算題目通常需要標準顯示空間。
        
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
            str: 具體的反三角函數題型分類
        """
        return "反三角函數練習"