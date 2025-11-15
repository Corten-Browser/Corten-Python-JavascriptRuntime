"""IntlLocale - Main Intl.Locale class (stub for RED phase)."""


class IntlLocale:
    """Intl.Locale class representing a Unicode BCP 47 locale identifier."""

    def __init__(self, tag, options=None):
        """Create locale object from BCP 47 tag with optional overrides."""
        raise NotImplementedError("RED phase - not implemented yet")

    @property
    def language(self):
        """Language subtag."""
        raise NotImplementedError("RED phase - not implemented yet")

    @property
    def script(self):
        """Script subtag."""
        raise NotImplementedError("RED phase - not implemented yet")

    @property
    def region(self):
        """Region subtag."""
        raise NotImplementedError("RED phase - not implemented yet")

    @property
    def baseName(self):
        """Complete language tag without extensions."""
        raise NotImplementedError("RED phase - not implemented yet")

    @property
    def calendar(self):
        """Calendar system."""
        raise NotImplementedError("RED phase - not implemented yet")

    @property
    def collation(self):
        """Collation type."""
        raise NotImplementedError("RED phase - not implemented yet")

    @property
    def hourCycle(self):
        """Hour cycle."""
        raise NotImplementedError("RED phase - not implemented yet")

    @property
    def caseFirst(self):
        """Case-first ordering."""
        raise NotImplementedError("RED phase - not implemented yet")

    @property
    def numeric(self):
        """Numeric collation flag."""
        raise NotImplementedError("RED phase - not implemented yet")

    @property
    def numberingSystem(self):
        """Numbering system."""
        raise NotImplementedError("RED phase - not implemented yet")

    def maximize(self):
        """Add likely subtags using CLDR data."""
        raise NotImplementedError("RED phase - not implemented yet")

    def minimize(self):
        """Remove likely subtags using CLDR data."""
        raise NotImplementedError("RED phase - not implemented yet")

    def toString(self):
        """Serialize to canonical BCP 47 format."""
        raise NotImplementedError("RED phase - not implemented yet")
