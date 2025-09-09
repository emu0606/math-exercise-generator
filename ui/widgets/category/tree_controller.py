#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 分類樹狀結構控制器

負責管理分類選擇器的樹狀結構邏輯，包括節點展開/收折、
父子關係維護、狀態同步等核心功能。

從原始 category_widget.py 中分離出的樹狀結構相關邏輯：
- populate_categories() - 填充分類數據  
- clear_categories() - 清空分類
- toggle_container() - 展開/收折控制
- expand_all_categories() - 全展開
- collapse_all_categories() - 全收折
- update_parent_checkbox_state() - 父節點狀態更新

重構收益：
- 職責清晰: 只負責樹狀結構控制邏輯
- 可測試性: 邏輯獨立，易於單元測試
- 可復用性: 可被其他樹狀組件復用
- 新架構整合: 充分利用日誌和配置系統
"""

from typing import Dict, List, Any, Optional, Tuple
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFrame, QCheckBox
from PyQt5.QtCore import Qt, pyqtSignal

from utils import get_logger, global_config
from ui.components.base import BaseWidget

class TreeController(BaseWidget):
    """
    分類樹狀結構控制器
    
    管理分類選擇器的樹狀結構，提供節點管理、狀態維護、
    展開控制等核心功能。使用新架構工具確保高品質實現。
    
    主要功能：
    - 樹狀數據結構管理
    - 節點展開/收折控制
    - 父子節點狀態同步
    - 批量操作支援 (全展開/全收折)
    
    Signals:
        tree_structure_changed: 樹狀結構變更時發出
        node_expanded: 節點展開時發出
        node_collapsed: 節點收折時發出
        parent_state_updated: 父節點狀態更新時發出
    
    Example:
        >>> controller = TreeController()
        >>> controller.populate_tree(categories_data)
        >>> controller.expand_all()
        >>> 
        >>> # 監聽結構變更
        >>> controller.tree_structure_changed.connect(on_tree_changed)
    """
    
    # 樹狀結構相關信號
    tree_structure_changed = pyqtSignal()
    node_expanded = pyqtSignal(str)      # node_id
    node_collapsed = pyqtSignal(str)     # node_id
    parent_state_updated = pyqtSignal(str, int)  # parent_id, new_state
    
    def __init__(self, parent=None, config=None):
        """
        初始化樹狀結構控制器
        
        Args:
            parent: 父組件
            config: 配置字典，支援以下選項：
                - auto_expand: 是否自動展開第一層 (預設: False)
                - max_expand_level: 最大展開層級 (預設: 無限制)
                - expand_animation: 是否啟用展開動畫 (預設: True)
        """
        self._category_widgets = []      # 分類組件列表
        self._subcategory_widgets = []   # 子分類組件列表
        self._node_states = {}           # 節點狀態字典 {node_id: expanded}
        
        super().__init__(parent, config)
        
        # 應用配置
        self.auto_expand = self.get_config_value('auto_expand', False)
        self.max_expand_level = self.get_config_value('max_expand_level', -1)
        self.expand_animation = self.get_config_value('expand_animation', True)
        
        self.logger.info("樹狀結構控制器初始化完成")
    
    def _setup_ui(self):
        """建立UI結構 - 控制器不需要可視UI"""
        pass
    
    def _connect_signals(self):
        """連接信號 - 控制器主要提供API，不需要內部信號連接"""
        pass
    
    def populate_tree(self, categories_data: List[Dict[str, Any]]) -> bool:
        """
        填充樹狀結構數據
        
        Args:
            categories_data: 分類數據列表，格式：
                [{"name": "分類名", "subcategories": ["子分類1", "子分類2"]}, ...]
                
        Returns:
            是否填充成功
            
        Example:
            >>> data = [
            ...     {"name": "代數", "subcategories": ["一次方程式", "二次方程式"]},
            ...     {"name": "幾何", "subcategories": ["三角形", "圓形"]}
            ... ]
            >>> controller.populate_tree(data)
        """
        try:
            # 清空現有數據
            self.clear_tree()
            
            self.logger.info(f"開始填充樹狀結構: {len(categories_data)} 個分類")
            
            for category_index, category in enumerate(categories_data):
                category_name = category.get('name', f'Category_{category_index}')
                subcategories = category.get('subcategories', [])
                
                # 記錄分類節點
                category_id = f"cat_{category_index}_{category_name}"
                self._node_states[category_id] = not self.auto_expand  # 初始狀態相反，因為後面會切換
                
                self.logger.debug(f"添加分類: {category_name}, {len(subcategories)} 個子分類")
                
                # 記錄子分類節點
                for subcat_index, subcat_name in enumerate(subcategories):
                    subcat_id = f"subcat_{category_index}_{subcat_index}_{subcat_name}"
                    # 子分類初始狀態總是可見的（如果父分類展開）
                    
            # 應用自動展開設定
            if self.auto_expand:
                self.expand_all(max_level=1)
                
            self.tree_structure_changed.emit()
            self.logger.info("樹狀結構填充完成")
            return True
            
        except Exception as e:
            self.logger.error(f"填充樹狀結構失敗: {e}")
            return False
    
    def clear_tree(self) -> None:
        """
        清空樹狀結構
        
        清除所有節點數據和狀態，重置控制器到初始狀態。
        """
        try:
            self.logger.debug("清空樹狀結構開始")
            
            # 清空數據結構
            self._category_widgets.clear()
            self._subcategory_widgets.clear()
            self._node_states.clear()
            
            self.tree_structure_changed.emit()
            self.logger.info("樹狀結構清空完成")
            
        except Exception as e:
            self.logger.error(f"清空樹狀結構失敗: {e}")
    
    def toggle_node(self, node_id: str) -> bool:
        """
        切換節點展開/收折狀態
        
        Args:
            node_id: 節點ID
            
        Returns:
            操作是否成功
        """
        try:
            if node_id not in self._node_states:
                self.logger.warning(f"節點不存在: {node_id}")
                return False
            
            # 切換狀態
            current_state = self._node_states[node_id]
            new_state = not current_state
            self._node_states[node_id] = new_state
            
            # 發送對應信號
            if new_state:
                self.logger.debug(f"展開節點: {node_id}")
                self.node_expanded.emit(node_id)
            else:
                self.logger.debug(f"收折節點: {node_id}")
                self.node_collapsed.emit(node_id)
            
            return True
            
        except Exception as e:
            self.logger.error(f"切換節點狀態失敗: {node_id}, 錯誤: {e}")
            return False
    
    def expand_node(self, node_id: str) -> bool:
        """
        展開指定節點
        
        Args:
            node_id: 節點ID
            
        Returns:
            操作是否成功
        """
        try:
            if node_id not in self._node_states:
                return False
                
            if not self._node_states[node_id]:  # 如果當前是收折狀態
                return self.toggle_node(node_id)
            
            return True  # 已經是展開狀態
            
        except Exception as e:
            self.logger.error(f"展開節點失敗: {node_id}, 錯誤: {e}")
            return False
    
    def collapse_node(self, node_id: str) -> bool:
        """
        收折指定節點
        
        Args:
            node_id: 節點ID
            
        Returns:
            操作是否成功
        """
        try:
            if node_id not in self._node_states:
                return False
                
            if self._node_states[node_id]:  # 如果當前是展開狀態
                return self.toggle_node(node_id)
            
            return True  # 已經是收折狀態
            
        except Exception as e:
            self.logger.error(f"收折節點失敗: {node_id}, 錯誤: {e}")
            return False
    
    def expand_all(self, max_level: int = -1) -> int:
        """
        展開所有節點
        
        Args:
            max_level: 最大展開層級，-1 表示無限制
            
        Returns:
            成功展開的節點數量
        """
        try:
            self.logger.info(f"開始全展開操作, 最大層級: {max_level}")
            
            expanded_count = 0
            for node_id in self._node_states.keys():
                # 簡化的層級檢查 - 假設 category 為第 1 層
                if max_level > 0:
                    if node_id.startswith('cat_') and max_level < 1:
                        continue
                    if node_id.startswith('subcat_') and max_level < 2:
                        continue
                
                if self.expand_node(node_id):
                    expanded_count += 1
            
            self.logger.info(f"全展開完成: {expanded_count} 個節點")
            return expanded_count
            
        except Exception as e:
            self.logger.error(f"全展開操作失敗: {e}")
            return 0
    
    def collapse_all(self) -> int:
        """
        收折所有節點
        
        Returns:
            成功收折的節點數量
        """
        try:
            self.logger.info("開始全收折操作")
            
            collapsed_count = 0
            for node_id in self._node_states.keys():
                if self.collapse_node(node_id):
                    collapsed_count += 1
            
            self.logger.info(f"全收折完成: {collapsed_count} 個節點")
            return collapsed_count
            
        except Exception as e:
            self.logger.error(f"全收折操作失敗: {e}")
            return 0
    
    def get_node_state(self, node_id: str) -> Optional[bool]:
        """
        獲取節點展開狀態
        
        Args:
            node_id: 節點ID
            
        Returns:
            True=展開, False=收折, None=節點不存在
        """
        return self._node_states.get(node_id)
    
    def get_expanded_nodes(self) -> List[str]:
        """
        獲取所有展開的節點
        
        Returns:
            展開節點ID列表
        """
        return [node_id for node_id, expanded in self._node_states.items() if expanded]
    
    def get_tree_statistics(self) -> Dict[str, int]:
        """
        獲取樹狀結構統計資訊
        
        Returns:
            統計字典，包含總節點數、展開節點數等
        """
        total_nodes = len(self._node_states)
        expanded_nodes = len(self.get_expanded_nodes())
        category_nodes = len([k for k in self._node_states.keys() if k.startswith('cat_')])
        subcategory_nodes = len([k for k in self._node_states.keys() if k.startswith('subcat_')])
        
        return {
            'total_nodes': total_nodes,
            'expanded_nodes': expanded_nodes,
            'collapsed_nodes': total_nodes - expanded_nodes,
            'category_nodes': category_nodes,
            'subcategory_nodes': subcategory_nodes
        }