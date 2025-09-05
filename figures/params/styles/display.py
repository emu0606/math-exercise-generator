#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 顯示配置參數

此模組定義了圖形顯示和視覺效果的配置模型，包括弧線樣式、
填充效果、線條樣式和整體顯示控制。這些配置模型提供了
細緻的視覺外觀控制，支援創建專業的數學圖形。

主要組件：
1. **弧線樣式配置**: 角度弧線和圓弧的外觀控制
2. **填充樣式配置**: 圖形內部填充效果和透明度
3. **線條樣式配置**: 線條粗細、顏色和樣式模式
4. **顯示控制配置**: 圖形元素的顯示開關和模式

設計特點：
- 分離視覺樣式與幾何參數
- 支援樣式配置的組合和重用
- 與 TikZ 渲染系統深度整合
- 提供豐富的預設樣式選項

Example:
    創建弧線樣式配置::
    
        from figures.params.styles.display import ArcStyleConfig
        
        arc_style = ArcStyleConfig(
            draw_options='thick, blue',
            line_width='1.2pt',
            dash_pattern='5pt,3pt'
        )
        
    配置填充效果::
    
        from figures.params.styles.display import FillStyleConfig
        
        fill_style = FillStyleConfig(
            fill_color='lightblue',
            fill_opacity=0.3,
            pattern='north east lines'
        )

Note:
    - 樣式配置獨立於具體圖形參數
    - 支援 TikZ 的所有樣式選項
    - 可以組合使用創建複雜效果
    - 提供預設配置確保基本可用性
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Literal, Union

class ArcStyleConfig(BaseModel):
    """弧線樣式配置模型
    
    定義角度弧線和圓弧的視覺樣式，包括線條屬性、
    顏色和特殊效果。用於統一管理弧線的外觀設定。
    
    Attributes:
        draw_options (Optional[str]): TikZ 繪製選項字串
        line_width (Optional[str]): 線條粗細，如 '1pt', 'thick', 'ultra thin'
        color (Optional[str]): 弧線顏色
        dash_pattern (Optional[str]): 虛線模式，如 '5pt,3pt'
        opacity (Optional[float]): 線條透明度，範圍 0-1
        arrow_style (Optional[str]): 箭頭樣式，如 '->', '<->', '|-|'
        
    Example:
        創建粗藍色弧線::
        
            arc_style = ArcStyleConfig(
                draw_options='thick, blue',
                line_width='2pt',
                opacity=0.8
            )
            
        創建虛線弧線::
        
            dashed_arc = ArcStyleConfig(
                color='red',
                dash_pattern='3pt,2pt',
                arrow_style='->'
            )
            
    Note:
        - draw_options 會覆蓋其他單獨設定的選項
        - 支援所有 TikZ 線條樣式
        - None 值使用 TikZ 預設設定
    """
    draw_options: Optional[str] = Field(default="thin", description="TikZ 繪製選項")
    line_width: Optional[str] = Field(default=None, description="線條粗細")
    color: Optional[str] = Field(default=None, description="弧線顏色")
    dash_pattern: Optional[str] = Field(default=None, description="虛線模式")
    opacity: Optional[float] = Field(default=None, ge=0, le=1, description="線條透明度")
    arrow_style: Optional[str] = Field(default=None, description="箭頭樣式")

class FillStyleConfig(BaseModel):
    """填充樣式配置模型
    
    定義圖形內部填充的視覺效果，包括純色填充、
    漸變效果、圖案填充和透明度控制。
    
    Attributes:
        fill_color (Optional[str]): 填充顏色
        fill_opacity (Optional[float]): 填充透明度，範圍 0-1
        pattern (Optional[str]): 填充圖案，如 'north east lines', 'dots'
        gradient_type (Optional[Literal]): 漸變類型
        gradient_colors (Optional[list]): 漸變顏色列表
        draw_border (bool): 是否繪製邊框
        border_color (Optional[str]): 邊框顏色
        border_width (Optional[str]): 邊框粗細
        
    Example:
        創建半透明藍色填充::
        
            fill_style = FillStyleConfig(
                fill_color='lightblue',
                fill_opacity=0.5,
                draw_border=True,
                border_color='blue'
            )
            
        創建條紋圖案填充::
        
            pattern_fill = FillStyleConfig(
                pattern='north east lines',
                fill_opacity=0.3,
                border_width='thick'
            )
    """
    fill_color: Optional[str] = Field(default=None, description="填充顏色")
    fill_opacity: Optional[float] = Field(default=None, ge=0, le=1, description="填充透明度")
    pattern: Optional[str] = Field(default=None, description="填充圖案")
    gradient_type: Optional[Literal['linear', 'radial', 'angular']] = Field(
        default=None, description="漸變類型"
    )
    gradient_colors: Optional[list] = Field(default=None, description="漸變顏色列表")
    draw_border: bool = Field(default=True, description="是否繪製邊框")
    border_color: Optional[str] = Field(default=None, description="邊框顏色")
    border_width: Optional[str] = Field(default=None, description="邊框粗細")

