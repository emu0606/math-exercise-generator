"""
幾何計算模組

提供現代化的幾何計算功能，支援多種數學後端：
- 基礎幾何運算 (distance, angle, area 等)
- 現代化數據類型 (Point, Vector, Triangle 等)
- 多後端支援 (NumPy, SymPy, Python)
- 完整的異常處理

使用方式：
    # 基礎運算
    from utils.geometry import distance, get_midpoint, angle_between_points
    
    # 三角形功能
    from utils.geometry import Triangle, construct_triangle, get_centroid
    
    # 數學後端配置
    from utils.geometry import configure_math_backend, get_geometry_info
"""

# 導入異常類
from .exceptions import (
    GeometryError,
    ValidationError,
    ComputationError,
    TriangleError,
    TriangleDefinitionError,
    TriangleConstructionError,
    TriangleInequalityError,
    DegenerateTriangleError,
    CircleError,
    InvalidRadiusError,
    CircleConstructionError,
    NumericalInstabilityError,
    RenderingError,
    LabelPlacementError,
    ConfigurationError
)

# 導入數據類型
from .types import (
    Point,
    Vector,
    Triangle,
    Circle,
    Line,
    GeometryConfig,
    LabelConfig,
    ArcConfig,
    # 工具函數
    ensure_point,
    ensure_triangle
)

# 導入數學後端
from .math_backend import (
    AbstractMathBackend,
    PythonMathBackend,
    NumpyMathBackend,
    SymPyMathBackend,
    MathBackendFactory,
    list_available_backends,
    benchmark_backends
)

# 導入基礎運算
from .basic_ops import (
    distance,
    midpoint, 
    centroid,
    area_of_triangle,
    signed_area_of_triangle,
    angle_between_vectors,
    angle_at_vertex,
    normalize_angle,
    angle_difference,
    rotate_point,
    reflect_point,
    is_point_on_segment,
    is_clockwise,
    perpendicular_distance,
    distances_from_point,
    find_closest_point
)

# 導入三角形構造功能
from .triangle_construction import (
    construct_triangle,
    construct_triangle_sss,
    construct_triangle_sas,
    construct_triangle_asa,
    construct_triangle_aas,
    construct_triangle_coordinates,
    TriangleConstructor
)

# 導入三角形特殊點功能
from .triangle_centers import (
    get_centroid as get_triangle_centroid,
    get_incenter,
    get_circumcenter,
    get_orthocenter,
    get_all_centers,
    TriangleCenterCalculator,
    # 向後相容函數
    get_centroid_legacy,
    get_incenter_legacy,
    get_circumcenter_legacy,
    get_orthocenter_legacy
)

# 版本資訊
__version__ = "1.0.0"
__author__ = "Math Exercise Generator Team"

# 模組日誌
from ..core.logging import get_logger
logger = get_logger(__name__)

# 模組初始化日誌
logger.debug(f"幾何計算模組載入完成，版本: {__version__}")

# 全域配置
from ..core.config import global_config

# 便利函數

def configure_math_backend(backend_name: str = "auto", **kwargs) -> AbstractMathBackend:
    """配置數學計算後端
    
    Args:
        backend_name: 後端名稱 ("numpy", "sympy", "python", "auto")
        **kwargs: 後端特定配置
        
    Returns:
        配置好的數學後端實例
        
    Raises:
        MathBackendError: 當後端配置失敗時
    """
    try:
        from .math_backend import get_math_backend
        # 將字符串轉換為適當的後端類型
        if backend_name == "numpy":
            backend_type = "numpy"
        elif backend_name == "sympy": 
            backend_type = "sympy"
        elif backend_name == "python":
            backend_type = "python"
        else:
            backend_type = None  # auto
        
        backend = get_math_backend(backend_type)
        
        # 更新全域配置
        global_config.update('math_backend', backend_name)
        
        logger.info(f"數學後端配置完成: {backend_name}")
        return backend
        
    except Exception as e:
        logger.error(f"數學後端配置失敗: {e}")
        raise


def get_geometry_info() -> dict:
    """取得幾何模組資訊
    
    Returns:
        包含模組資訊和可用功能的字典
    """
    available_backends = list_available_backends()
    
    return {
        'module': 'utils.geometry',
        'version': __version__,
        'author': __author__,
        'available_backends': available_backends,
        'current_backend': global_config.get('math_backend', 'python'),
        'supported_types': [
            'Point', 'Vector', 'Triangle', 'Circle', 'Line'
        ],
        'basic_operations': [
            'distance', 'get_midpoint', 'get_centroid',
            'angle_between_points', 'area_of_triangle',
            'rotate_point', 'reflect_point'
        ]
    }


