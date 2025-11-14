"""
Unit tests for SourceLocation dataclass.

Following TDD: These tests are written FIRST before implementation.
"""

import pytest
from dataclasses import is_dataclass


def test_source_location_exists():
    """Test that SourceLocation can be imported."""
    from src.location import SourceLocation

    assert is_dataclass(SourceLocation)


def test_source_location_has_filename_field():
    """Test that SourceLocation has filename field."""
    from src.location import SourceLocation

    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    assert hasattr(loc, "filename")
    assert loc.filename == "test.js"


def test_source_location_has_line_field():
    """Test that SourceLocation has line field (1-indexed)."""
    from src.location import SourceLocation

    loc = SourceLocation(filename="test.js", line=42, column=1, offset=0)
    assert hasattr(loc, "line")
    assert loc.line == 42


def test_source_location_has_column_field():
    """Test that SourceLocation has column field (1-indexed)."""
    from src.location import SourceLocation

    loc = SourceLocation(filename="test.js", line=1, column=15, offset=0)
    assert hasattr(loc, "column")
    assert loc.column == 15


def test_source_location_has_offset_field():
    """Test that SourceLocation has offset field (byte offset)."""
    from src.location import SourceLocation

    loc = SourceLocation(filename="test.js", line=1, column=1, offset=128)
    assert hasattr(loc, "offset")
    assert loc.offset == 128


def test_source_location_can_be_created_with_all_fields():
    """
    Given valid values for all fields
    When creating a SourceLocation
    Then all fields are correctly set
    """
    from src.location import SourceLocation

    loc = SourceLocation(filename="main.js", line=10, column=5, offset=256)

    assert loc.filename == "main.js"
    assert loc.line == 10
    assert loc.column == 5
    assert loc.offset == 256


def test_source_location_equality():
    """Test that two SourceLocation instances with same values are equal."""
    from src.location import SourceLocation

    loc1 = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    loc2 = SourceLocation(filename="test.js", line=1, column=1, offset=0)

    assert loc1 == loc2


def test_source_location_inequality():
    """Test that two SourceLocation instances with different values are not equal."""
    from src.location import SourceLocation

    loc1 = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    loc2 = SourceLocation(filename="test.js", line=2, column=1, offset=0)

    assert loc1 != loc2


def test_source_location_repr():
    """Test that SourceLocation has a useful repr."""
    from src.location import SourceLocation

    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    repr_str = repr(loc)

    assert "SourceLocation" in repr_str
    assert "test.js" in repr_str


def test_source_location_with_different_filenames():
    """Test SourceLocation with different filenames."""
    from src.location import SourceLocation

    loc1 = SourceLocation(filename="module1.js", line=1, column=1, offset=0)
    loc2 = SourceLocation(filename="module2.js", line=1, column=1, offset=0)

    assert loc1.filename != loc2.filename


def test_source_location_with_large_values():
    """Test SourceLocation with large line, column, and offset values."""
    from src.location import SourceLocation

    loc = SourceLocation(
        filename="large_file.js", line=100000, column=5000, offset=10000000
    )

    assert loc.line == 100000
    assert loc.column == 5000
    assert loc.offset == 10000000


def test_source_location_fields_are_immutable():
    """Test that SourceLocation is immutable (frozen dataclass)."""
    from src.location import SourceLocation

    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)

    with pytest.raises(Exception):  # Will raise FrozenInstanceError or AttributeError
        loc.line = 2


def test_source_location_validates_line_must_be_positive():
    """
    Given a line number less than 1
    When creating SourceLocation
    Then ValueError is raised
    """
    from src.location import SourceLocation

    with pytest.raises(ValueError, match="Line must be >= 1"):
        SourceLocation(filename="test.js", line=0, column=1, offset=0)

    with pytest.raises(ValueError, match="Line must be >= 1"):
        SourceLocation(filename="test.js", line=-1, column=1, offset=0)


def test_source_location_validates_column_must_be_positive():
    """
    Given a column number less than 1
    When creating SourceLocation
    Then ValueError is raised
    """
    from src.location import SourceLocation

    with pytest.raises(ValueError, match="Column must be >= 1"):
        SourceLocation(filename="test.js", line=1, column=0, offset=0)

    with pytest.raises(ValueError, match="Column must be >= 1"):
        SourceLocation(filename="test.js", line=1, column=-1, offset=0)


def test_source_location_validates_offset_must_be_non_negative():
    """
    Given a negative offset
    When creating SourceLocation
    Then ValueError is raised
    """
    from src.location import SourceLocation

    with pytest.raises(ValueError, match="Offset must be >= 0"):
        SourceLocation(filename="test.js", line=1, column=1, offset=-1)
