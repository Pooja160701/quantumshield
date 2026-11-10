"""Polynomial arithmetic in Z_q[x]/(x^n + 1), for toy RLWE research."""

from collections.abc import Sequence


def negacyclic_multiply(a: Sequence[int], b: Sequence[int], modulus: int) -> list[int]:
    """Multiply equal-length polynomials modulo x^n + 1 and q."""
    if len(a) != len(b) or not a:
        raise ValueError("polynomials must have the same non-zero length")
    if modulus < 2:
        raise ValueError("modulus must be >= 2")
    n = len(a)
    result = [0] * n
    for i, left in enumerate(a):
        for j, right in enumerate(b):
            degree = i + j
            sign = 1
            if degree >= n:
                degree -= n
                sign = -1
            result[degree] = (result[degree] + sign * left * right) % modulus
    return result


def add(a: Sequence[int], b: Sequence[int], modulus: int) -> list[int]:
    if len(a) != len(b):
        raise ValueError("polynomials must have equal lengths")
    return [(x + y) % modulus for x, y in zip(a, b, strict=True)]


def subtract(a: Sequence[int], b: Sequence[int], modulus: int) -> list[int]:
    if len(a) != len(b):
        raise ValueError("polynomials must have equal lengths")
    return [(x - y) % modulus for x, y in zip(a, b, strict=True)]
