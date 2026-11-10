# QUANTUMSHIELD

**Post-Quantum Cryptography Research, Crypto-Agility & Security Operations Platform**

QuantumShield is an open-source engineering platform for studying lattice-based cryptography, evaluating standardized post-quantum algorithms, exercising secure-file workflows, running controlled attack simulations, and observing cryptographic services.

> **Security boundary:** The built-in LWE/RLWE code is educational research code. It is deliberately not presented as production cryptography. Production-facing PQC operations use vetted, standards-oriented providers and must be independently reviewed before deployment.

## Platform capabilities

- **Cryptographic research:** parameterized toy LWE and negacyclic RLWE experiments, noise analysis, polynomial arithmetic, reproducible seeds, and correctness tests.
- **PQC provider boundary:** an adapter interface for ML-KEM, ML-DSA and SLH-DSA providers, with capability discovery and explicit unavailable-provider behavior.
- **Secure vault:** authenticated file encryption with AES-256-GCM, per-object data keys, wrapped-key envelopes, integrity metadata, and local storage.
- **Crypto inventory:** discover algorithms in configuration and record migration readiness.
- **Attack laboratory:** safe, bounded demonstrations using deliberately weak toy parameters; no production-key recovery or exploit automation.
- **Benchmark lab:** repeatable latency and throughput measurements with environment metadata.
- **Security intelligence:** transparent rule-based event scoring and optional local LLM explanation through Ollama (never required to run the core platform).
- **Observability:** structured health endpoints, Prometheus metrics, request IDs and audit events.
- **DevSecOps:** tests, linting, dependency checks, container build, SBOM and secret scanning workflows.

## Architecture

```text
 Next.js dashboard (optional UI)      Streamlit research console
                 |                              |
                 +----------- HTTPS / REST -----+
                                |
                         FastAPI gateway
                                |
      +-------------------------+--------------------------+
      |             |           |             |            |
  Research API   PQC adapter  Secure Vault  Inventory   Security API
      |             |           |             |            |
  LWE / RLWE    provider     AES-GCM +      PostgreSQL   Risk engine
  experiments   boundary     wrapped DEK   (optional)   + audit log
      |             |
      +-------------+--------------------------------------+
                                |
                       Background tasks (optional)
                     Redis / Celery / Kafka adapters
                                |
                Prometheus + Grafana + OpenTelemetry
```

The first milestone runs locally as a single FastAPI service with SQLite/local filesystem defaults. Distributed components are optional profiles, not required dependencies.

## Quick start

Requirements: Python 3.11+.

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
uvicorn quantumshield.api.main:app --reload
```

Open:
- API docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health
- Metrics: http://127.0.0.1:8000/metrics

Run tests:

```bash
pytest
ruff check .
mypy src
```

Run with Docker:

```bash
docker compose up --build
```

## API overview

| Area | Endpoint | Purpose |
|---|---|---|
| Health | `GET /health` | Liveness/readiness summary |
| Metrics | `GET /metrics` | Prometheus metrics |
| Research | `POST /api/v1/research/lwe` | Educational LWE round-trip |
| Research | `POST /api/v1/research/rlwe` | Educational negacyclic RLWE experiment |
| PQC | `GET /api/v1/pqc/providers` | Provider capabilities |
| Vault | `POST /api/v1/vault/encrypt` | Encrypt an uploaded file |
| Vault | `POST /api/v1/vault/decrypt` | Decrypt a vault object |
| Attacks | `POST /api/v1/lab/noise-sweep` | Bounded toy noise experiment |
| Benchmarks | `POST /api/v1/benchmarks/run` | Run a small reproducible benchmark |
| Security | `GET /api/v1/security/summary` | Recent security event summary |
| Inventory | `GET /api/v1/inventory` | Cryptographic asset inventory |

See [docs/API.md](docs/API.md), [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), and [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md).

## Security model and limitations

- AES-GCM is used for file confidentiality and integrity. Nonces are unique per encryption operation.
- File keys are random data-encryption keys. Local development wraps them with a master key supplied through `QUANTUMSHIELD_MASTER_KEY`; do not commit this value.
- A local filesystem vault is for development and controlled demonstrations, not multi-tenant production storage.
- The default PQC adapter reports availability honestly; it does not silently fall back to home-grown implementations.
- Toy LWE/RLWE and the attack lab are not cryptographic products and do not establish security levels.
- Do not upload sensitive data to an unreviewed deployment.

Read [SECURITY.md](SECURITY.md) before reporting vulnerabilities.

## Roadmap

1. Reproducible research primitives and tests.
2. Vault, key-envelope design and auditability.
3. PQC provider integration and interoperability tests.
4. Risk analytics, inventory and benchmarks.
5. Optional distributed deployment and UI.
6. Independent security review and production-hardening.

## License

Apache-2.0. See [LICENSE](LICENSE).
