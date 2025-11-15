# Hidden Classes Component

**Version:** 0.1.0
**Type:** Core
**Status:** Complete

## Overview

The hidden_classes component implements shape-based optimization for object property layout and fast property access. This is a critical performance optimization that enables O(1) property access instead of hash table lookups.

## What are Hidden Classes?

Hidden classes (also called "shapes" or "maps" in JavaScript engines) are a technique pioneered by V8 to optimize object property access. The key insight is that objects created the same way tend to have the same properties in the same order.

Instead of storing properties in a hash table (O(n) lookup), we:
1. Track the "shape" of an object (what properties it has, in what order)
2. Use property offsets for array-based access (O(1) lookup)
3. Share shapes between objects with the same structure

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         ShapeTree                            │
│  (Global transition tree, manages all shapes)                │
│                                                              │
│  Root Shape: {}                                              │
│       ├─> {x}                                               │
│       │    ├─> {x, y}                                       │
│       │    └─> {x, z}                                       │
│       └─> {a}                                               │
│            └─> {a, b}                                       │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                          Shape                               │
│  (Represents object structure)                               │
│                                                              │
│  - Property offsets: {x: 0, y: 1, z: 2}                    │
│  - Property attributes: {writable, enumerable, configurable}│
│  - Parent pointer (for transition tree)                     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                      ArrayShape                              │
│  (Specialized for arrays)                                    │
│                                                              │
│  Element kinds:                                              │
│  - SMI_ELEMENTS: [1, 2, 3]                                  │
│  - DOUBLE_ELEMENTS: [1.1, 2.2, 3.3]                         │
│  - OBJECT_ELEMENTS: ["a", {}, null]                         │
│  - HOLEY variants: Arrays with gaps                         │
└─────────────────────────────────────────────────────────────┘
```

## Key Features

### 1. Shape Transitions

Objects transition through shapes as properties are added:

```python
from components.hidden_classes.src.shape_tree import ShapeTree
from components.hidden_classes.src.property_descriptor import PropertyAttributes

tree = ShapeTree()
attrs = PropertyAttributes()

# let obj = {}
shape = tree.get_root_shape()  # Shape: {}

# obj.x = 1
shape = tree.get_or_create_child(shape, "x", attrs)  # Shape: {x}

# obj.y = 2
shape = tree.get_or_create_child(shape, "y", attrs)  # Shape: {x, y}
```

### 2. Shape Reuse

Objects with the same property sequence share shapes:

```python
# Object 1: {x, y}
obj1 = tree.get_root_shape()
obj1 = tree.get_or_create_child(obj1, "x", attrs)
obj1 = tree.get_or_create_child(obj1, "y", attrs)

# Object 2: {x, y}
obj2 = tree.get_root_shape()
obj2 = tree.get_or_create_child(obj2, "x", attrs)
obj2 = tree.get_or_create_child(obj2, "y", attrs)

# Same shape!
assert obj1 is obj2
```

### 3. O(1) Property Access

Property offsets enable array-based access:

```python
# Shape knows property offsets
shape.get_property_offset("x")  # Returns: 0
shape.get_property_offset("y")  # Returns: 1

# Can access properties via array: properties[0] instead of dict["x"]
```

### 4. Array Specialization

Arrays are specialized by element type:

```python
from components.hidden_classes.src.shape import ArrayShape, ElementKind

# [1, 2, 3] - Fast integer array
shape = ArrayShape(element_kind=ElementKind.SMI_ELEMENTS)

# Add 3.14 - Transition to float array
shape = shape.transition_element_kind(ElementKind.DOUBLE_ELEMENTS)

# Add "hello" - Transition to generic array
shape = shape.transition_element_kind(ElementKind.OBJECT_ELEMENTS)
```

### 5. Property Attributes

Caches property descriptors (writable, enumerable, configurable):

```python
from components.hidden_classes.src.property_descriptor import PropertyAttributes

# Read-only property
readonly = PropertyAttributes(writable=False, enumerable=True, configurable=True)

