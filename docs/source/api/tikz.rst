TikZ 模組 - 專業圖形渲染
========================

``utils.tikz`` 模組提供專業的 TikZ 圖形渲染功能，包括座標轉換、弧線渲染和標籤定位。

模組概覽
--------

.. code-block:: python

   from utils.tikz import (
       # 渲染器
       ArcRenderer, LabelPositioner,
       
       # 座標轉換
       tikz_coordinate, tikz_angle_degrees,
       CoordinateTransformer,
       
       # 類型和配置
       TikZPosition, TikZAnchor,
       ArcConfig, LabelConfig,
       
       # 便利函數
       get_arc_render_params,  # 向後相容
       position_vertex_label_auto
   )

核心渲染器
----------

弧線渲染器
~~~~~~~~~~

.. autoclass:: utils.tikz.arc_renderer.ArcRenderer
   :members:
   :show-inheritance:

標籤定位器  
~~~~~~~~~~

.. autoclass:: utils.tikz.label_positioner.LabelPositioner
   :members:
   :show-inheritance:

座標轉換
--------

轉換函數
~~~~~~~~

.. automodule:: utils.tikz.coordinate_transform
   :members:
   :undoc-members:
   :show-inheritance:

轉換器類
~~~~~~~~

.. autoclass:: utils.tikz.coordinate_transform.CoordinateTransformer
   :members:
   :show-inheritance:

類型和配置
----------

枚舉類型
~~~~~~~~

.. autoclass:: utils.tikz.types.TikZPosition
   :members:
   :show-inheritance:

.. autoclass:: utils.tikz.types.TikZAnchor
   :members:
   :show-inheritance:

配置類
~~~~~~

.. autoclass:: utils.tikz.types.ArcConfig
   :members:
   :show-inheritance:

.. autoclass:: utils.tikz.types.LabelConfig
   :members:
   :show-inheritance:

異常處理
--------

.. automodule:: utils.tikz.exceptions
   :members:
   :undoc-members:
   :show-inheritance: