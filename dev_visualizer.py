#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
開發輔助工具：用於可視化 GeometryUtils 計算結果和圖形元素。
使用 matplotlib 進行繪圖。
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Arc as PlotArc # Renamed to avoid conflict if Arc is defined elsewhere
import math
from typing import Any # Import Any for type hinting

# 假設此腳本與 utils, figures 等目錄在同一級別或 Python 路徑已配置
from utils.geometry.types import Point
from utils.geometry.triangle_constructions import TriangleConstructor, TriangleDefinitionError
from utils.geometry.basic_ops import midpoint, distance
from utils.geometry.triangle_centers import TriangleCenterCalculator
from utils.tikz.arc_renderer import ArcRenderer
from utils.tikz.label_positioner import LabelPositioner

# --- 繪圖輔助函數 ---

def setup_plot(ax, title: str = "Triangle Visualization", aspect_equal: bool = True, grid: bool = True, x_margin: float = 1.0, y_margin: float = 1.0, all_points: list = None):
    """設置 matplotlib Axes 對象的基本屬性"""
    ax.set_title(title)
    if aspect_equal:
        ax.set_aspect('equal', adjustable='box')
    if grid:
        ax.grid(True, linestyle='--', alpha=0.7)
    
    if all_points and all_points: # Check if list is not empty
        min_x = min(p[0] for p in all_points) - x_margin
        max_x = max(p[0] for p in all_points) + x_margin
        min_y = min(p[1] for p in all_points) - y_margin
        max_y = max(p[1] for p in all_points) + y_margin
        ax.set_xlim(min_x, max_x)
        ax.set_ylim(min_y, max_y)
    
    ax.axhline(0, color='black', lw=0.5)
    ax.axvline(0, color='black', lw=0.5)

def draw_point(ax, point: Point, label: str = None, color='blue', marker='o', s=30, text_offset=(0.05, 0.05)):
    """在 Axes 上繪製一個點，可選標籤"""
    ax.scatter(point[0], point[1], color=color, marker=marker, s=s, zorder=5)
    if label:
        ax.text(point[0] + text_offset[0], point[1] + text_offset[1], label, color=color, fontsize=9, zorder=6)

def draw_segment(ax, p1: Point, p2: Point, color='black', linestyle='-', linewidth=1.0, **kwargs):
    """在 Axes 上繪製一條線段"""
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=color, linestyle=linestyle, linewidth=linewidth, **kwargs)

def draw_triangle_sides(ax, p1: Point, p2: Point, p3: Point, **kwargs):
    """繪製三角形的三條邊"""
    draw_segment(ax, p1, p2, **kwargs)
    draw_segment(ax, p2, p3, **kwargs)
    draw_segment(ax, p3, p1, **kwargs)

def draw_arc_matplotlib(ax, center: Point, radius: float,
                        # Pass original arm points to determine sweep direction for inner angle
                        p_on_arm1_for_sweep: Point,
                        p_on_arm2_for_sweep: Point,
                        # raw_start_angle_rad and raw_end_angle_rad are from get_arc_render_params
                        raw_start_angle_rad: float,
                        raw_end_angle_rad: float,
                        color='green', linewidth=1.0, **kwargs):
    """在 Axes 上繪製一個表示內角的角弧"""
    
    # 向量 arm1: center -> p_on_arm1_for_sweep
    # 向量 arm2: center -> p_on_arm2_for_sweep
    vec1_x = p_on_arm1_for_sweep[0] - center[0]
    vec1_y = p_on_arm1_for_sweep[1] - center[1]
    vec2_x = p_on_arm2_for_sweep[0] - center[0]
    vec2_y = p_on_arm2_for_sweep[1] - center[1]

    # 使用原始的 atan2 角度，這些角度定義了射線
    # raw_start_angle_rad 是 vec1 的角度
    # raw_end_angle_rad 是 vec2 的角度
    
    theta1_plot_deg = math.degrees(raw_start_angle_rad)
    theta2_plot_deg = math.degrees(raw_end_angle_rad)

    # 判斷從 vec1 到 vec2 的轉向 (2D 叉積的 Z 分量)
    # cross_product > 0: vec1 到 vec2 是逆時針 (CCW)
    # cross_product < 0: vec1 到 vec2 是順時針 (CW)
    cross_product = vec1_x * vec2_y - vec1_y * vec2_x

    if cross_product < 0: # 從 arm1 到 arm2 是順時針，我們想畫的是逆時針的小角
        # 所以應該從 arm2 (raw_end_angle_rad) 掃描到 arm1 (raw_start_angle_rad)
        theta1_plot_deg = math.degrees(raw_end_angle_rad)
        theta2_plot_deg = math.degrees(raw_start_angle_rad)

    # 確保 matplotlib 的 theta2_plot_deg > theta1_plot_deg 以繪製正確的逆時針弧
    if theta2_plot_deg < theta1_plot_deg:
        theta2_plot_deg += 360.0
    
    # 如果掃描角度大於180度，說明我們可能選錯了方向（例如，對於 cross_product > 0 的情況）
    # 正常的內角掃描不應大於180度（除非是直線上的180度角）
    # 這一層保護確保我們總是畫較小的角
    if (theta2_plot_deg - theta1_plot_deg) > 180.0 + 1e-6 : # 允許微小誤差
         # 如果掃描角大於180，說明初始的 arm1, arm2 順序導致了優角
         # 我們需要反向掃描
         if cross_product > 0: # 原本是CCW，但掃了優角，所以改為從 arm2 到 arm1
            theta1_plot_deg = math.degrees(raw_end_angle_rad)
            theta2_plot_deg = math.degrees(raw_start_angle_rad)
            if theta2_plot_deg < theta1_plot_deg: # 再次確保順序
                theta2_plot_deg += 360.0
         # else cross_product < 0 的情況已在上面處理過交換，理論上不應再到這裡形成 >180 的掃描

    arc_patch = PlotArc((center[0], center[1]), width=2*radius, height=2*radius,
                        angle=0, theta1=theta1_plot_deg, theta2=theta2_plot_deg,
                        color=color, linewidth=linewidth, fill=False, zorder=2, **kwargs)
    ax.add_patch(arc_patch)

