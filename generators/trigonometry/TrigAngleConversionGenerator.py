#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 三角函數角度轉換生成器

本模組提供三角函數角度轉換題目的現代化生成器，採用新架構設計並支持
多種角度轉換模式。使用 Pydantic 進行參數驗證，提供高品質的三角函數
角度轉換教學內容。

主要功能:
- 第一象限角轉換 (0° - 90°)
- 窄角轉換 (0° - 45°) 
- 公式問答題
- 智能週期性處理
- 完整的象限分析

作者: 數學測驗生成器開發團隊
創建日期: 2025-09-07
"""

from __future__ import annotations
from typing import Dict, Any, List, Tuple, Optional
from enum import Enum
import random

from pydantic import BaseModel, Field, validator
from sympy import *

from utils import global_config, get_logger
from generators.base import QuestionGenerator, register_generator

logger = get_logger(__name__)


class TrigFunction(str, Enum):
    """三角函數類型枚舉
    
    定義支援的三角函數類型，確保標準化處理。
    """
    SIN = "sin"
    COS = "cos"
    TAN = "tan"
    COT = "cot"


class ConversionMode(str, Enum):
    """角度轉換模式枚舉
    
    定義不同的角度轉換題目類型。
    """
    FIRST_QUADRANT = "first_quadrant"  # 第一象限角轉換 (0° - 90°)
    NARROW_ANGLE = "narrow_angle"      # 窄角轉換 (0° - 45°)
    FORMULA_QUIZ = "formula_quiz"      # 公式問答題


class TrigConversionParams(BaseModel):
    """三角函數角度轉換生成器參數模型
    
    定義三角函數角度轉換題目生成的所有可配置參數，包含函數選擇、
    轉換模式、難度設定和出現機率控制。
    
    Attributes:
        functions (List[TrigFunction]): 使用的三角函數列表
        conversion_modes (List[ConversionMode]): 支援的轉換模式
        mode_weights (List[int]): 各模式的出現權重 [第一象限, 公式, 窄角]
        angle_range (Tuple[int, int]): 基本角度範圍（度）
        exclude_multiples_of_90 (bool): 是否排除90度的倍數
        max_rotation_turns (int): 最大旋轉圈數
        difficulty_level (str): 難度等級
        
    Example:
        >>> params = TrigConversionParams(
        ...     functions=[TrigFunction.SIN, TrigFunction.COS],
        ...     mode_weights=[60, 20, 20],
        ...     angle_range=(-80, 260)
        ... )
        >>> print(params.functions)
        [TrigFunction.SIN, TrigFunction.COS]
    """
    
    functions: List[TrigFunction] = Field(
        default=[TrigFunction.SIN, TrigFunction.COS, TrigFunction.TAN],
        description="使用的三角函數列表，決定題目涵蓋的函數類型"
    )
    
    conversion_modes: List[ConversionMode] = Field(
        default=[ConversionMode.FIRST_QUADRANT, ConversionMode.FORMULA_QUIZ, ConversionMode.NARROW_ANGLE],
        description="支援的轉換模式列表，決定生成的題目類型"
    )
    
    mode_weights: List[int] = Field(
        default=[70, 10, 20],
        description="各轉換模式的出現權重 [第一象限, 公式問答, 窄角轉換]"
    )
    
    angle_range: tuple = Field(
        default=(-80, 260),
        description="基本角度生成範圍（度），支援負角練習"
    )
    
    exclude_multiples_of_90: bool = Field(
        default=True,
        description="是否排除90度的倍數（避免不適當的角度）"
    )
    
    max_rotation_turns: int = Field(
        default=4,
        description="最大旋轉圈數，控制角度超出基本範圍的程度"
    )
    
    difficulty_level: str = Field(
        default="MEDIUM",
        description="難度等級，影響角度選擇的複雜程度"
    )
    
    @validator('mode_weights')
    def validate_mode_weights(cls, v, values):
        """驗證模式權重配置
        
        確保權重列表長度正確且所有權重為正數。
        """
        if len(v) != 3:
            raise ValueError("mode_weights 必須包含3個權重值 [第一象限, 公式問答, 窄角轉換]")
        if any(weight <= 0 for weight in v):
            raise ValueError("所有權重值必須為正數")
        return v
    
    @validator('angle_range')
    def validate_angle_range(cls, v):
        """驗證角度範圍設定
        
        確保角度範圍合理且覆蓋足夠的學習範圍。
        """
        min_angle, max_angle = v
        if min_angle >= max_angle:
            raise ValueError("最小角度必須小於最大角度")
        if max_angle - min_angle < 90:
            raise ValueError("角度範圍至少需要涵蓋90度以上")
        return v


@register_generator
class TrigAngleConversionGenerator(QuestionGenerator):
    """三角函數角度轉換題目生成器
    
    現代化的三角函數角度轉換生成器，使用新架構API和Pydantic參數驗證。
    支援多種轉換模式，包含第一象限角轉換、窄角轉換和公式問答題。
    
    特色功能:
    - **智能角度轉換**: 自動處理象限轉換和符號變化
    - **多重轉換模式**: 支援第一象限角和窄角轉換
    - **公式問答系統**: 內建三角函數基本關係題庫  
    - **週期性處理**: 智能處理超過360度的角度
    - **完整解析**: 提供詳細的轉換步驟說明
    - **參數驗證**: 使用Pydantic確保配置正確性
    
    轉換邏輯:
    - 第一象限轉換: 任意角度 → 0°-90° 等價角度
    - 窄角轉換: 第一象限角 → 0°-45° + 餘角關係
    - 公式問答: 三角函數基本關係和變換公式
    
    Example:
        >>> generator = TrigAngleConversionGenerator()
        >>> question = generator.generate_question()
        >>> print(question['question'])
        '以 $0\\sim90°$ 表示 $\\sin(150°)$'
        >>> print(question['answer'])
        '$\\sin(30°)$'
        
        >>> # 使用自訂參數
        >>> custom_params = TrigConversionParams(
        ...     functions=[TrigFunction.SIN, TrigFunction.COS],
        ...     mode_weights=[80, 10, 10],
        ...     angle_range=(-60, 240)
        ... )
        >>> generator = TrigAngleConversionGenerator(custom_params)
        >>> question = generator.generate_question()
    
    Note:
        本生成器採用完全重建的新架構設計，不保持與舊版本的向後兼容性。
        使用Pydantic進行參數驗證，確保生成的題目數學正確性。所有角度
        計算使用精確的整數運算，避免浮點數誤差。
    
    Mathematics:
        基於三角函數的週期性和象限特性：
        - sin(θ) 在各象限的符號變化
        - cos(θ) 在各象限的符號變化  
        - tan(θ) 在各象限的符號變化
        - 餘角關係: sin(90°-θ) = cos(θ), cos(90°-θ) = sin(θ)
    """
    
    # 三角函數的 LaTeX 表示映射
    FUNC_LATEX = {
        TrigFunction.SIN: "\\sin",
        TrigFunction.COS: "\\cos", 
        TrigFunction.TAN: "\\tan",
        TrigFunction.COT: "\\cot"
    }
    
    # 三角函數公式問答題庫（角度制）
    FORMULA_QUESTIONS = {
        TrigFunction.SIN: [
            {"question": "\\sin(180°-θ) = ", "answer": "\\sin(θ)"},
            {"question": "\\sin(θ ± 180°) = ", "answer": "-\\sin(θ)"},
            {"question": "\\sin(-θ) = ", "answer": "-\\sin(θ)"},
            {"question": "\\sin(90°-θ) = ", "answer": "\\cos(θ)"},
            {"question": "\\sin(90°+θ) = ", "answer": "\\cos(θ)"}
        ],
        TrigFunction.COS: [
            {"question": "\\cos(180°-θ) = ", "answer": "-\\cos(θ)"},
            {"question": "\\cos(θ ± 180°) = ", "answer": "-\\cos(θ)"},
            {"question": "\\cos(-θ) = ", "answer": "\\cos(θ)"},
            {"question": "\\cos(90°-θ) = ", "answer": "\\sin(θ)"},
            {"question": "\\cos(90°+θ) = ", "answer": "-\\sin(θ)"}
        ],
        TrigFunction.TAN: [
            {"question": "\\tan(180°-θ) = ", "answer": "-\\tan(θ)"},
            {"question": "\\tan(θ ± 180°) = ", "answer": "\\tan(θ)"},
            {"question": "\\tan(-θ) = ", "answer": "-\\tan(θ)"},
            {"question": "\\tan(90°-θ) = ", "answer": "\\cot(θ)"},
            {"question": "\\tan(90°+θ) = ", "answer": "-\\cot(θ)"}
        ]
    }

    def __init__(self, params: Optional[TrigConversionParams] = None):
        """初始化三角函數角度轉換生成器
        
        Args:
            params (Optional[TrigConversionParams]): 生成器參數配置，
                如果未提供則使用預設值
                
        Raises:
            ValidationError: 當參數驗證失敗時拋出異常
        """
        self.params = params or TrigConversionParams()
        
        # 生成基本角度列表
        self.base_angles = self._generate_base_angles()
        
        # 記錄初始化完成
        logger.info("三角函數角度轉換生成器初始化完成")

    def _generate_base_angles(self) -> List[int]:
        """生成基本角度列表
        
        根據參數設定生成用於題目的基本角度列表，自動排除不適當的角度。
        
        Returns:
            List[int]: 過濾後的基本角度列表
        """
        min_angle, max_angle = self.params.angle_range
        angles = list(range(min_angle, max_angle + 1, 10))
        
        if self.params.exclude_multiples_of_90:
            # 排除 90 度的倍數以避免不適當的角度
            angles = [angle for angle in angles if angle % 90 != 0]
        
        logger.debug(f"生成基本角度列表: {len(angles)} 個角度，範圍 {min_angle}° 到 {max_angle}°")
        return angles

    def generate_question(self) -> Dict[str, Any]:
        """生成三角函數角度轉換題目
        
        根據配置的轉換模式和權重，隨機選擇一種模式生成對應的題目。
        
        Returns:
            Dict[str, Any]: 包含以下鍵值的題目字典：
                - question (str): 題目文字（LaTeX格式）
                - answer (str): 答案文字（LaTeX格式）
                - explanation (str): 詳細解析（LaTeX格式）
                - difficulty (str): 難度等級
                - category (str): 題目類別
                - subcategory (str): 題目子類別
                
        Raises:
            ValueError: 當生成過程中遇到無效配置時
        """
        logger.info("開始生成三角函數角度轉換題目")
        
        # 根據權重隨機選擇轉換模式
        mode = random.choices(
            self.params.conversion_modes,
            weights=self.params.mode_weights[:len(self.params.conversion_modes)]
        )[0]
        
        # 根據選擇的模式生成對應題目
        if mode == ConversionMode.FORMULA_QUIZ:
            result = self._generate_formula_question()
        elif mode == ConversionMode.NARROW_ANGLE:
            result = self._generate_narrow_angle_question()
        else:  # ConversionMode.FIRST_QUADRANT
            result = self._generate_first_quadrant_question()
        
        # 添加通用屬性
        result.update({
            "difficulty": self.params.difficulty_level,
            "category": "三角比", 
            "subcategory": "三角函數角度轉換"
        })
        
        logger.info("成功生成三角函數角度轉換題目")
        return result

    def _generate_formula_question(self) -> Dict[str, Any]:
        """生成三角函數公式問答題
        
        從內建的公式題庫中隨機選擇一個公式問答題，測試學生對
        三角函數基本關係的理解。
        
        Returns:
            Dict[str, Any]: 公式問答題目字典
        """
        func = random.choice(self.params.functions)
        question_data = random.choice(self.FORMULA_QUESTIONS[func])
        
        return {
            "question": f"計算 ${question_data['question']}$",
            "answer": f"${question_data['answer']}$",
            "explanation": "公式基本關係題，請熟記三角函數基本公式和變換關係。"
        }

    def _generate_first_quadrant_question(self) -> Dict[str, Any]:
        """生成第一象限角轉換題目
        
        將任意角度的三角函數值轉換為第一象限（0° - 90°）的等價表示，
        包含適當的符號處理和週期性考慮。
        
        Returns:
            Dict[str, Any]: 第一象限轉換題目字典
        """
        func = random.choice(self.params.functions)
        func_latex = self.FUNC_LATEX[func]
        
        # 選擇基本角度和旋轉倍數
        base_angle = random.choice(self.base_angles)
        turns = random.choice([t for t in range(-self.params.max_rotation_turns, 
                                               self.params.max_rotation_turns + 1) if t != 0])
        
        # 計算題目角度
        question_angle = base_angle + turns * 360
        
        # 確保 tan 函數角度的有效性
        if func == TrigFunction.TAN and (question_angle % 180 in [90, -90]):
            question_angle += 10  # 避開 tan 的不連續點
        
        # 執行第一象限轉換
        first_quad_angle, sign = self._convert_to_first_quadrant(func, base_angle)
        
        # 構建題目和答案
        sign_text = "-" if sign == -1 else ""
        
        return {
            "question": f"以 $0\\sim90°$ 表示 ${func_latex}({question_angle}°)$",
            "answer": f"${sign_text}{func_latex}({first_quad_angle}°)$",
            "explanation": self._generate_first_quadrant_explanation(
                func, question_angle, base_angle, first_quad_angle, sign, turns
            )
        }

    def _generate_narrow_angle_question(self) -> Dict[str, Any]:
        """生成窄角（0° - 45°）轉換題目
        
        將任意角度的三角函數值轉換為窄角（0° - 45°）表示，
        需要結合象限轉換和餘角關係。
        
        Returns:
            Dict[str, Any]: 窄角轉換題目字典
        """
        func = random.choice(self.params.functions)
        func_latex = self.FUNC_LATEX[func]
        
        # 選擇基本角度和旋轉倍數
        base_angle = random.choice(self.base_angles)
        turns = random.choice([t for t in range(-self.params.max_rotation_turns,
                                               self.params.max_rotation_turns + 1) if t != 0])
        
        # 計算題目角度
        question_angle = base_angle + turns * 360
        
        # 確保 tan 函數角度的有效性
        if func == TrigFunction.TAN and (question_angle % 180 in [90, -90]):
            question_angle += 10
        
        # 執行兩階段轉換：第一象限 → 窄角
        first_quad_angle, first_sign = self._convert_to_first_quadrant(func, base_angle)
        narrow_angle, final_sign, new_func = self._convert_to_narrow_angle(
            func, first_quad_angle, first_sign
        )
        
        # 構建題目和答案
        new_func_latex = self.FUNC_LATEX[new_func]
        sign_text = "-" if final_sign == -1 else ""
        
        return {
            "question": f"以 $0\\sim45°$ 表示 ${func_latex}({question_angle}°)$",
            "answer": f"${sign_text}{new_func_latex}({narrow_angle}°)$",
            "explanation": self._generate_narrow_angle_explanation(
                func, question_angle, base_angle, first_quad_angle, first_sign,
                new_func, narrow_angle, final_sign, turns
            )
        }

    def _convert_to_first_quadrant(self, func: TrigFunction, angle: int) -> tuple:
        """將角度轉換為第一象限等價角度
        
        根據三角函數在各象限的符號規律，將任意角度轉換為第一象限
        的等價角度，並返回相應的符號。
        
        Args:
            func (TrigFunction): 三角函數類型
            angle (int): 輸入角度（度）
            
        Returns:
            Tuple[int, int]: (等價第一象限角度, 符號) 其中符號為 1 或 -1
        """
        # 正規化角度到 0° - 360° 或負角範圍
        normalized_angle = angle % 360 if angle >= 0 else angle
        
        if 0 <= normalized_angle <= 90:  # 第一象限
            return normalized_angle, 1
        elif 90 < normalized_angle < 180:  # 第二象限
            equiv_angle = 180 - normalized_angle
            return equiv_angle, 1 if func == TrigFunction.SIN else -1
        elif 180 <= normalized_angle < 270:  # 第三象限
            equiv_angle = normalized_angle - 180
            return equiv_angle, 1 if func == TrigFunction.TAN else -1
        elif 270 <= normalized_angle < 360:  # 第四象限
            equiv_angle = 360 - normalized_angle
            return equiv_angle, 1 if func == TrigFunction.COS else -1
        else:  # 負角 (-90° < angle < 0°)
            equiv_angle = -normalized_angle
            return equiv_angle, 1 if func == TrigFunction.COS else -1

    def _convert_to_narrow_angle(self, func: TrigFunction, angle: int, 
                                sign: int) -> tuple:
        """將第一象限角度轉換為窄角（0° - 45°）
        
        使用餘角關係將第一象限角度進一步轉換為 0° - 45° 範圍。
        
        Args:
            func (TrigFunction): 原始三角函數類型
            angle (int): 第一象限角度
            sign (int): 原始符號（1 或 -1）
            
        Returns:
            Tuple[int, int, TrigFunction]: (窄角度, 最終符號, 新函數類型)
        """
        if 0 <= angle <= 45:
            return angle, sign, func  # 已經在窄角範圍內
        else:  # 45° < angle <= 90°
            narrow_angle = 90 - angle
            # 應用餘角關係
            if func == TrigFunction.SIN:
                return narrow_angle, sign, TrigFunction.COS
            elif func == TrigFunction.COS:
                return narrow_angle, sign, TrigFunction.SIN
            else:  # TrigFunction.TAN
                return narrow_angle, sign, TrigFunction.COT

    def _generate_first_quadrant_explanation(self, func: TrigFunction, question_angle: int,
                                           base_angle: int, first_quad_angle: int,
                                           sign: int, turns: int) -> str:
        """生成第一象限轉換的詳細解析
        
        Args:
            func: 三角函數類型
            question_angle: 題目角度
            base_angle: 基本角度（移除週期後）
            first_quad_angle: 第一象限等價角度
            sign: 符號（1 或 -1）
            turns: 旋轉圈數
            
        Returns:
            str: LaTeX 格式的詳細解析文字
        """
        func_latex = self.FUNC_LATEX[func]
        explanation = f"${func_latex}({question_angle}°)"
        
        # 第一步：處理週期性（如果需要）
        if turns != 0:
            if turns > 0:
                explanation += f" = {func_latex}({question_angle}° - {turns} \\cdot 360°) = {func_latex}({base_angle}°)"
            else:
                explanation += f" = {func_latex}({question_angle}° + {-turns} \\cdot 360°) = {func_latex}({base_angle}°)"
        
        # 第二步：象限轉換
        if 0 <= base_angle <= 90:
            pass  # 已在第一象限，無需轉換
        elif 90 < base_angle < 180:  # 第二象限
            if func == TrigFunction.SIN:
                explanation += f" = {func_latex}(180° - {base_angle}°) = {func_latex}({first_quad_angle}°)"
            else:
                explanation += f" = -{func_latex}(180° - {base_angle}°) = -{func_latex}({first_quad_angle}°)"
        elif 180 <= base_angle < 270:  # 第三象限
            if func == TrigFunction.TAN:
                explanation += f" = {func_latex}({base_angle}° - 180°) = {func_latex}({first_quad_angle}°)"
            else:
                explanation += f" = -{func_latex}({base_angle}° - 180°) = -{func_latex}({first_quad_angle}°)"
        elif 270 <= base_angle < 360:  # 第四象限
            if func == TrigFunction.COS:
                explanation += f" = {func_latex}(360° - {base_angle}°) = {func_latex}({first_quad_angle}°)"
            else:
                explanation += f" = -{func_latex}(360° - {base_angle}°) = -{func_latex}({first_quad_angle}°)"
        elif -90 < base_angle < 0:  # 負角
            if func == TrigFunction.COS:
                explanation += f" = {func_latex}(-({base_angle}°)) = {func_latex}({first_quad_angle}°)"
            else:
                explanation += f" = -{func_latex}(-({base_angle}°)) = -{func_latex}({first_quad_angle}°)"
        
        explanation += "$"
        return explanation

    def _generate_narrow_angle_explanation(self, func: TrigFunction, question_angle: int,
                                         base_angle: int, first_quad_angle: int, first_sign: int,
                                         new_func: TrigFunction, narrow_angle: int,
                                         final_sign: int, turns: int) -> str:
        """生成窄角轉換的詳細解析
        
        結合第一象限轉換和餘角關係的完整解析步驟。
        
        Returns:
            str: LaTeX 格式的詳細解析文字
        """
        # 先生成第一象限轉換的解析
        first_part = self._generate_first_quadrant_explanation(
            func, question_angle, base_angle, first_quad_angle, first_sign, turns
        )
        
        # 如果已經在窄角範圍內，直接返回
        if first_quad_angle <= 45:
            return first_part
        
        # 移除末尾的 $ 符號
        if first_part.endswith("$"):
            first_part = first_part[:-1]
        
        # 添加窄角轉換步驟
        func_latex = self.FUNC_LATEX[func]
        new_func_latex = self.FUNC_LATEX[new_func]
        sign_text = "-" if first_sign == -1 else ""
        final_sign_text = "-" if final_sign == -1 else ""
        
        second_part = (f" = {sign_text}{func_latex}(90° - {narrow_angle}°) = "
                      f"{final_sign_text}{new_func_latex}({narrow_angle}°)$")
        
        return first_part + second_part

    def get_category(self) -> str:
        """獲取題目主類別
        
        Returns:
            str: 題目主類別名稱
        """
        return "三角函數"

    def get_subcategory(self) -> str:
        """獲取題目子類別
        
        Returns:
            str: 題目子類別名稱
        """
        return "三角函數角度轉換"

    def get_question_size(self) -> int:
        """獲取題目大小
        
        Returns:
            int: 題目顯示大小，通常用於UI佈局
        """
        # 假設有一個 QuestionSize 類別定義了常數
        return 2  # 或根據具體需求返回適當的大小