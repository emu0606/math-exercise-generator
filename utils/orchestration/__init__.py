#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
業務協調層模組 - PDF 生成協調器

統一管理 PDF 生成的完整流程，協調各個模組的工作。
"""

# 嘗試導入主要類，忽略不存在的類
try:
    from .pdf_orchestrator import PDFOrchestrator
except ImportError:
    PDFOrchestrator = None

try:
    from .question_distributor import QuestionDistributor, DistributionStrategy
except ImportError:
    QuestionDistributor = None
    DistributionStrategy = None

try:
    from .error_handler import ErrorHandler
except ImportError:
    ErrorHandler = None

try:
    from .progress_reporter import ProgressReporter, ProgressTracker
except ImportError:
    ProgressReporter = None
    ProgressTracker = None

# 版本資訊
__version__ = "1.0.0"
__author__ = "Math Exercise Generator Team"

# 公開接口（僅導出成功導入的類）
__all__ = []

if PDFOrchestrator:
    __all__.append('PDFOrchestrator')
if QuestionDistributor:
    __all__.append('QuestionDistributor')
if DistributionStrategy:
    __all__.append('DistributionStrategy')
if ErrorHandler:
    __all__.append('ErrorHandler')
if ProgressReporter:
    __all__.append('ProgressReporter')
if ProgressTracker:
    __all__.append('ProgressTracker')

# 便利函數
def create_default_orchestrator():
    """創建默認配置的PDF協調器"""
    if PDFOrchestrator:
        return PDFOrchestrator()
    else:
        raise ImportError("PDFOrchestrator無法導入")

def generate_pdf_with_orchestration(output_config, content_config, progress_callback=None):
    """使用協調器生成PDF的便利函數"""
    if not PDFOrchestrator:
        raise ImportError("PDFOrchestrator無法導入")
        
    orchestrator = PDFOrchestrator()
    if progress_callback and ProgressReporter:
        progress_reporter = ProgressReporter(progress_callback)
        orchestrator.set_progress_reporter(progress_reporter)
    
    return orchestrator.generate_pdfs(output_config, content_config)

# 向後兼容函數  
def generate_latex_pdfs(output_config, content_config, progress_callback=None):
    """向後兼容的PDF生成函數
    
    Args:
        output_config: 輸出配置
        content_config: 內容配置
        progress_callback: 進度回調函數
        
    Returns:
        PDF生成結果
    """
    return generate_pdf_with_orchestration(output_config, content_config, progress_callback)