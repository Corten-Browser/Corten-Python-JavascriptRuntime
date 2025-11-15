"""
RelativeTimeFormatter - Core formatting implementation.

Handles formatting logic for different styles, numeric modes, and locales.
"""

import re


class RelativeTimeFormatter:
    """Core formatter for relative time strings."""

    # Locale-specific templates for numeric formatting
    # Format: {locale: {unit: {style: (past_template, future_template)}}}
    NUMERIC_TEMPLATES = {
        'en-US': {
            'second': {
                'long': ('{n} second ago', 'in {n} second', '{n} seconds ago', 'in {n} seconds'),
                'short': ('{n} sec. ago', 'in {n} sec.', '{n} sec. ago', 'in {n} sec.'),
                'narrow': ('{n}s ago', 'in {n}s', '{n}s ago', 'in {n}s')
            },
            'minute': {
                'long': ('{n} minute ago', 'in {n} minute', '{n} minutes ago', 'in {n} minutes'),
                'short': ('{n} min. ago', 'in {n} min.', '{n} min. ago', 'in {n} min.'),
                'narrow': ('{n}m ago', 'in {n}m', '{n}m ago', 'in {n}m')
            },
            'hour': {
                'long': ('{n} hour ago', 'in {n} hour', '{n} hours ago', 'in {n} hours'),
                'short': ('{n} hr. ago', 'in {n} hr.', '{n} hr. ago', 'in {n} hr.'),
                'narrow': ('{n}h ago', 'in {n}h', '{n}h ago', 'in {n}h')
            },
            'day': {
                'long': ('{n} day ago', 'in {n} day', '{n} days ago', 'in {n} days'),
                'short': ('{n} day ago', 'in {n} day', '{n} days ago', 'in {n} days'),
                'narrow': ('{n}d ago', 'in {n}d', '{n}d ago', 'in {n}d')
            },
            'week': {
                'long': ('{n} week ago', 'in {n} week', '{n} weeks ago', 'in {n} weeks'),
                'short': ('{n} wk. ago', 'in {n} wk.', '{n} wk. ago', 'in {n} wk.'),
                'narrow': ('{n}w ago', 'in {n}w', '{n}w ago', 'in {n}w')
            },
            'month': {
                'long': ('{n} month ago', 'in {n} month', '{n} months ago', 'in {n} months'),
                'short': ('{n} mo. ago', 'in {n} mo.', '{n} mo. ago', 'in {n} mo.'),
                'narrow': ('{n}mo ago', 'in {n}mo', '{n}mo ago', 'in {n}mo')
            },
            'quarter': {
                'long': ('{n} quarter ago', 'in {n} quarter', '{n} quarters ago', 'in {n} quarters'),
                'short': ('{n} qtr. ago', 'in {n} qtr.', '{n} qtr. ago', 'in {n} qtr.'),
                'narrow': ('{n}q ago', 'in {n}q', '{n}q ago', 'in {n}q')
            },
            'year': {
                'long': ('{n} year ago', 'in {n} year', '{n} years ago', 'in {n} years'),
                'short': ('{n} yr. ago', 'in {n} yr.', '{n} yr. ago', 'in {n} yr.'),
                'narrow': ('{n}y ago', 'in {n}y', '{n}y ago', 'in {n}y')
            }
        },
        'es-ES': {
            'day': {
                'long': ('hace {n} día', 'dentro de {n} día', 'hace {n} días', 'dentro de {n} días'),
                'short': ('hace {n} d', 'en {n} d', 'hace {n} d', 'en {n} d'),
                'narrow': ('-{n} d', '+{n} d', '-{n} d', '+{n} d')
            },
            'hour': {
                'long': ('hace {n} hora', 'dentro de {n} hora', 'hace {n} horas', 'dentro de {n} horas'),
                'short': ('hace {n} h', 'en {n} h', 'hace {n} h', 'en {n} h'),
                'narrow': ('-{n}h', '+{n}h', '-{n}h', '+{n}h')
            }
        },
        'fr-FR': {
            'day': {
                'long': ('il y a {n} jour', 'dans {n} jour', 'il y a {n} jours', 'dans {n} jours'),
                'short': ('il y a {n} j', 'dans {n} j', 'il y a {n} j', 'dans {n} j'),
                'narrow': ('-{n} j', '+{n} j', '-{n} j', '+{n} j')
            },
            'hour': {
                'long': ('il y a {n} heure', 'dans {n} heure', 'il y a {n} heures', 'dans {n} heures'),
                'short': ('il y a {n} h', 'dans {n} h', 'il y a {n} h', 'dans {n} h'),
                'narrow': ('-{n}h', '+{n}h', '-{n}h', '+{n}h')
            }
        }
    }

    # Auto mode special words
    AUTO_WORDS = {
        'en-US': {
            'day': {-1: 'yesterday', 0: 'today', 1: 'tomorrow'},
            'week': {-1: 'last week', 1: 'next week'},
            'month': {-1: 'last month', 1: 'next month'},
            'quarter': {-1: 'last quarter', 1: 'next quarter'},
            'year': {-1: 'last year', 1: 'next year'}
        },
        'es-ES': {
            'day': {-1: 'ayer', 0: 'hoy', 1: 'mañana'}
        },
        'fr-FR': {
            'day': {-1: 'hier', 0: 'aujourd\'hui', 1: 'demain'}
        }
    }

    def format_numeric(self, value, unit, locale, style):
        """
        Format using numeric mode (always shows number).

        Args:
            value: Numeric value (positive=future, negative=past)
            unit: Time unit (normalized to singular)
            locale: BCP 47 locale
            style: Formatting style (long, short, narrow)

        Returns:
            Formatted string (always numeric)
        """
        # Get base locale (e.g., 'en' from 'en-US')
        base_locale = locale.split('-')[0]

        # Get template for locale and unit
        templates = self._get_templates(locale, unit, style)

        # Format number
        abs_value = abs(value)
        formatted_number = self._format_number(abs_value, locale)

        # Select template based on value sign and plural
        if value < 0:
            # Past
            template = templates[0] if abs_value == 1 else templates[2]
        elif value > 0:
            # Future
            template = templates[1] if abs_value == 1 else templates[3]
        else:
            # Zero: use future plural form
            template = templates[3]

        # Replace {n} with formatted number
        result = template.replace('{n}', formatted_number)

        return result

    def format_auto(self, value, unit, locale, style):
        """
        Format using auto mode (uses words when available).

        Args:
            value: Numeric value
            unit: Time unit
            locale: BCP 47 locale
            style: Formatting style

        Returns:
            Formatted string (may use words like "yesterday")
        """
        # Try to get special word
        special_word = self._get_auto_word(value, unit, locale)
        if special_word:
            return special_word

        # Fall back to numeric
        return self.format_numeric(value, unit, locale, style)

    def split_to_parts(self, formatted_string, value):
        """
        Split formatted string into parts (literal and integer).

        Args:
            formatted_string: Formatted relative time string
            value: Original numeric value

        Returns:
            Array of {type, value} objects
        """
        # Find numeric part in string
        abs_value = abs(value)
        number_str = self._format_number(abs_value, 'en-US')  # Locale doesn't matter for splitting

        # Look for number in string (may have thousand separators)
        # For simple case, look for digits
        number_pattern = r'\d+(?:[,\.]\d+)*'
        match = re.search(number_pattern, formatted_string)

        if match:
            # Split into before, number, after
            start = match.start()
            end = match.end()

            parts = []

            # Before number
            if start > 0:
                parts.append({
                    'type': 'literal',
                    'value': formatted_string[:start]
                })

            # Number
            parts.append({
                'type': 'integer',
                'value': formatted_string[start:end]
            })

            # After number
            if end < len(formatted_string):
                parts.append({
                    'type': 'literal',
                    'value': formatted_string[end:]
                })

            return parts
        else:
            # No number found (e.g., "yesterday")
            return [{
                'type': 'literal',
                'value': formatted_string
            }]

    def _get_templates(self, locale, unit, style):
        """
        Get templates for locale, unit, and style.

        Returns:
            Tuple of (past_singular, future_singular, past_plural, future_plural)
        """
        # Try exact locale
        if locale in self.NUMERIC_TEMPLATES:
            locale_templates = self.NUMERIC_TEMPLATES[locale]
            if unit in locale_templates and style in locale_templates[unit]:
                return locale_templates[unit][style]

        # Try base locale (e.g., 'en' from 'en-US')
        base_locale = locale.split('-')[0]
        if base_locale in self.NUMERIC_TEMPLATES:
            locale_templates = self.NUMERIC_TEMPLATES[base_locale]
            if unit in locale_templates and style in locale_templates[unit]:
                return locale_templates[unit][style]

        # Fall back to en-US
        if 'en-US' in self.NUMERIC_TEMPLATES:
            locale_templates = self.NUMERIC_TEMPLATES['en-US']
            if unit in locale_templates and style in locale_templates[unit]:
                return locale_templates[unit][style]

        # Last resort: generic template
        return (
            f'{{n}} {unit} ago',
            f'in {{n}} {unit}',
            f'{{n}} {unit}s ago',
            f'in {{n}} {unit}s'
        )

    def _get_auto_word(self, value, unit, locale):
        """
        Get special word for auto mode (e.g., "yesterday").

        Returns:
            Special word or None
        """
        # Only for -1, 0, 1
        if value not in [-1, 0, 1]:
            return None

        # Try exact locale
        if locale in self.AUTO_WORDS:
            locale_words = self.AUTO_WORDS[locale]
            if unit in locale_words and value in locale_words[unit]:
                return locale_words[unit][value]

        # Try base locale
        base_locale = locale.split('-')[0]
        if base_locale in self.AUTO_WORDS:
            locale_words = self.AUTO_WORDS[base_locale]
            if unit in locale_words and value in locale_words[unit]:
                return locale_words[unit][value]

        # Fall back to en-US
        if 'en-US' in self.AUTO_WORDS:
            locale_words = self.AUTO_WORDS['en-US']
            if unit in locale_words and value in locale_words[unit]:
                return locale_words[unit][value]

        return None

    def _format_number(self, value, locale):
        """
        Format number with locale-specific thousands separators.

        Args:
            value: Number to format
            locale: BCP 47 locale

        Returns:
            Formatted number string
        """
        # For most locales, use comma for thousands
        # (Simplified - real implementation would use CLDR data)
        if value >= 1000:
            # Format with thousands separator
            formatted = f"{int(value):,}"
            return formatted
        else:
            # Simple integer or decimal
            if isinstance(value, float) and value != int(value):
                # Has decimal part
                return str(value)
            else:
                return str(int(value))
