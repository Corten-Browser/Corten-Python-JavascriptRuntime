"""UnicodeExtensionParser - Unicode locale extension parser."""

import re


class UnicodeExtensionParser:
    """Unicode locale extension (-u-) parser."""

    def parse_extension(self, extension):
        """
        Parse Unicode extension string into key-value pairs.

        Example: "ca-chinese-nu-hanidec" ->
                 {'ca': 'chinese', 'nu': 'hanidec'}
        """
        if not extension or not extension.strip():
            return {}

        # Normalize to lowercase for case-insensitive parsing
        extension = extension.lower()

        # Split by hyphens
        parts = extension.split('-')

        result = {}
        i = 0
        while i < len(parts):
            # Each key should be 2 characters
            if len(parts[i]) == 2:
                key = parts[i]
                # Collect values until next key
                values = []
                i += 1
                while i < len(parts) and len(parts[i]) != 2:
                    values.append(parts[i])
                    i += 1

                if values:
                    result[key] = '-'.join(values)
                else:
                    # Key without value is malformed
                    raise ValueError("Invalid Unicode extension")
            else:
                # Not a valid key, likely malformed
                raise ValueError("Invalid Unicode extension")

        return result

    def get_calendar(self, extensions):
        """Extract calendar from -u-ca- extension key."""
        return extensions.get('ca')

    def get_collation(self, extensions):
        """Extract collation from -u-co- extension key."""
        return extensions.get('co')

    def get_hour_cycle(self, extensions):
        """Extract hour cycle from -u-hc- extension key."""
        return extensions.get('hc')

    def get_case_first(self, extensions):
        """Extract case-first from -u-kf- extension key."""
        return extensions.get('kf')

    def get_numeric(self, extensions):
        """
        Extract numeric flag from -u-kn- extension key.

        Returns True if "true", False if "false", None if not present.
        """
        value = extensions.get('kn')
        if value == 'true':
            return True
        elif value == 'false':
            return False
        return None

    def get_numbering_system(self, extensions):
        """Extract numbering system from -u-nu- extension key."""
        return extensions.get('nu')
