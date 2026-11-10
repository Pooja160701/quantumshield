"""Educational Learning With Errors experiment.

This intentionally tiny scheme illustrates the LWE relation. It is not a
secure encryption scheme: parameter selection, message encoding and noise
handling are pedagogical only. Never use it to protect data.
"""

from dataclasses import dataclass
import random


@dataclass(frozen=True)
class LWEParameters:
    dimension: int = 32
    modulus: int = 257
    noise_bound: int = 1

    def validate(self) -> None:
        if self.dimension < 1 or self.dimension > 256:
            raise ValueError("dimension must be between 1 and 256")
        if self.modulus < 17 or self.modulus > 4093:
            raise ValueError("modulus must be between 17 and 4093")
        if self.noise_bound < 0 or self.noise_bound > 3:
            raise ValueError("noise_bound must be between 0 and 3")


@dataclass(frozen=True)
class LWEKeyPair:
    secret: tuple[int, ...]
    public_a: tuple[int, ...]
    public_b: int


@dataclass(frozen=True)
class LWECiphertext:
    u: tuple[int, ...]
    v: int


def keygen(params: LWEParameters, seed: int = 7) -> LWEKeyPair:
    """Generate a toy secret and a single public LWE sample."""
    params.validate()
    rng = random.Random(seed)
    q, n = params.modulus, params.dimension
    secret = tuple(rng.randrange(q) for _ in range(n))
    a = tuple(rng.randrange(q) for _ in range(n))
    error = rng.randint(-params.noise_bound, params.noise_bound)
    b = (sum(x * s for x, s in zip(a, secret, strict=True)) + error) % q
    return LWEKeyPair(secret, a, b)


def encrypt(
    message: int, public_key: LWEKeyPair, params: LWEParameters, seed: int = 11
) -> LWECiphertext:
    """Encrypt one bit in a pedagogical LWE construction."""
    params.validate()
    if message not in (0, 1):
        raise ValueError("message must be a bit (0 or 1)")
    rng = random.Random(seed)
    q = params.modulus
    r = [rng.randrange(2) for _ in range(params.dimension)]
    error = rng.randint(-params.noise_bound, params.noise_bound)
    u = tuple(
        sum(r[i] * public_key.public_a[i] for i in range(params.dimension)) % q
        for _ in range(params.dimension)
    )
    # The first public vector is intentionally reused to keep this example small.
    # This construction exists only to expose modular arithmetic, not security.
    inner = sum(r[i] * public_key.public_a[i] for i in range(params.dimension)) % q
    v = (sum(r) * public_key.public_b + error + message * (q // 2)) % q
    return LWECiphertext(tuple((x + inner) % q for x in u), v)


def decrypt(ciphertext: LWECiphertext, secret_key: tuple[int, ...], params: LWEParameters) -> int:
    """Recover the nearest encoded bit in this toy demonstration."""
    params.validate()
    # A toy decoding threshold; this is not a standards-based construction.
    phase = (ciphertext.v - sum(ciphertext.u[i] * secret_key[i] for i in range(len(secret_key)))) % params.modulus
    return int(phase > params.modulus // 4 and phase < 3 * params.modulus // 4)
