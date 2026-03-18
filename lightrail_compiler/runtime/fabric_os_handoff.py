"""
Stage 6c: Fabric OS Global Scheduler Handoff

The Fabric OS Global Scheduler (FOGS) is the LightRail equivalent of
CUDA's CUDA Driver / PTX executor.  It receives compiled kernels (as
CompiledKernel handles or .lrnpu blobs) and:

  1. Assigns them to wavelength channels on the physical fabric.
  2. Performs sub-microsecond optical dispatch — no thread scheduling,
     no idle-wait, deterministic single-stream execution per channel.
  3. Manages DMA between SRAM regions across photonic nodes (bypassing HBM).
  4. Returns results synchronously (or posts to a completion ring).

Contrast with CUDA:
  CUDA Driver → PTX JIT → warp scheduling → thread execution → sync
  FOGS        → .lrbs JIT → channel assignment → optical dispatch → sync

This module is the Python-level bridge to FOGS.
"""

from __future__ import annotations
import os
import time
from typing import Any, Dict, Optional, Tuple

from .jit import JITCompiler
from ..codegen.fat_binary import FatBinaryBundler, SEG_LRBS1


class DispatchResult:
    def __init__(self, value: Any, latency_ns: int):
        self.value = value
        self.latency_ns = latency_ns

    def __repr__(self):
        return f"<DispatchResult latency={self.latency_ns}ns value={self.value!r}>"


class FabricOSScheduler:
    """
    Singleton interface to the Fabric OS Global Scheduler.

    In production this communicates with the LightRail kernel module.
    In emulation mode it falls back to executing the original Python callable.
    """

    _instance: Optional["FabricOSScheduler"] = None

    def __init__(self):
        self._jit = JITCompiler()
        self._bundler = FatBinaryBundler()
        self._dispatch_count = 0

    @classmethod
    def get_instance(cls) -> "FabricOSScheduler":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def is_available(self) -> bool:
        return self._jit.has_hardware

    def dispatch(
        self,
        fat_binary: bytes,
        args: Tuple,
        kwargs: Dict,
    ) -> Any:
        """
        Dispatch a kernel represented by ``fat_binary`` with the given args.

        1. Extract the .lrbs segment from the fat binary.
        2. JIT-compile it (or use cached compilation).
        3. Hand the CompiledKernel to FOGS for optical dispatch.
        4. Return the result.
        """
        t0 = time.perf_counter_ns()

        # Extract primary .lrbs blob
        segments = self._bundler.load(fat_binary)
        lrbs_blobs = segments.get(SEG_LRBS1, [])
        if not lrbs_blobs:
            raise RuntimeError("Fat binary contains no .lrbs segment")

        lrbs = lrbs_blobs[0]

        # JIT compile
        compiled = self._jit.compile(lrbs)

        # Dispatch
        result = self._jit.execute(compiled, args, kwargs)

        self._dispatch_count += 1
        latency_ns = time.perf_counter_ns() - t0

        if result is None:
            # Hardware not available; result will be handled by caller's fallback
            return None

        return DispatchResult(value=result, latency_ns=latency_ns)

    @property
    def dispatch_count(self) -> int:
        return self._dispatch_count

    def reset_stats(self):
        self._dispatch_count = 0
