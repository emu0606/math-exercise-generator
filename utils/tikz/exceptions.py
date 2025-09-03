"""
TikZ 渲染異常定義

定義 TikZ 圖形渲染過程中可能遇到的各種異常情況，提供清晰的錯誤分類。

使用方式：
    from utils.tikz.exceptions import TikZError, RenderingError
    
    try:
        result = render_arc_params(vertex, p1, p2)
    except ArcRenderingError as e:
        logger.error(f"弧線渲染錯誤: {e}")
    except TikZError as e:
        logger.error(f"TikZ 渲染錯誤: {e}")
"""

from typing import Any, Optional, Dict
from ..geometry.exceptions import GeometryError


class TikZError(GeometryError):
    """TikZ 渲染基礎異常類
    
    所有 TikZ 相關異常的基類，繼承自 GeometryError。
    """
    pass


class RenderingError(TikZError):
    """渲染錯誤
    
    當 TikZ 圖形渲染過程中遇到問題時拋出。
    """
    
    def __init__(self, operation: str, reason: str, **context):
        """初始化渲染錯誤
        
        Args:
            operation: 正在執行的渲染操作
            reason: 渲染失敗的原因
            **context: 渲染上下文資訊
        """
        message = f"TikZ 渲染錯誤 ({operation}): {reason}"
        details = {
            'operation': operation,
            'reason': reason,
            **context
        }
        super().__init__(message, details)
        self.operation = operation
        self.reason = reason
        self.context = context


class ArcRenderingError(RenderingError):
    """弧線渲染錯誤
    
    當計算弧線渲染參數時遇到問題時拋出。
    """
    
    def __init__(self, arc_type: str, reason: str, **context):
        """初始化弧線渲染錯誤
        
        Args:
            arc_type: 弧線類型 (angle_arc, right_angle)
            reason: 錯誤原因
            **context: 相關上下文
        """
        super().__init__(f"arc_rendering_{arc_type}", f"弧線渲染失敗: {reason}", **context)
        self.arc_type = arc_type


class LabelPlacementError(RenderingError):
    """標籤放置錯誤
    
    當無法計算合適的標籤放置位置時拋出。
    """
    
    def __init__(self, label_type: str, reason: str, **context):
        """初始化標籤放置錯誤
        
        Args:
            label_type: 標籤類型 (vertex, side, angle_value)
            reason: 放置失敗原因
            **context: 相關上下文
        """
        super().__init__(f"label_placement_{label_type}", f"標籤放置失敗: {reason}", **context)
        self.label_type = label_type


class CoordinateTransformError(RenderingError):
    """座標轉換錯誤
    
    當 TikZ 座標轉換過程中遇到問題時拋出。
    """
    
    def __init__(self, transform_type: str, reason: str, **context):
        """初始化座標轉換錯誤
        
        Args:
            transform_type: 轉換類型
            reason: 轉換失敗原因
            **context: 相關上下文
        """
        super().__init__(f"coordinate_transform_{transform_type}", f"座標轉換失敗: {reason}", **context)
        self.transform_type = transform_type


class TikZConfigError(TikZError):
    """TikZ 配置錯誤
    
    當 TikZ 渲染配置參數不正確時拋出。
    """
    
    def __init__(self, config_key: str, value: Any, expected: str):
        """初始化配置錯誤
        
        Args:
            config_key: 配置項名稱
            value: 錯誤的配置值
            expected: 期望的配置值描述
        """
        message = f"TikZ 配置錯誤: {config_key} = {value}，期望: {expected}"
        details = {
            'config_key': config_key,
            'value': str(value),
            'expected': expected
        }
        super().__init__(message, details)
        self.config_key = config_key
        self.value = value
        self.expected = expected


class TikZSyntaxError(TikZError):
    """TikZ 語法錯誤
    
    當生成的 TikZ 代碼語法不正確時拋出。
    """
    
    def __init__(self, tikz_code: str, error_position: Optional[int] = None, reason: str = "語法錯誤"):
        """初始化語法錯誤
        
        Args:
            tikz_code: 出錯的 TikZ 代碼
            error_position: 錯誤位置（可選）
            reason: 錯誤原因
        """
        message = f"TikZ 語法錯誤: {reason}"
        details = {
            'tikz_code': tikz_code,
            'error_position': error_position,
            'reason': reason
        }
        super().__init__(message, details)
        self.tikz_code = tikz_code
        self.error_position = error_position
        self.reason = reason


# 便利函數：快速創建常見異常

def invalid_arc_config_error(config: Any, context: str = "") -> TikZConfigError:
    """創建無效弧線配置異常
    
    Args:
        config: 無效的弧線配置
        context: 額外的上下文描述
        
    Returns:
        TikZConfigError 實例
    """
    expected = "數值、'auto' 或配置字典 {'radius': float, 'type': str}"
    if context:
        expected += f" ({context})"
    return TikZConfigError("arc_config", config, expected)


def invalid_label_offset_error(offset: float, context: str = "") -> TikZConfigError:
    """創建無效標籤偏移異常
    
    Args:
        offset: 無效的偏移值
        context: 額外的上下文描述
        
    Returns:
        TikZConfigError 實例
    """
    expected = "正數偏移值 (通常在 0.1 到 1.0 之間)"
    if context:
        expected += f" ({context})"
    return TikZConfigError("label_offset", offset, expected)


def invalid_tikz_position_error(position: str, context: str = "") -> TikZConfigError:
    """創建無效 TikZ 位置異常
    
    Args:
        position: 無效的位置字串
        context: 額外的上下文描述
        
    Returns:
        TikZConfigError 實例
    """
    expected = "有效的 TikZ 位置關鍵字 (north, south, east, west, center 等)"
    if context:
        expected += f" ({context})"
    return TikZConfigError("tikz_position", position, expected)