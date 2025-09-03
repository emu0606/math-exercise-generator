#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 統一錯誤處理
負責處理整個 PDF 生成流程中的錯誤和異常
"""

import traceback
from typing import Dict, List, Any, Optional, Union
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

class ErrorSeverity(Enum):
    """錯誤嚴重程度"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ErrorType(Enum):
    """錯誤類型"""
    QUESTION_GENERATION = "question_generation"
    LAYOUT_ENGINE = "layout_engine"
    LATEX_GENERATION = "latex_generation"
    PDF_COMPILATION = "pdf_compilation"
    FILE_IO = "file_io"
    VALIDATION = "validation"
    CONFIGURATION = "configuration"

@dataclass
class ErrorInfo:
    """錯誤信息結構"""
    error_type: ErrorType
    severity: ErrorSeverity
    message: str
    details: Optional[str] = None
    timestamp: Optional[datetime] = None
    traceback_info: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class OrchestrationError(Exception):
    """協調器通用錯誤"""
    def __init__(self, message: str, error_type: ErrorType = ErrorType.CONFIGURATION, 
                 details: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.error_type = error_type
        self.details = details
        self.context = context

class QuestionGenerationError(OrchestrationError):
    """題目生成錯誤"""
    def __init__(self, message: str, details: Optional[str] = None, 
                 context: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorType.QUESTION_GENERATION, details, context)

class LayoutError(OrchestrationError):
    """佈局錯誤"""
    def __init__(self, message: str, details: Optional[str] = None, 
                 context: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorType.LAYOUT_ENGINE, details, context)

class LaTeXGenerationError(OrchestrationError):
    """LaTeX 生成錯誤"""
    def __init__(self, message: str, details: Optional[str] = None, 
                 context: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorType.LATEX_GENERATION, details, context)

class PDFCompilationError(OrchestrationError):
    """PDF 編譯錯誤"""
    def __init__(self, message: str, details: Optional[str] = None, 
                 context: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorType.PDF_COMPILATION, details, context)

class ErrorHandler:
    """統一錯誤處理器
    
    負責收集、處理和報告整個 PDF 生成流程中的錯誤。
    提供統一的錯誤格式和處理策略。
    """
    
    def __init__(self, debug_mode: bool = False):
        """初始化錯誤處理器
        
        Args:
            debug_mode: 是否啟用詳細調試信息
        """
        self.debug_mode = debug_mode
        self.errors: List[ErrorInfo] = []
        self.warnings: List[ErrorInfo] = []
    
    def handle_error(self, error: Union[Exception, str], error_type: ErrorType,
                    severity: ErrorSeverity = ErrorSeverity.ERROR,
                    context: Optional[Dict[str, Any]] = None) -> ErrorInfo:
        """處理錯誤
        
        Args:
            error: 錯誤對象或錯誤消息
            error_type: 錯誤類型
            severity: 錯誤嚴重程度
            context: 錯誤上下文信息
            
        Returns:
            錯誤信息對象
        """
        if isinstance(error, Exception):
            message = str(error)
            details = None
            traceback_info = traceback.format_exc() if self.debug_mode else None
        else:
            message = error
            details = None
            traceback_info = None
        
        error_info = ErrorInfo(
            error_type=error_type,
            severity=severity,
            message=message,
            details=details,
            traceback_info=traceback_info,
            context=context
        )
        
        if severity in [ErrorSeverity.ERROR, ErrorSeverity.CRITICAL]:
            self.errors.append(error_info)
        elif severity == ErrorSeverity.WARNING:
            self.warnings.append(error_info)
        
        return error_info
    
    def handle_question_generation_error(self, error: Union[Exception, str],
                                       context: Optional[Dict[str, Any]] = None) -> ErrorInfo:
        """處理題目生成錯誤"""
        return self.handle_error(error, ErrorType.QUESTION_GENERATION, 
                               ErrorSeverity.ERROR, context)
    
    def handle_layout_error(self, error: Union[Exception, str],
                          context: Optional[Dict[str, Any]] = None) -> ErrorInfo:
        """處理佈局錯誤"""
        return self.handle_error(error, ErrorType.LAYOUT_ENGINE, 
                               ErrorSeverity.ERROR, context)
    
    def handle_latex_error(self, error: Union[Exception, str],
                         context: Optional[Dict[str, Any]] = None) -> ErrorInfo:
        """處理 LaTeX 生成錯誤"""
        return self.handle_error(error, ErrorType.LATEX_GENERATION, 
                               ErrorSeverity.ERROR, context)
    
    def handle_pdf_compilation_error(self, error: Union[Exception, str],
                                   context: Optional[Dict[str, Any]] = None) -> ErrorInfo:
        """處理 PDF 編譯錯誤"""
        return self.handle_error(error, ErrorType.PDF_COMPILATION, 
                               ErrorSeverity.CRITICAL, context)
    
    def handle_file_io_error(self, error: Union[Exception, str],
                           context: Optional[Dict[str, Any]] = None) -> ErrorInfo:
        """處理文件 I/O 錯誤"""
        return self.handle_error(error, ErrorType.FILE_IO, 
                               ErrorSeverity.ERROR, context)
    
    def handle_validation_error(self, error: Union[Exception, str],
                              context: Optional[Dict[str, Any]] = None) -> ErrorInfo:
        """處理驗證錯誤"""
        return self.handle_error(error, ErrorType.VALIDATION, 
                               ErrorSeverity.WARNING, context)
    
    def add_warning(self, message: str, error_type: ErrorType = ErrorType.CONFIGURATION,
                   context: Optional[Dict[str, Any]] = None) -> ErrorInfo:
        """添加警告信息"""
        return self.handle_error(message, error_type, ErrorSeverity.WARNING, context)
    
    def has_errors(self) -> bool:
        """檢查是否有錯誤"""
        return len(self.errors) > 0
    
    def has_critical_errors(self) -> bool:
        """檢查是否有嚴重錯誤"""
        return any(err.severity == ErrorSeverity.CRITICAL for err in self.errors)
    
    def get_error_summary(self) -> Dict[str, Any]:
        """獲取錯誤摘要"""
        return {
            "total_errors": len(self.errors),
            "total_warnings": len(self.warnings),
            "critical_errors": len([e for e in self.errors if e.severity == ErrorSeverity.CRITICAL]),
            "error_types": list(set(err.error_type.value for err in self.errors)),
            "has_critical": self.has_critical_errors()
        }
    
    def format_errors(self, include_traceback: bool = False) -> str:
        """格式化錯誤報告
        
        Args:
            include_traceback: 是否包含堆疊追蹤信息
            
        Returns:
            格式化的錯誤報告字符串
        """
        if not self.errors and not self.warnings:
            return "無錯誤或警告"
        
        lines = []
        
        if self.warnings:
            lines.append(f"警告 ({len(self.warnings)}):")
            for warning in self.warnings:
                lines.append(f"  [{warning.error_type.value}] {warning.message}")
                if warning.details and self.debug_mode:
                    lines.append(f"    詳細: {warning.details}")
            lines.append("")
        
        if self.errors:
            lines.append(f"錯誤 ({len(self.errors)}):")
            for error in self.errors:
                severity_marker = "🔴" if error.severity == ErrorSeverity.CRITICAL else "⚠️"
                lines.append(f"  {severity_marker} [{error.error_type.value}] {error.message}")
                if error.details and self.debug_mode:
                    lines.append(f"    詳細: {error.details}")
                if error.traceback_info and include_traceback:
                    lines.append(f"    堆疊追蹤:\n{error.traceback_info}")
        
        return "\n".join(lines)
    
    def clear(self):
        """清除所有錯誤和警告"""
        self.errors.clear()
        self.warnings.clear()
    
    def get_errors_by_type(self, error_type: ErrorType) -> List[ErrorInfo]:
        """按類型獲取錯誤"""
        return [err for err in self.errors if err.error_type == error_type]
    
    def get_latest_error(self) -> Optional[ErrorInfo]:
        """獲取最新錯誤"""
        return self.errors[-1] if self.errors else None