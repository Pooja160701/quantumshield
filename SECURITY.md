# Security Policy

QuantumShield is a research and engineering project. Toy LWE/RLWE modules are not secure cryptographic implementations.

## Reporting
Report sensitive vulnerabilities through a private GitHub Security Advisory where enabled, or contact the repository owner privately. Include affected commit, impact, reproduction steps and mitigation.

## Current limitations
The local vault is a development demonstration. The API currently has no user authentication, tenant authorization, rate limiting, persistent audit log, or KMS/HSM integration. Do not expose it to the public internet or place real sensitive documents in it.

Never commit keys or secrets. Do not claim FIPS validation based solely on provider presence or algorithm names. Treat all toy experiment outputs as educational.
