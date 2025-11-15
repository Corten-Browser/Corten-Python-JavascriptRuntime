"""
Tests for IR node definitions

RED phase - These tests will fail until we implement IR nodes
"""

import pytest
from components.optimizing_jit.src.ir_nodes import (
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


class TestIRNodeType:
    """Test IR node type enumeration"""

    def test_ir_node_types_exist(self):
        """Should have all required IR node types"""
        # Given: IR node types
        # When: We check for required types
        # Then: All types should exist
        assert hasattr(IRNodeType, "CONSTANT")
        assert hasattr(IRNodeType, "PARAMETER")
        assert hasattr(IRNodeType, "BINARY_OP")
        assert hasattr(IRNodeType, "UNARY_OP")
        assert hasattr(IRNodeType, "PHI")
        assert hasattr(IRNodeType, "LOAD_PROPERTY")
        assert hasattr(IRNodeType, "STORE_PROPERTY")
        assert hasattr(IRNodeType, "CALL")
        assert hasattr(IRNodeType, "RETURN")
        assert hasattr(IRNodeType, "BRANCH")
        assert hasattr(IRNodeType, "MERGE")


class TestIRNode:
    """Test base IR node"""

    def test_create_ir_node(self):
        """Should create base IR node"""
        # Given: IR node type
        node_type = IRNodeType.CONSTANT

        # When: We create an IR node
        node = IRNode(node_type)

        # Then: Node should be created with correct type
        assert node.node_type == IRNodeType.CONSTANT
        assert node.inputs == []
        assert node.uses == []
        assert node.id is not None

    def test_ir_node_add_input(self):
        """Should add input to IR node"""
        # Given: Two IR nodes
        node1 = IRNode(IRNodeType.CONSTANT)
        node2 = IRNode(IRNodeType.BINARY_OP)

        # When: We add node1 as input to node2
        node2.add_input(node1)

        # Then: node1 should be in node2's inputs and node2 in node1's uses
        assert node1 in node2.inputs
        assert node2 in node1.uses

    def test_ir_node_remove_input(self):
        """Should remove input from IR node"""
        # Given: Two connected IR nodes
        node1 = IRNode(IRNodeType.CONSTANT)
        node2 = IRNode(IRNodeType.BINARY_OP)
        node2.add_input(node1)

        # When: We remove the input
        node2.remove_input(node1)

        # Then: Connection should be removed
        assert node1 not in node2.inputs
        assert node2 not in node1.uses


class TestConstantNode:
    """Test constant IR node"""

    def test_create_constant_node(self):
        """Should create constant node with value"""
        # Given: A constant value
        value = 42

        # When: We create a constant node
        node = ConstantNode(value)

        # Then: Node should have correct type and value
        assert node.node_type == IRNodeType.CONSTANT
        assert node.value == 42

    def test_constant_node_types(self):
        """Should support different constant types"""
        # Given: Different constant types
        # When: We create constant nodes
        int_node = ConstantNode(42)
        float_node = ConstantNode(3.14)
        str_node = ConstantNode("hello")
        bool_node = ConstantNode(True)

        # Then: All should be created correctly
        assert int_node.value == 42
        assert float_node.value == 3.14
        assert str_node.value == "hello"
        assert bool_node.value is True


class TestParameterNode:
    """Test parameter IR node"""

    def test_create_parameter_node(self):
        """Should create parameter node with index"""
        # Given: Parameter index
        index = 0

        # When: We create a parameter node
        node = ParameterNode(index)

        # Then: Node should have correct type and index
        assert node.node_type == IRNodeType.PARAMETER
        assert node.index == 0

    def test_multiple_parameters(self):
        """Should create multiple parameter nodes"""
        # Given: Multiple parameter indices
        # When: We create parameter nodes
        param0 = ParameterNode(0)
        param1 = ParameterNode(1)
        param2 = ParameterNode(2)

        # Then: Each should have correct index
        assert param0.index == 0
        assert param1.index == 1
        assert param2.index == 2


class TestBinaryOpNode:
    """Test binary operation IR node"""

    def test_create_binary_op_node(self):
        """Should create binary op node"""
        # Given: Operator and two operands
        left = ConstantNode(10)
        right = ConstantNode(20)
        op = "ADD"

        # When: We create a binary op node
        node = BinaryOpNode(op, left, right)

        # Then: Node should be created correctly
        assert node.node_type == IRNodeType.BINARY_OP
        assert node.op == "ADD"
        assert left in node.inputs
        assert right in node.inputs

    def test_binary_op_types(self):
        """Should support different binary operations"""
        # Given: Different operations
        a = ConstantNode(10)
        b = ConstantNode(5)

        # When: We create different binary ops
        add = BinaryOpNode("ADD", a, b)
        sub = BinaryOpNode("SUB", a, b)
        mul = BinaryOpNode("MUL", a, b)
        div = BinaryOpNode("DIV", a, b)

        # Then: Each should have correct operator
        assert add.op == "ADD"
        assert sub.op == "SUB"
        assert mul.op == "MUL"
        assert div.op == "DIV"


class TestPhiNode:
    """Test phi node for SSA merge points"""

    def test_create_phi_node(self):
        """Should create phi node"""
        # Given: Values from different control flow paths
        value1 = ConstantNode(10)
        value2 = ConstantNode(20)

        # When: We create a phi node
        phi = PhiNode([value1, value2])

        # Then: Phi should merge both values
        assert phi.node_type == IRNodeType.PHI
        assert value1 in phi.inputs
        assert value2 in phi.inputs

    def test_phi_node_multiple_inputs(self):
        """Should support phi with multiple inputs"""
        # Given: Multiple control flow paths
        v1 = ConstantNode(1)
        v2 = ConstantNode(2)
        v3 = ConstantNode(3)
        v4 = ConstantNode(4)

        # When: We create phi with 4 inputs
        phi = PhiNode([v1, v2, v3, v4])

        # Then: All inputs should be connected
        assert len(phi.inputs) == 4
        assert v1 in phi.inputs
        assert v4 in phi.inputs


class TestLoadPropertyNode:
    """Test property load IR node"""

    def test_create_load_property_node(self):
        """Should create property load node"""
        # Given: Object and property name
        obj = ParameterNode(0)
        property_name = "x"

        # When: We create load property node
        load = LoadPropertyNode(obj, property_name)

        # Then: Node should be created correctly
        assert load.node_type == IRNodeType.LOAD_PROPERTY
        assert load.property_name == "x"
        assert obj in load.inputs


class TestStorePropertyNode:
    """Test property store IR node"""

    def test_create_store_property_node(self):
        """Should create property store node"""
        # Given: Object, property name, and value
        obj = ParameterNode(0)
        value = ConstantNode(42)
        property_name = "x"

        # When: We create store property node
        store = StorePropertyNode(obj, property_name, value)

        # Then: Node should be created correctly
        assert store.node_type == IRNodeType.STORE_PROPERTY
        assert store.property_name == "x"
        assert obj in store.inputs
        assert value in store.inputs


class TestCallNode:
    """Test function call IR node"""

    def test_create_call_node(self):
        """Should create call node"""
        # Given: Function and arguments
        func = ParameterNode(0)
        arg1 = ConstantNode(10)
        arg2 = ConstantNode(20)

        # When: We create call node
        call = CallNode(func, [arg1, arg2])

        # Then: Node should be created correctly
        assert call.node_type == IRNodeType.CALL
        assert func in call.inputs
        assert arg1 in call.inputs
        assert arg2 in call.inputs

    def test_call_node_no_args(self):
        """Should support call with no arguments"""
        # Given: Function with no args
        func = ParameterNode(0)

        # When: We create call node with no args
        call = CallNode(func, [])

        # Then: Only function should be in inputs
        assert len(call.inputs) == 1
        assert func in call.inputs


class TestReturnNode:
    """Test return IR node"""

    def test_create_return_node(self):
        """Should create return node"""
        # Given: Return value
        value = ConstantNode(42)

        # When: We create return node
        ret = ReturnNode(value)

        # Then: Node should be created correctly
        assert ret.node_type == IRNodeType.RETURN
        assert value in ret.inputs

    def test_return_void(self):
        """Should support return with no value (undefined)"""
        # Given: No return value
        # When: We create return node with None
        ret = ReturnNode(None)

        # Then: Should have no inputs
        assert len(ret.inputs) == 0


class TestBranchNode:
    """Test conditional branch IR node"""

    def test_create_branch_node(self):
        """Should create branch node"""
        # Given: Condition
        condition = ConstantNode(True)

        # When: We create branch node
        branch = BranchNode(condition)

        # Then: Node should be created correctly
        assert branch.node_type == IRNodeType.BRANCH
        assert condition in branch.inputs


class TestMergeNode:
    """Test control flow merge IR node"""

    def test_create_merge_node(self):
        """Should create merge node"""
        # Given: Multiple control flow paths
        # When: We create merge node
        merge = MergeNode(num_predecessors=2)

        # Then: Node should be created correctly
        assert merge.node_type == IRNodeType.MERGE
        assert merge.num_predecessors == 2

    def test_merge_multiple_paths(self):
        """Should support merging multiple paths"""
        # Given: 4 control flow paths
        # When: We create merge node with 4 predecessors
        merge = MergeNode(num_predecessors=4)

        # Then: Should support 4 paths
        assert merge.num_predecessors == 4
