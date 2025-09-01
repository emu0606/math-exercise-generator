#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - LaTeX 工具函數
"""

import io
import matplotlib
import matplotlib.pyplot as plt
from reportlab.lib.utils import ImageReader

def render_latex_to_image(latex_str, fontsize=12, dpi=300):
    """使用matplotlib將LaTeX字符串渲染為圖像
    
    Args:
        latex_str: LaTeX字符串
        fontsize: 字體大小
        dpi: 圖像解析度
        
    Returns:
        reportlab可用的圖像對象
    """
    # 設置matplotlib使用內置數學渲染
    matplotlib.rcParams.update({
        "text.usetex": False,  # 不使用系統LaTeX
        "mathtext.fontset": "cm",  # 使用Computer Modern字體
    })
    
    # 創建一個空白圖像
    fig = plt.figure(figsize=(5, 0.5))
    fig.text(0, 0.4, f"${latex_str}$", fontsize=fontsize)
    
    # 保存為內存中的PNG
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1, transparent=True, dpi=dpi)
    buf.seek(0)
    
    # 關閉圖像以釋放內存
    plt.close(fig)
    
    # 返回reportlab可用的圖像對象
    return ImageReader(buf)

def get_latex_image_size(latex_str, fontsize=12, dpi=300):
    """獲取渲染後的LaTeX圖像大小
    
    Args:
        latex_str: LaTeX字符串
        fontsize: 字體大小
        dpi: 圖像解析度
        
    Returns:
        (寬度, 高度) 元組，單位為點
    """
    # 設置matplotlib使用內置數學渲染
    matplotlib.rcParams.update({
        "text.usetex": False,  # 不使用系統LaTeX
        "mathtext.fontset": "cm",  # 使用Computer Modern字體
    })
    
    # 創建一個空白圖像
    fig = plt.figure(figsize=(5, 0.5))
    fig.text(0, 0.4, f"${latex_str}$", fontsize=fontsize)
    
    # 保存為內存中的PNG
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1, transparent=True, dpi=dpi)
    
    # 獲取圖像大小
    buf.seek(0)
    from PIL import Image
    img = Image.open(buf)
    width, height = img.size
    
    # 關閉圖像以釋放內存
    plt.close(fig)
    img.close()
    
    # 返回大小（轉換為點）
    return width * 72 / dpi, height * 72 / dpi
