#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 標籤樣式參數

此模組定義了標籤和文字相關的樣式配置模型，提供細緻的
文字外觀控制和定位選項。支援 LaTeX 數學模式、字體設定、
顏色配置和高級 TikZ 樣式功能。

主要組件：
1. **標籤樣式配置**: 文字外觀和格式控制
2. **點標籤樣式**: 點圖形專用的標籤配置
3. **頂點顯示配置**: 多邊形頂點的標籤管理
4. **邊標籤配置**: 線段和邊的標籤樣式

設計特點：
- 分離樣式配置與具體參數
- 支援樣式的重用和組合
- 與 TikZ 系統深度整合
- 靈活的覆蓋和繼承機制

Example:
    創建數學公式標籤樣式::
    
        from figures.params.styles.labels import LabelStyleConfig
        
        math_style = LabelStyleConfig(
            color='blue',
            font_size=r'\\large',
            math_mode=True,
            anchor='center',
            position_modifiers='above=0.2cm'
        )
        
    配置頂點顯示樣式::
    
        from figures.params.styles.labels import VertexDisplayConfig
        
        vertex_config = VertexDisplayConfig(
            show_label=True,
            label_style=LabelStyleConfig(
                color='red',
                font_size=r'\\small'
            ),
            show_point=True
        )

Note:
    - 樣式配置可以被多個圖形元素重用
    - 支援 LaTeX 數學公式和 TikZ 高級功能
    - 提供預設值確保基本可用性
    - 可與基礎參數模型組合使用
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Literal

class LabelStyleConfig(BaseModel):
    """標籤樣式配置模型
    
    定義文字標籤的詳細樣式選項，包括顏色、字體、位置和
    特殊效果。此配置類別用於覆蓋預設的標籤外觀設定。
    
    Attributes:
        text_override (Optional[str]): 覆蓋標籤文字內容
        position_modifiers (Optional[str]): TikZ 位置修飾詞，如 'above', 'below left'
        anchor (Optional[str]): 標籤節點錨點，如 'north west', 'center'
        rotate (Optional[float]): 文字旋轉角度（度）
        color (Optional[str]): 文字顏色覆蓋
        font_size (Optional[str]): 字體大小命令，如 '\\small', '\\large'
        math_mode (Optional[bool]): 是否使用數學模式 ($...$)
        additional_node_options (Optional[str]): 額外的 TikZ 節點選項
        default_offset_override (Optional[float]): 預設偏移量覆蓋
        
    Example:
        創建強調樣式::
        
            emphasis_style = LabelStyleConfig(
                color='red',
                font_size=r'\\large',
                additional_node_options='draw, circle',
                math_mode=False
            )
            
        創建數學公式樣式::
        
            formula_style = LabelStyleConfig(
                color='blue',
                math_mode=True,
                font_size=r'\\normalsize',
                anchor='center'
            )
            
    Note:
        - None 值表示使用預設設定
        - position_modifiers 支援所有 TikZ positioning 語法
        - additional_node_options 允許任意 TikZ 節點自定義
        - 旋轉角度為正數時逆時針旋轉
    """
    text_override: Optional[str] = Field(default=None, description="覆蓋標籤文字內容")
    position_modifiers: Optional[str] = Field(default=None, description="TikZ 位置修飾詞")
    anchor: Optional[str] = Field(default=None, description="標籤節點錨點")
    rotate: Optional[float] = Field(default=None, description="文字旋轉角度（度）")
    color: Optional[str] = Field(default=None, description="文字顏色")
    font_size: Optional[str] = Field(default=None, description="字體大小命令")
    math_mode: Optional[bool] = Field(default=None, description="是否使用數學模式")
    additional_node_options: Optional[str] = Field(default=None, description="額外的 TikZ 節點選項")
    default_offset_override: Optional[float] = Field(default=None, description="預設偏移量覆蓋")
    
    @validator('anchor', 'position_modifiers', 'font_size', 'additional_node_options', pre=True, always=True)
    def ensure_optional_strings_are_strings(cls, v):
        """確保可選字串欄位為字串類型"""
        if v is not None and not isinstance(v, str):
            raise ValueError("樣式字串選項必須是字符串類型")
        return v

