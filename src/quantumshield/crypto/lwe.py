"""Pedagogical LWE relation demo; absolutely not production cryptography."""
from dataclasses import dataclass
import random
@dataclass(frozen=True)
class Params:
    n:int=32
    q:int=257
    noise:int=1
    def validate(self):
        if not 4<=self.n<=256 or not 17<=self.q<=4093 or not 0<=self.noise<=3: raise ValueError("parameters outside educational bounds")
@dataclass(frozen=True)
class Sample:
    a:tuple[int,...]
    b:int
    secret:tuple[int,...]
def sample(params:Params,seed:int=7)->Sample:
    params.validate(); rng=random.Random(seed)
    s=tuple(rng.randrange(params.q) for _ in range(params.n))
    a=tuple(rng.randrange(params.q) for _ in range(params.n))
    e=rng.randint(-params.noise,params.noise)
    b=(sum(x*y for x,y in zip(a,s,strict=True))+e)%params.q
    return Sample(a,b,s)
def noise_experiment(params:Params,trials:int=100,seed:int=1)->dict:
    params.validate()
    if not 1<=trials<=2000: raise ValueError("trials outside bounded range")
    rng=random.Random(seed); values=[rng.randint(-params.noise,params.noise) for _ in range(trials)]
    return {"trials":trials,"min":min(values),"max":max(values),"mean":sum(values)/trials,"toy_only":True}
