"""
Math object method extensions for ES2024 compliance

Requirements:
- FR-ES24-053: Math.sign()
- FR-ES24-054: Math.trunc()
- FR-ES24-055: Math.cbrt()
- FR-ES24-056: Math.expm1()
- FR-ES24-057: Math.log1p()
- FR-ES24-058: Math.log10()
- FR-ES24-059: Math.log2()
- FR-ES24-060: Math.hypot()
- FR-ES24-061: Math.clz32()
- FR-ES24-062: Math.imul()
- FR-ES24-063: Math.fround()
- FR-ES24-064: Math.sinh(), cosh(), tanh()
- FR-ES24-065: Math.asinh(), acosh(), atanh()
"""
import math
import struct
from typing import List


class MathMethods:
    """Math object method extensions per ES2024 specification"""

    @staticmethod
    def sign(x: float) -> int:
        """
        Return the sign of a number

        FR-ES24-053: Math.sign()

        Args:
            x: Number to get sign of

        Returns:
            1 for positive, -1 for negative, 0 for zero, NaN for NaN
        """
        if math.isnan(x):
            return float('nan')
        if x > 0:
            return 1
        elif x < 0:
            return -1
        else:
            return 0

    @staticmethod
    def trunc(x: float) -> int:
        """
        Truncate number to integer (remove fractional part)

        FR-ES24-054: Math.trunc()

        Args:
            x: Number to truncate

        Returns:
            Integer part of the number
        """
        return int(x)

    @staticmethod
    def cbrt(x: float) -> float:
        """
        Compute cube root

        FR-ES24-055: Math.cbrt()

        Args:
            x: Number to get cube root of

        Returns:
            Cube root of x
        """
        # Handle negative numbers correctly
        if x < 0:
            return -math.pow(-x, 1/3)
        return math.pow(x, 1/3)

    @staticmethod
    def expm1(x: float) -> float:
        """
        Compute e^x - 1 (more accurate for small x)

        FR-ES24-056: Math.expm1()

        Args:
            x: Exponent

        Returns:
            e^x - 1

        For small values of x, this is more accurate than computing
        exp(x) - 1 directly, as it avoids catastrophic cancellation.
        """
        return math.expm1(x)

    @staticmethod
    def log1p(x: float) -> float:
        """
        Compute ln(1 + x) (more accurate for small x)

        FR-ES24-057: Math.log1p()

        Args:
            x: Number to compute log1p of

        Returns:
            ln(1 + x)

        For small values of x, this is more accurate than computing
        log(1 + x) directly, as it avoids catastrophic cancellation.
        """
        return math.log1p(x)

    @staticmethod
    def log10(x: float) -> float:
        """
        Compute base-10 logarithm

        FR-ES24-058: Math.log10()

        Args:
            x: Number to compute log10 of

        Returns:
            Base-10 logarithm of x
        """
        return math.log10(x)

    @staticmethod
    def log2(x: float) -> float:
        """
        Compute base-2 logarithm

        FR-ES24-059: Math.log2()

        Args:
            x: Number to compute log2 of

        Returns:
            Base-2 logarithm of x
        """
        return math.log2(x)

    @staticmethod
    def hypot(values: List[float]) -> float:
        """
        Compute square root of sum of squares (hypotenuse)

        FR-ES24-060: Math.hypot()

        Args:
            values: List of numbers

        Returns:
            √(x1² + x2² + ... + xn²)

        Computes the hypotenuse without intermediate overflow or underflow.
        """
        return math.hypot(*values)

    @staticmethod
    def clz32(x: int) -> int:
        """
        Count leading zero bits in 32-bit integer representation

        FR-ES24-061: Math.clz32()

        Args:
            x: 32-bit integer

        Returns:
            Number of leading zero bits (0-32)
        """
        # Convert to 32-bit unsigned integer
        x = int(x) & 0xFFFFFFFF

        if x == 0:
            return 32

        # Count leading zeros
        count = 0
        mask = 0x80000000

        while (x & mask) == 0:
            count += 1
            mask >>= 1

        return count

    @staticmethod
    def imul(a: int, b: int) -> int:
        """
        32-bit integer multiplication

        FR-ES24-062: Math.imul()

        Args:
            a: First operand
            b: Second operand

        Returns:
            32-bit multiplication result (with wrapping)

        Performs C-like 32-bit integer multiplication with overflow wrapping.
        """
        # Convert to 32-bit signed integers
        a = int(a) & 0xFFFFFFFF
        b = int(b) & 0xFFFFFFFF

        # Perform multiplication
        result = a * b

        # Keep only lower 32 bits and convert to signed
        result = result & 0xFFFFFFFF

        # Convert to signed 32-bit integer
        if result >= 0x80000000:
            result -= 0x100000000

        return result

    @staticmethod
    def fround(x: float) -> float:
        """
        Round to nearest 32-bit float (single precision)

        FR-ES24-063: Math.fround()

        Args:
            x: Number to round

        Returns:
            Nearest 32-bit float representation

        Converts to 32-bit float precision and back to 64-bit,
        simulating single-precision floating point operations.
        """
        # Pack as 32-bit float and unpack
        return struct.unpack('f', struct.pack('f', x))[0]

    @staticmethod
    def sinh(x: float) -> float:
        """
        Compute hyperbolic sine

        FR-ES24-064: Math.sinh()

        Args:
            x: Number

        Returns:
            Hyperbolic sine of x: (e^x - e^(-x)) / 2
        """
        return math.sinh(x)

    @staticmethod
    def cosh(x: float) -> float:
        """
        Compute hyperbolic cosine

        FR-ES24-064: Math.cosh()

        Args:
            x: Number

        Returns:
            Hyperbolic cosine of x: (e^x + e^(-x)) / 2
        """
        return math.cosh(x)

    @staticmethod
    def tanh(x: float) -> float:
        """
        Compute hyperbolic tangent

        FR-ES24-064: Math.tanh()

        Args:
            x: Number

        Returns:
            Hyperbolic tangent of x: sinh(x) / cosh(x)
        """
        return math.tanh(x)

    @staticmethod
    def asinh(x: float) -> float:
        """
        Compute inverse hyperbolic sine

        FR-ES24-065: Math.asinh()

        Args:
            x: Number

        Returns:
            Inverse hyperbolic sine of x
        """
        return math.asinh(x)

    @staticmethod
    def acosh(x: float) -> float:
        """
        Compute inverse hyperbolic cosine

        FR-ES24-065: Math.acosh()

        Args:
            x: Number (must be ≥ 1)

        Returns:
            Inverse hyperbolic cosine of x
        """
        return math.acosh(x)

    @staticmethod
    def atanh(x: float) -> float:
        """
        Compute inverse hyperbolic tangent

        FR-ES24-065: Math.atanh()

        Args:
            x: Number (must be in range -1 to 1)

        Returns:
            Inverse hyperbolic tangent of x
        """
        return math.atanh(x)
