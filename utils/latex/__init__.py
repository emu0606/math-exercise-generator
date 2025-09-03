"""
LaTeX 文檔處理模組

提供 LaTeX 文檔生成、編譯和配置管理功能：
- LaTeX 文檔編譯 (XeLaTeX, PDFLaTeX, LuaLaTeX)
- 文檔配置管理 (字體、版面、樣式)
- 編譯錯誤處理和日誌解析
- 中文數學文檔支援

使用方式：
    # LaTeX 編譯
    from utils.latex import LaTeXCompiler, DocumentConfig
    
    compiler = LaTeXCompiler()
    result = compiler.compile(tex_content, output_path)
    
    # 快速創建數學文檔
    from utils.latex import create_math_document
    
    config = DocumentConfig(title="測試文檔")
    doc = create_math_document(config)
"""

# 導入異常類
from .exceptions import (
    LaTeXError,
    CompilationError,
    TemplateError,
    DocumentStructureError,
    PackageDependencyError,
    LaTeXConfigError,
    LaTeXSyntaxError,
    FontError,
    # 便利函數
    missing_package_error,
    invalid_template_error,
    compilation_timeout_error,
    invalid_latex_syntax_error
)

# 導入類型定義
from .types import (
    # 枚舉類
    PaperSize,
    FontSize,
    Encoding,
    Geometry,
    
    # 配置類
    DocumentConfig,
    CompilerConfig,
    FontConfig,
    TemplateConfig,
    
    # 文檔類
    LaTeXDocument,
    CompilationResult
)

# 導入編譯器
from .compiler import (
    LaTeXCompiler,
    quick_compile,
    compile_file
)

# 導入生成器
from .generator import LaTeXGenerator

# 導入結構模組
from .structure import LaTeXStructure

# 導入配置模組  
from .config import LaTeXConfig

# 導入轉義功能
from .escape import escape_latex as escape_latex_text

# 版本資訊
__version__ = "1.0.0"
__author__ = "Math Exercise Generator Team"

# 模組日誌
from ..core.logging import get_logger
logger = get_logger(__name__)

# 模組初始化日誌
logger.debug(f"LaTeX 模組載入完成，版本: {__version__}")

# 全域配置
from ..core.config import global_config

# 便利函數

def create_latex_compiler(engine: str = "xelatex", **kwargs) -> LaTeXCompiler:
    """創建 LaTeX 編譯器
    
    Args:
        engine: 編譯引擎名稱
        **kwargs: 編譯器配置
        
    Returns:
        LaTeXCompiler 實例
    """
    logger.debug(f"創建 LaTeX 編譯器: {engine}")
    return LaTeXCompiler(engine=engine, **kwargs)


def create_math_document(title: str = "數學文檔", 
                        author: str = "", 
                        **kwargs) -> LaTeXDocument:
    """創建數學文檔
    
    Args:
        title: 文檔標題
        author: 作者
        **kwargs: 其他文檔配置
        
    Returns:
        LaTeXDocument 實例
    """
    config = DocumentConfig(
        title=title,
        author=author,
        **kwargs
    )
    
    logger.debug(f"創建數學文檔: {title}")
    return LaTeXDocument(config)


def create_chinese_math_document(title: str = "數學練習", **kwargs) -> LaTeXDocument:
    """創建中文數學文檔
    
    Args:
        title: 文檔標題
        **kwargs: 其他配置
        
    Returns:
        配置好中文支援的 LaTeXDocument 實例
    """
    # 中文數學文檔的預設配置
    chinese_config = {
        'encoding': 'utf8',
        'font_config': FontConfig(),
        'packages': [
            'fontspec',
            'xeCJK',
            'amsmath',
            'amsfonts',
            'amssymb',
            'geometry'
        ]
    }
    
    # 合併用戶配置
    chinese_config.update(kwargs)
    
    logger.debug(f"創建中文數學文檔: {title}")
    return create_math_document(title, **chinese_config)


def get_latex_info() -> dict:
    """取得 LaTeX 模組資訊
    
    Returns:
        包含模組資訊的字典
    """
    return {
        'module': 'utils.latex',
        'version': __version__,
        'author': __author__,
        'current_engine': global_config.get('latex_engine', 'xelatex'),
        'supported_document_classes': [
            'article', 'report', 'book', 'standalone'
        ],
        'supported_paper_sizes': [
            'A4', 'A3', 'letter', 'legal'
        ],
        'features': [
            'Chinese support',
            'Math environments',
            'TikZ integration',
            'Multiple engines',
            'Error handling',
            'Compilation caching'
        ]
    }


def validate_latex_setup() -> bool:
    """驗證 LaTeX 設置
    
    Returns:
        True 如果設置正確，否則 False
    """
    try:
        # 測試創建編譯器
        compiler = create_latex_compiler()
        logger.info("LaTeX 設置驗證通過")
        return True
        
    except Exception as e:
        logger.error(f"LaTeX 設置驗證失敗: {e}")
        return False


# 模板函數

def get_basic_document_template() -> str:
    """取得基礎文檔模板
    
    Returns:
        LaTeX 文檔模板字符串
    """
    return r"""
\documentclass[12pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage{fontspec}
\usepackage{xeCJK}
\usepackage{amsmath}
\usepackage{amsfonts}
\usepackage{amssymb}
\usepackage{tikz}
\usepackage{geometry}

\geometry{margin=2cm}

\title{{{title}}}
\author{{{author}}}
\date{{\today}}

\begin{{document}}

\maketitle

{content}

\end{{document}}
"""


def get_tikz_figure_template() -> str:
    """取得 TikZ 圖形模板
    
    Returns:
        TikZ 圖形模板字符串
    """
    return r"""
\begin{{tikzpicture}}[scale={scale}]
{tikz_content}
\end{{tikzpicture}}
"""


# 公開 API
__all__ = [
    # 異常類
    'LaTeXError',
    'CompilationError',
    'TemplateError',
    'DocumentStructureError',
    'PackageDependencyError',
    'LaTeXConfigError',
    'LaTeXSyntaxError',
    'FontError',
    
    # 類型和配置
    'PaperSize',
    'FontSize',
    'Encoding',
    'Geometry',
    'DocumentConfig',
    'CompilerConfig',
    'FontConfig',
    'TemplateConfig',
    'LaTeXDocument',
    'CompilationResult',
    
    # 編譯器
    'LaTeXCompiler',
    'quick_compile',
    'compile_file',
    
    # 生成器和結構
    'LaTeXGenerator',
    'LaTeXStructure', 
    'LaTeXConfig',
    
    # 轉義功能
    'escape_latex_text',
    'unescape_latex_text',
    
    # 便利函數
    'create_latex_compiler',
    'create_math_document',
    'create_chinese_math_document',
    'get_latex_info',
    'validate_latex_setup',
    'get_basic_document_template',
    'get_tikz_figure_template',
    
    # 錯誤處理便利函數
    'missing_package_error',
    'invalid_template_error',
    'compilation_timeout_error',
    'invalid_latex_syntax_error'
]