"""
數學後端集成系統

提供統一的數學計算介面，支援多種數學後端（NumPy、SymPy、純Python），
讓幾何計算可以根據需求選擇最適合的計算方式。

使用方式：
    from utils.geometry.math_backend import MathBackend, get_math_backend
    
    # 獲取數學後端實例
    backend = get_math_backend('numpy')  # 或 'sympy', 'python'
    
    # 使用統一介面進行計算
    distance = backend.distance(p1, p2)
    angle = backend.angle_between_vectors(v1, v2)
"""

import math
from abc import ABC, abstractmethod
from typing import Tuple, Optional, Union, List, Any, Dict
from .types import Point, Vector, MathBackend as BackendType
from .exceptions import ComputationError, NumericalInstabilityError
from ..core.logging import get_logger
from ..core.config import global_config

# 模組專用日誌器
logger = get_logger(__name__)

# 可選依賴導入
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    np = None
    HAS_NUMPY = False
    logger.info("NumPy 未安裝，數值計算將使用純 Python 實現")

try:
    import sympy as sp
    from sympy.geometry import Point as SymPyPoint, Line as SymPyLine
    HAS_SYMPY = True
except ImportError:
    sp = None
    SymPyPoint = None
    SymPyLine = None
    HAS_SYMPY = False
    logger.info("SymPy 未安裝，符號計算不可用")


