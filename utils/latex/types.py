"""
LaTeX 文檔類型定義

定義 LaTeX 文檔處理相關的數據類型和配置結構。

使用方式：
    from utils.latex.types import DocumentConfig, CompilerConfig, FontConfig
    
    # 創建文檔配置
    doc_config = DocumentConfig(
        document_class="article",
        paper_size="a4paper",
        font_size="12pt"
    )
    
    # 創建編譯器配置
    compiler_config = CompilerConfig(
        engine="xelatex",
        output_directory="./output",
        timeout=30
    )
"""

from typing import Union, List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


# 基本類型別名
LaTeXCode = str                    # LaTeX 代碼
LaTeXCommand = str                 # LaTeX 命令
LaTeXPackage = str                 # LaTeX 包名
LaTeXOption = Union[str, List[str]]  # LaTeX 選項


# 文檔類別
DocumentClass = Union[
    str,  # 自定義類別
    # 標準類別
    'article', 'book', 'report', 'letter', 'beamer'
]

# 編譯引擎
CompilerEngine = Union[
    str,  # 自定義引擎
    'pdflatex', 'xelatex', 'lualatex', 'latex'
]

# 字體系統
FontSystem = Union[
    str,  # 自定義字體系統
    'computer_modern', 'times', 'helvetica', 'palatino', 'chinese'
]


class PaperSize(Enum):
    """紙張尺寸枚舉"""
    A4 = "a4paper"
    A5 = "a5paper"
    LETTER = "letterpaper"
    LEGAL = "legalpaper"
    EXECUTIVE = "executivepaper"


class FontSize(Enum):
    """字體大小枚舉"""
    TINY = "6pt"
    SCRIPT = "7pt"
    FOOTNOTE = "8pt"
    SMALL = "9pt"
    NORMAL = "10pt"
    LARGE = "11pt"
    LARGER = "12pt"
    LARGEST = "14pt"


class Encoding(Enum):
    """編碼枚舉"""
    UTF8 = "utf8"
    LATIN1 = "latin1"
    ASCII = "ascii"


class Geometry(Enum):
    """頁面幾何設置"""
    MARGIN_NORMAL = "margin=2.5cm"
    MARGIN_NARROW = "margin=2cm"
    MARGIN_WIDE = "margin=3cm"
    MARGIN_CUSTOM = "margin={top}cm,bottom={bottom}cm,left={left}cm,right={right}cm"


@dataclass
class DocumentConfig:
    """LaTeX 文檔配置
    
    Attributes:
        document_class: 文檔類別
        paper_size: 紙張尺寸
        font_size: 字體大小
        encoding: 字符編碼
        language: 文檔語言
        geometry: 頁面幾何設置
        packages: 需要的包列表
        custom_commands: 自定義命令
    """
    document_class: DocumentClass = "article"
    paper_size: Union[PaperSize, str] = PaperSize.A4
    font_size: Union[FontSize, str] = FontSize.NORMAL
    encoding: Union[Encoding, str] = Encoding.UTF8
    language: str = "english"
    geometry: Optional[Union[Geometry, str]] = Geometry.MARGIN_NORMAL
    packages: List[Union[str, Tuple[str, List[str]]]] = field(default_factory=list)
    custom_commands: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        """標準化配置參數"""
        # 標準化枚舉值
        if isinstance(self.paper_size, PaperSize):
            self.paper_size = self.paper_size.value
        if isinstance(self.font_size, FontSize):
            self.font_size = self.font_size.value
        if isinstance(self.encoding, Encoding):
            self.encoding = self.encoding.value
        if isinstance(self.geometry, Geometry):
            self.geometry = self.geometry.value


@dataclass
class CompilerConfig:
    """LaTeX 編譯器配置
    
    Attributes:
        engine: 編譯引擎
        output_directory: 輸出目錄
        working_directory: 工作目錄
        timeout: 編譯超時時間（秒）
        max_runs: 最大編譯次數
        quiet_mode: 靜默模式
        draft_mode: 草稿模式
        shell_escape: 允許 shell 轉義
        synctex: 啟用 SyncTeX
        interaction_mode: 交互模式
        extra_options: 額外編譯選項
    """
    engine: CompilerEngine = "xelatex"
    output_directory: Optional[Union[str, Path]] = None
    working_directory: Optional[Union[str, Path]] = None
    timeout: int = 30
    max_runs: int = 3
    quiet_mode: bool = False
    draft_mode: bool = False
    shell_escape: bool = False
    synctex: bool = True
    interaction_mode: str = "nonstopmode"
    extra_options: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """標準化路徑參數"""
        if self.output_directory is not None:
            self.output_directory = Path(self.output_directory)
        if self.working_directory is not None:
            self.working_directory = Path(self.working_directory)


@dataclass
class FontConfig:
    """字體配置
    
    Attributes:
        font_system: 字體系統
        main_font: 主字體
        sans_font: 無襯線字體
        mono_font: 等寬字體
        math_font: 數學字體
        chinese_font: 中文字體
        font_features: 字體特性
    """
    font_system: FontSystem = "computer_modern"
    main_font: Optional[str] = None
    sans_font: Optional[str] = None
    mono_font: Optional[str] = None
    math_font: Optional[str] = None
    chinese_font: Optional[str] = None
    font_features: Dict[str, str] = field(default_factory=dict)


@dataclass
class TemplateConfig:
    """模板配置
    
    Attributes:
        template_name: 模板名稱
        template_path: 模板路徑
        variables: 模板變數
        include_paths: 包含路徑列表
        auto_escape: 自動轉義
    """
    template_name: str
    template_path: Optional[Union[str, Path]] = None
    variables: Dict[str, Any] = field(default_factory=dict)
    include_paths: List[Union[str, Path]] = field(default_factory=list)
    auto_escape: bool = True
    
    def __post_init__(self):
        """標準化路徑參數"""
        if self.template_path is not None:
            self.template_path = Path(self.template_path)
        self.include_paths = [Path(p) for p in self.include_paths]


