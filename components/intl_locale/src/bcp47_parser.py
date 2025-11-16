"""BCP47Parser - BCP 47 language tag parser."""

import re


class BCP47Parser:
    """BCP 47 language tag parser per RFC 5646."""

    # Grandfathered tags (legacy support)
    GRANDFATHERED_TAGS = {
        'i-default', 'i-enochian', 'i-hak', 'i-klingon', 'i-lux',
        'i-mingo', 'i-navajo', 'i-pwn', 'i-tao', 'i-tay', 'i-tsu'
    }

    def parse(self, tag):
        """
        Parse BCP 47 language tag into structured components.

        Returns dict with:
        - language: Language subtag (required)
        - script: Script subtag (optional)
        - region: Region subtag (optional)
        - variants: List of variant subtags
        - extensions: Dict of extension singletons to values
        - privateUse: Private use subtags
        """
        if not tag or not isinstance(tag, str):
            raise ValueError("Invalid language tag")

        tag = tag.strip()
        if not tag:
            raise ValueError("Invalid language tag")

        # Handle grandfathered tags
        if tag.lower() in self.GRANDFATHERED_TAGS:
            return {
                'language': tag.lower(),
                'script': None,
                'region': None,
                'variants': [],
                'extensions': {},
                'privateUse': None
            }

        # Split by hyphens
        parts = tag.split('-')
        if not parts:
            raise ValueError("Invalid language tag")

        result = {
            'language': None,
            'script': None,
            'region': None,
            'variants': [],
            'extensions': {},
            'privateUse': None
        }

        i = 0

        # Parse language (required, 2-3 letters)
        if i < len(parts):
            language = parts[i].lower()
            if not re.match(r'^[a-z]{2,3}$', language):
                raise ValueError("Invalid language tag")
            result['language'] = language
            i += 1
        else:
            raise ValueError("Invalid language tag")

        # Parse script (optional, 4 letters)
        if i < len(parts) and re.match(r'^[a-z]{4}$', parts[i].lower()):
            script = parts[i]
            # Canonicalize to title case
            result['script'] = script[0].upper() + script[1:].lower()
            i += 1
        elif i < len(parts) and re.match(r'^[a-z]{3}$', parts[i].lower()):
            # 3 letters that look like a script but wrong length - reject
            raise ValueError("Invalid language tag")

        # Parse region (optional, 2 letters or 3 digits)
        if i < len(parts) and re.match(r'^([a-z]{2}|[0-9]{3})$', parts[i].lower()):
            region = parts[i]
            # Canonicalize: uppercase for letters, as-is for digits
            if region.isdigit():
                result['region'] = region
            else:
                result['region'] = region.upper()
            i += 1
        elif i < len(parts) and (re.match(r'^[a-z]{3}$', parts[i].lower()) or
                                  re.match(r'^[0-9]{1,2}$', parts[i])):
            # 3 letters or 1-2 digits that look like a region but wrong length - reject
            raise ValueError("Invalid language tag")

        # Parse variants (5-8 alphanumeric or 4 chars starting with digit)
        while i < len(parts):
            part = parts[i].lower()
            if re.match(r'^([a-z0-9]{5,8}|[0-9][a-z0-9]{3})$', part):
                result['variants'].append(part)
                i += 1
            else:
                break

        # Parse extensions (singleton followed by subtags)
        while i < len(parts):
            if len(parts[i]) == 1 and parts[i].lower() != 'x':
                # Extension singleton
                singleton = parts[i].lower()
                i += 1
                # Collect extension values
                ext_values = []
                while i < len(parts) and len(parts[i]) > 1 and parts[i].lower() != 'x':
                    ext_values.append(parts[i].lower())
                    i += 1
                if ext_values:
                    result['extensions'][singleton] = '-'.join(ext_values)
                else:
                    # Extension without values is invalid
                    break
            elif parts[i].lower() == 'x':
                # Private use
                i += 1
                private_parts = []
                while i < len(parts):
                    private_parts.append(parts[i].lower())
                    i += 1
                if private_parts:
                    result['privateUse'] = '-'.join(private_parts)
                break
            else:
                # Unknown part, stop parsing
                break

        return result

    def validate(self, tag):
        """
        Validate BCP 47 tag structure.

        Returns True if valid, False otherwise.
        """
        try:
            self.parse(tag)
            return True
        except (ValueError, AttributeError):
            return False

    def canonicalize(self, tag):
        """
        Canonicalize BCP 47 tag casing:
        - Language: lowercase
        - Script: Title case
        - Region: uppercase
        - Extensions: lowercase
        """
        try:
            parsed = self.parse(tag)

            # Rebuild tag
            parts = [parsed['language']]

            if parsed['script']:
                parts.append(parsed['script'])

            if parsed['region']:
                parts.append(parsed['region'])

            if parsed['variants']:
                parts.extend(parsed['variants'])

            # Add extensions in sorted order (canonical)
            for singleton in sorted(parsed['extensions'].keys()):
                parts.append(singleton)
                parts.extend(parsed['extensions'][singleton].split('-'))

            if parsed['privateUse']:
                parts.append('x')
                parts.extend(parsed['privateUse'].split('-'))

            return '-'.join(parts)

        except ValueError:
            # If parsing fails, return as-is
            return tag
