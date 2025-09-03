"""
統一日誌系統

提供全專案統一的日誌管理功能：
1. 統一日誌格式和級別管理
2. 多模組日誌支援
3. 自動配置與全域配置集成
4. 調試模式支援
5. 防重複添加 handler

使用方式：
    from utils.core.logging import get_logger
    
    # 取得模組專用 logger
    logger = get_logger(__name__)
    
    # 使用日誌
    logger.info("這是一條資訊日誌")
    logger.debug("這是一條調試日誌")
    logger.warning("這是一條警告日誌")
    logger.error("這是一條錯誤日誌")
"""

import logging
import sys
from typing import Optional, Dict
from pathlib import Path
from datetime import datetime

# 延遲導入配置，避免循環依賴
_global_config = None


def _get_global_config():
    """延遲取得全域配置
    
    避免模組初始化時的循環依賴問題。
    """
    global _global_config
    if _global_config is None:
        try:
            from .config import global_config
            _global_config = global_config
        except ImportError:
            # 如果配置模組不可用，使用預設設定
            _global_config = None
    return _global_config


class ColoredFormatter(logging.Formatter):
    """帶顏色的日誌格式化器
    
    在控制台輸出時為不同級別的日誌添加顏色，
    提升開發體驗和日誌可讀性。
    """
    
    # ANSI 顏色碼定義
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 綠色  
        'WARNING': '\033[33m',    # 黃色
        'ERROR': '\033[31m',      # 紅色
        'CRITICAL': '\033[91m',   # 亮紅色
    }
    RESET = '\033[0m'  # 重置顏色
    
    def __init__(self, use_colors: bool = True):
        """初始化格式化器
        
        Args:
            use_colors: 是否使用顏色輸出
        """
        # 標準日誌格式：時間 - 模組名 - 級別 - 訊息
        super().__init__(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.use_colors = use_colors
    
    def format(self, record):
        """格式化日誌記錄
        
        Args:
            record: 日誌記錄對象
            
        Returns:
            格式化後的日誌字串
        """
        # 先進行標準格式化
        formatted = super().format(record)
        
        # 如果啟用顏色且輸出到終端，添加顏色
        if self.use_colors and hasattr(sys.stderr, 'isatty') and sys.stderr.isatty():
            level_color = self.COLORS.get(record.levelname, '')
            if level_color:
                formatted = f"{level_color}{formatted}{self.RESET}"
        
        return formatted


class LoggerManager:
    """日誌管理器
    
    負責創建和管理所有模組的 logger，
    確保日誌配置的一致性和避免重複配置。
    """
    
    def __init__(self):
        """初始化日誌管理器"""
        # 存儲已創建的 logger
        self._loggers: Dict[str, logging.Logger] = {}
        
        # 日誌級別映射
        self._level_mapping = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        
        # 是否已設定根日誌器
        self._root_configured = False
    
    def _configure_root_logger(self) -> None:
        """配置根日誌器
        
        只在第一次調用時執行，避免重複配置。
        """
        if self._root_configured:
            return
        
        # 取得全域配置
        config = _get_global_config()
        
        # 確定日誌級別
        if config and hasattr(config, 'log_level'):
            log_level = config.log_level
        else:
            log_level = "INFO"
        
        # 設定根日誌器級別
        root_logger = logging.getLogger()
        root_logger.setLevel(self._level_mapping.get(log_level, logging.INFO))
        
        self._root_configured = True
    
    def get_logger(self, name: str, level: Optional[str] = None) -> logging.Logger:
        """取得或創建指定名稱的 logger
        
        Args:
            name: logger 名稱，通常使用模組的 __name__
            level: 自定義日誌級別，如不指定則使用全域設定
            
        Returns:
            配置好的 logger 實例
        """
        # 配置根日誌器（只執行一次）
        self._configure_root_logger()
        
        # 如果 logger 已存在，直接返回
        if name in self._loggers:
            return self._loggers[name]
        
        # 創建新的 logger
        logger = logging.getLogger(name)
        
        # 避免重複添加 handler
        if not logger.handlers:
            # 創建控制台 handler
            console_handler = logging.StreamHandler(sys.stdout)
            
            # 設定格式化器
            formatter = ColoredFormatter(use_colors=True)
            console_handler.setFormatter(formatter)
            
            # 添加 handler
            logger.addHandler(console_handler)
            
            # 設定日誌級別
            if level:
                logger.setLevel(self._level_mapping.get(level.upper(), logging.INFO))
            else:
                # 使用全域配置的級別
                config = _get_global_config()
                if config and hasattr(config, 'log_level'):
                    logger.setLevel(self._level_mapping.get(config.log_level, logging.INFO))
                else:
                    logger.setLevel(logging.INFO)
            
            # 防止日誌向上傳播（避免重複輸出）
            logger.propagate = False
        
        # 快取 logger
        self._loggers[name] = logger
        
        return logger
    
    def set_global_level(self, level: str) -> None:
        """設定所有 logger 的全域級別
        
        Args:
            level: 日誌級別字串
        """
        log_level = self._level_mapping.get(level.upper(), logging.INFO)
        
        # 更新根日誌器
        logging.getLogger().setLevel(log_level)
        
        # 更新所有已創建的 logger
        for logger in self._loggers.values():
            logger.setLevel(log_level)
    
    def add_file_handler(self, 
                        name: str, 
                        filepath: str, 
                        level: Optional[str] = None) -> None:
        """為指定 logger 添加文件輸出 handler
        
        Args:
            name: logger 名稱
            filepath: 日誌文件路徑
            level: 文件日誌級別，如不指定則使用 logger 的級別
        """
        if name not in self._loggers:
            raise ValueError(f"Logger '{name}' 不存在，請先創建")
        
        logger = self._loggers[name]
        
        # 確保目錄存在
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        # 創建文件 handler
        file_handler = logging.FileHandler(filepath, encoding='utf-8')
        
        # 設定格式化器（文件輸出不使用顏色）
        formatter = ColoredFormatter(use_colors=False)
        file_handler.setFormatter(formatter)
        
        # 設定級別
        if level:
            file_handler.setLevel(self._level_mapping.get(level.upper(), logging.INFO))
        
        # 添加到 logger
        logger.addHandler(file_handler)
    
    def get_logger_info(self) -> Dict[str, Dict]:
        """取得所有 logger 的資訊
        
        Returns:
            包含所有 logger 資訊的字典
        """
        info = {}
        for name, logger in self._loggers.items():
            info[name] = {
                'level': logging.getLevelName(logger.level),
                'handlers_count': len(logger.handlers),
                'propagate': logger.propagate
            }
        return info


# 全域日誌管理器實例
_logger_manager = LoggerManager()


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """取得模組專用的 logger
    
    這是主要的對外接口，其他模組應該使用此函數來獲取 logger。
    
    Args:
        name: logger 名稱，建議使用 __name__
        level: 自定義日誌級別，可選
        
    Returns:
        配置好的 logger 實例
        
    Example:
        # 在模組中使用
        from utils.core.logging import get_logger
        logger = get_logger(__name__)
        
        # 記錄不同級別的日誌
        logger.debug("調試資訊")
        logger.info("一般資訊") 
        logger.warning("警告訊息")
        logger.error("錯誤訊息")
        logger.critical("嚴重錯誤")
    """
    return _logger_manager.get_logger(name, level)


def set_global_log_level(level: str) -> None:
    """設定全域日誌級別
    
    影響所有已創建和未來創建的 logger。
    
    Args:
        level: 日誌級別 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    _logger_manager.set_global_level(level)


def add_file_logging(name: str, filepath: str, level: Optional[str] = None) -> None:
    """為指定 logger 添加文件輸出
    
    Args:
        name: logger 名稱
        filepath: 日誌文件路徑
        level: 文件日誌級別
    """
    _logger_manager.add_file_handler(name, filepath, level)


def get_all_loggers_info() -> Dict[str, Dict]:
    """取得所有 logger 的狀態資訊
    
    主要用於調試和監控目的。
    
    Returns:
        包含所有 logger 資訊的字典
    """
    return _logger_manager.get_logger_info()


def setup_debug_logging() -> None:
    """啟用調試模式日誌
    
    將所有日誌級別設為 DEBUG，方便開發調試。
    """
    set_global_log_level('DEBUG')
    
    # 同時更新全域配置（如果可用）
    config = _get_global_config()
    if config and hasattr(config, 'set_debug_mode'):
        config.set_debug_mode(True)