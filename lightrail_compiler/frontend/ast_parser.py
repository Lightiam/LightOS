"""
Stage 1: AST Parsing & High-Level IR Construction

Walks the Python AST of a decorated function, identifies Host vs Device
operations, and emits an SSA-form IRModule.
"""

from __future__ import annotations
import ast
import textwrap
from typing import Any, Callable, Dict, List, Optional

from .ir import (
    BasicBlock, IRFunction, IRModule, Op, OpKind, ScalarKind,
    ScalarType, TensorType, Value, _fresh_id,
)


# Sentinel attributes that mark an expression as device-side
_DEVICE_CALLS = {
    "matmul", "dot", "einsum", "conv2d", "relu", "softmax",
    "allreduce", "reduce", "scatter", "gather",
}

_NUMPY_LIKE_MODULES = {"np", "numpy", "torch", "jax"}


class _IRBuilder:
    """Convenience wrapper for constructing IR inside a function."""

    def __init__(self, fn: IRFunction):
        self.fn = fn
        self.current_block = fn.entry_block if fn.blocks else fn.add_block("entry")
        self._symbol_table: Dict[str, Value] = {}

    def emit(self, kind: OpKind, operands: List[Value], attrs: Dict = None, lineno: int = 0) -> Value:
        result = Value(name=f"v{_fresh_id()}")
        op = Op(kind=kind, operands=operands, result=result, attrs=attrs or {}, lineno=lineno)
        self.current_block.append(op)
        return result

    def bind(self, name: str, value: Value):
        self._symbol_table[name] = value

    def lookup(self, name: str) -> Optional[Value]:
        return self._symbol_table.get(name)


