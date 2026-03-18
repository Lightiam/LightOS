"""
Stage 6a: Just-In-Time Compiler

The JIT path compiles .lrbs bytecode on-the-fly when the kernel is first
invoked on real LightRail hardware.  It preserves the portable bytecode
as a cache entry so subsequent calls skip recompilation.

Compilation flow (JIT):
  .lrbs bytecode
       │
       ▼
  LightRail Driver (kernel module) ← calls ioctl(LR_IOCTL_COMPILE)
       │
       ▼
  NCE machine code (NPU binary)
       │
       ▼
  Fabric OS Global Scheduler → dispatch

This module provides the Python-side interface to that driver path,
with a software-only emulation when hardware is absent.
"""

from __future__ import annotations
import hashlib
import os
import struct
from typing import Any, Dict, Optional, Tuple


# Driver ioctl numbers (mirrored from kernel/drivers/lightrail_npu.h)
LR_IOCTL_COMPILE  = 0xC0184C01
LR_IOCTL_DISPATCH = 0xC0184C02
LR_IOCTL_FREE     = 0xC0184C03


class CompiledKernel:
    """Handle to a kernel that has been compiled by the driver."""

    def __init__(self, handle: int, bytecode_hash: str):
        self.handle = handle          # opaque driver handle
        self.bytecode_hash = bytecode_hash
        self._exec_count = 0

    def __repr__(self):
        return f"<CompiledKernel handle={self.handle:#x} calls={self._exec_count}>"


class JITCompiler:
    """
    Manages JIT compilation of .lrbs bytecode blobs via the LightRail
    kernel driver.  Falls back to a software interpreter when the driver
    is not present.
    """

    _DRIVER_PATH = "/dev/lightrail0"

    def __init__(self):
        self._cache: Dict[str, CompiledKernel] = {}
        self._driver_fd: Optional[int] = None
        self._try_open_driver()

    def _try_open_driver(self):
        if os.path.exists(self._DRIVER_PATH):
            try:
                self._driver_fd = os.open(self._DRIVER_PATH, os.O_RDWR)
            except OSError:
                self._driver_fd = None

    @property
    def has_hardware(self) -> bool:
        return self._driver_fd is not None

    def compile(self, lrbs_bytes: bytes) -> CompiledKernel:
        """Compile .lrbs bytecode; returns a driver handle or emulated handle."""
        bchash = hashlib.sha256(lrbs_bytes).hexdigest()
        if bchash in self._cache:
            return self._cache[bchash]

        if self.has_hardware:
            handle = self._ioctl_compile(lrbs_bytes)
        else:
            # Software emulation: assign a pseudo handle
            handle = hash(bchash) & 0xFFFFFFFF

        kernel = CompiledKernel(handle=handle, bytecode_hash=bchash)
        self._cache[bchash] = kernel
        return kernel

    def execute(self, kernel: CompiledKernel, args: Tuple, kwargs: Dict) -> Any:
        """Execute a compiled kernel with the given arguments."""
        kernel._exec_count += 1
        if self.has_hardware:
            return self._ioctl_dispatch(kernel.handle, args, kwargs)
        # Software emulation: return None (caller handles fallback)
        return None

    def free(self, kernel: CompiledKernel):
        """Release driver resources for a compiled kernel."""
        if self.has_hardware and kernel.handle:
            self._ioctl_free(kernel.handle)
        self._cache.pop(kernel.bytecode_hash, None)

    # ------------------------------------------------------------------
    # Driver ioctl wrappers (stubs — real impl calls fcntl.ioctl)
    # ------------------------------------------------------------------

    def _ioctl_compile(self, lrbs_bytes: bytes) -> int:
        # In production: fcntl.ioctl(self._driver_fd, LR_IOCTL_COMPILE, buf)
        return hash(lrbs_bytes) & 0xFFFFFFFF

    def _ioctl_dispatch(self, handle: int, args: Tuple, kwargs: Dict) -> Any:
        # In production: write dispatch descriptor to driver fd
        return None

    def _ioctl_free(self, handle: int):
        # In production: fcntl.ioctl(self._driver_fd, LR_IOCTL_FREE, handle)
        pass

    def __del__(self):
        if self._driver_fd is not None:
            try:
                os.close(self._driver_fd)
            except OSError:
                pass
