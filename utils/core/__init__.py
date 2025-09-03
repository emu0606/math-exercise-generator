"""
Utils 核心模組

提供基礎設施功能：
- 配置管理 (config)
- 日誌系統 (logging)
- 註冊系統 (registry)
- 佈局引擎 (layout)

使用方式：
    # 全域配置
    from utils.core import global_config
    
    # 日誌系統
    from utils.core import get_logger
    
    # 註冊系統
    from utils.core import registry
    
    # 佈局引擎
    from utils.core import LayoutEngine
"""

# 導入核心模組
from .config import global_config, GlobalConfig
from .logging import get_logger, set_global_log_level, setup_debug_logging
from .registry import registry, GeneratorRegistry, RegistryError
from .layout import LayoutEngine, QuestionSize, LayoutError

# 公開模組介面清單
__all__ = [
    # 配置系統
    'global_config',
    'GlobalConfig',
    
    # 日誌系統
    'get_logger',
    'set_global_log_level', 
    'setup_debug_logging',
    
    # 註冊系統
    'registry',
    'GeneratorRegistry',
    'RegistryError',
    
    # 佈局引擎
    'LayoutEngine',
    'QuestionSize',
    'LayoutError'
]

# 版本資訊
__version__ = "1.0.0"

# 模組資訊
__author__ = "Math Exercise Generator Team"
__description__ = "Core utilities for math exercise generator"