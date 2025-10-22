#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 函數圖形參數

此模組定義函數圖形生成器的參數模型，支援多項式、指數、對數、
三角函數等常見高中數學函數的圖形繪製。使用 PGFPlots 生成高品質
的函數圖形，自動處理不連續點和漸近線。

主要組件：
1. **FunctionPlotParams**: 萬用函數圖形參數模型
2. **支援的函數類型**:
   - polynomial: 多項式函數
   - exponential: 指數函數
   - logarithmic: 對數函數
   - trigonometric: 三角函數

設計特點：
- 使用 PGFPlots 繪製，自動處理不連續點
- Optional 參數設計，根據函數類型彈性配置
- Pydantic 驗證確保參數正確性
- 支援振幅、週期等高級三角函數參數
- 自動處理定義域和值域

Example:
    多項式函數::

        from figures.params.function_plot import FunctionPlotParams

        params = FunctionPlotParams(
            function_type='polynomial',
            coefficients=[1, -2, 1],  # x^2 - 2x + 1
            x_range=(-2, 4),
            y_range=(-1, 5),
            show_y_intercept=True
        )

    三角函數::

        params = FunctionPlotParams(
            function_type='trigonometric',
            trig_function='sin',
            amplitude=2.0,
            period=3.14159,
            x_range=(-6.28, 6.28),
            y_range=(-2.5, 2.5)
        )

    指數函數::

        params = FunctionPlotParams(
            function_type='exponential',
            base=2.0,
            x_range=(-3, 3),
            y_range=(0, 8)
        )

Note:
    - tan 函數會自動使用 unbounded coords=jump 處理不連續點
    - 對數函數定義域自動從 0.001 開始避免無效值
    - coefficients 按降冪排列: [a_n, ..., a_1, a_0] 表示 a_n*x^n + ... + a_0
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional, Literal, Tuple, Dict, Any
from .base import BaseFigureParams

