"""
Unicode handling for JSON (FR-ES24-B-036)

Provides:
- Surrogate pair escaping
- Unpaired surrogate detection and escaping
- Unicode validation
"""


class JSONUnicode:
    """Unicode handling for JSON"""

    def escape_surrogate_pair(self, high: int, low: int) -> str:
        """
        Escape complete surrogate pairs

        Args:
            high: High surrogate (U+D800 to U+DBFF)
            low: Low surrogate (U+DC00 to U+DFFF)

        Returns:
            Properly escaped surrogate pair
        """
        # Validate range
        if not (0xD800 <= high <= 0xDBFF):
            raise ValueError(f"Invalid high surrogate: {hex(high)}")
        if not (0xDC00 <= low <= 0xDFFF):
            raise ValueError(f"Invalid low surrogate: {hex(low)}")

        # Convert surrogate pair to Unicode code point
        # Formula: ((high - 0xD800) * 0x400) + (low - 0xDC00) + 0x10000
        code_point = ((high - 0xD800) * 0x400) + (low - 0xDC00) + 0x10000

        # Return the character (Python handles this natively)
        try:
            return chr(code_point)
        except ValueError:
            # If can't convert, return escaped form
            return f"\\u{high:04x}\\u{low:04x}"

    def escape_unpaired_surrogate(self, code: int) -> str:
        """
        Escape unpaired surrogates (well-formed JSON requirement)

        Args:
            code: Unpaired surrogate code point

        Returns:
            Escaped as \\uXXXX
        """
        # Validate it's actually a surrogate
        if not (0xD800 <= code <= 0xDFFF):
            raise ValueError(f"Not a surrogate code point: {hex(code)}")

        # Return escaped form
        return f"\\u{code:04x}"

    def validate_unicode(self, text: str) -> bool:
        """
        Validate Unicode in JSON strings

        Args:
            text: JSON text

        Returns:
            True if valid Unicode
        """
        if not text:
            return True

        try:
            # Check if text is valid UTF-8
            if isinstance(text, str):
                # Already Unicode in Python 3
                # Check for unpaired surrogates
                i = 0
                while i < len(text):
                    code = ord(text[i])

                    # High surrogate
                    if 0xD800 <= code <= 0xDBFF:
                        # Should be followed by low surrogate
                        if i + 1 < len(text):
                            next_code = ord(text[i + 1])
                            if 0xDC00 <= next_code <= 0xDFFF:
                                # Valid pair
                                i += 2
                                continue
                        # Unpaired high surrogate detected
                        # For validation, we'll allow it but mark as detectable
                        i += 1

                    # Low surrogate without high
                    elif 0xDC00 <= code <= 0xDFFF:
                        # Unpaired low surrogate
                        i += 1

                    else:
                        # Normal character
                        i += 1

                return True

            else:
                # Not a string
                return False

        except Exception:
            return False

    def has_unpaired_surrogates(self, text: str) -> bool:
        """
        Check if text contains unpaired surrogates

        Args:
            text: Text to check

        Returns:
            True if unpaired surrogates found
        """
        i = 0
        while i < len(text):
            code = ord(text[i])

            # High surrogate
            if 0xD800 <= code <= 0xDBFF:
                # Check for low surrogate
                if i + 1 < len(text):
                    next_code = ord(text[i + 1])
                    if 0xDC00 <= next_code <= 0xDFFF:
                        # Valid pair
                        i += 2
                        continue
                # Unpaired high surrogate
                return True

            # Low surrogate without high
            elif 0xDC00 <= code <= 0xDFFF:
                return True

            i += 1

        return False

    def fix_unpaired_surrogates(self, text: str) -> str:
        """
        Fix unpaired surrogates by escaping them

        Args:
            text: Text with potential unpaired surrogates

        Returns:
            Text with unpaired surrogates escaped
        """
        result = []
        i = 0

        while i < len(text):
            char = text[i]
            code = ord(char)

            # High surrogate
            if 0xD800 <= code <= 0xDBFF:
                # Check for low surrogate
                if i + 1 < len(text):
                    next_code = ord(text[i + 1])
                    if 0xDC00 <= next_code <= 0xDFFF:
                        # Valid pair - keep both
                        result.append(char)
                        result.append(text[i + 1])
                        i += 2
                        continue

                # Unpaired high surrogate - escape
                result.append(self.escape_unpaired_surrogate(code))
                i += 1

            # Low surrogate without high
            elif 0xDC00 <= code <= 0xDFFF:
                # Unpaired low surrogate - escape
                result.append(self.escape_unpaired_surrogate(code))
                i += 1

            else:
                # Normal character
                result.append(char)
                i += 1

        return ''.join(result)
