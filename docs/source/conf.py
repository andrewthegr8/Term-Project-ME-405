# Configuration file for the Sphinx documentation builder.
import os
import sys

# Path to repo root (the folder that contains `code/` and `pyproject.toml`)
PROJECT_ROOT = os.path.abspath(os.path.join(__file__, "..", "..", ".."))

# Put our project root *before* everything else so it wins over stdlib `code`
sys.path.insert(0, PROJECT_ROOT)

# Optionally also add the `code` directory itself and its `src` subpackage
sys.path.insert(0, os.path.join(PROJECT_ROOT, "code"))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "code", "src"))

# -- Project information

project = 'ME 405 Term Project'
copyright = '2025, Andrew Jones'
author = 'Andrew Jones'

release = '1.0'
version = '1.0.0'

# -- General configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

# -- Options for HTML output

html_theme = 'sphinx_rtd_theme'

# -- Options for EPUB output
epub_show_urls = 'footnote'
