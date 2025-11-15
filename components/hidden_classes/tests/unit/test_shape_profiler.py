"""
Unit tests for ShapeProfiler class

RED phase: Tests written before implementation
Tests for FR-P4-020: Shape statistics and profiling
"""
import pytest


class TestShapeProfilerCreation:
    """Test ShapeProfiler initialization"""

    def test_profiler_creation(self):
        """Test creating profiler"""
        from components.hidden_classes.src.shape_profiler import ShapeProfiler

        profiler = ShapeProfiler()
        assert profiler is not None
        assert profiler.stats == {}

    def test_profiler_empty_profile(self):
        """Test empty profiler returns zero stats"""
        from components.hidden_classes.src.shape_profiler import ShapeProfiler

        profiler = ShapeProfiler()
        profile = profiler.get_profile()

        assert profile.total_shapes == 0
        assert profile.active_shapes == 0
        assert profile.deprecated_shapes == 0
        assert profile.hot_shapes == []


class TestShapeCreationRecording:
    """Test recording shape creation"""

    def test_record_single_creation(self):
        """Test recording single shape creation"""
        from components.hidden_classes.src.shape_profiler import ShapeProfiler
        from components.hidden_classes.src.shape import Shape

        profiler = ShapeProfiler()
        shape = Shape(parent=None, property_name=None, property_attributes=None)

        profiler.record_creation(shape)

        # Shape should be tracked
        assert id(shape) in profiler.stats
        stats = profiler.stats[id(shape)]
        assert stats.shape_id == id(shape)
        assert stats.creation_count == 1
        assert stats.transition_count == 0
        assert stats.access_count == 0

    def test_record_multiple_creations(self):
        """Test recording multiple shape creations"""
        from components.hidden_classes.src.shape_profiler import ShapeProfiler
        from components.hidden_classes.src.shape import Shape

        profiler = ShapeProfiler()
        shape1 = Shape(parent=None, property_name=None, property_attributes=None)
        shape2 = Shape(parent=None, property_name=None, property_attributes=None)

        profiler.record_creation(shape1)
        profiler.record_creation(shape2)

        profile = profiler.get_profile()
        assert profile.total_shapes == 2


class TestShapeTransitionRecording:
    """Test recording shape transitions"""

    def test_record_single_transition(self):
        """Test recording shape transition"""
        from components.hidden_classes.src.shape_profiler import ShapeProfiler
        from components.hidden_classes.src.shape import Shape
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        profiler = ShapeProfiler()
        root = Shape(parent=None, property_name=None, property_attributes=None)
        attrs = PropertyAttributes()
        child = Shape(parent=root, property_name="x", property_attributes=attrs)

        profiler.record_creation(root)
        profiler.record_creation(child)
        profiler.record_transition(root, "x", child)

        # Check transition recorded
        stats = profiler.stats[id(root)]
        assert stats.transition_count == 1
        assert "x" in stats.children
        assert stats.children["x"] == id(child)

    def test_record_multiple_transitions(self):
        """Test recording multiple transitions from same shape"""
        from components.hidden_classes.src.shape_profiler import ShapeProfiler
        from components.hidden_classes.src.shape import Shape
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        profiler = ShapeProfiler()
        root = Shape(parent=None, property_name=None, property_attributes=None)
        attrs = PropertyAttributes()
        child_x = Shape(parent=root, property_name="x", property_attributes=attrs)
        child_y = Shape(parent=root, property_name="y", property_attributes=attrs)

        profiler.record_creation(root)
        profiler.record_creation(child_x)
        profiler.record_creation(child_y)
        profiler.record_transition(root, "x", child_x)
        profiler.record_transition(root, "y", child_y)

        # Check both transitions recorded
        stats = profiler.stats[id(root)]
        assert stats.transition_count == 2
        assert len(stats.children) == 2
        assert stats.children["x"] == id(child_x)
        assert stats.children["y"] == id(child_y)

    def test_transition_frequency_tracking(self):
        """Test tracking transition frequencies"""
        from components.hidden_classes.src.shape_profiler import ShapeProfiler
        from components.hidden_classes.src.shape import Shape
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        profiler = ShapeProfiler()
        root = Shape(parent=None, property_name=None, property_attributes=None)
        attrs = PropertyAttributes()
        child = Shape(parent=root, property_name="x", property_attributes=attrs)

        profiler.record_creation(root)
        profiler.record_creation(child)

        # Record same transition multiple times
        profiler.record_transition(root, "x", child)
        profiler.record_transition(root, "x", child)
        profiler.record_transition(root, "x", child)

        profile = profiler.get_profile()
        key = (id(root), "x")
        assert key in profile.transition_frequencies
        assert profile.transition_frequencies[key] == 3


