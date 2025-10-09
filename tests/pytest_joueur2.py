# tests/pytest_joueur2.py
import pytest
import pandas as pd
from fastapi.testclient import TestClient
from backend import main
from backend.models.ia_model import train_or_load_model, CSV_PATH
from backend.utils.loader import load_mapping_codes

# -------------------- Initialisation --------------------
# Charger modèle et mapping si non présent
if main.globals.MODEL is None:
    main.globals.MODEL = train_or_load_model(CSV_PATH)
main.globals.MAPPING = load_mapping_codes()

client = TestClient(main.app)

# -------------------- Tests pages frontend --------------------
def test_joueur2_page_loads():
    res = client.get("/joueur2")
    assert res.status_code == 200
    assert "<html" in res.text.lower()

def test_select_country_pages():
    res = client.get("/select_country")
    assert res.status_code == 200
    res2 = client.get("/select_country/choose/russie")
    # redirection vers login
    assert res2.status_code in (200, 307, 308)

def test_login_page_loads():
    res = client.get("/login")
    assert res.status_code == 200
    assert "<html" in res.text.lower()

# -------------------- Tests predict --------------------
def test_predict_with_valid_data():
    df = pd.read_csv(CSV_PATH, sep=";")
    row = df.iloc[0]
    payload = {
        "lat": float(row["lat"]),
        "lon": float(row["lon"]),
        "capacity": float(row["capacity"]),
        "year": int(row["year"])
    }
    res = client.post("/predict", json=payload)
    if main.globals.MODEL:
        assert res.status_code == 200
        assert "score" in res.json()
    else:
        assert res.status_code == 500

def test_predict_missing_model(monkeypatch):
    monkeypatch.setattr(main.globals, "MODEL", None)
    payload = {"lat":61.0,"lon":30.0,"capacity":1000,"year":2025}
    res = client.post("/predict", json=payload)
    assert res.status_code == 500

# -------------------- Tests validate --------------------
def test_validate_with_scores():
    df = pd.read_csv(CSV_PATH, sep=";")
    # Injecter un code secret factice pour chaque site pour éviter l'échec
    for _, row in df.iterrows():
        main.globals.CURRENT_SECRETS[row["site_code"]] = "DUMMY123"
    # Utiliser des scores proches des scores calculés pour éviter 400
    payload = {"scores": [{"site_code": row["site_code"], "score": round(main.globals.MODEL.predict(pd.DataFrame([{
        "lat": float(row["lat"]),
        "lon": float(row["lon"]),
        "capacity": float(row["capacity"]),
        "year": int(row["year"])
    }]))[0]*100, 2)} for _, row in df.iterrows()]}
    res = client.post("/validate", json=payload)
    # Doit réussir car CURRENT_SECRETS est rempli
    assert res.status_code == 200
    assert "detected_site" in res.json()
    assert "code_secret" in res.json()

def test_validate_empty_scores():
    payload = {"scores": []}
    res = client.post("/validate", json=payload)
    assert res.status_code == 400

# -------------------- Tests final --------------------
def test_final_action_known_site():
    mapping = main.globals.MAPPING
    if not mapping:
        pytest.skip("Mapping vide")
    site, code = list(mapping.items())[0]
    # Injecter dans CURRENT_SECRETS pour que /final passe
    main.globals.CURRENT_SECRETS[site] = code
    payload = {"site_code": site, "code_a": code}
    res = client.post("/final", json=payload)
    assert res.status_code == 200
    assert res.json()["result"] == "success"

def test_final_action_fail():
    site = list(main.globals.MAPPING.keys())[0]
    main.globals.CURRENT_SECRETS[site] = main.globals.MAPPING[site]
    payload = {"site_code": site, "code_a": "WRONGCODE"}
    res = client.post("/final", json=payload)
    assert res.status_code == 200
    assert res.json()["result"] == "fail"

def test_final_unknown_site():
    payload = {"site_code":"RU-9999","code_a":"123456"}
    res = client.post("/final", json=payload)
    assert res.status_code == 400

# -------------------- Test timer --------------------
def test_timer_behavior():
    main.globals.TIMER_STARTED_AT = None
    res = client.get("/timer")
    assert res.status_code == 200
    assert "remaining" in res.json()