class LineStyleConfig(BaseModel):
    """線條樣式配置模型
    
    定義直線、曲線和邊框的視覺樣式，包括粗細、
    顏色、線型和端點樣式等屬性。
    
    Attributes:
        color (Optional[str]): 線條顏色
        width (Optional[str]): 線條粗細
        style (Optional[Literal]): 線條樣式模式
        dash_pattern (Optional[str]): 自定義虛線模式
        opacity (Optional[float]): 線條透明度
        cap_style (Optional[Literal]): 線條端點樣式
        join_style (Optional[Literal]): 線條連接樣式
        arrow_start (Optional[str]): 起點箭頭樣式
        arrow_end (Optional[str]): 終點箭頭樣式
        
    Example:
        創建粗紅色實線::
        
            line_style = LineStyleConfig(
                color='red',
                width='thick',
                style='solid',
                cap_style='round'
            )
            
        創建帶箭頭的虛線::
        
            arrow_line = LineStyleConfig(
                color='blue',
                style='dashed',
                arrow_end='stealth',
                opacity=0.8
            )
    """
    color: Optional[str] = Field(default=None, description="線條顏色")
    width: Optional[str] = Field(default=None, description="線條粗細")
    style: Optional[Literal['solid', 'dashed', 'dotted', 'dash dot', 'custom']] = Field(
        default=None, description="線條樣式"
    )
    dash_pattern: Optional[str] = Field(default=None, description="自定義虛線模式")
    opacity: Optional[float] = Field(default=None, ge=0, le=1, description="線條透明度")
    cap_style: Optional[Literal['round', 'rect', 'butt']] = Field(
        default=None, description="線條端點樣式"
    )
    join_style: Optional[Literal['round', 'bevel', 'miter']] = Field(
        default=None, description="線條連接樣式"
    )
    arrow_start: Optional[str] = Field(default=None, description="起點箭頭樣式")
    arrow_end: Optional[str] = Field(default=None, description="終點箭頭樣式")

class DisplayControlConfig(BaseModel):
    """顯示控制配置模型
    
    定義圖形元素的顯示開關和模式控制，用於精確
    控制哪些元素在特定情況下應該顯示或隱藏。
    
    Attributes:
        show_construction_lines (bool): 是否顯示輔助線
        show_measurements (bool): 是否顯示測量數值
        show_labels (bool): 是否顯示標籤
        show_grid (bool): 是否顯示背景網格
        show_axes (bool): 是否顯示座標軸
        highlight_elements (Optional[list]): 需要高亮的元素列表
        fade_elements (Optional[list]): 需要淡化的元素列表
        animation_mode (Optional[str]): 動畫模式（未來擴展）
        
    Example:
        創建教學模式顯示配置::
        
            display_config = DisplayControlConfig(
                show_construction_lines=True,
                show_measurements=True,
                show_labels=True,
                show_grid=True,
                highlight_elements=['main_triangle']
            )
            
        創建簡潔模式配置::
        
            minimal_config = DisplayControlConfig(
                show_construction_lines=False,
                show_measurements=False,
                show_grid=False,
                fade_elements=['auxiliary_lines']
            )
    """
    show_construction_lines: bool = Field(default=False, description="是否顯示輔助線")
    show_measurements: bool = Field(default=False, description="是否顯示測量數值")
    show_labels: bool = Field(default=True, description="是否顯示標籤")
    show_grid: bool = Field(default=False, description="是否顯示背景網格")
    show_axes: bool = Field(default=False, description="是否顯示座標軸")
    highlight_elements: Optional[list] = Field(default=None, description="高亮元素列表")
    fade_elements: Optional[list] = Field(default=None, description="淡化元素列表")
    animation_mode: Optional[str] = Field(default=None, description="動畫模式")