class PointStyleConfig(BaseModel):
    """點樣式配置模型
    
    定義點圖形的可視化樣式，支援不同的標記類型、
    顏色和大小配置。用於統一管理點的外觀設定。
    
    Attributes:
        color (Optional[str]): 點的顏色
        marker (Optional[str]): 標記樣式，如 'o' (圓), 'x', '*', 's' (方形)
        size_mpl (Optional[float]): Matplotlib 散點圖大小（點²）
        tikz_scale (Optional[float]): TikZ 點縮放比例
        
    Example:
        創建紅色大圓點樣式::
        
            point_style = PointStyleConfig(
                color='red',
                marker='o',
                size_mpl=50,
                tikz_scale=1.5
            )
            
    Note:
        - size_mpl 用於 matplotlib 可視化
        - tikz_scale 用於 TikZ 輸出
        - marker 支援標準 matplotlib 標記符號
    """
    color: Optional[str] = Field(default='black', description="點的顏色")
    marker: Optional[str] = Field(default='o', description="標記樣式")
    size_mpl: Optional[float] = Field(default=30, description="Matplotlib 散點大小")
    tikz_scale: Optional[float] = Field(default=1.0, description="TikZ 點縮放比例")

class VertexDisplayConfig(BaseModel):
    """頂點顯示配置模型
    
    定義多邊形或圖形頂點的顯示方式，包括點標記和
    標籤的樣式控制。用於統一管理頂點的可視化效果。
    
    Attributes:
        show_point (bool): 是否顯示頂點標記
        point_style (Optional[PointStyleConfig]): 頂點點的樣式配置
        show_label (bool): 是否顯示頂點標籤
        label_style (Optional[LabelStyleConfig]): 頂點標籤的樣式配置
        
    Example:
        創建簡潔的頂點配置::
        
            vertex_config = VertexDisplayConfig(
                show_point=True,
                show_label=True,
                point_style=PointStyleConfig(color='red', marker='o'),
                label_style=LabelStyleConfig(
                    color='blue',
                    font_size=r'\\small',
                    position_modifiers='above left'
                )
            )
            
    Note:
        - 點和標籤可以獨立控制顯示
        - 預設使用標準樣式配置
        - 適合用於三角形、多邊形等頂點管理
    """
    show_point: bool = Field(default=True, description="是否顯示頂點標記")
    point_style: Optional[PointStyleConfig] = Field(
        default_factory=PointStyleConfig,
        description="頂點點的樣式"
    )
    show_label: bool = Field(default=True, description="是否顯示頂點標籤")
    label_style: Optional[LabelStyleConfig] = Field(
        default_factory=LabelStyleConfig,
        description="頂點標籤的樣式"
    )

class SideDisplayConfig(BaseModel):
    """邊顯示配置模型
    
    定義線段、多邊形邊或其他線性元素的標籤顯示配置。
    支援不同的標籤內容類型和格式化選項。
    
    Attributes:
        show_label (bool): 是否顯示邊標籤
        label_text_type (Literal): 標籤文字類型
            - 'default_name': 使用預設名稱（如 'a', 'b', 'c'）
            - 'length': 顯示邊長數值
            - 'custom': 使用自定義文字
        custom_label_text (Optional[str]): 自定義標籤文字（當 label_text_type='custom' 時使用）
        length_format (str): 邊長顯示格式字串
        label_style (Optional[LabelStyleConfig]): 邊標籤的樣式配置
        
    Example:
        顯示邊長的配置::
        
            side_config = SideDisplayConfig(
                show_label=True,
                label_text_type='length',
                length_format="{value:.1f}",
                label_style=LabelStyleConfig(
                    color='green',
                    font_size=r'\\footnotesize'
                )
            )
            
        自定義標籤配置::
        
            custom_side = SideDisplayConfig(
                show_label=True,
                label_text_type='custom',
                custom_label_text='底邊',
                label_style=LabelStyleConfig(color='purple')
            )
            
    Note:
        - length_format 使用 Python 格式字串語法
        - 預設名稱通常為小寫字母（a, b, c...）
        - 自定義文字支援 LaTeX 語法
    """
    show_label: bool = Field(default=True, description="是否顯示邊標籤")
    label_text_type: Literal['default_name', 'length', 'custom'] = Field(
        default='default_name',
        description="標籤文字類型"
    )
    custom_label_text: Optional[str] = Field(default=None, description="自定義標籤文字")
    length_format: str = Field(default="{value:.2f}", description="邊長顯示格式")
    label_style: Optional[LabelStyleConfig] = Field(
        default_factory=LabelStyleConfig,
        description="邊標籤樣式"
    )
    
    @validator('custom_label_text')
    def validate_custom_text_when_needed(cls, v, values):
        """當標籤類型為 custom 時驗證自定義文字不為空"""
        if values.get('label_text_type') == 'custom' and not v:
            raise ValueError("當 label_text_type 為 'custom' 時必須提供 custom_label_text")
        return v

