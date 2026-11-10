"""Shared API schemas."""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str


class LWERequest(BaseModel):
    message: int = Field(ge=0, le=1)
    dimension: int = Field(default=32, ge=4, le=256)
    modulus: int = Field(default=257, ge=17, le=4093)
    noise_bound: int = Field(default=1, ge=0, le=3)
    seed: int = Field(default=7, ge=0, le=2**31 - 1)


class RLWERequest(BaseModel):
    message: list[int] = Field(min_length=1, max_length=64)
    degree: int = Field(default=16, ge=4, le=64)
    modulus: int = Field(default=257, ge=17, le=4093)
    noise_bound: int = Field(default=1, ge=0, le=3)
    seed: int = Field(default=7, ge=0, le=2**31 - 1)


class NoiseSweepRequest(BaseModel):
    dimensions: list[int] = Field(default=[8, 16, 32], min_length=1, max_length=8)
    trials: int = Field(default=100, ge=10, le=2000)
    noise_bounds: list[int] = Field(default=[0, 1, 2], min_length=1, max_length=5)
    seed: int = 1234


class BenchmarkRequest(BaseModel):
    iterations: int = Field(default=100, ge=1, le=5000)
    payload_bytes: int = Field(default=1024, ge=16, le=1_000_000)


class SecurityEvent(BaseModel):
    category: str
    severity: str
    description: str
    score: int = Field(ge=0, le=100)
