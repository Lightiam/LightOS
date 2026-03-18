"""
Stage 4: Dataflow & Wavelength Mapping

Replaces the CUDA thread/block/grid hierarchy with LightRail's
Wavelength Division Multiplexing (WDM) model:

  * Each of the N wavelength channels acts as an independent virtual
    processor executing deterministically in parallel.
  * No warp scheduling, no idle waiting — tasks are bound to specific
    optical channels at compile time.
  * Data moves as messages across the optical mesh; the compiler
    inserts WDM_SEND/WDM_RECV pairs at every cross-channel boundary.

Key difference from CUDA:
  CUDA:  grid → blocks → warps → threads  (dynamic scheduling, lots of idle)
  LightRail: wavelength channels  (compile-time static, deterministic)
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from ..frontend.ir import (
    BasicBlock, IRFunction, IRModule, Op, OpKind, Value,
)


# ---------------------------------------------------------------------------
# WDM Channel model
# ---------------------------------------------------------------------------

@dataclass
class WDMChannel:
    """
    Represents one wavelength (virtual processor) in the optical fabric.

    channel_id : 0 .. num_wavelengths-1
    layer_id   : which of the 20 optical fabric layers this channel runs on
    ops        : ordered list of IR ops bound to this channel
    """
    channel_id: int
    layer_id: int
    ops: List[Op] = field(default_factory=list)

    # Compile-time reservation of wavelength nm range (illustrative)
    @property
    def wavelength_nm(self) -> float:
        """O-band center + 0.8 nm spacing (ITU-T G.694.2 CWDM-like)."""
        return 1271.0 + self.channel_id * 0.8


@dataclass
class DataflowGraph:
    """
    The result of Stage 4: a set of WDM channels, each owning a slice
    of the device IR, with explicit send/receive edges between channels.
    """
    channels: List[WDMChannel]
    num_layers: int
    # Edge list: (src_channel, dst_channel, value_vid)
    edges: List[Tuple[int, int, int]] = field(default_factory=list)
    # Original IRModule (host side unchanged)
    source_module: Optional[IRModule] = None

    def dump(self) -> str:
        lines = [f"DataflowGraph ({len(self.channels)} channels, {self.num_layers} layers)"]
        for ch in self.channels:
            lines.append(
                f"  λ{ch.channel_id:03d} ({ch.wavelength_nm:.1f}nm) "
                f"[layer {ch.layer_id}]: {len(ch.ops)} ops"
            )
        lines.append(f"  Edges: {len(self.edges)}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Mapper
# ---------------------------------------------------------------------------

class WavelengthMapper:
    """
    Distributes device IR ops across WDM channels.

    Strategy
    --------
    1. Topologically sort ops inside each device function.
    2. Assign ops to channels in a round-robin fashion, grouping
       data-dependent ops onto the same channel to minimise cross-channel
       WDM_SEND/RECV traffic.
    3. Insert WDM_SEND/RECV pairs wherever an op on channel A produces
       a value consumed by an op on channel B.
    4. Pin heavy collective ops (DOT, ALLREDUCE) to dedicated channels
       to avoid resource contention.
    """

    def __init__(self, num_wavelengths: int = 64, target_layers: Tuple[int, ...] = tuple(range(1, 21))):
        self.num_wavelengths = num_wavelengths
        self.target_layers = list(target_layers)
        self.num_layers = len(self.target_layers)

    def map(self, module: IRModule) -> DataflowGraph:
        channels = [
            WDMChannel(
                channel_id=i,
                layer_id=self.target_layers[i % self.num_layers] - 1,
            )
            for i in range(self.num_wavelengths)
        ]
        edges: List[Tuple[int, int, int]] = []

        for fn in module.device_functions:
            self._map_function(fn, channels, edges)

        graph = DataflowGraph(
            channels=channels,
            num_layers=self.num_layers,
            edges=edges,
            source_module=module,
        )
        return graph

    def _map_function(
        self,
        fn: IRFunction,
        channels: List[WDMChannel],
        edges: List[Tuple[int, int, int]],
    ):
        # vid → channel_id of the producing op
        producer_channel: Dict[int, int] = {}
        # Parameters are "on" channel 0 by convention
        for param in fn.params:
            producer_channel[param.vid] = 0

        channel_cursor = 0  # Round-robin cursor

        for block in fn.blocks:
            for op in block.ops:
                # Heavy ops get their own dedicated channel
                if op.kind in (OpKind.DOT, OpKind.WDM_SEND, OpKind.WDM_RECV):
                    target_ch = self._dedicated_channel(op, channel_cursor, channels)
                else:
                    # Prefer the channel of the first operand (data locality)
                    target_ch = channel_cursor % self.num_wavelengths
                    if op.operands:
                        primary_vid = op.operands[0].vid
                        target_ch = producer_channel.get(primary_vid, target_ch)

                # Insert WDM_SEND/RECV for cross-channel dependencies
                for operand in op.operands:
                    src_ch = producer_channel.get(operand.vid, 0)
                    if src_ch != target_ch:
                        # Need to relay the value across channels
                        send_op = Op(
                            kind=OpKind.WDM_SEND,
                            operands=[operand],
                            result=None,
                            attrs={
                                "src_channel": src_ch,
                                "dst_channel": target_ch,
                                "wavelength_nm": channels[src_ch].wavelength_nm,
                            },
                        )
                        recv_op = Op(
                            kind=OpKind.WDM_RECV,
                            operands=[],
                            result=Value(name=f"relay_{operand.vid}"),
                            attrs={
                                "src_channel": src_ch,
                                "dst_channel": target_ch,
                                "wavelength_nm": channels[src_ch].wavelength_nm,
                            },
                        )
                        channels[src_ch].ops.append(send_op)
                        channels[target_ch].ops.append(recv_op)
                        edges.append((src_ch, target_ch, operand.vid))
                        # Redirect operand to the received value
                        producer_channel[recv_op.result.vid] = target_ch

                channels[target_ch].ops.append(op)
                if op.result:
                    producer_channel[op.result.vid] = target_ch

                # Advance round-robin cursor for next non-local op
                channel_cursor = (channel_cursor + 1) % self.num_wavelengths

    def _dedicated_channel(
        self, op: Op, cursor: int, channels: List[WDMChannel]
    ) -> int:
        """
        Reserve a channel from the upper half of the wavelength range
        for heavy collective/compute ops to avoid blocking light data ops.
        """
        heavy_base = self.num_wavelengths // 2
        layer_hint = op.attrs.get("layer", 0)
        return (heavy_base + layer_hint) % self.num_wavelengths
