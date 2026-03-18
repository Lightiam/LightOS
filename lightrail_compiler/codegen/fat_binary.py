"""
Stage 5b: Fat Binary Bundler

Combines:
  - The host-side Python/C++ callable (pickled or symbol reference)
  - One or more .lrbs bytecode blobs (one per hardware generation)
into a single .lrfat file that the runtime can load and dispatch.

Fat Binary Layout (.lrfat):
  ┌──────────────────────────────────────────────┐
  │  Magic     : b"LRFAT"     5 bytes            │
  │  Version   : uint16                          │
  │  NumSegments: uint16                         │
  │  SegmentTable[NumSegments]:                  │
  │    type      : uint8  (0=host, 1=lrbs_v1,   │
  │                        2=lrbs_v2, ...)       │
  │    hw_gen    : uint16  target HW generation  │
  │    offset    : uint64                        │
  │    size      : uint64                        │
  │  Segments (contiguous blobs)                 │
  └──────────────────────────────────────────────┘
"""

from __future__ import annotations
import io
import pickle
import struct
from typing import Callable, List, Optional, Tuple

LRFAT_MAGIC   = b"LRFAT"
LRFAT_VERSION = (1, 0)

SEG_HOST  = 0   # Serialised Python callable (host fallback)
SEG_LRBS1 = 1   # .lrbs v1 (NCE gen 1)
SEG_LRBS2 = 2   # .lrbs v2 (NCE gen 2, reserved)


class FatBinaryBundler:
    """Assembles a .lrfat fat binary from bytecode blobs and host code."""

    def bundle(
        self,
        bytecode: bytes,
        host_fn: Optional[Callable] = None,
        extra_blobs: Optional[List[Tuple[int, int, bytes]]] = None,
    ) -> bytes:
        """
        Parameters
        ----------
        bytecode  : .lrbs bytes for NCE gen 1
        host_fn   : Optional Python callable (CPU fallback)
        extra_blobs : [(seg_type, hw_gen, blob_bytes), ...] for future gens
        """
        segments: List[Tuple[int, int, bytes]] = []

        # Host segment
        if host_fn is not None:
            try:
                host_bytes = pickle.dumps(host_fn)
            except Exception:
                host_bytes = b""
            segments.append((SEG_HOST, 0, host_bytes))

        # Primary .lrbs segment
        segments.append((SEG_LRBS1, 1, bytecode))

        # Extra blobs
        if extra_blobs:
            segments.extend(extra_blobs)

        # Compute layout
        header_size = (
            5   # magic
            + 2 # version
            + 2 # num_segments
        )
        SEG_ENTRY = 1 + 2 + 8 + 8   # type, hw_gen, offset, size

        data_start = header_size + len(segments) * SEG_ENTRY

        buf = io.BytesIO()
        buf.write(LRFAT_MAGIC)
        buf.write(struct.pack(">BB", *LRFAT_VERSION))
        buf.write(struct.pack(">H", len(segments)))

        # Write segment table
        offset = 0
        for seg_type, hw_gen, blob in segments:
            buf.write(struct.pack("B", seg_type))
            buf.write(struct.pack(">H", hw_gen))
            buf.write(struct.pack(">Q", data_start + offset))
            buf.write(struct.pack(">Q", len(blob)))
            offset += len(blob)

        # Write segment data
        for _, _, blob in segments:
            buf.write(blob)

        return buf.getvalue()

    def load(self, fat_bytes: bytes) -> dict:
        """Parse a .lrfat blob and return a dict of {seg_type: blob}."""
        buf = io.BytesIO(fat_bytes)
        magic = buf.read(5)
        assert magic == LRFAT_MAGIC, f"Bad magic: {magic}"
        major, minor = struct.unpack(">BB", buf.read(2))
        (num_segs,) = struct.unpack(">H", buf.read(2))

        entries = []
        for _ in range(num_segs):
            (seg_type,) = struct.unpack("B", buf.read(1))
            (hw_gen,) = struct.unpack(">H", buf.read(2))
            (offset,) = struct.unpack(">Q", buf.read(8))
            (size,) = struct.unpack(">Q", buf.read(8))
            entries.append((seg_type, hw_gen, offset, size))

        result = {}
        raw = fat_bytes
        for seg_type, hw_gen, offset, size in entries:
            result.setdefault(seg_type, []).append(raw[offset : offset + size])

        return result
