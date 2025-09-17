#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 題目生成器模組
"""

import os
import importlib
import pkgutil

# 導入基礎類別和裝飾器
from generators.base import QuestionGenerator, register_generator, QuestionSize

# 自動導入所有子包和模組
def import_submodules():
    """自動導入所有子模組以觸發註冊"""
    current_dir = os.path.dirname(__file__)
    for _, name, is_pkg in pkgutil.iter_modules([current_dir]):
        if is_pkg:  # 如果是子包（如 algebra, arithmetic）
            # 導入子包
            module_name = f"generators.{name}"
            module = importlib.import_module(module_name)
            # 遍歷子包中的所有模組
            submodule_dir = os.path.join(current_dir, name)
            for _, sub_name, _ in pkgutil.iter_modules([submodule_dir]):
                try:
                    # 導入模組，這將觸發裝飾器
                    importlib.import_module(f"{module_name}.{sub_name}")
                except Exception as e:
                    print(f"無法導入模組 {module_name}.{sub_name}: {e}")

# 執行自動導入
import_submodules()

# 為了向後兼容，保留這些導入
from generators.algebra import DoubleRadicalSimplificationGenerator

__all__ = [
    'QuestionGenerator', 
    'register_generator', 
    'QuestionSize',
    'DoubleRadicalSimplificationGenerator'
]
