"""Arithmetic in Z_q[x]/(x^n + 1)."""
from collections.abc import Sequence
def negacyclic_multiply(a:Sequence[int],b:Sequence[int],modulus:int)->list[int]:
    if len(a)!=len(b) or not a: raise ValueError("polynomials must have equal non-zero length")
    if modulus<2: raise ValueError("modulus must be >= 2")
    n=len(a); out=[0]*n
    for i,x in enumerate(a):
        for j,y in enumerate(b):
            k=i+j; sign=1
            if k>=n: k-=n; sign=-1
            out[k]=(out[k]+sign*x*y)%modulus
    return out
def add(a:Sequence[int],b:Sequence[int],q:int)->list[int]:
    if len(a)!=len(b): raise ValueError("polynomials must have equal lengths")
    return [(x+y)%q for x,y in zip(a,b,strict=True)]
def subtract(a:Sequence[int],b:Sequence[int],q:int)->list[int]:
    if len(a)!=len(b): raise ValueError("polynomials must have equal lengths")
    return [(x-y)%q for x,y in zip(a,b,strict=True)]
