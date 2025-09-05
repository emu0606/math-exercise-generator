#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 預定義三角形生成器

此模組實現了功能完整的三角形圖形生成器，支援多種三角形定義方式、
豐富的標註選項和特殊點顯示。使用新架構的統一 API 進行幾何計算
和 TikZ 渲染。

主要特性：
1. **多種構造方式**: SSS, SAS, ASA, AAS, 座標定義
2. **完整標註系統**: 頂點標籤、邊標籤、角標記
3. **特殊點支援**: 質心、內心、外心、垂心
4. **靈活樣式控制**: 可配置的顯示和樣式選項
5. **新架構整合**: 使用統一的幾何計算和渲染 API

此生成器是新架構 API 使用的典型範例，展示了如何：
- 使用 `from utils import` 統一導入
- 整合幾何計算模組和 TikZ 渲染
- 處理複雜的參數模型和驗證
- 生成高品質的數學圖形

Example:
    生成基本 SSS 三角形::

        from figures import get_figure_generator
        
        generator = get_figure_generator('predefined_triangle')
        tikz_code = generator.generate_tikz({
            'definition_mode': 'sss',
            'side_a': 3, 'side_b': 4, 'side_c': 5,
            'variant': 'explanation'
        })

Note:
    - 此生成器已完全遷移到新架構 API
    - 使用 `PredefinedTriangleParams` 進行參數驗證
    - 支援複雜的顯示配置和樣式控制
    - 是其他生成器遷移到新架構的參考範例
