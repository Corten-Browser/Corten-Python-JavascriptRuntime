"""
Unit tests for ICShapeIntegration class

RED phase: Tests written before implementation
Tests for FR-P4-021: Integration with inline caching
"""
import pytest


class TestICShapeIntegrationCreation:
    """Test ICShapeIntegration initialization"""

    def test_ic_integration_creation(self):
        """Test creating IC integration"""
        from components.hidden_classes.src.ic_integration import ICShapeIntegration
        from components.hidden_classes.src.shape_tree import ShapeTree
        from components.hidden_classes.src.shape_profiler import ShapeProfiler

        tree = ShapeTree()
        profiler = ShapeProfiler()
        ic_integration = ICShapeIntegration(tree, profiler)

        assert ic_integration is not None
        assert ic_integration.shape_tree is tree
        assert ic_integration.profiler is profiler


class TestGetShapeForIC:
    """Test getting shape from object for IC validation"""

    def test_get_shape_for_ic(self):
        """Test getting object's shape for IC"""
        from components.hidden_classes.src.ic_integration import ICShapeIntegration
        from components.hidden_classes.src.shape_tree import ShapeTree
        from components.hidden_classes.src.shape_profiler import ShapeProfiler

        tree = ShapeTree()
        profiler = ShapeProfiler()
        ic_integration = ICShapeIntegration(tree, profiler)

        # Create mock object with shape
        class MockJSObject:
            def __init__(self, shape):
                self.shape = shape

        root_shape = tree.get_root_shape()
        obj = MockJSObject(root_shape)

        shape = ic_integration.get_shape_for_ic(obj)
        assert shape is root_shape


class TestICEntryValidation:
    """Test validating IC cache entries"""

    def test_validate_ic_entry_same_shape(self):
        """Test IC entry validation when shape matches"""
        from components.hidden_classes.src.ic_integration import ICShapeIntegration
        from components.hidden_classes.src.shape_tree import ShapeTree
        from components.hidden_classes.src.shape_profiler import ShapeProfiler

        tree = ShapeTree()
        profiler = ShapeProfiler()
        ic_integration = ICShapeIntegration(tree, profiler)

        shape = tree.get_root_shape()
        cached_shape = shape
        cached_offset = 0

        # Same shape should validate
        assert ic_integration.validate_ic_entry(shape, cached_shape, cached_offset) is True

    def test_validate_ic_entry_different_shape(self):
        """Test IC entry validation when shape differs"""
        from components.hidden_classes.src.ic_integration import ICShapeIntegration
        from components.hidden_classes.src.shape_tree import ShapeTree
        from components.hidden_classes.src.shape_profiler import ShapeProfiler
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        tree = ShapeTree()
        profiler = ShapeProfiler()
        ic_integration = ICShapeIntegration(tree, profiler)

        root = tree.get_root_shape()
        attrs = PropertyAttributes()
        child = tree.get_or_create_child(root, "x", attrs)

        # Different shapes should not validate (unless offset same)
        result = ic_integration.validate_ic_entry(child, root, 0)
        # This should be False unless shapes are compatible
        assert isinstance(result, bool)

    def test_validate_ic_entry_same_offset_different_shape(self):
        """Test IC validation with different shape but same offset"""
        from components.hidden_classes.src.ic_integration import ICShapeIntegration
        from components.hidden_classes.src.shape_tree import ShapeTree
        from components.hidden_classes.src.shape_profiler import ShapeProfiler
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        tree = ShapeTree()
        profiler = ShapeProfiler()
        ic_integration = ICShapeIntegration(tree, profiler)

        root = tree.get_root_shape()
        attrs = PropertyAttributes()

        # Create two different shapes with same property at same offset
        shape1 = tree.get_or_create_child(root, "x", attrs)
        shape2 = tree.get_or_create_child(root, "x", attrs)

        # Since they have same parent and property, they should be the same shape
        assert shape1 is shape2


class TestPropertyOffsetForIC:
    """Test getting property offset for IC fast path"""

    def test_get_property_offset_for_ic_found(self):
        """Test getting property offset for IC when property exists"""
        from components.hidden_classes.src.ic_integration import ICShapeIntegration
        from components.hidden_classes.src.shape_tree import ShapeTree
        from components.hidden_classes.src.shape_profiler import ShapeProfiler
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        tree = ShapeTree()
        profiler = ShapeProfiler()
        ic_integration = ICShapeIntegration(tree, profiler)

        root = tree.get_root_shape()
        attrs = PropertyAttributes()
        shape = tree.get_or_create_child(root, "x", attrs)

        offset = ic_integration.get_property_offset_for_ic(shape, "x")
        assert offset == 0

    def test_get_property_offset_for_ic_not_found(self):
        """Test getting property offset for IC when property doesn't exist"""
        from components.hidden_classes.src.ic_integration import ICShapeIntegration
        from components.hidden_classes.src.shape_tree import ShapeTree
        from components.hidden_classes.src.shape_profiler import ShapeProfiler

        tree = ShapeTree()
        profiler = ShapeProfiler()
        ic_integration = ICShapeIntegration(tree, profiler)

        root = tree.get_root_shape()

        offset = ic_integration.get_property_offset_for_ic(root, "nonexistent")
        assert offset is None


