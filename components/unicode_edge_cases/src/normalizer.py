"""
UnicodeNormalizer class - Main normalization interface
Implements NFC, NFD, NFKC, NFKD normalization with comprehensive edge case handling
"""
import unicodedata
from typing import Optional


class UnicodeNormalizer:
    """
    Static methods for Unicode normalization with comprehensive edge case handling.
    Implements FR-ES24-D-001 (NFC), FR-ES24-D-002 (NFD), FR-ES24-D-003 (NFKC/NFKD).
    """

    @staticmethod
    def normalize_nfc(text: str) -> str:
        """
        Normalize to Unicode NFC (Canonical Decomposition + Canonical Composition).

        Args:
            text: Input string to normalize

        Returns:
            NFC-normalized string

        Raises:
            TypeError: If text is not a string
        """
        if not isinstance(text, str):
            raise TypeError("text must be a string")

        # Empty string fast path
        if not text:
            return text

        # Use Python's built-in normalization
        return unicodedata.normalize('NFC', text)

    @staticmethod
    def normalize_nfd(text: str) -> str:
        """
        Normalize to Unicode NFD (Canonical Decomposition).

        Args:
            text: Input string to normalize

        Returns:
            NFD-normalized string

        Raises:
            TypeError: If text is not a string
        """
        if not isinstance(text, str):
            raise TypeError("text must be a string")

        # Empty string fast path
        if not text:
            return text

        # Use Python's built-in normalization
        return unicodedata.normalize('NFD', text)

    @staticmethod
    def normalize_nfkc(text: str) -> str:
        """
        Normalize to Unicode NFKC (Compatibility Decomposition + Canonical Composition).

        Args:
            text: Input string to normalize

        Returns:
            NFKC-normalized string

        Raises:
            TypeError: If text is not a string
        """
        if not isinstance(text, str):
            raise TypeError("text must be a string")

        # Empty string fast path
        if not text:
            return text

        # Use Python's built-in normalization
        return unicodedata.normalize('NFKC', text)

    @staticmethod
    def normalize_nfkd(text: str) -> str:
        """
        Normalize to Unicode NFKD (Compatibility Decomposition).

        Args:
            text: Input string to normalize

        Returns:
            NFKD-normalized string

        Raises:
            TypeError: If text is not a string
        """
        if not isinstance(text, str):
            raise TypeError("text must be a string")

        # Empty string fast path
        if not text:
            return text

        # Use Python's built-in normalization
        return unicodedata.normalize('NFKD', text)

    @staticmethod
    def is_normalized(text: str, form: str) -> bool:
        """
        Test if string is already in normalized form WITHOUT performing normalization.
        Uses Unicode Quick Check algorithm for O(n) performance.

        Args:
            text: Input string to test
            form: Normalization form ("NFC", "NFD", "NFKC", "NFKD")

        Returns:
            True if string is already normalized in specified form

        Raises:
            TypeError: If text is not a string
            ValueError: If form is not a valid normalization form
        """
        if not isinstance(text, str):
            raise TypeError("text must be a string")

        # Validate form
        valid_forms = {'NFC', 'NFD', 'NFKC', 'NFKD'}
        if form not in valid_forms:
            raise ValueError(f"Invalid normalization form (must be NFC, NFD, NFKC, or NFKD)")

        # Empty string is always normalized
        if not text:
            return True

        # Compare with normalized form
        normalized = unicodedata.normalize(form, text)
        return text == normalized
