"""
LightRail High-Level Intermediate Representation (IR)

SSA-like IR where all variables are uniquified and operations are typed
but still abstract (hardware-independent). Mirrors MLIR value semantics.
"""

from __future__ import annotations
import enum
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

class ScalarKind(enum.Enum):
    INT8    = "int8"
    INT16   = "int16"
    INT32   = "int32"
    INT64   = "int64"
    FP8     = "fp8"       # 8-bit float
    FP16    = "fp16"      # IEEE half
    BF16    = "bf16"      # BFloat16
    ABFP16  = "abfp16"    # LightRail adaptive BFP16
    FP32    = "fp32"
    FP64    = "fp64"
    TERNARY = "ternary"   # {-1, 0, +1} — LightRail native
    ANALOG  = "analog"    # Continuous amplitude (layers 6-7)
    BOOL    = "bool"


@dataclass
class TensorType:
    element: ScalarKind
    shape: Tuple[int, ...]
    layout: str = "row_major"  # or "col_major", "tiled"

    def __repr__(self):
        return f"Tensor<{self.element.value}{list(self.shape)}>"


@dataclass
class ScalarType:
    kind: ScalarKind

    def __repr__(self):
        return self.kind.value


IRType = TensorType | ScalarType


# ---------------------------------------------------------------------------
# Values (SSA)
# ---------------------------------------------------------------------------

_value_counter = 0


def _fresh_id() -> int:
    global _value_counter
    _value_counter += 1
    return _value_counter


@dataclass
class Value:
    """An SSA value — produced by exactly one operation."""
    vid: int = field(default_factory=_fresh_id)
    type: Optional[IRType] = None
    name: str = ""          # Optional human-readable hint

    def __repr__(self):
        hint = f"({self.name})" if self.name else ""
        t = f": {self.type}" if self.type else ""
        return f"%{self.vid}{hint}{t}"


# ---------------------------------------------------------------------------
# Operations
# ---------------------------------------------------------------------------

class OpKind(enum.Enum):
    # Arithmetic
    ADD         = "add"
    SUB         = "sub"
    MUL         = "mul"
    DIV         = "div"
    FMA         = "fma"         # Fused multiply-add (a*b+c)
    DOT         = "dot"         # Tensor contraction / matmul
    # Memory
    LOAD        = "load"
    STORE       = "store"
    DMA         = "dma"         # Direct SRAM-to-SRAM transfer
    # Control flow
    BRANCH      = "branch"
    RETURN      = "return"
    # Photonic-specific
    WDM_SEND    = "wdm_send"    # Emit value on wavelength channel
    WDM_RECV    = "wdm_recv"    # Receive value from wavelength channel
    ALLREDUCE   = "allreduce"   # Mapped to photonic collective
    TERNARY_OP  = "ternary_op"  # Ternary logic operation
    ANALOG_OP   = "analog_op"   # Analog wave compute
    # Meta
    CONSTANT    = "constant"
    CAST        = "cast"
    RESHAPE     = "reshape"
    NOP         = "nop"


@dataclass
class Op:
    """A single IR operation."""
    kind: OpKind
    operands: List[Value] = field(default_factory=list)
    result: Optional[Value] = None
    attrs: Dict[str, Any] = field(default_factory=dict)
    # Source location for error messages
    lineno: int = 0

    def __repr__(self):
        res = f"{self.result} = " if self.result else ""
        ops = ", ".join(str(v) for v in self.operands)
        attrs = f" [{', '.join(f'{k}={v}' for k, v in self.attrs.items())}]" if self.attrs else ""
        return f"{res}{self.kind.value}({ops}){attrs}"


# ---------------------------------------------------------------------------
# Blocks & Functions
# ---------------------------------------------------------------------------

@dataclass
class BasicBlock:
    label: str
    ops: List[Op] = field(default_factory=list)
    predecessors: List["BasicBlock"] = field(default_factory=list)
    successors: List["BasicBlock"] = field(default_factory=list)

    def append(self, op: Op):
        self.ops.append(op)

    def __repr__(self):
        lines = [f"{self.label}:"]
        lines += [f"  {op}" for op in self.ops]
        return "\n".join(lines)


@dataclass
class IRFunction:
    name: str
    params: List[Value] = field(default_factory=list)
    return_type: Optional[IRType] = None
    blocks: List[BasicBlock] = field(default_factory=list)
    # Categorization
    is_device: bool = True   # False = host (CPU) code
    # Attributes
    attrs: Dict[str, Any] = field(default_factory=dict)

    @property
    def entry_block(self) -> BasicBlock:
        return self.blocks[0]

    def add_block(self, label: str = "") -> BasicBlock:
        if not label:
            label = f"bb{len(self.blocks)}"
        bb = BasicBlock(label)
        self.blocks.append(bb)
        return bb

    def dump(self) -> str:
        params = ", ".join(str(p) for p in self.params)
        ret = f" -> {self.return_type}" if self.return_type else ""
        header = f"{'device' if self.is_device else 'host'} fn {self.name}({params}){ret}:"
        body = "\n".join(str(b) for b in self.blocks)
        return f"{header}\n{body}"


@dataclass
class IRModule:
    """Top-level container produced by Stage 1."""
    name: str
    host_functions: List[IRFunction] = field(default_factory=list)
    device_functions: List[IRFunction] = field(default_factory=list)
    global_constants: Dict[str, Any] = field(default_factory=dict)

    def dump(self) -> str:
        parts = [f"module {self.name}:"]
        for fn in self.host_functions + self.device_functions:
            parts.append(fn.dump())
        return "\n\n".join(parts)
