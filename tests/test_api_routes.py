# tests/test_api_routes.py
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.main import MODEL
from backend.models.ia_model import train_or_load_model, CSV_PATH

# s'assure que le modèle est chargé même si uvicorn n'est pas lancé
if MODEL is None:
    MODEL = train_or_load_model(CSV_PATH)

client = TestClient(app)

# --- TEST /predict ---
def test_predict_success():
    payload = {
        "lat": 61.0,
        "lon": 30.0,
        "capacity": 50000,
        "year": 2025,
        "operator": "Gazprom",
        "k": 3
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "predictions" in data
    assert isinstance(data["predictions"], list)
    # check top-1 has confidence float
    top1 = data["predictions"][0]
    assert "name" in top1 and "confidence" in top1
    assert isinstance(top1["confidence"], float)

def test_predict_model_missing(monkeypatch):
    # simulate MODEL = None
    from backend import main
    monkeypatch.setattr(main, "MODEL", None)
    payload = {
        "lat": 61.0,
        "lon": 30.0,
        "capacity": 50000,
        "year": 2025,
        "operator": "Gazprom"
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 500
    assert "Modèle IA non disponible" in response.text

# --- TEST /validate ---
def test_validate_success():
    payload = {
        "scores": [
            {"site_code": "RU-0001", "score": 0.12},
            {"site_code": "RU-0002", "score": 0.85},
            {"site_code": "RU-0003", "score": 0.43}
        ]
    }
    response = client.post("/validate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["detected_site"] == "RU-0002"
    assert data["score"] == 0.85

def test_validate_empty():
    payload = {"scores": []}
    response = client.post("/validate", json=payload)
    assert response.status_code == 400
    assert "Aucun score fourni" in response.text

# --- TEST /final ---
def test_final_success(monkeypatch):
    # simulate mapping
    from backend import main
    monkeypatch.setattr(main, "MAPPING", {"RU-0001": "5309"})
    payload = {"site_code": "RU-0001", "code_a": "53", "code_b": "09"}
    response = client.post("/final", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == "success"

def test_final_fail(monkeypatch):
    from backend import main
    monkeypatch.setattr(main, "MAPPING", {"RU-0001": "5309"})
    payload = {"site_code": "RU-0001", "code_a": "12", "code_b": "34"}
    response = client.post("/final", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == "fail"

def test_final_unknown_site():
    payload = {"site_code": "RU-9999", "code_a": "53", "code_b": "09"}
    response = client.post("/final", json=payload)
    assert response.status_code == 400
    assert "site_code inconnu" in response.text
