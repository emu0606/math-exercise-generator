"""
LaTeX 編譯異常定義

定義 LaTeX 文檔編譯過程中可能遇到的各種異常情況，提供清晰的錯誤分類。

使用方式：
    from utils.latex.exceptions import LaTeXError, CompilationError
    
    try:
        result = compile_document(latex_content)
    except CompilationError as e:
        logger.error(f"LaTeX 編譯錯誤: {e}")
    except LaTeXError as e:
        logger.error(f"LaTeX 處理錯誤: {e}")
"""

from typing import Any, Optional, Dict, List
from ..geometry.exceptions import GeometryError


class LaTeXError(GeometryError):
    """LaTeX 處理基礎異常類
    
    所有 LaTeX 相關異常的基類，繼承自 GeometryError。
    """
    pass


class CompilationError(LaTeXError):
    """LaTeX 編譯錯誤
    
    當 LaTeX 文檔編譯過程中遇到問題時拋出。
    """
    
    def __init__(self, reason: str, latex_code: str = "", compile_log: str = "", **context):
        """初始化編譯錯誤
        
        Args:
            reason: 編譯失敗的原因
            latex_code: 導致錯誤的 LaTeX 代碼
            compile_log: 編譯器日誌
            **context: 編譯上下文資訊
        """
        message = f"LaTeX 編譯錯誤: {reason}"
        details = {
            'reason': reason,
            'latex_code': latex_code[:500] + "..." if len(latex_code) > 500 else latex_code,
            'compile_log': compile_log[:1000] + "..." if len(compile_log) > 1000 else compile_log,
            **context
        }
        super().__init__(message, details)
        self.reason = reason
        self.latex_code = latex_code
        self.compile_log = compile_log
        self.context = context


class TemplateError(LaTeXError):
    """LaTeX 模板錯誤
    
    當 LaTeX 模板解析或應用時遇到問題時拋出。
    """
    
    def __init__(self, template_name: str, reason: str, **context):
        """初始化模板錯誤
        
        Args:
            template_name: 模板名稱
            reason: 錯誤原因
            **context: 相關上下文
        """
        message = f"LaTeX 模板錯誤 ({template_name}): {reason}"
        details = {
            'template_name': template_name,
            'reason': reason,
            **context
        }
        super().__init__(message, details)
        self.template_name = template_name
        self.reason = reason
        self.context = context


class DocumentStructureError(LaTeXError):
    """LaTeX 文檔結構錯誤
    
    當文檔結構不正確時拋出。
    """
    
    def __init__(self, structure_issue: str, reason: str, **context):
        """初始化文檔結構錯誤
        
        Args:
            structure_issue: 結構問題類型
            reason: 錯誤原因
            **context: 相關上下文
        """
        message = f"LaTeX 文檔結構錯誤 ({structure_issue}): {reason}"
        details = {
            'structure_issue': structure_issue,
            'reason': reason,
            **context
        }
        super().__init__(message, details)
        self.structure_issue = structure_issue
        self.reason = reason
        self.context = context


class PackageDependencyError(LaTeXError):
    """LaTeX 包依賴錯誤
    
    當所需的 LaTeX 包不可用時拋出。
    """
    
    def __init__(self, package_name: str, reason: str, **context):
        """初始化包依賴錯誤
        
        Args:
            package_name: 包名稱
            reason: 不可用原因
            **context: 相關上下文
        """
        message = f"LaTeX 包依賴錯誤 ({package_name}): {reason}"
        details = {
            'package_name': package_name,
            'reason': reason,
            **context
        }
        super().__init__(message, details)
        self.package_name = package_name
        self.reason = reason
        self.context = context


class LaTeXConfigError(LaTeXError):
    """LaTeX 配置錯誤
    
    當 LaTeX 處理配置參數不正確時拋出。
    """
    
    def __init__(self, config_key: str, value: Any, expected: str):
        """初始化配置錯誤
        
        Args:
            config_key: 配置項名稱
            value: 錯誤的配置值
            expected: 期望的配置值描述
        """
        message = f"LaTeX 配置錯誤: {config_key} = {value}，期望: {expected}"
        details = {
            'config_key': config_key,
            'value': str(value),
            'expected': expected
        }
        super().__init__(message, details)
        self.config_key = config_key
        self.value = value
        self.expected = expected


class LaTeXSyntaxError(LaTeXError):
    """LaTeX 語法錯誤
    
    當生成的 LaTeX 代碼語法不正確時拋出。
    """
    
    def __init__(self, latex_code: str, error_position: Optional[int] = None, reason: str = "語法錯誤"):
        """初始化語法錯誤
        
        Args:
            latex_code: 出錯的 LaTeX 代碼
            error_position: 錯誤位置（可選）
            reason: 錯誤原因
        """
        message = f"LaTeX 語法錯誤: {reason}"
        details = {
            'latex_code': latex_code[:500] + "..." if len(latex_code) > 500 else latex_code,
            'error_position': error_position,
            'reason': reason
        }
        super().__init__(message, details)
        self.latex_code = latex_code
        self.error_position = error_position
        self.reason = reason


class FontError(LaTeXError):
    """LaTeX 字體錯誤
    
    當字體相關問題時拋出。
    """
    
    def __init__(self, font_issue: str, reason: str, **context):
        """初始化字體錯誤
        
        Args:
            font_issue: 字體問題類型
            reason: 錯誤原因
            **context: 相關上下文
        """
        message = f"LaTeX 字體錯誤 ({font_issue}): {reason}"
        details = {
            'font_issue': font_issue,
            'reason': reason,
            **context
        }
        super().__init__(message, details)
        self.font_issue = font_issue
        self.reason = reason
        self.context = context


# 便利函數：快速創建常見異常

def missing_package_error(package_name: str, context: str = "") -> PackageDependencyError:
    """創建缺失包異常
    
    Args:
        package_name: 缺失的包名稱
        context: 額外的上下文描述
        
    Returns:
        PackageDependencyError 實例
    """
    reason = f"LaTeX 包 '{package_name}' 未安裝或不可用"
    if context:
        reason += f" ({context})"
    return PackageDependencyError(package_name, reason)


def invalid_template_error(template_name: str, issue: str, context: str = "") -> TemplateError:
    """創建無效模板異常
    
    Args:
        template_name: 模板名稱
        issue: 模板問題
        context: 額外的上下文描述
        
    Returns:
        TemplateError 實例
    """
    reason = f"模板問題: {issue}"
    if context:
        reason += f" ({context})"
    return TemplateError(template_name, reason)


def compilation_timeout_error(timeout_seconds: int) -> CompilationError:
    """創建編譯超時異常
    
    Args:
        timeout_seconds: 超時秒數
        
    Returns:
        CompilationError 實例
    """
    reason = f"編譯超時 ({timeout_seconds} 秒)"
    return CompilationError(reason, timeout=timeout_seconds)


def invalid_latex_syntax_error(code_snippet: str, position: int = None) -> LaTeXSyntaxError:
    """創建無效 LaTeX 語法異常
    
    Args:
        code_snippet: 錯誤的代碼片段
        position: 錯誤位置
        
    Returns:
        LaTeXSyntaxError 實例
    """
    return LaTeXSyntaxError(code_snippet, position, "無效的 LaTeX 語法")