class TestPropertyAccessRecording:
    """Test recording property accesses"""

    def test_record_property_access(self):
        """Test recording property access"""
        from components.hidden_classes.src.shape_profiler import ShapeProfiler
        from components.hidden_classes.src.shape import Shape
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        profiler = ShapeProfiler()
        root = Shape(parent=None, property_name=None, property_attributes=None)
        attrs = PropertyAttributes()
        shape = Shape(parent=root, property_name="x", property_attributes=attrs)

        profiler.record_creation(shape)
        profiler.record_access(shape, "x")

        stats = profiler.stats[id(shape)]
        assert stats.access_count == 1

    def test_record_multiple_accesses(self):
        """Test recording multiple property accesses"""
        from components.hidden_classes.src.shape_profiler import ShapeProfiler
        from components.hidden_classes.src.shape import Shape
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        profiler = ShapeProfiler()
        root = Shape(parent=None, property_name=None, property_attributes=None)
        attrs = PropertyAttributes()
        shape = Shape(parent=root, property_name="x", property_attributes=attrs)

        profiler.record_creation(shape)
        profiler.record_access(shape, "x")
        profiler.record_access(shape, "x")
        profiler.record_access(shape, "x")

        stats = profiler.stats[id(shape)]
        assert stats.access_count == 3


class TestShapeDeprecationRecording:
    """Test recording shape deprecation"""

    def test_record_deprecation(self):
        """Test recording shape deprecation"""
        from components.hidden_classes.src.shape_profiler import ShapeProfiler
        from components.hidden_classes.src.shape import Shape

        profiler = ShapeProfiler()
        shape = Shape(parent=None, property_name=None, property_attributes=None)

        profiler.record_creation(shape)
        profiler.record_deprecation(shape)

        stats = profiler.stats[id(shape)]
        assert stats.deprecation_count == 1

    def test_profile_deprecated_count(self):
        """Test profile tracks deprecated shapes"""
        from components.hidden_classes.src.shape_profiler import ShapeProfiler
        from components.hidden_classes.src.shape import Shape

        profiler = ShapeProfiler()
        shape1 = Shape(parent=None, property_name=None, property_attributes=None)
        shape2 = Shape(parent=None, property_name=None, property_attributes=None)

        profiler.record_creation(shape1)
        profiler.record_creation(shape2)
        profiler.record_deprecation(shape1)

        profile = profiler.get_profile()
        assert profile.total_shapes == 2
        assert profile.deprecated_shapes == 1
        assert profile.active_shapes == 1


class TestHotShapeDetection:
    """Test identifying hot (frequently-used) shapes"""

    def test_get_hot_shapes_empty(self):
        """Test getting hot shapes from empty profiler"""
        from components.hidden_classes.src.shape_profiler import ShapeProfiler

        profiler = ShapeProfiler()
        hot_shapes = profiler.get_hot_shapes(threshold=100)
        assert hot_shapes == []

    def test_get_hot_shapes_by_access(self):
        """Test identifying hot shapes by access count"""
        from components.hidden_classes.src.shape_profiler import ShapeProfiler
        from components.hidden_classes.src.shape import Shape

        profiler = ShapeProfiler()
        cold_shape = Shape(parent=None, property_name=None, property_attributes=None)
        hot_shape = Shape(parent=None, property_name=None, property_attributes=None)

        profiler.record_creation(cold_shape)
        profiler.record_creation(hot_shape)

        # cold_shape: 10 accesses
        for _ in range(10):
            profiler.record_access(cold_shape, "x")

        # hot_shape: 1000 accesses (above threshold)
        for _ in range(1000):
            profiler.record_access(hot_shape, "x")

        hot_shapes = profiler.get_hot_shapes(threshold=100)
        assert len(hot_shapes) == 1
        assert hot_shapes[0] == id(hot_shape)

    def test_hot_shapes_in_profile(self):
        """Test hot shapes appear in profile"""
        from components.hidden_classes.src.shape_profiler import ShapeProfiler
        from components.hidden_classes.src.shape import Shape

        profiler = ShapeProfiler()
        shape = Shape(parent=None, property_name=None, property_attributes=None)

        profiler.record_creation(shape)
        for _ in range(2000):
            profiler.record_access(shape, "x")

        profile = profiler.get_profile()
        # Should be in top 10 hot shapes
        assert id(shape) in profile.hot_shapes


class TestShapeProfile:
    """Test complete profile generation"""

    def test_comprehensive_profile(self):
        """Test generating comprehensive profile"""
        from components.hidden_classes.src.shape_profiler import ShapeProfiler
        from components.hidden_classes.src.shape import Shape
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        profiler = ShapeProfiler()
        root = Shape(parent=None, property_name=None, property_attributes=None)
        attrs = PropertyAttributes()
        child = Shape(parent=root, property_name="x", property_attributes=attrs)

        # Create shapes
        profiler.record_creation(root)
        profiler.record_creation(child)

        # Transition
        profiler.record_transition(root, "x", child)

        # Accesses
        profiler.record_access(child, "x")
        profiler.record_access(child, "x")

        # Deprecate one
        profiler.record_deprecation(root)

        profile = profiler.get_profile()
        assert profile.total_shapes == 2
        assert profile.active_shapes == 1
        assert profile.deprecated_shapes == 1
        assert len(profile.transition_frequencies) == 1
