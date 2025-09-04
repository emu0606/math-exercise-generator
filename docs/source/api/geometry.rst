Geometry 模組 - 幾何計算核心
==============================

``utils.geometry`` 模組提供強大的幾何計算功能，支持多種數學後端和現代化的類型系統。

模組概覽
--------

.. code-block:: python

   from utils.geometry import (
       # 基礎類型
       Point, Vector, Triangle, Circle, Line,
       
       # 三角形構造
       construct_triangle, TriangleConstructor,
       
       # 特殊點計算
       get_centroid, get_incenter, get_circumcenter,
       
       # 基礎運算
       distance, midpoint, area_of_triangle, 
       angle_between_vectors,
       
       # 數學後端
       configure_math_backend, get_geometry_info
   )

核心類型
--------

基礎幾何類型
~~~~~~~~~~~~

.. autoclass:: utils.geometry.types.Point
   :members:
   :show-inheritance:

.. autoclass:: utils.geometry.types.Vector  
   :members:
   :show-inheritance:

.. autoclass:: utils.geometry.types.Triangle
   :members:
   :show-inheritance:

三角形構造
----------

構造函數
~~~~~~~~

.. automodule:: utils.geometry.triangle_construction
   :members:
   :undoc-members:
   :show-inheritance:

構造器類
~~~~~~~~

.. autoclass:: utils.geometry.triangle_construction.TriangleConstructor
   :members:
   :show-inheritance:

特殊點計算
----------

.. automodule:: utils.geometry.triangle_centers
   :members:
   :undoc-members:
   :show-inheritance:

基礎運算
--------

.. automodule:: utils.geometry.basic_ops
   :members:
   :undoc-members:
   :show-inheritance:

數學後端
--------

.. automodule:: utils.geometry.math_backend
   :members:
   :undoc-members:
   :show-inheritance:

異常處理
--------

.. automodule:: utils.geometry.exceptions
   :members:
   :undoc-members:
   :show-inheritance: