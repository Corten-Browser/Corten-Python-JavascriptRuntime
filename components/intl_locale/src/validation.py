"""LocaleValidation - Locale validation utilities."""

import re


class LocaleValidation:
    """Locale validation utilities."""

    # Valid calendar types from Unicode CLDR
    VALID_CALENDARS = {
        'gregory', 'buddhist', 'chinese', 'coptic', 'dangi',
        'ethioaa', 'ethiopic', 'hebrew', 'indian', 'islamic',
        'islamic-civil', 'islamic-rgsa', 'islamic-tbla',
        'islamic-umalqura', 'iso8601', 'japanese', 'persian', 'roc'
    }

    # Valid numbering systems from Unicode CLDR
    VALID_NUMBERING_SYSTEMS = {
        'arab', 'arabext', 'bali', 'beng', 'deva', 'fullwide',
        'gujr', 'guru', 'hanidec', 'khmr', 'knda', 'laoo', 'latn',
        'limb', 'mlym', 'mong', 'mymr', 'orya', 'tamldec', 'telu',
        'thai', 'tibt'
    }

    def validate_language(self, language):
        """
        Validate language subtag (ISO 639).

        Language must be 2-3 lowercase letters.
        """
        if not language:
            return False
        if not isinstance(language, str):
            return False
        # Must be 2-3 lowercase letters
        return bool(re.match(r'^[a-z]{2,3}$', language))

    def validate_script(self, script):
        """
        Validate script subtag (ISO 15924).

        Script must be 4 letters in title case (e.g., Latn, Hans).
        """
        if not script:
            return False
        if not isinstance(script, str):
            return False
        # Must be 4 letters, first uppercase, rest lowercase
        return bool(re.match(r'^[A-Z][a-z]{3}$', script))

    def validate_region(self, region):
        """
        Validate region subtag.

        Region must be either:
        - 2 uppercase letters (ISO 3166-1 alpha-2)
        - 3 digits (UN M.49)
        """
        if not region:
            return False
        if not isinstance(region, str):
            return False
        # Must be 2 uppercase letters OR 3 digits
        return bool(re.match(r'^([A-Z]{2}|[0-9]{3})$', region))

    def validate_calendar(self, calendar):
        """
        Validate calendar identifier against Unicode CLDR.

        Calendar must be a valid CLDR calendar type.
        """
        if not calendar:
            return False
        if not isinstance(calendar, str):
            return False
        return calendar in self.VALID_CALENDARS

    def validate_numbering_system(self, numbering_system):
        """
        Validate numbering system identifier against Unicode CLDR.

        Numbering system must be a valid CLDR numbering system.
        """
        if not numbering_system:
            return False
        if not isinstance(numbering_system, str):
            return False
        return numbering_system in self.VALID_NUMBERING_SYSTEMS
