from quantumshield.crypto.polynomial import add,negacyclic_multiply,subtract
from quantumshield.crypto.lwe import Params as LWEParams,sample as lwe_sample
from quantumshield.crypto.rlwe import Params as RLWEParams,sample as rlwe_sample

def test_polynomial_add_subtract():
    a=[1,2,3,4]; b=[4,3,2,1]
    assert subtract(add(a,b,17),b,17)==a

def test_negacyclic_wrap_sign():
    assert negacyclic_multiply([0,0,0,1],[0,1,0,0],17)==[16,0,0,0]

def test_lwe_deterministic():
    p=LWEParams()
    assert lwe_sample(p,42)==lwe_sample(p,42)

def test_rlwe_deterministic():
    p=RLWEParams()
    assert rlwe_sample(p,42)==rlwe_sample(p,42)
