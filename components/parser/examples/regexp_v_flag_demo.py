#!/usr/bin/env python
"""
Demonstration of RegExp /v flag implementation for ES2024.

Shows how the lexer and parser handle:
- /v flag parsing
- Character class set operations
- String properties in character classes
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from components.parser.src.lexer import Lexer
from components.parser.src.regexp_v_flag import RegExpVFlag, RegExpFlags, CharacterClassSetParser


def demo_v_flag_parsing():
    """Demonstrate /v flag parsing in RegExp literals."""
    print("=" * 70)
    print("DEMO 1: RegExp /v flag parsing")
    print("=" * 70)

    # Example 1: Basic /v flag
    lexer = Lexer("/[a-z]/v", "demo.js")
    token = lexer.next_token()
    print(f"\n1. Basic /v flag:")
    print(f"   Pattern: /[a-z]/v")
    print(f"   Token type: {token.type}")
    print(f"   Pattern: {token.value['pattern']}")
    print(f"   Flags: {token.value['flags']}")

    # Example 2: /v with other flags
    lexer = Lexer("/pattern/giv", "demo.js")
    token = lexer.next_token()
    print(f"\n2. /v with other flags:")
    print(f"   Pattern: /pattern/giv")
    print(f"   Flags: {token.value['flags']}")

    # Example 3: /v and /u mutual exclusivity
    print(f"\n3. /v and /u mutual exclusivity:")
    try:
        flags = RegExpFlags.from_string("uv")
        print(f"   ERROR: Should have raised TypeError!")
    except TypeError as e:
        print(f"   ✓ Correctly rejected: {e}")


def demo_set_operations():
    """Demonstrate character class set operations."""
    print("\n" + "=" * 70)
    print("DEMO 2: Character class set operations")
    print("=" * 70)

    parser = CharacterClassSetParser()

    # Example 1: Intersection
    print(f"\n1. Intersection (vowels):")
    pattern = "[a-z&&[aeiou]]"
    result = parser.parse(pattern, has_v_flag=True)
    print(f"   Pattern: {pattern}")
    print(f"   Type: {result['type']}")
    print(f"   Left: {result['left']}")
    print(f"   Right: {result['right']}")

    # Example 2: Subtraction
    print(f"\n2. Subtraction (consonants):")
    pattern = "[a-z--[aeiou]]"
    result = parser.parse(pattern, has_v_flag=True)
    print(f"   Pattern: {pattern}")
    print(f"   Type: {result['type']}")
    print(f"   Left: {result['left']}")
    print(f"   Right: {result['right']}")

    # Example 3: Without /v flag
    print(f"\n3. Set operations require /v flag:")
    try:
        result = parser.parse("[a-z&&[aeiou]]", has_v_flag=False)
        print(f"   ERROR: Should have raised ValueError!")
    except ValueError as e:
        print(f"   ✓ Correctly rejected: {e}")


def demo_string_properties():
    """Demonstrate string properties in character classes."""
    print("\n" + "=" * 70)
    print("DEMO 3: String properties in character classes")
    print("=" * 70)

    parser = CharacterClassSetParser()

    # Example 1: Unicode property
    print(f"\n1. Unicode property:")
    pattern = r"[\p{RGI_Emoji}]"
    result = parser.parse(pattern, has_v_flag=True)
    print(f"   Pattern: {pattern}")
    print(f"   Type: {result['type']}")
    print(f"   Property: {result['property']}")
    print(f"   String property: {result['string_property']}")

    # Example 2: Negated property
    print(f"\n2. Negated property:")
    pattern = r"[\P{ASCII}]"
    result = parser.parse(pattern, has_v_flag=True)
    print(f"   Pattern: {pattern}")
    print(f"   Type: {result['type']}")
    print(f"   Property: {result['property']}")
    print(f"   Negated: {result['negated']}")


def demo_full_integration():
    """Demonstrate complete RegExp /v flag integration."""
    print("\n" + "=" * 70)
    print("DEMO 4: Full integration")
    print("=" * 70)

    # Example: Complex pattern with all features
    pattern = r"/[\p{RGI_Emoji}&&[^aeiou]]/v"
    print(f"\n1. Complex pattern with all /v features:")
    print(f"   Pattern: {pattern}")

    lexer = Lexer(pattern, "demo.js")
    token = lexer.next_token()
    print(f"   Token type: {token.type}")
    print(f"   Flags: {token.value['flags']}")
    print(f"   Pattern content: {token.value['pattern']}")

    # Parse with RegExpVFlag class
    regexp = RegExpVFlag(pattern)
    print(f"\n2. Parsed RegExp object:")
    print(f"   Pattern: {regexp.pattern}")
    print(f"   Has /v flag: {regexp.flags.v}")
    print(f"   Has /u flag: {regexp.flags.u}")

    char_classes = regexp.parse_character_classes()
    print(f"\n3. Parsed character classes: {len(char_classes)}")
    for i, cc in enumerate(char_classes):
        print(f"   Class {i + 1}: {cc['type']}")


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 70)
    print("RegExp /v Flag Implementation Demo - ES2024")
    print("=" * 70)

    demo_v_flag_parsing()
    demo_set_operations()
    demo_string_properties()
    demo_full_integration()

    print("\n" + "=" * 70)
    print("All demonstrations completed successfully!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
