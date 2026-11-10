from fastapi.testclient import TestClient
from quantumshield.api.main import app
client=TestClient(app)

def test_health():
    r=client.get("/health")
    assert r.status_code==200 and r.json()["status"]=="healthy"

def test_pqc_provider_catalog():
    data=client.get("/api/v1/pqc/providers").json()
    assert len(data["algorithms"])>=7
    assert all("status" in item for item in data["algorithms"])

def test_lwe_experiment_disclaims_security():
    r=client.post("/api/v1/research/lwe",json={})
    assert r.status_code==200 and r.json()["production_safe"] is False

def test_noise_sweep_bounded():
    r=client.post("/api/v1/lab/noise-sweep",json={"dimensions":[8],"trials":10,"bounds":[1]})
    assert r.status_code==200 and r.json()["results"][0]["samples"]==80

def test_bad_noise_bounds_rejected():
    r=client.post("/api/v1/lab/noise-sweep",json={"dimensions":[8],"trials":10,"bounds":[4]})
    assert r.status_code==422
