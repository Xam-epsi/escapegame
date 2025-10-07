# tests/test_api_routes.py
import pytest
import pandas as pd
from backend.models.ia_model import train_or_load_model, CSV_PATH
from backend.utils.loader import load_mapping_codes
import backend.main as main
from fastapi.testclient import TestClient

import os
print("Mapping path:", os.path.join(os.path.dirname(main.__file__), "..", "data", "mapping_codes.csv"))
print("Exists:", os.path.exists(os.path.join(os.path.dirname(main.__file__), "..", "data", "mapping_codes.csv")))


# Charger le modèle pour que /predict fonctionne
if main.MODEL is None:
    main.MODEL = train_or_load_model(CSV_PATH)

client = TestClient(main.app)

# Charger CSV et opérateurs
df = pd.read_csv(CSV_PATH, sep=";")
operators = df["operator"].dropna().unique().tolist()
valid_operator = operators[0] if operators else "dummy"

# Charger mapping complet
MAPPING = load_mapping_codes()
main.MAPPING = MAPPING  # injecte dans l'API pour final_action

def test_predict_success():
    payload = {
        "lat": float(df.iloc[0]["lat"]),
        "lon": float(df.iloc[0]["lon"]),
        "capacity": float(df.iloc[0]["capacity"]),
        "year": int(df.iloc[0]["year"]),
        "operator": valid_operator,
        "k": 3
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    assert "predictions" in response.json()
    preds = response.json()["predictions"]
    assert isinstance(preds, list)
    assert len(preds) > 0

def test_predict_model_missing(monkeypatch):
    # Simule un modèle manquant
    monkeypatch.setattr(main, "MODEL", None)
    payload = {
        "lat": 61.0,
        "lon": 30.0,
        "capacity": 50000,
        "year": 2025,
        "operator": valid_operator,
        "k": 3
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 500
    assert response.json()["detail"] == "Modèle IA non disponible."

def test_validate_success():
    payload = {"scores":[{"site_code":"RU-0001","score":0.8},{"site_code":"RU-0002","score":0.5}]}
    response = client.post("/validate", json=payload)
    assert response.status_code == 200
    assert response.json()["detected_site"] == "RU-0001"

def test_validate_empty():
    payload = {"scores":[]}
    response = client.post("/validate", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Aucun score fourni"

def test_final_success():
    if not MAPPING:
        pytest.skip("Mapping vide, impossible de tester final_success")
    site, code = list(MAPPING.items())[0]
    payload = {"site_code": site, "code_a": code[:2], "code_b": code[2:]}
    response = client.post("/final", json=payload)
    assert response.status_code == 200
    assert response.json()["result"] == "success"

def test_final_fail():
    if not MAPPING:
        pytest.skip("Mapping vide, impossible de tester final_fail")
    site = "RU-0001" if "RU-0001" in MAPPING else list(MAPPING.keys())[0]
    payload = {"site_code": site, "code_a": "12", "code_b": "34"}  # mauvais code
    response = client.post("/final", json=payload)
    # Doit rester 200 même si le code est faux
    assert response.status_code == 200
    assert response.json()["result"] == "fail"

def test_final_unknown_site():
    payload = {"site_code": "RU-9999", "code_a": "12", "code_b": "34"}
    response = client.post("/final", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "site_code inconnu"
