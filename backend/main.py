import os
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from models.ia_model import train_or_load_model, predict_topk
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
        print("⚠️ Warning: modèle IA non chargé à l'initialisation:", e)
    # Charger mapping complet, léger
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
    code = code.upper()
    if code != "RU":
        path = os.path.join(DATA_DIR, f"pipelines_{code.lower()}.csv")
        if os.path.exists(path):
            return FileResponse(path, media_type="text/csv", filename=os.path.basename(path))
        raise HTTPException(status_code=404, detail="Aucune donnée pour ce pays (leurre)")
    # Russia
    if x_auth_a:
        path = os.path.join(DATA_DIR, "pipelines_ru.csv")
        if os.path.exists(path):
            return FileResponse(path, media_type="text/csv", filename="pipelines_ru.csv")
        raise HTTPException(status_code=500, detail="Fichier pipelines_ru.csv introuvable.")
    if x_auth_b:
        path = os.path.join(DATA_DIR, "pipelines_ru_cut.csv")
        if os.path.exists(path):
            return FileResponse(path, media_type="text/csv", filename="pipelines_ru_cut.csv")
        raise HTTPException(status_code=500, detail="Fichier pipelines_ru_cut.csv introuvable.")
    raise HTTPException(status_code=401, detail="Header d'authentification requis (X-Auth-A ou X-Auth-B).")

@app.post("/predict")
def predict(req: PredictRequest):
    global MODEL
    if MODEL is None:
        raise HTTPException(status_code=500, detail="Modèle IA non disponible.")
    try:
        results = predict_topk(MODEL, req.lat, req.lon, req.capacity, req.year, req.operator, k=req.k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"predictions": results}

class ValidatePayload(BaseModel):
    scores: List[dict]

@app.post("/validate")
def validate(payload: ValidatePayload):
    if not payload.scores:
        raise HTTPException(status_code=400, detail="Aucun score fourni")
    best = max(payload.scores, key=lambda x: x.get("score", 0))
    return {"detected_site": best.get("site_code"), "score": best.get("score")}

class FinalPayload(BaseModel):
    site_code: str
    code_a: str
    code_b: str

@app.post("/final")
def final_action(payload: FinalPayload):
    global MAPPING
    site = payload.site_code
    if site not in MAPPING:
        raise HTTPException(status_code=400, detail="site_code inconnu")
    expected = MAPPING.get(site)
    combined = (payload.code_a + payload.code_b).replace("*", "")
    if combined == expected:
        return {"result":"success", "message":"Pipeline sécurisé. Pollution évitée."}
    else:
        return {"result":"fail", "message":"Code incorrect. Fuite détectée."}
