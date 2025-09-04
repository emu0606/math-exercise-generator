快速入門指南
============

歡迎使用 Math Exercise Generator！本指南將幫助你快速上手這個強大的數學測驗生成系統。

安裝和環境設定
--------------

基本需求
~~~~~~~~

.. code-block:: bash

   # Python 3.8+
   python --version
   
   # 必要依賴
   pip install numpy sympy matplotlib
   
   # 可選依賴（用於 PDF 生成）
   # LaTeX 發行版（如 MiKTeX, TeX Live）

核心功能演示
------------

1. 基礎三角形操作
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from utils import construct_triangle, get_centroid, distance, Point
   
   # 構造 3-4-5 直角三角形
   triangle = construct_triangle('sss', side_a=3, side_b=4, side_c=5)
   print(f"三角形頂點: {triangle.p1}, {triangle.p2}, {triangle.p3}")
   
   # 計算特殊點
   centroid = get_centroid(triangle)
   print(f"質心: {centroid}")
   
   # 計算距離
   side_length = distance(triangle.p1, triangle.p2)
   print(f"邊長: {side_length}")

輸出::

   三角形頂點: Point(0.000, 0.000), Point(3.000, 0.000), Point(2.733, 0.800)
   質心: Point(1.911, 0.267)
   邊長: 3.000

2. 多種構造方式
~~~~~~~~~~~~~~~

.. code-block:: python

   from utils import construct_triangle
   
   # SSS - 三邊長構造
   t1 = construct_triangle('sss', side_a=3, side_b=4, side_c=5)
   
   # SAS - 兩邊及夾角構造  
   import math
   t2 = construct_triangle('sas', side1=3, angle_rad=math.pi/2, side2=4)
   
   # ASA - 兩角及夾邊構造
   t3 = construct_triangle('asa', angle1_rad=math.pi/6, side_length=5, 
                          angle2_rad=math.pi/3)

3. 特殊點計算
~~~~~~~~~~~~~

.. code-block:: python

   from utils import (
       construct_triangle, 
       get_centroid, get_incenter, get_circumcenter, get_orthocenter
   )
   
   # 構造等邊三角形
   triangle = construct_triangle('sss', side_a=6, side_b=6, side_c=6)
   
   # 計算所有特殊點
   centroid = get_centroid(triangle)        # 質心
   incenter = get_incenter(triangle)        # 內心  
   circumcenter = get_circumcenter(triangle) # 外心
   orthocenter = get_orthocenter(triangle)  # 垂心
   
   print(f"質心: {centroid}")
   print(f"內心: {incenter}")
   print(f"外心: {circumcenter}")
   print(f"垂心: {orthocenter}")

4. TikZ 渲染功能
~~~~~~~~~~~~~~~

.. code-block:: python

   from utils import construct_triangle, tikz_coordinate
   from utils.tikz import ArcRenderer
   
   # 構造三角形
   triangle = construct_triangle('sss', side_a=3, side_b=4, side_c=5)
   
   # 座標轉換為 TikZ 格式
   tikz_p1 = tikz_coordinate(triangle.p1)
   print(f"TikZ 座標: {tikz_p1}")  # "(0.000,0.000)"
   
   # 弧線渲染
   arc_renderer = ArcRenderer()
   arc_params = arc_renderer.render_angle_arc(
       vertex=triangle.p1,
       point1=triangle.p2, 
       point2=triangle.p3,
       radius=0.5
   )
   print(f"弧線參數: {arc_params}")

常見使用模式
------------

1. 批次三角形生成
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from utils import construct_triangle, get_centroid
   
   # 生成多個三角形
   triangles = []
   for i in range(1, 6):
       triangle = construct_triangle('sss', side_a=3*i, side_b=4*i, side_c=5*i)
       triangles.append(triangle)
   
   # 計算所有質心
   centroids = [get_centroid(t) for t in triangles]
   print("所有質心:", centroids)

2. 數學後端選擇
~~~~~~~~~~~~~~~

.. code-block:: python

   from utils import configure_math_backend, get_geometry_info
   
   # 檢查可用後端
   info = get_geometry_info()
   print(f"可用後端: {info['available_backends']}")
   
   # 切換到 SymPy 後端（高精度）
   configure_math_backend('sympy')
   
   # 使用高精度計算
   from utils import get_circumcenter
   triangle = construct_triangle('sss', side_a=3, side_b=4, side_c=5)
   circumcenter = get_circumcenter(triangle)  # 使用 SymPy 精確計算

3. 錯誤處理
~~~~~~~~~~~

.. code-block:: python

   from utils import construct_triangle, TriangleDefinitionError
   
   try:
       # 嘗試構造無效三角形（違反三角形不等式）
       invalid_triangle = construct_triangle('sss', side_a=1, side_b=2, side_c=5)
   except TriangleDefinitionError as e:
       print(f"三角形構造錯誤: {e}")

進階功能
--------

1. 自定義配置
~~~~~~~~~~~~~

.. code-block:: python

   from utils.core import global_config
   
   # 修改全域配置
   global_config.debug_mode = True
   global_config.default_precision = 6
   global_config.math_backend = 'sympy'

2. PDF 生成集成
~~~~~~~~~~~~~~~

.. code-block:: python

   from utils.orchestration import PDFOrchestrator, OutputConfig
   
   # 創建 PDF 生成協調器
   config = OutputConfig(
       output_dir="./output",
       filename_prefix="math_test",
       include_answers=True
   )
   
   orchestrator = PDFOrchestrator(config)
   # 後續可集成到完整的 PDF 生成流程

下一步
------

現在你已經掌握了基本用法，可以：

1. 查看 :doc:`architecture` 了解系統架構
2. 閱讀 :doc:`migration` 了解從舊版本遷移  
3. 瀏覽 :doc:`../api/utils` 查看完整 API 文檔
4. 查看 :doc:`../development/testing` 學習如何貢獻代碼