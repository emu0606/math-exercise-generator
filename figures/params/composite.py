#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 複合圖形參數

此模組定義了複合圖形系統的參數模型，允許將多個基礎圖形
組合成複雜的圖形結構。支援絕對定位和相對定位，並提供
完整的依賴關係管理和驗證功能。

主要組件：
1. **子圖形參數模型**: 定義單個子圖形的參數
2. **複合圖形參數模型**: 管理子圖形集合和佈局
3. **定位系統**: 支援絕對和相對定位模式
4. **依賴關係驗證**: 確保相對定位引用的正確性

複合圖形系統特點：
- 支援任意數量的子圖形組合
- 靈活的定位控制（絕對/相對）
- 自動驗證依賴關係和引用完整性
- 支援嵌套和複雜的圖形佈局
- 與基礎圖形參數完全兼容

Example:
    創建包含圓和點的複合圖形::
    
        from figures.params.composite import CompositeParams, SubFigureParams
        from figures.params.base import AbsolutePosition, RelativePosition
        
        composite = CompositeParams(
            variant='explanation',
            sub_figures=[
                SubFigureParams(
                    id='center_circle',
                    type='circle', 
                    params={'radius': 2.0, 'variant': 'question'},
                    position=AbsolutePosition(x=0, y=0)
                ),
                SubFigureParams(
                    type='point',
                    params={'x': 2, 'y': 0, 'label': 'P'},
                    position=RelativePosition(
                        relative_to='center_circle',
                        placement='right',
                        distance='0cm'
                    )
                )
            ]
        )

Note:
    - 子圖形定義順序決定渲染順序
    - 相對定位只能引用之前定義的圖形 ID
    - 驗證器自動檢查引用完整性和循環依賴
    - 支援與所有基礎圖形類型的組合
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Union, Optional, Literal
from .base import BaseFigureParams, AbsolutePosition, RelativePosition

class SubFigureParams(BaseModel):
    """子圖形參數模型
    
    定義複合圖形中單個子圖形的完整參數，包括圖形類型、
    參數配置和位置資訊。每個子圖形可以獨立配置樣式
    和行為，並通過位置系統進行精確佈局。
    
    Attributes:
        id (Optional[str]): 子圖形的唯一標識符，用於相對定位引用。
            為 None 時表示該子圖形不需要被其他圖形引用。
        type (str): 基礎圖形類型名稱，如 'circle', 'triangle', 'point' 等
        params (Dict[str, Any]): 基礎圖形的參數字典，必須匹配對應圖形的
            Pydantic 模型結構
        position (Union[AbsolutePosition, RelativePosition]): 圖形定位配置，
            預設為絕對定位在原點 (0, 0)
            
    Example:
        絕對定位的圓形::
        
            circle_sub = SubFigureParams(
                id='main_circle',
                type='circle',
                params={
                    'radius': 1.5,
                    'color': 'blue',
                    'fill_color': 'lightblue',
                    'variant': 'question'
                },
                position=AbsolutePosition(x=2, y=1)
            )
            
        相對定位的標籤::
        
            label_sub = SubFigureParams(
                type='label',
                params={
                    'text': '圓心',
                    'color': 'red',
                    'variant': 'explanation'
                },
                position=RelativePosition(
                    relative_to='main_circle',
                    placement='above',
                    distance='0.5cm'
                )
            )
            
    Note:
        - id 必須為有效的標識符（字母、數字、下劃線）
        - params 字典的內容必須與圖形類型的參數模型匹配
        - position 決定圖形在複合結構中的位置
        - 相對定位的 relative_to 必須引用已定義的 id
    """
    id: Optional[str] = Field(default=None, description="用於相對定位的引用 ID")
    type: str = Field(..., description="基礎圖形類型")
    params: Dict[str, Any] = Field(..., description="基礎圖形的參數")
    position: Union[AbsolutePosition, RelativePosition] = Field(
        default_factory=AbsolutePosition,
        description="圖形定位配置"
    )
    
    @validator('id')
    def id_must_be_valid(cls, v):
        """驗證 ID 格式的有效性"""
        if v is not None and not v.isalnum() and not all(c.isalnum() or c == '_' for c in v):
            raise ValueError('ID 只能包含字母、數字和下劃線')
        return v

