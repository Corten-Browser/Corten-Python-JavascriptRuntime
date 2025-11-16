"""
Unicode Collation Algorithm (UCA) implementation.

FR-ES24-C-004: Sensitivity option
FR-ES24-C-005: Numeric option
FR-ES24-C-006: CaseFirst option
FR-ES24-C-007: IgnorePunctuation option
"""

import unicodedata
import re


def normalize_string(s):
    """
    Normalize string to NFC form for consistent comparison.

    Args:
        s: String to normalize

    Returns:
        str: Normalized string
    """
    if not s:
        return s
    return unicodedata.normalize('NFC', s)


def compare_strings(string1, string2, sensitivity='variant', numeric=False,
                   case_first='false', ignore_punctuation=False, locale='en-US'):
    """
    Compare two strings using Unicode Collation Algorithm.

    Args:
        string1: First string
        string2: Second string
        sensitivity: 'base', 'accent', 'case', or 'variant'
        numeric: Whether to use numeric collation
        case_first: 'upper', 'lower', or 'false'
        ignore_punctuation: Whether to ignore punctuation
        locale: Locale for comparison

    Returns:
        int: Negative if string1 < string2, 0 if equal, positive if string1 > string2
    """
    # Normalize strings
    s1 = normalize_string(string1)
    s2 = normalize_string(string2)

    # Remove punctuation if requested
    if ignore_punctuation:
        s1 = remove_punctuation(s1)
        s2 = remove_punctuation(s2)

    # Numeric collation
    if numeric:
        return _compare_numeric(s1, s2, sensitivity, case_first)

    # Apply sensitivity levels
    if sensitivity == 'base':
        # Only base differences matter (ignore case and accents)
        s1_normalized = _normalize_base(s1)
        s2_normalized = _normalize_base(s2)
    elif sensitivity == 'accent':
        # Base and accent differences matter (ignore case)
        s1_normalized = _normalize_accent(s1)
        s2_normalized = _normalize_accent(s2)
    elif sensitivity == 'case':
        # Base, accent, and case differences matter
        s1_normalized = _normalize_case(s1)
        s2_normalized = _normalize_case(s2)
    else:  # variant
        # All differences matter
        s1_normalized = s1
        s2_normalized = s2

    # Apply caseFirst if specified and sensitivity allows case differences
    if case_first != 'false' and sensitivity in ['case', 'variant']:
        return _compare_with_case_first(s1_normalized, s2_normalized, case_first)

    # Standard comparison
    if s1_normalized < s2_normalized:
        return -1
    elif s1_normalized > s2_normalized:
        return 1
    else:
        return 0


def _normalize_base(s):
    """Normalize for base sensitivity (remove accents and case)."""
    # Decompose to NFD, remove combining marks, convert to lowercase
    nfd = unicodedata.normalize('NFD', s)
    without_accents = ''.join(
        c for c in nfd
        if unicodedata.category(c) != 'Mn'  # Mn = Nonspacing_Mark
    )
    return without_accents.lower()


def _normalize_accent(s):
    """Normalize for accent sensitivity (keep accents, remove case)."""
    # Just lowercase, keep accents
    return s.lower()


def _normalize_case(s):
    """Normalize for case sensitivity (keep accents and case)."""
    # For case sensitivity, we keep both accents and case
    # Just normalize to consistent form
    return s


def _compare_with_case_first(s1, s2, case_first):
    """Compare with caseFirst preference."""
    # First compare ignoring case
    s1_lower = s1.lower()
    s2_lower = s2.lower()

    if s1_lower != s2_lower:
        # Different base strings
        if s1_lower < s2_lower:
            return -1
        else:
            return 1

    # Same base string, apply case ordering
    if s1 == s2:
        return 0

    # Check case differences
    has_upper_s1 = any(c.isupper() for c in s1)
    has_upper_s2 = any(c.isupper() for c in s2)

    if has_upper_s1 != has_upper_s2:
        if case_first == 'upper':
            # Uppercase first
            return -1 if has_upper_s1 else 1
        else:  # lower
            # Lowercase first
            return 1 if has_upper_s1 else -1

    # Fall back to standard comparison
    if s1 < s2:
        return -1
    elif s1 > s2:
        return 1
    else:
        return 0


def _compare_numeric(s1, s2, sensitivity, case_first):
    """Compare strings with numeric collation."""
    parts1 = extract_numeric_parts(s1)
    parts2 = extract_numeric_parts(s2)

    # Compare part by part
    for i in range(min(len(parts1), len(parts2))):
        is_num1, val1 = parts1[i]
        is_num2, val2 = parts2[i]

        if is_num1 and is_num2:
            # Both numeric, compare as numbers
            if val1 < val2:
                return -1
            elif val1 > val2:
                return 1
        elif is_num1:
            # Numbers come before text
            return -1
        elif is_num2:
            # Numbers come before text
            return 1
        else:
            # Both text, compare according to sensitivity
            result = compare_strings(val1, val2, sensitivity=sensitivity,
                                    numeric=False, case_first=case_first,
                                    ignore_punctuation=False)
            if result != 0:
                return result

    # If all parts equal, compare lengths
    if len(parts1) < len(parts2):
        return -1
    elif len(parts1) > len(parts2):
        return 1
    else:
        return 0


def extract_numeric_parts(s):
    """
    Extract numeric parts from string for numeric collation.

    Args:
        s: String to parse

    Returns:
        list: List of (is_numeric, value) tuples
    """
    if not s:
        return []

    parts = []
    # Split string into numeric and non-numeric parts
    pattern = r'(\d+)'
    tokens = re.split(pattern, s)

    for token in tokens:
        if not token:
            continue
        if token.isdigit():
            # Numeric part - convert to int for proper comparison
            parts.append((True, int(token)))
        else:
            # Text part
            parts.append((False, token))

    return parts


def remove_punctuation(s):
    """
    Remove punctuation from string for ignorePunctuation option.

    Args:
        s: String to process

    Returns:
        str: String without punctuation
    """
    if not s:
        return s

    # Remove all punctuation characters
    result = []
    for char in s:
        category = unicodedata.category(char)
        # Keep if not punctuation (P* categories)
        if not category.startswith('P'):
            result.append(char)

    return ''.join(result)
