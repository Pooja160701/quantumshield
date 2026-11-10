# API Reference

OpenAPI UI: `/docs`; base URL `http://127.0.0.1:8000`.

- `GET /health` — health and version.
- `GET /metrics` — Prometheus metrics.
- `POST /api/v1/research/lwe` — create an educational LWE public sample.
- `POST /api/v1/research/rlwe` — create an educational RLWE public sample.
- `GET /api/v1/pqc/providers` — detect available PQC provider and list algorithm identifiers.
- `POST /api/v1/lab/noise-sweep` — bounded noise distribution experiment.
- `POST /api/v1/benchmarks/run` — local AES-GCM microbenchmark.
- `POST /api/v1/vault/encrypt` — encrypt multipart file upload.
- `POST /api/v1/vault/decrypt/{object_id}` — decrypt vault object.
- `GET /api/v1/inventory` — starter cryptographic inventory.
- `GET /api/v1/security/summary` — current audit/risk implementation status.

Vault operations require `QUANTUMSHIELD_MASTER_KEY`, a URL-safe base64-encoded 32-byte random key. Generate it with:

```bash
python -c "import base64,secrets; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())"
```

LWE and RLWE endpoints are demonstrations, not secure encryption or security estimators.
