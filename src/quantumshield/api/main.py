"""QuantumShield FastAPI service."""
import base64,os,random,secrets,statistics,time
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI,File,HTTPException,UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST,Counter,generate_latest
from pydantic import BaseModel,Field
from quantumshield import __version__
from quantumshield.config import get_settings
from quantumshield.crypto.lwe import Params as LWEParams,sample as lwe_sample
from quantumshield.crypto.rlwe import Params as RLWEParams,sample as rlwe_sample
from quantumshield.crypto.providers import discover
from quantumshield.crypto.polynomial import negacyclic_multiply
from quantumshield.services.vault import Vault,VaultError
settings=get_settings(); REQUESTS=Counter("quantumshield_requests_total","HTTP requests",["method","path"])
@asynccontextmanager
async def lifespan(app):
    settings.data_dir.mkdir(parents=True,exist_ok=True); yield
app=FastAPI(title="QuantumShield API",version=__version__,description="PQC research and crypto-agility lab. Toy crypto is not production safe.",lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=[x.strip() for x in settings.allowed_origins.split(",") if x.strip()],allow_credentials=False,allow_methods=["GET","POST"],allow_headers=["*"])
@app.middleware("http")
async def metrics_middleware(request,call_next):
    response=await call_next(request); REQUESTS.labels(request.method,request.url.path).inc()
    response.headers["X-Content-Type-Options"]="nosniff"; response.headers["X-Frame-Options"]="DENY"; response.headers["Referrer-Policy"]="no-referrer"
    return response
@app.get("/health")
def health(): return {"status":"healthy","version":__version__,"environment":settings.env}
@app.get("/metrics",include_in_schema=False)
def metrics(): return Response(generate_latest(),media_type=CONTENT_TYPE_LATEST)
class LweIn(BaseModel):
    dimension:int=Field(32,ge=4,le=256); modulus:int=Field(257,ge=17,le=4093); noise_bound:int=Field(1,ge=0,le=3); seed:int=7
@app.post("/api/v1/research/lwe")
def research_lwe(body:LweIn):
    try: result=lwe_sample(LWEParams(body.dimension,body.modulus,body.noise_bound),body.seed)
    except ValueError as exc: raise HTTPException(422,str(exc)) from exc
    return {"scheme":"LWE-sample-demonstration","production_safe":False,"dimension":body.dimension,"modulus":body.modulus,"public_sample":{"a":result.a,"b":result.b},"disclaimer":"Educational sample only; not encryption and not a security estimate."}
class RlweIn(BaseModel):
    degree:int=Field(16,ge=4,le=64); modulus:int=Field(257,ge=17,le=4093); noise_bound:int=Field(1,ge=0,le=3); seed:int=7
@app.post("/api/v1/research/rlwe")
def research_rlwe(body:RlweIn):
    try: result=rlwe_sample(RLWEParams(body.degree,body.modulus,body.noise_bound),body.seed)
    except ValueError as exc: raise HTTPException(422,str(exc)) from exc
    return {"scheme":"negacyclic-RLWE-sample-demonstration","production_safe":False,"degree":body.degree,"modulus":body.modulus,"public_sample":{"a":result.a,"b":result.b},"disclaimer":"Educational relation only; not a production encryption scheme."}
@app.get("/api/v1/pqc/providers")
def pqc_providers(): return {"algorithms":discover(),"note":"Provider presence is not certification or FIPS validation."}
@app.post("/api/v1/research/ntt-placeholder")
def arithmetic_placeholder(): return {"available":False,"reason":"NTT optimization is a future milestone; current exact negacyclic multiplication is O(n^2)."}
class NoiseIn(BaseModel):
    dimensions:list[int]=Field(default=[8,16,32],min_length=1,max_length=8); trials:int=Field(100,ge=10,le=2000); bounds:list[int]=Field(default=[0,1,2],min_length=1,max_length=5); seed:int=123
@app.post("/api/v1/lab/noise-sweep")
def noise_sweep(body:NoiseIn):
    rng=random.Random(body.seed); rows=[]
    if any(not 1<=n<=256 for n in body.dimensions) or any(not 0<=b<=3 for b in body.bounds): raise HTTPException(422,"values outside educational bounds")
    for n in body.dimensions:
        for bound in body.bounds:
            values=[rng.randint(-bound,bound) for _ in range(n*body.trials)]
            rows.append({"dimension":n,"noise_bound":bound,"samples":len(values),"mean":round(statistics.mean(values),5),"min":min(values),"max":max(values)})
    return {"results":rows,"disclaimer":"Toy noise sampling only; not an attack or security estimate."}
class BenchIn(BaseModel):
    iterations:int=Field(100,ge=1,le=5000); payload_bytes:int=Field(1024,ge=16,le=1000000)
@app.post("/api/v1/benchmarks/run")
def benchmark(body:BenchIn):
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    aes=AESGCM(AESGCM.generate_key(256)); payload=os.urandom(body.payload_bytes); values=[]
    for _ in range(body.iterations):
        start=time.perf_counter(); aes.encrypt(os.urandom(12),payload,b"qs-benchmark"); values.append((time.perf_counter()-start)*1000)
    return {"algorithm":"AES-256-GCM","iterations":body.iterations,"payload_bytes":body.payload_bytes,"mean_ms":round(statistics.mean(values),4),"p50_ms":round(statistics.median(values),4),"p95_ms":round(sorted(values)[min(len(values)-1,int(len(values)*.95))],4),"note":"Local microbenchmark, not cross-algorithm security evidence."}
def vault()->Vault:
    try: return Vault(settings.vault_dir,settings.master_key,settings.max_upload_bytes)
    except VaultError as exc: raise HTTPException(503,str(exc)) from exc
@app.post("/api/v1/vault/encrypt")
async def encrypt_file(file:UploadFile=File(...)):
    content=await file.read(settings.max_upload_bytes+1)
    if len(content)>settings.max_upload_bytes: raise HTTPException(413,"file too large")
    try: return vault().encrypt(file.filename or "upload.bin",content)
    except VaultError as exc: raise HTTPException(400,str(exc)) from exc
@app.post("/api/v1/vault/decrypt/{object_id}")
def decrypt_file(object_id:str):
    try: name,data=vault().decrypt(object_id)
    except VaultError as exc: raise HTTPException(404,str(exc)) from exc
    except Exception as exc: raise HTTPException(400,"decryption failed; invalid or tampered object") from exc
    return Response(data,media_type="application/octet-stream",headers={"Content-Disposition":f'attachment; filename="{name}"'})
@app.get("/api/v1/inventory")
def inventory():
    return {"assets":[{"name":"File encryption","algorithm":"AES-256-GCM","status":"implemented"},{"name":"Key wrapping","algorithm":"AES-256-GCM","status":"implemented-development-only"},{"name":"PQC key establishment","algorithm":"ML-KEM","status":"provider-dependent"},{"name":"PQC signatures","algorithm":"ML-DSA / SLH-DSA","status":"provider-dependent"},{"name":"Research primitives","algorithm":"toy LWE / RLWE","status":"education-only"}]}
@app.get("/api/v1/security/summary")
def security_summary():
    return {"events_recorded":0,"risk_score":None,"note":"Persistent audit/risk scoring is not yet implemented; no synthetic risk score is claimed."}
