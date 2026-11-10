# Threat Model

Assets: plaintext while processed, DEKs, master key, user data, object metadata, audit events and service availability.

| Threat | Mitigation / status |
|---|---|
| Ciphertext modification | AES-GCM authenticated encryption |
| DEK disclosure at rest | Wrapped DEK envelope |
| Master-key compromise | Local environment key only; KMS/HSM required in production |
| Path traversal | Random object IDs and basename-only filenames |
| Oversized upload | Configured bounded read |
| Nonce reuse | Fresh CSPRNG nonce per encryption |
| Toy scheme misuse | Explicit research labels and API disclaimers |
| Unauthorized vault access | Authentication is not yet implemented; do not expose API |
| PQC downgrade | Negotiation policy not yet implemented |
| Supply-chain compromise | CI secret and dependency scans |

Out of scope: compromised hosts, malicious administrators, memory scraping, traffic analysis, and cryptanalysis of standardized schemes. Residual risks include no auth, tenant boundary, rate limiting, persistent audit trail or managed key service.
