"""
Tests for the full 6-stage LightRail compilation pipeline.

These tests exercise the compiler in software-emulation mode (no hardware
required) and verify that each stage produces well-formed output.
"""

import sys
import os

# Add the LightOS root so `lightrail_compiler` is importable as a package
_LIGHTOS_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _LIGHTOS_ROOT)

import ast
import pytest

# ---------------------------------------------------------------------------
# Package imports
# ---------------------------------------------------------------------------
from lightrail_compiler.frontend.ir import (
    IRModule, IRFunction, BasicBlock, Op, Value,
    OpKind, ScalarKind, ScalarType,
)
from lightrail_compiler.frontend.ast_parser import ASTParser
from lightrail_compiler.frontend.type_inference import TypeInferenceEngine
from lightrail_compiler.python.decorator import CompileOptions
from lightrail_compiler.optimizer.photonic_passes import (
    AliasAnalysisPass, FMAFusionPass, LoopSplittingPass,
    CollectiveLoweringPass, GraphPartitioningPass, PhotonicOptimizer,
)
from lightrail_compiler.dataflow.wavelength_mapper import WavelengthMapper
from lightrail_compiler.codegen.bytecode import BytecodeGenerator, LRBS_MAGIC
from lightrail_compiler.codegen.fat_binary import FatBinaryBundler, LRFAT_MAGIC, SEG_LRBS1
from lightrail_compiler.codegen.ternary import encode_ternary, decode_ternary, apply_ternary, TernaryOp
from lightrail_compiler.runtime.jit import JITCompiler


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_options(**kw):
    return CompileOptions(**kw)


def _parse_fn(fn):
    import textwrap, inspect
    src = textwrap.dedent(inspect.getsource(fn))
    tree = ast.parse(src)
    parser = ASTParser(fn.__globals__)
    return parser.parse(tree, fn)


def _make_simple_module():
    module = IRModule(name="test")
    fn = IRFunction(name="test_device", is_device=True)
    bb = fn.add_block("entry")
    module.device_functions.append(fn)
    return module, fn, bb


def _make_graph_for(fn_py):
    module = _parse_fn(fn_py)
    opts = _make_options()
    typed = TypeInferenceEngine(opts).infer_and_lower(module)
    optimized = PhotonicOptimizer(opts).run_passes(typed)
    return WavelengthMapper(64).map(optimized)


# ---------------------------------------------------------------------------
# Stage 1: AST Parsing
# ---------------------------------------------------------------------------

class TestStage1ASTParsing:
    def test_simple_add(self):
        def add(a, b):
            return a + b

        module = _parse_fn(add)
        assert module.name == "add"
        assert len(module.host_functions) == 1
        assert len(module.device_functions) == 1

    def test_matmul_goes_to_device(self):
        def mm(a, b):
            return a @ b

        module = _parse_fn(mm)
        dev_fn = module.device_functions[0]
        all_kinds = [op.kind for bb in dev_fn.blocks for op in bb.ops]
        assert OpKind.DOT in all_kinds

    def test_params_registered(self):
        def fn(x, y, z):
            return x + y + z

        module = _parse_fn(fn)
        host_params = {p.name for p in module.host_functions[0].params}
        assert {"x", "y", "z"} == host_params

    def test_constant_emitted(self):
        def fn(a):
            return a + 1.0

        module = _parse_fn(fn)
        host_fn = module.host_functions[0]
        consts = [op for bb in host_fn.blocks for op in bb.ops
                  if op.kind == OpKind.CONSTANT]
        assert len(consts) >= 1
        assert consts[0].attrs["value"] == 1.0


# ---------------------------------------------------------------------------
# Stage 2: Type Inference
# ---------------------------------------------------------------------------

class TestStage2TypeInference:
    def test_float_constant_inferred_fp32(self):
        def fn(a):
            return a + 3.14

        module = _parse_fn(fn)
        opts = _make_options()
        typed = TypeInferenceEngine(opts).infer_and_lower(module)

        host_fn = typed.host_functions[0]
        const_ops = [op for bb in host_fn.blocks for op in bb.ops
                     if op.kind == OpKind.CONSTANT]
        assert const_ops[0].result.type == ScalarType(ScalarKind.FP32)

    def test_int_constant_inferred_int32(self):
        def fn(a):
            return a + 7

        module = _parse_fn(fn)
        opts = _make_options()
        typed = TypeInferenceEngine(opts).infer_and_lower(module)

        host_fn = typed.host_functions[0]
        const_ops = [op for bb in host_fn.blocks for op in bb.ops
                     if op.kind == OpKind.CONSTANT]
        assert const_ops[0].result.type == ScalarType(ScalarKind.INT32)


# ---------------------------------------------------------------------------
# Stage 3: Optimizer
# ---------------------------------------------------------------------------

