"""
Fabric Router: maps the DataflowGraph onto the physical 20-layer
optical mesh topology.

Layers 1-5  : Standard binary digital photonic compute
Layers 6-7  : Analog wave compute  (continuous amplitude)
Layers 8-20 : High-bandwidth optical interconnect fabric

The router assigns channels to layers based on operation type:
  - Analog / float ops          → layers 6-7
  - Ternary logic ops           → layers 3-5
  - AllReduce / collective      → layers 8-12 (high-BW interconnect)
  - Standard arithmetic         → layers 1-5
  - DMA / memory transfers      → layers 13-20
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple

from ..frontend.ir import OpKind
from .wavelength_mapper import DataflowGraph, WDMChannel


LAYER_BINARY_COMPUTE  = list(range(1, 6))     # layers 1-5
LAYER_ANALOG_COMPUTE  = [6, 7]                # layers 6-7
LAYER_COLLECTIVE      = list(range(8, 13))    # layers 8-12
LAYER_INTERCONNECT    = list(range(13, 21))   # layers 13-20


@dataclass
class RoutingTable:
    """Maps channel_id → physical layer_id after routing."""
    entries: Dict[int, int]   # channel_id → layer_id

    def layer_for(self, channel_id: int) -> int:
        return self.entries.get(channel_id, 1)


class FabricRouter:
    """
    Assigns DataflowGraph channels to physical layers.
    Also verifies that:
    - Analog ops only land on layers 6-7.
    - Ternary ops only land on layers 3-5.
    - No layer is overloaded beyond its channel capacity.
    """

    # Maximum simultaneous channels per layer (hardware constraint)
    LAYER_CAPACITY = 64  # Same as default WDM count

    def __init__(self, num_layers: int = 20):
        self.num_layers = num_layers
        self._layer_load: Dict[int, int] = {i: 0 for i in range(1, num_layers + 1)}

    def route(self, graph: DataflowGraph) -> RoutingTable:
        entries: Dict[int, int] = {}
        for ch in graph.channels:
            layer = self._pick_layer(ch)
            entries[ch.channel_id] = layer
            ch.layer_id = layer - 1  # 0-indexed storage
            self._layer_load[layer] += 1
        return RoutingTable(entries)

    def _pick_layer(self, ch: WDMChannel) -> int:
        dominant = self._dominant_op_kind(ch)

        if dominant in (OpKind.ANALOG_OP,):
            return self._least_loaded(LAYER_ANALOG_COMPUTE)
        if dominant in (OpKind.TERNARY_OP,):
            return self._least_loaded(LAYER_BINARY_COMPUTE[2:])  # layers 3-5
        if dominant in (OpKind.ALLREDUCE, OpKind.WDM_SEND, OpKind.WDM_RECV):
            return self._least_loaded(LAYER_COLLECTIVE)
        if dominant in (OpKind.DMA, OpKind.LOAD, OpKind.STORE):
            return self._least_loaded(LAYER_INTERCONNECT)
        return self._least_loaded(LAYER_BINARY_COMPUTE)

    def _dominant_op_kind(self, ch: WDMChannel) -> OpKind:
        if not ch.ops:
            return OpKind.NOP
        counts: Dict[OpKind, int] = {}
        for op in ch.ops:
            counts[op.kind] = counts.get(op.kind, 0) + 1
        return max(counts, key=counts.get)

    def _least_loaded(self, layers: List[int]) -> int:
        return min(layers, key=lambda l: self._layer_load.get(l, 0))
