"""Toy RLWE polynomial relation; not a secure encryption implementation."""
from dataclasses import dataclass
import random
from quantumshield.crypto.polynomial import add,negacyclic_multiply
@dataclass(frozen=True)
class Params:
    n:int=16
    q:int=257
    noise:int=1
    def validate(self):
        if not 4<=self.n<=64 or not 17<=self.q<=4093 or not 0<=self.noise<=3: raise ValueError("parameters outside educational bounds")
@dataclass(frozen=True)
class PublicSample:
    a:tuple[int,...]
    b:tuple[int,...]
    secret:tuple[int,...]
def sample(params:Params,seed:int=7)->PublicSample:
    params.validate(); rng=random.Random(seed)
    s=tuple(rng.choice([-1,0,1])%params.q for _ in range(params.n))
    a=tuple(rng.randrange(params.q) for _ in range(params.n))
    e=[rng.randint(-params.noise,params.noise) for _ in range(params.n)]
    b=tuple((x+y)%params.q for x,y in zip(negacyclic_multiply(a,s,params.q),e,strict=True))
    return PublicSample(a,b,s)
def multiply_demo(a:list[int],b:list[int],q:int)->list[int]: return negacyclic_multiply(a,b,q)
