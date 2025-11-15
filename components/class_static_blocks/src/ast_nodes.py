"""
AST node definitions for static blocks.

Implements FR-ES24-B-011: Static initialization blocks AST representation.
"""

from dataclasses import dataclass
from typing import List
from components.parser.src.ast_nodes import Statement, SourceLocation


@dataclass
class StaticBlock(Statement):
    """
    Static initialization block AST node.

    Represents static { ... } blocks inside class bodies.

    Attributes:
        body: List of statements in the static block
        location: Source location of the static block

    Example:
        class C {
            static {
                console.log('initialized');
            }
        }

    The static block is executed once when the class is defined,
    after all static fields are initialized.
    """

    body: List[Statement]
    location: SourceLocation

    def __post_init__(self):
        """Validate static block structure."""
        if not isinstance(self.body, list):
            raise TypeError(f"Static block body must be list, got {type(self.body)}")

        # Validate all body elements are statements
        for stmt in self.body:
            if not isinstance(stmt, Statement):
                raise TypeError(
                    f"Static block body must contain statements, "
                    f"got {type(stmt)}"
                )


# Extension to ClassDeclaration to include static_blocks field
# This is conceptual - actual ClassDeclaration modification happens in parser
class ClassDeclarationExtension:
    """
    Extension to ClassDeclaration to include static blocks.

    This adds the static_blocks field to ClassDeclaration:
        static_blocks: List[StaticBlock]

    The parser will include this field when parsing class bodies.
    """
    pass
