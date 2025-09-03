"""
統一配置管理系統

提供全域配置管理，包含以下功能：
1. 調試模式控制
2. 日誌級別設定
3. 數學後端選擇
4. TikZ 精度設定
5. LaTeX 字體路徑
6. PDF 編譯超時設定

使用方式：
    from utils.core.config import global_config
    
    # 讀取配置
    debug_mode = global_config.debug_mode
    
    # 修改配置
    global_config.set_debug_mode(True)
"""

import os
from typing import Literal, Optional
from pathlib import Path


class GlobalConfig:
    """全域配置管理類
    
    採用單例模式，確保全專案使用同一套配置。
    所有配置項都有合理的預設值，並提供驗證機制。
    """
    
    _instance: Optional['GlobalConfig'] = None
    _initialized: bool = False
    
    def __new__(cls) -> 'GlobalConfig':
        """單例模式實現
        
        確保整個應用程序中只存在一個配置實例。
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化配置
        
        只在第一次創建實例時執行初始化。
        """
        if self._initialized:
            return
            
        # 調試與日誌設定
        self._debug_mode: bool = False
        self._log_level: str = "INFO"
        
        # 數學計算後端設定
        self._math_backend_default: Literal["numpy", "sympy", "python"] = "numpy"
        
        # TikZ 渲染設定
        self._tikz_precision: int = 7  # TikZ 座標精度（小數位數）
        
        # LaTeX 相關設定
        self._latex_font_path: str = "./assets/fonts/"
        self._pdf_compiler: str = "xelatex"  # PDF 編譯器選擇
        self._pdf_compiler_timeout: int = 120  # 編譯超時時間（秒）
        
        # 性能設定
        self._cache_enabled: bool = True  # 啟用編譯快取
        self._parallel_compilation: bool = False  # 並行編譯（實驗功能）
        
        self._initialized = True
    
    # === 調試與日誌相關屬性 ===
    
    @property
    def debug_mode(self) -> bool:
        """調試模式狀態"""
        return self._debug_mode
    
    def set_debug_mode(self, enabled: bool) -> None:
        """設定調試模式
        
        Args:
            enabled: 是否啟用調試模式
        """
        self._debug_mode = bool(enabled)
        if enabled:
            self._log_level = "DEBUG"
    
    @property
    def log_level(self) -> str:
        """當前日誌級別"""
        return self._log_level
    
    def set_log_level(self, level: str) -> None:
        """設定日誌級別
        
        Args:
            level: 日誌級別 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if level.upper() not in valid_levels:
            raise ValueError(f"無效的日誌級別: {level}. 有效選項: {valid_levels}")
        self._log_level = level.upper()
    
    # === 數學計算後端相關屬性 ===
    
    @property
    def math_backend_default(self) -> str:
        """預設數學計算後端"""
        return self._math_backend_default
    
    def set_math_backend_default(self, backend: Literal["numpy", "sympy", "python"]) -> None:
        """設定預設數學計算後端
        
        Args:
            backend: 後端類型
                - numpy: 高效數值計算
                - sympy: 符號數學計算  
                - python: 純 Python 實現（後備選項）
        """
        if backend not in ["numpy", "sympy", "python"]:
            raise ValueError(f"不支持的數學後端: {backend}")
        self._math_backend_default = backend
    
    # === TikZ 渲染相關屬性 ===
    
    @property
    def tikz_precision(self) -> int:
        """TikZ 座標精度（小數位數）"""
        return self._tikz_precision
    
    def set_tikz_precision(self, precision: int) -> None:
        """設定 TikZ 座標精度
        
        Args:
            precision: 小數位數 (1-15)
        """
        if not 1 <= precision <= 15:
            raise ValueError("TikZ 精度必須在 1-15 之間")
        self._tikz_precision = precision
    
    # === LaTeX 相關屬性 ===
    
    @property
    def latex_font_path(self) -> str:
        """LaTeX 字體路徑"""
        return self._latex_font_path
    
    def set_latex_font_path(self, path: str) -> None:
        """設定 LaTeX 字體路徑
        
        Args:
            path: 字體目錄路徑
        """
        font_path = Path(path)
        if not font_path.exists():
            raise ValueError(f"字體路徑不存在: {path}")
        self._latex_font_path = str(font_path.resolve())
    
    @property
    def pdf_compiler(self) -> str:
        """PDF 編譯器"""
        return self._pdf_compiler
    
    def set_pdf_compiler(self, compiler: str) -> None:
        """設定 PDF 編譯器
        
        Args:
            compiler: 編譯器名稱 (xelatex, pdflatex, lualatex)
        """
        valid_compilers = ["xelatex", "pdflatex", "lualatex"]
        if compiler not in valid_compilers:
            raise ValueError(f"不支持的編譯器: {compiler}. 有效選項: {valid_compilers}")
        self._pdf_compiler = compiler
    
    @property
    def pdf_compiler_timeout(self) -> int:
        """PDF 編譯超時時間（秒）"""
        return self._pdf_compiler_timeout
    
    def set_pdf_compiler_timeout(self, timeout: int) -> None:
        """設定 PDF 編譯超時時間
        
        Args:
            timeout: 超時時間（秒），最小 30 秒
        """
        if timeout < 30:
            raise ValueError("編譯超時時間不能少於 30 秒")
        self._pdf_compiler_timeout = timeout
    
    # === 性能相關屬性 ===
    
    @property
    def cache_enabled(self) -> bool:
        """快取是否啟用"""
        return self._cache_enabled
    
    def set_cache_enabled(self, enabled: bool) -> None:
        """設定是否啟用快取
        
        Args:
            enabled: 是否啟用快取
        """
        self._cache_enabled = bool(enabled)
    
    @property
    def parallel_compilation(self) -> bool:
        """並行編譯是否啟用"""
        return self._parallel_compilation
    
    def set_parallel_compilation(self, enabled: bool) -> None:
        """設定是否啟用並行編譯（實驗功能）
        
        Args:
            enabled: 是否啟用並行編譯
        """
        self._parallel_compilation = bool(enabled)
    
    # === 工具方法 ===
    
    def reset_to_defaults(self) -> None:
        """重置所有配置為預設值"""
        self._debug_mode = False
        self._log_level = "INFO"
        self._math_backend_default = "numpy"
        self._tikz_precision = 7
        self._latex_font_path = "./assets/fonts/"
        self._pdf_compiler = "xelatex"
        self._pdf_compiler_timeout = 120
        self._cache_enabled = True
        self._parallel_compilation = False
    
    def get_config_summary(self) -> dict:
        """取得所有配置的摘要資訊
        
        Returns:
            包含所有配置項的字典
        """
        return {
            "debug_mode": self._debug_mode,
            "log_level": self._log_level,
            "math_backend_default": self._math_backend_default,
            "tikz_precision": self._tikz_precision,
            "latex_font_path": self._latex_font_path,
            "pdf_compiler": self._pdf_compiler,
            "pdf_compiler_timeout": self._pdf_compiler_timeout,
            "cache_enabled": self._cache_enabled,
            "parallel_compilation": self._parallel_compilation
        }
    
    def __repr__(self) -> str:
        """配置對象的字串表示"""
        return f"GlobalConfig(debug={self._debug_mode}, backend={self._math_backend_default})"


# 全域配置實例
# 整個專案中使用此實例來存取配置
global_config = GlobalConfig()