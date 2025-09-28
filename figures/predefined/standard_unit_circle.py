#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 標準單位圓預定義複合圖形生成器
"""

from typing import Dict, Any, List
import sympy
from pydantic import ValidationError

from utils import Point, get_logger
from ..base import FigureGenerator
from ..params import StandardUnitCircleParams, CompositeParams, SubFigureParams, AbsolutePosition
from .. import register_figure_generator, get_figure_generator

logger = get_logger(__name__)

@register_figure_generator
class StandardUnitCircleGenerator(FigureGenerator):
    """標準單位圓預定義複合圖形生成器
    
    這是一個元生成器，它不直接生成 TikZ 代碼，而是構建一個 CompositeParams 實例，
    然後使用 CompositeFigureGenerator 生成最終的 TikZ 代碼。
    """
    
    @classmethod
    def get_name(cls) -> str:
        """獲取圖形類型唯一標識符"""
        return 'standard_unit_circle'
    
    def generate_tikz(self, params: Dict[str, Any]) -> str:
        """生成標準單位圓 TikZ 圖形內容
        
        Args:
            params: 標準單位圓參數字典，應符合 StandardUnitCircleParams 模型
            
        Returns:
            TikZ 圖形內容（不包含 tikzpicture 環境）
            
        Raises:
            ValidationError: 如果參數驗證失敗
        """
        # 使用 Pydantic 模型驗證參數
        try:
            validated_params = StandardUnitCircleParams(**params)
        except ValidationError as e:
            logger.error(f"標準單位圓參數驗證失敗: {str(e)}")
            raise ValueError(f"標準單位圓參數驗證失敗: {str(e)}")
        
        # 構建 CompositeParams 實例
        composite_params = self._build_composite_params(validated_params)
        
        # 獲取 CompositeFigureGenerator 實例
        composite_generator = get_figure_generator('composite')()
        
        # 使用 CompositeFigureGenerator 生成 TikZ 代碼
        return composite_generator.generate_tikz(composite_params.dict())
    
    def _build_composite_params(self, params: StandardUnitCircleParams) -> CompositeParams:
        """構建 CompositeParams 實例
        
        Args:
            params: 驗證後的 StandardUnitCircleParams 實例
            
        Returns:
            CompositeParams 實例
        """
        # 提取參數
        angle = params.angle
        show_coordinates = params.show_coordinates
        show_angle = params.show_angle
        show_point = params.show_point
        show_radius = params.show_radius
        line_color = params.line_color
        point_color = params.point_color
        angle_color = params.angle_color
        radius_color = params.radius_color
        coordinate_color = params.coordinate_color
        radius = params.radius
        label_point = params.label_point
        point_label = params.point_label
        variant = params.variant
        
        # 創建子圖形列表
        sub_figures: List[SubFigureParams] = []
        
        # 1. 添加坐標系（如果需要）
        if show_coordinates:
            sub_figures.append(
                SubFigureParams(
                    id="coordinates",
                    type="coordinate_system",
                    params={
                        "x_range": (-radius * 1.2, radius * 1.2),
                        "y_range": (-radius * 1.2, radius * 1.2),
                        "show_labels": False,
                        "color": coordinate_color,
                        "variant": variant
                    },
                    position=AbsolutePosition(x=0, y=0)
                )
            )
        
        # 2. 添加單位圓
        sub_figures.append(
            SubFigureParams(
                id="circle",
                type="circle",
                params={
                    "radius": radius,
                    "center_x": 0,
                    "center_y": 0,
                    "fill": False,
                    "line_color": line_color,
                    "variant": variant
                },
                position=AbsolutePosition(x=0, y=0)
            )
        )
        
        # 3. 添加原點
        sub_figures.append(
            SubFigureParams(
                id="origin",
                type="point",
                params={
                    "x": 0,
                    "y": 0,
                    #"label": "O",
                    "color": line_color
                },
                position=AbsolutePosition(x=0, y=0)
            )
        )
        
        # 4. 添加點 P（如果需要）
        if show_point:
            # 使用新架構的 sympy 計算幾何座標
            angle_rad = sympy.rad(angle)
            # 使用 sympy.N() 進行數值評估以獲得精確座標值
            cos_value = radius * sympy.N(sympy.cos(angle_rad))
            sin_value = radius * sympy.N(sympy.sin(angle_rad))
            point_on_circle = Point(float(cos_value), float(sin_value))
            
            # 確定點標籤的位置
            label_position = self._get_label_position(angle)
            
            sub_figures.append(
                SubFigureParams(
                    id="point",
                    type="point",
                    params={
                        "x": float(cos_value),
                        "y": float(sin_value),
                        "label": point_label if label_point else None,
                        "label_position": label_position,
                        "color": point_color,
                        "variant": variant
                    },
                    position=AbsolutePosition(x=0, y=0)
                )
            )
            
            # 5. 添加半徑線段（如果需要）
            if show_radius:
                sub_figures.append(
                    SubFigureParams(
                        id="radius",
                        type="line",
                        params={
                            "start_point": [0, 0],
                            "end_point": [float(cos_value), float(sin_value)],
                            "color": radius_color,
                            "width": "thick",
                            "variant": variant
                        },
                        position=AbsolutePosition(x=0, y=0)
                    )
                )
        
        # 6. 添加角度弧（如果需要）
        if show_angle:
            # 確定角度標籤的位置
            angle_label_position = self._get_angle_label_position(angle)
            
            sub_figures.append(
                SubFigureParams(
                    id="angle",
                    type="arc",
                    params={
                        "center": [0, 0],
                        "start_angle": 0,
                        "end_angle": angle,
                        "radius": 0.3,
                        "color": angle_color
                        #"label": f"{angle}^\\circ",
                        #"label_position": angle_label_position,
                    },
                    position=AbsolutePosition(x=0, y=0)
                )
            )
        
        # 7. 如果是詳解變體，添加更多信息
        if variant == 'explanation':
            # 使用新架構的 sympy 計算三角函數值
            angle_rad = sympy.rad(angle)
            # 使用 sympy 計算符號表達式
            cos_expr = sympy.cos(angle_rad)
            sin_expr = sympy.sin(angle_rad)
            # 計算數值坐標 (使用 sympy.N() 進行數值評估)
            cos_value = radius * sympy.N(cos_expr)
            sin_value = radius * sympy.N(sin_expr)
            # 使用 Point 類型記錄座標
            explanation_point = Point(float(cos_value), float(sin_value))

            # 格式化為 LaTeX (統一由 _get_exact_trig_values 處理)
            cos_latex, sin_latex = self._get_exact_trig_values(angle)
            
            
            # 添加坐標標籤
            if show_point and label_point:  # 確保點 P 存在且有標籤
                # 根據象限決定坐標標籤的相對位置
                if 0 <= angle < 90 or 270 <= angle < 360:  # 第一或第四象限
                    coord_position = "right"  # 坐標標籤放在點標籤的右邊
                else:  # 第二或第三象限
                    coord_position = "left"   # 坐標標籤放在點標籤的左邊
                
                # 計算坐標標籤的位置（相對於點 P 的位置）
                # 根據 coord_position 調整偏移方向
                offset_x = 0.3 if coord_position == "right" else -0.3
                
                sub_figures.append(
                    SubFigureParams(
                        id="coord_label",
                        type="label",
                        params={
                            "x": float(cos_value + offset_x),  # 水平偏移
                            "y": float(sin_value),             # 保持與點 P 相同的垂直位置
                            "text": f"({cos_latex},{sin_latex})",
                            "anchor": coord_position
                        },
                        position=AbsolutePosition(x=0, y=0)
                    )
                )
            
            
            
            # 添加 x 和 y 投影線，暫時註記起來調整，之後刪除
            """
            sub_figures.append(
                SubFigureParams(
                    id="x_projection",
                    type="line",
                    params={
                        "x1": cos_value,
                        "y1": sin_value,
                        "x2": cos_value,
                        "y2": 0,
                        "color": "gray",
                        "style": "dashed",
                        "variant": variant
                    },
                    position=AbsolutePosition(x=0, y=0)
                )
            )
            
            sub_figures.append(
                SubFigureParams(
                    id="x_label",
                    type="label",
                    params={
                        "x": cos_value,
                        "y": 0,
                        "text": cos_latex,
                        "position": "below",
                        "variant": variant
                    },
                    position=AbsolutePosition(x=0, y=0)
                )
            )
            
            sub_figures.append(
                SubFigureParams(
                    id="y_projection",
                    type="line",
                    params={
                        "x1": cos_value,
                        "y1": sin_value,
                        "x2": 0,
                        "y2": sin_value,
                        "color": "gray",
                        "style": "dashed",
                        "variant": variant
                    },
                    position=AbsolutePosition(x=0, y=0)
                )
            )
            
            sub_figures.append(
                SubFigureParams(
                    id="y_label",
                    type="label",
                    params={
                        "x": 0,
                        "y": sin_value,
                        "text": sin_latex,
                        "position": "left",
                        "variant": variant
                    },
                    position=AbsolutePosition(x=0, y=0)
                )
            )
        """  
        # 創建 CompositeParams 實例
        return CompositeParams(
            variant=variant,
            sub_figures=sub_figures
        )
    
    def _get_label_position(self, angle: float) -> str:
        """確定點標籤的位置"""
        if 0 <= angle < 45 or 315 <= angle <= 360:
            return "above right"
        elif 45 <= angle < 135:
            return "above"
        elif 135 <= angle < 225:
            return "above left"
        elif 225 <= angle < 315:
            return "below"
        else:
            return "right"
    
    def _get_angle_label_position(self, angle: float) -> str:
        """確定角度標籤的位置"""
        if 0 <= angle < 90:
            return "above right"
        elif 90 <= angle < 180:
            return "above left"
        elif 180 <= angle < 270:
            return "below left"
        else:
            return "below right"
    
    def _get_exact_trig_values(self, angle: float) -> tuple:
        """使用 sympy 獲取角度的三角函數值的 LaTeX 表示。
        對於特殊角度，生成精確的 LaTeX。
        對於非特殊角度，生成保留4位小數的數值 LaTeX。
        """
        angle_rad = sympy.rad(angle)
        cos_expr = sympy.cos(angle_rad)
        sin_expr = sympy.sin(angle_rad)

        # 嘗試簡化表達式，看是否能得到特殊角度的精確形式
        # 使用 evalf() 進行數值評估來檢查是否接近特殊角度的值，避免符號比較問題
        # 增加一個小的容差 epsilon
        epsilon = 1e-10
        is_special = False
        special_angles_rad = [sympy.rad(a) for a in [0, 30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 240, 270, 300, 315, 330, 360]]

        for special_rad in special_angles_rad:
             # 比較數值評估結果
            if abs(sympy.N(angle_rad - special_rad)) < epsilon:
                is_special = True
                # 使用特殊角度的精確表達式
                cos_expr = sympy.cos(special_rad)
                sin_expr = sympy.sin(special_rad)
                break # 找到匹配的特殊角度後跳出循環

        if is_special:
            # 對於特殊角度，直接使用 sympy.latex 生成精確 LaTeX
            # 確保簡化後的結果用於生成 LaTeX
            cos_latex = sympy.latex(sympy.simplify(cos_expr))
            sin_latex = sympy.latex(sympy.simplify(sin_expr))
        else:
            # 對於非特殊角度，計算數值並格式化為 LaTeX 字串
            # 使用原始表達式進行數值評估以獲得更高精度
            cos_val = sympy.N(cos_expr, 4)
            sin_val = sympy.N(sin_expr, 4)
            # 確保數值結果是字符串
            cos_latex = f"{cos_val}"
            sin_latex = f"{sin_val}"

        result = (cos_latex, sin_latex)
        logger.debug(f"獲取角度 {angle}° 的三角函數 LaTeX 值: cos={cos_latex}, sin={sin_latex}")
        return result