"""
Graph Coloring Register Allocator

Advanced register allocation using graph coloring (Chaitin's algorithm).

Algorithm:
1. Build interference graph (nodes = SSA values, edges = live simultaneously)
2. Simplify: Remove nodes with degree < K (K = # registers)
3. Spill: If no node with degree < K, choose spill candidate
4. Color: Assign registers (colors) to nodes
5. Rewrite: Generate spill/reload code
"""

from typing import Dict, List, Set, Optional, Tuple
from ..ssa_builder import SSAGraph
from ..ir_nodes import IRNode, IRNodeType


class InterferenceGraph:
    """
    Interference graph for register allocation

    Nodes = SSA values
    Edges = values that are live simultaneously (interfere)

    If two values are live at the same time, they need different registers.
    """

    def __init__(self):
        """Create empty interference graph"""
        self.nodes: Set[IRNode] = set()
        self.edges: Set[Tuple[IRNode, IRNode]] = set()

    def add_node(self, node: IRNode):
        """
        Add node to graph

        Args:
            node: SSA value
        """
        self.nodes.add(node)

    def add_edge(self, v1: IRNode, v2: IRNode):
        """
        Add interference edge (v1 and v2 are live simultaneously)

        Args:
            v1: First value
            v2: Second value
        """
        if v1 == v2:
            return  # No self-edges

        # Add both directions (undirected graph)
        self.edges.add((v1, v2))
        self.edges.add((v2, v1))

    def has_edge(self, v1: IRNode, v2: IRNode) -> bool:
        """
        Check if edge exists

        Args:
            v1: First value
            v2: Second value

        Returns:
            True if v1 and v2 interfere
        """
        return (v1, v2) in self.edges

    def degree(self, node: IRNode) -> int:
        """
        Get degree of node (number of neighbors)

        Args:
            node: Node to query

        Returns:
            Number of neighbors
        """
        return len([v2 for (v1, v2) in self.edges if v1 == node])

    def neighbors(self, node: IRNode) -> Set[IRNode]:
        """
        Get all neighbors of node

        Args:
            node: Node to query

        Returns:
            Set of neighboring nodes
        """
        return {v2 for (v1, v2) in self.edges if v1 == node}

    def remove_node(self, node: IRNode):
        """
        Remove node from graph

        Args:
            node: Node to remove
        """
        self.nodes.discard(node)
        # Remove all edges involving this node
        self.edges = {
            (v1, v2) for (v1, v2) in self.edges
            if v1 != node and v2 != node
        }


class RegisterAllocation:
    """
    Register allocation result

    Maps SSA values to physical registers or stack slots.
    """

    def __init__(self, num_registers: int):
        """
        Create register allocation

        Args:
            num_registers: Number of available registers
        """
        self.num_registers = num_registers
        self._allocation: Dict[IRNode, int] = {}  # node -> register (-1 = spilled)
        self._spilled: Set[IRNode] = set()

    def assign(self, value: IRNode, register: int):
        """
        Assign register to value

        Args:
            value: SSA value
            register: Register number (0 to num_registers-1)
        """
        if 0 <= register < self.num_registers:
            self._allocation[value] = register

    def spill(self, value: IRNode):
        """
        Mark value as spilled to stack

        Args:
            value: SSA value to spill
        """
        self._spilled.add(value)
        self._allocation[value] = -1  # -1 indicates spilled

    def get_register(self, value: IRNode) -> Optional[int]:
        """
        Get register assigned to value

        Args:
            value: SSA value

        Returns:
            Register number, or None if not allocated
        """
        return self._allocation.get(value)

    def is_spilled(self, value: IRNode) -> bool:
        """
        Check if value is spilled

        Args:
            value: SSA value

        Returns:
            True if spilled to stack
        """
        return value in self._spilled

    def get_spilled(self) -> Set[IRNode]:
        """
        Get all spilled values

        Returns:
            Set of spilled values
        """
        return self._spilled.copy()


