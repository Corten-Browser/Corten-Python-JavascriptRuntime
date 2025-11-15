"""LocaleLikelySubtags - Likely subtag computation using CLDR data."""


class LocaleLikelySubtags:
    """Likely subtag computation using Unicode CLDR likelySubtags data."""

    # Likely subtags data from Unicode CLDR
    # Format: {language: (script, region)} or {language-script: region} or {language-region: script}
    LIKELY_SUBTAGS = {
        # Language only -> script + region
        'en': ('Latn', 'US'),
        'zh': ('Hans', 'CN'),
        'ja': ('Jpan', 'JP'),
        'ar': ('Arab', 'EG'),
        'fr': ('Latn', 'FR'),
        'de': ('Latn', 'DE'),
        'es': ('Latn', 'ES'),
        'ru': ('Cyrl', 'RU'),
        'pt': ('Latn', 'BR'),
        'hi': ('Deva', 'IN'),
        'ko': ('Kore', 'KR'),
        'it': ('Latn', 'IT'),
        'tr': ('Latn', 'TR'),
        'pl': ('Latn', 'PL'),
        'nl': ('Latn', 'NL'),
        'id': ('Latn', 'ID'),
        'th': ('Thai', 'TH'),
        'vi': ('Latn', 'VN'),
        'he': ('Hebr', 'IL'),
        'el': ('Grek', 'GR'),
        'cs': ('Latn', 'CZ'),
        'sv': ('Latn', 'SE'),
        'hu': ('Latn', 'HU'),
        'fi': ('Latn', 'FI'),
        'da': ('Latn', 'DK'),
        'no': ('Latn', 'NO'),
        'ro': ('Latn', 'RO'),
        'uk': ('Cyrl', 'UA'),
        'bg': ('Cyrl', 'BG'),
        'sr': ('Cyrl', 'RS'),
        'sk': ('Latn', 'SK'),
        'hr': ('Latn', 'HR'),
        'ca': ('Latn', 'ES'),
        'ms': ('Latn', 'MY'),
        'ta': ('Taml', 'IN'),
        'te': ('Telu', 'IN'),
        'bn': ('Beng', 'BD'),
        'fa': ('Arab', 'IR'),
        'gsw': ('Latn', 'CH'),
        'yue': ('Hant', 'HK'),
        'sl': ('Latn', 'SI'),
    }

    # Language-Script combinations -> region
    LIKELY_SUBTAGS_SCRIPT = {
        'zh-Hans': 'CN',
        'zh-Hant': 'TW',
        'sr-Cyrl': 'RS',
        'sr-Latn': 'RS',
        'pa-Arab': 'PK',
        'pa-Guru': 'IN',
        'uz-Arab': 'AF',
        'uz-Cyrl': 'UZ',
        'uz-Latn': 'UZ',
    }

    # Language-Region combinations -> script
    LIKELY_SUBTAGS_REGION = {
        'zh-CN': 'Hans',
        'zh-TW': 'Hant',
        'zh-HK': 'Hant',
        'zh-SG': 'Hans',
        'zh-MO': 'Hant',
        'en-GB': 'Latn',
        'en-US': 'Latn',
        'en-AU': 'Latn',
        'en-CA': 'Latn',
        'pt-BR': 'Latn',
        'pt-PT': 'Latn',
        'sr-RS': 'Cyrl',
    }

    def add_likely_subtags(self, language, script, region):
        """
        Add likely script and/or region using CLDR data.

        Returns dict with filled subtags.
        """
        result = {
            'language': language,
            'script': script,
            'region': region
        }

        # If all present, nothing to do
        if script and region:
            return result

        # Try language-script combination
        if script and not region:
            key = f"{language}-{script}"
            if key in self.LIKELY_SUBTAGS_SCRIPT:
                result['region'] = self.LIKELY_SUBTAGS_SCRIPT[key]
                return result

        # Try language-region combination
        if region and not script:
            key = f"{language}-{region}"
            if key in self.LIKELY_SUBTAGS_REGION:
                result['script'] = self.LIKELY_SUBTAGS_REGION[key]
                return result

        # Try language only
        if language in self.LIKELY_SUBTAGS:
            likely_script, likely_region = self.LIKELY_SUBTAGS[language]
            if not script:
                result['script'] = likely_script
            if not region:
                result['region'] = likely_region

        return result

    def remove_likely_subtags(self, language, script, region):
        """
        Remove likely subtags that can be inferred.

        Returns dict with minimal subtags.
        """
        result = {
            'language': language,
            'script': script,
            'region': region
        }

        # If nothing to remove, return as-is
        if not script and not region:
            return result

        # Try removing both script and region
        if script and region and language in self.LIKELY_SUBTAGS:
            likely_script, likely_region = self.LIKELY_SUBTAGS[language]
            if script == likely_script and region == likely_region:
                # Can remove both
                result['script'] = None
                result['region'] = None
                return result

        # Try removing just region (keeping script)
        if script and region:
            key = f"{language}-{script}"
            if key in self.LIKELY_SUBTAGS_SCRIPT:
                likely_region_for_script = self.LIKELY_SUBTAGS_SCRIPT[key]
                if region == likely_region_for_script:
                    # Region is implied by language+script
                    result['region'] = None
                    return result

        # Try removing just script (keeping region)
        if script and region:
            key = f"{language}-{region}"
            if key in self.LIKELY_SUBTAGS_REGION:
                likely_script_for_region = self.LIKELY_SUBTAGS_REGION[key]
                if script == likely_script_for_region:
                    # Script is implied by language+region
                    result['script'] = None
                    return result

        return result
