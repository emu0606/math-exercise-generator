#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 基礎生成器類別

提供題目生成系統的核心抽象基礎類別和枚舉定義。
"""

from abc import ABC, abstractmethod
from enum import IntEnum
from typing import Dict, List, Any, ClassVar, Optional
from utils import get_logger

logger = get_logger(__name__)


class QuestionSize(IntEnum):
    """題目顯示大小枚舉

    定義題目在UI中的布局空間大小。
    """
    SMALL = 1   # 1x1
    WIDE = 2    # 2x1
    SQUARE = 3  # 1x2
    MEDIUM = 4  # 2x2
    LARGE = 5   # 3x2
    EXTRA = 6   # 4x2


class QuestionGenerator(ABC):
    """題目生成器抽象基礎類別

    所有具體題目生成器的基礎介面。
    """

    auto_register: ClassVar[bool] = True

    def __init__(self, options: Dict[str, Any] = None):
        """初始化生成器"""
        self.options = options or {}
        logger.debug(f"初始化生成器: {self.__class__.__name__}")

    @abstractmethod
    def generate_question(self) -> Dict[str, Any]:
        """生成一個完整的題目

        Returns:
            Dict包含: question, answer, explanation, metadata等
        """
        pass

    @abstractmethod
    def get_question_size(self) -> int:
        """獲取題目顯示大小"""
        pass

    @abstractmethod
    def get_category(self) -> str:
        """獲取題目主類別"""
        pass

    @abstractmethod
    def get_subcategory(self) -> str:
        """獲取題目子類別"""
        pass

    @abstractmethod
    def get_grade(self) -> str:
        """獲取適用年級"""
        pass

    def get_subject(self) -> str:
        """獲取科目，預設為數學，未來可擴展為物理、化學等"""
        return "數學"

    def get_difficulty(self) -> str:
        """獲取難度等級，預設為MEDIUM"""
        return "MEDIUM"

    def get_figure_data_question(self) -> Optional[Dict[str, Any]]:
        """獲取題目圖形數據，預設無圖形"""
        return None

    def get_figure_data_explanation(self) -> Optional[Dict[str, Any]]:
        """獲取解釋圖形數據，預設無圖形"""
        return None

    def get_figure_position(self) -> str:
        """獲取題目圖形位置，預設右側"""
        return "right"

    def get_explanation_figure_position(self) -> str:
        """獲取解釋圖形位置，預設右側"""
        return "right"

    def _get_standard_metadata(self) -> Dict[str, Any]:
        """獲取標準化元數據，消除重複代碼"""
        return {
            "subject": self.get_subject(),
            "category": self.get_category(),
            "subcategory": self.get_subcategory(),
            "grade": self.get_grade(),
            "size": self.get_question_size(),
            "difficulty": self.get_difficulty(),
            "figure_data_question": self.get_figure_data_question(),
            "figure_data_explanation": self.get_figure_data_explanation(),
            "figure_position": self.get_figure_position(),
            "explanation_figure_position": self.get_explanation_figure_position()
        }

    def generate_batch(self, count: int) -> List[Dict[str, Any]]:
        """生成一批題目"""
        if count <= 0:
            raise ValueError(f"題目數量必須大於0，得到: {count}")
        return [self.generate_question() for _ in range(count)]

    def set_options(self, options: Dict[str, Any]) -> None:
        """設置生成器選項"""
        self.options = options

    @classmethod
    def get_config_schema(cls) -> Dict[str, Any]:
        """取得生成器配置描述，供UI動態生成配置介面"""
        return {}

    @classmethod
    def has_config(cls) -> bool:
        """檢查生成器是否需要配置"""
        return bool(cls.get_config_schema())

    @classmethod
    def register(cls) -> None:
        """註冊生成器到中央系統"""
        from utils.core.registry import registry

        try:
            temp_instance = cls()
            category = temp_instance.get_category()
            subcategory = temp_instance.get_subcategory()
            registry.register(cls, category, subcategory)
            logger.info(f"生成器註冊成功: {cls.__name__} [{category}/{subcategory}]")
        except Exception as e:
            logger.error(f"註冊生成器失敗: {cls.__name__} - {e}")
            raise


def register_generator(cls):
    """註冊生成器裝飾器"""
    if getattr(cls, 'auto_register', True):
        try:
            cls.register()
        except Exception as e:
            logger.error(f"裝飾器註冊失敗: {cls.__name__} - {e}")
    return cls