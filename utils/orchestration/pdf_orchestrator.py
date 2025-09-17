"""
PDF 生成協調器

統一管理整個 PDF 生成流程，協調各個模組的工作。
從原始 pdf_generator.py 重構而來，提供更清晰的架構和更好的錯誤處理。

主要功能：
- 統一的 PDF 生成接口
- 題目生成和分配協調
- 佈局計算和 LaTeX 生成協調
- 編譯過程管理和錯誤處理
- 進度回報和狀態追蹤

使用方式：
    from utils.orchestration import PDFOrchestrator
    
    orchestrator = PDFOrchestrator()
    result = orchestrator.generate_pdfs(output_config, content_config)
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum

# 導入核心模組
from ..core.config import global_config
from ..core.logging import get_logger
from ..core.layout import LayoutEngine
from ..core.registry import registry

# 導入 LaTeX 模組
from ..latex import LaTeXCompiler, DocumentConfig

# 模組專用日誌器
logger = get_logger(__name__)


class GenerationStage(Enum):
    """PDF 生成階段"""
    INITIALIZING = "initializing"
    GENERATING_QUESTIONS = "generating_questions"
    DISTRIBUTING_QUESTIONS = "distributing_questions"
    CALCULATING_LAYOUT = "calculating_layout"
    GENERATING_LATEX = "generating_latex"
    COMPILING_PDF = "compiling_pdf"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class OutputConfig:
    """輸出配置"""
    output_dir: str
    filename_prefix: str
    generate_questions: bool = True
    generate_answers: bool = True
    generate_explanations: bool = True
    
    def __post_init__(self):
        """確保輸出目錄存在"""
        os.makedirs(self.output_dir, exist_ok=True)


@dataclass
class ContentConfig:
    """內容配置"""
    test_title: str
    selected_data: List[Dict[str, Any]]
    rounds: int
    questions_per_round: int
    template_name: str = "standard"


@dataclass
class GenerationProgress:
    """生成進度"""
    current_stage: GenerationStage
    progress_percent: float
    current_task: str
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            'stage': self.current_stage.value,
            'progress': self.progress_percent,
            'task': self.current_task,
            'error': self.error_message
        }


@dataclass
class PDFGenerationResult:
    """PDF 生成結果"""
    success: bool
    generated_files: List[str]
    error_message: Optional[str] = None
    generation_stats: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """後初始化驗證"""
        if not self.success and not self.error_message:
            self.error_message = "未知錯誤：生成失敗但無錯誤訊息"


class PDFOrchestrator:
    """PDF 生成協調器
    
    統一管理整個 PDF 生成流程的核心類別。
    負責協調題目生成、佈局計算、LaTeX 生成和 PDF 編譯等各個步驟。
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化 PDF 協調器
        
        Args:
            config: 可選的配置字典，會與全域配置合併
        """
        self.config = global_config
        if config:
            self.config.update_multiple(config)
        
        # 初始化各個子系統
        self.layout_engine = LayoutEngine()
        self.latex_compiler = LaTeXCompiler()
        
        # 進度回調
        self.progress_callback: Optional[Callable[[GenerationProgress], None]] = None
        
        logger.info("PDF 協調器初始化完成")
    
    def set_progress_callback(self, callback: Callable[[GenerationProgress], None]):
        """設置進度回調函數
        
        Args:
            callback: 進度回調函數，接收 GenerationProgress 物件
        """
        self.progress_callback = callback
        logger.debug("進度回調函數已設置")
    
    def _report_progress(self, stage: GenerationStage, progress: float, task: str, 
                        error: Optional[str] = None):
        """報告進度
        
        Args:
            stage: 當前階段
            progress: 進度百分比 (0-100)
            task: 當前任務描述
            error: 可選的錯誤訊息
        """
        progress_info = GenerationProgress(stage, progress, task, error)
        
        if self.progress_callback:
            try:
                self.progress_callback(progress_info)
            except Exception as e:
                logger.warning(f"進度回調執行失敗: {e}")
        
        # 記錄到日誌
        if error:
            logger.error(f"{stage.value}: {task} - 錯誤: {error}")
        else:
            logger.info(f"{stage.value}: {task} ({progress:.1f}%)")
    
    def generate_pdfs(self, output_config: OutputConfig, 
                     content_config: ContentConfig) -> PDFGenerationResult:
        """生成 PDF 檔案
        
        統一的 PDF 生成入口點，協調整個生成流程。
        
        Args:
            output_config: 輸出配置
            content_config: 內容配置
            
        Returns:
            PDFGenerationResult 包含生成結果和統計資訊
        """
        logger.info(f"開始 PDF 生成流程：{content_config.test_title}")
        
        try:
            # 階段 1: 初始化
            self._report_progress(GenerationStage.INITIALIZING, 0, "準備生成環境")
            generated_files = []
            stats = {
                'total_questions': 0,
                'generated_files_count': 0,
                'compilation_time': 0
            }
            
            # 階段 2: 生成題目
            self._report_progress(GenerationStage.GENERATING_QUESTIONS, 10, "生成原始題目")
            raw_questions = self._generate_raw_questions(content_config.selected_data)
            stats['total_questions'] = len(raw_questions)
            
            # 階段 3: 分配題目
            self._report_progress(GenerationStage.DISTRIBUTING_QUESTIONS, 20, "分配和排序題目")
            ordered_questions = self._distribute_questions(
                raw_questions, content_config.rounds, content_config.questions_per_round
            )
            
            # 階段 4: 計算佈局
            self._report_progress(GenerationStage.CALCULATING_LAYOUT, 35, "計算頁面佈局")
            layout_results = self.layout_engine.layout(ordered_questions, content_config.questions_per_round)
            
            # 階段 5: 生成 LaTeX
            self._report_progress(GenerationStage.GENERATING_LATEX, 50, "生成 LaTeX 內容")
            latex_contents = self._generate_latex_contents(
                layout_results, ordered_questions, content_config
            )
            
            # 階段 6: 編譯 PDF
            self._report_progress(GenerationStage.COMPILING_PDF, 70, "編譯 PDF 檔案")
            compilation_results = self._compile_pdfs(
                latex_contents, output_config, content_config
            )
            
            # 收集結果
            generated_files = compilation_results['files']
            stats['generated_files_count'] = len(generated_files)
            stats['compilation_time'] = compilation_results['total_time']
            
            # 完成
            self._report_progress(GenerationStage.COMPLETED, 100, "PDF 生成完成")
            
            return PDFGenerationResult(
                success=True,
                generated_files=generated_files,
                generation_stats=stats
            )
            
        except Exception as e:
            error_msg = f"PDF 生成失敗: {str(e)}"
            self._report_progress(GenerationStage.FAILED, 0, "生成失敗", error_msg)
            logger.error(error_msg, exc_info=True)
            
            return PDFGenerationResult(
                success=False,
                generated_files=[],
                error_message=error_msg
            )
    
    def _generate_raw_questions(self, selected_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成原始題目列表
        
        Args:
            selected_data: 選定的題型數據
            
        Returns:
            原始題目列表
        """
        from .question_distributor import generate_raw_questions
        return generate_raw_questions(selected_data)
    
    def _distribute_questions(self, raw_questions: List[Dict[str, Any]], 
                            rounds: int, questions_per_round: int) -> List[Dict[str, Any]]:
        """分配和排序題目
        
        Args:
            raw_questions: 原始題目列表
            rounds: 回合數
            questions_per_round: 每回合題目數
            
        Returns:
            排序後的題目列表
        """
        from .question_distributor import distribute_questions
        return distribute_questions(raw_questions, rounds, questions_per_round)
    
    def _generate_latex_contents(self, layout_results: Any, ordered_questions: List[Dict[str, Any]], 
                               content_config: ContentConfig) -> Dict[str, str]:
        """生成 LaTeX 內容
        
        Args:
            layout_results: 佈局結果
            ordered_questions: 排序後的題目
            content_config: 內容配置
            
        Returns:
            包含各種 LaTeX 內容的字典
        """
        from ..latex.generator import LaTeXGenerator
        
        latex_generator = LaTeXGenerator()
        
        contents = {}
        
        # 生成題目 LaTeX
        contents['questions'] = latex_generator.generate_question_tex(
            layout_results, content_config.test_title, content_config.questions_per_round
        )
        
        # 生成答案 LaTeX
        contents['answers'] = latex_generator.generate_answer_tex(
            layout_results, content_config.test_title, content_config.questions_per_round
        )
        
        # 生成詳解 LaTeX
        contents['explanations'] = latex_generator.generate_explanation_tex(
            layout_results, content_config.test_title, content_config.questions_per_round
        )
        
        return contents
    
    def _compile_pdfs(self, latex_contents: Dict[str, str], output_config: OutputConfig, 
                     content_config: ContentConfig) -> Dict[str, Any]:
        """編譯 PDF 檔案
        
        Args:
            latex_contents: LaTeX 內容字典
            output_config: 輸出配置
            content_config: 內容配置
            
        Returns:
            編譯結果字典
        """
        import time
        import os
        import subprocess
        from pathlib import Path
        
        generated_files = []
        start_time = time.time()
        
        # 編譯題目 PDF
        if output_config.generate_questions and 'questions' in latex_contents:
            success = self._simple_compile_tex_to_pdf(
                latex_contents['questions'], 
                output_config.output_dir, 
                f"{output_config.filename_prefix}_question"
            )
            if success:
                generated_files.append(f"{output_config.filename_prefix}_question.pdf")
        
        # 編譯答案 PDF
        if output_config.generate_answers and 'answers' in latex_contents:
            success = self._simple_compile_tex_to_pdf(
                latex_contents['answers'], 
                output_config.output_dir, 
                f"{output_config.filename_prefix}_answer"
            )
            if success:
                generated_files.append(f"{output_config.filename_prefix}_answer.pdf")
        
        # 編譯詳解 PDF
        if output_config.generate_explanations and 'explanations' in latex_contents:
            success = self._simple_compile_tex_to_pdf(
                latex_contents['explanations'], 
                output_config.output_dir, 
                f"{output_config.filename_prefix}_explanation"
            )
            if success:
                generated_files.append(f"{output_config.filename_prefix}_explanation.pdf")
        
        total_time = time.time() - start_time
        
        return {
            'files': generated_files,
            'total_time': total_time
        }

    def _simple_compile_tex_to_pdf(self, tex_content: str, output_dir: str, filename: str) -> bool:
        """簡化的LaTeX編譯器 - 基於成功經驗的穩定實現
        
        Args:
            tex_content: 完整的LaTeX文檔內容
            output_dir: 輸出目錄路徑
            filename: 文件名（不含副檔名）
            
        Returns:
            編譯是否成功
        """
        try:
            # 1. 確保輸出目錄存在
            os.makedirs(output_dir, exist_ok=True)
            
            # 2. 寫入.tex文件到輸出目錄
            tex_path = os.path.join(output_dir, f"{filename}.tex")
            with open(tex_path, 'w', encoding='utf-8') as f:
                f.write(tex_content)
                
            print(f"LaTeX文件已寫入: {tex_path}")
            
            # 3. 在輸出目錄執行編譯 (關鍵：在同一目錄操作)
            import subprocess
            compile_result = subprocess.run([
                'xelatex', 
                '-interaction=nonstopmode',
                f'{filename}.tex'
            ], 
            cwd=output_dir,  # 在目標目錄執行
            capture_output=True, 
            text=True,
            timeout=60
            )
            
            # 4. 檢查PDF是否成功生成
            pdf_path = os.path.join(output_dir, f"{filename}.pdf")
            success = os.path.exists(pdf_path)
            
            if success:
                print(f"PDF編譯成功: {pdf_path}")
            else:
                print(f"PDF編譯失敗: {filename}")
                if compile_result.stdout:
                    print(f"編譯輸出: {compile_result.stdout[:500]}...")  # 限制輸出長度
                if compile_result.stderr:
                    print(f"編譯錯誤: {compile_result.stderr[:500]}...")
            
            # 5. 保留.tex文件供檢視 (不清理)
            print(f"LaTeX文件已保留: {tex_path}")
            
            return success
            
        except subprocess.TimeoutExpired:
            print(f"編譯超時: {filename}")
            return False
        except Exception as e:
            print(f"編譯過程異常: {filename}, 錯誤: {e}")
            return False


