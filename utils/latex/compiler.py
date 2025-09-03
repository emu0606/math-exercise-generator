"""
LaTeX 編譯器

實現 LaTeX 文檔編譯功能，支持多種編譯引擎和配置選項。
從原始 geometry_utils.py 重構而來，提供更強大的編譯控制。

主要功能：
- 支持多種 LaTeX 引擎：XeLaTeX、PDFLaTeX、LuaLaTeX
- 編譯過程監控和錯誤處理
- 自動處理多次編譯需求
- 編譯日誌解析和錯誤提取

使用方式：
    from utils.latex.compiler import LaTeXCompiler
    from utils.latex.types import CompilerConfig, LaTeXDocument
    
    compiler = LaTeXCompiler()
    result = compiler.compile_document(document, config)
    
    if result.success:
        print(f"編譯成功: {result.output_file}")
    else:
        print(f"編譯失敗: {result.error_messages}")
"""

import subprocess
import time
import re
import tempfile
import shutil
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
from contextlib import contextmanager

from .types import (
    CompilerConfig, LaTeXDocument, CompilationResult,
    CompilerEngine
)
from .exceptions import (
    CompilationError, LaTeXConfigError, PackageDependencyError,
    compilation_timeout_error
)
from ..core.logging import get_logger

# 模組專用日誌器
logger = get_logger(__name__)