def validate_geometry_setup() -> bool:
    """驗證幾何模組設置
    
    Returns:
        True 如果設置正確，否則 False
    """
    try:
        # 測試基本功能
        p1 = Point(0, 0)
        p2 = Point(3, 4)
        dist = distance(p1, p2)
        
        if abs(dist - 5.0) > 1e-9:
            logger.warning(f"基礎距離計算異常: 期望 5.0，得到 {dist}")
            return False
        
        # 測試數學後端
        backend = configure_math_backend("auto")
        test_result = backend.sqrt(25.0)
        
        if abs(test_result - 5.0) > 1e-9:
            logger.warning(f"數學後端測試異常: 期望 5.0，得到 {test_result}")
            return False
        
        logger.info("幾何模組設置驗證通過")
        return True
        
    except Exception as e:
        logger.error(f"幾何模組設置驗證失敗: {e}")
        return False


# 向後相容函數 - 覆蓋從 triangle_construction 導入的版本


# 向後相容別名
def get_vertices(*args, **kwargs):
    """向後相容的 get_vertices 函數
    
    將調用轉發到新的 construct_triangle 函數
    """
    logger.warning("get_vertices 函數已棄用，請使用 construct_triangle")
    return construct_triangle("coordinates", *args, **kwargs)

def get_midpoint(*args, **kwargs):
    """向後相容的 get_midpoint 函數"""
    return midpoint(*args, **kwargs)

def get_centroid(*args, **kwargs):
    """向後相容的 get_centroid 函數"""
    # 如果第一個參數是 Triangle 對象，使用三角形質心函數
    if args and hasattr(args[0], 'p1') and hasattr(args[0], 'p2') and hasattr(args[0], 'p3'):
        return get_triangle_centroid(*args, **kwargs)
    # 否則使用點列表質心函數
    return centroid(*args, **kwargs)


# 公開 API
__all__ = [
    # 異常類
    'GeometryError',
    'ValidationError', 
    'ComputationError',
    'TriangleError',
    'TriangleDefinitionError',
    'TriangleConstructionError',
    'TriangleInequalityError',
    'DegenerateTriangleError',
    'CircleError',
    'InvalidRadiusError',
    'CircleConstructionError',
    'NumericalInstabilityError',
    'RenderingError',
    'LabelPlacementError',
    'ConfigurationError',
    
    # 數據類型
    'Point',
    'Vector',
    'Triangle',
    'Circle',
    'Line',
    'GeometryConfig',
    'LabelConfig',
    'ArcConfig',
    
    # 數學後端
    'AbstractMathBackend',
    'PythonMathBackend',
    'NumpyMathBackend', 
    'SymPyMathBackend',
    'MathBackendFactory',
    'list_available_backends',
    'benchmark_backends',
    
    # 基礎運算
    'distance',
    'midpoint',
    'centroid',
    'area_of_triangle',
    'signed_area_of_triangle',
    'angle_between_vectors',
    'angle_at_vertex',
    'normalize_angle',
    'angle_difference',
    'rotate_point',
    'reflect_point',
    'is_point_on_segment',
    'is_clockwise',
    'perpendicular_distance',
    'distances_from_point',
    'find_closest_point',
    
    # 三角形構造
    'construct_triangle',
    'construct_triangle_sss',
    'construct_triangle_sas', 
    'construct_triangle_asa',
    'construct_triangle_aas',
    'construct_triangle_coordinates',
    'TriangleConstructor',
    
    # 三角形特殊點
    'get_triangle_centroid',
    'get_incenter',
    'get_circumcenter',
    'get_orthocenter',
    'get_all_centers',
    'TriangleCenterCalculator',
    
    # 工具函數
    'ensure_point',
    'ensure_triangle',
    
    # 便利函數
    'configure_math_backend',
    'get_geometry_info',
    'validate_geometry_setup',
    
    # 向後相容
    'get_vertices',
    'get_midpoint',
    'get_centroid',
    'get_centroid_legacy',
    'get_incenter_legacy',
    'get_circumcenter_legacy',
    'get_orthocenter_legacy'
]