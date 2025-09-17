#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 複合圖形生成器

本模組提供複合圖形的生成功能，允許將多個基礎圖形組合成
一個複雜的圖形，支援絕對和相對定位、命名空間管理和自動對齊。
"""

from typing import Dict, Any, List, Optional
from pydantic import ValidationError

from utils import Point, global_config, get_logger
from .base import FigureGenerator
from .params import CompositeParams, SubFigureParams, AbsolutePosition, RelativePosition
from . import register_figure_generator, get_figure_generator

logger = get_logger(__name__)

@register_figure_generator
class CompositeFigureGenerator(FigureGenerator):
    """複合圖形生成器
    
    允許將多個基礎圖形組合成一個複雜的圖形，自動處理命名空間衝突、
    定位計算和子圖形之間的相依關係。使用新架構的統一 API，
    整合幾何計算和日誌系統。
    
    支援的功能：
    - 多個子圖形的組合和對齊
    - 絕對定位和相對定位系統
    - 自動命名空間管理避免衝突
    - TikZ 庫的自動載入和管理
    - 子圖形依賴關係的驗證
    
    Attributes:
        logger: 模組日誌記錄器
        config: 全域配置物件
        
    Example:
        >>> generator = CompositeFigureGenerator()
        >>> params = {
        ...     'variant': 'question',
        ...     'sub_figures': [
        ...         {
        ...             'id': 'circle1',
        ...             'type': 'circle',
        ...             'params': {'radius': 1.0},
        ...             'position': {'type': 'absolute', 'x': 0, 'y': 0}
        ...         },
        ...         {
        ...             'id': 'point1',
        ...             'type': 'point',
        ...             'params': {'x': 1, 'y': 0},
        ...             'position': {'type': 'absolute', 'x': 0, 'y': 0}
        ...         }
        ...     ]
        ... }
        >>> tikz_code = generator.generate_tikz(params)
        >>> 'usetikzlibrary{positioning}' in tikz_code
        True
        
    Note:
        此生成器使用 TikZ 的 scope 環境和 positioning 庫管理複雜定位。
        命名空間使用前綴 'sf{i}_' 格式避免衝突。
    """
    
    @classmethod
    def get_name(cls) -> str:
        """獲取圖形類型唯一標識符"""
        return 'composite'
    
    def generate_tikz(self, params: Dict[str, Any]) -> str:
        """生成複合圖形 TikZ 內容
        
        將多個子圖形組合成一個統一的複合圖形，處理它們之間的
        定位關係和命名空間管理。
        
        Args:
            params (Dict[str, Any]): 複合圖形參數字典，支援的鍵值包括：
                - variant (str): 變體類型，'question' 或 'explanation'
                - sub_figures (List[Dict]): 子圖形列表，每個包含：
                  - id (str, optional): 子圖形的唯一標識符
                  - type (str): 子圖形類型（必須是已註冊的生成器）
                  - params (Dict): 子圖形的參數
                  - position (Dict): 子圖形的位置設定
                    - type: 'absolute' 或 'relative'
                    - 絕對定位: x, y 坐標
                    - 相對定位: relative_to, placement, distance 等
                
        Returns:
            str: TikZ 圖形內容（不包含 tikzpicture 環境），
                 包含所有子圖形和必要的 TikZ 庫導入
                
        Raises:
            ValidationError: 如果參數驗證失敗或包含無效值
            ValueError: 如果子圖形類型不存在或定位參數無效
            
        Example:
            >>> generator = CompositeFigureGenerator()
            >>> params = {
            ...     'variant': 'question',
            ...     'sub_figures': [
            ...         {
            ...             'type': 'circle',
            ...             'params': {'radius': 1.0, 'center': (0, 0)},
            ...             'position': {'type': 'absolute', 'x': 0, 'y': 0}
            ...         }
            ...     ]
            ... }
            >>> result = generator.generate_tikz(params)
            >>> 'begin{scope}' in result
            True
            >>> 'usetikzlibrary' in result
            True
            
        Note:
            每個子圖形都會被包裝在獨立的 TikZ scope 中。
            自動管理命名空間以避免節點名稱衝突。
        """
        # 使用新架構的參數模型驗證
        try:
            validated_params = CompositeParams(**params)
            logger.debug(f"複合圖形參數驗證成功: {len(validated_params.sub_figures)} 個子圖形, 變體={validated_params.variant}")
        except ValidationError as e:
            logger.error(f"複合圖形參數驗證失敗: {str(e)}")
            raise ValueError(f"複合圖形參數驗證失敗: {str(e)}")
        
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
                
                # 使用新架構處理定位計算
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
        
        logger.debug(f"生成複合圖形 TikZ 代碼: {len(validated_params.sub_figures)} 個子圖形組合完成")
        
        return tikz_content
    
    def _generate_position_command(self, position, prefix: str, processed_ids: Dict[str, Any]) -> str:
        """生成 TikZ 定位命令
        
        根據位置參數的類型生成相應的 TikZ 定位命令，支援絕對和相對定位。
        
        Args:
            position: 位置參數對象，可為 AbsolutePosition 或 RelativePosition
            prefix (str): 當前子圖形的命名空間前綴
            processed_ids (Dict[str, Any]): 已處理的子圖形 ID 和位置的對應關係
            
        Returns:
            str: 用於 TikZ scope 的定位命令字串
            
        Example:
            >>> generator = CompositeFigureGenerator()
            >>> abs_pos = AbsolutePosition(x=1.0, y=2.0)
            >>> cmd = generator._generate_position_command(abs_pos, "sf0_", {})
            >>> "shift={(1.0, 2.0)}" in cmd
            True
            
        Note:
            相對定位需要目標子圖形已經被處理，否則會失敗。
        """
        if isinstance(position, AbsolutePosition):
            # 絕對定位，使用 Point 類型處理座標
            position_point = Point(position.x, position.y)
            return f"shift={{{position_point.to_tikz()}}}"
        elif isinstance(position, RelativePosition):
            # 相對定位，使用新架構的幾何計算
            relative_to = position.relative_to
            placement = position.placement
            distance = position.distance
            
            # 構建定位命令
            cmd = f"{placement}={distance}"
            
            # 添加錨點（如果提供）
            if position.my_anchor is not None:
                cmd += f", anchor={position.my_anchor}"
            
            # 尋找目標子圖形的前綴
            target_prefix = ""
            for id_key, pos in processed_ids.items():
                if id_key == relative_to:
                    # 找到目標 ID，獲取其前綴
                    idx = list(processed_ids.keys()).index(id_key)
                    target_prefix = f"sf{idx}_"
                    logger.debug(f"相對定位: 目標 '{relative_to}' 找到，前綴='{target_prefix}'")
                    break
            
            if not target_prefix:
                logger.warning(f"相對定位: 找不到目標 '{relative_to}'，可能造成定位錯誤")
            
            # 添加 of 部分
            target_node = f"{target_prefix}{relative_to}"
            if position.target_anchor is not None:
                target_node += f".{position.target_anchor}"
            
            cmd += f", of={target_node}"
            
            return cmd
        else:
            # 未知位置類型
            return ""