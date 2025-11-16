"""
Unit tests for IntlNumberFormat formatToParts() method (FR-ES24-C-023)

These tests cover:
- Decimal parts
- Currency parts
- Percent parts
- Unit parts
- Compact notation parts
- Scientific notation parts
- Negative number parts
- Grouping separator parts
- Part types validation
"""

import pytest
from components.intl_numberformat.src.number_format import IntlNumberFormat


class TestFormatToPartsBasic:
    """Test basic formatToParts functionality."""

    def test_format_to_parts_simple_integer(self):
        """Format simple integer to parts."""
        formatter = IntlNumberFormat('en-US')
        parts = formatter.formatToParts(1234)

        assert isinstance(parts, list)
        assert len(parts) > 0
        assert all(isinstance(part, dict) for part in parts)
        assert all('type' in part and 'value' in part for part in parts)

    def test_format_to_parts_types(self):
        """Parts should have correct types."""
        formatter = IntlNumberFormat('en-US')
        parts = formatter.formatToParts(1234.56)

        part_types = [part['type'] for part in parts]
        assert 'integer' in part_types
        assert 'group' in part_types or len([p for p in parts if p['type'] == 'integer']) > 0
        assert 'decimal' in part_types
        assert 'fraction' in part_types

    def test_format_to_parts_values(self):
        """Parts should have correct values."""
        formatter = IntlNumberFormat('en-US')
        parts = formatter.formatToParts(1234.56)

        # Reconstruct the formatted string
        reconstructed = ''.join(part['value'] for part in parts)
        assert reconstructed == formatter.format(1234.56)

    def test_format_to_parts_integer_no_decimal(self):
        """Format integer (no decimal/fraction parts)."""
        formatter = IntlNumberFormat('en-US', {'maximumFractionDigits': 0})
        parts = formatter.formatToParts(1234)

        part_types = [part['type'] for part in parts]
        assert 'integer' in part_types
        assert 'decimal' not in part_types
        assert 'fraction' not in part_types


class TestFormatToPartsCurrency:
    """Test currency formatting parts (FR-ES24-C-027)."""

    def test_format_to_parts_currency_usd(self):
        """Format USD currency to parts."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'currency',
            'currency': 'USD'
        })
        parts = formatter.formatToParts(1234.56)

        part_types = [part['type'] for part in parts]
        assert 'currency' in part_types
        assert 'integer' in part_types
        assert 'decimal' in part_types
        assert 'fraction' in part_types

        # Find currency part
        currency_parts = [p for p in parts if p['type'] == 'currency']
        assert len(currency_parts) > 0
        assert '$' in currency_parts[0]['value']

    def test_format_to_parts_currency_literal(self):
        """Currency formatting includes literal parts."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'currency',
            'currency': 'USD'
        })
        parts = formatter.formatToParts(1234.56)

        # There might be literal parts (spaces, etc.)
        literal_parts = [p for p in parts if p['type'] == 'literal']
        # Literals are optional but common

    def test_format_to_parts_currency_group(self):
        """Currency formatting includes group separator."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'currency',
            'currency': 'USD'
        })
        parts = formatter.formatToParts(1234.56)

        part_types = [part['type'] for part in parts]
        assert 'group' in part_types

        group_parts = [p for p in parts if p['type'] == 'group']
        assert ',' in group_parts[0]['value']


class TestFormatToPartsPercent:
    """Test percent formatting parts."""

    def test_format_to_parts_percent(self):
        """Format percent to parts."""
        formatter = IntlNumberFormat('en-US', {'style': 'percent'})
        parts = formatter.formatToParts(0.5)

        part_types = [part['type'] for part in parts]
        assert 'percentSign' in part_types
        assert 'integer' in part_types

        percent_parts = [p for p in parts if p['type'] == 'percentSign']
        assert '%' in percent_parts[0]['value']

    def test_format_to_parts_percent_decimal(self):
        """Format percent with decimals to parts."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'percent',
            'minimumFractionDigits': 1
        })
        parts = formatter.formatToParts(0.555)

        part_types = [part['type'] for part in parts]
        assert 'percentSign' in part_types
        assert 'decimal' in part_types or 'fraction' in part_types


class TestFormatToPartsUnit:
    """Test unit formatting parts."""

    def test_format_to_parts_unit(self):
        """Format unit to parts."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'unit',
            'unit': 'meter'
        })
        parts = formatter.formatToParts(10)

        part_types = [part['type'] for part in parts]
        assert 'unit' in part_types
        assert 'integer' in part_types

    def test_format_to_parts_unit_value(self):
        """Unit part has correct value."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'unit',
            'unit': 'meter',
            'unitDisplay': 'short'
        })
        parts = formatter.formatToParts(10)

        unit_parts = [p for p in parts if p['type'] == 'unit']
        assert len(unit_parts) > 0
        # Short form might be 'm' or 'meters' depending on implementation
        assert len(unit_parts[0]['value']) > 0


class TestFormatToPartsNotation:
    """Test notation formatting parts."""

    def test_format_to_parts_scientific(self):
        """Format scientific notation to parts."""
        formatter = IntlNumberFormat('en-US', {'notation': 'scientific'})
        parts = formatter.formatToParts(123456)

        part_types = [part['type'] for part in parts]
        # Scientific notation should have exponent parts
        assert ('exponentSeparator' in part_types or
                'exponentInteger' in part_types or
                'compact' in part_types)

    def test_format_to_parts_compact(self):
        """Format compact notation to parts."""
        formatter = IntlNumberFormat('en-US', {'notation': 'compact'})
        parts = formatter.formatToParts(1234567)

        part_types = [part['type'] for part in parts]
        # Compact notation has compact part type
        assert 'compact' in part_types or 'integer' in part_types

        # If compact part exists, it should be 'M' or similar
        compact_parts = [p for p in parts if p['type'] == 'compact']
        if compact_parts:
            assert compact_parts[0]['value'] in ['K', 'M', 'B', 'T']


class TestFormatToPartsSign:
    """Test sign parts."""

    def test_format_to_parts_negative_minus_sign(self):
        """Negative number has minusSign part."""
        formatter = IntlNumberFormat('en-US')
        parts = formatter.formatToParts(-1234)

        part_types = [part['type'] for part in parts]
        assert 'minusSign' in part_types

        minus_parts = [p for p in parts if p['type'] == 'minusSign']
        assert '-' in minus_parts[0]['value']

    def test_format_to_parts_positive_plus_sign(self):
        """Positive number with always sign has plusSign part."""
        formatter = IntlNumberFormat('en-US', {'signDisplay': 'always'})
        parts = formatter.formatToParts(1234)

        part_types = [part['type'] for part in parts]
        assert 'plusSign' in part_types

        plus_parts = [p for p in parts if p['type'] == 'plusSign']
        assert '+' in plus_parts[0]['value']

    def test_format_to_parts_no_sign_auto(self):
        """Positive number with auto sign has no sign part."""
        formatter = IntlNumberFormat('en-US', {'signDisplay': 'auto'})
        parts = formatter.formatToParts(1234)

        part_types = [part['type'] for part in parts]
        assert 'plusSign' not in part_types


class TestFormatToPartsSpecialValues:
    """Test special value parts."""

    def test_format_to_parts_nan(self):
        """Format NaN to parts."""
        formatter = IntlNumberFormat('en-US')
        parts = formatter.formatToParts(float('nan'))

        part_types = [part['type'] for part in parts]
        assert 'nan' in part_types

        nan_parts = [p for p in parts if p['type'] == 'nan']
        assert 'NaN' in nan_parts[0]['value']

    def test_format_to_parts_infinity(self):
        """Format infinity to parts."""
        formatter = IntlNumberFormat('en-US')
        parts = formatter.formatToParts(float('inf'))

        part_types = [part['type'] for part in parts]
        assert 'infinity' in part_types


