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
import time as _time
from collections import deque
import builtins

# Sphinx should not try to import real MicroPython modules
autodoc_mock_imports = ["pyb", "micropython", "ucollections"]

# ------------------------------
# Mock 'pyb' module and classes
# ------------------------------
pyb = types.ModuleType("pyb")

class Pin:
    """Stub for pyb.Pin used only for documentation."""
    OUT_PP = 0

    def __init__(self, *args, **kwargs):
        pass

    def high(self):
        pass

    def low(self):
        pass


class Timer:
    """Stub for pyb.Timer used only for documentation."""
    PWM = 0
    ENC_AB = 1

    def __init__(self, *args, **kwargs):
        pass

    def channel(self, *args, **kwargs):
        # Return self so that `self.tim.channel(...)` is harmless
        return self

    def counter(self, *args, **kwargs):
        return 0

    def period(self):
        return 65535


pyb.Pin = Pin
pyb.Timer = Timer

# Make this fake module available as 'pyb'
sys.modules["pyb"] = pyb

# Also put it in builtins so code that *only* does
# "from pyb import Pin, Timer" can still see `pyb` in annotations.
builtins.pyb = pyb

# ------------------------------
# Mock 'micropython' module
# ------------------------------
micropython = types.ModuleType("micropython")

def native(func):
    """Decorator stub that just returns the function unchanged."""
    return func

micropython.native = native
sys.modules["micropython"] = micropython

# ------------------------------
# Mock 'ucollections.deque'
# ------------------------------
ucollections = types.ModuleType("ucollections")
ucollections.deque = deque
sys.modules["ucollections"] = ucollections

# ------------------------------
# Provide time.ticks_us / ticks_diff
# ------------------------------
def ticks_us():
    return int(_time.perf_counter() * 1_000_000)

def ticks_diff(new, old):
    return new - old

# Inject into the real 'time' module so
# "from time import ticks_us, ticks_diff" works.
if not hasattr(_time, "ticks_us"):
    _time.ticks_us = ticks_us
if not hasattr(_time, "ticks_diff"):
    _time.ticks_diff = ticks_diff


# ------------------------------------------------------------
# MicroPython compatibility: fake 'utime' for docs build only
# ------------------------------------------------------------
utime = types.ModuleType("utime")

def _ticks_us():
    """Return a monotonically increasing time in microseconds (stub)."""
    return int(_time.perf_counter() * 1_000_000)

def _ticks_ms():
    """Return a monotonically increasing time in milliseconds (stub)."""
    return int(_time.perf_counter() * 1_000)

def _ticks_diff(new, old):
    """Return signed difference between two tick readings (stub)."""
    return new - old

def _sleep_ms(ms):
    """Sleep for the given number of milliseconds (stub)."""
    _time.sleep(ms / 1000.0)

def _sleep_us(us):
    """Sleep for the given number of microseconds (stub)."""
    _time.sleep(us / 1_000_000.0)

# Wire these into the fake utime module
utime.ticks_us = _ticks_us
utime.ticks_ms = _ticks_ms
utime.ticks_diff = _ticks_diff
utime.sleep_ms = _sleep_ms
utime.sleep_us = _sleep_us

# Register the fake module so `import utime` works
sys.modules["utime"] = utime

#Show type hints nicely in the parameter docs
autodoc_typehints = "description"

autodoc_type_aliases = {
    "Pin": "pyb.Pin",
    "Timer": "pyb.Timer",
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

# --- Extra pyb stubs for docs build (UART, I2C, IRQ helpers) ---

class UART:
    """Stub for pyb.UART used only for documentation."""
    def __init__(self, *args, **kwargs):
        pass

    def read(self, *args, **kwargs):
        return b""

    def write(self, *args, **kwargs):
        return 0

class I2C:
    """Stub for pyb.I2C used only for documentation."""
    CONTROLLER = 0

    def __init__(self, *args, **kwargs):
        pass

    def mem_read(self, *args, **kwargs):
        return b""

    def mem_write(self, *args, **kwargs):
        return 0

# Attach to the fake pyb module
pyb.UART = UART
pyb.I2C = I2C

# IRQ helpers used by task_share.Queue/Share
def _disable_irq():
    return 0

def _enable_irq(state):
    return None

pyb.disable_irq = _disable_irq
pyb.enable_irq = _enable_irq



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
