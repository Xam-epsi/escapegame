# backend/main.py
import os
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from pydantic import BaseModel
from typing import Optional, List
from backend.models.ia_model import train_or_load_model, predict_topk
from backend.utils.loader import load_csv_for_country, load_mapping_codes

app = FastAPI(title="Pipeline Rescue Backend")

# CORS pour dev local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
MODEL = None
MAPPING = {}

@app.on_event("startup")
def startup_event():
    global MODEL, MAPPING
    try:
        MODEL = train_or_load_model()
    except Exception as e:
        MODEL = None
        # print sur console pour debug, et laisser l'API vivante
        print("⚠️ Warning: modèle IA non chargé à l'initialisation:", e)
    # mapping est léger => on le charge toujours (ou vide si absent)
    MAPPING = load_mapping_codes()


class PredictRequest(BaseModel):
    lat: float
    lon: float
    capacity: float
    operator: str
    year: int
    k: Optional[int] = 3

@app.get("/country/{code}")
def get_country(code: str, x_auth_a: Optional[str] = Header(None), x_auth_b: Optional[str] = Header(None)):
    """
    Retourne le CSV correspondant au pays.
    Si country == RU et X-Auth-A présent -> retourne la version complète (pipelines_ru.csv)
    Si country == RU et X-Auth-B présent -> retourne la version amputée (pipelines_ru_cut.csv)
    Pour autres pays, retourne un petit CSV (leurres) ou vide.
    """
    code = code.upper()
    # Only Russia has real data in this prototype
    if code != "RU":
        # return empty placeholder CSV stored in data (or 404)
        df = load_csv_for_country(code)
        # if file exists return it
        path = os.path.join(DATA_DIR, f"pipelines_{code.lower()}.csv")
        if os.path.exists(path):
            return FileResponse(path, media_type="text/csv", filename=os.path.basename(path))
        raise HTTPException(status_code=404, detail="Aucune donnée pour ce pays (leurre)")
    # Russia
    if x_auth_a:
        path = os.path.join(DATA_DIR, "pipelines_ru.csv")
        if os.path.exists(path):
            return FileResponse(path, media_type="text/csv", filename="pipelines_ru.csv")
        raise HTTPException(status_code=500, detail="Fichier pipelines_ru.csv introuvable sur le serveur.")
    if x_auth_b:
        path = os.path.join(DATA_DIR, "pipelines_ru_cut.csv")
        if os.path.exists(path):
            return FileResponse(path, media_type="text/csv", filename="pipelines_ru_cut.csv")
        raise HTTPException(status_code=500, detail="Fichier pipelines_ru_cut.csv introuvable sur le serveur.")
    raise HTTPException(status_code=401, detail="Header d'authentification requis (X-Auth-A ou X-Auth-B).")

@app.post("/predict")
def predict(req: PredictRequest):
    """
    Reçoit features et renvoie top-k predictions avec confidence.
    """
    global MODEL
    if MODEL is None:
        raise HTTPException(status_code=500, detail="Modèle IA non disponible.")
    try:
        results = predict_topk(MODEL, req.lat, req.lon, req.capacity, req.year, req.operator, k=req.k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"predictions": results}

class ValidatePayload(BaseModel):
    scores: List[dict]  # [{"site_code":"RU-0001", "score":0.12}, ...]

@app.post("/validate")
def validate(payload: ValidatePayload):
    """
    Vérifie la cohérence des scores. Pour prototype : on accepte la soumission
    et renvoie le site avec le score max.
    """
    if not payload.scores:
        raise HTTPException(status_code=400, detail="Aucun score fourni")
    # find max
    best = max(payload.scores, key=lambda x: x.get("score", 0))
    return {"detected_site": best.get("site_code"), "score": best.get("score")}

class FinalPayload(BaseModel):
    site_code: str
    code_a: str
    code_b: str

@app.post("/final")
def final_action(payload: FinalPayload):
    """
    Vérifie les deux codes de désactivation en comparant mapping.
    mapping_codes.csv doit exister dans data.
    """
    global MAPPING
    site = payload.site_code
    if site not in MAPPING:
        raise HTTPException(status_code=400, detail="site_code inconnu")
    expected = MAPPING.get(site)
    # expected is full 4-digit; we assume code_a + code_b concatened must equal expected
    combined = (payload.code_a + payload.code_b).replace("*", "")
    if combined == expected:
        return {"result":"success", "message":"Pipeline sécurisé. Pollution évitée."}
    else:
        return {"result":"fail", "message":"Code incorrect. Fuite détectée."}
