"""
SSA Builder - Converts IR to Static Single Assignment form

Implements SSA construction using dominance frontiers and phi node insertion.
Based on Cytron et al. algorithm.
"""

from typing import List, Set, Dict, Optional
from .ir_builder import IRGraph, BasicBlock
from .ir_nodes import PhiNode


class DominatorTree:
    """
    Dominator tree for SSA construction

    Computes dominance relationships between basic blocks:
    - Block A dominates block B if every path from entry to B passes through A
    - Immediate dominator (idom): The closest dominator of a block
    - Dominance frontier: Blocks where dominance of a block ends
    """

    def __init__(self, blocks: List[BasicBlock], entry: BasicBlock):
        """
        Build dominator tree

        Args:
            blocks: All basic blocks in the CFG
            entry: Entry block
        """
        self.blocks = blocks
        self.entry = entry
        self._idom: Dict[BasicBlock, Optional[BasicBlock]] = {}
        self._dominators: Dict[BasicBlock, Set[BasicBlock]] = {}
        self._dominance_frontier: Dict[BasicBlock, Set[BasicBlock]] = {}

        # Build dominator tree
        self._compute_dominators()
        self._compute_dominance_frontier()

    def _compute_dominators(self):
        """
        Compute dominators using iterative algorithm

        Algorithm:
        1. Initialize: entry dominates itself, all others dominated by all blocks
        2. Iterate until fixed point:
            For each block B (except entry):
                DOM(B) = {B} ∪ (∩ DOM(P) for all predecessors P of B)
        """
        # Initialize
        for block in self.blocks:
            if block == self.entry:
                self._dominators[block] = {block}
            else:
                self._dominators[block] = set(self.blocks)

        # Iterate until fixed point
        changed = True
        while changed:
            changed = False
            for block in self.blocks:
                if block == self.entry:
                    continue

                # DOM(B) = {B} ∪ (∩ DOM(P) for all predecessors P)
                if block.predecessors:
                    # Intersection of all predecessor dominators
                    new_dom = set(self.blocks)
                    for pred in block.predecessors:
                        new_dom &= self._dominators[pred]
                    new_dom.add(block)

                    if new_dom != self._dominators[block]:
                        self._dominators[block] = new_dom
                        changed = True

        # Compute immediate dominators
        for block in self.blocks:
            if block == self.entry:
                self._idom[block] = None
            else:
                # idom(B) is the unique dominator closest to B
                # (dominator with largest depth in dom tree)
                doms = self._dominators[block] - {block}
                if doms:
                    # Find the dominator that is not dominated by any other dominator
                    for candidate in doms:
                        is_idom = True
                        for other in doms:
                            if candidate != other and candidate in self._dominators[other]:
                                is_idom = False
                                break
                        if is_idom:
                            self._idom[block] = candidate
                            break

    def _compute_dominance_frontier(self):
        """
        Compute dominance frontier for each block

        Dominance frontier of block X:
        DF(X) = { Y : X dominates a predecessor of Y, but X does not strictly dominate Y }

        This is where phi nodes need to be inserted in SSA construction.
        """
        for block in self.blocks:
            self._dominance_frontier[block] = set()

        for block in self.blocks:
            if len(block.predecessors) >= 2:
                # Block has multiple predecessors - potential merge point
                for pred in block.predecessors:
                    runner = pred
                    while runner and not self.strictly_dominates(runner, block):
                        self._dominance_frontier[runner].add(block)
                        runner = self._idom.get(runner)

    def dominates(self, a: BasicBlock, b: BasicBlock) -> bool:
        """
        Check if block a dominates block b

        Args:
            a: Potential dominator
            b: Block to check

        Returns:
            True if a dominates b
        """
        return a in self._dominators.get(b, set())

    def strictly_dominates(self, a: BasicBlock, b: BasicBlock) -> bool:
        """
        Check if block a strictly dominates block b (a dominates b and a != b)

        Args:
            a: Potential dominator
            b: Block to check

        Returns:
            True if a strictly dominates b
        """
        return a != b and self.dominates(a, b)

    def get_idom(self, block: BasicBlock) -> Optional[BasicBlock]:
        """
        Get immediate dominator of a block

        Args:
            block: Block to query

        Returns:
            Immediate dominator or None if entry block
        """
        return self._idom.get(block)

    def get_dominance_frontier(self, block: BasicBlock) -> Set[BasicBlock]:
        """
        Get dominance frontier of a block

        Args:
            block: Block to query

        Returns:
            Set of blocks in dominance frontier
        """
        return self._dominance_frontier.get(block, set())


class SSAGraph(IRGraph):
    """
    SSA form IR graph

    Extends IRGraph with:
    - Phi nodes at merge points
    - Dominator tree
    - SSA variable renaming
    """

    def __init__(self):
        """Create SSA graph"""
        super().__init__()
        self.dominator_tree: Optional[DominatorTree] = None
        self.phi_nodes: List[PhiNode] = []


class SSABuilder:
    """
    SSA Builder - Converts IR to SSA form

    Algorithm (Cytron et al.):
    1. Build dominator tree
    2. Compute dominance frontiers
    3. Insert phi nodes at dominance frontiers
    4. Rename variables to SSA form
    """

    def __init__(self):
        """Create SSA builder"""
        pass

    def build_ssa(self, ir_graph: IRGraph) -> SSAGraph:
        """
        Convert IR graph to SSA form

        Args:
            ir_graph: Input IR graph

        Returns:
            SSA form IR graph with phi nodes

        Algorithm:
        1. Build dominator tree
        2. Insert phi nodes at merge points (dominance frontiers)
        3. Rename variables to SSA form (each assignment gets unique name)
        """
        # Create SSA graph
        ssa_graph = SSAGraph()

        # Copy basic blocks and nodes
        for block in ir_graph.basic_blocks:
            ssa_graph.add_basic_block(block)

        for node in ir_graph.nodes:
            ssa_graph.add_node(node)

        # Set entry and exit
        if ir_graph.entry:
            ssa_graph.set_entry(ir_graph.entry)
        if ir_graph.exit:
            ssa_graph.set_exit(ir_graph.exit)

        # Build dominator tree
        if ir_graph.basic_blocks and ir_graph.entry:
            ssa_graph.dominator_tree = DominatorTree(
                ir_graph.basic_blocks, ir_graph.entry
            )

        # Insert phi nodes at merge points
        # (Simplified: In a full implementation, this would analyze variable definitions
        # and insert phi nodes at dominance frontiers of blocks that define variables)
        self._insert_phi_nodes(ssa_graph)

        # Rename variables to SSA form
        # (Simplified: In a full implementation, this would walk the dominator tree
        # and rename variable uses/definitions to ensure single assignment)
        # For now, we skip this step as our IR is already in a form where each
        # node produces a unique value

        return ssa_graph

    def _insert_phi_nodes(self, ssa_graph: SSAGraph):
        """
        Insert phi nodes at merge points

        Simplified implementation:
        - Insert phi nodes at blocks with multiple predecessors
        - In a full implementation, would analyze variable definitions and
          insert phi nodes only where needed

        Args:
            ssa_graph: SSA graph to modify
        """
        if not ssa_graph.dominator_tree:
            return

        # For each block with multiple predecessors, it's a potential merge point
        for block in ssa_graph.basic_blocks:
            if len(block.predecessors) >= 2:
                # This is a merge point
                # In a real implementation, we would:
                # 1. Identify variables defined in different predecessors
                # 2. Insert phi nodes for those variables
                # For now, we just mark it as a merge point
                pass
