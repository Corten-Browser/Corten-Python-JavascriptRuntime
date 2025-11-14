"""JavaScript module representation."""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from components.module_system.src.module_status import ModuleStatus


@dataclass
class Module:
    """
    Represents a JavaScript module.

    Attributes:
        url: Absolute file path or URL to module
        source: Module source code
        ast: Parsed AST (populated during linking)
        bytecode: Compiled bytecode (populated during linking)
        namespace: Module namespace object (exported bindings)
        imports: List of import declarations (extracted from AST)
        exports: List of export declarations (extracted from AST)
        status: Current lifecycle status
        dependencies: Other modules this module depends on
        environment: Module's execution environment (locals)
        error: Error that occurred during linking/evaluation
    """
    url: str
    source: str
    ast: Optional[Any] = None
    bytecode: Optional[Any] = None
    namespace: Dict[str, Any] = field(default_factory=dict)
    imports: List[Any] = field(default_factory=list)
    exports: List[Any] = field(default_factory=list)
    status: ModuleStatus = ModuleStatus.UNLINKED
    dependencies: List['Module'] = field(default_factory=list)
    environment: Dict[str, Any] = field(default_factory=dict)
    error: Optional[Exception] = None

    def __repr__(self):
        return f"Module(url={self.url!r}, status={self.status.name})"