class ColorSchemeConfig(BaseModel):
    """色彩方案配置模型
    
    定義統一的色彩方案，用於確保圖形中各元素
    顏色的協調性和一致性。支援預定義主題和
    自定義色彩組合。
    
    Attributes:
        primary_color (str): 主要顏色
        secondary_color (str): 次要顏色
        accent_color (str): 強調顏色
        background_color (str): 背景顏色
        text_color (str): 文字顏色
        grid_color (str): 網格顏色
        construction_color (str): 輔助線顏色
        highlight_color (str): 高亮顏色
        theme_name (Optional[str]): 主題名稱
        
    Example:
        創建藍色主題::
        
            blue_scheme = ColorSchemeConfig(
                primary_color='blue',
                secondary_color='lightblue',
                accent_color='darkblue',
                text_color='navy',
                theme_name='Blue Academic'
            )
            
        創建單色主題::
        
            mono_scheme = ColorSchemeConfig(
                primary_color='black',
                secondary_color='gray',
                accent_color='darkgray',
                highlight_color='red',
                theme_name='Monochrome'
            )
    """
    primary_color: str = Field(default='blue', description="主要顏色")
    secondary_color: str = Field(default='lightblue', description="次要顏色")
    accent_color: str = Field(default='red', description="強調顏色")
    background_color: str = Field(default='white', description="背景顏色")
    text_color: str = Field(default='black', description="文字顏色")
    grid_color: str = Field(default='lightgray', description="網格顏色")
    construction_color: str = Field(default='gray', description="輔助線顏色")
    highlight_color: str = Field(default='orange', description="高亮顏色")
    theme_name: Optional[str] = Field(default=None, description="主題名稱")

class RenderingConfig(BaseModel):
    """渲染配置模型
    
    定義圖形渲染的技術參數，包括解析度、品質
    設定和輸出格式控制。用於優化不同用途的
    圖形輸出效果。
    
    Attributes:
        dpi (Optional[int]): 輸出解析度（點每英寸）
        quality (Literal): 渲染品質等級
        anti_aliasing (bool): 是否啟用抗鋸齒
        vector_output (bool): 是否輸出向量格式
        compression_level (Optional[int]): 壓縮等級（0-9）
        optimization_mode (Optional[str]): 優化模式
        
    Example:
        高品質輸出配置::
        
            hq_config = RenderingConfig(
                dpi=300,
                quality='high',
                anti_aliasing=True,
                vector_output=True
            )
            
        快速預覽配置::
        
            preview_config = RenderingConfig(
                dpi=150,
                quality='draft',
                compression_level=5,
                optimization_mode='speed'
            )
    """
    dpi: Optional[int] = Field(default=150, gt=0, description="輸出解析度")
    quality: Literal['draft', 'normal', 'high', 'ultra'] = Field(
        default='normal', description="渲染品質"
    )
    anti_aliasing: bool = Field(default=True, description="抗鋸齒")
    vector_output: bool = Field(default=True, description="向量輸出")
    compression_level: Optional[int] = Field(default=None, ge=0, le=9, description="壓縮等級")
    optimization_mode: Optional[str] = Field(default=None, description="優化模式")

class StylePresets:
    """樣式預設集合
    
    提供常用的顯示樣式預設配置，方便快速應用
    統一的視覺風格。包含教學和專業用途的各種
    預設組合。
    
    預設樣式：
    - ACADEMIC: 學術風格
    - TEXTBOOK: 教科書風格
    - PRESENTATION: 演示風格
    - MINIMAL: 簡約風格
    - COLORFUL: 彩色風格
    """
    
    ACADEMIC = {
        'line_style': LineStyleConfig(
            color='black',
            width='thick',
            style='solid'
        ),
        'fill_style': FillStyleConfig(
            fill_color='lightgray',
            fill_opacity=0.2,
            border_color='black'
        ),
        'color_scheme': ColorSchemeConfig(
            primary_color='black',
            secondary_color='gray',
            accent_color='red',
            theme_name='Academic'
        )
    }
    
    TEXTBOOK = {
        'line_style': LineStyleConfig(
            color='blue',
            width='thick',
            style='solid'
        ),
        'fill_style': FillStyleConfig(
            fill_color='lightblue',
            fill_opacity=0.3,
            border_color='blue'
        ),
        'color_scheme': ColorSchemeConfig(
            primary_color='blue',
            secondary_color='lightblue',
            accent_color='red',
            theme_name='Textbook'
        )
    }
    
    PRESENTATION = {
        'line_style': LineStyleConfig(
            color='darkblue',
            width='ultra thick',
            style='solid'
        ),
        'fill_style': FillStyleConfig(
            fill_color='yellow',
            fill_opacity=0.4,
            border_color='darkblue'
        ),
        'color_scheme': ColorSchemeConfig(
            primary_color='darkblue',
            secondary_color='yellow',
            accent_color='red',
            theme_name='Presentation'
        )
    }
    
    MINIMAL = {
        'line_style': LineStyleConfig(
            color='black',
            width='thin',
            style='solid'
        ),
        'fill_style': FillStyleConfig(
            fill_opacity=0.0,
            draw_border=True,
            border_color='black'
        ),
        'color_scheme': ColorSchemeConfig(
            primary_color='black',
            secondary_color='white',
            accent_color='gray',
            theme_name='Minimal'
        )
    }