@dataclass
class CompilationResult:
    """編譯結果
    
    Attributes:
        success: 編譯是否成功
        output_file: 輸出文件路徑
        log_content: 編譯日誌內容
        error_messages: 錯誤信息列表
        warnings: 警告信息列表
        compilation_time: 編譯時間（秒）
        runs_count: 實際編譯次數
    """
    success: bool
    output_file: Optional[Path] = None
    log_content: str = ""
    error_messages: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    compilation_time: float = 0.0
    runs_count: int = 0


@dataclass
class LaTeXDocument:
    """LaTeX 文檔表示
    
    Attributes:
        preamble: 文檔前言
        content: 文檔內容
        config: 文檔配置
        metadata: 文檔元數據
    """
    content: LaTeXCode
    config: DocumentConfig = field(default_factory=DocumentConfig)
    preamble: LaTeXCode = ""
    metadata: Dict[str, str] = field(default_factory=dict)
    
    @property
    def full_document(self) -> str:
        """獲取完整的 LaTeX 文檔代碼"""
        lines = []
        
        # 文檔類別聲明
        class_options = []
        if self.config.paper_size:
            class_options.append(self.config.paper_size)
        if self.config.font_size:
            class_options.append(self.config.font_size)
        
        if class_options:
            lines.append(f"\\documentclass[{','.join(class_options)}]{{{self.config.document_class}}}")
        else:
            lines.append(f"\\documentclass{{{self.config.document_class}}}")
        
        # 編碼設置
        if self.config.encoding:
            lines.append(f"\\usepackage[{self.config.encoding}]{{inputenc}}")
        
        # 語言設置
        if self.config.language != "english":
            lines.append(f"\\usepackage[{self.config.language}]{{babel}}")
        
        # 幾何設置
        if self.config.geometry:
            lines.append(f"\\usepackage[{self.config.geometry}]{{geometry}}")
        
        # 包引入
        for package in self.config.packages:
            if isinstance(package, tuple):
                pkg_name, options = package
                lines.append(f"\\usepackage[{','.join(options)}]{{{pkg_name}}}")
            else:
                lines.append(f"\\usepackage{{{package}}}")
        
        # 自定義命令
        for cmd_name, cmd_def in self.config.custom_commands.items():
            lines.append(f"\\newcommand{{\\{cmd_name}}}{{{cmd_def}}}")
        
        # 前言
        if self.preamble:
            lines.append("")
            lines.append("% 自定義前言")
            lines.append(self.preamble)
        
        # 文檔開始
        lines.append("")
        lines.append("\\begin{document}")
        
        # 文檔內容
        lines.append("")
        lines.append(self.content)
        
        # 文檔結束
        lines.append("")
        lines.append("\\end{document}")
        
        return "\n".join(lines)


# 工具函數

def format_latex_command(command: str, arguments: List[str] = None, options: List[str] = None) -> str:
    """格式化 LaTeX 命令
    
    Args:
        command: 命令名稱（不含反斜線）
        arguments: 命令參數列表
        options: 命令選項列表
        
    Returns:
        格式化的 LaTeX 命令字串
        
    Example:
        >>> format_latex_command("documentclass", ["article"], ["a4paper", "12pt"])
        '\\documentclass[a4paper,12pt]{article}'
    """
    cmd_parts = [f"\\{command}"]
    
    if options:
        cmd_parts.append(f"[{','.join(options)}]")
    
    if arguments:
        for arg in arguments:
            cmd_parts.append(f"{{{arg}}}")
    
    return "".join(cmd_parts)


def escape_latex_text(text: str) -> str:
    """轉義 LaTeX 特殊字符
    
    Args:
        text: 要轉義的文本
        
    Returns:
        轉義後的文本
        
    Example:
        >>> escape_latex_text("Price: $5 & 10%")
        'Price: \\$5 \\& 10\\%'
    """
    # LaTeX 特殊字符映射
    special_chars = {
        '\\': '\\textbackslash{}',
        '{': '\\{',
        '}': '\\}',
        '$': '\\$',
        '&': '\\&',
        '%': '\\%',
        '#': '\\#',
        '^': '\\textasciicircum{}',
        '_': '\\_',
        '~': '\\textasciitilde{}',
    }
    
    for char, replacement in special_chars.items():
        text = text.replace(char, replacement)
    
    return text


def normalize_package_spec(package: Union[str, Tuple[str, List[str]]]) -> Tuple[str, List[str]]:
    """標準化包規範
    
    Args:
        package: 包規範，可以是字串或 (包名, 選項列表) 元組
        
    Returns:
        (包名, 選項列表) 元組
    """
    if isinstance(package, str):
        return package, []
    elif isinstance(package, tuple) and len(package) == 2:
        pkg_name, options = package
        if isinstance(options, str):
            options = [options]
        return pkg_name, options
    else:
        raise ValueError(f"無效的包規範: {package}")


def validate_document_class(doc_class: str) -> bool:
    """驗證文檔類別是否有效
    
    Args:
        doc_class: 文檔類別名稱
        
    Returns:
        是否為有效的文檔類別
    """
    standard_classes = {
        'article', 'book', 'report', 'letter', 'beamer',
        'minimal', 'slides', 'proc', 'standalone'
    }
    
    # 檢查是否為標準類別或包含有效字符的自定義類別
    return (doc_class in standard_classes or 
            (doc_class.isalnum() or '_' in doc_class or '-' in doc_class))