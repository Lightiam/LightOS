"""
Stage 6b: Ahead-of-Time (AOT) Compilation

Produces a native NPU binary directly from the .lrbs bytecode.
The AOT path is used for deployment scenarios where JIT warm-up
latency is unacceptable (real-time inference, embedded NCE nodes).

Output: .lrnpu binary — NPU machine code for a specific NCE generation.
"""

from __future__ import annotations
import io
import os
import struct
import subprocess
import tempfile
from typing import Optional

LRNPU_MAGIC   = b"LRNPU"
LRNPU_VERSION = (1, 0)


class AOTCompiler:
    """
    Invokes the LightRail offline compiler toolchain (lrc-aot) if installed,
    otherwise produces a stub binary for testing.
    """

    # Path to the offline compiler binary (installed by the LightRail SDK)
    LRC_AOT_PATH = os.environ.get("LRC_AOT_PATH", "/opt/lightrail/bin/lrc-aot")

    def __init__(self, hw_gen: int = 1):
        self.hw_gen = hw_gen
        self._toolchain_available = os.path.isfile(self.LRC_AOT_PATH)

    def compile(self, lrbs_bytes: bytes, output_path: Optional[str] = None) -> bytes:
        """
        Compile .lrbs bytecode to NPU machine code.

        Parameters
        ----------
        lrbs_bytes  : The .lrbs bytecode blob.
        output_path : If given, write the .lrnpu binary to this path.

        Returns
        -------
        NPU binary bytes.
        """
        if self._toolchain_available:
            npu_bytes = self._run_toolchain(lrbs_bytes)
        else:
            npu_bytes = self._stub_compile(lrbs_bytes)

        if output_path:
            with open(output_path, "wb") as f:
                f.write(npu_bytes)

        return npu_bytes

    def _run_toolchain(self, lrbs_bytes: bytes) -> bytes:
        with tempfile.NamedTemporaryFile(suffix=".lrbs", delete=False) as tmp_in:
            tmp_in.write(lrbs_bytes)
            tmp_in_path = tmp_in.name

        tmp_out_path = tmp_in_path.replace(".lrbs", ".lrnpu")
        try:
            result = subprocess.run(
                [self.LRC_AOT_PATH, "--hw-gen", str(self.hw_gen),
                 "-o", tmp_out_path, tmp_in_path],
                capture_output=True, timeout=120,
            )
            if result.returncode != 0:
                raise RuntimeError(
                    f"lrc-aot failed: {result.stderr.decode()}"
                )
            with open(tmp_out_path, "rb") as f:
                return f.read()
        finally:
            for p in (tmp_in_path, tmp_out_path):
                try:
                    os.unlink(p)
                except FileNotFoundError:
                    pass

    def _stub_compile(self, lrbs_bytes: bytes) -> bytes:
        """Produce a well-formed stub .lrnpu for testing without hardware."""
        buf = io.BytesIO()
        buf.write(LRNPU_MAGIC)
        buf.write(struct.pack(">BB", *LRNPU_VERSION))
        buf.write(struct.pack(">H", self.hw_gen))
        buf.write(struct.pack(">I", len(lrbs_bytes)))
        # In production this would be the translated NCE instruction stream.
        # For now embed the .lrbs verbatim as a passthrough.
        buf.write(lrbs_bytes)
        return buf.getvalue()
