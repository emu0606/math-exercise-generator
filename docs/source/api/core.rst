Core 模組 - 核心基礎設施
=======================

``utils.core`` 模組提供整個系統的基礎設施，包括配置管理、日誌系統、註冊機制和佈局引擎。

模組概覽
--------

.. code-block:: python

   from utils.core import (
       # 配置系統
       global_config, GlobalConfig,
       
       # 日誌系統
       get_logger, setup_logging,
       
       # 註冊系統
       registry, GeneratorRegistry,
       
       # 佈局引擎
       LayoutEngine, LayoutStrategy
   )

配置管理
--------

全域配置
~~~~~~~~

.. autoclass:: utils.core.config.GlobalConfig
   :members:
   :show-inheritance:

配置實例
~~~~~~~~

.. autodata:: utils.core.config.global_config

日誌系統
--------

.. automodule:: utils.core.logging
   :members:
   :undoc-members:
   :show-inheritance:

註冊系統
--------

註冊機制
~~~~~~~~

.. autoclass:: utils.core.registry.GeneratorRegistry
   :members:
   :show-inheritance:

全域註冊表
~~~~~~~~~~

.. autodata:: utils.core.registry.registry

佈局引擎
--------

佈局引擎類
~~~~~~~~~~

.. autoclass:: utils.core.layout.LayoutEngine
   :members:
   :show-inheritance:

佈局策略
~~~~~~~~

.. autoclass:: utils.core.layout.LayoutStrategy
   :members:
   :show-inheritance:

放置策略實現
~~~~~~~~~~~~

.. autoclass:: utils.core.layout.CompactPlacementStrategy
   :members:
   :show-inheritance:

.. autoclass:: utils.core.layout.TopLeftPlacementStrategy
   :members:
   :show-inheritance: