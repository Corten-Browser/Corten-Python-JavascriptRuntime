"""
Options validation for RelativeTimeFormat.

Validates style, numeric, and unit options.
"""

from .exceptions import RangeError


class RelativeTimeFormatOptions:
    """Validator for RelativeTimeFormat options."""

    # Valid time units (both singular and plural forms)
    VALID_UNITS = {
        'second', 'seconds',
        'minute', 'minutes',
        'hour', 'hours',
        'day', 'days',
        'week', 'weeks',
        'month', 'months',
        'quarter', 'quarters',
        'year', 'years'
    }

    # Unit normalization (plural -> singular)
    UNIT_NORMALIZATION = {
        'seconds': 'second',
        'minutes': 'minute',
        'hours': 'hour',
        'days': 'day',
        'weeks': 'week',
        'months': 'month',
        'quarters': 'quarter',
        'years': 'year'
    }

    def validate_style(self, style):
        """
        Validate and normalize style option.

        Args:
            style: Style value to validate

        Returns:
            Validated style ('long', 'short', or 'narrow')

        Raises:
            RangeError: If style is not one of the valid values
        """
        if style not in ['long', 'short', 'narrow']:
            raise RangeError(f"Invalid value for option 'style': {style}")
        return style

    def validate_numeric(self, numeric):
        """
        Validate and normalize numeric option.

        Args:
            numeric: Numeric value to validate

        Returns:
            Validated numeric ('always' or 'auto')

        Raises:
            RangeError: If numeric is not one of the valid values
        """
        if numeric not in ['always', 'auto']:
            raise RangeError(f"Invalid value for option 'numeric': {numeric}")
        return numeric

    def validate_unit(self, unit):
        """
        Validate and normalize time unit.

        Args:
            unit: Time unit to validate

        Returns:
            Normalized unit (singular form)

        Raises:
            RangeError: If unit is not valid
        """
        if not isinstance(unit, str):
            raise RangeError(f"Invalid unit argument: {unit}")

        unit_lower = unit.lower()

        if unit_lower not in self.VALID_UNITS:
            raise RangeError(f"Invalid unit argument: {unit}")

        # Normalize to singular form
        if unit_lower in self.UNIT_NORMALIZATION:
            return self.UNIT_NORMALIZATION[unit_lower]

        return unit_lower
