"""
HangulNormalizer - Specialized handler for Korean Hangul syllable normalization
Implements algorithmic composition/decomposition per Unicode Standard
"""


class HangulNormalizer:
    """
    Specialized handler for Korean Hangul syllable normalization.
    Implements algorithmic composition and decomposition.
    """

    # Hangul constants per Unicode Standard
    SBASE = 0xAC00  # First syllable
    LBASE = 0x1100  # First leading Jamo
    VBASE = 0x1161  # First vowel Jamo
    TBASE = 0x11A7  # First trailing Jamo
    LCOUNT = 19     # Number of leading Jamo
    VCOUNT = 21     # Number of vowel Jamo
    TCOUNT = 28     # Number of trailing Jamo
    NCOUNT = VCOUNT * TCOUNT  # 588
    SCOUNT = LCOUNT * NCOUNT  # 11172

    @staticmethod
    def compose_jamo(text: str) -> str:
        """
        Compose Hangul Jamo to syllables using algorithmic composition.

        Args:
            text: String containing Hangul Jamo (U+1100-U+11FF)

        Returns:
            String with Jamo composed to syllables (U+AC00-U+D7A3)
        """
        if not text:
            return text

        result = []
        i = 0
        while i < len(text):
            char = text[i]
            cp = ord(char)

            # Check if this is a leading Jamo (L)
            if HangulNormalizer.LBASE <= cp < HangulNormalizer.LBASE + HangulNormalizer.LCOUNT:
                # Look ahead for vowel Jamo (V)
                if i + 1 < len(text):
                    next_cp = ord(text[i + 1])
                    if HangulNormalizer.VBASE <= next_cp < HangulNormalizer.VBASE + HangulNormalizer.VCOUNT:
                        # Compose L + V
                        l_index = cp - HangulNormalizer.LBASE
                        v_index = next_cp - HangulNormalizer.VBASE
                        lv_index = l_index * HangulNormalizer.NCOUNT + v_index * HangulNormalizer.TCOUNT
                        syllable = HangulNormalizer.SBASE + lv_index

                        # Look ahead for trailing Jamo (T)
                        if i + 2 < len(text):
                            trail_cp = ord(text[i + 2])
                            if HangulNormalizer.TBASE < trail_cp < HangulNormalizer.TBASE + HangulNormalizer.TCOUNT:
                                # Compose LV + T
                                t_index = trail_cp - HangulNormalizer.TBASE
                                syllable += t_index
                                result.append(chr(syllable))
                                i += 3
                                continue

                        # Just LV composition
                        result.append(chr(syllable))
                        i += 2
                        continue

            # Not composable, keep as-is
            result.append(char)
            i += 1

        return ''.join(result)

    @staticmethod
    def decompose_syllables(text: str) -> str:
        """
        Decompose Hangul syllables to Jamo using algorithmic decomposition.

        Args:
            text: String containing Hangul syllables (U+AC00-U+D7A3)

        Returns:
            String with syllables decomposed to Jamo
        """
        if not text:
            return text

        result = []
        for char in text:
            cp = ord(char)

            # Check if this is a Hangul syllable
            if HangulNormalizer.is_hangul_syllable(cp):
                # Decompose using algorithmic decomposition
                s_index = cp - HangulNormalizer.SBASE
                l_index = s_index // HangulNormalizer.NCOUNT
                v_index = (s_index % HangulNormalizer.NCOUNT) // HangulNormalizer.TCOUNT
                t_index = s_index % HangulNormalizer.TCOUNT

                # Add L and V
                result.append(chr(HangulNormalizer.LBASE + l_index))
                result.append(chr(HangulNormalizer.VBASE + v_index))

                # Add T if present (TIndex > 0)
                if t_index > 0:
                    result.append(chr(HangulNormalizer.TBASE + t_index))
            else:
                # Not a Hangul syllable, keep as-is
                result.append(char)

        return ''.join(result)

    @staticmethod
    def is_hangul_syllable(codepoint: int) -> bool:
        """
        Test if character is a precomposed Hangul syllable.

        Args:
            codepoint: Unicode codepoint

        Returns:
            True if codepoint is Hangul syllable (U+AC00-U+D7A3)
        """
        return HangulNormalizer.SBASE <= codepoint < HangulNormalizer.SBASE + HangulNormalizer.SCOUNT
