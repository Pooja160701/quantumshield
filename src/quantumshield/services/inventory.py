"""Starter cryptographic asset inventory."""

ASSETS = [
    {"name": "Vault file encryption", "algorithm": "AES-256-GCM", "purpose": "symmetric-encryption", "status": "current"},
    {"name": "Vault key wrapping", "algorithm": "AES-256-GCM", "purpose": "key-wrapping", "status": "current"},
    {"name": "PQC key establishment", "algorithm": "ML-KEM", "purpose": "key-establishment", "status": "provider-dependent"},
    {"name": "PQC signatures", "algorithm": "ML-DSA / SLH-DSA", "purpose": "digital-signature", "status": "provider-dependent"},
    {"name": "Research experiments", "algorithm": "toy LWE / RLWE", "purpose": "education-only", "status": "not-for-production"},
]


def list_assets() -> list[dict[str, str]]:
    return [asset.copy() for asset in ASSETS]
