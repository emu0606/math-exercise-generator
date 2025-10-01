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
        """初始化生成器

        Args:
            options: 生成器配置選項，用於自定義生成行為
        """
        self.options = options or {}
        self.logger = get_logger(self.__class__.__name__)
        logger.debug(f"初始化生成器: {self.__class__.__name__}")

    def generate_question(self) -> Dict[str, Any]:
        """標準生成方法，提供統一的錯誤處理機制

        開發者無需覆蓋此方法，而是實現 _generate_core_question()。
        此方法確保所有生成器都有一致的錯誤處理和日誌記錄。

        Returns:
            Dict包含: question, answer, explanation, metadata等
        """
        self.logger.info(f"開始生成{self.__class__.__name__}題目")
        return self._safe_generate("題目生成")

    def _safe_generate(self, description: str = "題目生成") -> Dict[str, Any]:
        """標準安全生成模式，提供統一的異常處理

        採用單次嘗試模式，避免重試機制掩蓋設計問題。
        當核心生成邏輯失敗時，自動使用後備題目確保系統穩定性。

        Args:
            description: 生成階段描述，用於錯誤日誌

        Returns:
            成功時返回核心生成的題目，失敗時返回後備題目
        """
        try:
            return self._generate_core_question()
        except Exception as e:
            # 詳細錯誤信息，包含異常類型和上下文
            self.logger.error(f"{description}失敗: {type(e).__name__}: {str(e)}")

            # 調試模式下提供完整堆疊信息，協助開發者排查問題
            if hasattr(self, 'debug_mode') and self.debug_mode:
                import traceback
                self.logger.debug(f"錯誤堆疊: {traceback.format_exc()}")

            return self._get_fallback_question()

    @abstractmethod
    def _generate_core_question(self) -> Dict[str, Any]:
        """核心生成邏輯，子類必須實現

        此方法應包含生成器的主要邏輯，採用確定性設計避免隨機失敗。
        建議使用預篩選策略而非重試機制來確保生成成功。

        Returns:
            Dict包含: question, answer, explanation等核心內容
        """
        pass

    @abstractmethod
    def _get_fallback_question(self) -> Dict[str, Any]:
        """後備題目，子類必須實現

        當核心生成邏輯失敗時使用的安全題目，必須保證能夠正常工作。
        應選擇簡單、可靠的題目，確保系統在任何情況下都能產生有效輸出。

        Returns:
            Dict包含: question, answer, explanation等完整內容
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