class AngleLabelConfig(BaseModel):
    """角度標籤配置模型
    
    專門用於角度標記和標籤的樣式配置，包括弧線樣式
    和角度數值的顯示格式。
    
    Attributes:
        show_arc (bool): 是否顯示角度弧線
        show_label (bool): 是否顯示角度標籤
        arc_radius (float): 弧線半徑
        arc_color (str): 弧線顏色
        arc_style (str): 弧線樣式
        label_text_type (Literal): 角度標籤類型
        angle_format (str): 角度數值格式
        label_style (Optional[LabelStyleConfig]): 角度標籤樣式
        
    Example:
        創建角度標記配置::
        
            angle_config = AngleLabelConfig(
                show_arc=True,
                show_label=True,
                arc_color='blue',
                label_text_type='degree',
                angle_format="{value:.0f}°",
                label_style=LabelStyleConfig(
                    color='blue',
                    font_size=r'\\scriptsize'
                )
            )
    """
    show_arc: bool = Field(default=True, description="是否顯示角度弧線")
    show_label: bool = Field(default=True, description="是否顯示角度標籤")
    arc_radius: float = Field(default=0.5, gt=0, description="弧線半徑")
    arc_color: str = Field(default='blue', description="弧線顏色")
    arc_style: str = Field(default='solid', description="弧線樣式")
    label_text_type: Literal['symbol', 'degree', 'radian', 'custom'] = Field(
        default='symbol',
        description="角度標籤類型"
    )
    angle_format: str = Field(default="{value:.1f}°", description="角度數值格式")
    label_style: Optional[LabelStyleConfig] = Field(
        default_factory=LabelStyleConfig,
        description="角度標籤樣式"
    )

class TextStylePresets:
    """文字樣式預設集合
    
    提供常用的標籤樣式預設配置，方便快速應用統一的
    視覺風格。包含教學常用的各種文字樣式。
    
    預設樣式：
    - TITLE: 標題樣式
    - SUBTITLE: 副標題樣式  
    - NORMAL: 標準文字樣式
    - SMALL: 小字樣式
    - MATH: 數學公式樣式
    - EMPHASIS: 強調樣式
    - NOTE: 註解樣式
    """
    
    TITLE = LabelStyleConfig(
        font_size=r'\\Large',
        color='black',
        math_mode=False,
        anchor='center'
    )
    
    SUBTITLE = LabelStyleConfig(
        font_size=r'\\large',
        color='darkgray',
        math_mode=False,
        anchor='center'
    )
    
    NORMAL = LabelStyleConfig(
        font_size=r'\\normalsize',
        color='black',
        math_mode=True,
        anchor='center'
    )
    
    SMALL = LabelStyleConfig(
        font_size=r'\\small',
        color='gray',
        math_mode=True,
        anchor='center'
    )
    
    MATH = LabelStyleConfig(
        font_size=r'\\normalsize',
        color='blue',
        math_mode=True,
        anchor='center'
    )
    
    EMPHASIS = LabelStyleConfig(
        font_size=r'\\normalsize',
        color='red',
        math_mode=False,
        anchor='center',
        additional_node_options='font=\\bfseries'
    )
    
    NOTE = LabelStyleConfig(
        font_size=r'\\footnotesize',
        color='gray',
        math_mode=False,
        anchor='north west',
        position_modifiers='above right'
    )