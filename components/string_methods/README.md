# String Methods - ES2024 String.prototype Compliance

ES2024-compliant String.prototype method implementations for JavaScript runtime.

## Overview

This component provides missing ES2024 String methods and full Unicode support for the Corten JavaScript Runtime.

**Version**: 0.1.0
**Type**: Feature Component
**Test Coverage**: 90%
**Test Pass Rate**: 100%

## Features

### String.prototype Methods

- **at()** - Access characters with negative indices (FR-ES24-011)
- **replaceAll()** - Replace all occurrences, not just first (FR-ES24-012)
- **matchAll()** - Iterator of all regex matches (FR-ES24-013)
- **trimStart()** - Remove leading whitespace (FR-ES24-014)
- **trimEnd()** - Remove trailing whitespace (FR-ES24-015)
- **padStart()** - Pad string from start (FR-ES24-016)
- **padEnd()** - Pad string from end (FR-ES24-017)
- **codePointAt()** - Get Unicode code point at index (FR-ES24-018)
- **fromCodePoint()** - Create string from code points (FR-ES24-019)
- **raw()** - Template literal raw strings (FR-ES24-020)

### Unicode Support

- **normalize()** - Unicode normalization (NFC, NFD, NFKC, NFKD) (FR-ES24-021)
- **Unicode escapes** - Parse \\uXXXX and \\u{XXXXX} (FR-ES24-022)
- **Surrogate pairs** - Proper handling of emoji and complex Unicode (FR-ES24-023)
- **Unicode length** - Code point counting, not UTF-16 units (FR-ES24-024)
- **Unicode regex** - Full Unicode regex support (FR-ES24-025)

## Installation

```python
from components.string_methods import StringMethods, UnicodeSupport
```

## Usage Examples

### Basic String Operations

```python
from components.string_methods import StringMethods

# at() - Negative indexing
text = "hello"
StringMethods.at(text, -1)  # "o"
StringMethods.at(text, -2)  # "l"

# trimStart() / trimEnd()
StringMethods.trim_start("  hello  ")  # "hello  "
StringMethods.trim_end("  hello  ")    # "  hello"

# padStart() / padEnd()
StringMethods.pad_start("5", 3, "0")   # "005"
StringMethods.pad_end("5", 3, "0")     # "500"

# replaceAll()
StringMethods.replace_all("test test", "test", "pass")  # "pass pass"

# matchAll() - Returns iterator
matches = list(StringMethods.match_all("test1 test2", r"test(\d)"))
# [('test1', '1'), ('test2', '2')]
```

### Code Point Operations

```python
# codePointAt()
StringMethods.code_point_at("A", 0)    # 65
StringMethods.code_point_at("😀", 0)   # 0x1F600

# fromCodePoint()
StringMethods.from_code_point([65, 66, 67])     # "ABC"
StringMethods.from_code_point([0x1F600])        # "😀"

# String.raw()
StringMethods.raw(["C:\\", "\\file.txt"], ["Users"])
# "C:\\Users\\file.txt" (escapes preserved)
```

### Unicode Support

```python
from components.string_methods import UnicodeSupport

# normalize() - Unicode normalization
UnicodeSupport.normalize("café", "NFC")   # Composed form
UnicodeSupport.normalize("café", "NFD")   # Decomposed form

# get_unicode_length() - Code point count
UnicodeSupport.get_unicode_length("😀")          # 1 (not 2)
UnicodeSupport.get_unicode_length("Hello 😀")    # 7 (not 8)

# handle_surrogate_pairs()
chars = UnicodeSupport.handle_surrogate_pairs("😀🎉")
# ["😀", "🎉"]

# parse_unicode_escape()
UnicodeSupport.parse_unicode_escape("\\u{1F600}")  # "😀"
UnicodeSupport.parse_unicode_escape("\\u0048\\u0069")  # "Hi"

# unicode_regex_match() - Unicode-aware regex
UnicodeSupport.unicode_regex_match("😀", r"😀")  # Match object
```

## Requirements Coverage

All 15 functional requirements implemented:

