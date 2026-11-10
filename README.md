# QUANTUMSHIELD

**Post-Quantum Cryptography Research, Crypto-Agility & Security Operations Platform**

QuantumShield is an open-source engineering platform for studying lattice-based cryptography, evaluating standardized post-quantum algorithm providers, experimenting with authenticated file encryption, and measuring cryptographic operations.

> **Security boundary:** LWE/RLWE modules are educational research demonstrations, not production cryptography. The PQC module detects provider availability only; it does not claim FIPS validation or implement custom production algorithms.

## Implemented in this milestone

- Educational LWE public-sample generation and parameter validation.
- Negacyclic polynomial arithmetic in the quotient ring Z_q[x]/(x^n + 1).
- Educational RLWE public-sample experiments.
- PQC provider capability catalog for ML-KEM (FIPS 203), ML-DSA (FIPS 204), SLH-DSA (FIPS 205).
- AES-256-GCM file vault with random per-object DEK and wrapped-key envelope.
- Bounded noise distribution experiments and local AES-GCM microbenchmark.
- FastAPI API, OpenAPI docs, health and Prometheus metrics.
- Docker image, Compose configuration, tests, CI and security scanning workflows.

## Architecture

```text
Research client / API docs
          |
      FastAPI API
          |
  +-------+-------------+---------------+
  |                     |               |
Research engine      PQC catalog     Secure vault
LWE / RLWE / NTT*    provider check   AES-GCM envelope
  |                     |               |
  +---------------------+---------------+
                        |
          Benchmarks / Noise experiments
                        |
             Prometheus metrics / CI
```

*Exact negacyclic multiplication is included; optimized NTT is a future milestone.*

## Quick start

Requirements: Python 3.11+.

```bash
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
uvicorn quantumshield.api.main:app --reload
```

Open API docs at http://127.0.0.1:8000/docs, health at http://127.0.0.1:8000/health, and metrics at http://127.0.0.1:8000/metrics.

Run tests and lint with `pytest` and `ruff check .`. Run Docker using `docker compose up --build`.

## API overview

| Endpoint | Purpose |
|---|---|
| `GET /health` | Health and version |
| `GET /metrics` | Prometheus metrics |
| `POST /api/v1/research/lwe` | Educational LWE public sample |
| `POST /api/v1/research/rlwe` | Educational RLWE public sample |
| `GET /api/v1/pqc/providers` | PQC provider capability discovery |
| `POST /api/v1/lab/noise-sweep` | Bounded noise distribution experiment |
| `POST /api/v1/benchmarks/run` | AES-GCM local microbenchmark |
| `POST /api/v1/vault/encrypt` | Encrypt an uploaded file |
| `POST /api/v1/vault/decrypt/{object_id}` | Decrypt a vault object |
| `GET /api/v1/inventory` | Starter cryptographic inventory |
| `GET /api/v1/security/summary` | Current security telemetry status |

See [docs/API.md](docs/API.md), [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), and [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md).

## Vault key setup

Vault operations require `QUANTUMSHIELD_MASTER_KEY`, a URL-safe-base64 encoded 32-byte key. Generate one locally:

```bash
python -c "import base64,secrets; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())"
```

Put it in `.env`. Never commit it.

## Security limitations

The local vault is a development demonstration. The API does not yet implement user authentication, tenant authorization, rate limiting, persistent audit logging, or KMS/HSM integration. Do not expose it to the public internet or store real sensitive documents. Read [SECURITY.md](SECURITY.md).

## Roadmap

1. Add maintained PQC provider integration and official-vector interoperability tests.
2. Implement authentication, authorization, tenant separation and persistent audit.
3. Integrate KMS/HSM and managed object storage.
4. Add NTT acceleration and deeper lattice experiments.
5. Build research/admin dashboards and distributed worker profiles.
6. Add independent security review and production hardening.

## License

Apache-2.0. See [LICENSE](LICENSE).