class LaTeXCompiler:
    """LaTeX 編譯器
    
    負責處理 LaTeX 文檔的編譯過程，包括引擎選擇、參數配置、
    錯誤處理和結果解析。
    """
    
    def __init__(self, config: Optional[CompilerConfig] = None):
        """初始化編譯器
        
        Args:
            config: 編譯器配置，如果未提供則使用預設值
        """
        self.config = config or CompilerConfig()
        self._validate_config()
        logger.debug(f"初始化 LaTeX 編譯器，引擎: {self.config.engine}")
    
    def compile_document(self, 
                        document: LaTeXDocument,
                        output_name: str = "document",
                        config_override: Optional[CompilerConfig] = None) -> CompilationResult:
        """編譯 LaTeX 文檔
        
        Args:
            document: 要編譯的 LaTeX 文檔
            output_name: 輸出文件名（不含副檔名）
            config_override: 臨時覆蓋的配置
            
        Returns:
            編譯結果物件
            
        Raises:
            CompilationError: 當編譯過程失敗時
        """
        # 使用覆蓋配置或預設配置
        compile_config = config_override or self.config
        
        logger.info(f"開始編譯 LaTeX 文檔: {output_name}")
        start_time = time.time()
        
        try:
            with self._create_temp_workspace() as workspace:
                # 準備文件
                tex_file = workspace / f"{output_name}.tex"
                tex_file.write_text(document.full_document, encoding='utf-8')
                
                # 執行編譯
                result = self._compile_with_engine(
                    tex_file, compile_config, workspace
                )
                
                # 複製輸出文件到目標目錄
                if result.success and compile_config.output_directory:
                    self._copy_output_files(
                        workspace, compile_config.output_directory, output_name
                    )
                
                result.compilation_time = time.time() - start_time
                
                if result.success:
                    logger.info(f"編譯成功，耗時: {result.compilation_time:.2f}s")
                else:
                    logger.error(f"編譯失敗，錯誤: {result.error_messages}")
                
                return result
                
        except Exception as e:
            compilation_time = time.time() - start_time
            if isinstance(e, CompilationError):
                raise
            else:
                raise CompilationError(
                    f"編譯過程異常: {str(e)}",
                    latex_code=document.content[:200] + "...",
                    compilation_time=compilation_time
                ) from e
    
    def compile_from_file(self,
                         tex_file: Path,
                         config_override: Optional[CompilerConfig] = None) -> CompilationResult:
        """從文件編譯 LaTeX 文檔
        
        Args:
            tex_file: LaTeX 源文件路徑
            config_override: 臨時覆蓋的配置
            
        Returns:
            編譯結果物件
        """
        if not tex_file.exists():
            raise CompilationError(f"LaTeX 文件不存在: {tex_file}")
        
        # 讀取文檔內容
        try:
            content = tex_file.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            content = tex_file.read_text(encoding='latin1')
        
        # 創建文檔物件（簡化版，不解析配置）
        from .types import DocumentConfig
        document = LaTeXDocument(
            content=content,
            config=DocumentConfig()
        )
        
        return self.compile_document(
            document, 
            tex_file.stem,
            config_override
        )
    
    def check_engine_availability(self, engine: CompilerEngine) -> bool:
        """檢查編譯引擎是否可用
        
        Args:
            engine: 編譯引擎名稱
            
        Returns:
            引擎是否可用
        """
        try:
            result = subprocess.run(
                [engine, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            available = result.returncode == 0
            
            if available:
                logger.debug(f"編譯引擎 {engine} 可用")
            else:
                logger.warning(f"編譯引擎 {engine} 不可用")
            
            return available
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning(f"編譯引擎 {engine} 不可用或無回應")
            return False
    
    def get_available_engines(self) -> List[str]:
        """獲取所有可用的編譯引擎
        
        Returns:
            可用引擎列表
        """
        engines_to_check = ['xelatex', 'pdflatex', 'lualatex', 'latex']
        available = []
        
        for engine in engines_to_check:
            if self.check_engine_availability(engine):
                available.append(engine)
        
        logger.debug(f"可用的編譯引擎: {available}")
        return available
    
    @contextmanager
    def _create_temp_workspace(self):
        """創建臨時工作空間"""
        temp_dir = tempfile.mkdtemp(prefix="latex_compile_")
        workspace = Path(temp_dir)
        
        try:
            logger.debug(f"創建臨時工作空間: {workspace}")
            yield workspace
        finally:
            # 清理臨時目錄
            try:
                shutil.rmtree(workspace)
                logger.debug(f"清理臨時工作空間: {workspace}")
            except Exception as e:
                logger.warning(f"清理臨時工作空間失敗: {e}")
    
    def _compile_with_engine(self,
                           tex_file: Path,
                           config: CompilerConfig,
                           workspace: Path) -> CompilationResult:
        """使用指定引擎編譯文檔
        
        Args:
            tex_file: LaTeX 源文件
            config: 編譯配置
            workspace: 工作空間目錄
            
        Returns:
            編譯結果
        """
        result = CompilationResult(success=False)
        
        for run_num in range(1, config.max_runs + 1):
            logger.debug(f"執行第 {run_num} 次編譯")
            
            # 構建編譯命令
            cmd = self._build_compile_command(tex_file, config, workspace)
            
            # 執行編譯
            run_result = self._execute_compile_command(cmd, config, workspace)
            
            result.runs_count = run_num
            result.log_content += f"\n=== Run {run_num} ===\n" + run_result['log']
            
            if not run_result['success']:
                result.error_messages.extend(run_result['errors'])
                break
            
            # 檢查是否需要再次編譯
            if not self._needs_rerun(run_result['log']) or run_num == config.max_runs:
                result.success = True
                # 設置輸出文件路徑
                pdf_file = workspace / f"{tex_file.stem}.pdf"
                if pdf_file.exists():
                    result.output_file = pdf_file
                break
        
        # 解析警告信息
        result.warnings = self._extract_warnings(result.log_content)
        
        return result
    
    def _build_compile_command(self,
                             tex_file: Path,
                             config: CompilerConfig,
                             workspace: Path) -> List[str]:
        """構建編譯命令
        
        Args:
            tex_file: LaTeX 源文件
            config: 編譯配置
            workspace: 工作空間目錄
            
        Returns:
            編譯命令列表
        """
        cmd = [config.engine]
        
        # 基本選項
        cmd.extend([
            f"-interaction={config.interaction_mode}",
            f"-output-directory={workspace}",
        ])
        
        # 可選選項
        if config.shell_escape:
            cmd.append("-shell-escape")
        
        if config.synctex:
            cmd.append("-synctex=1")
        
        if config.draft_mode:
            cmd.append("-draftmode")
        
        # 額外選項
        cmd.extend(config.extra_options)
        
        # 源文件
        cmd.append(str(tex_file))
        
        logger.debug(f"編譯命令: {' '.join(cmd)}")
        return cmd
    
    def _execute_compile_command(self,
                               cmd: List[str],
                               config: CompilerConfig,
                               workspace: Path) -> Dict[str, Any]:
        """執行編譯命令
        
        Args:
            cmd: 編譯命令
            config: 編譯配置
            workspace: 工作空間目錄
            
        Returns:
            執行結果字典
        """
        try:
            result = subprocess.run(
                cmd,
                cwd=workspace,
                capture_output=True,
                text=True,
                timeout=config.timeout,
                encoding='utf-8',
                errors='replace'
            )
            
            log_content = result.stdout + result.stderr
            success = result.returncode == 0
            errors = self._extract_errors(log_content) if not success else []
            
            return {
                'success': success,
                'log': log_content,
                'errors': errors,
                'return_code': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            raise compilation_timeout_error(config.timeout)
        
        except Exception as e:
            raise CompilationError(f"執行編譯命令失敗: {str(e)}")
    
    def _needs_rerun(self, log_content: str) -> bool:
        """檢查是否需要重新編譯
        
        Args:
            log_content: 編譯日誌內容
            
        Returns:
            是否需要重新編譯
        """
        rerun_patterns = [
            r"Label\(s\) may have changed\. Rerun to get cross-references right\.",
            r"There were undefined references\.",
            r"Rerun to get cross-references right\.",
            r"Table widths have changed\. Rerun LaTeX\.",
            r"Rerun LaTeX\."
        ]
        
        for pattern in rerun_patterns:
            if re.search(pattern, log_content):
                logger.debug("檢測到需要重新編譯的標記")
                return True
        
        return False
    
    def _extract_errors(self, log_content: str) -> List[str]:
        """從編譯日誌中提取錯誤信息
        
        Args:
            log_content: 編譯日誌內容
            
        Returns:
            錯誤信息列表
        """
        errors = []
        
        # 匹配 LaTeX 錯誤模式
        error_patterns = [
            r"! (.+)",  # 一般錯誤
            r"Error: (.+)",  # 明確標記的錯誤
            r"Fatal error: (.+)",  # 致命錯誤
            r"Emergency stop",  # 緊急停止
        ]
        
        for pattern in error_patterns:
            matches = re.findall(pattern, log_content, re.MULTILINE)
            errors.extend(matches)
        
        # 去重並清理
        errors = list(set(error for error in errors if error.strip()))
        
        return errors
    
    def _extract_warnings(self, log_content: str) -> List[str]:
        """從編譯日誌中提取警告信息
        
        Args:
            log_content: 編譯日誌內容
            
        Returns:
            警告信息列表
        """
        warnings = []
        
        # 匹配 LaTeX 警告模式
        warning_patterns = [
            r"Warning: (.+)",
            r"LaTeX Warning: (.+)",
            r"Package \w+ Warning: (.+)",
        ]
        
        for pattern in warning_patterns:
            matches = re.findall(pattern, log_content, re.MULTILINE)
            warnings.extend(matches)
        
        # 去重並清理
        warnings = list(set(warning.strip() for warning in warnings if warning.strip()))
        
        return warnings
    
    def _copy_output_files(self,
                          workspace: Path,
                          output_dir: Path,
                          base_name: str) -> None:
        """複製輸出文件到目標目錄
        
        Args:
            workspace: 工作空間目錄
            output_dir: 輸出目錄
            base_name: 基本檔名
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 需要複製的文件類型
        file_extensions = ['.pdf', '.log', '.aux', '.synctex.gz']
        
        for ext in file_extensions:
            src_file = workspace / f"{base_name}{ext}"
            if src_file.exists():
                dst_file = output_dir / f"{base_name}{ext}"
                shutil.copy2(src_file, dst_file)
                logger.debug(f"複製文件: {src_file} -> {dst_file}")
    
    def _validate_config(self) -> None:
        """驗證編譯器配置"""
        if not self.check_engine_availability(self.config.engine):
            raise LaTeXConfigError(
                "compiler_engine",
                self.config.engine,
                f"可用的編譯引擎: {', '.join(self.get_available_engines())}"
            )
        
        if self.config.timeout <= 0:
            raise LaTeXConfigError(
                "timeout",
                self.config.timeout,
                "正整數（秒）"
            )
        
        if self.config.max_runs <= 0 or self.config.max_runs > 10:
            raise LaTeXConfigError(
                "max_runs",
                self.config.max_runs,
                "1 到 10 之間的整數"
            )


# 便利函數

def quick_compile(latex_code: str, 
                 output_name: str = "document",
                 engine: str = "xelatex") -> CompilationResult:
    """快速編譯 LaTeX 代碼
    
    Args:
        latex_code: LaTeX 代碼
        output_name: 輸出檔名
        engine: 編譯引擎
        
    Returns:
        編譯結果
        
    Example:
        >>> result = quick_compile("\\documentclass{article}\\begin{document}Hello\\end{document}")
        >>> print(result.success)
        True
    """
    from .types import DocumentConfig
    
    document = LaTeXDocument(
        content=latex_code,
        config=DocumentConfig()
    )
    
    compiler = LaTeXCompiler(CompilerConfig(engine=engine))
    return compiler.compile_document(document, output_name)


def compile_file(tex_file: Path, 
                engine: str = "xelatex",
                output_dir: Optional[Path] = None) -> CompilationResult:
    """編譯 LaTeX 文件
    
    Args:
        tex_file: LaTeX 文件路徑
        engine: 編譯引擎
        output_dir: 輸出目錄
        
    Returns:
        編譯結果
    """
    config = CompilerConfig(
        engine=engine,
        output_directory=output_dir
    )
    
    compiler = LaTeXCompiler(config)
    return compiler.compile_from_file(tex_file)