class GraphColoringAllocator:
    """
    Graph Coloring Register Allocator

    Uses Chaitin's algorithm for register allocation:
    1. Build interference graph
    2. Simplify (remove low-degree nodes)
    3. Spill (when no low-degree nodes)
    4. Color (assign registers)
    5. Actual spill (generate spill code if needed)
    """

    def __init__(self, num_registers: int = 14):
        """
        Create graph coloring allocator

        Args:
            num_registers: Number of available registers (default: 14 for x64)
        """
        self.num_registers = num_registers

    def allocate(self, ir_graph: SSAGraph) -> RegisterAllocation:
        """
        Allocate registers for IR graph

        Args:
            ir_graph: SSA IR graph

        Returns:
            Register allocation
        """
        # Build interference graph
        interference = self.build_interference_graph(ir_graph)

        # Simplify and build stack
        stack = self.simplify(interference, self.num_registers)

        # Color the graph
        coloring = self.color(stack, interference, self.num_registers)

        # Create allocation result
        allocation = RegisterAllocation(self.num_registers)

        for node, color in coloring.items():
            if color == -1:
                allocation.spill(node)
            else:
                allocation.assign(node, color)

        return allocation

    def build_interference_graph(self, ir_graph: SSAGraph) -> InterferenceGraph:
        """
        Build interference graph from IR

        Two values interfere if they are live at the same point.

        Args:
            ir_graph: SSA IR graph

        Returns:
            Interference graph
        """
        interference = InterferenceGraph()

        # Add all SSA values as nodes
        for node in ir_graph.nodes:
            if self._needs_register(node):
                interference.add_node(node)

        # Compute live ranges
        live_ranges = self.compute_live_ranges(ir_graph)

        # Add interference edges
        # Two values interfere if their live ranges overlap
        nodes_list = list(interference.nodes)
        for i, node1 in enumerate(nodes_list):
            for node2 in nodes_list[i+1:]:
                if self._ranges_overlap(
                    live_ranges.get(node1, (0, 0)),
                    live_ranges.get(node2, (0, 0))
                ):
                    interference.add_edge(node1, node2)

        return interference

    def compute_live_ranges(self, ir_graph: SSAGraph) -> Dict[IRNode, Tuple[int, int]]:
        """
        Compute live ranges for all values

        Live range = (first_use, last_use) positions

        Args:
            ir_graph: IR graph

        Returns:
            Map from node to (start, end) positions
        """
        live_ranges = {}

        # Assign position to each node
        position = {}
        pos = 0
        for block in ir_graph.basic_blocks:
            for node in block.nodes:
                position[node] = pos
                pos += 1

        # Compute live range for each value
        for node in ir_graph.nodes:
            if not self._needs_register(node):
                continue

            # Live range starts at definition
            start = position.get(node, 0)

            # Live range ends at last use
            end = start
            for use in node.uses:
                use_pos = position.get(use, 0)
                end = max(end, use_pos)

            live_ranges[node] = (start, end)

        return live_ranges

    def _ranges_overlap(
        self,
        range1: Tuple[int, int],
        range2: Tuple[int, int]
    ) -> bool:
        """
        Check if two live ranges overlap

        Args:
            range1: (start, end) of first range
            range2: (start, end) of second range

        Returns:
            True if ranges overlap
        """
        start1, end1 = range1
        start2, end2 = range2

        # Ranges overlap if they intersect
        return not (end1 < start2 or end2 < start1)

    def _needs_register(self, node: IRNode) -> bool:
        """
        Check if node needs a register

        Args:
            node: IR node

        Returns:
            True if node needs register allocation
        """
        # These node types produce values that need registers
        needs_reg_types = {
            IRNodeType.PARAMETER,
            IRNodeType.BINARY_OP,
            IRNodeType.UNARY_OP,
            IRNodeType.LOAD_PROPERTY,
            IRNodeType.CALL,
            IRNodeType.PHI,
        }
        return node.node_type in needs_reg_types

    def simplify(
        self,
        graph: InterferenceGraph,
        num_colors: int
    ) -> List[IRNode]:
        """
        Simplify phase: Remove nodes with degree < K

        Args:
            graph: Interference graph (will be modified)
            num_colors: Number of colors (registers)

        Returns:
            Stack of removed nodes (for coloring phase)
        """
        stack = []

        while graph.nodes:
            # Find node with degree < K
            low_degree_node = None
            for node in graph.nodes:
                if graph.degree(node) < num_colors:
                    low_degree_node = node
                    break

            if low_degree_node:
                # Remove and push to stack
                stack.append(low_degree_node)
                graph.remove_node(low_degree_node)
            else:
                # No low-degree node: spill
                spill_candidate = self.choose_spill_candidate(graph)
                if spill_candidate:
                    stack.append(spill_candidate)
                    graph.remove_node(spill_candidate)
                else:
                    # No nodes left
                    break

        return stack

    def choose_spill_candidate(self, graph: InterferenceGraph) -> Optional[IRNode]:
        """
        Choose spill candidate using heuristic

        Heuristic: Spill node with highest degree (most neighbors)
        This frees up the most constraints.

        Args:
            graph: Interference graph

        Returns:
            Node to spill, or None if graph is empty
        """
        if not graph.nodes:
            return None

        # Choose node with highest degree
        best = None
        max_degree = -1

        for node in graph.nodes:
            degree = graph.degree(node)
            if degree > max_degree:
                best = node
                max_degree = degree

        return best

    def color(
        self,
        stack: List[IRNode],
        original_graph: InterferenceGraph,
        num_colors: int
    ) -> Dict[IRNode, int]:
        """
        Coloring phase: Assign registers to nodes

        Pop nodes from stack and assign colors (registers).

        Args:
            stack: Stack from simplify phase
            original_graph: Original interference graph (for neighbor info)
            num_colors: Number of colors (registers)

        Returns:
            Map from node to color (-1 = spilled)
        """
        coloring = {}

        # Rebuild graph to track neighbors
        graph = InterferenceGraph()
        for node in stack:
            graph.add_node(node)
        for (v1, v2) in original_graph.edges:
            if v1 in graph.nodes and v2 in graph.nodes:
                graph.add_edge(v1, v2)

        # Color nodes in reverse order
        for node in reversed(stack):
            # Get colors of neighbors
            neighbor_colors = set()
            for neighbor in graph.neighbors(node):
                if neighbor in coloring:
                    color = coloring[neighbor]
                    if color != -1:
                        neighbor_colors.add(color)

            # Find free color
            color = self._find_free_color(neighbor_colors, num_colors)

            if color is None:
                # No color available: spill
                coloring[node] = -1
            else:
                coloring[node] = color

        return coloring

    def _find_free_color(
        self,
        used_colors: Set[int],
        num_colors: int
    ) -> Optional[int]:
        """
        Find free color (register)

        Args:
            used_colors: Colors already used by neighbors
            num_colors: Total colors available

        Returns:
            Free color, or None if all used
        """
        for color in range(num_colors):
            if color not in used_colors:
                return color
        return None