class AbstractMathBackend(ABC):
    """數學後端抽象基類
    
    定義所有數學後端必須實現的統一介面。
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """後端名稱"""
        pass
    
    @property
    @abstractmethod
    def precision(self) -> float:
        """數值精度"""
        pass
    
    @abstractmethod
    def distance(self, p1: Point, p2: Point) -> float:
        """計算兩點距離
        
        Args:
            p1: 第一個點
            p2: 第二個點
            
        Returns:
            兩點間的歐幾里得距離
        """
        pass
    
    @abstractmethod
    def angle_between_vectors(self, v1: Vector, v2: Vector) -> float:
        """計算兩向量夾角
        
        Args:
            v1: 第一個向量
            v2: 第二個向量
            
        Returns:
            兩向量夾角（弧度制）
        """
        pass
    
    @abstractmethod
    def cross_product(self, v1: Vector, v2: Vector) -> float:
        """計算向量叉積（2D情況下返回標量）
        
        Args:
            v1: 第一個向量
            v2: 第二個向量
            
        Returns:
            叉積結果
        """
        pass
    
    @abstractmethod
    def solve_quadratic(self, a: float, b: float, c: float) -> List[float]:
        """求解二次方程 ax² + bx + c = 0
        
        Args:
            a: 二次項係數
            b: 一次項係數
            c: 常數項
            
        Returns:
            實數解列表
        """
        pass
    
    @abstractmethod
    def is_zero(self, value: float) -> bool:
        """判斷數值是否接近零
        
        Args:
            value: 待判斷的數值
            
        Returns:
            是否接近零
        """
        pass


class PythonMathBackend(AbstractMathBackend):
    """純Python數學後端
    
    使用標準Python數學庫進行計算，適合對精度要求不高的場合。
    優點：無外部依賴，輕量級
    缺點：性能較差，精度有限
    """
    
    def __init__(self, precision: float = 1e-9):
        """初始化Python後端
        
        Args:
            precision: 數值精度容忍度
        """
        self._precision = precision
        logger.debug(f"初始化 Python 數學後端，精度: {precision}")
    
    @property
    def name(self) -> str:
        return "python"
    
    @property
    def precision(self) -> float:
        return self._precision
    
    def distance(self, p1: Point, p2: Point) -> float:
        """使用純Python計算兩點距離"""
        dx = p2.x - p1.x
        dy = p2.y - p1.y
        return math.sqrt(dx*dx + dy*dy)
    
    def angle_between_vectors(self, v1: Vector, v2: Vector) -> float:
        """使用純Python計算兩向量夾角"""
        # 計算向量長度
        len1 = math.sqrt(v1.x*v1.x + v1.y*v1.y)
        len2 = math.sqrt(v2.x*v2.x + v2.y*v2.y)
        
        # 檢查零向量
        if len1 < self._precision or len2 < self._precision:
            raise ComputationError(
                "angle_calculation", 
                "無法計算零向量的夾角",
                v1=v1, v2=v2, len1=len1, len2=len2
            )
        
        # 計算點積
        dot_product = v1.x*v2.x + v1.y*v2.y
        
        # 計算餘弦值並限制範圍
        cos_angle = dot_product / (len1 * len2)
        cos_angle = max(-1.0, min(1.0, cos_angle))  # 防止數值誤差
        
        return math.acos(cos_angle)
    
    def cross_product(self, v1: Vector, v2: Vector) -> float:
        """使用純Python計算向量叉積"""
        return v1.x * v2.y - v1.y * v2.x
    
    def solve_quadratic(self, a: float, b: float, c: float) -> List[float]:
        """使用純Python求解二次方程"""
        if abs(a) < self._precision:
            # 退化為一次方程
            if abs(b) < self._precision:
                # 常數方程
                return [] if abs(c) > self._precision else [0.0]
            return [-c / b]
        
        # 計算判別式
        discriminant = b*b - 4*a*c
        
        if discriminant < -self._precision:
            # 無實數解
            return []
        elif discriminant < self._precision:
            # 一個重根
            return [-b / (2*a)]
        else:
            # 兩個不同實根
            sqrt_d = math.sqrt(discriminant)
            return [(-b + sqrt_d) / (2*a), (-b - sqrt_d) / (2*a)]
    
    def is_zero(self, value: float) -> bool:
        """判斷數值是否接近零"""
        return abs(value) < self._precision


class NumpyMathBackend(AbstractMathBackend):
    """NumPy數學後端
    
    使用NumPy進行高效數值計算，適合大量數據處理。
    優點：高性能，向量化計算
    缺點：需要外部依賴
    """
    
    def __init__(self, precision: float = 1e-12):
        """初始化NumPy後端
        
        Args:
            precision: 數值精度容忍度
            
        Raises:
            ComputationError: 如果NumPy不可用
        """
        if not HAS_NUMPY:
            raise ComputationError(
                "backend_initialization", 
                "NumPy 後端不可用，請安裝 numpy 套件"
            )
        
        self._precision = precision
        logger.debug(f"初始化 NumPy 數學後端，精度: {precision}")
    
    @property
    def name(self) -> str:
        return "numpy"
    
    @property
    def precision(self) -> float:
        return self._precision
    
    def distance(self, p1: Point, p2: Point) -> float:
        """使用NumPy計算兩點距離"""
        p1_arr = np.array([p1.x, p1.y])
        p2_arr = np.array([p2.x, p2.y])
        return float(np.linalg.norm(p2_arr - p1_arr))
    
    def angle_between_vectors(self, v1: Vector, v2: Vector) -> float:
        """使用NumPy計算兩向量夾角"""
        v1_arr = np.array([v1.x, v1.y])
        v2_arr = np.array([v2.x, v2.y])
        
        # 計算向量長度
        len1 = np.linalg.norm(v1_arr)
        len2 = np.linalg.norm(v2_arr)
        
        # 檢查零向量
        if len1 < self._precision or len2 < self._precision:
            raise ComputationError(
                "angle_calculation",
                "無法計算零向量的夾角",
                v1=v1, v2=v2, len1=float(len1), len2=float(len2)
            )
        
        # 計算餘弦值
        cos_angle = np.dot(v1_arr, v2_arr) / (len1 * len2)
        
        # 使用NumPy的clip確保範圍正確
        cos_angle = np.clip(cos_angle, -1.0, 1.0)
        
        return float(np.arccos(cos_angle))
    
    def cross_product(self, v1: Vector, v2: Vector) -> float:
        """使用NumPy計算向量叉積"""
        # 2D向量叉積
        return float(v1.x * v2.y - v1.y * v2.x)
    
    def solve_quadratic(self, a: float, b: float, c: float) -> List[float]:
        """使用NumPy求解二次方程"""
        if abs(a) < self._precision:
            # 使用純Python方法處理退化情況
            return PythonMathBackend(self._precision).solve_quadratic(a, b, c)
        
        # 使用NumPy求解
        coeffs = np.array([a, b, c])
        roots = np.roots(coeffs)
        
        # 過濾實數解
        real_roots = []
        for root in roots:
            if np.isreal(root) and not np.isnan(root):
                real_roots.append(float(root.real))
        
        return real_roots
    
    def is_zero(self, value: float) -> bool:
        """判斷數值是否接近零"""
        return np.abs(value) < self._precision


class SymPyMathBackend(AbstractMathBackend):
    """SymPy數學後端
    
    使用SymPy進行精確符號計算，適合需要高精度的場合。
    優點：精確計算，符號表示
    缺點：性能較慢，需要外部依賴
    """
    
    def __init__(self, precision: float = 1e-15):
        """初始化SymPy後端
        
        Args:
            precision: 數值精度容忍度
            
        Raises:
            ComputationError: 如果SymPy不可用
        """
        if not HAS_SYMPY:
            raise ComputationError(
                "backend_initialization",
                "SymPy 後端不可用，請安裝 sympy 套件"
            )
        
        self._precision = precision
        logger.debug(f"初始化 SymPy 數學後端，精度: {precision}")
    
    @property
    def name(self) -> str:
        return "sympy"
    
    @property
    def precision(self) -> float:
        return self._precision
    
    def distance(self, p1: Point, p2: Point) -> float:
        """使用SymPy計算兩點距離"""
        sp_p1 = SymPyPoint(p1.x, p1.y)
        sp_p2 = SymPyPoint(p2.x, p2.y)
        distance = sp_p1.distance(sp_p2)
        return float(distance.evalf())
    
    def angle_between_vectors(self, v1: Vector, v2: Vector) -> float:
        """使用SymPy計算兩向量夾角"""
        # 創建SymPy向量（以點的形式）
        v1_sp = sp.Matrix([v1.x, v1.y])
        v2_sp = sp.Matrix([v2.x, v2.y])
        
        # 計算向量長度
        len1 = sp.sqrt(v1_sp.dot(v1_sp))
        len2 = sp.sqrt(v2_sp.dot(v2_sp))
        
        # 檢查零向量
        if len1 < self._precision or len2 < self._precision:
            raise ComputationError(
                "angle_calculation",
                "無法計算零向量的夾角",
                v1=v1, v2=v2, len1=float(len1), len2=float(len2)
            )
        
        # 計算餘弦值
        cos_angle = v1_sp.dot(v2_sp) / (len1 * len2)
        
        # 計算反餘弦
        angle = sp.acos(cos_angle)
        return float(angle.evalf())
    
    def cross_product(self, v1: Vector, v2: Vector) -> float:
        """使用SymPy計算向量叉積"""
        result = sp.simplify(v1.x * v2.y - v1.y * v2.x)
        return float(result.evalf())
    
    def solve_quadratic(self, a: float, b: float, c: float) -> List[float]:
        """使用SymPy求解二次方程"""
        x = sp.Symbol('x')
        equation = a*x**2 + b*x + c
        
        try:
            solutions = sp.solve(equation, x)
            real_solutions = []
            
            for sol in solutions:
                if sol.is_real:
                    real_solutions.append(float(sol.evalf()))
            
            return real_solutions
        except Exception as e:
            raise ComputationError(
                "quadratic_solve",
                f"SymPy求解失敗: {str(e)}",
                a=a, b=b, c=c
            )
    
    def is_zero(self, value: float) -> bool:
        """判斷數值是否接近零"""
        return abs(value) < self._precision


# 後端工廠和管理

class MathBackendFactory:
    """數學後端工廠類
    
    負責創建和管理不同的數學後端實例。
    """
    
    _backends = {}  # 後端實例快取
    
    @classmethod
    def create_backend(cls, backend_type: BackendType, precision: Optional[float] = None) -> AbstractMathBackend:
        """創建數學後端實例
        
        Args:
            backend_type: 後端類型
            precision: 數值精度，如果未指定則使用預設值
            
        Returns:
            數學後端實例
            
        Raises:
            ComputationError: 如果後端類型無效或依賴不滿足
        """
        # 獲取預設精度
        if precision is None:
            config = global_config
            precision = getattr(config, 'math_precision', 1e-9)
        
        # 創建快取鍵
        cache_key = f"{backend_type}_{precision}"
        
        # 檢查快取
        if cache_key in cls._backends:
            return cls._backends[cache_key]
        
        # 創建新實例
        try:
            if backend_type == 'python':
                backend = PythonMathBackend(precision)
            elif backend_type == 'numpy':
                backend = NumpyMathBackend(precision)
            elif backend_type == 'sympy':
                backend = SymPyMathBackend(precision)
            else:
                raise ComputationError(
                    "backend_creation",
                    f"未知的數學後端類型: {backend_type}",
                    available_types=['python', 'numpy', 'sympy']
                )
            
            # 快取實例
            cls._backends[cache_key] = backend
            logger.info(f"創建數學後端: {backend.name} (精度: {precision})")
            
            return backend
            
        except Exception as e:
            if isinstance(e, ComputationError):
                raise
            else:
                raise ComputationError(
                    "backend_creation",
                    f"創建後端失敗: {str(e)}",
                    backend_type=backend_type,
                    precision=precision
                ) from e
    
    @classmethod
    def get_available_backends(cls) -> List[str]:
        """獲取可用的後端列表
        
        Returns:
            可用後端名稱列表
        """
        available = ['python']  # Python總是可用
        
        if HAS_NUMPY:
            available.append('numpy')
        if HAS_SYMPY:
            available.append('sympy')
        
        return available
    
    @classmethod
    def clear_cache(cls) -> None:
        """清除後端快取"""
        cls._backends.clear()
        logger.debug("已清除數學後端快取")


# 便利函數

def get_math_backend(backend_type: Optional[BackendType] = None, 
                    precision: Optional[float] = None) -> AbstractMathBackend:
    """獲取數學後端實例
    
    Args:
        backend_type: 後端類型，如果未指定則使用全域配置
        precision: 數值精度，如果未指定則使用預設值
        
    Returns:
        數學後端實例
    """
    if backend_type is None:
        config = global_config
        backend_type = getattr(config, 'math_backend_default', 'python')
    
    return MathBackendFactory.create_backend(backend_type, precision)


def get_default_backend() -> AbstractMathBackend:
    """獲取預設數學後端
    
    Returns:
        預設的數學後端實例
    """
    return get_math_backend()


def list_available_backends() -> List[str]:
    """列出所有可用的數學後端
    
    Returns:
        可用後端名稱列表
    """
    return MathBackendFactory.get_available_backends()


def benchmark_backends() -> Dict[str, Dict[str, float]]:
    """基準測試所有可用後端的性能
    
    Returns:
        包含性能測試結果的字典
    """
    import time
    
    # 測試數據
    p1 = Point(0.0, 0.0)
    p2 = Point(3.0, 4.0)
    v1 = Vector(1.0, 0.0)
    v2 = Vector(0.0, 1.0)
    
    results = {}
    
    for backend_name in list_available_backends():
        try:
            backend = get_math_backend(backend_name)
            result = {'backend': backend_name}
            
            # 距離計算測試
            start_time = time.time()
            for _ in range(10000):
                backend.distance(p1, p2)
            result['distance_time'] = time.time() - start_time
            
            # 角度計算測試
            start_time = time.time()
            for _ in range(10000):
                backend.angle_between_vectors(v1, v2)
            result['angle_time'] = time.time() - start_time
            
            results[backend_name] = result
            
        except Exception as e:
            logger.warning(f"後端 {backend_name} 基準測試失敗: {e}")
            results[backend_name] = {'error': str(e)}
    
    return results