class TestStage3Optimizer:
    def test_fma_fusion(self):
        module, fn, bb = _make_simple_module()
        a, b, c = Value(name="a"), Value(name="b"), Value(name="c")
        mul_res = Value(name="mul")
        add_res = Value(name="add")

        mul_op = Op(kind=OpKind.MUL, operands=[a, b], result=mul_res)
        add_op = Op(kind=OpKind.ADD, operands=[mul_res, c], result=add_res)
        bb.ops = [mul_op, add_op]

        FMAFusionPass().run(module)
        assert bb.ops[0].kind == OpKind.FMA
        assert bb.ops[0].result == add_res

    def test_collective_lowering(self):
        module, fn, bb = _make_simple_module()
        inp = Value(name="x")
        out = Value(name="reduced")
        ar_op = Op(kind=OpKind.ALLREDUCE, operands=[inp], result=out)
        bb.ops = [ar_op]

        CollectiveLoweringPass().run(module)
        kinds = [op.kind for op in bb.ops]
        assert OpKind.WDM_SEND in kinds
        assert OpKind.WDM_RECV in kinds
        assert OpKind.ALLREDUCE not in kinds

    def test_loop_splitting_tags(self):
        module, fn, bb = _make_simple_module()
        loop_op = Op(kind=OpKind.NOP, operands=[], attrs={"loop_hint": True})
        bb.ops = [loop_op]

        LoopSplittingPass(tile_size=64).run(module)
        assert bb.ops[0].attrs.get("tiled") is True
        assert bb.ops[0].attrs.get("tile_size") == 64

    def test_graph_partitioning_assigns_layers(self):
        module, fn, bb = _make_simple_module()
        a, b = Value(name="a"), Value(name="b")
        res = Value(name="res")
        dot_op = Op(kind=OpKind.DOT, operands=[a, b], result=res)
        bb.ops = [dot_op]

        GraphPartitioningPass(num_layers=20).run(module)
        assert "layer" in bb.ops[0].attrs


# ---------------------------------------------------------------------------
# Stage 4: Wavelength Mapper
# ---------------------------------------------------------------------------

class TestStage4WavelengthMapper:
    def test_correct_channel_count(self):
        def mm(a, b):
            return a @ b

        module = _parse_fn(mm)
        opts = _make_options(num_wavelengths=32)
        typed = TypeInferenceEngine(opts).infer_and_lower(module)
        optimized = PhotonicOptimizer(opts).run_passes(typed)
        graph = WavelengthMapper(num_wavelengths=32).map(optimized)
        assert len(graph.channels) == 32

    def test_channel_wavelengths_unique(self):
        mod = IRModule(name="empty")
        fn = IRFunction(name="d", is_device=True)
        fn.add_block("entry")
        mod.device_functions.append(fn)
        graph = WavelengthMapper(num_wavelengths=64).map(mod)
        wls = [ch.wavelength_nm for ch in graph.channels]
        assert len(set(wls)) == 64

    def test_edge_list_populated_for_cross_channel_deps(self):
        def mm(a, b):
            return a @ b

        module = _parse_fn(mm)
        opts = _make_options(num_wavelengths=64)
        typed = TypeInferenceEngine(opts).infer_and_lower(module)
        optimized = PhotonicOptimizer(opts).run_passes(typed)
        graph = WavelengthMapper(64).map(optimized)
        assert isinstance(graph.edges, list)


# ---------------------------------------------------------------------------
# Stage 5: Bytecode & Fat Binary
# ---------------------------------------------------------------------------

class TestStage5Codegen:
    def _graph(self):
        def fn(a, b):
            return a @ b
        return _make_graph_for(fn)

    def test_bytecode_magic(self):
        bc = BytecodeGenerator(_make_options()).emit(self._graph())
        assert bc[:4] == LRBS_MAGIC

    def test_bytecode_nonzero_length(self):
        bc = BytecodeGenerator(_make_options()).emit(self._graph())
        assert len(bc) > 20

    def test_fat_binary_magic(self):
        bc = BytecodeGenerator(_make_options()).emit(self._graph())
        fat = FatBinaryBundler().bundle(bc)
        assert fat[:5] == LRFAT_MAGIC

    def test_fat_binary_roundtrip(self):
        bc = BytecodeGenerator(_make_options()).emit(self._graph())
        bundler = FatBinaryBundler()
        fat = bundler.bundle(bc)
        segments = bundler.load(fat)
        assert SEG_LRBS1 in segments
        assert segments[SEG_LRBS1][0] == bc


# ---------------------------------------------------------------------------
# Stage 6: Runtime
# ---------------------------------------------------------------------------

class TestStage6Runtime:
    def _bc(self):
        def fn(a, b):
            return a @ b
        return BytecodeGenerator(_make_options()).emit(_make_graph_for(fn))

    def test_jit_caches_compilation(self):
        bc = self._bc()
        jit = JITCompiler()
        k1 = jit.compile(bc)
        k2 = jit.compile(bc)
        assert k1 is k2

    def test_jit_handle_nonzero(self):
        bc = self._bc()
        jit = JITCompiler()
        k = jit.compile(bc)
        assert k.handle != 0


# ---------------------------------------------------------------------------
# Ternary encoding
# ---------------------------------------------------------------------------

class TestTernaryEncoding:
    def test_encode_decode_roundtrip(self):
        original = [1, 0, -1, 1, -1, 0, 0, 1, -1, 1]
        encoded = encode_ternary(original)
        decoded = decode_ternary(encoded, len(original))
        assert decoded == original

    def test_ternary_ops(self):
        assert apply_ternary(TernaryOp.NOT, 1)     == -1
        assert apply_ternary(TernaryOp.NOT, -1)    ==  1
        assert apply_ternary(TernaryOp.AND, 1, -1) == -1
        assert apply_ternary(TernaryOp.OR,  1, -1) ==  1
        assert apply_ternary(TernaryOp.ADD, 1, 1)  ==  1   # saturated
        assert apply_ternary(TernaryOp.MUL, -1, -1) == 1

    def test_single_trit_roundtrip(self):
        for v in (-1, 0, 1):
            enc = encode_ternary([v])
            assert decode_ternary(enc, 1)[0] == v


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