# 便利函數 - 向後相容接口

def generate_latex_pdfs(output_dir: str, filename_prefix: str, test_title: str,
                       selected_data: List[Dict[str, Any]], rounds: int,
                       questions_per_round: int) -> bool:
    """生成 LaTeX PDF 測驗檔案 (向後相容函數)
    
    這是對原始 pdf_generator.generate_latex_pdfs 的包裝，
    使用新的 PDFOrchestrator 實現。
    
    Args:
        output_dir: 輸出目錄
        filename_prefix: 文件名前綴
        test_title: 測驗標題
        selected_data: 選定的題型數據
        rounds: 回數
        questions_per_round: 每回題數
        
    Returns:
        是否成功生成 PDF
    """
    try:
        # 創建配置
        output_config = OutputConfig(
            output_dir=output_dir,
            filename_prefix=filename_prefix
        )
        
        content_config = ContentConfig(
            test_title=test_title,
            selected_data=selected_data,
            rounds=rounds,
            questions_per_round=questions_per_round
        )
        
        # 使用協調器生成 PDF
        orchestrator = PDFOrchestrator()
        result = orchestrator.generate_pdfs(output_config, content_config)
        
        return result.success
        
    except Exception as e:
        logger.error(f"PDF 生成失敗: {e}")
        return False


