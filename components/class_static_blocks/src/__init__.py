"""
Static initialization blocks for ES2022 classes.

This component implements static initialization blocks (static { ... })
for JavaScript classes, including:
- Syntax parsing
- Execution order semantics
- This binding to class constructor
- Private field access

Public API exports match contract specification.
"""

from components.class_static_blocks.src.ast_nodes import (
    StaticBlock,
    ClassDeclarationExtension,
)
from components.class_static_blocks.src.parser_extensions import (
    parse_class_static_block,
    is_static_block,
    StaticBlockParser,
)
from components.class_static_blocks.src.static_block_executor import (
    StaticBlockExecutor,
)
from components.class_static_blocks.src.static_block_scope import (
    StaticBlockScope,
    StaticBlockDescriptor,
)

__all__ = [
    # AST Nodes
    'StaticBlock',
    'ClassDeclarationExtension',

    # Parser
    'parse_class_static_block',
    'is_static_block',
    'StaticBlockParser',

    # Executor
    'StaticBlockExecutor',

    # Scope
    'StaticBlockScope',
    'StaticBlockDescriptor',
]

__version__ = '0.1.0'