class CompositeParams(BaseFigureParams):
    """複合圖形參數模型
    
    用於定義由多個子圖形組成的複雜圖形結構。支援絕對定位
    和相對定位，並提供完整的依賴關係驗證。複合圖形系統
    允許創建任意複雜度的圖形組合。
    
    複合圖形功能：
    1. **圖形組合**: 將多個基礎圖形組合成統一結構
    2. **定位管理**: 支援絕對和相對定位模式
    3. **依賴驗證**: 自動驗證相對定位的引用完整性
    4. **層次渲染**: 按定義順序渲染子圖形
    5. **ID 系統**: 通過唯一標識符管理圖形引用
    
    Attributes:
        sub_figures (List[SubFigureParams]): 子圖形列表，至少包含一個子圖形。
            每個子圖形定義了類型、參數和定位資訊。列表順序決定渲染順序。
            
    Example:
        創建三角形與內心的複合圖形::
        
            composite = CompositeParams(
                variant='explanation',
                sub_figures=[
                    # 主三角形
                    SubFigureParams(
                        id='main_triangle',
                        type='triangle',
                        params={
                            'points': [[0, 0], [4, 0], [2, 3]],
                            'show_labels': True,
                            'label_names': ['A', 'B', 'C'],
                            'variant': 'question'
                        },
                        position=AbsolutePosition(x=0, y=0)
                    ),
                    # 內心點
                    SubFigureParams(
                        id='incenter',
                        type='point',
                        params={
                            'x': 2, 'y': 1,  # 計算得出的內心座標
                            'label': 'I',
                            'color': 'red',
                            'variant': 'explanation'
                        },
                        position=AbsolutePosition(x=2, y=1)
                    ),
                    # 內切圓
                    SubFigureParams(
                        type='circle',
                        params={
                            'center': [2, 1],
                            'radius': 1,
                            'color': 'green',
                            'variant': 'explanation'
                        },
                        position=RelativePosition(
                            relative_to='incenter',
                            placement='center',  # 以內心為圓心
                            distance='0cm'
                        )
                    )
                ]
            )
            
        創建座標系統與函數圖形::
        
            func_graph = CompositeParams(
                variant='question',
                sub_figures=[
                    # 座標系統背景
                    SubFigureParams(
                        id='coord_system',
                        type='coordinate_system',
                        params={
                            'x_range': [-3, 3],
                            'y_range': [-2, 4],
                            'show_grid': True,
                            'variant': 'question'
                        },
                        position=AbsolutePosition(x=0, y=0)
                    ),
                    # 拋物線上的點
                    SubFigureParams(
                        type='point',
                        params={
                            'x': 1, 'y': 1,
                            'label': 'P(1,1)',
                            'variant': 'explanation'
                        },
                        position=RelativePosition(
                            relative_to='coord_system',
                            placement='center',
                            distance='0cm'
                        )
                    )
                ]
            )
            
    Validation Rules:
        1. **ID 唯一性**: 所有提供的 ID 必須在子圖形列表中唯一
        2. **引用有效性**: 相對定位的 relative_to 必須引用已定義的 ID
        3. **定義順序**: 被引用的子圖形必須在引用它的子圖形之前定義
        4. **無循環依賴**: 相對定位不能形成循環引用
        
    Note:
        - 子圖形的定義順序很重要，決定了渲染層次
        - ID 系統建立子圖形間的引用關係
        - 驗證器確保所有引用的有效性和完整性
        - 支援任意深度的圖形組合和定位關係
        - 每個子圖形可以有不同的 variant 設定
    """
    sub_figures: List[SubFigureParams] = Field(..., min_items=1, description="子圖形列表")
    
    @validator('sub_figures')
    def validate_sub_figures(cls, v):
        """驗證子圖形列表的完整性和一致性
        
        執行以下驗證：
        1. 確保子圖形中 ID 的唯一性（如果提供）
        2. 確保相對定位的 'relative_to' 引用已定義的 ID
        3. 確保引用順序正確（被引用的圖形必須先定義）
        4. 檢測並防止循環引用
        
        Args:
            v: 子圖形列表
            
        Returns:
            驗證通過的子圖形列表
            
        Raises:
            ValueError: 當發現以下問題時拋出異常
                - 重複的 ID
                - 引用未定義的 ID  
                - 引用順序錯誤
                - 循環依賴
        """
        ids = set()
        dependencies = {}  # id -> set of ids it depends on
        
        for i, sub_figure in enumerate(v):
            # 檢查 ID 唯一性
            if sub_figure.id is not None:
                if sub_figure.id in ids:
                    raise ValueError(f"重複的子圖形 ID: {sub_figure.id}")
                ids.add(sub_figure.id)
                dependencies[sub_figure.id] = set()
            
            # 檢查相對定位引用
            if isinstance(sub_figure.position, RelativePosition):
                relative_to = sub_figure.position.relative_to
                
                # 確保引用的 ID 存在且在當前子圖形之前定義
                if relative_to not in ids:
                    raise ValueError(
                        f"子圖形 {i} 引用了未定義或後定義的 ID: {relative_to}。"
                        f"請確保被引用的圖形在引用它的圖形之前定義。"
                    )
                
                # 記錄依賴關係
                current_id = sub_figure.id or f"_anonymous_{i}"
                if current_id not in dependencies:
                    dependencies[current_id] = set()
                dependencies[current_id].add(relative_to)
        
        # 檢查循環依賴
        def has_cycle(graph):
            """使用深度優先搜尋檢測有向圖中的循環"""
            WHITE, GRAY, BLACK = 0, 1, 2
            colors = {node: WHITE for node in graph}
            
            def dfs(node):
                if colors[node] == GRAY:
                    return True  # 發現循環
                if colors[node] == BLACK:
                    return False  # 已完成處理
                
                colors[node] = GRAY
                for neighbor in graph.get(node, set()):
                    if neighbor in colors and dfs(neighbor):
                        return True
                colors[node] = BLACK
                return False
            
            for node in graph:
                if colors[node] == WHITE and dfs(node):
                    return True
            return False
        
        if has_cycle(dependencies):
            raise ValueError("檢測到子圖形間的循環依賴關係，這會導致無法解析的定位問題")
        
        return v

