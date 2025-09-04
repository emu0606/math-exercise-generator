LaTeX 模組 - 文檔生成系統
==========================

``utils.latex`` 模組提供完整的 LaTeX 文檔生成和編譯功能，支持多種編譯引擎和中文配置。

模組概覽
--------

.. code-block:: python

   from utils.latex import (
       # 生成器
       LaTeXGenerator, LaTeXStructure,
       
       # 編譯器
       LaTeXCompiler, CompilerConfig,
       
       # 配置類型
       DocumentConfig, FontConfig,
       PaperSize, FontSize, Encoding,
       
       # 工具函數
       escape_latex_text, create_math_document
   )

文檔生成器
----------

LaTeX 生成器
~~~~~~~~~~~~

.. autoclass:: utils.latex.generator.LaTeXGenerator
   :members:
   :show-inheritance:

文檔結構
~~~~~~~~

.. autoclass:: utils.latex.structure.LaTeXStructure
   :members:
   :show-inheritance:

編譯系統
--------

編譯器
~~~~~~

.. autoclass:: utils.latex.compiler.LaTeXCompiler
   :members:
   :show-inheritance:

配置類型
--------

文檔配置
~~~~~~~~

.. autoclass:: utils.latex.types.DocumentConfig
   :members:
   :show-inheritance:

編譯配置
~~~~~~~~

.. autoclass:: utils.latex.types.CompilerConfig
   :members:
   :show-inheritance:

字體配置
~~~~~~~~

.. autoclass:: utils.latex.types.FontConfig
   :members:
   :show-inheritance:

枚舉類型
~~~~~~~~

.. autoclass:: utils.latex.types.PaperSize
   :members:
   :show-inheritance:

.. autoclass:: utils.latex.types.FontSize
   :members:
   :show-inheritance:

工具函數
--------

轉義功能
~~~~~~~~

.. automodule:: utils.latex.escape
   :members:
   :undoc-members:
   :show-inheritance:

配置管理
~~~~~~~~

.. automodule:: utils.latex.config
   :members:
   :undoc-members:
   :show-inheritance:

異常處理
--------

.. automodule:: utils.latex.exceptions
   :members:
   :undoc-members:
   :show-inheritance: