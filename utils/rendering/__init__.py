#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
圖形渲染模組

提供解耦的圖形渲染功能。
"""

from .figure_renderer import (
    FigureRenderer,
    RenderingCache,
    render_figure,
    create_figure_renderer,
    get_default_renderer
)

__version__ = "1.0.0"

from ..core.logging import get_logger
logger = get_logger(__name__)

logger.debug(f"圖形渲染模組載入完成，版本: {__version__}")

__all__ = [
    'FigureRenderer',
    'RenderingCache',
    'render_figure',
    'create_figure_renderer',
    'get_default_renderer'
]