class LayoutParams(BaseModel):
    """佈局參數模型
    
    定義複合圖形的整體佈局配置，包括對齊方式、間距
    和分佈規則。用於自動化複合圖形的佈局管理。
    
    Attributes:
        align (Literal): 子圖形的對齊方式
        spacing (float): 子圖形間的標準間距
        direction (Literal): 佈局方向
        wrap (bool): 是否允許換行佈局
        margin (float): 整體佈局的外邊距
        
    Note:
        - 此功能為未來擴展預留
        - 可用於實現自動佈局算法
        - 與手動定位系統並行使用
    """
    align: Literal['left', 'center', 'right', 'top', 'bottom'] = Field(
        default='center', 
        description="子圖形對齊方式"
    )
    spacing: float = Field(default=1.0, ge=0, description="子圖形間距")
    direction: Literal['horizontal', 'vertical', 'grid'] = Field(
        default='horizontal',
        description="佈局方向"
    )
    wrap: bool = Field(default=False, description="是否允許換行")
    margin: float = Field(default=0.5, ge=0, description="外邊距")

class GroupParams(BaseFigureParams):
    """圖形群組參數模型
    
    將多個相關的子圖形組織成邏輯群組，支援群組級別的
    樣式控制和變換操作。
    
    Attributes:
        sub_figures (List[SubFigureParams]): 群組包含的子圖形
        group_style (Optional[Dict]): 群組級別的樣式覆蓋
        transform (Optional[Dict]): 群組變換參數（旋轉、縮放等）
        layout (Optional[LayoutParams]): 群組內的佈局配置
        
    Example:
        創建函數圖形群組::
        
            function_group = GroupParams(
                variant='explanation',
                sub_figures=[...],  # 函數相關的多個圖形
                group_style={'color': 'blue', 'line_width': 'thick'},
                transform={'scale': 1.2, 'rotate': 15}
            )
    """
    sub_figures: List[SubFigureParams] = Field(..., min_items=1, description="群組子圖形")
    group_style: Optional[Dict[str, Any]] = Field(default=None, description="群組樣式覆蓋")
    transform: Optional[Dict[str, Any]] = Field(default=None, description="群組變換參數")
    layout: Optional[LayoutParams] = Field(default=None, description="群組佈局配置")