"""
生成器註冊系統

提供統一的題目生成器註冊和管理機制：
1. 線程安全的單例模式
2. 統一的日誌記錄
3. 完整的錯誤處理
4. 類別和子類別管理
5. 生成器查詢和驗證

使用方式：
    from utils.core.registry import registry
    
    # 註冊生成器
    registry.register(MyGenerator, "geometry", "triangle")
    
    # 獲取生成器
    generator_class = registry.get_generator("geometry", "triangle")
    
    # 查詢類別
    categories = registry.get_categories()
"""

import threading
from typing import Dict, Type, Optional, Any, List, Tuple, Set
from .logging import get_logger

# 生成器基類的前向聲明
# 使用 Any 類型避免循環導入問題
QuestionGeneratorType = Any

# 模組專用日誌器
logger = get_logger(__name__)


class RegistryError(Exception):
    """註冊系統專用異常類
    
    用於註冊系統相關的錯誤情況。
    """
    pass


class GeneratorRegistry:
    """生成器註冊系統
    
    採用線程安全的單例模式，管理所有題目生成器的註冊、查詢和驗證。
    
    功能特色：
    - 線程安全的單例實現
    - 完整的錯誤處理和驗證
    - 統一的日誌記錄
    - 支援動態查詢和統計
    - 重複註冊檢測
    """
    
    _instance: Optional['GeneratorRegistry'] = None
    _lock = threading.Lock()  # 線程安全鎖
    _initialized = False
    
    def __new__(cls) -> 'GeneratorRegistry':
        """線程安全的單例模式實現
        
        使用雙重檢查鎖定模式確保線程安全。
        
        Returns:
            GeneratorRegistry 實例
        """
        if cls._instance is None:
            with cls._lock:
                # 雙重檢查，確保線程安全
                if cls._instance is None:
                    cls._instance = super(GeneratorRegistry, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化註冊系統
        
        只在第一次創建實例時執行初始化。
        """
        if self._initialized:
            return
            
        # 生成器儲存：{(category, subcategory): generator_class}
        self._generators: Dict[Tuple[str, str], Type[QuestionGeneratorType]] = {}
        
        # 類別映射：{category: [subcategory1, subcategory2, ...]}
        self._category_map: Dict[str, List[str]] = {}
        
        # 註冊統計
        self._registration_count = 0
        
        # 註冊歷史（用於調試和監控）
        self._registration_history: List[Dict[str, Any]] = []
        
        self._initialized = True
        logger.info("生成器註冊系統初始化完成")
    
    def register(self, 
                generator_class: Type[QuestionGeneratorType], 
                category: str, 
                subcategory: str,
                allow_override: bool = False) -> None:
        """註冊一個生成器
        
        Args:
            generator_class: 生成器類
            category: 題目類別（如：geometry, algebra）
            subcategory: 題目子類別（如：triangle, quadratic）
            allow_override: 是否允許覆蓋已存在的註冊
            
        Raises:
            RegistryError: 當註冊參數無效或重複註冊時
        """
        # 輸入驗證
        self._validate_registration_params(generator_class, category, subcategory)
        
        key = (category, subcategory)
        
        # 檢查重複註冊
        if not allow_override and key in self._generators:
            existing_generator = self._generators[key]
            error_msg = (f"生成器重複註冊: 類別 '{category}', 子類別 '{subcategory}' "
                        f"已註冊 {existing_generator.__name__}，"
                        f"嘗試註冊 {generator_class.__name__}")
            logger.error(error_msg)
            raise RegistryError(error_msg)
        
        # 執行註冊
        with self._lock:
            self._generators[key] = generator_class
            self._update_category_map(category, subcategory)
            self._registration_count += 1
            
            # 記錄註冊歷史
            registration_info = {
                'generator_name': generator_class.__name__,
                'category': category,
                'subcategory': subcategory,
                'override': allow_override and key in self._generators,
                'registration_id': self._registration_count
            }
            self._registration_history.append(registration_info)
        
        # 記錄成功註冊
        logger.info(f"註冊生成器成功: {generator_class.__name__} "
                   f"[{category}/{subcategory}] (ID: {self._registration_count})")
        
        if allow_override and key in self._generators:
            logger.warning(f"覆蓋舊註冊: {category}/{subcategory}")
    
    def _validate_registration_params(self, 
                                    generator_class: Type[QuestionGeneratorType],
                                    category: str,
                                    subcategory: str) -> None:
        """驗證註冊參數
        
        Args:
            generator_class: 生成器類
            category: 類別
            subcategory: 子類別
            
        Raises:
            RegistryError: 參數無效時拋出
        """
        if not generator_class:
            raise RegistryError("生成器類不能為 None")
        
        if not hasattr(generator_class, '__name__'):
            raise RegistryError("無效的生成器類：缺少 __name__ 屬性")
        
        if not isinstance(category, str) or not category.strip():
            raise RegistryError("類別必須是非空字串")
        
        if not isinstance(subcategory, str) or not subcategory.strip():
            raise RegistryError("子類別必須是非空字串")
        
        # 檢查類別和子類別格式
        if not category.replace('_', '').replace('-', '').isalnum():
            raise RegistryError(f"類別格式無效: '{category}' (只允許字母、數字、底線和連字符)")
        
        if not subcategory.replace('_', '').replace('-', '').isalnum():
            raise RegistryError(f"子類別格式無效: '{subcategory}' (只允許字母、數字、底線和連字符)")
    
    def _update_category_map(self, category: str, subcategory: str) -> None:
        """更新類別映射
        
        Args:
            category: 類別
            subcategory: 子類別
        """
        if category not in self._category_map:
            self._category_map[category] = []
            logger.debug(f"新增類別: {category}")
        
        if subcategory not in self._category_map[category]:
            self._category_map[category].append(subcategory)
            logger.debug(f"新增子類別: {category}/{subcategory}")
    
    def get_generator(self, category: str, subcategory: str) -> Optional[Type[QuestionGeneratorType]]:
        """獲取生成器類
        
        Args:
            category: 題目類別
            subcategory: 題目子類別
            
        Returns:
            生成器類，如果找不到則返回 None
        """
        if not isinstance(category, str) or not isinstance(subcategory, str):
            logger.error(f"無效的查詢參數: category={category}, subcategory={subcategory}")
            return None
        
        key = (category, subcategory)
        generator = self._generators.get(key)
        
        if generator:
            logger.debug(f"找到生成器: {generator.__name__} [{category}/{subcategory}]")
        else:
            logger.warning(f"未找到生成器: {category}/{subcategory}")
            logger.debug(f"已註冊的生成器數量: {len(self._generators)}")
        
        return generator
    
    def has_generator(self, category: str, subcategory: str) -> bool:
        """檢查是否存在指定的生成器
        
        Args:
            category: 題目類別
            subcategory: 題目子類別
            
        Returns:
            True 如果生成器存在，否則 False
        """
        key = (category, subcategory)
        return key in self._generators
    
    def get_categories(self) -> Dict[str, List[str]]:
        """獲取所有類別和子類別
        
        Returns:
            類別映射，格式為 {類別: [子類別1, 子類別2, ...]}
        """
        # 返回副本，避免外部修改
        return {k: v.copy() for k, v in self._category_map.items()}
    
    def get_subcategories(self, category: str) -> List[str]:
        """獲取指定類別的所有子類別
        
        Args:
            category: 題目類別
            
        Returns:
            子類別列表
        """
        return self._category_map.get(category, []).copy()
    
    def get_all_generators(self) -> Dict[Tuple[str, str], Type[QuestionGeneratorType]]:
        """獲取所有已註冊的生成器
        
        Returns:
            生成器字典，格式為 {(category, subcategory): generator_class}
        """
        return self._generators.copy()
    
    def get_generator_names(self) -> List[str]:
        """獲取所有生成器的名稱列表
        
        Returns:
            生成器名稱列表
        """
        return [gen_class.__name__ for gen_class in self._generators.values()]
    
    def unregister(self, category: str, subcategory: str) -> bool:
        """取消註冊指定的生成器
        
        Args:
            category: 題目類別
            subcategory: 題目子類別
            
        Returns:
            True 如果成功取消註冊，False 如果生成器不存在
        """
        key = (category, subcategory)
        
        with self._lock:
            if key not in self._generators:
                logger.warning(f"嘗試取消註冊不存在的生成器: {category}/{subcategory}")
                return False
            
            generator_class = self._generators.pop(key)
            
            # 更新類別映射
            if category in self._category_map:
                try:
                    self._category_map[category].remove(subcategory)
                    if not self._category_map[category]:  # 如果該類別沒有子類別了
                        del self._category_map[category]
                        logger.debug(f"移除空類別: {category}")
                except ValueError:
                    pass  # 子類別不在列表中
        
        logger.info(f"取消註冊生成器: {generator_class.__name__} [{category}/{subcategory}]")
        return True
    
    def clear(self) -> None:
        """清空所有註冊的生成器
        
        主要用於測試或重新初始化。
        """
        with self._lock:
            count = len(self._generators)
            self._generators.clear()
            self._category_map.clear()
            self._registration_count = 0
            self._registration_history.clear()
        
        logger.info(f"清空所有註冊 ({count} 個生成器)")
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """獲取註冊系統統計資訊
        
        Returns:
            包含統計資訊的字典
        """
        return {
            'total_generators': len(self._generators),
            'total_categories': len(self._category_map),
            'registration_count': self._registration_count,
            'categories': self.get_categories(),
            'generator_names': self.get_generator_names(),
            'recent_registrations': self._registration_history[-10:]  # 最近10次註冊
        }
    
    def __len__(self) -> int:
        """返回已註冊生成器的數量"""
        return len(self._generators)
    
    def __contains__(self, key: Tuple[str, str]) -> bool:
        """支援 in 操作符檢查生成器是否存在"""
        return key in self._generators
    
    def __repr__(self) -> str:
        """註冊系統的字串表示"""
        return f"GeneratorRegistry(generators={len(self._generators)}, categories={len(self._category_map)})"


# 全域註冊系統實例
# 整個專案中使用此實例來註冊和獲取生成器
registry = GeneratorRegistry()