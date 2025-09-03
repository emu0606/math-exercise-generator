"""
幾何計算異常定義

定義幾何計算中可能遇到的各種異常情況，提供清晰的錯誤分類和處理機制。

使用方式：
    from utils.geometry.exceptions import GeometryError, TriangleError
    
    try:
        result = calculate_triangle_area(p1, p2, p3)
    except TriangleError as e:
        logger.error(f"三角形計算錯誤: {e}")
    except GeometryError as e:
        logger.error(f"幾何計算錯誤: {e}")
"""

from typing import Any, Optional, Tuple


class GeometryError(Exception):
    """幾何計算基礎異常類
    
    所有幾何相關異常的基類，提供統一的錯誤處理介面。
    """
    
    def __init__(self, message: str, details: Optional[dict] = None):
        """初始化幾何異常
        
        Args:
            message: 錯誤訊息
            details: 額外的錯誤詳情，用於調試
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self) -> str:
        """返回詳細的錯誤描述"""
        base_msg = self.message
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{base_msg} (詳情: {details_str})"
        return base_msg


class ValidationError(GeometryError):
    """參數驗證錯誤
    
    當輸入的參數不符合幾何計算要求時拋出。
    """
    
    def __init__(self, parameter: str, value: Any, requirement: str):
        """初始化驗證錯誤
        
        Args:
            parameter: 參數名稱
            value: 無效的參數值
            requirement: 參數要求說明
        """
        message = f"參數 '{parameter}' 驗證失敗: {requirement}"
        details = {
            'parameter': parameter,
            'value': str(value),
            'requirement': requirement
        }
        super().__init__(message, details)
        self.parameter = parameter
        self.value = value
        self.requirement = requirement


class TriangleError(GeometryError):
    """三角形相關錯誤基類
    
    所有三角形計算相關的錯誤基類。
    """
    pass


class TriangleDefinitionError(TriangleError):
    """三角形定義錯誤
    
    當提供的參數無法構成有效三角形時拋出。
    繼承自原始代碼中的 TriangleDefinitionError，保持向後相容。
    """
    
    def __init__(self, definition_mode: str, reason: str, **params):
        """初始化三角形定義錯誤
        
        Args:
            definition_mode: 三角形定義模式 (sss, sas, asa, aas, coordinates)
            reason: 具體的錯誤原因
            **params: 相關的參數值
        """
        message = f"三角形定義錯誤 ({definition_mode} 模式): {reason}"
        details = {
            'definition_mode': definition_mode,
            'reason': reason,
            **params
        }
        super().__init__(message, details)
        self.definition_mode = definition_mode
        self.reason = reason
        self.params = params


class TriangleConstructionError(TriangleError):
    """三角形構造錯誤
    
    當三角形構造過程中發生錯誤時拋出。
    """
    
    def __init__(self, message: str, construction_mode: str = "unknown", **params):
        """初始化三角形構造錯誤
        
        Args:
            message: 錯誤訊息
            construction_mode: 構造模式 (sss, sas, asa, aas, coordinates)
            **params: 相關的構造參數
        """
        details = {
            'construction_mode': construction_mode,
            **params
        }
        super().__init__(message, details)
        self.construction_mode = construction_mode
        self.params = params


class TriangleInequalityError(TriangleDefinitionError):
    """三角形不等式錯誤
    
    當三邊長度不滿足三角形不等式時拋出。
    """
    
    def __init__(self, side_a: float, side_b: float, side_c: float):
        """初始化三角形不等式錯誤
        
        Args:
            side_a: 邊 a 的長度
            side_b: 邊 b 的長度  
            side_c: 邊 c 的長度
        """
        # 檢查哪個不等式失敗了
        failures = []
        if side_a >= side_b + side_c:
            failures.append(f"a ({side_a}) >= b + c ({side_b + side_c})")
        if side_b >= side_a + side_c:
            failures.append(f"b ({side_b}) >= a + c ({side_a + side_c})")
        if side_c >= side_a + side_b:
            failures.append(f"c ({side_c}) >= a + b ({side_a + side_b})")
        
        failure_desc = "; ".join(failures) if failures else "未知原因"
        reason = f"不滿足三角形不等式: {failure_desc}"
        
        super().__init__(
            "sss", 
            reason, 
            side_a=side_a, 
            side_b=side_b, 
            side_c=side_c
        )


class DegenerateTriangleError(TriangleDefinitionError):
    """退化三角形錯誤
    
    當三個點共線或過於接近，導致三角形退化時拋出。
    """
    
    def __init__(self, points: Optional[Tuple] = None, reason: str = "三點共線或過於接近"):
        """初始化退化三角形錯誤
        
        Args:
            points: 導致退化的三個點 (可選)
            reason: 退化原因的詳細描述
        """
        params = {}
        if points:
            params['points'] = str(points)
        
        super().__init__(
            "coordinates",
            reason,
            **params
        )


class CircleError(GeometryError):
    """圓形相關錯誤基類
    
    所有圓形計算相關的錯誤基類。
    """
    pass


class InvalidRadiusError(CircleError):
    """無效半徑錯誤
    
    當圓的半徑為非正數時拋出。
    """
    
    def __init__(self, radius: float):
        """初始化無效半徑錯誤
        
        Args:
            radius: 無效的半徑值
        """
        message = f"無效的圓半徑: {radius} (半徑必須為正數)"
        details = {'radius': radius}
        super().__init__(message, details)
        self.radius = radius


class CircleConstructionError(CircleError):
    """圓構造錯誤
    
    當無法根據給定參數構造圓時拋出。
    """
    
    def __init__(self, reason: str, **params):
        """初始化圓構造錯誤
        
        Args:
            reason: 構造失敗的原因
            **params: 相關參數
        """
        message = f"圓構造錯誤: {reason}"
        super().__init__(message, params)
        self.reason = reason
        self.params = params


class ComputationError(GeometryError):
    """計算錯誤
    
    當幾何計算過程中遇到數學錯誤時拋出。
    """
    
    def __init__(self, operation: str, reason: str, **context):
        """初始化計算錯誤
        
        Args:
            operation: 正在執行的計算操作
            reason: 計算失敗的原因
            **context: 計算上下文資訊
        """
        message = f"計算錯誤 ({operation}): {reason}"
        details = {
            'operation': operation,
            'reason': reason,
            **context
        }
        super().__init__(message, details)
        self.operation = operation
        self.reason = reason
        self.context = context


class NumericalInstabilityError(ComputationError):
    """數值不穩定錯誤
    
    當計算結果由於數值精度問題而不可靠時拋出。
    """
    
    def __init__(self, operation: str, precision_issue: str, **context):
        """初始化數值不穩定錯誤
        
        Args:
            operation: 不穩定的計算操作
            precision_issue: 精度問題描述
            **context: 相關上下文
        """
        reason = f"數值精度問題: {precision_issue}"
        super().__init__(operation, reason, **context)


class RenderingError(GeometryError):
    """渲染參數錯誤
    
    當計算渲染參數時遇到問題時拋出。
    """
    
    def __init__(self, element_type: str, reason: str, **params):
        """初始化渲染錯誤
        
        Args:
            element_type: 渲染元素類型 (arc, label, etc.)
            reason: 錯誤原因
            **params: 渲染參數
        """
        message = f"渲染參數錯誤 ({element_type}): {reason}"
        details = {
            'element_type': element_type,
            'reason': reason,
            **params
        }
        super().__init__(message, details)
        self.element_type = element_type
        self.reason = reason
        self.params = params


class LabelPlacementError(RenderingError):
    """標籤放置錯誤
    
    當無法計算合適的標籤放置位置時拋出。
    """
    
    def __init__(self, label_type: str, reason: str, **context):
        """初始化標籤放置錯誤
        
        Args:
            label_type: 標籤類型
            reason: 放置失敗原因
            **context: 相關上下文
        """
        super().__init__(f"label_{label_type}", f"標籤放置失敗: {reason}", **context)


class ConfigurationError(GeometryError):
    """配置錯誤
    
    當幾何計算的配置參數不正確時拋出。
    """
    
    def __init__(self, config_key: str, value: Any, expected: str):
        """初始化配置錯誤
        
        Args:
            config_key: 配置項名稱
            value: 錯誤的配置值
            expected: 期望的配置值描述
        """
        message = f"配置錯誤: {config_key} = {value}，期望: {expected}"
        details = {
            'config_key': config_key,
            'value': str(value),
            'expected': expected
        }
        super().__init__(message, details)
        self.config_key = config_key
        self.value = value
        self.expected = expected


# 便利函數：快速創建常見異常

def invalid_point_error(point: Any, context: str = "") -> ValidationError:
    """創建無效點座標異常
    
    Args:
        point: 無效的點座標
        context: 額外的上下文描述
        
    Returns:
        ValidationError 實例
    """
    requirement = "必須是 (x, y) 格式的數值座標對"
    if context:
        requirement += f" ({context})"
    return ValidationError("point", point, requirement)


def invalid_angle_error(angle: float, context: str = "") -> ValidationError:
    """創建無效角度異常
    
    Args:
        angle: 無效的角度值
        context: 額外的上下文描述
        
    Returns:
        ValidationError 實例
    """
    requirement = "角度必須在有效範圍內 (通常為 0 到 2π 弧度)"
    if context:
        requirement += f" ({context})"
    return ValidationError("angle", angle, requirement)


def invalid_distance_error(distance: float, context: str = "") -> ValidationError:
    """創建無效距離異常
    
    Args:
        distance: 無效的距離值
        context: 額外的上下文描述
        
    Returns:
        ValidationError 實例
    """
    requirement = "距離必須為非負數值"
    if context:
        requirement += f" ({context})"
    return ValidationError("distance", distance, requirement)