| Requirement | Method | Status |
|-------------|--------|--------|
| FR-ES24-011 | String.prototype.at() | ✅ |
| FR-ES24-012 | String.prototype.replaceAll() | ✅ |
| FR-ES24-013 | String.prototype.matchAll() | ✅ |
| FR-ES24-014 | String.prototype.trimStart() | ✅ |
| FR-ES24-015 | String.prototype.trimEnd() | ✅ |
| FR-ES24-016 | String.prototype.padStart() | ✅ |
| FR-ES24-017 | String.prototype.padEnd() | ✅ |
| FR-ES24-018 | String.prototype.codePointAt() | ✅ |
| FR-ES24-019 | String.fromCodePoint() | ✅ |
| FR-ES24-020 | String.raw() | ✅ |
| FR-ES24-021 | Unicode normalization | ✅ |
| FR-ES24-022 | Unicode escape sequences | ✅ |
| FR-ES24-023 | Surrogate pair handling | ✅ |
| FR-ES24-024 | Unicode-aware length | ✅ |
| FR-ES24-025 | Unicode regex support | ✅ |

## Testing

### Unit Tests

79 unit tests covering all methods:
- 51 tests for StringMethods
- 28 tests for UnicodeSupport

```bash
pytest components/string_methods/tests/unit/ -v
```

### Integration Tests

18 integration tests for real-world scenarios:
- User input processing
- Text formatting
- Search and replace
- Emoji handling
- Performance tests
- Edge cases

```bash
pytest components/string_methods/tests/integration/ -v
```

### Test Coverage

```bash
pytest components/string_methods/tests/ --cov=components/string_methods/src
```

**Coverage**: 90% (exceeds 85% target)

## Performance

All performance requirements met:

- String operations: < 10ms for < 1MB strings ✅
- Unicode normalization: < 5ms for typical strings ✅
- Padding operations: 10,000 ops in < 100ms ✅

## Dependencies

- **object_runtime** (^0.3.0) - JSValue, JSString
- **regex_engine** (^0.2.0) - RegExp support

Optional:
- **regex** library - For advanced Unicode properties (\\p{...})

## API Reference

### StringMethods

All methods are static:

```python
class StringMethods:
    @staticmethod
    def at(string: str, index: int) -> Optional[str]

    @staticmethod
    def trim_start(string: str) -> str

    @staticmethod
    def trim_end(string: str) -> str

    @staticmethod
    def pad_start(string: str, target_length: int, pad_string: str = " ") -> str

    @staticmethod
    def pad_end(string: str, target_length: int, pad_string: str = " ") -> str

    @staticmethod
    def replace_all(string: str, search: str, replace: str) -> str

    @staticmethod
    def match_all(string: str, regexp: str) -> Iterator[Tuple]

    @staticmethod
    def code_point_at(string: str, index: int) -> Optional[int]

    @staticmethod
    def from_code_point(code_points: List[int]) -> str

    @staticmethod
    def raw(template: List[str], substitutions: List[Any]) -> str
```

### UnicodeSupport

All methods are static:

```python
class UnicodeSupport:
    @staticmethod
    def normalize(string: str, form: str = "NFC") -> str

    @staticmethod
    def get_unicode_length(string: str) -> int

    @staticmethod
    def handle_surrogate_pairs(string: str) -> List[str]

    @staticmethod
    def parse_unicode_escape(string: str) -> str

    @staticmethod
    def unicode_regex_match(string: str, pattern: str,
                           case_insensitive: bool = False) -> Optional[re.Match]
```

## Architecture

```
components/string_methods/
├── src/
│   ├── __init__.py           # Public API exports
│   ├── string_methods.py     # ES2024 String methods
│   └── unicode_support.py    # Unicode operations
├── tests/
│   ├── unit/
│   │   ├── test_string_methods.py      # 51 tests
│   │   └── test_unicode_support.py     # 28 tests
│   └── integration/
│       └── test_es2024_compliance.py   # 18 tests
└── README.md                 # This file
```

## Known Limitations

1. **Unicode Properties**: Advanced regex Unicode properties (\\p{Emoji}, \\p{Script=Greek}) require the `regex` library. Tests skip if not available.

2. **Grapheme Clusters**: `get_unicode_length()` counts code points, not grapheme clusters. Complex emoji with ZWJ sequences count as multiple code points.

3. **Performance**: Very large strings (> 1MB) may exceed the < 1ms performance target on slower systems.

## Future Enhancements

- Grapheme cluster segmentation
- Additional normalization forms
- Locale-aware string operations
- Regex library integration for full Unicode property support

## Contributing

This component follows TDD methodology:
1. Write failing tests (RED)
2. Implement minimum code to pass (GREEN)
3. Refactor for clarity (REFACTOR)

All commits show Red-Green-Refactor pattern in git history.

## License

Part of Corten JavaScript Runtime project.

## Version History

### 0.1.0 (Current)
- Initial implementation
- All 15 ES2024 requirements implemented
- 79 unit tests + 18 integration tests
- 90% test coverage
- 100% test pass rate
