"""
Stage 5a: LightRail Tile Bytecode Generation (.lrbs)

Serialises the DataflowGraph (post Stage 4) into a portable, versioned
binary bytecode that acts as the LightRail virtual ISA.

File format (.lrbs — LightRail Bytecode Segment):
  ┌─────────────────────────────────────────────────────────────┐
  │  Magic    : b"LRBS"       (4 bytes)                         │
  │  Version  : uint16        (major.minor packed)              │
  │  Flags    : uint16        (ternary|analog|debug bits)        │
  │  NumCh    : uint32        number of WDM channels            │
  │  NumLayers: uint8         number of optical layers          │
  │  Reserved : 3 bytes                                         │
  │  ChannelTable[NumCh]:                                       │
  │    channel_id  : uint16                                     │
  │    layer_id    : uint8                                       │
  │    wavelength  : float32  (nm)                              │
  │    num_ops     : uint32                                      │
  │    ops_offset  : uint64   (byte offset into ops section)    │
  │  OpsSection:                                                 │
  │    For each channel: packed op stream                       │
  └─────────────────────────────────────────────────────────────┘

Each op is encoded as:
  opcode  : uint8
  n_ops   : uint8  (number of operand vids)
  operands: uint32 * n_ops
  n_attrs : uint8
  attrs   : key=value pairs (length-prefixed UTF-8 strings)
"""

from __future__ import annotations
import struct
import io
from typing import Any, Dict, List

from ..frontend.ir import OpKind, ScalarKind
from ..dataflow.wavelength_mapper import DataflowGraph, WDMChannel
from ..frontend.ir import Op


# Magic header
LRBS_MAGIC   = b"LRBS"
LRBS_VERSION = (1, 0)   # major=1, minor=0

# Flags bitfield
FLAG_TERNARY = 0x0001
FLAG_ANALOG  = 0x0002
FLAG_DEBUG   = 0x0004

# Opcode table (uint8)
_OPCODE: Dict[OpKind, int] = {
    OpKind.NOP:        0x00,
    OpKind.ADD:        0x01,
    OpKind.SUB:        0x02,
    OpKind.MUL:        0x03,
    OpKind.DIV:        0x04,
    OpKind.FMA:        0x05,
    OpKind.DOT:        0x06,
    OpKind.LOAD:       0x10,
    OpKind.STORE:      0x11,
    OpKind.DMA:        0x12,
    OpKind.BRANCH:     0x20,
    OpKind.RETURN:     0x21,
    OpKind.WDM_SEND:   0x30,
    OpKind.WDM_RECV:   0x31,
    OpKind.ALLREDUCE:  0x32,
    OpKind.TERNARY_OP: 0x40,
    OpKind.ANALOG_OP:  0x41,
    OpKind.CONSTANT:   0x50,
    OpKind.CAST:       0x51,
    OpKind.RESHAPE:    0x52,
}


def _pack_string(s: str) -> bytes:
    enc = s.encode("utf-8")
    return struct.pack(">H", len(enc)) + enc


def _pack_attrs(attrs: Dict[str, Any]) -> bytes:
    buf = io.BytesIO()
    buf.write(struct.pack("B", min(len(attrs), 255)))
    for k, v in list(attrs.items())[:255]:
        buf.write(_pack_string(str(k)))
        buf.write(_pack_string(str(v)))
    return buf.getvalue()


def _pack_op(op: Op) -> bytes:
    opcode = _OPCODE.get(op.kind, 0x00)
    operand_vids = [v.vid for v in op.operands][:255]
    buf = io.BytesIO()
    buf.write(struct.pack("B", opcode))
    result_vid = op.result.vid if op.result else 0
    buf.write(struct.pack(">I", result_vid))
    buf.write(struct.pack("B", len(operand_vids)))
    for vid in operand_vids:
        buf.write(struct.pack(">I", vid))
    buf.write(_pack_attrs(op.attrs))
    return buf.getvalue()


class BytecodeGenerator:
    """Serialises a DataflowGraph into .lrbs bytes."""

    def __init__(self, options):
        self._options = options

    def emit(self, graph: DataflowGraph) -> bytes:
        flags = 0
        if self._options.enable_ternary:
            flags |= FLAG_TERNARY
        if self._options.enable_analog:
            flags |= FLAG_ANALOG
        if self._options.debug:
            flags |= FLAG_DEBUG

        # Encode all channels' op streams first
        channel_streams: List[bytes] = []
        for ch in graph.channels:
            stream = b"".join(_pack_op(op) for op in ch.ops)
            channel_streams.append(stream)

        # Build channel table (each entry = 15 bytes + variable)
        # We do two passes: first compute offsets, then write header
        header_size = (
            4   # magic
            + 2 # version
            + 2 # flags
            + 4 # num_channels
            + 1 # num_layers
            + 3 # reserved
        )
        CHANNEL_ENTRY_SIZE = 2 + 1 + 4 + 4 + 8   # id, layer, wavelength, num_ops, offset

        ops_section_start = header_size + len(graph.channels) * CHANNEL_ENTRY_SIZE

        buf = io.BytesIO()
        # Magic + version
        buf.write(LRBS_MAGIC)
        buf.write(struct.pack(">BB", *LRBS_VERSION))
        buf.write(struct.pack(">H", flags))
        buf.write(struct.pack(">I", len(graph.channels)))
        buf.write(struct.pack("B", graph.num_layers))
        buf.write(b"\x00\x00\x00")  # reserved

        # Channel table
        offset = 0
        for ch, stream in zip(graph.channels, channel_streams):
            buf.write(struct.pack(">H", ch.channel_id))
            buf.write(struct.pack("B", ch.layer_id))
            buf.write(struct.pack(">f", ch.wavelength_nm))
            buf.write(struct.pack(">I", len(ch.ops)))
            buf.write(struct.pack(">Q", ops_section_start + offset))
            offset += len(stream)

        # Ops section
        for stream in channel_streams:
            buf.write(stream)

        return buf.getvalue()
