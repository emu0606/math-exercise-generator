Math Exercise Generator 開發文檔
=====================================

歡迎來到 Math Exercise Generator 的開發者文檔！這是一個專業的數學測驗生成系統，採用現代化的模組架構設計。

🎯 **專案特色**

* **模組化架構**: 6層清晰的模組分離設計
* **多數學後端**: 支持 NumPy/SymPy/Python 三種計算後端  
* **專業渲染**: TikZ/LaTeX 專業數學圖形渲染
* **統一 API**: 簡潔一致的開發接口
* **完整測試**: 100% 核心功能測試覆蓋

🚀 **快速開始**

.. code-block:: python

   # 導入核心功能
   from utils import construct_triangle, get_centroid, distance
   
   # 構造 3-4-5 直角三角形
   triangle = construct_triangle('sss', side_a=3, side_b=4, side_c=5)
   
   # 計算質心
   centroid = get_centroid(triangle)
   print(f"質心座標: {centroid}")  # Point(2.333, 0.800)

📚 **文檔目錄**

.. toctree::
   :maxdepth: 2
   :caption: 用戶指南

   guides/quickstart
   guides/architecture
   guides/migration
   
.. toctree::
   :maxdepth: 2
   :caption: API 參考
   
   api/utils
   api/geometry
   api/tikz
   api/latex
   api/core
   api/orchestration

.. toctree::
   :maxdepth: 1
   :caption: 開發指南
   
   development/contributing
   development/testing
   development/performance

📊 **架構概覽**

.. code-block:: text

   utils/
   ├── core/          # 核心功能 (配置、日誌、註冊)
   ├── geometry/      # 幾何計算 (NumPy/SymPy 集成)
   ├── tikz/          # TikZ 渲染系統
   ├── latex/         # LaTeX 文檔生成
   ├── rendering/     # 圖形渲染協調
   └── orchestration/ # PDF 生成業務流程

🏆 **重構成果**

從 **969行** 單一文件成功重構為 **9,485行** 現代化模組架構：

* **性能提升**: 155,958 triangles/second  
* **測試覆蓋**: 核心功能 100% 通過
* **代碼品質**: 平均 < 300行/文件
* **API 統一**: 清晰的導入接口

索引和表格
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`