class FunctionPlotParams(BaseFigureParams):
    """函數圖形參數模型

    萬用函數圖形生成器的參數配置，支援多種常見高中數學函數類型。
    根據不同的 function_type，某些參數為必需或可選。

    Attributes:
        function_type (Literal): 函數類型，支援:
            - 'polynomial': 多項式
            - 'exponential': 指數函數
            - 'logarithmic': 對數函數
            - 'trigonometric': 三角函數

        coefficients (Optional[List[float]]): 多項式係數列表（降冪排列）
            例如 [1, -2, 1] 表示 x^2 - 2x + 1
            **polynomial 類型必需**

        base (Optional[float]): 指數/對數的底數
            預設為 e (自然底數)
            **exponential/logarithmic 類型可選**

        trig_function (Optional[Literal]): 三角函數類型
            支援 'sin', 'cos', 'tan'
            **trigonometric 類型必需**

        amplitude (Optional[float]): 三角函數振幅
            預設為 1.0
            **trigonometric 類型可選**

        period (Optional[float]): 三角函數週期
            預設為 2π
            **trigonometric 類型可選**

        x_range (Tuple[float, float]): x 軸顯示範圍 [xmin, xmax]

        y_range (Tuple[float, float]): y 軸顯示範圍 [ymin, ymax]

        samples (int): PGFPlots 採樣點數量
            預設為 100，tan 函數建議 200

        plot_color (str): 函數曲線顏色

        line_thickness (str): 線條粗細

        show_grid (bool): 是否顯示網格

        show_axes_labels (bool): 是否顯示座標軸標籤

        show_y_intercept (bool): 是否標記 y 截距點

        y_intercept_color (str): y 截距標記顏色

    Example:
        對數函數::

            params = FunctionPlotParams(
                function_type='logarithmic',
                base=10,  # log₁₀(x)
                x_range=(0.001, 10),
                y_range=(-3, 3),
                show_grid=True,
                plot_color='green'
            )

        正切函數（自動處理不連續）::

            params = FunctionPlotParams(
                function_type='trigonometric',
                trig_function='tan',
                x_range=(-6.28, 6.28),
                y_range=(-4, 4),
                samples=200  # tan 需要更多採樣點
            )

    Note:
        - 參數驗證會根據 function_type 檢查必需參數
        - tan 函數會自動添加 unbounded coords=jump 選項
        - 對數函數的 x_range 不應包含負值或零
    """

    # 核心參數
    function_type: Literal['polynomial', 'exponential', 'logarithmic', 'trigonometric'] = Field(
        ...,
        description="函數類型"
    )

    # 多項式專用參數
    coefficients: Optional[List[float]] = Field(
        default=None,
        description="多項式係數（降冪排列），polynomial 類型必需"
    )

    # 指數/對數專用參數
    base: Optional[float] = Field(
        default=None,
        description="指數/對數底數，None 表示自然底數 e"
    )

    # 三角函數專用參數
    trig_function: Optional[Literal['sin', 'cos', 'tan']] = Field(
        default=None,
        description="三角函數類型，trigonometric 類型必需"
    )

    amplitude: Optional[float] = Field(
        default=1.0,
        description="三角函數振幅"
    )

    period: Optional[float] = Field(
        default=6.283185307179586,  # 2π
        description="三角函數週期"
    )

    # 座標範圍
    x_range: Tuple[float, float] = Field(
        default=(-5, 5),
        description="x 軸顯示範圍 [xmin, xmax]"
    )

    y_range: Tuple[float, float] = Field(
        default=(-5, 5),
        description="y 軸顯示範圍 [ymin, ymax]"
    )

    # 繪圖選項
    samples: int = Field(
        default=100,
        ge=20,
        le=500,
        description="採樣點數量"
    )

    plot_color: str = Field(
        default='blue',
        description="曲線顏色"
    )

    line_thickness: str = Field(
        default='thick',
        description="線條粗細 (ultra thin/very thin/thin/semithick/thick/very thick/ultra thick)"
    )

    show_grid: bool = Field(
        default=True,
        description="是否顯示網格"
    )

    show_axes_labels: bool = Field(
        default=True,
        description="是否顯示座標軸標籤"
    )

    show_y_intercept: bool = Field(
        default=False,
        description="是否標記 y 截距點"
    )

    y_intercept_color: str = Field(
        default='red',
        description="y 截距標記顏色"
    )

    # === 新增：圖形尺寸控制 ===
    figure_width: str = Field(
        default='10cm',
        description="圖形寬度（LaTeX 單位，如 '10cm', '0.8\\textwidth'）"
    )

    figure_height: str = Field(
        default='7cm',
        description="圖形高度（LaTeX 單位，如 '7cm', '0.6\\textwidth'）"
    )

    # === 新增：座標軸樣式控制 ===
    axis_lines_style: Literal['none', 'middle', 'box', 'left', 'right', 'center'] = Field(
        default='middle',
        description="座標軸樣式：none=隱藏, middle=居中穿過, box=邊框, left/right/center=其他樣式"
    )

    show_ticks: bool = Field(
        default=True,
        description="是否顯示刻度標記"
    )

    # === 新增：主曲線繪圖範圍 ===
    main_plot_domain: Optional[Tuple[float, float]] = Field(
        default=None,
        description="主曲線繪製範圍 (x_min, x_max)，None 則使用完整 x_range"
    )

    # === 新增：多曲線支援 ===
    additional_plots: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="""額外曲線列表，每個字典包含：
        - domain: (x_min, x_max) - 繪製範圍（必需）
        - color: 顏色（預設 'blue'）
        - thickness: 線條粗細（預設 'thick'）
        - samples: 採樣點數（預設使用主曲線的 samples）
        - expression: TikZ 表達式（可選，預設使用主函數）
        """
    )

    # === 新增：點標註支援 ===
    plot_points: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="""要標記的點列表，每個字典包含：
        - x, y: 座標（必需）
        - color: 顏色（預設 'black'）
        - size: 點大小（預設 '3pt'）
        """
    )

    # === 新增：標籤支援 ===
    plot_labels: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="""標籤列表，每個字典包含：
        - x, y: 位置（必需）
        - text: 標籤文字（必需）
        - position: 'above', 'below', 'left', 'right'（預設 'above'）
        - color: 顏色（預設 'black'）
        - math_mode: 是否使用數學模式（預設 True）
        """
    )

    # ============== 驗證器 ==============

    @model_validator(mode='after')
    def validate_function_type_requirements(self):
        """驗證不同函數類型的必需參數"""
        if self.function_type == 'polynomial':
            if self.coefficients is None or len(self.coefficients) == 0:
                raise ValueError("多項式函數必須提供 coefficients 參數")
            if not all(isinstance(c, (int, float)) for c in self.coefficients):
                raise ValueError("係數必須全部為數值類型")

        elif self.function_type == 'trigonometric':
            if self.trig_function is None:
                raise ValueError("三角函數必須指定 trig_function 參數 (sin/cos/tan)")

        return self

    @field_validator('base')
    @classmethod
    def validate_base(cls, v, info):
        """驗證底數必須為正數"""
        if v is not None and v <= 0:
            raise ValueError("底數必須為正數")

        return v

    @field_validator('amplitude')
    @classmethod
    def validate_amplitude(cls, v):
        """驗證振幅必須為正數"""
        if v is not None and v <= 0:
            raise ValueError("振幅必須為正數")

        return v

    @field_validator('period')
    @classmethod
    def validate_period(cls, v):
        """驗證週期必須為正數"""
        if v is not None and v <= 0:
            raise ValueError("週期必須為正數")

        return v

    @field_validator('x_range', 'y_range')
    @classmethod
    def validate_range(cls, v):
        """驗證範圍格式"""
        if len(v) != 2:
            raise ValueError("範圍必須包含恰好兩個數值 [最小值, 最大值]")
        if v[0] >= v[1]:
            raise ValueError("範圍的最小值必須小於最大值")
        return v

    @field_validator('x_range')
    @classmethod
    def validate_logarithmic_domain(cls, v, info):
        """驗證對數函數定義域不包含非正數"""
        function_type = info.data.get('function_type')

        if function_type == 'logarithmic':
            if v[0] <= 0:
                raise ValueError("對數函數的 x 範圍最小值必須大於 0（建議使用 0.001）")

        return v