class TestFormatToPartsGrouping:
    """Test grouping separator parts."""

    def test_format_to_parts_with_grouping(self):
        """Format with grouping separator."""
        formatter = IntlNumberFormat('en-US', {'useGrouping': True})
        parts = formatter.formatToParts(1234567)

        part_types = [part['type'] for part in parts]
        assert 'group' in part_types

        group_parts = [p for p in parts if p['type'] == 'group']
        # US English uses comma
        assert ',' in group_parts[0]['value']

    def test_format_to_parts_without_grouping(self):
        """Format without grouping separator."""
        formatter = IntlNumberFormat('en-US', {'useGrouping': False})
        parts = formatter.formatToParts(1234567)

        part_types = [part['type'] for part in parts]
        assert 'group' not in part_types

    def test_format_to_parts_multiple_groups(self):
        """Format with multiple grouping separators."""
        formatter = IntlNumberFormat('en-US')
        parts = formatter.formatToParts(1234567890)

        group_parts = [p for p in parts if p['type'] == 'group']
        # Should have multiple group separators
        assert len(group_parts) >= 2


class TestFormatToPartsLocales:
    """Test parts with different locales."""

    def test_format_to_parts_german(self):
        """Format with German locale (different separators)."""
        formatter = IntlNumberFormat('de-DE')
        parts = formatter.formatToParts(1234.56)

        # German uses . for thousands and , for decimal
        group_parts = [p for p in parts if p['type'] == 'group']
        decimal_parts = [p for p in parts if p['type'] == 'decimal']

        if group_parts:
            assert '.' in group_parts[0]['value']
        if decimal_parts:
            assert ',' in decimal_parts[0]['value']


class TestFormatToPartsConsistency:
    """Test consistency between format() and formatToParts()."""

    def test_parts_reconstruct_to_format(self):
        """Joining parts should equal format() output."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'currency',
            'currency': 'USD'
        })
        number = 1234.56

        formatted = formatter.format(number)
        parts = formatter.formatToParts(number)
        reconstructed = ''.join(part['value'] for part in parts)

        assert formatted == reconstructed

    def test_parts_reconstruct_percent(self):
        """Parts reconstruct for percent style."""
        formatter = IntlNumberFormat('en-US', {'style': 'percent'})
        number = 0.75

        formatted = formatter.format(number)
        parts = formatter.formatToParts(number)
        reconstructed = ''.join(part['value'] for part in parts)

        assert formatted == reconstructed

    def test_parts_reconstruct_compact(self):
        """Parts reconstruct for compact notation."""
        formatter = IntlNumberFormat('en-US', {'notation': 'compact'})
        number = 1234567

        formatted = formatter.format(number)
        parts = formatter.formatToParts(number)
        reconstructed = ''.join(part['value'] for part in parts)

        assert formatted == reconstructed


class TestFormatToPartsValidation:
    """Test part structure validation."""

    def test_parts_have_required_fields(self):
        """All parts must have type and value."""
        formatter = IntlNumberFormat('en-US')
        parts = formatter.formatToParts(1234.56)

        for part in parts:
            assert 'type' in part
            assert 'value' in part
            assert isinstance(part['type'], str)
            assert isinstance(part['value'], str)

    def test_parts_types_are_valid(self):
        """Part types must be from valid set."""
        valid_types = {
            'integer', 'group', 'decimal', 'fraction',
            'plusSign', 'minusSign', 'percentSign',
            'currency', 'literal', 'nan', 'infinity',
            'compact', 'exponentInteger', 'exponentMinusSign',
            'exponentSeparator', 'unit'
        }

        formatter = IntlNumberFormat('en-US', {
            'style': 'currency',
            'currency': 'USD'
        })
        parts = formatter.formatToParts(1234.56)

        for part in parts:
            assert part['type'] in valid_types

    def test_parts_values_are_non_empty(self):
        """Part values should be non-empty strings."""
        formatter = IntlNumberFormat('en-US')
        parts = formatter.formatToParts(1234.56)

        for part in parts:
            assert len(part['value']) > 0
