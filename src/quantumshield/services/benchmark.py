"""Small, reproducible AES-GCM benchmark utility."""

import os
import statistics
import time

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def run_aes_benchmark(iterations: int, payload_bytes: int) -> dict:
    key = AESGCM.generate_key(bit_length=256)
    aes = AESGCM(key)
    payload = os.urandom(payload_bytes)
    samples: list[float] = []
    for _ in range(iterations):
        nonce = os.urandom(12)
        start = time.perf_counter()
        aes.encrypt(nonce, payload, b"quantumshield-benchmark")
        samples.append((time.perf_counter() - start) * 1000)
    total_seconds = sum(samples) / 1000
    return {
        "algorithm": "AES-256-GCM",
        "iterations": iterations,
        "payload_bytes": payload_bytes,
        "mean_ms": round(statistics.mean(samples), 4),
        "p50_ms": round(statistics.median(samples), 4),
        "p95_ms": round(sorted(samples)[min(len(samples) - 1, int(len(samples) * 0.95))], 4),
        "operations_per_second": round(iterations / total_seconds, 2) if total_seconds else 0,
        "note": "single-process microbenchmark; not a comparative security benchmark",
    }
