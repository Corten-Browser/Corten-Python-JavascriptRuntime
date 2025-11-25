"""
Locale negotiation and BCP 47 locale support.
Handles locale parsing, canonicalization, and negotiation.
"""

import re


class LocaleSupport:
    """Locale negotiation and matching."""

    # Common available locales
    AVAILABLE_LOCALES = {
        'en-US', 'en-GB', 'de-DE', 'fr-FR', 'ja-JP', 'zh-CN', 'ar-SA', 'es-ES',
        'it-IT', 'pt-BR', 'ru-RU', 'ko-KR', 'hi-IN', 'th-TH', 'he-IL', 'ar-EG',
        'en', 'de', 'fr', 'ja', 'zh', 'ar', 'es', 'it', 'pt', 'ru', 'ko', 'hi', 'th', 'he'
    }


def negotiate_locale(requestedLocales, availableLocales, defaultLocale):
    """
    Perform BCP 47 locale negotiation.

    Args:
        requestedLocales: Array of requested locale identifiers
        availableLocales: Array of available locale identifiers
        defaultLocale: Fallback locale

    Returns:
        Best matching locale string
    """
    if not requestedLocales:
        return defaultLocale

    # Normalize inputs
    if isinstance(requestedLocales, str):
        requestedLocales = [requestedLocales]

    if not isinstance(availableLocales, (list, set)):
        availableLocales = LocaleSupport.AVAILABLE_LOCALES

    available_set = set(availableLocales)

    # Try exact match first
    for requested in requestedLocales:
        canonical = canonicalize_locale(requested)
        if canonical in available_set:
            return canonical

    # Try language-only fallback (e.g., en-US -> en)
    for requested in requestedLocales:
        parsed = parse_locale(requested)
        language_only = parsed['language']
        if language_only in available_set:
            return language_only

    # Try prefix matching (e.g., en-US matches en-GB if en not available)
    for requested in requestedLocales:
        parsed = parse_locale(requested)
        language = parsed['language']
        for available in available_set:
            if available.startswith(language + '-'):
                return available

    return defaultLocale


def parse_locale(locale):
    """
    Parse BCP 47 locale identifier.

    Args:
        locale: BCP 47 locale identifier string

    Returns:
        Dict with parsed components (language, script, region, variants, extensions)

    Raises:
        ValueError: If locale contains invalid characters or format
    """
    if not locale:
        return {
            'language': 'en',
            'script': None,
            'region': None,
            'variants': [],
            'extensions': {}
        }

    # Check for invalid characters (only alphanumeric and hyphens allowed)
    if not re.match(r'^[a-zA-Z0-9\-]+$', locale):
        raise ValueError(f"Invalid locale: {locale}")

    # BCP 47 pattern: language[-script][-region][-variants][-extensions]
    # Example: en-Latn-US-posix-u-ca-gregory
    parts = locale.split('-')

    result = {
        'language': parts[0].lower() if parts else 'en',
        'script': None,
        'region': None,
        'variants': [],
        'extensions': {}
    }

    if len(parts) < 2:
        return result

    idx = 1

    # Check for script (4 letters, first uppercase)
    if idx < len(parts) and len(parts[idx]) == 4 and parts[idx].isalpha():
        result['script'] = parts[idx].capitalize()
        idx += 1

    # Check for region (2 letters or 3 digits)
    if idx < len(parts):
        part = parts[idx]
        if (len(part) == 2 and part.isalpha()) or (len(part) == 3 and part.isdigit()):
            result['region'] = part.upper()
            idx += 1

    # Remaining parts are variants and extensions
    while idx < len(parts):
        part = parts[idx]

        # Extension starts with single letter
        if len(part) == 1:
            ext_key = part
            ext_values = []
            idx += 1
            while idx < len(parts) and len(parts[idx]) > 1:
                ext_values.append(parts[idx])
                idx += 1

            # Parse extension values into a dictionary (key-value pairs)
            ext_dict = {}
            i = 0
            while i < len(ext_values):
                # Key is 2-letter code
                if len(ext_values[i]) == 2:
                    key = ext_values[i]
                    # Collect values until next key or end
                    value_parts = []
                    i += 1
                    while i < len(ext_values) and len(ext_values[i]) > 2:
                        value_parts.append(ext_values[i])
                        i += 1
                    ext_dict[key] = '-'.join(value_parts) if value_parts else ''
                else:
                    i += 1

            # Consolidate duplicate extensions by merging dictionaries
            if ext_key in result['extensions']:
                if isinstance(result['extensions'][ext_key], dict):
                    result['extensions'][ext_key].update(ext_dict)
                else:
                    result['extensions'][ext_key] = ext_dict
            else:
                result['extensions'][ext_key] = ext_dict
        else:
            result['variants'].append(part)
            idx += 1

    return result


def canonicalize_locale(locale):
    """
    Canonicalize locale to standard form.

    Args:
        locale: Locale identifier string

    Returns:
        Canonicalized locale identifier

    Raises:
        ValueError: If locale is invalid
    """
    if not locale:
        return 'en-US'

    # Check for invalid characters before parsing
    if not re.match(r'^[a-zA-Z0-9\-]+$', locale):
        raise ValueError(f"Invalid locale: {locale}")

    # Parse and rebuild in canonical form
    parsed = parse_locale(locale)

    parts = [parsed['language'].lower()]

    if parsed['script']:
        parts.append(parsed['script'].capitalize())

    if parsed['region']:
        parts.append(parsed['region'].upper())

    for variant in parsed['variants']:
        parts.append(variant.lower())

    # Add extensions in sorted order
    for ext_key in sorted(parsed['extensions'].keys()):
        parts.append(ext_key)
        ext_value = parsed['extensions'][ext_key]
        if isinstance(ext_value, dict):
            # Sort extension keys and add them
            for key in sorted(ext_value.keys()):
                parts.append(key)
                if ext_value[key]:
                    parts.append(ext_value[key])
        else:
            # Legacy string format (shouldn't happen with new parsing)
            parts.append(ext_value)

    return '-'.join(parts)
