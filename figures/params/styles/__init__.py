"""樣式參數模組

提供標籤、顯示配置和其他視覺樣式相關的參數模型。

模組組件：
- labels: 標籤樣式參數 (文字、位置、格式)
- display: 顯示配置參數 (顏色、線條、填充)

Example:
    >>> from figures.params.styles import LabelParams
    >>> label = LabelParams(
    ...     x=1.0, y=2.0,
    ...     text="A",
    ...     color="blue",
    ...     variant="question"
    ... )

Note:
    樣式參數模組專注於視覺呈現配置，與幾何計算分離。
"""

__all__ = []

# TODO: 重構完成後將添加以下導出
# from .labels import LabelParams
# from .display import DisplayConfig