"""

import math
from typing import Dict, Any, List, Tuple, Optional
from pydantic import ValidationError

from ..base import FigureGenerator
from .. import register_figure_generator, get_figure_generator
from ..params_models import (
    PredefinedTriangleParams, PointTuple,
    LabelParams, ArcParams, BasicTriangleParams # For constructing sub-figure params
)
# 新架構 API
from utils import (
    construct_triangle,
    TriangleConstructionError as TriangleDefinitionError,
    distance,
    midpoint,
    get_centroid,
    get_incenter,
    get_circumcenter,
    get_orthocenter,
    Point,
    Triangle
)
from utils.tikz import (
    ArcRenderer,
    position_vertex_label_auto,
    position_side_label_auto,
    position_angle_label_auto
)

# 初始化渲染器
arc_renderer = ArcRenderer()

@register_figure_generator
class PredefinedTriangleGenerator(FigureGenerator):
    """預定義三角形生成器
    
    高級三角形圖形生成器，支援完整的數學標註和多種構造方式。
    此生成器展示了新架構 API 的全面應用，包括幾何計算、TikZ 渲染
    和複雜參數處理。
    
    核心功能：
    1. **靈活構造**: 支援 SSS、SAS、ASA、AAS 和座標定義方式
    2. **豐富標註**: 自動或手動配置頂點、邊、角的標籤和標記
    3. **特殊點計算**: 質心、內心、外心、垂心的自動計算和顯示
    4. **樣式控制**: 細粒度的顏色、字體、定位控制
    5. **變體支援**: question/explanation 變體的不同顯示策略
    
    技術特點：
    - 使用新架構統一 API (`from utils import`)
    - 整合 `PredefinedTriangleParams` 複雜參數模型
    - 使用 `ArcRenderer` 和標籤定位系統
    - 支援 TikZ 高品質數學圖形輸出
    
    Attributes:
        無實例屬性，所有狀態通過參數傳遞
        
    Example:
        基本使用::
        
            generator = PredefinedTriangleGenerator()
            
            # SSS 三角形（3-4-5 直角三角形）
            params = {
                'definition_mode': 'sss',
                'side_a': 3, 'side_b': 4, 'side_c': 5,
                'variant': 'question'
            }
            tikz_code = generator.generate_tikz(params)
            
        詳解變體與特殊點::
        
            params = {
                'definition_mode': 'sss',
                'side_a': 6, 'side_b': 8, 'side_c': 10,
                'variant': 'explanation',
                'display_centroid': {'show_point': True, 'show_label': True},
                'display_incenter': {'show_point': True, 'show_label': True}
            }
            
    Note:
        - 此類別是新架構遷移的完整範例
        - 參數驗證使用 Pydantic v2 模型
        - 錯誤處理包含詳細的幾何驗證
        - 輸出的 TikZ 代碼符合數學出版標準
    """

    @classmethod
    def get_name(cls) -> str:
        return "predefined_triangle"

    def _get_sub_generator(self, type_name: str) -> FigureGenerator:
        """輔助方法，獲取基礎圖形生成器實例"""
        # 此處不緩存實例，因為基礎生成器通常是無狀態的
        generator_class = get_figure_generator(type_name)
        return generator_class()

    def generate_tikz(self, params: Dict[str, Any]) -> str:
        """生成預定義三角形的 TikZ 圖形內容
        
        這是預定義三角形生成器的核心方法，負責將複雜的三角形參數
        轉換為完整的 TikZ 圖形代碼。整合了幾何計算、標籤定位、
        特殊點計算等多個子系統。
        
        處理流程：
        1. 參數驗證（使用 PredefinedTriangleParams）
        2. 三角形構造（使用新架構幾何 API）
        3. 基礎三角形渲染
        4. 頂點標籤處理
        5. 邊標籤處理
        6. 角標記處理
        7. 特殊點計算和顯示
        8. TikZ 代碼組合
        
        Args:
            params (Dict[str, Any]): 三角形參數字典，必須符合 PredefinedTriangleParams 模型。
                主要參數包括：
                - definition_mode: 構造方式 ('sss', 'sas', 'asa', 'aas', 'coordinates')
                - 幾何參數: 根據 definition_mode 提供對應參數
                - 顯示配置: 頂點、邊、角的顯示和樣式選項
                - 特殊點配置: 質心、內心等特殊點的顯示選項
                
        Returns:
            str: 完整的 TikZ 圖形內容，不包含 tikzpicture 環境。
                包含三角形輪廓、所有標籤、角標記和特殊點。
                
        Raises:
            ValueError: 當參數驗證失敗時，包含詳細的 Pydantic 錯誤信息
            TriangleDefinitionError: 當幾何參數無法構成有效三角形時
            RuntimeError: 當 TikZ 渲染過程中發生錯誤時
            
        Example:
            生成標準 3-4-5 直角三角形::
            
                params = {
                    'definition_mode': 'sss',
                    'side_a': 3, 'side_b': 4, 'side_c': 5,
                    'variant': 'explanation'
                }
                tikz_code = generator.generate_tikz(params)
                
        Note:
            - 使用新架構的 construct_triangle 函數進行幾何計算
            - 自動處理標籤衝突和定位優化
            - 支援複雜的樣式配置和顯示選項
            - 輸出符合數學出版品質要求
        """
        try:
            config = PredefinedTriangleParams(**params)
        except ValidationError as e:
            # Consider logging e.errors() for detailed Pydantic error info
            raise ValueError(f"PredefinedTriangleGenerator 參數驗證失敗: {e}") from e

        tikz_parts: List[str] = []

        # 1. 獲取三角形頂點
        vertex_params = {
            'definition_mode': config.definition_mode,
            'side_a': config.side_a, 'side_b': config.side_b, 'side_c': config.side_c,
            'p1': config.p1, 'p2': config.p2, 'p3': config.p3,
            'side1': config.sas_side1, 'angle_rad': config.sas_angle_rad, 'side2': config.sas_side2,
            'angle1_rad': config.asa_angle1_rad, 'side_length': config.asa_side_length, 'angle2_rad': config.asa_angle2_rad,
            # AAS uses 'angle1_rad', 'angle2_rad', 'side_opposite_angle1' in get_vertices
            # Need to map config.aas_angle1_rad etc. to these.
            # For now, assuming direct mapping for simplicity in this skeleton.
            # Correct mapping for AAS:
            # 'angle1_rad': config.aas_angle1_rad,
            # 'angle2_rad': config.aas_angle2_rad,
            # 'side_opposite_angle1': config.aas_side_a_opposite_p1
        }
        # Filter out None values before passing to get_vertices
        actual_vertex_params = {k: v for k, v in vertex_params.items() if v is not None}
        # Add definition_mode back as it's always required
        actual_vertex_params['definition_mode'] = config.definition_mode
        
        # AAS specific mapping for get_vertices
        if config.definition_mode == 'aas':
            actual_vertex_params['angle1_rad'] = config.aas_angle1_rad
            actual_vertex_params['angle2_rad'] = config.aas_angle2_rad
            actual_vertex_params['side_opposite_angle1'] = config.aas_side_a_opposite_p1
            # Remove potentially conflicting general angle1_rad, angle2_rad if they were None and got included
            actual_vertex_params.pop('angle_rad', None) 
            actual_vertex_params.pop('side_length', None)


        try:
            triangle = construct_triangle(config.definition_mode, **{k: v for k, v in actual_vertex_params.items() if k != 'definition_mode'})
            p1, p2, p3 = (triangle.p1.x, triangle.p1.y), (triangle.p2.x, triangle.p2.y), (triangle.p3.x, triangle.p3.y)
        except (TriangleDefinitionError, ValueError, NotImplementedError) as e:
            # Handle error, maybe return an error message in TikZ
            return f"% Error generating triangle vertices: {e}"

        all_vertices_tuple: Tuple[PointTuple, PointTuple, PointTuple] = (p1, p2, p3)
        
        # 2. 繪製基礎三角形
        triangle_gen = self._get_sub_generator("basic_triangle")
        base_triangle_params_dict: Dict[str, Any] = {
            "p1": p1, "p2": p2, "p3": p3,
            "variant": config.variant
        }
        if config.triangle_draw_options:
            base_triangle_params_dict["draw_options"] = config.triangle_draw_options
        if config.triangle_fill_color:
            base_triangle_params_dict["fill_color"] = config.triangle_fill_color
        
        # Validate with BasicTriangleParams before generating
        try:
            # BasicTriangleParams(**base_triangle_params_dict) # Validation step
            tikz_parts.append(triangle_gen.generate_tikz(base_triangle_params_dict))
        except ValidationError as e_base_tri:
            tikz_parts.append(f"% Error in BasicTriangleParams for base triangle: {e_base_tri}")


        # 3. 處理頂點顯示和標籤 (P1, P2, P3)
        vertex_coords = [p1, p2, p3]
        vertex_configs = [
            config.vertex_p1_display_config,
            config.vertex_p2_display_config,
            config.vertex_p3_display_config
        ]

        label_gen = self._get_sub_generator("label")

        for i, v_coord in enumerate(vertex_coords):
            v_config = vertex_configs[i]
            default_v_label_text = config.default_vertex_labels[i] if i < len(config.default_vertex_labels) else f"V{i+1}"

            if v_config.show_point:
                # v_config.point_style is a PointStyleConfig instance due to default_factory
                p_color = v_config.point_style.color
                # tikz_scale = v_config.point_style.tikz_scale
                point_size_tikz = "1.5pt" # Fixed for now
                tikz_v_coord_x = f"{v_coord[0]:.7g}"
                tikz_v_coord_y = f"{v_coord[1]:.7g}"
                tikz_parts.append(f"\\filldraw[{p_color}] ({tikz_v_coord_x},{tikz_v_coord_y}) circle ({point_size_tikz});")

            if v_config.show_label:
                # v_config.label_style is a LabelStyleConfig instance due to default_factory
                label_style_cfg = v_config.label_style
                
                # 確定標籤文本和 math_mode
                actual_text_for_label = default_v_label_text
                effective_math_mode = True # Default for vertex labels unless overridden

                if label_style_cfg.text_override is not None:
                    actual_text_for_label = label_style_cfg.text_override
                    # 如果 text_override 已包含 $...$，則去除它們，並確保 math_mode 為 True (除非 style 中明確設為 False)
                    if actual_text_for_label.startswith('$') and actual_text_for_label.endswith('$') and len(actual_text_for_label) >= 2:
                        actual_text_for_label = actual_text_for_label[1:-1]
                        if label_style_cfg.math_mode is False: # User explicitly wants non-math for a $-wrapped string
                            effective_math_mode = False
                        else: # Default to math if user provided $
                            effective_math_mode = True
                    elif label_style_cfg.math_mode is not None: # text_override is plain, but style has math_mode
                        effective_math_mode = label_style_cfg.math_mode
                    # else: text_override is plain, math_mode in style is None, use default effective_math_mode (True for vertices)
                elif label_style_cfg.math_mode is not None: # No text_override, but style has math_mode
                     effective_math_mode = label_style_cfg.math_mode
                
                if actual_text_for_label is None:
                    actual_text_for_label = f"Vtx{i+1}" # Fallback

                # 獲取定位參數
                current_offset = label_style_cfg.default_offset_override if label_style_cfg.default_offset_override is not None else config.global_label_default_offset
                
                # 使用新的標籤定位API
                adjacent_vertices = [v for v in vertex_coords if v != v_coord]
                label_params = position_vertex_label_auto(v_coord, adjacent_vertices, current_offset)
                placement_info = {
                    'reference_point': (label_params.position.x, label_params.position.y),
                    'label_anchor': label_params.tikz_anchor,
                    'rotation': label_params.rotation_angle
                }

                # 準備 LabelParams
                label_params_dict: Dict[str, Any] = {
                    "variant": config.variant,
                    "text": actual_text_for_label, # Use processed text
                    "x": placement_info.get('reference_point', v_coord)[0], # Fallback to v_coord
                    "y": placement_info.get('reference_point', v_coord)[1],
                    "anchor": placement_info.get('label_anchor'), # From get_label_placement_params
                    "rotate": placement_info.get('rotation')      # From get_label_placement_params
                }
                
                # 合併樣式: LabelParams defaults < LabelStyleConfig override
                if label_style_cfg.position_modifiers is not None:
                    label_params_dict['position_modifiers'] = label_style_cfg.position_modifiers
                if label_style_cfg.color is not None:
                    label_params_dict['color'] = label_style_cfg.color
                if label_style_cfg.font_size is not None:
                    label_params_dict['font_size'] = label_style_cfg.font_size
                # math_mode is now determined by effective_math_mode
                label_params_dict['math_mode'] = effective_math_mode
                
                if label_style_cfg.additional_node_options is not None:
                    label_params_dict['additional_node_options'] = label_style_cfg.additional_node_options
                
                try:
                    # LabelParams(**label_params_dict) # Validation step
                    tikz_parts.append(label_gen.generate_tikz(label_params_dict))
                except ValidationError as e_label:
                    tikz_parts.append(f"% Error in LabelParams for vertex {i+1}: {e_label}")
        
        # 4. 處理邊顯示和標籤
        # 邊的順序: P1P2 (通常是 c), P2P3 (通常是 a), P3P1 (通常是 b)
        sides_def = [
            (p1, p2, config.side_p1p2_display_config, config.default_side_names[0] if len(config.default_side_names) > 0 else "s1"),
            (p2, p3, config.side_p2p3_display_config, config.default_side_names[1] if len(config.default_side_names) > 1 else "s2"),
            (p3, p1, config.side_p3p1_display_config, config.default_side_names[2] if len(config.default_side_names) > 2 else "s3")
        ]

        for sp, ep, side_config, default_side_name_text in sides_def:
            if side_config.show_label:
                label_style_cfg = side_config.label_style # Guaranteed by default_factory
                actual_text_for_label = ""
                side_len = distance(sp, ep)
                effective_math_mode = False # Default for side labels unless overridden or default_name

                if side_config.label_text_type == 'custom' and side_config.custom_label_text is not None:
                    try:
                        actual_text_for_label = side_config.custom_label_text.format(value=side_len, name=default_side_name_text)
                    except (KeyError, ValueError) as e:
                        tikz_parts.append(f"% Warning: Custom label for side {default_side_name_text} has invalid placeholder(s) or format in '{side_config.custom_label_text}': {e}")
                        actual_text_for_label = side_config.custom_label_text
                    # For custom text, math_mode is determined by style or defaults to False
                    if label_style_cfg.math_mode is not None:
                        effective_math_mode = label_style_cfg.math_mode
                    # else effective_math_mode remains False for custom side labels
                elif side_config.label_text_type == 'length':
                    actual_text_for_label = side_config.length_format.format(value=side_len)
                    if label_style_cfg.math_mode is not None: # Check style for length-based labels
                        effective_math_mode = label_style_cfg.math_mode
                    # else effective_math_mode remains False for length side labels
                elif side_config.label_text_type == 'default_name':
                    actual_text_for_label = default_side_name_text
                    # Default names like 'a', 'b', 'c' usually ARE math mode
                    effective_math_mode = label_style_cfg.math_mode if label_style_cfg.math_mode is not None else True
                
                if not actual_text_for_label:
                    continue

                # If effective_math_mode is True and actual_text_for_label (from custom_label_text)
                # is already $-wrapped, strip the $ for LabelGenerator.
                if effective_math_mode and \
                   side_config.label_text_type == 'custom' and \
                   actual_text_for_label.startswith('$') and \
                   actual_text_for_label.endswith('$') and \
                   len(actual_text_for_label) >= 2:
                    actual_text_for_label = actual_text_for_label[1:-1]
                
                current_offset = label_style_cfg.default_offset_override if label_style_cfg.default_offset_override is not None else config.global_label_default_offset

                # 使用新的標籤定位API
                label_params = position_side_label_auto(sp, ep, all_vertices_tuple, current_offset)
                placement_info = {
                    'reference_point': (label_params.position.x, label_params.position.y),
                    'label_anchor': label_params.tikz_anchor,
                    'rotation': label_params.rotation_angle
                }

                label_params_dict: Dict[str, Any] = {
                    "variant": config.variant,
                    "text": actual_text_for_label,
                    "x": placement_info.get('reference_point', midpoint(sp,ep))[0], # Fallback
                    "y": placement_info.get('reference_point', midpoint(sp,ep))[1],
                    "anchor": placement_info.get('label_anchor'),
                    "rotate": placement_info.get('rotation')
                }

                # 合併樣式
                if label_style_cfg.position_modifiers is not None:
                    label_params_dict['position_modifiers'] = label_style_cfg.position_modifiers
                if label_style_cfg.color is not None:
                    label_params_dict['color'] = label_style_cfg.color
                if label_style_cfg.font_size is not None:
                    label_params_dict['font_size'] = label_style_cfg.font_size
                # math_mode is now determined by effective_math_mode
                label_params_dict['math_mode'] = effective_math_mode
                
                if label_style_cfg.additional_node_options is not None:
                    label_params_dict['additional_node_options'] = label_style_cfg.additional_node_options

                try:
                    # LabelParams(**label_params_dict) # Validation step
                    tikz_parts.append(label_gen.generate_tikz(label_params_dict))
                except ValidationError as e_label:
                    tikz_parts.append(f"% Error in LabelParams for side {default_side_name_text}: {e_label}")

        # 5. 處理角顯示和標籤 (at P1, P2, P3)
        arc_gen = self._get_sub_generator("arc")
        angles_data = [ # vertex, arm_point1, arm_point2, config, default_name
            (p1, p2, p3, config.angle_at_p1_display_config, config.default_angle_names[0] if len(config.default_angle_names) > 0 else "Ang1"),
            (p2, p1, p3, config.angle_at_p2_display_config, config.default_angle_names[1] if len(config.default_angle_names) > 1 else "Ang2"),
            (p3, p1, p2, config.angle_at_p3_display_config, config.default_angle_names[2] if len(config.default_angle_names) > 2 else "Ang3")
        ]

        for v_angle, ap1, ap2, angle_config, default_angle_name_text in angles_data:
            if not angle_config.show_arc and not angle_config.show_label:
                continue

            # 獲取角弧參數 (即使只顯示標籤，也可能需要其半徑來定位標籤)
            current_arc_radius_config = angle_config.arc_radius_config # From AngleDisplayConfig
            # If AngleDisplayConfig.arc_radius_config is None or not set, use global one.
            # However, AngleDisplayConfig.arc_radius_config has a default "auto".
            # So, it will always be "auto" unless overridden in params.
            
            # Determine radius_config for get_arc_render_params:
            # Prioritize angle_config.arc_radius_config if it's set, else use global.
            radius_to_use_for_arc = angle_config.arc_radius_config \
                if angle_config.arc_radius_config is not None \
                else config.global_angle_arc_radius_config

            # 使用新的弧線渲染API
            arc_params = arc_renderer.render_angle_arc(
                vertex=v_angle,
                point1=ap1,
                point2=ap2,
                radius_config=radius_to_use_for_arc
            )
            # 轉換為舊格式以保持兼容
            arc_render_info = {
                'type': 'arc',
                'center': arc_params.center,
                'radius': arc_params.radius,
                'start_angle_rad': arc_params.start_angle,
                'end_angle_rad': arc_params.end_angle
            }

            if angle_config.show_arc and arc_render_info and arc_render_info['type'] == 'arc':
                arc_style_cfg = angle_config.arc_style # Guaranteed by default_factory
                
                # Adjust start/end angles for ArcGenerator to draw inner angle for TikZ
                raw_start_rad = arc_render_info['start_angle_rad']
                raw_end_rad = arc_render_info['end_angle_rad']
                
                # Vectors from vertex (v_angle) to arm points (ap1, ap2)
                vec1_x_for_cross = ap1[0] - v_angle[0]
                vec1_y_for_cross = ap1[1] - v_angle[1]
                vec2_x_for_cross = ap2[0] - v_angle[0]
                vec2_y_for_cross = ap2[1] - v_angle[1]
                cross_product = vec1_x_for_cross * vec2_y_for_cross - vec1_y_for_cross * vec2_x_for_cross

                tikz_arc_start_rad = raw_start_rad
                tikz_arc_end_rad = raw_end_rad

                if cross_product < 0: # Clockwise from arm1 to arm2, TikZ needs to sweep from arm2 to arm1 (CCW)
                    tikz_arc_start_rad = raw_end_rad
                    tikz_arc_end_rad = raw_start_rad
                
                if tikz_arc_end_rad < tikz_arc_start_rad:
                    tikz_arc_end_rad += 2 * math.pi
                
                # If sweep is > 180 deg (and not a straight line), it's the reflex angle.
                # We want the inner angle, so swap again.
                current_sweep = tikz_arc_end_rad - tikz_arc_start_rad
                if current_sweep > math.pi + 1e-9 and current_sweep < (2 * math.pi - 1e-9):
                    # This implies the initial CCW sweep (cross_product > 0) was the reflex one.
                    # So, we should have taken the CW sweep, which means starting from raw_end_rad.
                    # Or, if cross_product < 0, this state should not be reached if logic is correct.
                    # This part of logic might need refinement based on visualizer.
                    # For now, if sweep > 180, assume we need to go the other way.
                    temp_start = tikz_arc_start_rad
                    tikz_arc_start_rad = tikz_arc_end_rad - 2 * math.pi # Effectively the other end
                    tikz_arc_end_rad = temp_start
                    if tikz_arc_end_rad < tikz_arc_start_rad: # Ensure positive sweep
                        tikz_arc_end_rad += 2 * math.pi


                arc_params_dict: Dict[str, Any] = {
                    "variant": config.variant,
                    "center": arc_render_info['center'], # This is v_angle
                    "radius": arc_render_info['radius'],
                    "start_angle_rad": tikz_arc_start_rad, # Use adjusted angles
                    "end_angle_rad": tikz_arc_end_rad,     # Use adjusted angles
                    "draw_options": arc_style_cfg.draw_options
                }
                try:
                    tikz_parts.append(arc_gen.generate_tikz(arc_params_dict))
                except ValidationError as e_arc:
                    tikz_parts.append(f"% Error in ArcParams for angle at {default_angle_name_text}: {e_arc}")

            if angle_config.show_label:
                label_style_cfg = angle_config.label_style # Guaranteed by default_factory
                actual_text_for_label = ""
                effective_math_mode = True # Default for angle labels unless custom or overridden

                # 計算角度值
                vec_v_arm1 = (ap1[0] - v_angle[0], ap1[1] - v_angle[1])
                vec_v_arm2 = (ap2[0] - v_angle[0], ap2[1] - v_angle[1])
                dot_prod = vec_v_arm1[0] * vec_v_arm2[0] + vec_v_arm1[1] * vec_v_arm2[1]
                len1 = distance(v_angle, ap1)
                len2 = distance(v_angle, ap2)
                angle_value_rad = 0.0
                if len1 > 1e-9 and len2 > 1e-9:
                    cos_theta = max(-1.0, min(1.0, dot_prod / (len1 * len2)))
                    angle_value_rad = math.acos(cos_theta)
                angle_value_deg = math.degrees(angle_value_rad)

                if angle_config.label_text_type == 'custom' and angle_config.custom_label_text is not None:
                    try:
                        actual_text_for_label = angle_config.custom_label_text.format(value=angle_value_deg, name=default_angle_name_text)
                    except (KeyError, ValueError) as e:
                        tikz_parts.append(f"% Warning: Custom label for angle {default_angle_name_text} has invalid placeholder(s) or format in '{angle_config.custom_label_text}': {e}")
                        actual_text_for_label = angle_config.custom_label_text
                    # For custom text, math_mode is determined by style or defaults
                    if label_style_cfg.math_mode is not None:
                        effective_math_mode = label_style_cfg.math_mode
                    else: # Custom angle text defaults to non-math unless it contains typical math chars
                        if any(c in actual_text_for_label for c in ['°', '^', '_', '\\']): # Heuristic
                             effective_math_mode = True
                        else:
                             effective_math_mode = False
                elif angle_config.label_text_type == 'value':
                    actual_text_for_label = angle_config.value_format.format(value=angle_value_deg)
                    # Default to math if degree symbol present and not overridden by style
                    if "°" in actual_text_for_label and label_style_cfg.math_mode is None:
                        effective_math_mode = True
                    elif label_style_cfg.math_mode is not None:
                        effective_math_mode = label_style_cfg.math_mode
                    # else effective_math_mode remains True (initial default for angle values)
                elif angle_config.label_text_type == 'default_name':
                    actual_text_for_label = default_angle_name_text
                    # Default names like 'A', 'Alpha' usually ARE math mode
                    effective_math_mode = label_style_cfg.math_mode if label_style_cfg.math_mode is not None else True
                
                if not actual_text_for_label:
                    continue # This continue is inside the for loop and if angle_config.show_label
                
                # If user provided text_override (via custom_label_text) that was already $-wrapped,
                # and effective_math_mode is True, strip the $ for LabelGenerator.
                # This ensures LabelGenerator always receives raw text.
                if effective_math_mode and \
                   angle_config.label_text_type == 'custom' and \
                   actual_text_for_label.startswith('$') and \
                   actual_text_for_label.endswith('$') and \
                   len(actual_text_for_label) >=2 :
                    actual_text_for_label = actual_text_for_label[1:-1]

                current_offset = label_style_cfg.default_offset_override if label_style_cfg.default_offset_override is not None else config.global_label_default_offset

                # 使用新的標籤定位API
                label_params = position_angle_label_auto(v_angle, ap1, ap2, current_offset)
                placement_info = {
                    'reference_point': (label_params.position.x, label_params.position.y),
                    'label_anchor': label_params.tikz_anchor,
                    'rotation': label_params.rotation_angle
                }

                label_params_dict: Dict[str, Any] = {
                    "variant": config.variant,
                    "text": actual_text_for_label,
                    "x": placement_info.get('reference_point', v_angle)[0], # Fallback
                    "y": placement_info.get('reference_point', v_angle)[1],
                    "anchor": placement_info.get('label_anchor'),
                    "rotate": placement_info.get('rotation', 0.0) # Angle labels usually not rotated
                }
                # Merge styles
                if label_style_cfg.position_modifiers is not None:
                    label_params_dict['position_modifiers'] = label_style_cfg.position_modifiers
                if label_style_cfg.color is not None:
                    label_params_dict['color'] = label_style_cfg.color
                if label_style_cfg.font_size is not None:
                    label_params_dict['font_size'] = label_style_cfg.font_size
                
                label_params_dict['math_mode'] = effective_math_mode

                if label_style_cfg.additional_node_options is not None:
                    label_params_dict['additional_node_options'] = label_style_cfg.additional_node_options
                
                try:
                    # LabelParams(**label_params_dict) # Validation
                    tikz_parts.append(label_gen.generate_tikz(label_params_dict))
                except ValidationError as e_label:
                    tikz_parts.append(f"% Error in LabelParams for angle {default_angle_name_text}: {e_label}")

        # 6. 處理特殊點顯示和標籤
        special_points_coords_map: Dict[str, PointTuple] = {} # To store calculated coords
        
        special_point_definitions = [
            ('centroid', config.display_centroid, get_centroid),
            ('incenter', config.display_incenter, get_incenter),
            ('circumcenter', config.display_circumcenter, get_circumcenter),
            ('orthocenter', config.display_orthocenter, get_orthocenter),
        ]

        for name, sp_config, getter_func in special_point_definitions:
            if sp_config: # If display config for this special point exists
                try:
                    # 使用新的特殊點API
                    triangle_obj = Triangle(Point(*p1), Point(*p2), Point(*p3))
                    sp_point = getter_func(triangle_obj)
                    sp_coord = (sp_point.x, sp_point.y)
                    special_points_coords_map[name] = sp_coord

                    if sp_config.show_point:
                        # sp_config.point_style is a PointStyleConfig instance due to default_factory
                        p_color = sp_config.point_style.color # Directly access attribute
                        # tikz_scale = sp_config.point_style.tikz_scale
                        point_size_tikz = "1.2pt" # Fixed for now, can use tikz_scale later
                        tikz_sp_coord_x = f"{sp_coord[0]:.7g}"
                        tikz_sp_coord_y = f"{sp_coord[1]:.7g}"
                        tikz_parts.append(f"\\filldraw[{p_color}] ({tikz_sp_coord_x},{tikz_sp_coord_y}) circle ({point_size_tikz});")

                    if sp_config.show_label:
                        label_style_cfg = sp_config.label_style # Guaranteed by default_factory
                        default_text = config.default_special_point_labels.get(name, name.capitalize()[0]) # Default if no override
                        
                        # Prioritize text_override in label_style, then fallback to default_text
                        text_to_display = label_style_cfg.text_override if label_style_cfg.text_override is not None else default_text
                        
                        current_offset = label_style_cfg.default_offset_override if label_style_cfg.default_offset_override is not None else config.global_label_default_offset
                        
                        # 使用新的標籤定位API - 特殊點當作頂點處理
                        label_params = position_vertex_label_auto(sp_coord, all_vertices_tuple, current_offset)
                        placement_info = {
                            'reference_point': (label_params.position.x, label_params.position.y),
                            'label_anchor': label_params.tikz_anchor,
                            'rotation': label_params.rotation_angle
                        }

                        label_params_dict: Dict[str, Any] = {
                            "variant": config.variant,
                            "text": text_to_display,
                            "x": placement_info.get('reference_point', sp_coord)[0],
                            "y": placement_info.get('reference_point', sp_coord)[1],
                            "anchor": placement_info.get('label_anchor'),
                            "rotate": placement_info.get('rotation')
                        }
                        # Merge styles
                        if label_style_cfg.position_modifiers is not None:
                            label_params_dict['position_modifiers'] = label_style_cfg.position_modifiers
                        if label_style_cfg.color is not None:
                            label_params_dict['color'] = label_style_cfg.color
                        else:
                            label_params_dict['color'] = "darkgray"
                        if label_style_cfg.font_size is not None:
                            label_params_dict['font_size'] = label_style_cfg.font_size
                        if label_style_cfg.math_mode is not None:
                            label_params_dict['math_mode'] = label_style_cfg.math_mode
                        if label_style_cfg.additional_node_options is not None:
                            label_params_dict['additional_node_options'] = label_style_cfg.additional_node_options
                        
                        try:
                            tikz_parts.append(label_gen.generate_tikz(label_params_dict))
                        except ValidationError as e_label:
                            tikz_parts.append(f"% Error in LabelParams for special point {name}: {e_label}")
                
                except (TriangleDefinitionError, ValueError) as e_sp:
                    # Error calculating special point (e.g., collinear for circumcenter/orthocenter)
                    tikz_parts.append(f"% Error calculating special point {name}: {e_sp}")
        
        # --- 組合 TikZ ---
        # Add a scope for the whole figure?
        # final_tikz = "\\begin{scope}\n" + "\n".join(tikz_parts) + "\n\\end{scope}"
        final_tikz = "\n".join(filter(None, tikz_parts))

        return final_tikz