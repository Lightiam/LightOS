"""
Stage 1 entry point: @lightrail.jit decorator

Parses the decorated function's AST, splits Host/Device code, and
kicks off the 6-stage LightRail compilation pipeline.
"""

import ast
import functools
import inspect
import textwrap
import hashlib
from typing import Any, Callable, Dict, Optional, Tuple

from ..frontend.ast_parser import ASTParser
from ..frontend.type_inference import TypeInferenceEngine
from ..optimizer.photonic_passes import PhotonicOptimizer
from ..dataflow.wavelength_mapper import WavelengthMapper
from ..codegen.bytecode import BytecodeGenerator
from ..codegen.fat_binary import FatBinaryBundler
from ..runtime.jit import JITCompiler


class CompileOptions:
    """Compilation configuration for a LightRail kernel."""

    def __init__(
        self,
        num_wavelengths: int = 64,
        enable_ternary: bool = True,
        enable_analog: bool = True,
        enable_fma_fusion: bool = True,
        enable_loop_splitting: bool = True,
        target_layers: Tuple[int, ...] = tuple(range(1, 21)),
        aot: bool = False,
        debug: bool = False,
    ):
        self.num_wavelengths = num_wavelengths   # WDM virtual processors
        self.enable_ternary = enable_ternary      # Ternary logic support (-1,0,+1)
        self.enable_analog = enable_analog         # Analog wave compute (layers 6-7)
        self.enable_fma_fusion = enable_fma_fusion
        self.enable_loop_splitting = enable_loop_splitting
        self.target_layers = target_layers         # Active photonic layers (1-20)
        self.aot = aot                             # Ahead-of-time vs JIT
        self.debug = debug


class LightRailKernel:
    """
    A compiled, ready-to-dispatch LightRail kernel.

    Wraps the fat binary and provides a callable interface that transparently
    dispatches to the photonic fabric or falls back to CPU emulation when no
    hardware is present.
    """

    def __init__(
        self,
        fn: Callable,
        fat_binary: bytes,
        options: CompileOptions,
        source_hash: str,
    ):
        self._fn = fn
        self._fat_binary = fat_binary
        self._options = options
        self._source_hash = source_hash
        self._jit_compiler: Optional[JITCompiler] = None
        self.__name__ = fn.__name__
        self.__doc__ = fn.__doc__

    def __call__(self, *args, **kwargs):
        from ..runtime.fabric_os_handoff import FabricOSScheduler
        scheduler = FabricOSScheduler.get_instance()
        if scheduler.is_available():
            return scheduler.dispatch(self._fat_binary, args, kwargs)
        # Software emulation fallback (CPU)
        return self._fn(*args, **kwargs)

    def __repr__(self):
        return (
            f"<LightRailKernel '{self.__name__}' "
            f"wavelengths={self._options.num_wavelengths} "
            f"hash={self._source_hash[:8]}>"
        )


# ---------------------------------------------------------------------------
# Internal pipeline runner
# ---------------------------------------------------------------------------

_KERNEL_CACHE: Dict[str, LightRailKernel] = {}


def _compile_fn(fn: Callable, options: CompileOptions) -> LightRailKernel:
    source = textwrap.dedent(inspect.getsource(fn))
    source_hash = hashlib.sha256(source.encode()).hexdigest()

    cache_key = f"{fn.__qualname__}:{source_hash}:{id(options)}"
    if cache_key in _KERNEL_CACHE:
        return _KERNEL_CACHE[cache_key]

    # --- Stage 1: AST Parsing & High-Level IR ---
    tree = ast.parse(source)
    parser = ASTParser(fn.__globals__)
    high_level_ir = parser.parse(tree, fn)

    # --- Stage 2: Type Inference & Lowering ---
    type_engine = TypeInferenceEngine(options)
    typed_ir = type_engine.infer_and_lower(high_level_ir)

    # --- Stage 3: Photonic-Aware Optimization ---
    optimizer = PhotonicOptimizer(options)
    optimized_ir = optimizer.run_passes(typed_ir)

    # --- Stage 4: Dataflow & Wavelength Mapping ---
    mapper = WavelengthMapper(options.num_wavelengths, options.target_layers)
    dataflow_ir = mapper.map(optimized_ir)

    # --- Stage 5: Bytecode & Fat Binary ---
    codegen = BytecodeGenerator(options)
    bytecode = codegen.emit(dataflow_ir)
    bundler = FatBinaryBundler()
    fat_binary = bundler.bundle(bytecode, host_fn=fn)

    kernel = LightRailKernel(fn, fat_binary, options, source_hash)
    _KERNEL_CACHE[cache_key] = kernel
    return kernel


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def jit(
    fn: Optional[Callable] = None,
    *,
    num_wavelengths: int = 64,
    enable_ternary: bool = True,
    enable_analog: bool = True,
    enable_fma_fusion: bool = True,
    enable_loop_splitting: bool = True,
    target_layers: Tuple[int, ...] = tuple(range(1, 21)),
    aot: bool = False,
    debug: bool = False,
):
    """
    JIT-compile a Python function for the LightRail Neural Compute Engine.

    Usage::

        @lightrail.jit
        def my_kernel(a, b):
            return a @ b

        # With options:
        @lightrail.jit(num_wavelengths=32, enable_ternary=True)
        def my_kernel(a, b):
            return a @ b

    Parameters
    ----------
    num_wavelengths : int
        Number of WDM channels (virtual processors). Default 64.
    enable_ternary : bool
        Map logic to ternary encoding (-1, 0, +1) where supported.
    enable_analog : bool
        Offload to analog wave compute layers (6 & 7).
    enable_fma_fusion : bool
        Fuse multiply-add operations into single optical steps.
    enable_loop_splitting : bool
        Split loops for better photonic tile utilization.
    target_layers : tuple[int]
        Which of the 20 optical fabric layers to target.
    aot : bool
        Emit AOT machine code instead of portable bytecode + JIT.
    debug : bool
        Preserve IR dumps and emit verbose diagnostics.
    """
    options = CompileOptions(
        num_wavelengths=num_wavelengths,
        enable_ternary=enable_ternary,
        enable_analog=enable_analog,
        enable_fma_fusion=enable_fma_fusion,
        enable_loop_splitting=enable_loop_splitting,
        target_layers=target_layers,
        aot=aot,
        debug=debug,
    )

    def decorator(f: Callable) -> LightRailKernel:
        kernel = _compile_fn(f, options)

        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            return kernel(*args, **kwargs)

        wrapper._lightrail_kernel = kernel
        return wrapper

    if fn is not None:
        # Called as @lightrail.jit without parentheses
        return decorator(fn)
    return decorator


def compile(fn: Callable, **kwargs) -> LightRailKernel:
    """Eagerly compile ``fn`` and return the LightRailKernel object."""
    options = CompileOptions(**kwargs)
    return _compile_fn(fn, options)
