"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest
from fastapi.responses import Response

from quantumshield import __version__
from quantumshield.config import get_settings
from quantumshield.crypto.lwe import LWEParameters, decrypt as lwe_decrypt, encrypt as lwe_encrypt, keygen as lwe_keygen
from quantumshield.crypto.providers import discover_algorithms
from quantumshield.crypto.rlwe import RLWEParameters, encrypt as rlwe_encrypt, keygen as rlwe_keygen
from quantumshield.models import BenchmarkRequest, HealthResponse, LWERequest, NoiseSweepRequest, RLWERequest
from quantumshield.services.benchmark import run_aes_benchmark
from quantumshield.services.inventory import list_assets
from quantumshield.services.security import record_event, summary
from quantumshield.services.vault import VaultConfigurationError, VaultError, VaultService

REQUESTS = Counter("quantumshield_api_requests_total", "API requests", ["method", "path"])


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title="QuantumShield API",
    description="Post-quantum research, crypto-agility and security operations. Toy cryptography is not production-safe.",
    version=__version__,
    lifespan=lifespan,
)
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.allowed_origins.split(",") if origin.strip()],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.middleware("http")
async def count_requests(request, call_next):
    response = await call_next(request)
    REQUESTS.labels(request.method, request.url.path).inc()
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


@app.get("/health", response_model=HealthResponse, tags=["operations"])
def health():
    return HealthResponse(status="healthy", version=__version__, environment=settings.env)


@app.get("/metrics", include_in_schema=False)
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/api/v1/research/lwe", tags=["research"])
def run_lwe(request: LWERequest):
    params = LWEParameters(request.dimension, request.modulus, request.noise_bound)
    try:
        key = lwe_keygen(params, request.seed)
        ciphertext = lwe_encrypt(request.message, key, params, request.seed + 1)
        recovered = lwe_decrypt(ciphertext, key.secret, params)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {
        "scheme": "toy-LWE-demonstration",
        "production_safe": False,
        "dimension": params.dimension,
        "modulus": params.modulus,
        "ciphertext": {"u": list(ciphertext.u), "v": ciphertext.v},
        "recovered_message": recovered,
        "correct": recovered == request.message,
    }


@app.post("/api/v1/research/rlwe", tags=["research"])
def run_rlwe(request: RLWERequest):
    params = RLWEParameters(request.degree, request.modulus, request.noise_bound)
    if len(request.message) != request.degree or any(bit not in (0, 1) for bit in request.message):
        raise HTTPException(status_code=422, detail="message must contain degree bits")
    try:
        key = rlwe_keygen(params, request.seed)
        c0, c1 = rlwe_encrypt(request.message, key, params, request.seed + 1)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {
        "scheme": "toy-RLWE-arithmetic-demonstration",
        "production_safe": False,
        "degree": params.degree,
        "modulus": params.modulus,
        "ciphertext": {"c0": c0, "c1": c1},
        "note": "Arithmetic exercise only; no secure RLWE decryption/parameter claim is made.",
    }


@app.get("/api/v1/pqc/providers", tags=["pqc"])
def pqc_providers():
    return {"algorithms": [item.__dict__ for item in discover_algorithms()],
            "security_note": "Provider presence is not validation or certification."}


@app.post("/api/v1/vault/encrypt", tags=["vault"])
async def vault_encrypt(file: UploadFile = File(...)):
    content = await file.read(settings.max_upload_bytes + 1)
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="file exceeds upload limit")
    try:
        service = VaultService(settings.vault_dir, settings.master_key, settings.max_upload_bytes)
        result = service.encrypt(file.filename or "upload.bin", content)
    except VaultConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except VaultError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    record_event("vault.encrypt", f"Encrypted object {result['object_id']}", "info")
    return result


@app.post("/api/v1/vault/decrypt/{object_id}", tags=["vault"])
def vault_decrypt(object_id: str):
    try:
        service = VaultService(settings.vault_dir, settings.master_key, settings.max_upload_bytes)
        filename, content = service.decrypt(object_id)
    except VaultConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except VaultError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail="decryption failed; object may be corrupt") from exc
    from fastapi.responses import Response
    return Response(content=content, media_type="application/octet-stream",
                    headers={"Content-Disposition": f'attachment; filename="{filename}"'})


@app.post("/api/v1/lab/noise-sweep", tags=["attack-lab"])
def noise_sweep(request: NoiseSweepRequest):
    # A bounded educational experiment: samples signed noise only, no secret recovery.
    import random
    rng = random.Random(request.seed)
    results = []
    for dimension in request.dimensions:
        if not 1 <= dimension <= 256:
            raise HTTPException(status_code=422, detail="dimensions must be between 1 and 256")
        for bound in request.noise_bounds:
            if not 0 <= bound <= 3:
                raise HTTPException(status_code=422, detail="noise bounds must be between 0 and 3")
            values = [rng.randint(-bound, bound) for _ in range(request.trials * dimension)]
            results.append({
                "dimension": dimension, "noise_bound": bound,
                "samples": len(values), "observed_min": min(values),
                "observed_max": max(values),
                "mean": round(sum(values) / len(values), 5),
                "note": "noise-distribution demonstration, not an attack or security estimate",
            })
    return {"results": results}


@app.post("/api/v1/benchmarks/run", tags=["benchmarks"])
def benchmark(request: BenchmarkRequest):
    return run_aes_benchmark(request.iterations, request.payload_bytes)


@app.get("/api/v1/security/summary", tags=["security"])
def security_summary():
    return summary()


@app.get("/api/v1/inventory", tags=["inventory"])
def inventory():
    return {"assets": list_assets()}
