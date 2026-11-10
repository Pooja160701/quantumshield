"""Honest PQC provider capability discovery; no homemade algorithm fallback."""
from dataclasses import asdict,dataclass
import importlib.util
@dataclass(frozen=True)
class Capability:
    algorithm:str
    standard:str
    purpose:str
    available:bool
def discover()->list[dict]:
    available=importlib.util.find_spec("oqs") is not None
    items=[
        Capability(n,"FIPS 203","key-establishment",available)
        for n in ("ML-KEM-512","ML-KEM-768","ML-KEM-1024")
    ]+[Capability(n,"FIPS 204","digital-signature",available) for n in ("ML-DSA-44","ML-DSA-65","ML-DSA-87")]
    items += [Capability("SLH-DSA","FIPS 205","digital-signature",available)]
    return [asdict(x)|{"status":"provider-detected" if x.available else "provider-unavailable"} for x in items]
