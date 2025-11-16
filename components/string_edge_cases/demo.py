#!/usr/bin/env python3
"""
Demonstration of String Edge Cases Component
ES2024 Wave D - All 4 Requirements
"""

from src.edge_cases import StringEdgeCases

print("=" * 70)
print("STRING EDGE CASES COMPONENT - ES2024 WAVE D")
print("=" * 70)
print()

# FR-ES24-D-007: String.at() with negative indices
print("1. String.at() - Negative Indices")
print("-" * 70)
result = StringEdgeCases.at("hello", -1)
print(f"   StringEdgeCases.at('hello', -1) = {result}")
result = StringEdgeCases.at("hello 😀 world", 6)
print(f"   StringEdgeCases.at('hello 😀 world', 6) = {result}")
print()

# FR-ES24-D-006: code_point_at() with surrogate pairs
print("2. Code Point At - Surrogate Pair Detection")
print("-" * 70)
result = StringEdgeCases.code_point_at("hello", 0)
print(f"   StringEdgeCases.code_point_at('hello', 0) = {result}")
result = StringEdgeCases.code_point_at("😀", 0)
print(f"   StringEdgeCases.code_point_at('😀', 0) = {result}")
print()

# FR-ES24-D-008: iterate_code_points() iterator
print("3. Iterate Code Points - String Iterator")
print("-" * 70)
result = StringEdgeCases.iterate_code_points("hello")
print(f"   StringEdgeCases.iterate_code_points('hello') =")
print(f"      {result}")
result = StringEdgeCases.iterate_code_points("😀😁😂")
print(f"   StringEdgeCases.iterate_code_points('😀😁😂') =")
print(f"      {result}")
print()

# FR-ES24-D-009: match_unicode_property() Unicode properties
print("4. Match Unicode Property - RegExp Property Escapes")
print("-" * 70)
result = StringEdgeCases.match_unicode_property("Hello 😀 World 🌍", "Emoji")
print(f"   StringEdgeCases.match_unicode_property('Hello 😀 World 🌍', 'Emoji') =")
print(f"      {result}")
result = StringEdgeCases.match_unicode_property("Hello123World", "Letter")
print(f"   StringEdgeCases.match_unicode_property('Hello123World', 'Letter') =")
print(f"      Count: {result['count']}, First 5: {result['matches'][:5]}")
result = StringEdgeCases.match_unicode_property("Αλφα Beta Γάμμα", "Script=Greek")
print(f"   StringEdgeCases.match_unicode_property('Αλφα Beta Γάμμα', 'Script=Greek') =")
print(f"      Count: {result['count']}, Matches: {result['matches'][:5]}...")
print()

print("=" * 70)
print("✅ ALL 4 REQUIREMENTS DEMONSTRATED")
print("=" * 70)
