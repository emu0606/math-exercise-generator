#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 複合圖形生成器
"""

from typing import Dict, Any, List, Optional
from pydantic import ValidationError

from .base import FigureGenerator
from .params_models import CompositeParams, SubFigureParams, AbsolutePosition, RelativePosition
from . import register_figure_generator, get_figure_generator

@register_figure_generator
class CompositeFigureGenerator(FigureGenerator):
    """複合圖形生成器
    
    用於組合多個基礎圖形生成器，處理命名空間衝突和定位問題。
    """
    
    @classmethod
    def get_name(cls) -> str:
        """獲取圖形類型唯一標識符"""
        return 'composite'
    
    def generate_tikz(self, params: Dict[str, Any]) -> str:
        """生成複合 TikZ 圖形內容
        
        Args:
            params: 複合圖形參數字典，應符合 CompositeParams 模型
            
        Returns:
            TikZ 圖形內容（不包含 tikzpicture 環境）
            
        Raises:
            ValidationError: 如果參數驗證失敗
        """
        # 使用 Pydantic 模型驗證參數
        try:
            validated_params = CompositeParams(**params)
        except ValidationError as e:
            raise ValidationError(f"複合圖形參數驗證失敗: {str(e)}", e.raw_errors)
        
        # 收集所有需要的 TikZ 庫
        tikz_libraries = set(["positioning"])  # 預設需要 positioning 庫
        
        # 生成子圖形內容
        sub_figure_contents = []
        
        # 記錄已處理的子圖形 ID 和位置
        processed_ids = {}
        
        # 處理每個子圖形
        for i, sub_figure in enumerate(validated_params.sub_figures):
            # 生成唯一的命名空間前綴
            prefix = f"sf{i}_"
            
            # 獲取子圖形 ID（如果未提供則使用索引）
            sub_id = sub_figure.id if sub_figure.id is not None else f"auto_{i}"
            
            # 獲取子圖形生成器
            try:
                generator_cls = get_figure_generator(sub_figure.type)
                generator = generator_cls()
            except ValueError as e:
                raise ValueError(f"子圖形 {i} 類型 '{sub_figure.type}' 無效: {str(e)}")
            
            # 生成子圖形內容（使用命名空間前綴）
            try:
                # 複製參數並添加 variant
                sub_params = dict(sub_figure.params)
                sub_params['variant'] = validated_params.variant
                
                # 生成子圖形內容
                sub_content = generator.generate_tikz(sub_params)
                
                # 替換所有命名空間（假設 TikZ 中的命名使用 \coordinate, \node, \path 等命令）
                # 這是一個簡單的實現，可能需要更複雜的正則表達式來處理所有情況
                for cmd in ["\\coordinate", "\\node", "\\path"]:
                    sub_content = sub_content.replace(f"{cmd} (", f"{cmd} ({prefix}")
                
                # 處理定位
                position_cmd = self._generate_position_command(sub_figure.position, prefix, processed_ids)
                
                # 組合子圖形內容
                scope_content = f"  % 子圖形 {sub_id} (類型: {sub_figure.type})\n"
                scope_content += f"  \\begin{{scope}}[{position_cmd}]\n"
                
                # 縮進子圖形內容
                indented_content = "\n".join(f"    {line}" for line in sub_content.split("\n"))
                scope_content += indented_content + "\n"
                
                scope_content += f"  \\end{{scope}}\n"
                
                # 添加到子圖形內容列表
                sub_figure_contents.append(scope_content)
                
                # 記錄已處理的子圖形 ID 和位置
                processed_ids[sub_id] = sub_figure.position
                
            except Exception as e:
                raise ValueError(f"生成子圖形 {i} (類型: {sub_figure.type}) 時出錯: {str(e)}")
        
        # 組合所有子圖形內容
        tikz_content = "% 複合圖形\n"
        tikz_content += "% 注意：此內容不包含 \\begin{tikzpicture} 和 \\end{tikzpicture}\n"
        tikz_content += f"% 變體: {validated_params.variant}\n\n"
        
        # 添加 TikZ 庫
        if tikz_libraries:
            libraries_str = ", ".join(sorted(tikz_libraries))
            tikz_content += f"\\usetikzlibrary{{{libraries_str}}}\n\n"
        
        # 添加所有子圖形內容
        tikz_content += "\n".join(sub_figure_contents)
        
        return tikz_content
    
    def _generate_position_command(self, position, prefix: str, processed_ids: Dict[str, Any]) -> str:
        """生成 TikZ 定位命令
        
        Args:
            position: 位置參數（AbsolutePosition 或 RelativePosition）
            prefix: 命名空間前綴
            processed_ids: 已處理的子圖形 ID 和位置
            
        Returns:
            TikZ 定位命令
        """
        if isinstance(position, AbsolutePosition):
            # 絕對定位
            return f"shift={{({position.x}, {position.y})}}" # Corrected: removed trailing ]
        elif isinstance(position, RelativePosition):
            # 相對定位
            relative_to = position.relative_to
            placement = position.placement
            distance = position.distance
            
            # 構建定位命令
            cmd = f"{placement}={distance}"
            
            # 添加錨點（如果提供）
            if position.my_anchor is not None:
                cmd += f", anchor={position.my_anchor}"
            
            # 添加目標錨點（如果提供）
            target_prefix = ""
            for id_key, pos in processed_ids.items():
                if id_key == relative_to:
                    # 找到目標 ID，獲取其前綴
                    idx = list(processed_ids.keys()).index(id_key)
                    target_prefix = f"sf{idx}_"
                    break
            
            # 添加 of 部分
            target_node = f"{target_prefix}{relative_to}"
            if position.target_anchor is not None:
                target_node += f".{position.target_anchor}"
            
            cmd += f", of={target_node}"
            
            return cmd
        else:
            # 未知位置類型
            return ""