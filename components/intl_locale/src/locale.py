"""IntlLocale - Main Intl.Locale class."""

from .bcp47_parser import BCP47Parser
from .unicode_extension import UnicodeExtensionParser
from .validation import LocaleValidation
from .likely_subtags import LocaleLikelySubtags


class IntlLocale:
    """Intl.Locale class representing a Unicode BCP 47 locale identifier."""

    def __init__(self, tag, options=None):
        """
        Create locale object from BCP 47 tag with optional overrides.

        Args:
            tag: BCP 47 language tag string
            options: Optional dict with overrides (language, script, region,
                    calendar, collation, hourCycle, caseFirst, numeric,
                    numberingSystem)
        """
        self._parser = BCP47Parser()
        self._ext_parser = UnicodeExtensionParser()
        self._validator = LocaleValidation()
        self._subtagger = LocaleLikelySubtags()

        # Parse the tag
        parsed = self._parser.parse(tag)

        # Extract base components
        self._language = parsed['language']
        self._script = parsed.get('script')
        self._region = parsed.get('region')
        self._variants = parsed.get('variants', [])

        # Parse Unicode extensions
        extensions = {}
        if 'u' in parsed.get('extensions', {}):
            extensions = self._ext_parser.parse_extension(parsed['extensions']['u'])

        # Extract extension values
        self._calendar = self._ext_parser.get_calendar(extensions)
        self._collation = self._ext_parser.get_collation(extensions)
        self._hourCycle = self._ext_parser.get_hour_cycle(extensions)
        self._caseFirst = self._ext_parser.get_case_first(extensions)
        self._numeric = self._ext_parser.get_numeric(extensions)
        self._numberingSystem = self._ext_parser.get_numbering_system(extensions)

        # Apply options (override tag values)
        if options:
            if 'language' in options and options['language']:
                self._language = options['language']
            if 'script' in options and options['script']:
                self._script = options['script']
            if 'region' in options and options['region']:
                self._region = options['region']
            if 'calendar' in options:
                cal = options['calendar']
                if cal and not self._validator.validate_calendar(cal):
                    raise ValueError(f"Invalid calendar: {cal}")
                self._calendar = cal
            if 'collation' in options:
                self._collation = options['collation']
            if 'hourCycle' in options:
                hc = options['hourCycle']
                if hc and hc not in ('h11', 'h12', 'h23', 'h24'):
                    raise ValueError(f"Invalid hour cycle: {hc}")
                self._hourCycle = hc
            if 'caseFirst' in options:
                cf = options['caseFirst']
                if cf and cf not in ('upper', 'lower', 'false'):
                    raise ValueError(f"Invalid caseFirst: {cf}")
                self._caseFirst = cf
            if 'numeric' in options:
                self._numeric = options['numeric']
            if 'numberingSystem' in options:
                ns = options['numberingSystem']
                if ns and not self._validator.validate_numbering_system(ns):
                    raise ValueError(f"Invalid numbering system: {ns}")
                self._numberingSystem = ns

    @property
    def language(self):
        """Language subtag (2-3 letters, lowercase)."""
        return self._language

    @language.setter
    def language(self, value):
        """Language is read-only."""
        raise AttributeError("can't set attribute")

    @property
    def script(self):
        """Script subtag (4 letters, title case) or None."""
        return self._script

    @script.setter
    def script(self, value):
        """Script is read-only."""
        raise AttributeError("can't set attribute")

    @property
    def region(self):
        """Region subtag (2 letters uppercase or 3 digits) or None."""
        return self._region

    @region.setter
    def region(self, value):
        """Region is read-only."""
        raise AttributeError("can't set attribute")

    @property
    def baseName(self):
        """Complete language tag without extensions."""
        parts = [self._language]
        if self._script:
            parts.append(self._script)
        if self._region:
            parts.append(self._region)
        if self._variants:
            parts.extend(self._variants)
        return '-'.join(parts)

    @baseName.setter
    def baseName(self, value):
        """baseName is read-only."""
        raise AttributeError("can't set attribute")

    @property
    def calendar(self):
        """Calendar system from -u-ca- extension."""
        return self._calendar

    @calendar.setter
    def calendar(self, value):
        """Calendar is read-only."""
        raise AttributeError("can't set attribute")

    @property
    def collation(self):
        """Collation type from -u-co- extension."""
        return self._collation

    @collation.setter
    def collation(self, value):
        """Collation is read-only."""
        raise AttributeError("can't set attribute")

    @property
    def hourCycle(self):
        """Hour cycle from -u-hc- extension."""
        return self._hourCycle

    @hourCycle.setter
    def hourCycle(self, value):
        """hourCycle is read-only."""
        raise AttributeError("can't set attribute")

    @property
    def caseFirst(self):
        """Case-first ordering from -u-kf- extension."""
        return self._caseFirst

    @caseFirst.setter
    def caseFirst(self, value):
        """caseFirst is read-only."""
        raise AttributeError("can't set attribute")

    @property
    def numeric(self):
        """Numeric collation flag from -u-kn- extension."""
        return self._numeric

    @numeric.setter
    def numeric(self, value):
        """numeric is read-only."""
        raise AttributeError("can't set attribute")

    @property
    def numberingSystem(self):
        """Numbering system from -u-nu- extension."""
        return self._numberingSystem

    @numberingSystem.setter
    def numberingSystem(self, value):
        """numberingSystem is read-only."""
        raise AttributeError("can't set attribute")

    def maximize(self):
        """
        Return new locale with likely subtags added using CLDR data.

        Example: "en" -> "en-Latn-US"
        """
        result = self._subtagger.add_likely_subtags(
            self._language,
            self._script,
            self._region
        )

        # Build new tag with maximized subtags
        tag_parts = [result['language']]
        if result['script']:
            tag_parts.append(result['script'])
        if result['region']:
            tag_parts.append(result['region'])

        # Preserve extensions
        ext_parts = []
        if self._calendar:
            ext_parts.append(f"ca-{self._calendar}")
        if self._collation:
            ext_parts.append(f"co-{self._collation}")
        if self._hourCycle:
            ext_parts.append(f"hc-{self._hourCycle}")
        if self._caseFirst:
            ext_parts.append(f"kf-{self._caseFirst}")
        if self._numeric is not None:
            ext_parts.append(f"kn-{'true' if self._numeric else 'false'}")
        if self._numberingSystem:
            ext_parts.append(f"nu-{self._numberingSystem}")

        if ext_parts:
            tag_parts.append('u')
            tag_parts.extend('-'.join(ext_parts).split('-'))

        new_tag = '-'.join(tag_parts)
        return IntlLocale(new_tag)

    def minimize(self):
        """
        Return new locale with likely subtags removed using CLDR data.

        Example: "en-Latn-US" -> "en"
        """
        result = self._subtagger.remove_likely_subtags(
            self._language,
            self._script,
            self._region
        )

        # Build new tag with minimized subtags
        tag_parts = [result['language']]
        if result['script']:
            tag_parts.append(result['script'])
        if result['region']:
            tag_parts.append(result['region'])

        # Preserve extensions
        ext_parts = []
        if self._calendar:
            ext_parts.append(f"ca-{self._calendar}")
        if self._collation:
            ext_parts.append(f"co-{self._collation}")
        if self._hourCycle:
            ext_parts.append(f"hc-{self._hourCycle}")
        if self._caseFirst:
            ext_parts.append(f"kf-{self._caseFirst}")
        if self._numeric is not None:
            ext_parts.append(f"kn-{'true' if self._numeric else 'false'}")
        if self._numberingSystem:
            ext_parts.append(f"nu-{self._numberingSystem}")

        if ext_parts:
            tag_parts.append('u')
            tag_parts.extend('-'.join(ext_parts).split('-'))

        new_tag = '-'.join(tag_parts)
        return IntlLocale(new_tag)

    def toString(self):
        """
        Serialize to canonical BCP 47 format.

        Returns properly cased, normalized locale identifier.
        """
        parts = [self._language]

        if self._script:
            parts.append(self._script)

        if self._region:
            parts.append(self._region)

        if self._variants:
            parts.extend(self._variants)

        # Add Unicode extensions in sorted order (canonical)
        ext_keys = []
        if self._calendar:
            ext_keys.append(('ca', self._calendar))
        if self._caseFirst:
            ext_keys.append(('kf', self._caseFirst))
        if self._numeric is not None:
            ext_keys.append(('kn', 'true' if self._numeric else 'false'))
        if self._collation:
            ext_keys.append(('co', self._collation))
        if self._hourCycle:
            ext_keys.append(('hc', self._hourCycle))
        if self._numberingSystem:
            ext_keys.append(('nu', self._numberingSystem))

        if ext_keys:
            # Sort by key for canonical order
            ext_keys.sort(key=lambda x: x[0])
            parts.append('u')
            for key, value in ext_keys:
                parts.append(key)
                if '-' in value:
                    parts.extend(value.split('-'))
                else:
                    parts.append(value)

        return '-'.join(parts)
