# Configuration file for the Sphinx documentation builder.
import os
import sys

# Add repo root (folder that contains `code/` and `pyproject.toml`)
sys.path.insert(0, os.path.abspath('../..'))

# -- Project information

project = 'ME 405 Term Project'
copyright = '2025, Andrew Jones'
author = 'Andrew Jones'

release = '1.0'
version = '1.0.0'

# -- General configuration

extensions = [
    'sphinx.ext.duration',
    'sphinxcontrib.youtube',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    "sphinx.ext.napoleon",
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
]
autosummary_generate = True

# Tell autodoc to pretend these MicroPython-only modules exist.
# This lets us import me405.Motor, me405.Encoder, etc. on Read the Docs.
autodoc_mock_imports = [
    "pyb",
    "micropython",
    "ucollections",
]

# ------------------------------------------------------------
# MicroPython compatibility mocks so CPython can import firmware
# ------------------------------------------------------------
import types

# Create dummy 'pyb' module with dummy classes used in your code
pyb = types.ModuleType("pyb")

class DummyPin:
    OUT_PP = 0
    def __init__(self, *a, **kw): pass
    def high(self): pass
    def low(self): pass

class DummyTimer:
    PWM = 0
    ENC_AB = 1
    def __init__(self, *a, **kw): pass
    def channel(self, *a, **kw): return self
    def counter(self, *a, **kw): return 0
    def period(self): return 65535

pyb.Pin = DummyPin
pyb.Timer = DummyTimer

sys.modules["pyb"] = pyb

autodoc_type_aliases = {
    "DummyPin": "pyb.Pin",
    "DummyTimer": "pyb.Timer",
}


# ---- Mock micropython.native decorator ----
micropython = types.ModuleType("micropython")
def native(func): return func
micropython.native = native
sys.modules["micropython"] = micropython


# ---- Mock ucollections.deque ----
ucollections = types.ModuleType("ucollections")
from collections import deque
ucollections.deque = deque
sys.modules["ucollections"] = ucollections


# ---- Mock time.ticks_us and ticks_diff ----
import time as _time
def ticks_us(): return int(_time.perf_counter() * 1_000_000)
def ticks_diff(new, old): return new - old

if not hasattr(_time, "ticks_us"):
    # inject these into the time module for import compatibility
    _time.ticks_us = ticks_us
    _time.ticks_diff = ticks_diff

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
