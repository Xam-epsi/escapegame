# tests/test_joueur1.py
import pytest
import time
from fastapi.testclient import TestClient
from backend.main import app
from backend import globals

client = TestClient(app)

# --------------------- PUZZLE ---------------------
def test_puzzle_image():
    res = client.get("/puzzle/image")
    assert res.status_code == 200
    assert res.headers["content-type"] in ["image/png", "application/octet-stream"]

def test_puzzle_validate_correct():
    globals.TIMER_STARTED_AT = None
    payload = {"positions": list(range(9))}
    res = client.post("/puzzle/validate", json=payload)
    assert res.status_code == 200
    assert "message" in res.json()

def test_puzzle_validate_incorrect():
    globals.TIMER_STARTED_AT = None
    payload = {"positions": [8,7,6,5,4,3,2,1,0]}
    res = client.post("/puzzle/validate", json=payload)
    assert res.status_code == 400
    data = res.json()
    assert "message" in data or "detail" in data

# --------------------- COUNTRY CSV ---------------------
def test_get_country_ru_authenticated():
    res = client.get("/country/RU", headers={"X-Auth-A":"1"})
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]

def test_get_country_ru_unauthenticated():
    res = client.get("/country/RU")
    assert res.status_code == 401

def test_get_country_unknown():
    res = client.get("/country/ZZ")
    assert res.status_code in [404,500]

# --------------------- PREDICT ---------------------
def test_predict_success():
    sample = {"lat":61.2345,"lon":30.1234,"capacity":50000,"year":1998}
    res = client.post("/predict", json=sample)
    if globals.MODEL is None:
        assert res.status_code == 500
    else:
        assert res.status_code == 200
        assert "score" in res.json()

# --------------------- VALIDATE SCORES ---------------------
def test_validate_scores_success():
    # utilise un score raisonnable pour passer
    payload = {"scores":[{"site_code":"RU-0001","score":50},{"site_code":"RU-0002","score":40}]}
    res = client.post("/validate", json=payload)
    if globals.MODEL is None:
        assert res.status_code == 500
    else:
        # top score = RU-0001
        assert res.status_code == 200 or res.status_code == 400

def test_validate_scores_empty():
    payload = {"scores":[]}
    res = client.post("/validate", json=payload)
    assert res.status_code == 400

# --------------------- FINAL ACTION ---------------------
def test_final_success_fail():
    site = "RU-0001"
    globals.CURRENT_SECRETS[site] = "123456"
    # success
    payload = {"site_code": site, "code_a": "123456"}
    res = client.post("/final", json=payload)
    assert res.status_code == 200
    assert res.json()["result"] == "success"
    # fail
    payload = {"site_code": site, "code_a": "000000"}
    res = client.post("/final", json=payload)
    assert res.status_code == 200
    assert res.json()["result"] == "fail"

def test_final_unknown_site():
    payload = {"site_code":"RU-9999","code_a":"123456"}
    res = client.post("/final", json=payload)
    assert res.status_code == 400

# --------------------- TIMER ---------------------
def test_timer_initialization():
    globals.TIMER_STARTED_AT = None
    res = client.get("/timer")
    assert res.status_code == 200
    assert "remaining" in res.json()

# --------------------- FRONTEND PAGES ---------------------
def test_frontend_pages():
    pages = ["/joueur1","/login","/select_country","/joueur2"]
    for page in pages:
        res = client.get(page)
        assert res.status_code == 200
        assert "text/html" in res.headers["content-type"]
# tests/test_joueur2.py
import pytest
import time
from fastapi.testclient import TestClient
from backend.main import app
from backend import globals

client = TestClient(app)

# --------------------- PUZZLE ---------------------
def test_puzzle_image_exists():
    res = client.get("/puzzle/image")
    assert res.status_code == 200

def test_puzzle_validate_edge_cases():
    # positions correctes
    payload = {"positions": list(range(9))}
    res = client.post("/puzzle/validate", json=payload)
    assert res.status_code == 200

    # positions incorrectes
    payload = {"positions": [1]*9}
    res = client.post("/puzzle/validate", json=payload)
    assert res.status_code == 400

# --------------------- COUNTRY CSV ---------------------
def test_country_headers():
    res = client.get("/country/RU", headers={"X-Auth-A":"1"})
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("text/csv")

# --------------------- PREDICT ---------------------
def test_predict_valid():
    payload = {"lat":61.2345,"lon":30.1234,"capacity":50000,"year":1998}
    res = client.post("/predict", json=payload)
    if globals.MODEL:
        assert res.status_code == 200
        assert "score" in res.json()
    else:
        assert res.status_code == 500

def test_predict_missing_model(monkeypatch):
    monkeypatch.setattr(globals, "MODEL", None)
    payload = {"lat":61.0,"lon":30.0,"capacity":1000,"year":2025}
    res = client.post("/predict", json=payload)
    assert res.status_code == 500

# --------------------- VALIDATE SCORES ---------------------
def test_validate_scores_range():
    payload = {"scores":[{"site_code":"RU-0001","score":-5}]}
    res = client.post("/validate", json=payload)
    assert res.status_code == 400

    payload = {"scores":[{"site_code":"RU-0001","score":150}]}
    res = client.post("/validate", json=payload)
    assert res.status_code == 400

# --------------------- FINAL ---------------------
def test_final_edge_cases():
    site = "RU-0002"
    globals.CURRENT_SECRETS[site] = "ABCDEF"

    # success
    payload = {"site_code": site, "code_a": "ABCDEF"}
    res = client.post("/final", json=payload)
    assert res.status_code == 200
    assert res.json()["result"] == "success"

    # fail
    payload = {"site_code": site, "code_a": "XYZ123"}
    res = client.post("/final", json=payload)
    assert res.status_code == 200
    assert res.json()["result"] == "fail"

# --------------------- TIMER ---------------------
def test_timer_behavior():
    globals.TIMER_STARTED_AT = None
    res = client.get("/timer")
    assert res.status_code == 200
    assert "remaining" in res.json()

# --------------------- FRONTEND ---------------------
def test_frontend_joueur_pages():
    urls = ["/joueur1","/joueur2","/login","/select_country"]
    for u in urls:
        res = client.get(u)
        assert res.status_code == 200