def generate_pdf_with_progress(output_path: str, test_title: str, 
                              selected_data: List[Dict[str, Any]],
                              rounds: int, questions_per_round: int,
                              progress_callback: Optional[Callable] = None,
                              template_name: str = "standard") -> bool:
    """帶進度回報的 PDF 生成函數
    
    Args:
        output_path: 輸出路徑
        test_title: 測驗標題
        selected_data: 題型數據
        rounds: 回合數
        questions_per_round: 每回合題目數
        progress_callback: 進度回調函數
        template_name: 模板名稱
        
    Returns:
        是否成功生成
    """
    try:
        # 解析輸出路徑
        output_dir = os.path.dirname(output_path)
        filename_prefix = os.path.splitext(os.path.basename(output_path))[0]
        
        # 創建配置
        output_config = OutputConfig(
            output_dir=output_dir,
            filename_prefix=filename_prefix
        )
        
        content_config = ContentConfig(
            test_title=test_title,
            selected_data=selected_data,
            rounds=rounds,
            questions_per_round=questions_per_round,
            template_name=template_name
        )
        
        # 創建協調器並設置進度回調
        orchestrator = PDFOrchestrator()
        if progress_callback:
            orchestrator.set_progress_callback(progress_callback)
        
        # 生成 PDF
        result = orchestrator.generate_pdfs(output_config, content_config)
        
        return result.success
        
    except Exception as e:
        logger.error(f"帶進度的 PDF 生成失敗: {e}")
        if progress_callback:
            error_progress = GenerationProgress(
                GenerationStage.FAILED, 0, "生成失敗", str(e)
            )
            progress_callback(error_progress)
        return False


