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
    """
    if not locale:
        return {
            'language': 'en',
            'script': None,
            'region': None,
            'variants': [],
            'extensions': {}
        }

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
            result['extensions'][ext_key] = '-'.join(ext_values)
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
    """
    if not locale:
        return 'en-US'

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
    for key in sorted(parsed['extensions'].keys()):
        parts.append(key)
        parts.append(parsed['extensions'][key])

    return '-'.join(parts)