class ASTParser(ast.NodeVisitor):
    """
    Transforms a Python AST into an IRModule.

    Host/Device split heuristic:
    - Calls to tensor operations (matmul, conv, reduce, etc.) → Device.
    - All other Python control flow / IO → Host.
    """

    def __init__(self, globals_dict: Dict[str, Any]):
        self._globals = globals_dict
        self._module: Optional[IRModule] = None
        self._current_builder: Optional[_IRBuilder] = None
        self._host_builder: Optional[_IRBuilder] = None
        self._device_builder: Optional[_IRBuilder] = None

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def parse(self, tree: ast.Module, fn: Callable) -> IRModule:
        fn_name = fn.__name__
        self._module = IRModule(name=fn_name)

        # Create one host function and one device function skeleton
        host_fn = IRFunction(name=f"{fn_name}_host", is_device=False)
        host_fn.add_block("entry")
        device_fn = IRFunction(name=f"{fn_name}_device", is_device=True)
        device_fn.add_block("entry")

        self._module.host_functions.append(host_fn)
        self._module.device_functions.append(device_fn)

        self._host_builder = _IRBuilder(host_fn)
        self._device_builder = _IRBuilder(device_fn)

        # Walk the top-level FunctionDef
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == fn.__name__:
                self._visit_function(node)
                break

        return self._module

    # ------------------------------------------------------------------
    # Visitors
    # ------------------------------------------------------------------

    def _visit_function(self, node: ast.FunctionDef):
        # Register parameters as Values in both builders
        for arg in node.args.args:
            val = Value(name=arg.arg)
            self._host_builder.bind(arg.arg, val)
            self._device_builder.bind(arg.arg, val)
            self._host_builder.fn.params.append(val)
            self._device_builder.fn.params.append(val)

        for stmt in node.body:
            self._visit_stmt(stmt)

    def _visit_stmt(self, node: ast.stmt):
        if isinstance(node, ast.Assign):
            self._visit_assign(node)
        elif isinstance(node, ast.Return):
            self._visit_return(node)
        elif isinstance(node, ast.For):
            self._visit_for(node)
        elif isinstance(node, ast.If):
            self._visit_if(node)
        elif isinstance(node, ast.Expr):
            self._visit_expr_stmt(node)
        # Other statement kinds are emitted as NOP on the host side
        else:
            self._host_builder.emit(OpKind.NOP, [], lineno=getattr(node, "lineno", 0))

    def _visit_assign(self, node: ast.Assign):
        rhs_val = self._visit_expr(node.value)
        for target in node.targets:
            if isinstance(target, ast.Name):
                builder = self._pick_builder(node.value)
                builder.bind(target.id, rhs_val)

    def _visit_return(self, node: ast.Return):
        if node.value:
            val = self._visit_expr(node.value)
            builder = self._pick_builder(node.value)
            builder.emit(OpKind.RETURN, [val], lineno=node.lineno)
        else:
            self._host_builder.emit(OpKind.RETURN, [], lineno=node.lineno)

    def _visit_for(self, node: ast.For):
        # Emit a loop header NOP; actual loop splitting happens in Stage 3
        self._device_builder.emit(
            OpKind.NOP, [], attrs={"loop_hint": True}, lineno=node.lineno
        )
        for stmt in node.body:
            self._visit_stmt(stmt)

    def _visit_if(self, node: ast.If):
        cond = self._visit_expr(node.test)
        self._host_builder.emit(
            OpKind.BRANCH, [cond],
            attrs={"then_label": "if_true", "else_label": "if_false"},
            lineno=node.lineno,
        )
        for stmt in node.body:
            self._visit_stmt(stmt)
        for stmt in node.orelse:
            self._visit_stmt(stmt)

    def _visit_expr_stmt(self, node: ast.Expr):
        self._visit_expr(node.value)

    def _visit_expr(self, node: ast.expr) -> Value:
        if isinstance(node, ast.BinOp):
            return self._visit_binop(node)
        elif isinstance(node, ast.Call):
            return self._visit_call(node)
        elif isinstance(node, ast.Name):
            return self._resolve_name(node)
        elif isinstance(node, ast.Constant):
            return self._emit_constant(node)
        elif isinstance(node, ast.Attribute):
            return self._visit_attribute(node)
        else:
            # Unknown expression — emit a placeholder
            return self._host_builder.emit(OpKind.NOP, [], lineno=getattr(node, "lineno", 0))

    def _visit_binop(self, node: ast.BinOp) -> Value:
        left = self._visit_expr(node.left)
        right = self._visit_expr(node.right)
        op_map = {
            ast.Add: OpKind.ADD,
            ast.Sub: OpKind.SUB,
            ast.Mult: OpKind.MUL,
            ast.Div: OpKind.DIV,
            ast.MatMult: OpKind.DOT,  # Python @ operator
        }
        kind = op_map.get(type(node.op), OpKind.NOP)
        builder = self._device_builder if kind == OpKind.DOT else self._pick_builder(node)
        return builder.emit(kind, [left, right], lineno=node.lineno)

    def _visit_call(self, node: ast.Call) -> Value:
        fn_name = self._extract_call_name(node)
        args = [self._visit_expr(a) for a in node.args]

        if fn_name in _DEVICE_CALLS:
            return self._device_builder.emit(
                OpKind.DOT if "matmul" in fn_name or "dot" in fn_name else OpKind.NOP,
                args,
                attrs={"call": fn_name},
                lineno=node.lineno,
            )
        # Check for allreduce
        if "allreduce" in fn_name or "reduce" in fn_name:
            return self._device_builder.emit(
                OpKind.ALLREDUCE, args, attrs={"call": fn_name}, lineno=node.lineno
            )
        # Generic host call
        return self._host_builder.emit(
            OpKind.NOP, args, attrs={"call": fn_name}, lineno=node.lineno
        )

    def _visit_attribute(self, node: ast.Attribute) -> Value:
        # e.g., torch.matmul, np.dot
        base = self._extract_module_name(node.value)
        return self._host_builder.emit(
            OpKind.NOP, [], attrs={"attr": f"{base}.{node.attr}"}
        )

    def _resolve_name(self, node: ast.Name) -> Value:
        # Try device builder first, then host
        val = self._device_builder.lookup(node.id) or self._host_builder.lookup(node.id)
        if val:
            return val
        # Introduce a new SSA value for an external name
        v = Value(name=node.id)
        self._host_builder.bind(node.id, v)
        return v

    def _emit_constant(self, node: ast.Constant) -> Value:
        v = Value(name=f"const_{node.value}")
        self._host_builder.fn.entry_block.append(
            Op(OpKind.CONSTANT, [], result=v, attrs={"value": node.value}, lineno=node.lineno)
        )
        return v

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _pick_builder(self, node: ast.AST) -> _IRBuilder:
        """Route an expression to host or device builder based on content."""
        src = ast.dump(node)
        for call in _DEVICE_CALLS:
            if call in src:
                return self._device_builder
        return self._host_builder

    @staticmethod
    def _extract_call_name(node: ast.Call) -> str:
        if isinstance(node.func, ast.Name):
            return node.func.id
        if isinstance(node.func, ast.Attribute):
            return node.func.attr
        return ""

    @staticmethod
    def _extract_module_name(node: ast.expr) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return f"{ASTParser._extract_module_name(node.value)}.{node.attr}"
        return "<unknown>"
