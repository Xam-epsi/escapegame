import os
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List

# Importations internes
from backend.models.ia_model import train_or_load_model, predict_topk
from backend.utils.loader import load_csv_for_country, load_mapping_codes

# --- CONFIG APP ---
app = FastAPI(title="Pipeline Rescue Backend")

# Servir les fichiers statiques et les templates
BASE_DIR = os.path.dirname(__file__)
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# --- CORS (pour développement local) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- VARIABLES GLOBALES ---
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
MODEL = None
MAPPING = {}

# --- ÉVÉNEMENT STARTUP ---
@app.on_event("startup")
def startup_event():
    global MODEL, MAPPING
    try:
        MODEL = train_or_load_model()
    except Exception as e:
        MODEL = None
        print("⚠️ Warning: modèle IA non chargé à l'initialisation:", e)

    try:
        MAPPING = load_mapping_codes()
    except Exception as e:
        MAPPING = {}
        print("⚠️ Warning: mapping non chargé:", e)


# --- SCHEMAS DE REQUÊTES ---
class PredictRequest(BaseModel):
    lat: float
    lon: float
    capacity: float
    operator: str
    year: int
    k: Optional[int] = 3


class ValidatePayload(BaseModel):
    scores: List[dict]


class FinalPayload(BaseModel):
    site_code: str
    code_a: str
    code_b: str


# --- ROUTES FRONTEND ---
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    """Page d'accueil (login)"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/joueur1", response_class=HTMLResponse)
def joueur1_page(request: Request):
    """Page du Joueur 1"""
    return templates.TemplateResponse("joueur1.html", {"request": request, "csv_data": {}})


@app.get("/joueur2", response_class=HTMLResponse)
def joueur2_page(request: Request):
    """Page du Joueur 2"""
    return templates.TemplateResponse("joueur2.html", {"request": request})


# --- ROUTES API ---
@app.get("/country/{code}")
def get_country(code: str, x_auth_a: Optional[str] = Header(None), x_auth_b: Optional[str] = Header(None)):
    """Retourne le CSV du pays demandé (leurres pour pays ≠ Russie)"""
    code = code.upper()

    if code != "RU":
        path = os.path.join(DATA_DIR, f"pipelines_{code.lower()}.csv")
        if os.path.exists(path):
            return FileResponse(path, media_type="text/csv", filename=os.path.basename(path))
        raise HTTPException(status_code=404, detail="Aucune donnée pour ce pays (leurre)")

    # Russie → authentification par header
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
    """Retourne les prédictions IA (kNN)"""
    global MODEL
    if MODEL is None:
        raise HTTPException(status_code=500, detail="Modèle IA non disponible.")
    try:
        results = predict_topk(MODEL, req.lat, req.lon, req.capacity, req.year, req.operator, k=req.k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"predictions": results}


@app.post("/validate")
def validate(payload: ValidatePayload):
    """Valide les scores envoyés par les joueurs et détermine le meilleur site"""
    if not payload.scores:
        raise HTTPException(status_code=400, detail="Aucun score fourni")
    best = max(payload.scores, key=lambda x: x.get("score", 0))
    return {"detected_site": best.get("site_code"), "score": best.get("score")}


@app.post("/final")
def final_action(payload: FinalPayload):
    """Compare les codes finaux et détermine si la coupure est réussie"""
    global MAPPING
    site = payload.site_code
    if site not in MAPPING:
        raise HTTPException(status_code=400, detail="site_code inconnu")

    expected = MAPPING.get(site)
    combined = (payload.code_a + payload.code_b).replace("*", "")
    if combined == expected:
        return {"result": "success", "message": "✅ Pipeline sécurisé. Pollution évitée."}
    else:
        return {"result": "fail", "message": "❌ Code incorrect. Fuite détectée."}
