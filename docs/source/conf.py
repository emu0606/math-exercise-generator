# Configuration file for the Sphinx documentation builder.
# Math Exercise Generator - API Documentation

import os
import sys
import datetime

# -- Path setup --------------------------------------------------------------
# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../'))

# -- Project information -----------------------------------------------------
project = 'Math Exercise Generator'
copyright = f'{datetime.datetime.now().year}, Math Exercise Generator Team'
author = 'Math Exercise Generator Team'

# The full version, including alpha/beta/rc tags
release = '1.0.0'
version = '1.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',          # 自動生成 API 文檔
    'sphinx.ext.viewcode',         # 查看原始碼連結
    'sphinx.ext.napoleon',         # 支持 Google/NumPy 風格 docstring
    'sphinx.ext.autosummary',      # 自動生成摘要表格
    'sphinx.ext.intersphinx',      # 跨專案參考連結
    'sphinx.ext.githubpages',      # GitHub Pages 支持
    'myst_parser',                 # Markdown 支持
]

# Templates path
templates_path = ['_templates']

# List of patterns to exclude
exclude_patterns = []

# Master doc
master_doc = 'index'

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'  # Read the Docs 主題
html_static_path = ['_static']

# Theme options
html_theme_options = {
    'canonical_url': '',
    'analytics_id': '',
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'vcs_pageview_mode': '',
    # Toc options
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}

# -- Extension configuration -------------------------------------------------
# autodoc 配置
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
    'special-members': '__init__',
    'private-members': False,
    'inherited-members': True,
}

# napoleon 配置 (Google/NumPy docstring 風格)
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True

# autosummary 配置
autosummary_generate = True
autosummary_imported_members = True

# intersphinx 配置
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'sympy': ('https://docs.sympy.org/latest/', None),
}

# -- Chinese language support ------------------------------------------------
language = 'zh_TW'
html_search_language = 'zh'