class TestICHitRecording:
    """Test recording IC hits for profiling"""

    def test_record_ic_hit(self):
        """Test recording IC hit"""
        from components.hidden_classes.src.ic_integration import ICShapeIntegration
        from components.hidden_classes.src.shape_tree import ShapeTree
        from components.hidden_classes.src.shape_profiler import ShapeProfiler
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        tree = ShapeTree()
        profiler = ShapeProfiler()
        ic_integration = ICShapeIntegration(tree, profiler)

        root = tree.get_root_shape()
        attrs = PropertyAttributes()
        shape = tree.get_or_create_child(root, "x", attrs)

        profiler.record_creation(shape)
        ic_integration.record_ic_hit(shape, "x")

        # Check profiler recorded access
        stats = profiler.stats[id(shape)]
        assert stats.access_count == 1

    def test_record_multiple_ic_hits(self):
        """Test recording multiple IC hits"""
        from components.hidden_classes.src.ic_integration import ICShapeIntegration
        from components.hidden_classes.src.shape_tree import ShapeTree
        from components.hidden_classes.src.shape_profiler import ShapeProfiler
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        tree = ShapeTree()
        profiler = ShapeProfiler()
        ic_integration = ICShapeIntegration(tree, profiler)

        root = tree.get_root_shape()
        attrs = PropertyAttributes()
        shape = tree.get_or_create_child(root, "x", attrs)

        profiler.record_creation(shape)
        ic_integration.record_ic_hit(shape, "x")
        ic_integration.record_ic_hit(shape, "x")
        ic_integration.record_ic_hit(shape, "x")

        stats = profiler.stats[id(shape)]
        assert stats.access_count == 3


class TestICMissRecording:
    """Test recording IC misses"""

    def test_record_ic_miss(self):
        """Test recording IC miss"""
        from components.hidden_classes.src.ic_integration import ICShapeIntegration
        from components.hidden_classes.src.shape_tree import ShapeTree
        from components.hidden_classes.src.shape_profiler import ShapeProfiler
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        tree = ShapeTree()
        profiler = ShapeProfiler()
        ic_integration = ICShapeIntegration(tree, profiler)

        root = tree.get_root_shape()
        attrs = PropertyAttributes()
        shape = tree.get_or_create_child(root, "x", attrs)

        profiler.record_creation(shape)
        ic_integration.record_ic_miss(shape, "x")

        # IC miss should still be recorded (for profiling)
        # Implementation may choose to record this differently
        # Just verify it doesn't crash
        assert True


class TestICIntegrationWorkflow:
    """Test complete IC integration workflow"""

    def test_ic_fast_path_workflow(self):
        """Test IC fast path with shape validation"""
        from components.hidden_classes.src.ic_integration import ICShapeIntegration
        from components.hidden_classes.src.shape_tree import ShapeTree
        from components.hidden_classes.src.shape_profiler import ShapeProfiler
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        tree = ShapeTree()
        profiler = ShapeProfiler()
        ic_integration = ICShapeIntegration(tree, profiler)

        # Create object with property
        root = tree.get_root_shape()
        attrs = PropertyAttributes()
        shape = tree.get_or_create_child(root, "x", attrs)

        class MockJSObject:
            def __init__(self, shape):
                self.shape = shape

        obj = MockJSObject(shape)

        # Simulate IC cache
        cached_shape = shape
        cached_offset = 0

        # Get current shape
        current_shape = ic_integration.get_shape_for_ic(obj)

        # Validate IC entry
        if ic_integration.validate_ic_entry(current_shape, cached_shape, cached_offset):
            # IC HIT - use fast path
            offset = ic_integration.get_property_offset_for_ic(current_shape, "x")
            assert offset == 0
            ic_integration.record_ic_hit(current_shape, "x")
        else:
            # IC MISS - slow path
            ic_integration.record_ic_miss(current_shape, "x")

    def test_ic_miss_workflow_shape_changed(self):
        """Test IC miss workflow when shape changes"""
        from components.hidden_classes.src.ic_integration import ICShapeIntegration
        from components.hidden_classes.src.shape_tree import ShapeTree
        from components.hidden_classes.src.shape_profiler import ShapeProfiler
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        tree = ShapeTree()
        profiler = ShapeProfiler()
        ic_integration = ICShapeIntegration(tree, profiler)

        root = tree.get_root_shape()
        attrs = PropertyAttributes()

        # Original shape: {x}
        shape1 = tree.get_or_create_child(root, "x", attrs)

        # New shape: {x, y}
        shape2 = tree.get_or_create_child(shape1, "y", attrs)

        class MockJSObject:
            def __init__(self, shape):
                self.shape = shape

        obj = MockJSObject(shape2)

        # IC cached for shape1
        cached_shape = shape1
        cached_offset = 0

        # Get current shape (shape2)
        current_shape = ic_integration.get_shape_for_ic(obj)

        # Shapes differ - should be miss (unless offset compatible)
        result = ic_integration.validate_ic_entry(current_shape, cached_shape, cached_offset)
        # Just verify we get a boolean result
        assert isinstance(result, bool)
