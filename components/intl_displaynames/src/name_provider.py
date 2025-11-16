"""
Name provider for IntlDisplayNames
Handles CLDR data loading and name lookups
"""
from typing import Optional, Dict, Any


class NameProvider:
    """
    Provides localized display names using CLDR data
    """

    def __init__(self, locale: str, display_type: str, style: str, language_display: str):
        """
        Initialize name provider

        Args:
            locale: Resolved locale identifier
            display_type: Type of display names (language, region, script, currency, calendar)
            style: Display style (long, short, narrow)
            language_display: Language display mode (dialect, standard)
        """
        self.locale = locale
        self.display_type = display_type
        self.style = style
        self.language_display = language_display

        # Cache for loaded names
        self._cache: Dict[str, str] = {}

        # Load CLDR data for the locale
        self._load_cldr_data()

    def _load_cldr_data(self):
        """
        Load CLDR display names data for the locale

        This loads localized names from CLDR data.
        For now, we use a simplified static dataset.
        """
        # Initialize data storage
        self._data: Dict[str, str] = {}

        # Load data based on locale and type
        if self.display_type == 'language':
            self._load_language_names()
        elif self.display_type == 'region':
            self._load_region_names()
        elif self.display_type == 'script':
            self._load_script_names()
        elif self.display_type == 'currency':
            self._load_currency_names()
        elif self.display_type == 'calendar':
            self._load_calendar_names()

    def _load_language_names(self):
        """Load language display names based on locale"""
        base_locale = self.locale.split('-')[0]

        if base_locale == 'en':
            # English language names
            self._data = {
                'en': 'English',
                'es': 'Spanish',
                'fr': 'French',
                'de': 'German',
                'zh': 'Chinese',
                'ja': 'Japanese',
                'ru': 'Russian',
                'ar': 'Arabic',
                'pt': 'Portuguese',
                'it': 'Italian',
                'ko': 'Korean',
                'nl': 'Dutch',
                'sv': 'Swedish',
                'no': 'Norwegian',
                'da': 'Danish',
                'fi': 'Finnish',
                'pl': 'Polish',
                'tr': 'Turkish',
                'he': 'Hebrew',
                'hi': 'Hindi',
                'th': 'Thai',
                'vi': 'Vietnamese',
                'id': 'Indonesian',
                'ms': 'Malay',
                # 3-letter codes
                'eng': 'English',
                'spa': 'Spanish',
                'fra': 'French',
                'deu': 'German',
                'zho': 'Chinese',
                'jpn': 'Japanese',
                # Dialect variants
                'en-US': 'American English',
                'en-GB': 'British English',
                'en-AU': 'Australian English',
                'es-ES': 'European Spanish',
                'es-MX': 'Mexican Spanish',
                'fr-FR': 'European French',
                'fr-CA': 'Canadian French',
                'pt-BR': 'Brazilian Portuguese',
                'pt-PT': 'European Portuguese',
                'zh-Hans': 'Simplified Chinese',
                'zh-Hant': 'Traditional Chinese',
            }
        elif base_locale == 'fr':
            # French language names
            self._data = {
                'en': 'anglais',
                'es': 'espagnol',
                'fr': 'français',
                'de': 'allemand',
                'zh': 'chinois',
                'ja': 'japonais',
                'ru': 'russe',
                'ar': 'arabe',
                'pt': 'portugais',
                'it': 'italien',
            }
        elif base_locale == 'de':
            # German language names
            self._data = {
                'en': 'Englisch',
                'es': 'Spanisch',
                'fr': 'Französisch',
                'de': 'Deutsch',
                'zh': 'Chinesisch',
                'ja': 'Japanisch',
                'ru': 'Russisch',
                'ar': 'Arabisch',
                'pt': 'Portugiesisch',
                'it': 'Italienisch',
            }
        else:
            # Default to English
            self._data = {
                'en': 'English',
                'es': 'Spanish',
                'fr': 'French',
                'de': 'German',
            }

    def _load_region_names(self):
        """Load region/country display names based on locale"""
        base_locale = self.locale.split('-')[0]

        if base_locale == 'en':
            # English region names
            self._data = {
                'US': 'United States',
                'GB': 'United Kingdom',
                'CA': 'Canada',
                'AU': 'Australia',
                'NZ': 'New Zealand',
                'IE': 'Ireland',
                'JP': 'Japan',
                'CN': 'China',
                'KR': 'South Korea',
                'IN': 'India',
                'BR': 'Brazil',
                'MX': 'Mexico',
                'DE': 'Germany',
                'FR': 'France',
                'IT': 'Italy',
                'ES': 'Spain',
                'PT': 'Portugal',
                'NL': 'Netherlands',
                'BE': 'Belgium',
                'CH': 'Switzerland',
                'AT': 'Austria',
                'SE': 'Sweden',
                'NO': 'Norway',
                'DK': 'Denmark',
                'FI': 'Finland',
                'PL': 'Poland',
                'RU': 'Russia',
                'TR': 'Turkey',
                'SA': 'Saudi Arabia',
                'AE': 'United Arab Emirates',
                'EG': 'Egypt',
                'ZA': 'South Africa',
                'NG': 'Nigeria',
                'KE': 'Kenya',
                'AR': 'Argentina',
                'CL': 'Chile',
                'CO': 'Colombia',
                'PE': 'Peru',
                'VE': 'Venezuela',
            }
        elif base_locale == 'fr':
            # French region names
            self._data = {
                'US': 'États-Unis',
                'GB': 'Royaume-Uni',
                'CA': 'Canada',
                'FR': 'France',
                'DE': 'Allemagne',
                'IT': 'Italie',
                'ES': 'Espagne',
                'JP': 'Japon',
                'CN': 'Chine',
                'BR': 'Brésil',
            }
        elif base_locale == 'de':
            # German region names
            self._data = {
                'US': 'Vereinigte Staaten',
                'GB': 'Vereinigtes Königreich',
                'CA': 'Kanada',
                'FR': 'Frankreich',
                'DE': 'Deutschland',
                'IT': 'Italien',
                'ES': 'Spanien',
                'JP': 'Japan',
                'CN': 'China',
                'BR': 'Brasilien',
            }
        else:
            # Default to English
            self._data = {
                'US': 'United States',
                'GB': 'United Kingdom',
                'JP': 'Japan',
                'DE': 'Germany',
                'FR': 'France',
                'CN': 'China',
            }

    def _load_script_names(self):
        """Load script display names based on locale"""
        base_locale = self.locale.split('-')[0]

        if base_locale == 'en':
            # English script names
            self._data = {
                'Latn': 'Latin',
                'Cyrl': 'Cyrillic',
                'Arab': 'Arabic',
                'Hans': 'Simplified Han',
                'Hant': 'Traditional Han',
                'Hebr': 'Hebrew',
                'Deva': 'Devanagari',
                'Grek': 'Greek',
                'Kana': 'Katakana',
                'Hira': 'Hiragana',
                'Hang': 'Hangul',
                'Thai': 'Thai',
                'Armn': 'Armenian',
                'Geor': 'Georgian',
                'Ethi': 'Ethiopic',
            }
        elif base_locale == 'fr':
            # French script names
            self._data = {
                'Latn': 'latin',
                'Cyrl': 'cyrillique',
                'Arab': 'arabe',
                'Hans': 'chinois simplifié',
                'Hant': 'chinois traditionnel',
                'Hebr': 'hébreu',
            }
        elif base_locale == 'de':
            # German script names
            self._data = {
                'Latn': 'Lateinisch',
                'Cyrl': 'Kyrillisch',
                'Arab': 'Arabisch',
                'Hans': 'Vereinfachtes Chinesisch',
                'Hant': 'Traditionelles Chinesisch',
                'Hebr': 'Hebräisch',
            }
        else:
            # Default to English
            self._data = {
                'Latn': 'Latin',
                'Cyrl': 'Cyrillic',
                'Arab': 'Arabic',
                'Hans': 'Simplified Han',
                'Hant': 'Traditional Han',
            }

    def _load_currency_names(self):
        """Load currency display names based on locale"""
        base_locale = self.locale.split('-')[0]

        if base_locale == 'en':
            # English currency names
            self._data = {
                'USD': 'US Dollar',
                'EUR': 'Euro',
                'GBP': 'British Pound Sterling',
                'JPY': 'Japanese Yen',
                'CNY': 'Chinese Yuan',
                'CHF': 'Swiss Franc',
                'CAD': 'Canadian Dollar',
                'AUD': 'Australian Dollar',
                'NZD': 'New Zealand Dollar',
                'INR': 'Indian Rupee',
                'BRL': 'Brazilian Real',
                'RUB': 'Russian Ruble',
                'KRW': 'South Korean Won',
                'MXN': 'Mexican Peso',
                'ZAR': 'South African Rand',
                'SEK': 'Swedish Krona',
                'NOK': 'Norwegian Krone',
                'DKK': 'Danish Krone',
                'PLN': 'Polish Zloty',
                'TRY': 'Turkish Lira',
                'THB': 'Thai Baht',
                'IDR': 'Indonesian Rupiah',
                'MYR': 'Malaysian Ringgit',
                'SGD': 'Singapore Dollar',
                'HKD': 'Hong Kong Dollar',
                'ARS': 'Argentine Peso',
                'CLP': 'Chilean Peso',
                'COP': 'Colombian Peso',
            }
        elif base_locale == 'fr':
            # French currency names
            self._data = {
                'USD': 'dollar des États-Unis',
                'EUR': 'euro',
                'GBP': 'livre sterling',
                'JPY': 'yen japonais',
                'CNY': 'yuan chinois',
                'CHF': 'franc suisse',
                'CAD': 'dollar canadien',
            }
        elif base_locale == 'de':
            # German currency names
            self._data = {
                'USD': 'US-Dollar',
                'EUR': 'Euro',
                'GBP': 'Britisches Pfund',
                'JPY': 'Japanischer Yen',
                'CNY': 'Chinesischer Yuan',
                'CHF': 'Schweizer Franken',
                'CAD': 'Kanadischer Dollar',
            }
        else:
            # Default to English
            self._data = {
                'USD': 'US Dollar',
                'EUR': 'Euro',
                'GBP': 'British Pound Sterling',
                'JPY': 'Japanese Yen',
            }

    def _load_calendar_names(self):
        """Load calendar display names based on locale"""
        base_locale = self.locale.split('-')[0]

        if base_locale == 'en':
            # English calendar names
            self._data = {
                'gregory': 'Gregorian Calendar',
                'gregorian': 'Gregorian Calendar',
                'islamic': 'Islamic Calendar',
                'hebrew': 'Hebrew Calendar',
                'buddhist': 'Buddhist Calendar',
                'chinese': 'Chinese Calendar',
                'japanese': 'Japanese Calendar',
                'persian': 'Persian Calendar',
                'indian': 'Indian National Calendar',
                'coptic': 'Coptic Calendar',
                'ethiopic': 'Ethiopic Calendar',
            }
        elif base_locale == 'fr':
            # French calendar names
            self._data = {
                'gregory': 'calendrier grégorien',
                'gregorian': 'calendrier grégorien',
                'islamic': 'calendrier musulman',
                'hebrew': 'calendrier hébraïque',
                'buddhist': 'calendrier bouddhiste',
            }
        elif base_locale == 'de':
            # German calendar names
            self._data = {
                'gregory': 'Gregorianischer Kalender',
                'gregorian': 'Gregorianischer Kalender',
                'islamic': 'Islamischer Kalender',
                'hebrew': 'Hebräischer Kalender',
                'buddhist': 'Buddhistischer Kalender',
            }
        else:
            # Default to English
            self._data = {
                'gregory': 'Gregorian Calendar',
                'islamic': 'Islamic Calendar',
                'hebrew': 'Hebrew Calendar',
            }

    def get_display_name(self, code: str) -> Optional[str]:
        """
        Get display name for given code

        Args:
            code: Language/region/script/currency/calendar code

        Returns:
            Localized display name or None if not found
        """
        # Check cache first
        if code in self._cache:
            return self._cache[code]

        # Handle language display mode
        if self.display_type == 'language' and self.language_display == 'standard':
            # For standard mode, strip dialect/region subtags
            base_code = code.split('-')[0]
            name = self._data.get(base_code)
        else:
            # Try exact match first
            name = self._data.get(code)

            # For language codes with subtags, try base code if exact match not found
            if name is None and self.display_type == 'language' and '-' in code:
                base_code = code.split('-')[0]
                name = self._data.get(base_code)

        # Cache the result
        if name is not None:
            self._cache[code] = name

        return name