# --- 主可視化邏輯 (待擴展) ---

def visualize_triangle_elements(
    triangle_def: dict,
    show_vertex_labels: bool = True,
    show_side_labels: bool = False,
    show_angle_elements: bool = False,
    default_label_offset: float = 0.2,
    arc_radius_config: Any = "auto", # For get_arc_render_params
    angle_label_offset_scale: float = 1.0 # 額外調整角度標籤與角弧的距離
):
    """
    可視化一個三角形及其各種元素（頂點標籤、邊標籤、角弧、角度值標籤等）。
    triangle_def: 傳遞給 get_vertices 的參數字典, e.g., {'definition_mode':'sss', 'side_a':3, ...}
    """
    fig, ax = plt.subplots()
    
    try:
        p1, p2, p3 = get_vertices(**triangle_def)
    except (TriangleDefinitionError, ValueError, NotImplementedError) as e:
        print(f"無法生成三角形: {e}")
        setup_plot(ax, title=f"錯誤: {e}", all_points=[(0,0)]) # Basic plot for error
        plt.show()
        return

    all_triangle_points = [p1, p2, p3]
    plot_title = f"Triangle ({triangle_def.get('definition_mode')})"
    if show_vertex_labels: plot_title += " + Vertex Labels"
    if show_side_labels: plot_title += " + Side Labels"
    setup_plot(ax, title=plot_title, all_points=all_triangle_points)
    
    draw_triangle_sides(ax, p1, p2, p3, color='blue', linewidth=1.5)
    
    # 繪製頂點和頂點標籤
    if show_vertex_labels:
        vertex_map = {'P1': p1, 'P2': p2, 'P3': p3}
        for name, v_coord in vertex_map.items():
            draw_point(ax, v_coord, label=name, color='darkblue', s=50)
            
            label_params_input = {
                'element_type': 'vertex',
                'target_elements': {'vertex_coord': v_coord},
                'all_vertices': (p1, p2, p3),
                'special_points': {},
                'user_preference': "auto",
                'default_offset': default_label_offset
            }
            placement_info = get_label_placement_params(**label_params_input)
            ref_point = placement_info.get('reference_point')
            
            if ref_point:
                ax.text(ref_point[0], ref_point[1], name,
                        color='red', fontsize=10, ha='center', va='center',
                        bbox=dict(facecolor='white', alpha=0.5, pad=0.1, boxstyle='round,pad=0.2'))
                draw_point(ax, ref_point, color='magenta', marker='x', s=20)

    # 繪製邊標籤
    if show_side_labels:
        sides = [
            (p1, p2, "c"), # Side c (P1P2)
            (p2, p3, "a"), # Side a (P2P3)
            (p3, p1, "b")  # Side b (P3P1)
        ]
        for sp, ep, side_name_label in sides:
            side_len = _distance(sp, ep)
            label_text = f"{side_name_label}={side_len:.2f}"
            
            label_params_input = {
                'element_type': 'side',
                'target_elements': {'p_start': sp, 'p_end': ep},
                'all_vertices': (p1, p2, p3),
                'special_points': {},
                'user_preference': "auto",
                'default_offset': default_label_offset / 2 # 邊標籤偏移可以小一些
            }
            placement_info = get_label_placement_params(**label_params_input)
            
            ref_point = placement_info.get('reference_point')
            rotation = placement_info.get('rotation', 0)
            # label_anchor = placement_info.get('label_anchor', 'c') # 應為 'c'

            if ref_point:
                ax.text(ref_point[0], ref_point[1], label_text,
                        color='darkgreen', fontsize=9, ha='center', va='center', rotation=rotation,
                        bbox=dict(facecolor='white', alpha=0.7, pad=0.1, boxstyle='round,pad=0.1'))
                draw_point(ax, ref_point, color='cyan', marker='x', s=20)

    # 繪製角弧和角度值標籤
    if show_angle_elements:
        angles_def = [
            (p1, p2, p3, "A"), # Angle at P1, formed by P1P2 and P1P3
            (p2, p1, p3, "B"), # Angle at P2, formed by P2P1 and P2P3
            (p3, p1, p2, "C")  # Angle at P3, formed by P3P1 and P3P2
        ]
        for vertex, arm_pt1, arm_pt2, angle_name in angles_def:
            # 獲取角弧參數
            # 注意：get_arc_render_params 的 p_on_arm1, p_on_arm2 是從 vertex 出發的點
            arc_render_info = get_arc_render_params(
                vertex, arm_pt1, arm_pt2,
                radius_config=arc_radius_config,
                is_right_angle_symbol=False # 假設總是畫弧
            )
            if arc_render_info and arc_render_info['type'] == 'arc':
                draw_arc_matplotlib(ax,
                                  center=vertex, # arc_render_info['center'] is vertex
                                  radius=arc_render_info['radius'],
                                  p_on_arm1_for_sweep=arm_pt1, # Pass original arm points
                                  p_on_arm2_for_sweep=arm_pt2,
                                  raw_start_angle_rad=arc_render_info['start_angle_rad'],
                                  raw_end_angle_rad=arc_render_info['end_angle_rad'],
                                  color='orange', linewidth=1.2)

                # 計算角度值 (度)
                vec_v_arm1 = (arm_pt1[0] - vertex[0], arm_pt1[1] - vertex[1])
                vec_v_arm2 = (arm_pt2[0] - vertex[0], arm_pt2[1] - vertex[1])
                dot_product = vec_v_arm1[0]*vec_v_arm2[0] + vec_v_arm1[1]*vec_v_arm2[1]
                len1 = math.sqrt(vec_v_arm1[0]**2 + vec_v_arm1[1]**2)
                len2 = math.sqrt(vec_v_arm2[0]**2 + vec_v_arm2[1]**2)
                if len1 > 1e-9 and len2 > 1e-9:
                    cos_theta = max(-1.0, min(1.0, dot_product / (len1 * len2))) # Clamp for float errors
                    angle_val_rad = math.acos(cos_theta)
                    angle_val_deg = math.degrees(angle_val_rad)
                    angle_text = f"{angle_val_deg:.1f}°"

                    # 獲取角度值標籤的放置參數
                    # 使用一個稍大的偏移比例，或者基於 arc_render_info['radius']
                    angle_label_offset = default_label_offset * angle_label_offset_scale
                    
                    label_params_input_angle = {
                        'element_type': 'angle_value',
                        'target_elements': {'vertex': vertex, 'p_on_arm1': arm_pt1, 'p_on_arm2': arm_pt2},
                        'all_vertices': (p1, p2, p3),
                        'special_points': {},
                        'user_preference': "auto",
                        'default_offset': angle_label_offset
                    }
                    placement_info_angle = get_label_placement_params(**label_params_input_angle)
                    ref_point_angle = placement_info_angle.get('reference_point')
                    
                    if ref_point_angle:
                        ax.text(ref_point_angle[0], ref_point_angle[1], angle_text,
                                color='purple', fontsize=8, ha='center', va='center',
                                bbox=dict(facecolor='white', alpha=0.6, pad=0.1, boxstyle='round,pad=0.1'))
                        draw_point(ax, ref_point_angle, color='indigo', marker='x', s=15)

    plt.show()