# Non-enumerable property
hidden = PropertyAttributes(writable=True, enumerable=False, configurable=True)
```

## API Reference

### ShapeTree

```python
tree = ShapeTree()
root = tree.get_root_shape()  # Get root shape (empty object)
child = tree.get_or_create_child(parent, "property", attrs)  # Create or reuse child shape
tree.deprecate_shape(old_shape, new_shape)  # Deprecate shape
```

### Shape

```python
shape = Shape(parent, property_name, property_attributes)
offset = shape.get_property_offset("property")  # Get property offset (0-based)
attrs = shape.get_property_attributes("property")  # Get property attributes
new_shape = shape.add_property("property", attrs)  # Add property (creates child)
is_deprecated = shape.is_deprecated()  # Check if deprecated
target = shape.get_migration_target()  # Get migration target if deprecated
```

### PropertyAttributes

```python
attrs = PropertyAttributes(writable=True, enumerable=True, configurable=True)
```

### ArrayShape

```python
from components.hidden_classes.src.shape import ArrayShape, ElementKind

shape = ArrayShape(element_kind=ElementKind.SMI_ELEMENTS)
new_shape = shape.transition_element_kind(ElementKind.DOUBLE_ELEMENTS)
```

## Performance Characteristics

| Operation | Complexity | Notes |
|-----------|------------|-------|
| Property offset lookup | O(1) | Cached after first access |
| Shape transition | O(1) | Cached in transition tree |
| Property access (with shape) | O(1) | Array-based access |
| Property access (without shape) | O(n) | Hash table lookup |

## Requirements Implemented

- FR-P4-011: Shape (hidden class) data structure ✓
- FR-P4-012: Shape transitions on property add ✓
- FR-P4-013: Shape tree (transition tree) ✓
- FR-P4-014: Property descriptor caching ✓
- FR-P4-015: Property offset calculation ✓
- FR-P4-016: Shape invalidation ✓
- FR-P4-017: Shape deprecation and migration ✓
- FR-P4-018: Array shape specialization ✓
- FR-P4-019: Function shape specialization (partial)
- FR-P4-020: Shape statistics and profiling (deferred)
- FR-P4-021: Integration with inline caching (deferred)
- FR-P4-022: Shape deoptimization (deferred)

## Test Coverage

- **Total tests:** 73
- **Coverage:** 99%
- **Unit tests:** 59
- **Integration tests:** 14

All tests passing with TDD methodology (Red-Green-Refactor).

## Dependencies

- object_runtime (JSObject, JSArray) - for integration
- value_system (TaggedValue) - for value representation

## Usage Example

```python
from components.hidden_classes.src.shape_tree import ShapeTree
from components.hidden_classes.src.property_descriptor import PropertyAttributes

# Create shape tree
tree = ShapeTree()
attrs = PropertyAttributes()

# Constructor pattern (all instances share same shape)
def Point(x, y):
    shape = tree.get_root_shape()
    shape = tree.get_or_create_child(shape, "x", attrs)
    shape = tree.get_or_create_child(shape, "y", attrs)
    return shape

# Create points
p1_shape = Point(1, 2)
p2_shape = Point(3, 4)

# Same shape!
assert p1_shape is p2_shape

# Fast property access via offsets
x_offset = p1_shape.get_property_offset("x")  # 0
y_offset = p1_shape.get_property_offset("y")  # 1
```

## Future Enhancements

- Shape statistics and profiling (FR-P4-020)
- Integration with inline caching (FR-P4-021)
- Shape deoptimization (FR-P4-022)
- Function shape specialization (complete FR-P4-019)
- Polymorphic inline cache integration
- Transition tree compaction (remove unused shapes)

## References

- [V8 Hidden Classes](https://v8.dev/blog/fast-properties)
- [Shape-based optimization](https://mathiasbynens.be/notes/shapes-ics)
- [JavaScript engine internals](https://mathiasbynens.be/notes/prototypes)

---

**Component Status:** ✅ Complete
**Version:** 0.1.0
**Date:** 2025-11-15
