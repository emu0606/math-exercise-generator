"""
TikZ 模組

從原始 geometry_utils.py 重構而來的 TikZ 渲染功能，提供角弧、標籤定位和座標轉換。

主要功能：
- 角弧渲染參數計算
- 標籤定位和佈局
- 座標系統轉換
- TikZ 代碼生成

使用方式：
    from utils.tikz import ArcRenderer, LabelPositioner
    
    # 角弧渲染
    renderer = ArcRenderer()
    arc_params = renderer.render_angle_arc(vertex, p1, p2, radius_config="auto")
    print(arc_params.tikz_code)
    
    # 標籤定位
    positioner = LabelPositioner()
    label_params = positioner.position_vertex_label(point, "A")
    print(label_params.tikz_code)
"""

from .exceptions import (
    TikZError,
    RenderingError,
    ArcRenderingError,
    LabelPlacementError,
    CoordinateTransformError,
    TikZConfigError,
    TikZSyntaxError,
    # 便利函數
    invalid_arc_config_error,
    invalid_label_offset_error,
    invalid_tikz_position_error
)

from .types import (
    # 基礎類型
    TikZCoordinate,
    TikZDistance,
    TikZAngle,
    ArcType,
    LabelType,
    CoordinateSystem,
    
    # 枚舉類
    TikZPosition,
    TikZAnchor,
    
    # 配置類
    ArcConfig,
    LabelConfig,
    CoordinateTransform,
    RenderingContext,
    
    # 參數類
    ArcParameters,
    LabelParameters,
    
    # 工具函數
    normalize_tikz_position,
    normalize_tikz_anchor,
    format_tikz_coordinate,
    format_tikz_angle
)

from .arc_renderer import ArcRenderer
from .label_positioner import (
    LabelPositioner,
    position_vertex_label_auto,
    position_side_label_auto,
    position_angle_label_auto
)

from .coordinate_transform import (
    CoordinateTransformer,
    AdvancedCoordinateTransformer,
    # 向後相容函數
    get_arc_render_params,
    # 獨立工具函數
    tikz_coordinate,
    tikz_angle_degrees,
    tikz_distance,
    tikz_options_format,
    # 批次處理
    batch_coordinate_transform,
    batch_angle_transform,
    # 工具函數
    ensure_tikz_coordinate,
    ensure_tikz_angle
)

# 版本資訊
__version__ = "1.0.0"
__author__ = "Math Exercise Generator Team"

# 模組日誌
from ..core.logging import get_logger
logger = get_logger(__name__)

# 模組初始化
logger.debug(f"TikZ 模組載入完成，版本: {__version__}")

# 預設配置
DEFAULT_RENDERING_CONTEXT = RenderingContext(
    precision=3,
    unit="cm",
    debug_mode=False
)

# 便利函數

def create_arc_renderer(context: RenderingContext = None) -> ArcRenderer:
    """創建弧線渲染器
    
    Args:
        context: 渲染上下文，如果未提供則使用預設值
        
    Returns:
        ArcRenderer 實例
    """
    if context is None:
        context = DEFAULT_RENDERING_CONTEXT
    
    logger.debug("創建弧線渲染器")
    return ArcRenderer(context)

def create_label_positioner(context: RenderingContext = None) -> LabelPositioner:
    """創建標籤定位器
    
    Args:
        context: 渲染上下文，如果未提供則使用預設值
        
    Returns:
        LabelPositioner 實例
    """
    if context is None:
        context = DEFAULT_RENDERING_CONTEXT
    
    logger.debug("創建標籤定位器")
    return LabelPositioner(context)

def create_coordinate_transformer(precision: int = 3, unit: str = "cm") -> CoordinateTransformer:
    """創建座標轉換器
    
    Args:
        precision: 數值精度
        unit: 距離單位
        
    Returns:
        CoordinateTransformer 實例
    """
    logger.debug(f"創建座標轉換器: 精度={precision}, 單位={unit}")
    return CoordinateTransformer(precision, unit)

def get_tikz_info() -> dict:
    """取得 TikZ 模組資訊
    
    Returns:
        包含模組資訊的字典
    """
    return {
        'module': 'utils.tikz',
        'version': __version__,
        'author': __author__,
        'components': [
            'ArcRenderer',
            'LabelPositioner',
            'CoordinateTransformer'
        ],
        'supported_arc_types': [
            'angle_arc',
            'right_angle', 
            'custom'
        ],
        'supported_label_types': [
            'vertex',
            'side',
            'angle_value'
        ]
    }

# 公開 API
__all__ = [
    # 異常類
    'TikZError',
    'RenderingError', 
    'ArcRenderingError',
    'LabelPlacementError',
    'CoordinateTransformError',
    'TikZConfigError',
    'TikZSyntaxError',
    
    # 類型和配置
    'TikZCoordinate',
    'TikZDistance',
    'TikZAngle',
    'ArcType',
    'LabelType',
    'CoordinateSystem',
    'TikZPosition',
    'TikZAnchor',
    'ArcConfig',
    'LabelConfig',
    'CoordinateTransform', 
    'RenderingContext',
    'ArcParameters',
    'LabelParameters',
    
    # 渲染器
    'ArcRenderer',
    'LabelPositioner',
    'CoordinateTransformer',
    'AdvancedCoordinateTransformer',
    
    # 工具函數
    'normalize_tikz_position',
    'normalize_tikz_anchor',
    'format_tikz_coordinate',
    'format_tikz_angle',
    'create_arc_renderer',
    'create_label_positioner',
    'create_coordinate_transformer',
    'position_vertex_label_auto',
    'position_side_label_auto',
    'position_angle_label_auto',
    'get_tikz_info',
    
    # 座標轉換
    'get_arc_render_params',  # 向後相容
    'tikz_coordinate',
    'tikz_angle_degrees',
    'tikz_distance',
    'tikz_options_format',
    'batch_coordinate_transform',
    'batch_angle_transform',
    'ensure_tikz_coordinate',
    'ensure_tikz_angle',
    
    # 常數
    'DEFAULT_RENDERING_CONTEXT',
    
    # 便利函數
    'invalid_arc_config_error',
    'invalid_label_offset_error', 
    'invalid_tikz_position_error'
]