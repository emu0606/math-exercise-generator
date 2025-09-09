#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - PDF 編譯器
將 LaTeX 內容編譯為 PDF 文件
"""

import os
import tempfile
import subprocess
import shutil
from typing import List, Optional, Tuple

class PDFCompiler:
    """PDF 編譯器
    
    將 LaTeX 內容編譯為 PDF 文件。
    使用 xelatex 編譯 LaTeX 文件，支持中文和數學公式。
    """
    
    def __init__(self, project_root: Optional[str] = None):
        """初始化 PDF 編譯器
        
        Args:
            project_root: 專案根目錄路徑。如果為 None，則使用當前工作目錄。
        """
        self.project_root = project_root if project_root else os.getcwd()
        print(f"PDFCompiler initialized with project_root: {self.project_root}") # 添加日誌確認路徑
    
    def compile_tex_to_pdf(self, tex_content: str, output_dir: str, output_filename: str) -> bool:
        """編譯 LaTeX 內容為 PDF 文件
        
        Args:
            tex_content: LaTeX 文件內容
            output_dir: 輸出目錄
            output_filename: 輸出文件名（不含副檔名）
            
        Returns:
            是否成功編譯
        """
        # 確保輸出目錄存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 創建臨時目錄
        with tempfile.TemporaryDirectory() as temp_dir:
            # 寫入 LaTeX 文件
            tex_file_path = os.path.join(temp_dir, f"{output_filename}.tex")
            if not self._write_tex_file(tex_content, tex_file_path):
                return False
            
            # 先複製 TEX 文件到輸出目錄 (無論編譯成功與否都會保存)
            output_tex_path = os.path.join(output_dir, f"{output_filename}.tex")
            try:
                shutil.copy2(tex_file_path, output_tex_path)
                print(f"TEX 文件已複製：{output_tex_path}")
            except Exception as e:
                print(f"複製 TEX 文件時發生錯誤：{e}")
                # 即使TEX檔案複製失敗，我們仍然嘗試編譯PDF
            
            
            # 編譯 LaTeX 文件
            # 傳遞 project_root 給 _run_xelatex
            if not self._run_xelatex(tex_file_path, temp_dir, self.project_root):
                return False
            
            # 複製 PDF 文件到輸出目錄
            pdf_file_path = os.path.join(temp_dir, f"{output_filename}.pdf")
            output_pdf_path = os.path.join(output_dir, f"{output_filename}.pdf")
            
            try:
                shutil.copy2(pdf_file_path, output_pdf_path)
                print(f"PDF 文件已生成：{output_pdf_path}")
                return True
            except Exception as e:
                print(f"複製 PDF 文件時發生錯誤：{e}")
                return False
    
    def _write_tex_file(self, tex_content: str, file_path: str) -> bool:
        """寫入 LaTeX 文件
        
        Args:
            tex_content: LaTeX 文件內容
            file_path: 文件路徑
            
        Returns:
            是否成功寫入
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(tex_content)
            return True
        except Exception as e:
            print(f"寫入 LaTeX 文件時發生錯誤：{e}")
            return False
    
    def _run_xelatex(self, tex_file_path: str, working_dir: str, project_root: str) -> bool:
        """運行 xelatex 編譯 LaTeX 文件
        
        Args:
            tex_file_path: LaTeX 文件絕對路徑 (在臨時目錄中)
            working_dir: 臨時目錄路徑，用於存放輸出文件
            project_root: 專案根目錄，作為 xelatex 的工作目錄
            
        Returns:
            是否成功編譯
        """
        try:
            # 運行 xelatex 命令
            # 使用 project_root 作為 cwd，並指定輸出目錄到 working_dir
            command = [
                "xelatex",
                "-interaction=nonstopmode",
                f"-output-directory={working_dir}", # 指定輸出目錄
                tex_file_path # 使用絕對路徑指向臨時目錄中的 tex 文件
            ]
            print(f"Running command: {' '.join(command)}") # 打印執行的命令
            print(f"Working directory (cwd): {project_root}") # 打印工作目錄
            
            process = subprocess.run(
                command,
                cwd=project_root, # 在專案根目錄執行
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            # 檢查編譯結果
            if process.returncode != 0:
                print("編譯 LaTeX 文件時發生錯誤：")
                print(process.stderr)
                
                # 檢查日誌文件
                log_file = os.path.splitext(tex_file_path)[0] + ".log"
                if os.path.exists(log_file):
                    try:
                        with open(log_file, 'r', encoding='utf-8') as f:
                            log_content = f.read()
                            # 尋找錯誤信息
                            error_lines = []
                            for line in log_content.split('\n'):
                                if "Error" in line or "Fatal" in line:
                                    error_lines.append(line)
                            
                            if error_lines:
                                print("錯誤詳情：")
                                for line in error_lines:
                                    print(line)
                    except Exception as e:
                        print(f"讀取日誌文件時發生錯誤：{e}")
                
                return False
            
            return True
        except Exception as e:
            print(f"運行 xelatex 時發生錯誤：{e}")
            return False
    
    def cleanup_temp_files(self, base_path: str) -> None:
        """清理臨時文件
        
        Args:
            base_path: 基礎路徑（不含副檔名）
        """
        # 臨時文件副檔名列表
        temp_extensions = ['.aux', '.log', '.out', '.toc', '.lof', '.lot', '.fls', '.fdb_latexmk']
        
        for ext in temp_extensions:
            temp_file = base_path + ext
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception as e:
                    print(f"刪除臨時文件 {temp_file} 時發生錯誤：{e}")