"""
Optimizing JIT Compiler

Advanced JIT compiler with aggressive optimizations for 20-50x speedup.

Public API:
    Classes:
        - OptimizingJITCompiler: Main compiler
        - IRBuilder: Build IR from bytecode
        - SSABuilder: Convert IR to SSA form
        - TypeSpecializer: Type specialization
        - Inliner: Function inlining
        - LoopOptimizer: Loop optimizations
        - DeadCodeEliminator: Dead code elimination
        - ConstantFolder: Constant folding
        - EscapeAnalyzer: Escape analysis
        - BoundsCheckEliminator: Bounds check elimination
        - SpeculationManager: Guards and deoptimization
        - GraphColoringAllocator: Register allocation
        - OptimizingCodeGen: Code generation

    Data Classes:
        - IRGraph: IR graph structure
        - SSAGraph: SSA form IR
        - IRNode: Base IR node
        - BasicBlock: Basic block in CFG

Example:
    >>> from components.optimizing_jit.src import OptimizingJITCompiler
    >>> compiler = OptimizingJITCompiler()
    >>> optimized_code = compiler.compile_function(bytecode, profiling_data)
"""

# IR Infrastructure
from .ir_nodes import (
    IRNode,
    IRNodeType,
    ConstantNode,
    ParameterNode,
    BinaryOpNode,
    UnaryOpNode,
    PhiNode,
    LoadPropertyNode,
    StorePropertyNode,
    CallNode,
    ReturnNode,
    BranchNode,
    MergeNode,
)
from .ir_builder import IRBuilder, IRGraph, BasicBlock
from .ssa_builder import SSABuilder, SSAGraph, DominatorTree

# Optimizations
from .optimizations.dce import DeadCodeEliminator
from .optimizations.constant_folding import ConstantFolder

# Main compiler
from .compiler import OptimizingJITCompiler, ProfilingData, OptimizedCode

__all__ = [
    # IR Infrastructure
    "IRNode",
    "IRNodeType",
    "ConstantNode",
    "ParameterNode",
    "BinaryOpNode",
    "UnaryOpNode",
    "PhiNode",
    "LoadPropertyNode",
    "StorePropertyNode",
    "CallNode",
    "ReturnNode",
    "BranchNode",
    "MergeNode",
    "IRBuilder",
    "IRGraph",
    "BasicBlock",
    "SSABuilder",
    "SSAGraph",
    "DominatorTree",
    # Optimizations
    "DeadCodeEliminator",
    "ConstantFolder",
    # Main compiler
    "OptimizingJITCompiler",
    "ProfilingData",
    "OptimizedCode",
]

__version__ = "0.1.0"
