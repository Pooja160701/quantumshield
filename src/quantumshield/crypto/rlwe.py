"""Toy Ring-LWE arithmetic demonstration; not suitable for real encryption."""

from dataclasses import dataclass
import random

from quantumshield.crypto.polynomial import add, negacyclic_multiply


@dataclass(frozen=True)
class RLWEParameters:
    degree: int = 16
    modulus: int = 257
    noise_bound: int = 1

    def validate(self) -> None:
        if self.degree < 2 or self.degree > 64:
            raise ValueError("degree must be between 2 and 64")
        if self.modulus < 17 or self.modulus > 4093:
            raise ValueError("modulus must be between 17 and 4093")
        if not 0 <= self.noise_bound <= 3:
            raise ValueError("noise_bound must be between 0 and 3")


@dataclass(frozen=True)
class RLWEKeyPair:
    secret: tuple[int, ...]
    public_a: tuple[int, ...]
    public_b: tuple[int, ...]


def keygen(params: RLWEParameters, seed: int = 7) -> RLWEKeyPair:
    params.validate()
    rng = random.Random(seed)
    q, n = params.modulus, params.degree
    secret = tuple(rng.choice([-1, 0, 1]) % q for _ in range(n))
    a = tuple(rng.randrange(q) for _ in range(n))
    error = [rng.randint(-params.noise_bound, params.noise_bound) for _ in range(n)]
    product = negacyclic_multiply(a, secret, q)
    b = tuple((x + e) % q for x, e in zip(product, error, strict=True))
    return RLWEKeyPair(secret, a, b)


def encrypt(message: list[int], public_key: RLWEKeyPair, params: RLWEParameters, seed: int = 11) -> tuple[list[int], list[int]]:
    """Return toy RLWE ciphertext components (c0, c1)."""
    params.validate()
    if len(message) != params.degree:
        raise ValueError("message length must equal ring degree")
    rng = random.Random(seed)
    q, n = params.modulus, params.degree
    r = [rng.choice([-1, 0, 1]) % q for _ in range(n)]
    e1 = [rng.randint(-params.noise_bound, params.noise_bound) for _ in range(n)]
    e2 = [rng.randint(-params.noise_bound, params.noise_bound) for _ in range(n)]
    c1 = add(negacyclic_multiply(public_key.public_a, r, q), e1, q)
    c0 = add(
        add(negacyclic_multiply(public_key.public_b, r, q), e2, q),
        [int(x) * (q // 2) for x in message],
        q,
    )
    return c0, c1