if __name__ == "__main__":
    print("運行開發可視化工具...")

    # 示例1: SSS 三角形 (3-4-5)
    sss_triangle = {'definition_mode': 'sss', 'side_a': 3, 'side_b': 4, 'side_c': 5}
    visualize_triangle_elements(sss_triangle,
                                show_vertex_labels=True,
                                show_side_labels=True,
                                show_angle_elements=True,
                                arc_radius_config=0.4) # Smaller fixed radius for arcs

    # 示例2: 等腰三角形 (用於測試頂點標籤)
    isosceles_peak_y = 3.0
    isosceles_base_half = 2.0
    p1_iso = (isosceles_base_half, isosceles_peak_y) # Peak
    p2_iso = (0.0, 0.0)
    p3_iso = (2 * isosceles_base_half, 0.0)
    
    coord_triangle_iso = {
        'definition_mode': 'coordinates', 
        'p1': p1_iso, 'p2': p2_iso, 'p3': p3_iso
    }
    visualize_triangle_elements(coord_triangle_iso,
                                show_vertex_labels=True,
                                show_side_labels=True,
                                show_angle_elements=True,
                                default_label_offset=0.3,
                                arc_radius_config="auto") # Use "auto" or a float, dict not yet supported by get_arc_render_params

    # 示例3: SAS 三角形
    sas_triangle = {'definition_mode': 'sas', 'side1': 4, 'angle_rad': math.pi/3, 'side2': 3} # 60度角
    visualize_triangle_elements(sas_triangle,
                                show_vertex_labels=True,
                                show_side_labels=True,
                                show_angle_elements=True,
                                default_label_offset=0.25,
                                arc_radius_config=0.35)