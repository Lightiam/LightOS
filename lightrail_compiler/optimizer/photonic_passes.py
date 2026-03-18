"""
Stage 3: Photonic-Aware Optimization Passes

Runs a sequence of optimization passes over the typed IR:
  1. Alias Analysis       — determine which memory regions may alias
  2. Loop Splitting       — split loops for better tile utilization
  3. FMA Fusion           — fuse (a*b)+c into single FMA ops
  4. Graph Partitioning   — minimize cross-layer communication
  5. Collective Lowering  — map allreduce → photonic collective primitives
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from ..frontend.ir import (
    BasicBlock, IRFunction, IRModule, Op, OpKind, ScalarKind,
    ScalarType, TensorType, Value,
)


# ---------------------------------------------------------------------------
# Pass base class
# ---------------------------------------------------------------------------

class OptimizationPass:
    name: str = "base"

    def run(self, module: IRModule) -> IRModule:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Pass 1: Alias Analysis
# ---------------------------------------------------------------------------

@dataclass
class AliasSet:
    """Group of Values that may refer to the same memory location."""
    members: Set[int] = field(default_factory=set)   # Value.vid


class AliasAnalysisPass(OptimizationPass):
    """
    Conservative pointer alias analysis.
    Any two values produced by LOAD from the same base tensor are
    considered may-alias. Values produced by different constants never alias.
    """
    name = "alias_analysis"

    def run(self, module: IRModule) -> IRModule:
        for fn in module.device_functions:
            self._analyse_function(fn)
        return module

    def _analyse_function(self, fn: IRFunction):
        alias_map: Dict[int, AliasSet] = {}
        for block in fn.blocks:
            for op in block.ops:
                if op.kind == OpKind.LOAD and op.result:
                    base_vid = op.operands[0].vid if op.operands else -1
                    # Find or create alias set for this base
                    found = False
                    for aset in alias_map.values():
                        if base_vid in aset.members:
                            aset.members.add(op.result.vid)
                            alias_map[op.result.vid] = aset
                            found = True
                            break
                    if not found:
                        aset = AliasSet({base_vid, op.result.vid} if op.result else {base_vid})
                        alias_map[op.result.vid] = aset
        fn.attrs["alias_sets"] = alias_map


# ---------------------------------------------------------------------------
# Pass 2: Loop Splitting
# ---------------------------------------------------------------------------

class LoopSplittingPass(OptimizationPass):
    """
    Splits loops with trip counts > tile_size into outer/inner loops
    so each inner iteration fits into a single photonic tile execution.
    Default tile_size matches the 64-wavelength WDM channel count.
    """
    name = "loop_splitting"

    def __init__(self, tile_size: int = 64):
        self.tile_size = tile_size

    def run(self, module: IRModule) -> IRModule:
        for fn in module.device_functions:
            fn.attrs["loop_tile_size"] = self.tile_size
            self._split_loops(fn)
        return module

    def _split_loops(self, fn: IRFunction):
        for block in fn.blocks:
            new_ops: List[Op] = []
            for op in block.ops:
                if op.kind == OpKind.NOP and op.attrs.get("loop_hint"):
                    # Tag the loop for tiling; the codegen will emit
                    # the actual prologue/epilogue.
                    op.attrs["tiled"] = True
                    op.attrs["tile_size"] = self.tile_size
                new_ops.append(op)
            block.ops = new_ops


# ---------------------------------------------------------------------------
# Pass 3: FMA Fusion
# ---------------------------------------------------------------------------

class FMAFusionPass(OptimizationPass):
    """
    Finds (a*b)+c and (a*b)-c patterns in a basic block and replaces
    them with a single FMA operation.
    """
    name = "fma_fusion"

    def run(self, module: IRModule) -> IRModule:
        for fn in module.device_functions:
            for block in fn.blocks:
                self._fuse_block(block)
        return module

    def _fuse_block(self, block: BasicBlock):
        # Build a map: result.vid → op
        result_map: Dict[int, Op] = {}
        for op in block.ops:
            if op.result:
                result_map[op.result.vid] = op

        # First pass: collect which MUL ops will be absorbed into FMAs
        absorbed_ops: Set[int] = set()   # id(op) of MUL ops that get fused
        fma_replacements: Dict[int, Op] = {}  # id(add_op) → fma_op

        for op in block.ops:
            if op.kind in (OpKind.ADD, OpKind.SUB) and len(op.operands) == 2:
                for j, operand in enumerate(op.operands):
                    mul_op = result_map.get(operand.vid)
                    if mul_op is not None and mul_op.kind == OpKind.MUL:
                        other_operand = op.operands[1 - j]
                        fma_op = Op(
                            kind=OpKind.FMA,
                            operands=[mul_op.operands[0], mul_op.operands[1], other_operand],
                            result=op.result,
                            attrs={"negate_add": op.kind == OpKind.SUB},
                            lineno=op.lineno,
                        )
                        absorbed_ops.add(id(mul_op))
                        fma_replacements[id(op)] = fma_op
                        break

        # Second pass: emit ops, skipping absorbed MULs and replaced ADD/SUBs
        new_ops: List[Op] = []
        for op in block.ops:
            if id(op) in absorbed_ops:
                continue
            replacement = fma_replacements.get(id(op))
            new_ops.append(replacement if replacement else op)

        block.ops = new_ops


# ---------------------------------------------------------------------------
# Pass 4: Graph Partitioning
# ---------------------------------------------------------------------------

class GraphPartitioningPass(OptimizationPass):
    """
    Partitions the device IR graph across the 20-layer optical fabric to
    minimize cross-layer communication.  Uses a greedy min-cut heuristic:
    ops with high data-volume edges are co-located on the same layer.
    """
    name = "graph_partitioning"

    def __init__(self, num_layers: int = 20):
        self.num_layers = num_layers

    def run(self, module: IRModule) -> IRModule:
        for fn in module.device_functions:
            self._partition(fn)
        return module

    def _partition(self, fn: IRFunction):
        # Build a simple use-def graph weight
        layer_assignment: Dict[int, int] = {}  # vid → layer_id
        layer_counter = 0

        for block in fn.blocks:
            for op in block.ops:
                if op.result:
                    # Heavy ops (matmul, allreduce) get their own layer group
                    if op.kind in (OpKind.DOT, OpKind.ALLREDUCE):
                        layer_assignment[op.result.vid] = layer_counter % self.num_layers
                        layer_counter += 1
                    else:
                        # Light ops follow their primary operand's layer
                        primary = op.operands[0].vid if op.operands else -1
                        layer_assignment[op.result.vid] = layer_assignment.get(
                            primary, layer_counter % self.num_layers
                        )
                    op.attrs["layer"] = layer_assignment[op.result.vid]

        fn.attrs["layer_assignment"] = layer_assignment


# ---------------------------------------------------------------------------
# Pass 5: Collective Lowering (AllReduce → Photonic WDM collective)
# ---------------------------------------------------------------------------

class CollectiveLoweringPass(OptimizationPass):
    """
    Intercepts AllReduce (and similar collective) operations and
    replaces them with explicit WDM_SEND/WDM_RECV pairs so the
    Fabric OS can map them to the 20-layer photonic topology directly.
    """
    name = "collective_lowering"

    def run(self, module: IRModule) -> IRModule:
        for fn in module.device_functions:
            for block in fn.blocks:
                self._lower_collectives(block)
        return module

    def _lower_collectives(self, block: BasicBlock):
        new_ops: List[Op] = []
        for op in block.ops:
            if op.kind == OpKind.ALLREDUCE:
                # Lower to: WDM_SEND on channel 0, WDM_RECV from all peers
                send_op = Op(
                    kind=OpKind.WDM_SEND,
                    operands=op.operands,
                    result=None,
                    attrs={"channel": 0, "collective": "allreduce"},
                    lineno=op.lineno,
                )
                recv_op = Op(
                    kind=OpKind.WDM_RECV,
                    operands=[],
                    result=op.result,
                    attrs={"channel": 0, "collective": "allreduce", "reduce_op": "sum"},
                    lineno=op.lineno,
                )
                new_ops.extend([send_op, recv_op])
            else:
                new_ops.append(op)
        block.ops = new_ops


# ---------------------------------------------------------------------------
# Composite optimizer
# ---------------------------------------------------------------------------

class PhotonicOptimizer:
    """Runs all Stage 3 passes in order."""

    def __init__(self, options):
        self._passes: List[OptimizationPass] = [
            AliasAnalysisPass(),
        ]
        if options.enable_loop_splitting:
            self._passes.append(LoopSplittingPass(tile_size=options.num_wavelengths))
        if options.enable_fma_fusion:
            self._passes.append(FMAFusionPass())
        self._passes.append(GraphPartitioningPass(num_layers=len(options.target_layers)))
        self._passes.append(CollectiveLoweringPass())

    def run_passes(self, module: IRModule) -> IRModule:
        for p in self._passes:
            module = p.run(module)
        return module
