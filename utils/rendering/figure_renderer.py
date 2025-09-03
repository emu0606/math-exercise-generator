#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 圖形渲染器
解耦的圖形渲染系統，支援快取和統一接口
"""

from typing import Dict, List, Any, Optional, Protocol, Union
import hashlib
import time
from ..core.logging import get_logger
# 避免循環導入，使用基本類型

logger = get_logger(__name__)


class FigureGeneratorProtocol(Protocol):
    """圖形生成器協議
    
    定義圖形生成器必須實現的接口，解耦與具體figures模組的依賴。
    """
    
    def generate_tikz(self, params: Dict[str, Any]) -> str:
        """生成TikZ代碼
        
        Args:
            params: 圖形參數
            
        Returns:
            TikZ代碼字符串
        """
        ...


class RenderingCache:
    """渲染快取系統
    
    提供圖形渲染結果的快取功能，避免重複計算。
    """
    
    def __init__(self, max_size: int = 100, ttl_seconds: int = 3600):
        """初始化快取
        
        Args:
            max_size: 最大快取條目數
            ttl_seconds: 快取存活時間（秒）
        """
        self.cache = {}
        self.access_times = {}
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        
        logger.debug(f"初始化渲染快取: 最大{max_size}項, TTL={ttl_seconds}秒")
    
    def get_cache_key(self, figure_type: str, params: Dict[str, Any], 
                     options: Dict[str, Any]) -> str:
        """生成快取鍵
        
        Args:
            figure_type: 圖形類型
            params: 圖形參數
            options: 渲染選項
            
        Returns:
            快取鍵字符串
        """
        # 創建唯一標識符
        content = f"{figure_type}|{sorted(params.items())}|{sorted(options.items())}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def get(self, cache_key: str) -> Optional[str]:
        """獲取快取項目
        
        Args:
            cache_key: 快取鍵
            
        Returns:
            快取的渲染結果，如果不存在或過期則返回None
        """
        if cache_key not in self.cache:
            return None
        
        # 檢查TTL
        current_time = time.time()
        if current_time - self.access_times[cache_key] > self.ttl_seconds:
            # 過期，移除
            del self.cache[cache_key]
            del self.access_times[cache_key]
            logger.debug(f"快取項目過期移除: {cache_key[:8]}...")
            return None
        
        # 更新訪問時間
        self.access_times[cache_key] = current_time
        logger.debug(f"快取命中: {cache_key[:8]}...")
        return self.cache[cache_key]
    
    def put(self, cache_key: str, result: str) -> None:
        """存儲快取項目
        
        Args:
            cache_key: 快取鍵
            result: 渲染結果
        """
        current_time = time.time()
        
        # 檢查快取大小限制
        if len(self.cache) >= self.max_size:
            # 移除最舊的項目
            oldest_key = min(self.access_times.keys(), 
                           key=lambda k: self.access_times[k])
            del self.cache[oldest_key]
            del self.access_times[oldest_key]
            logger.debug(f"快取滿，移除最舊項目: {oldest_key[:8]}...")
        
        self.cache[cache_key] = result
        self.access_times[cache_key] = current_time
        logger.debug(f"快取新項目: {cache_key[:8]}...")
    
    def clear(self) -> None:
        """清空快取"""
        self.cache.clear()
        self.access_times.clear()
        logger.info("渲染快取已清空")
    
    def get_stats(self) -> Dict[str, Any]:
        """獲取快取統計信息
        
        Returns:
            快取統計數據
        """
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'ttl_seconds': self.ttl_seconds,
            'oldest_access': min(self.access_times.values()) if self.access_times else None,
            'newest_access': max(self.access_times.values()) if self.access_times else None
        }


class FigureRenderer:
    """解耦的圖形渲染器
    
    提供統一的圖形渲染接口，支援快取和錯誤處理。
    不直接依賴figures模組，通過協議接口實現解耦。
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, 
                 enable_cache: bool = True, cache_size: int = 100):
        """初始化圖形渲染器
        
        Args:
            config: 文檔配置字典
            enable_cache: 是否啟用渲染快取
            cache_size: 快取大小
        """
        self.config = config or {}
        self.enable_cache = enable_cache
        self.cache = RenderingCache(max_size=cache_size) if enable_cache else None
        self._generators = {}  # 動態註冊的生成器
        
        logger.info(f"圖形渲染器初始化完成, 快取: {'啟用' if enable_cache else '禁用'}")
    
    def register_generator(self, figure_type: str, 
                          generator: Union[FigureGeneratorProtocol, type]) -> None:
        """註冊圖形生成器
        
        Args:
            figure_type: 圖形類型名稱
            generator: 生成器實例或類
        """
        self._generators[figure_type] = generator
        logger.debug(f"註冊圖形生成器: {figure_type}")
    
    def render(self, figure_data: Dict[str, Any]) -> str:
        """渲染圖形
        
        Args:
            figure_data: 圖形數據字典，包含 'type', 'params' 和 'options'
            
        Returns:
            TikZ圖形代碼或錯誤信息
        """
        try:
            # 驗證輸入
            if not self._validate_figure_data(figure_data):
                return self._error_message("圖形數據格式無效")
            
            figure_type = figure_data['type']
            params = figure_data.get('params', {})
            options = figure_data.get('options', {})
            
            # 檢查快取
            if self.enable_cache:
                cache_key = self.cache.get_cache_key(figure_type, params, options)
                cached_result = self.cache.get(cache_key)
                if cached_result:
                    return cached_result
            
            # 渲染圖形
            try:
                tikz_content = self._render_figure(figure_type, params)
                tikz_code = self._wrap_tikz_content(tikz_content, options)
                
                # 存儲到快取
                if self.enable_cache:
                    self.cache.put(cache_key, tikz_code)
                
                logger.debug(f"圖形渲染成功: {figure_type}")
                return tikz_code
                
            except Exception as e:
                error_msg = self._error_message(f"渲染圖形失敗 (類型: {figure_type}): {str(e)}")
                logger.error(f"圖形渲染錯誤: {figure_type} - {e}")
                return error_msg
                
        except Exception as e:
            error_msg = self._error_message(f"渲染器內部錯誤: {str(e)}")
            logger.error(f"渲染器異常: {e}")
            return error_msg
    
    def _validate_figure_data(self, figure_data: Dict[str, Any]) -> bool:
        """驗證圖形數據格式
        
        Args:
            figure_data: 圖形數據
            
        Returns:
            True如果數據有效
        """
        if not isinstance(figure_data, dict):
            return False
        
        if 'type' not in figure_data:
            return False
        
        if not isinstance(figure_data['type'], str):
            return False
        
        # params和options是可選的
        if 'params' in figure_data and not isinstance(figure_data['params'], dict):
            return False
        
        if 'options' in figure_data and not isinstance(figure_data['options'], dict):
            return False
        
        return True
    
    def _render_figure(self, figure_type: str, params: Dict[str, Any]) -> str:
        """渲染具體圖形
        
        Args:
            figure_type: 圖形類型
            params: 圖形參數
            
        Returns:
            TikZ內容（不包含tikzpicture環境）
            
        Raises:
            Exception: 當渲染失敗時
        """
        # 首先嘗試使用註冊的生成器
        if figure_type in self._generators:
            generator = self._generators[figure_type]
            if isinstance(generator, type):
                generator = generator()
            return generator.generate_tikz(params)
        
        # 回退到動態導入figures模組（向後相容）
        try:
            import figures
            generator_cls = figures.get_figure_generator(figure_type)
            generator = generator_cls()
            return generator.generate_tikz(params)
        except ImportError:
            raise Exception(f"無法導入figures模組，且未註冊生成器: {figure_type}")
        except Exception as e:
            raise Exception(f"生成器錯誤: {e}")
    
    def _wrap_tikz_content(self, tikz_content: str, 
                          options: Dict[str, Any]) -> str:
        """包裝TikZ內容為完整的tikzpicture環境
        
        Args:
            tikz_content: TikZ內容
            options: 渲染選項
            
        Returns:
            完整的TikZ代碼
        """
        # 處理scale選項
        scale = options.get('scale', 1.0)
        
        # 處理其他TikZ選項
        tikz_options = []
        if scale != 1.0:
            tikz_options.append(f"scale={scale}")
        
        # 添加用戶自定義選項
        custom_options = options.get('tikz_options', [])
        if isinstance(custom_options, list):
            tikz_options.extend(custom_options)
        elif isinstance(custom_options, str):
            tikz_options.append(custom_options)
        
        # 構建tikzpicture環境
        if tikz_options:
            options_str = ", ".join(tikz_options)
            return f"\\begin{{tikzpicture}}[{options_str}]\n{tikz_content}\n\\end{{tikzpicture}}"
        else:
            return f"\\begin{{tikzpicture}}\n{tikz_content}\n\\end{{tikzpicture}}"
    
    def _error_message(self, message: str) -> str:
        """生成錯誤信息的LaTeX代碼
        
        Args:
            message: 錯誤信息
            
        Returns:
            LaTeX錯誤顯示代碼
        """
        # 轉義LaTeX特殊字符
        escaped_message = message.replace('\\', '\\textbackslash{}')
        escaped_message = escaped_message.replace('{', '\\{').replace('}', '\\}')
        escaped_message = escaped_message.replace('_', '\\_').replace('^', '\\textasciicircum{}')
        
        return f"\\textbf{{渲染錯誤: {escaped_message}}}"
    
    def render_batch(self, figure_list: List[Dict[str, Any]]) -> List[str]:
        """批次渲染多個圖形
        
        Args:
            figure_list: 圖形數據列表
            
        Returns:
            渲染結果列表
        """
        results = []
        for i, figure_data in enumerate(figure_list):
            try:
                result = self.render(figure_data)
                results.append(result)
            except Exception as e:
                error_msg = self._error_message(f"批次渲染第{i+1}項失敗: {e}")
                results.append(error_msg)
                logger.error(f"批次渲染錯誤: 第{i+1}項 - {e}")
        
        logger.info(f"批次渲染完成: {len(results)}項")
        return results
    
    def get_cache_stats(self) -> Optional[Dict[str, Any]]:
        """獲取快取統計信息
        
        Returns:
            快取統計，如果未啟用快取則返回None
        """
        if not self.enable_cache or not self.cache:
            return None
        
        return self.cache.get_stats()
    
    def clear_cache(self) -> None:
        """清空渲染快取"""
        if self.enable_cache and self.cache:
            self.cache.clear()
            logger.info("圖形渲染快取已清空")
    
    def get_supported_types(self) -> List[str]:
        """獲取支援的圖形類型
        
        Returns:
            支援的圖形類型列表
        """
        registered_types = list(self._generators.keys())
        
        # 嘗試從figures模組獲取額外類型（向後相容）
        try:
            import figures
            if hasattr(figures, 'get_available_types'):
                figures_types = figures.get_available_types()
                registered_types.extend([t for t in figures_types if t not in registered_types])
        except ImportError:
            pass
        
        return registered_types


