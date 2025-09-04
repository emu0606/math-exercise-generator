Orchestration 模組 - 業務流程協調
==================================

``utils.orchestration`` 模組提供 PDF 生成的完整業務流程協調，包括題目分配、錯誤處理和進度追蹤。

模組概覽
--------

.. code-block:: python

   from utils.orchestration import (
       # 主協調器
       PDFOrchestrator,
       
       # 題目分配
       QuestionDistributor, DistributionStrategy,
       
       # 錯誤處理
       ErrorHandler, ErrorSeverity,
       
       # 進度追蹤
       ProgressReporter, ProgressTracker,
       
       # 便利函數
       generate_pdf_with_orchestration,
       create_default_orchestrator
   )

PDF 協調器
----------

主協調器
~~~~~~~~

.. autoclass:: utils.orchestration.pdf_orchestrator.PDFOrchestrator
   :members:
   :show-inheritance:

配置類型
~~~~~~~~

.. autoclass:: utils.orchestration.pdf_orchestrator.OutputConfig
   :members:
   :show-inheritance:

.. autoclass:: utils.orchestration.pdf_orchestrator.ContentConfig
   :members:
   :show-inheritance:

題目分配系統
------------

分配器
~~~~~~

.. autoclass:: utils.orchestration.question_distributor.QuestionDistributor
   :members:
   :show-inheritance:

分配策略
~~~~~~~~

.. autoclass:: utils.orchestration.question_distributor.DistributionStrategy
   :members:
   :show-inheritance:

錯誤處理系統
------------

錯誤處理器
~~~~~~~~~~

.. autoclass:: utils.orchestration.error_handler.ErrorHandler
   :members:
   :show-inheritance:

錯誤類型
~~~~~~~~

.. autoclass:: utils.orchestration.error_handler.ErrorSeverity
   :members:
   :show-inheritance:

.. autoclass:: utils.orchestration.error_handler.ErrorType
   :members:
   :show-inheritance:

專門異常
~~~~~~~~

.. autoclass:: utils.orchestration.error_handler.QuestionGenerationError
   :members:
   :show-inheritance:

.. autoclass:: utils.orchestration.error_handler.LayoutError
   :members:
   :show-inheritance:

進度追蹤系統
------------

進度報告器
~~~~~~~~~~

.. autoclass:: utils.orchestration.progress_reporter.ProgressReporter
   :members:
   :show-inheritance:

進度追蹤器
~~~~~~~~~~

.. autoclass:: utils.orchestration.progress_reporter.ProgressTracker
   :members:
   :show-inheritance:

便利函數
--------

.. autofunction:: utils.orchestration.generate_pdf_with_orchestration
.. autofunction:: utils.orchestration.create_default_orchestrator
.. autofunction:: utils.orchestration.generate_latex_pdfs