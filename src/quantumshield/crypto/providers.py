"""PQC provider discovery boundary.

The platform never substitutes toy research primitives for standardized PQC.
An implementation is advertised only when its provider is installed.
"""

from dataclasses import dataclass
import importlib.util


@dataclass(frozen=True)
class AlgorithmCapability:
    name: str
    standard: str
    purpose: str
    provider_available: bool
    status: str


def discover_algorithms() -> list[AlgorithmCapability]:
    available = importlib.util.find_spec("oqs") is not None
    return [
        AlgorithmCapability("ML-KEM-512", "FIPS 203", "key-establishment", available,
                            "provider-detected" if available else "provider-unavailable"),
        AlgorithmCapability("ML-KEM-768", "FIPS 203", "key-establishment", available,
                            "provider-detected" if available else "provider-unavailable"),
        AlgorithmCapability("ML-KEM-1024", "FIPS 203", "key-establishment", available,
                            "provider-detected" if available else "provider-unavailable"),
        AlgorithmCapability("ML-DSA-44", "FIPS 204", "signature", available,
                            "provider-detected" if available else "provider-unavailable"),
        AlgorithmCapability("ML-DSA-65", "FIPS 204", "signature", available,
                            "provider-detected" if available else "provider-unavailable"),
        AlgorithmCapability("ML-DSA-87", "FIPS 204", "signature", available,
                            "provider-detected" if available else "provider-unavailable"),
        AlgorithmCapability("SLH-DSA", "FIPS 205", "signature", available,
                            "provider-detected" if available else "provider-unavailable"),
    ]