# 全域渲染器實例
_default_renderer = None


def get_default_renderer() -> FigureRenderer:
    """獲取預設的圖形渲染器
    
    Returns:
        預設渲染器實例
    """
    global _default_renderer
    if _default_renderer is None:
        _default_renderer = FigureRenderer()
        logger.debug("創建預設圖形渲染器")
    
    return _default_renderer


def render_figure(figure_data: Dict[str, Any], 
                 renderer: Optional[FigureRenderer] = None) -> str:
    """便利函數：渲染單個圖形
    
    Args:
        figure_data: 圖形數據
        renderer: 自定義渲染器，如果為None則使用預設渲染器
        
    Returns:
        渲染結果
    """
    if renderer is None:
        renderer = get_default_renderer()
    
    return renderer.render(figure_data)


def render_figures_batch(figure_list: List[Dict[str, Any]], 
                        renderer: Optional[FigureRenderer] = None) -> List[str]:
    """便利函數：批次渲染多個圖形
    
    Args:
        figure_list: 圖形數據列表
        renderer: 自定義渲染器，如果為None則使用預設渲染器
        
    Returns:
        渲染結果列表
    """
    if renderer is None:
        renderer = get_default_renderer()
    
    return renderer.render_batch(figure_list)


def create_figure_renderer(enable_cache: bool = True, 
                          cache_size: int = 100,
                          config: Optional[Dict[str, Any]] = None) -> FigureRenderer:
    """創建新的圖形渲染器
    
    Args:
        enable_cache: 是否啟用快取
        cache_size: 快取大小
        config: 文檔配置
        
    Returns:
        新的渲染器實例
    """
    return FigureRenderer(config=config, 
                         enable_cache=enable_cache, 
                         cache_size=cache_size)


# 向後相容支援
def legacy_render(figure_data: Dict[str, Any]) -> str:
    """向後相容的渲染函數
    
    提供與舊版本相同的接口，內部使用新的渲染器。
    
    Args:
        figure_data: 圖形數據
        
    Returns:
        渲染結果
    """
    logger.warning("使用向後相容的渲染函數，建議更新到新API")
    return render_figure(figure_data)