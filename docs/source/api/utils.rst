Utils 模組 - 統一入口
=====================

``utils`` 模組是整個系統的統一入口，提供最常用的功能和便利函數。

快速導入
--------

.. code-block:: python

   # 核心幾何功能
   from utils import (
       construct_triangle,    # 三角形構造
       get_centroid,         # 質心計算
       get_incenter,         # 內心計算
       distance,             # 距離計算
       Point, Triangle       # 基本類型
   )
   
   # TikZ 渲染功能
   from utils import (
       tikz_coordinate,      # 座標轉換
       ArcRenderer,          # 弧線渲染器
       LabelPositioner       # 標籤定位器
   )

模組 API
--------

.. automodule:: utils
   :members:
   :undoc-members:
   :show-inheritance:

核心功能函數
------------

三角形構造
~~~~~~~~~~

.. autofunction:: utils.construct_triangle

特殊點計算
~~~~~~~~~~

.. autofunction:: utils.get_centroid
.. autofunction:: utils.get_incenter
.. autofunction:: utils.get_circumcenter
.. autofunction:: utils.get_orthocenter

基礎幾何運算
~~~~~~~~~~~~

.. autofunction:: utils.distance
.. autofunction:: utils.midpoint
.. autofunction:: utils.area_of_triangle

便利函數
--------

.. autofunction:: utils.create_simple_triangle_figure
.. autofunction:: utils.get_geometry_info
.. autofunction:: utils.configure_math_backend