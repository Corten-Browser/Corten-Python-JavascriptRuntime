"""
Unit tests for SourceMapPreparer (FR-ES24-D-017)

Tests cover:
- Basic source location
- Location with source root
- Minimum line/column values
- Large line/column values
- Very long filename
- Filename with special characters
- Source map URL generation
- Metadata preparation
"""

import pytest
from components.error_stack_polish.src.source_map import SourceMapPreparer


class TestSourceMapPreparer:
    """Test suite for source map support preparation"""

    def setup_method(self):
        """Set up test fixtures"""
        self.preparer = SourceMapPreparer()

    # Test 1: Basic source location
    def test_basic_source_location(self):
        """Test preparing basic source location"""
        result = self.preparer.prepare_source_map(
            filename="dist/bundle.js",
            line=42,
            column=15
        )

        assert result["generated_location"]["filename"] == "dist/bundle.js"
        assert result["generated_location"]["line"] == 42
        assert result["generated_location"]["column"] == 15
        assert result["source_map_url"] == "dist/bundle.js.map"
        assert result["ready_for_resolution"] is True

    # Test 2: Location with source root
    def test_location_with_source_root(self):
        """Test preparing location with source root"""
        result = self.preparer.prepare_source_map(
            filename="dist/bundle.js",
            line=100,
            column=5,
            source_root="/app/src"
        )

        assert result["generated_location"]["filename"] == "dist/bundle.js"
        assert result["generated_location"]["line"] == 100
        assert result["generated_location"]["column"] == 5
        assert result["metadata"]["source_root"] == "/app/src"
        assert result["source_map_url"] == "dist/bundle.js.map"
        assert result["ready_for_resolution"] is True

    # Test 3: Minimum line/column values
    def test_minimum_line_column_values(self):
        """Test preparing location with minimum valid values"""
        result = self.preparer.prepare_source_map(
            filename="test.js",
            line=1,  # Minimum line (1-indexed)
            column=0  # Minimum column (0-indexed)
        )

        assert result["generated_location"]["line"] == 1
        assert result["generated_location"]["column"] == 0
        assert result["ready_for_resolution"] is True

    # Test 4: Large line/column values
    def test_large_line_column_values(self):
        """Test preparing location with large line/column values"""
        result = self.preparer.prepare_source_map(
            filename="large.js",
            line=999999,
            column=500
        )

        assert result["generated_location"]["line"] == 999999
        assert result["generated_location"]["column"] == 500
        assert result["ready_for_resolution"] is True

    # Test 5: Very long filename
    def test_very_long_filename(self):
        """Test preparing location with very long filename"""
        long_filename = "a" * 4000 + ".js"
        result = self.preparer.prepare_source_map(
            filename=long_filename,
            line=1,
            column=0
        )

        assert result["generated_location"]["filename"] == long_filename
        assert result["source_map_url"] == long_filename + ".map"
        assert result["ready_for_resolution"] is True

    # Test 6: Filename with special characters
    def test_filename_with_special_characters(self):
        """Test preparing location with special characters in filename"""
        special_filename = "my-app/dist/bundle@v2.0.0.js"
        result = self.preparer.prepare_source_map(
            filename=special_filename,
            line=10,
            column=5
        )

        assert result["generated_location"]["filename"] == special_filename
        assert result["source_map_url"] == special_filename + ".map"
        assert result["ready_for_resolution"] is True

    # Test 7: Source map URL generation
    def test_source_map_url_generation(self):
        """Test that source map URLs are correctly generated"""
        test_cases = [
            ("app.js", "app.js.map"),
            ("dist/bundle.js", "dist/bundle.js.map"),
            ("/absolute/path/file.js", "/absolute/path/file.js.map"),
            ("file.min.js", "file.min.js.map"),
            ("http://example.com/script.js", "http://example.com/script.js.map")
        ]

        for filename, expected_url in test_cases:
            result = self.preparer.prepare_source_map(
                filename=filename,
                line=1,
                column=0
            )
            assert result["source_map_url"] == expected_url

    # Test 8: Metadata preparation
    def test_metadata_preparation(self):
        """Test that metadata is correctly prepared"""
        result = self.preparer.prepare_source_map(
            filename="dist/bundle.js",
            line=42,
            column=15,
            source_root="/app/src"
        )

        assert "metadata" in result
        assert result["metadata"]["source_root"] == "/app/src"
        assert result["metadata"]["original_filename"] == "dist/bundle.js"
        assert result["ready_for_resolution"] is True


class TestSourceMapPreparerEdgeCases:
    """Test edge cases and error handling"""

    def setup_method(self):
        """Set up test fixtures"""
        self.preparer = SourceMapPreparer()

    def test_missing_filename(self):
        """Test handling of missing filename"""
        with pytest.raises(ValueError, match="filename"):
            self.preparer.prepare_source_map(
                filename="",
                line=1,
                column=0
            )

    def test_none_filename(self):
        """Test handling of None filename"""
        with pytest.raises(ValueError, match="filename"):
            self.preparer.prepare_source_map(
                filename=None,
                line=1,
                column=0
            )

    def test_invalid_line_zero(self):
        """Test handling of invalid line value (0)"""
        with pytest.raises(ValueError, match="line"):
            self.preparer.prepare_source_map(
                filename="test.js",
                line=0,  # Invalid: must be >= 1
                column=0
            )

    def test_invalid_line_negative(self):
        """Test handling of negative line value"""
        with pytest.raises(ValueError, match="line"):
            self.preparer.prepare_source_map(
                filename="test.js",
                line=-5,
                column=0
            )

    def test_invalid_column_negative(self):
        """Test handling of negative column value"""
        with pytest.raises(ValueError, match="column"):
            self.preparer.prepare_source_map(
                filename="test.js",
                line=1,
                column=-10
            )

    def test_filename_too_long(self):
        """Test handling of filename exceeding max length"""
        too_long_filename = "a" * 5000 + ".js"  # Exceeds 4096 limit
        with pytest.raises(ValueError, match="filename.*too long"):
            self.preparer.prepare_source_map(
                filename=too_long_filename,
                line=1,
                column=0
            )

    def test_invalid_source_root_type(self):
        """Test handling of invalid source_root type"""
        with pytest.raises(TypeError, match="source_root"):
            self.preparer.prepare_source_map(
                filename="test.js",
                line=1,
                column=0,
                source_root=123  # Should be string
            )

    def test_no_source_root(self):
        """Test that source_root is optional and defaults properly"""
        result = self.preparer.prepare_source_map(
            filename="test.js",
            line=1,
            column=0
        )

        assert result["metadata"]["source_root"] is None
        assert result["ready_for_resolution"] is True
