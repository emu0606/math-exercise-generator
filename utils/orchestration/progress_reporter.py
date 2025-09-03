#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 進度回報器
負責報告整個 PDF 生成流程的進度
"""

from typing import Dict, List, Any, Optional, Callable
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta

class ProgressStage(Enum):
    """進度階段"""
    INITIALIZING = "initializing"
    GENERATING_QUESTIONS = "generating_questions"
    DISTRIBUTING_QUESTIONS = "distributing_questions"
    CALCULATING_LAYOUT = "calculating_layout"
    GENERATING_LATEX = "generating_latex"
    COMPILING_PDF = "compiling_pdf"
    FINALIZING = "finalizing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class ProgressInfo:
    """進度信息結構"""
    stage: ProgressStage
    current_step: int
    total_steps: int
    message: str
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None
    
    @property
    def progress_percentage(self) -> float:
        """計算進度百分比"""
        if self.total_steps == 0:
            return 0.0
        return (self.current_step / self.total_steps) * 100.0

class ProgressReporter:
    """進度回報器
    
    負責跟蹤和報告整個 PDF 生成流程的進度。
    支持回調函數和詳細的進度信息。
    """
    
    def __init__(self, callback: Optional[Callable[[ProgressInfo], None]] = None,
                 verbose: bool = False):
        """初始化進度回報器
        
        Args:
            callback: 進度更新回調函數
            verbose: 是否啟用詳細輸出
        """
        self.callback = callback
        self.verbose = verbose
        self.start_time: Optional[datetime] = None
        self.current_stage = ProgressStage.INITIALIZING
        self.progress_history: List[ProgressInfo] = []
        self.stage_start_times: Dict[ProgressStage, datetime] = {}
    
    def start(self, total_steps: int = 100):
        """開始進度跟蹤
        
        Args:
            total_steps: 總步驟數
        """
        self.start_time = datetime.now()
        self.total_steps = total_steps
        self.current_step = 0
        self.progress_history.clear()
        self.stage_start_times.clear()
        
        self.update_progress(ProgressStage.INITIALIZING, 0, "開始生成 PDF...")
    
    def update_progress(self, stage: ProgressStage, step: int, message: str,
                       details: Optional[Dict[str, Any]] = None):
        """更新進度
        
        Args:
            stage: 當前階段
            step: 當前步驟
            message: 進度消息
            details: 額外詳細信息
        """
        # 記錄階段開始時間
        if stage != self.current_stage:
            self.stage_start_times[stage] = datetime.now()
            self.current_stage = stage
        
        self.current_step = step
        
        progress_info = ProgressInfo(
            stage=stage,
            current_step=step,
            total_steps=self.total_steps,
            message=message,
            timestamp=datetime.now(),
            details=details
        )
        
        self.progress_history.append(progress_info)
        
        # 輸出進度信息
        if self.verbose:
            self._print_progress(progress_info)
        
        # 調用回調函數
        if self.callback:
            try:
                self.callback(progress_info)
            except Exception as e:
                # 回調函數錯誤不應影響主流程
                if self.verbose:
                    print(f"進度回調錯誤: {e}")
    
    def update_step(self, step: int, message: str, details: Optional[Dict[str, Any]] = None):
        """更新當前階段的步驟
        
        Args:
            step: 當前步驟
            message: 進度消息
            details: 額外詳細信息
        """
        self.update_progress(self.current_stage, step, message, details)
    
    def next_stage(self, stage: ProgressStage, message: str, 
                  details: Optional[Dict[str, Any]] = None):
        """移動到下一個階段
        
        Args:
            stage: 新的階段
            message: 階段消息
            details: 額外詳細信息
        """
        # 計算新的步驟數（基於階段進展）
        stage_progress = self._calculate_stage_progress(stage)
        self.update_progress(stage, stage_progress, message, details)
    
    def complete(self, message: str = "PDF 生成完成"):
        """標記為完成
        
        Args:
            message: 完成消息
        """
        self.update_progress(ProgressStage.COMPLETED, self.total_steps, message)
    
    def fail(self, message: str, details: Optional[Dict[str, Any]] = None):
        """標記為失敗
        
        Args:
            message: 失敗消息
            details: 額外詳細信息
        """
        self.update_progress(ProgressStage.FAILED, self.current_step, message, details)
    
    def get_elapsed_time(self) -> Optional[timedelta]:
        """獲取已耗費時間"""
        if self.start_time is None:
            return None
        return datetime.now() - self.start_time
    
    def get_stage_duration(self, stage: ProgressStage) -> Optional[timedelta]:
        """獲取特定階段的持續時間"""
        if stage not in self.stage_start_times:
            return None
        
        start_time = self.stage_start_times[stage]
        if stage == self.current_stage:
            return datetime.now() - start_time
        
        # 找到該階段的結束時間
        stage_index = list(ProgressStage).index(stage)
        next_stages = list(ProgressStage)[stage_index + 1:]
        
        for next_stage in next_stages:
            if next_stage in self.stage_start_times:
                return self.stage_start_times[next_stage] - start_time
        
        # 如果沒有找到後續階段，使用最後一個進度記錄的時間
        if self.progress_history:
            return self.progress_history[-1].timestamp - start_time
        
        return datetime.now() - start_time
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """獲取進度摘要"""
        elapsed = self.get_elapsed_time()
        
        summary = {
            "current_stage": self.current_stage.value,
            "progress_percentage": self.progress_history[-1].progress_percentage if self.progress_history else 0.0,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "elapsed_time_seconds": elapsed.total_seconds() if elapsed else 0,
            "is_completed": self.current_stage == ProgressStage.COMPLETED,
            "is_failed": self.current_stage == ProgressStage.FAILED,
            "total_progress_updates": len(self.progress_history)
        }
        
        # 添加階段持續時間
        stage_durations = {}
        for stage in ProgressStage:
            duration = self.get_stage_duration(stage)
            if duration:
                stage_durations[stage.value] = duration.total_seconds()
        summary["stage_durations"] = stage_durations
        
        return summary
    
    def get_latest_progress(self) -> Optional[ProgressInfo]:
        """獲取最新進度信息"""
        return self.progress_history[-1] if self.progress_history else None
    
    def _calculate_stage_progress(self, stage: ProgressStage) -> int:
        """根據階段計算進度步驟數"""
        stage_mapping = {
            ProgressStage.INITIALIZING: 5,
            ProgressStage.GENERATING_QUESTIONS: 20,
            ProgressStage.DISTRIBUTING_QUESTIONS: 35,
            ProgressStage.CALCULATING_LAYOUT: 50,
            ProgressStage.GENERATING_LATEX: 70,
            ProgressStage.COMPILING_PDF: 90,
            ProgressStage.FINALIZING: 95,
            ProgressStage.COMPLETED: 100,
            ProgressStage.FAILED: self.current_step  # 保持當前步驟
        }
        return stage_mapping.get(stage, self.current_step)
    
    def _print_progress(self, progress_info: ProgressInfo):
        """打印進度信息"""
        percentage = progress_info.progress_percentage
        elapsed = self.get_elapsed_time()
        elapsed_str = f" ({elapsed.total_seconds():.1f}s)" if elapsed else ""
        
        print(f"[{percentage:5.1f}%] {progress_info.stage.value}: {progress_info.message}{elapsed_str}")
        
        if progress_info.details and self.verbose:
            for key, value in progress_info.details.items():
                print(f"  {key}: {value}")

class ProgressTracker:
    """進度追蹤器
    
    簡化的進度追蹤接口，用於在代碼中方便地報告進度。
    """
    
    def __init__(self, reporter: ProgressReporter, stage: ProgressStage, 
                 step_range: tuple = (0, 100)):
        """初始化進度追蹤器
        
        Args:
            reporter: 進度回報器
            stage: 當前階段
            step_range: 步驟範圍 (start, end)
        """
        self.reporter = reporter
        self.stage = stage
        self.start_step, self.end_step = step_range
        self.current_substep = 0
        self.total_substeps = 1
    
    def set_total_substeps(self, total: int):
        """設置子步驟總數"""
        self.total_substeps = max(1, total)
        self.current_substep = 0
    
    def update(self, substep: int, message: str, details: Optional[Dict[str, Any]] = None):
        """更新子步驟進度"""
        self.current_substep = substep
        
        # 計算在整體進度中的位置
        substep_progress = substep / self.total_substeps
        current_step = int(self.start_step + (self.end_step - self.start_step) * substep_progress)
        
        self.reporter.update_progress(self.stage, current_step, message, details)
    
    def next_substep(self, message: str, details: Optional[Dict[str, Any]] = None):
        """移動到下一個子步驟"""
        self.current_substep += 1
        self.update(self.current_substep, message, details)
    
    def complete(self, message: str, details: Optional[Dict[str, Any]] = None):
        """完成當前階段"""
        self.update(self.total_substeps, message, details)

def create_progress_callback(verbose: bool = True) -> Callable[[ProgressInfo], None]:
    """創建標準進度回調函數
    
    Args:
        verbose: 是否啟用詳細輸出
        
    Returns:
        進度回調函數
    """
    def callback(progress_info: ProgressInfo):
        if verbose:
            percentage = progress_info.progress_percentage
            print(f"[{percentage:5.1f}%] {progress_info.message}")
    
    return callback