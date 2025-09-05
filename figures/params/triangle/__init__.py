"""三角形參數模組

提供基礎和高級三角形參數配置，支援多種三角形類型和複雜的自定義選項。

模組組件：
- basic: 基礎三角形參數 (推薦日常使用)
- advanced: 高級三角形參數 (包含複雜的 PredefinedTriangleParams)

Example:
    >>> # 基礎使用
    >>> from figures.params.triangle import BasicTriangleParams
    >>> params = BasicTriangleParams(
    ...     p1=(0, 0), p2=(1, 0), p3=(0.5, 1),
    ...     variant="question"
    ... )
    
    >>> # 高級使用 (謹慎使用)
    >>> from figures.params.triangle import PredefinedTriangleParams
    >>> advanced_params = PredefinedTriangleParams(
    ...     triangle_type="equilateral",
    ...     side_length=2.0,
    ...     variant="question"
    ... )

Warning:
    advanced 模組包含非常複雜的參數配置，建議優先使用 basic 模組。
"""

__all__ = []

# TODO: 重構完成後將添加以下導出
# from .basic import BasicTriangleParams
# from .advanced import PredefinedTriangleParams