# 工廠函數

def create_pdf_orchestrator(config: Optional[Dict[str, Any]] = None) -> PDFOrchestrator:
    """創建 PDF 協調器實例
    
    Args:
        config: 可選配置
        
    Returns:
        PDFOrchestrator 實例
    """
    logger.debug("創建 PDF 協調器")
    return PDFOrchestrator(config)


def create_output_config(output_dir: str, filename_prefix: str, **kwargs) -> OutputConfig:
    """創建輸出配置
    
    Args:
        output_dir: 輸出目錄
        filename_prefix: 檔案名前綴
        **kwargs: 其他配置選項
        
    Returns:
        OutputConfig 實例
    """
    return OutputConfig(
        output_dir=output_dir,
        filename_prefix=filename_prefix,
        **kwargs
    )


def create_content_config(test_title: str, selected_data: List[Dict[str, Any]], 
                         rounds: int, questions_per_round: int, **kwargs) -> ContentConfig:
    """創建內容配置
    
    Args:
        test_title: 測驗標題
        selected_data: 題型數據
        rounds: 回合數
        questions_per_round: 每回合題目數
        **kwargs: 其他配置選項
        
    Returns:
        ContentConfig 實例
    """
    return ContentConfig(
        test_title=test_title,
        selected_data=selected_data,
        rounds=rounds,
        questions_per_round=questions_per_round,
        **kwargs
    )


# 模組資訊
__version__ = "1.0.0"
__author__ = "Math Exercise Generator Team"

logger.debug(f"PDF 協調器模組載入完成: {__version__}")