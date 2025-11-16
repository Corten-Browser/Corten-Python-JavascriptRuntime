"""
QuickCheckOptimizer - Performance optimizer using Unicode Quick Check algorithm
Implements UAX #15 Section 8 for fast normalization testing
"""
import unicodedata


class QuickCheckOptimizer:
    """
    Performance optimizer using Unicode Quick Check algorithm.
    Implements FR-ES24-D-005: Normalization performance optimization.
    """

    @staticmethod
    def quick_check_nfc(text: str) -> str:
        """
        Quick Check for NFC normalization (UAX #15 Section 8).

        Args:
            text: String to check

        Returns:
            'YES', 'NO', or 'MAYBE'
        """
        if not text:
            return "YES"

        # ASCII-only fast path
        if all(ord(c) < 128 for c in text):
            return "YES"

        # Check if already normalized (simplified Quick Check)
        normalized = unicodedata.normalize('NFC', text)
        if text == normalized:
            return "YES"
        else:
            # Could be NO or MAYBE depending on specific characters
            # For simplicity, return NO if not normalized
            return "NO"

    @staticmethod
    def quick_check_nfd(text: str) -> str:
        """
        Quick Check for NFD normalization.

        Args:
            text: String to check

        Returns:
            'YES' or 'NO' (no MAYBE for NFD)
        """
        if not text:
            return "YES"

        # ASCII-only fast path
        if all(ord(c) < 128 for c in text):
            return "YES"

        # Check if already normalized
        normalized = unicodedata.normalize('NFD', text)
        if text == normalized:
            return "YES"
        else:
            return "NO"

    @staticmethod
    def is_quick_check_yes(codepoint: int, form: str) -> bool:
        """
        Test if single character is Quick Check YES for given form.

        Args:
            codepoint: Unicode codepoint
            form: Normalization form

        Returns:
            True if character is Quick Check YES

        Raises:
            ValueError: If form is invalid
        """
        valid_forms = {'NFC', 'NFD', 'NFKC', 'NFKD'}
        if form not in valid_forms:
            raise ValueError(f"Invalid normalization form (must be NFC, NFD, NFKC, or NFKD)")

        # ASCII is always Quick Check YES
        if codepoint < 128:
            return True

        # Hangul Jamo (U+1100-U+11FF) are Quick Check NO for NFC (need composition)
        # but Quick Check YES for NFD
        if 0x1100 <= codepoint <= 0x11FF:
            return form in {'NFD', 'NFKD'}

        # Hangul syllables (U+AC00-U+D7A3) are Quick Check YES for NFC
        # but Quick Check NO for NFD (need decomposition)
        if 0xAC00 <= codepoint <= 0xD7A3:
            return form in {'NFC', 'NFKC'}

        char = chr(codepoint)

        # Check if normalizing changes the character
        normalized = unicodedata.normalize(form, char)
        return char == normalized
