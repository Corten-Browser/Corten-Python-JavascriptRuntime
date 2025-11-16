"""
CombiningCharacterHandler - Internal handler for combining character sequences
Handles canonical combining class ordering per UAX #15
"""
import unicodedata


class CombiningCharacterHandler:
    """
    Internal handler for Unicode combining character sequences.
    Handles combining mark reordering according to Canonical Combining Class.
    """

    @staticmethod
    def reorder_combining_marks(text: str) -> str:
        """
        Reorder combining marks according to Canonical Combining Class (UAX #15 Section 4).

        Args:
            text: String with combining marks

        Returns:
            String with combining marks in canonical order
        """
        if not text:
            return text

        # Process each sequence of base + combining marks
        result = []
        i = 0
        while i < len(text):
            char = text[i]
            result.append(char)
            i += 1

            # If this is a starter, collect following combining marks
            if CombiningCharacterHandler.is_starter(ord(char)):
                combining_marks = []
                while i < len(text) and not CombiningCharacterHandler.is_starter(ord(text[i])):
                    combining_marks.append(text[i])
                    i += 1

                # Sort combining marks by CCC (stable sort preserves order for same CCC)
                if combining_marks:
                    combining_marks.sort(
                        key=lambda c: CombiningCharacterHandler.get_combining_class(ord(c))
                    )
                    result.extend(combining_marks)

        return ''.join(result)

    @staticmethod
    def is_starter(codepoint: int) -> bool:
        """
        Test if character is a starter (blocks combining mark reordering).

        Args:
            codepoint: Unicode codepoint

        Returns:
            True if character is a starter (CCC=0)
        """
        return unicodedata.combining(chr(codepoint)) == 0

    @staticmethod
    def get_combining_class(codepoint: int) -> int:
        """
        Get Canonical Combining Class property value.

        Args:
            codepoint: Unicode codepoint

        Returns:
            Canonical Combining Class (0-254)
        """
        return unicodedata.combining(chr(codepoint))
