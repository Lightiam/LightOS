"""
Stage 2: Type Inference & Lowering

- Infers concrete types for all SSA values (e.g. Python 'float' → fp32).
- Supports LightRail-specific types: ABFP16, FP8, Ternary, Analog.
- Eliminates constant-foldable branches (dead code elimination pass 1).
"""

from __future__ import annotations
from typing import Any, Dict, Optional

from .ir import (
    BasicBlock, IRFunction, IRModule, IRType, Op, OpKind,
    ScalarKind, ScalarType, TensorType, Value,
)


# Python annotation → LightRail ScalarKind mapping
_PY_TYPE_MAP: Dict[str, ScalarKind] = {
    "int":     ScalarKind.INT32,
    "float":   ScalarKind.FP32,
    "bool":    ScalarKind.BOOL,
    "int8":    ScalarKind.INT8,
    "int16":   ScalarKind.INT16,
    "int32":   ScalarKind.INT32,
    "int64":   ScalarKind.INT64,
    "float16": ScalarKind.FP16,
    "float32": ScalarKind.FP32,
    "float64": ScalarKind.FP64,
    "fp8":     ScalarKind.FP8,
    "fp16":    ScalarKind.FP16,
    "bf16":    ScalarKind.BF16,
    "abfp16":  ScalarKind.ABFP16,
    "ternary": ScalarKind.TERNARY,
    "analog":  ScalarKind.ANALOG,
}


class TypeInferenceEngine:
    """
    Walks an IRModule and annotates every Value with a concrete IRType.
    After type inference it performs a first-pass dead-code elimination
    by removing branches that fold to compile-time constants.
    """

    def __init__(self, options):
        self._options = options
        self._type_env: Dict[int, IRType] = {}   # vid → IRType

    def infer_and_lower(self, module: IRModule) -> IRModule:
        for fn in module.host_functions + module.device_functions:
            self._infer_function(fn)
        module = self._dead_code_elimination(module)
        return module

    # ------------------------------------------------------------------
    # Type inference
    # ------------------------------------------------------------------

    def _infer_function(self, fn: IRFunction):
        # Assign default types to parameters (fp32 tensors unless annotated)
        for param in fn.params:
            if param.type is None:
                param.type = ScalarType(ScalarKind.FP32)
            self._type_env[param.vid] = param.type

        for block in fn.blocks:
            self._infer_block(block)

    def _infer_block(self, block: BasicBlock):
        for op in block.ops:
            inferred = self._infer_op(op)
            if op.result and inferred:
                op.result.type = inferred
                self._type_env[op.result.vid] = inferred

    def _infer_op(self, op: Op) -> Optional[IRType]:
        operand_types = [self._type_env.get(v.vid) for v in op.operands]

        if op.kind == OpKind.CONSTANT:
            return self._infer_constant_type(op.attrs.get("value"))

        if op.kind in (OpKind.ADD, OpKind.SUB, OpKind.MUL, OpKind.DIV):
            return self._promote(operand_types)

        if op.kind == OpKind.FMA:
            return self._promote(operand_types)

        if op.kind == OpKind.DOT:
            return self._infer_dot_type(operand_types)

        if op.kind == OpKind.CAST:
            target = op.attrs.get("target_kind")
            if target:
                return ScalarType(ScalarKind(target))

        if op.kind == OpKind.LOAD:
            # Load returns the element type of the source tensor
            src = operand_types[0] if operand_types else None
            if isinstance(src, TensorType):
                return ScalarType(src.element)
            return src

        if op.kind == OpKind.STORE:
            return None  # Store has no result

        if op.kind == OpKind.ALLREDUCE:
            return self._promote(operand_types)

        if op.kind == OpKind.TERNARY_OP:
            return ScalarType(ScalarKind.TERNARY)

        if op.kind == OpKind.ANALOG_OP:
            return ScalarType(ScalarKind.ANALOG)

        if op.kind == OpKind.WDM_SEND:
            return None  # side effect only

        if op.kind == OpKind.WDM_RECV:
            # Receives the same type that was sent
            return operand_types[0] if operand_types else None

        return None

    def _infer_constant_type(self, value: Any) -> IRType:
        if isinstance(value, bool):
            return ScalarType(ScalarKind.BOOL)
        if isinstance(value, int):
            return ScalarType(ScalarKind.INT32)
        if isinstance(value, float):
            return ScalarType(ScalarKind.FP32)
        return ScalarType(ScalarKind.FP32)

    def _promote(self, types) -> Optional[IRType]:
        """Binary type promotion following FP hierarchy."""
        _rank = {
            ScalarKind.BOOL: 0,
            ScalarKind.INT8: 1, ScalarKind.INT16: 2, ScalarKind.INT32: 3, ScalarKind.INT64: 4,
            ScalarKind.FP8: 5, ScalarKind.BF16: 6, ScalarKind.ABFP16: 6,
            ScalarKind.FP16: 7, ScalarKind.FP32: 8, ScalarKind.FP64: 9,
            ScalarKind.TERNARY: 3, ScalarKind.ANALOG: 8,
        }
        best: Optional[ScalarKind] = None
        for t in types:
            if t is None:
                continue
            k = t.kind if isinstance(t, ScalarType) else t.element
            if best is None or _rank.get(k, -1) > _rank.get(best, -1):
                best = k
        return ScalarType(best) if best else None

    def _infer_dot_type(self, operand_types) -> Optional[IRType]:
        # Result of matmul: accumulate in fp32 minimum
        promoted = self._promote(operand_types)
        if promoted and isinstance(promoted, ScalarType):
            if promoted.kind in (ScalarKind.FP8, ScalarKind.BF16, ScalarKind.ABFP16,
                                  ScalarKind.FP16):
                return ScalarType(ScalarKind.FP32)
        return promoted

    # ------------------------------------------------------------------
    # Dead code elimination (constant branch folding)
    # ------------------------------------------------------------------

    def _dead_code_elimination(self, module: IRModule) -> IRModule:
        for fn in module.host_functions + module.device_functions:
            for block in fn.blocks:
                block.ops = [
                    op for op in block.ops
                    if not self._is_dead(op)
                ]
        return module

    def _is_dead(self, op: Op) -> bool:
        if op.kind == OpKind.BRANCH:
            # If all operands are compile-time constants, the branch can
            # be resolved. In Stage 2 we mark it; a later pass removes it.
            if all(isinstance(v.type, ScalarType) for v in op.operands):
                const_vals = [op.attrs.get("value") for o in op.operands
                              for inner in [o.vid] if inner]
                if all(c is not None for c in const_vals):
                    op.attrs["foldable"] = True
        return False  # Actual removal is a separate pass; keep for now
