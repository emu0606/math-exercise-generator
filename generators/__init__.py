#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 題目生成器模組

本模組是題目生成系統的核心入口，提供統一的生成器註冊機制
和自動導入功能。所有的數學題目生成器都會透過此模組進行
統一管理和註冊。使用新架構的統一 API，整合配置管理和日誌系統。

主要功能：
- 自動導入所有子模組中的生成器
- 統一的生成器註冊和管理
- 提供基礎類別和裝飾器
- 向後兼容性支援

Example:
    >>> from generators import QuestionGenerator, register_generator
    >>> from generators import DoubleRadicalSimplificationGenerator
    >>> # 所有生成器會自動註冊到中央系統
    
Note:
    此模組會在導入時自動掃描所有子模組並觸發生成器註冊，
    確保系統能夠發現所有可用的題目生成器。
"""

import os
import importlib
import pkgutil

from utils import global_config, get_logger

logger = get_logger(__name__)

# 導入基礎類別和裝飾器
from generators.base import QuestionGenerator, register_generator, QuestionSize

# 自動導入所有子包和模組
def import_submodules():
    """自動導入所有子模組以觸發生成器註冊
    
    遞迴掃描 generators/ 目錄下的所有子包和模組，
    自動導入它們以觸發 @register_generator 裝飾器的執行，
    確保所有生成器都被正確註冊到中央系統中。
    
    此函數會處理以下結構：
    - generators/
      - algebra/
        - __init__.py
        - double_radical.py (包含生成器類別)
      - arithmetic/
        - addition.py
        - ...
        
    Raises:
        ImportError: 如果子模組導入失敗（會記錄但不中斷）
        
    Example:
        >>> # 此函數在模組導入時自動執行
        >>> import generators  # 觸發所有子模組的導入和註冊
        
    Note:
        導入錯誤會被捕獲並記錄，但不會中斷整個導入過程，
        確保其他正常的生成器能夠成功註冊。
    """
    logger.info("開始自動導入所有題目生成器子模組")
    current_dir = os.path.dirname(__file__)
    imported_count = 0
    error_count = 0
    
    for _, name, is_pkg in pkgutil.iter_modules([current_dir]):
        if is_pkg:  # 如果是子包（如 algebra, arithmetic）
            logger.debug(f"發現子包: {name}")
            
            try:
                # 導入子包
                module_name = f"generators.{name}"
                module = importlib.import_module(module_name)
                logger.debug(f"成功導入子包: {module_name}")
                
                # 遍歷子包中的所有模組
                submodule_dir = os.path.join(current_dir, name)
                for _, sub_name, _ in pkgutil.iter_modules([submodule_dir]):
                    try:
                        # 導入模組，這將觸發裝飾器
                        submodule_name = f"{module_name}.{sub_name}"
                        importlib.import_module(submodule_name)
                        logger.debug(f"成功導入子模組: {submodule_name}")
                        imported_count += 1
                    except Exception as e:
                        logger.warning(f"無法導入模組 {module_name}.{sub_name}: {str(e)}")
                        error_count += 1
                        
            except Exception as e:
                logger.error(f"無法導入子包 {name}: {str(e)}")
                error_count += 1
    
    logger.info(f"子模組導入完成: 成功 {imported_count} 個，失敗 {error_count} 個")

# 執行自動導入
logger.info("初始化 generators 模組，開始自動註冊所有生成器")
import_submodules()
logger.info("generators 模組初始化完成")

# 為了向後兼容，保留這些導入
try:
    from generators.algebra import DoubleRadicalSimplificationGenerator
    legacy_generators = ['DoubleRadicalSimplificationGenerator']
    logger.debug("成功導入舊版生成器以保持向後兼容")
except ImportError as e:
    logger.warning(f"無法導入舊版生成器，向後兼容性可能受影響: {str(e)}")
    legacy_generators = []

# 公開 API 列表
__all__ = [
    # 基礎類別和工具
    'QuestionGenerator', 
    'register_generator', 
    'QuestionSize',
    # 自動導入功能
    'import_submodules',
] + legacy_generators  # 動態添加可用的舊版生成器
