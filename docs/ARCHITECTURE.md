# Architecture

## Services
- FastAPI gateway: validation, error mapping, health, metrics and REST.
- Research package: toy LWE sample relations, RLWE public samples and exact negacyclic polynomial arithmetic.
- PQC adapter boundary: capability discovery for ML-KEM (FIPS 203), ML-DSA (FIPS 204) and SLH-DSA (FIPS 205); provider detection is not certification.
- Vault: random 256-bit DEK, AES-256-GCM data encryption, separately wrapped DEK and object ID as associated data.
- Benchmark and noise laboratory: bounded repeatable local experiments.

## File encryption
1. Generate a fresh random DEK.
2. Generate distinct 96-bit nonces for data and DEK wrapping.
3. Encrypt file bytes with AES-256-GCM.
4. Wrap the DEK using the configured 256-bit local key.
5. Store the encrypted envelope and return a random object ID.

## Future production hardening
Replace local key wrapping with KMS/HSM; implement authentication, tenant isolation, authorization, persistent audit, rate limiting, object-store retention, streaming uploads, provider interoperability tests, TLS policy and external cryptographic review.
