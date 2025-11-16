"""
Unicode Edge Cases - ES2024 Wave D
Complete Unicode normalization edge case handling
"""
from .normalizer import UnicodeNormalizer
from .combining_chars import CombiningCharacterHandler
from .hangul import HangulNormalizer
from .emoji import EmojiNormalizer
from .quick_check import QuickCheckOptimizer

__all__ = [
    'UnicodeNormalizer',
    'CombiningCharacterHandler',
    'HangulNormalizer',
    'EmojiNormalizer',
    'QuickCheckOptimizer',
]

__version__ = '0.1.0'
