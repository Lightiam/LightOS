"""
LightRail Photonic Compiler - Python Interface

Provides @lightrail.jit decorator and supporting utilities for targeting
the LightRail Neural Compute Engine (NCE) photonic fabric.
"""

from .decorator import jit, compile, LightRailKernel
from .runtime import LightRailRuntime, get_default_runtime

__all__ = ["jit", "compile", "LightRailKernel", "LightRailRuntime", "get_default_runtime"]
