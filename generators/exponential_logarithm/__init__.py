#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 指數與對數題目生成器模組

本模組提供指數與對數相關的數學題目生成器，涵蓋對數概算、
指數運算、對數性質等高中數學核心內容。使用新架構的統一 API，
整合配置管理和日誌系統，提供高品質的指數對數教學內容。

可用的指數對數生成器：
- LogarithmInterpolationGenerator: 對數內插法練習題目生成器

主要特色：
- 支援正向內插（給真數求對數）和反向內插（給對數求真數）
- 可逆配對表確保數學邏輯一致性
- 附帶數線圖形輔助視覺化
- 完整的詳解生成（公式→代入→答案）
- 符合 LaTeX 標準格式規範

Example:
    >>> from generators.exponential_logarithm import LogarithmInterpolationGenerator
    >>>
    >>> # 使用預設設定創建生成器（混合模式）
    >>> generator = LogarithmInterpolationGenerator()
    >>> question = generator.generate_question()
    >>> print(question['question'])
    '利用內插法估算：$\\log 2.5 \\approx$ ?'
    >>> print(question['grade'])
    'G10S2'
    >>>
    >>> # 使用自訂設定創建生成器（僅正向題型）
    >>> forward_generator = LogarithmInterpolationGenerator({
    ...     'question_type': 'forward'
    ... })
    >>> forward_question = forward_generator.generate_question()

Note:
    對數內插法生成器使用預建可逆配對表，確保正向和反向內插的數學
    一致性，避免產生矛盾的題目。所有對數值以十為底，符合高中教學標準。
"""

from utils import get_logger

logger = get_logger(__name__)

# 記錄模組初始化
logger.info("指數與對數生成器模組初始化完成")
logger.debug("生成器通過自動註冊系統載入")

# 不暴露任何具體生成器，完全依賴自動註冊
__all__ = []
