"""
LightRail Photonic Compiler

CUDA-like OS and compiler for the LightRail Neural Compute Engine (NCE).

Primary interface::

    import lightrail_compiler as lightrail

    @lightrail.jit
    def my_kernel(A, B):
        return A @ B

    result = my_kernel(a_tensor, b_tensor)

Stages:
    1. AST Parsing & High-Level IR      (frontend.ast_parser)
    2. Type Inference & Lowering        (frontend.type_inference)
    3. Photonic-Aware Optimization      (optimizer.photonic_passes)
    4. Dataflow & Wavelength Mapping    (dataflow.wavelength_mapper)
    5. Tile Bytecode & Fat Binary       (codegen.bytecode, codegen.fat_binary)
    6. Runtime / Fabric OS Handoff      (runtime.jit, runtime.fabric_os_handoff)
"""

from .python.decorator import jit, compile, LightRailKernel, CompileOptions
from .python.runtime import LightRailRuntime, LightRailDevice, get_default_runtime

__version__ = "0.1.0"
__all__ = [
    "jit", "compile", "LightRailKernel", "CompileOptions",
    "LightRailRuntime", "LightRailDevice", "get_default_runtime",
]
