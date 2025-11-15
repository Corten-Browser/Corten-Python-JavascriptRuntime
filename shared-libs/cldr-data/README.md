# Unicode CLDR Data

This directory contains Unicode Common Locale Data Repository (CLDR) data used by Intl components.

## Data Format
- JSON format for easy parsing
- Organized by locale
- Subset of full CLDR for size optimization

## Locales Included
- en-US (primary)
- Additional locales can be added as needed

## Data Categories
- Date/time patterns
- Number patterns
- Currency symbols
- Plural rules
- Collation rules
- Display names
- Segmentation rules

## Usage
Components load locale data on demand from this directory.

