#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - PDF 生成工具
使用 LaTeX 生成 PDF 文件，支持數學公式和自動換頁
"""

import os
import random
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from pprint import pprint

from utils.registry import registry
from utils.layout_engine import LayoutEngine
from utils.latex_generator import LaTeXGenerator
from utils.pdf_compiler import PDFCompiler

# --- 生成 LaTeX PDF ---
def generate_latex_pdfs(output_dir: str, filename_prefix: str, test_title: str,
                        selected_data: List[Dict[str, Any]], rounds: int,
                        questions_per_round: int) -> bool:
    """生成 LaTeX PDF 測驗檔案
    
    Args:
        output_dir: 輸出目錄
        filename_prefix: 文件名前綴
        test_title: 測驗標題
        selected_data: 選定的題型數據，格式為 [{"topic": "題型名稱", "count": 數量}, ...]
        rounds: 回數
        questions_per_round: 每回題數
        
    Returns:
        是否成功生成 PDF
    """
    # 步驟 1: 生成原始題目列表
    raw_questions = _generate_raw_questions(selected_data)
    
    # 步驟 2: 題型分佈與排序
    ordered_questions = _distribute_questions(raw_questions, rounds, questions_per_round)
    
    # 步驟 3: 獲取佈局結果
    layout_engine = LayoutEngine()
    # 傳遞 questions_per_round 參數給 layout 函數
    layout_results = layout_engine.layout(ordered_questions, questions_per_round)
    
    # 步驟 4: 生成 LaTeX 內容
    latex_generator = LaTeXGenerator()
    # 傳遞 questions_per_round 參數給所有生成函數
    question_tex = latex_generator.generate_question_tex(layout_results, test_title, questions_per_round)
    answer_tex = latex_generator.generate_answer_tex(ordered_questions, test_title, questions_per_round)
    explanation_tex = latex_generator.generate_explanation_tex(ordered_questions, test_title, questions_per_round)
    
    # 步驟 5: 編譯 PDF
    pdf_compiler = PDFCompiler()
    
    # 確保輸出目錄存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 編譯題目 PDF
    question_pdf_success = pdf_compiler.compile_tex_to_pdf(
        question_tex, output_dir, f"{filename_prefix}_question"
    )
    
    # 編譯簡答 PDF
    answer_pdf_success = pdf_compiler.compile_tex_to_pdf(
        answer_tex, output_dir, f"{filename_prefix}_answer"
    )
    
    # 編譯詳解 PDF
    explanation_pdf_success = pdf_compiler.compile_tex_to_pdf(
        explanation_tex, output_dir, f"{filename_prefix}_explanation"
    )
    
    # 返回是否全部成功
    return question_pdf_success and answer_pdf_success and explanation_pdf_success

# --- 為了保持向後兼容性，保留原有的函數名稱 ---
def generate_pdf(output_path: str, test_title: str, selected_data: List[Dict[str, Any]],
                 rounds: int, questions_per_round: int, template_name: str = "standard") -> bool:
    """生成 PDF 測驗檔案 (向後兼容函數)
    
    Args:
        output_path: 輸出 PDF 檔案的完整路徑
        test_title: 測驗標題
        selected_data: 選定的題型數據，格式為 [{"topic": "題型名稱", "count": 數量}, ...]
        rounds: 回數
        questions_per_round: 每回題數
        template_name: 模板名稱，預設為 "standard"
        
    Returns:
        是否成功生成 PDF
    """
    # 從 output_path 中提取目錄和文件名前綴
    output_dir = os.path.dirname(output_path)
    if not output_dir:
        output_dir = "."
    
    filename_prefix = os.path.splitext(os.path.basename(output_path))[0]
    
    # 調用新的函數
    return generate_latex_pdfs(output_dir, filename_prefix, test_title,
                              selected_data, rounds, questions_per_round)

# --- 輔助函數 ---
def _generate_raw_questions(selected_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """生成原始題目列表
    
    Args:
        selected_data: 選定的題型數據，格式為 [{"topic": "題型名稱", "count": 數量}, ...]
        
    Returns:
        原始題目列表
    """
    raw_questions = []
    
    # 為每個選定的題型生成題目
    for topic_data in selected_data:
        topic = topic_data["topic"]
        count = topic_data["count"]
        
        # 解析題型名稱，格式為 "類別 - 子類別"
        parts = topic.split(" - ")
        if len(parts) == 2:
            category, subcategory = parts
        else:
            # 對於格式不符的題型，使用預設題目
            for _ in range(count):
                raw_questions.append({
                    "question": f"[格式不符的題型: {topic}]",
                    "answer": "格式不符",
                    "explanation": "題型格式應為 '類別 - 子類別'",
                    "size": 1,  # 使用最小的題目大小
                    "difficulty": "EASY"
                })
            continue
        
        # 從註冊表中獲取生成器
        generator_class = registry.get_generator(category, subcategory)
        
        if generator_class:
            # 創建生成器實例
            generator = generator_class()
            
            # 生成題目
            for _ in range(count):
                raw_questions.append(generator.generate_question())
        else:
            # 對於尚未實現的題型，使用預設題目
            for _ in range(count):
                raw_questions.append({
                    "question": f"[未實現的題型: {topic}]",
                    "answer": "尚未實現",
                    "explanation": "此題型尚未實現生成器",
                    "size": 1,  # 使用最小的題目大小
                    "difficulty": "EASY"
                })
	
	
    return raw_questions

def _distribute_questions(raw_questions: List[Dict[str, Any]], rounds: int,
                         questions_per_round: int) -> List[Dict[str, Any]]:
    """題型分佈與排序
    
    Args:
        raw_questions: 原始題目列表
        rounds: 回數
        questions_per_round: 每回題數
        
    Returns:
        排序後的題目列表
    """
    # 如果題目不夠，複製現有題目
    while len(raw_questions) < rounds * questions_per_round:
        raw_questions.extend(raw_questions[:rounds * questions_per_round - len(raw_questions)])
    
    # 按題型分組
    questions_by_type = {}
    for q in raw_questions:
        # 嘗試從題目中提取更可靠的題型標識
        # 首先檢查是否有 topic 或 category 欄位
        if "topic" in q:
            q_type = q["topic"]
        elif "category" in q:
            q_type = q["category"]
        else:
            # 如果沒有，使用題目內容的前20個字符作為題型標識（比原來的10個更長）
            q_type = q.get("question", "")[:20]
        
        if q_type not in questions_by_type:
            questions_by_type[q_type] = []
        questions_by_type[q_type].append(q)
    
    # 創建代表各回的空列表
    round_questions = [[] for _ in range(rounds)]
    
    # 修改分發邏輯：逐個題目輪流分發，而不是整個題型組
    round_index = 0
    
    # 首先，將每種題型的題目逐個輪流分發到各回
    for q_type, questions in questions_by_type.items():
        for q in questions:
            # 如果當前回已經達到每回題數上限，跳過
            if len(round_questions[round_index]) >= questions_per_round:
                # 嘗試找下一個未滿的回
                original_index = round_index
                found_space = False
                
                # 檢查所有回
                for i in range(rounds):
                    next_index = (round_index + i) % rounds
                    if len(round_questions[next_index]) < questions_per_round:
                        round_index = next_index
                        found_space = True
                        break
                
                # 如果所有回都已滿，停止分發
                if not found_space:
                    break
            
            # 添加題目到當前回
            round_questions[round_index].append(q)
            
            # 更新回索引，輪流到下一回
            round_index = (round_index + 1) % rounds
    
    # 回內按尺寸排序
    for i in range(rounds):
        round_questions[i].sort(key=lambda q: q.get("size", 1))
    
    # 合併結果
    ordered_questions = []
    for round_list in round_questions:
        ordered_questions.extend(round_list)
    
    # 如果題目太多，截斷
    ordered_questions = ordered_questions[:rounds * questions_per_round]
    
    # 確保每回題目數量正確
    if len(ordered_questions) < rounds * questions_per_round:
        print(f"警告：最終題目數量 {len(ordered_questions)} 少於預期的 {rounds * questions_per_round}")
    
    return ordered_questions
