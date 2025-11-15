"""
ES2024 Number and Math Extensions Component

Provides ES2024-compliant Number and Math method implementations including:
- Number.isFinite(), isInteger(), isNaN(), isSafeInteger()
- Number.parseFloat(), parseInt()
- Number constants: EPSILON, MAX_SAFE_INTEGER, MIN_SAFE_INTEGER
- Math.sign(), trunc(), cbrt()
- Math.expm1(), log1p(), log10(), log2()
- Math.hypot(), clz32(), imul(), fround()
- Hyperbolic functions: sinh, cosh, tanh, asinh, acosh, atanh
"""
from .number_methods import NumberMethods
from .number_constants import NumberConstants
from .math_methods import MathMethods

__all__ = ['NumberMethods', 'NumberConstants', 'MathMethods']
__version__ = '0.1.0'
