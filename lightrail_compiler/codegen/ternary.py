"""
Ternary & Analog Native Encoding

LightRail supports three compute paradigms:
  1. Binary  : Standard {0, 1} digital logic  (layers 1-5)
  2. Ternary : {-1, 0, +1} balanced ternary   (layers 3-5)
  3. Analog  : Continuous amplitude wave compute (layers 6-7)

This module provides:
  - encode_ternary()   : pack int8 values into ternary trit streams
  - decode_ternary()   : unpack trit streams back to int8
  - TernaryOp          : named ternary logic operations
  - AnalogEncoding     : wave amplitude encoding helpers
"""

from __future__ import annotations
import enum
import struct
from typing import List, Sequence


# ---------------------------------------------------------------------------
# Ternary trit packing
# Two trits per byte using balanced base-3: trit ∈ {0,1,2} ↔ {-1,0,+1}
# Encoding: byte = (t0 + 1) * 3 + (t1 + 1), up to 2 trits per byte.
# For larger arrays we use 5 trits per byte via trit5 packing.
# ---------------------------------------------------------------------------

TRIT_NEG  = -1
TRIT_ZERO =  0
TRIT_POS  = +1


def _trit_to_sym(t: int) -> int:
    """Map {-1,0,+1} to {0,1,2} for storage."""
    return t + 1


def _sym_to_trit(s: int) -> int:
    """Map {0,1,2} back to {-1,0,+1}."""
    return s - 1


def encode_ternary(values: Sequence[int]) -> bytes:
    """
    Encode a sequence of ternary values ({-1,0,+1}) into a compact byte stream.
    Packs 5 trits into each byte (3^5 = 243 < 256).
    """
    result = []
    chunk: List[int] = []
    for v in values:
        assert v in (-1, 0, 1), f"Not a ternary value: {v}"
        chunk.append(_trit_to_sym(v))
        if len(chunk) == 5:
            packed = 0
            for s in chunk:
                packed = packed * 3 + s
            result.append(packed)
            chunk = []
    if chunk:
        # Pad with ZERO trits
        while len(chunk) < 5:
            chunk.append(1)  # TRIT_ZERO symbol = 1
        packed = 0
        for s in chunk:
            packed = packed * 3 + s
        result.append(packed)
    return bytes(result)


def decode_ternary(data: bytes, length: int) -> List[int]:
    """Decode a ternary byte stream back to a list of {-1,0,+1} values."""
    trits: List[int] = []
    for byte in data:
        chunk = []
        b = byte
        for _ in range(5):
            chunk.append(_sym_to_trit(b % 3))
            b //= 3
        trits.extend(reversed(chunk))
    return trits[:length]


# ---------------------------------------------------------------------------
# Ternary logic operations
# ---------------------------------------------------------------------------

class TernaryOp(enum.Enum):
    """Standard balanced-ternary logic operations."""
    AND  = "tand"   # min(a, b)
    OR   = "tor"    # max(a, b)
    NOT  = "tnot"   # negate: {-1,0,+1} → {+1,0,-1}
    ADD  = "tadd"   # saturating add in {-1,0,+1}
    MUL  = "tmul"   # product, clamped to {-1,0,+1}


def ternary_and(a: int, b: int) -> int:
    return min(a, b)


def ternary_or(a: int, b: int) -> int:
    return max(a, b)


def ternary_not(a: int) -> int:
    return -a


def ternary_add(a: int, b: int) -> int:
    return max(-1, min(1, a + b))


def ternary_mul(a: int, b: int) -> int:
    return max(-1, min(1, a * b))


_TERNARY_DISPATCH = {
    TernaryOp.AND: ternary_and,
    TernaryOp.OR:  ternary_or,
    TernaryOp.ADD: ternary_add,
    TernaryOp.MUL: ternary_mul,
}


def apply_ternary(op: TernaryOp, a: int, b: int = 0) -> int:
    if op == TernaryOp.NOT:
        return ternary_not(a)
    return _TERNARY_DISPATCH[op](a, b)


# ---------------------------------------------------------------------------
# Analog wave encoding (layers 6-7)
# ---------------------------------------------------------------------------

class AnalogEncoding:
    """
    Encode floating-point values as optical wave amplitudes for
    transmission on the analog compute layers (6 and 7).

    Amplitude range: [0.0, 1.0] maps to [V_low, V_high] on the modulator.
    Signed values use an offset encoding: 0.5 = zero, ±0.5 = ±full-scale.
    """

    V_LOW  = 0.0
    V_HIGH = 1.0

    @classmethod
    def encode_float(cls, value: float, min_val: float = -1.0, max_val: float = 1.0) -> float:
        """Normalise ``value`` from [min_val, max_val] to [0, 1] amplitude."""
        if max_val == min_val:
            return 0.5
        return (value - min_val) / (max_val - min_val)

    @classmethod
    def decode_float(cls, amplitude: float, min_val: float = -1.0, max_val: float = 1.0) -> float:
        """Recover float from normalised amplitude."""
        return amplitude * (max_val - min_val) + min_val

    @classmethod
    def encode_vector(cls, values: Sequence[float], min_val: float = -1.0, max_val: float = 1.0) -> List[float]:
        return [cls.encode_float(v, min_val, max_val) for v in values]

    @classmethod
    def decode_vector(cls, amplitudes: Sequence[float], min_val: float = -1.0, max_val: float = 1.0) -> List[float]:
        return [cls.decode_float(a, min_val, max_val) for a in amplitudes]
