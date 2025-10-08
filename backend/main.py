import os
import time
import random
import string
from typing import Optional, List, Dict

import pandas as pd
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# Import du modèle IA (ton fichier ia_model.py)
from backend.models.ia_model import train_or_load_model, predict_confidence
from backend.utils.loader import load_mapping_codes

# --- CONFIG APP ---
app = FastAPI(title="Pipeline Rescue Backend")

BASE_DIR = os.path.dirname(__file__)
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# --- CORS ---
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
MAPPING: Dict[str, str] = {}
# Timer partagé (timestamp de démarrage)
TIMER_STARTED_AT: Optional[float] = None
TOTAL_DURATION = 30 * 60  # 30 minutes en secondes
# Secrets générés à la validation (site_code -> secret)
CURRENT_SECRETS: Dict[str, str] = {}

# --- STARTUP ---
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

# --- SCHEMAS ---
class PredictRequest(BaseModel):
    lat: float
    lon: float
    capacity: float
    year: int

class ScoreItem(BaseModel):
    site_code: str
    score: float

class ValidatePayload(BaseModel):
    scores: List[ScoreItem]

class FinalPayload(BaseModel):
    site_code: str
    code_a: str  # code secret

# --- ROUTES FRONTEND ---
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/joueur1", response_class=HTMLResponse)
def joueur1_page(request: Request):
    return templates.TemplateResponse("joueur1.html", {"request": request})

@app.get("/joueur2", response_class=HTMLResponse)
def joueur2_page(request: Request):
    return templates.TemplateResponse("joueur2.html", {"request": request})

# --- ROUTES API ---
@app.get("/country/{code}")
def get_country(code: str, x_auth_a: Optional[str] = Header(None)):
    code = code.upper()
    if code != "RU":
        path = os.path.join(DATA_DIR, f"pipelines_{code.lower()}.csv")
        if os.path.exists(path):
            return FileResponse(path, media_type="text/csv", filename=os.path.basename(path))
        raise HTTPException(status_code=404, detail="Aucune donnée pour ce pays (leurre)")
    if x_auth_a:
        path = os.path.join(DATA_DIR, "pipelines_ru.csv")
        if os.path.exists(path):
            return FileResponse(path, media_type="text/csv", filename="pipelines_ru.csv")
        raise HTTPException(status_code=500, detail="Fichier pipelines_ru.csv introuvable.")
    raise HTTPException(status_code=401, detail="Header d'authentification requis (X-Auth-A).")

@app.post("/predict")
def predict(req: PredictRequest):
    global MODEL
    if MODEL is None:
        raise HTTPException(status_code=500, detail="Modèle IA non disponible.")
    try:
        score = predict_confidence(MODEL, req.lat, req.lon, req.capacity, req.year)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"score": score}

@app.post("/validate")
def validate(payload: ValidatePayload):
    """
    Valide le tableau complet :
     - vérifie que toutes les lignes ont un score (0-100)
     - recalcul le score réel via le modèle IA pour chaque site
     - si un (ou plusieurs) score(s) divergent de plus de 10 points, applique une pénalité de -5 min
       et retourne une erreur détaillée (sans révéler le pipeline ni le code)
     - sinon, retourne le site détecté (score max) et le code secret
    """
    global MODEL, MAPPING, CURRENT_SECRETS, TIMER_STARTED_AT

    if MODEL is None:
        raise HTTPException(status_code=500, detail="Modèle IA non disponible.")

    if not payload.scores:
        raise HTTPException(status_code=400, detail="Aucun score fourni.")

    # path CSV
    csv_path = os.path.join(DATA_DIR, "pipelines_ru.csv")
    if not os.path.exists(csv_path):
        raise HTTPException(status_code=500, detail="Fichier de données introuvable.")

    df = pd.read_csv(csv_path, sep=";")
    invalid_sites = []

    for s in payload.scores:
        # validation basique
        try:
            entered = float(s.score)
        except Exception:
            raise HTTPException(status_code=400, detail=f"Score invalide pour {s.site_code}")

        if entered < 0 or entered > 100:
            raise HTTPException(status_code=400, detail=f"Score hors bornes (0-100) pour {s.site_code}")

        # recherche de la ligne dans le CSV
        mask = df["site_code"].astype(str).str.strip() == str(s.site_code).strip()
        row = df[mask]
        if row.empty:
            # pas de données pour comparer -> on marque comme invalide (optionnel)
            invalid_sites.append((s.site_code, entered, None))
            continue

        r = row.iloc[0]
        try:
            real_score = predict_confidence(MODEL, float(r["lat"]), float(r["lon"]), float(r["capacity"]), int(r["year"]))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur calcul IA pour {s.site_code}: {e}")
        # predict_confidence renvoie [0..1], on convertit en pourcentage
        real_pct = float(round(real_score * 100, 2))

        # tolérance (en points de pourcentage)
        TOLERANCE = 10.0
        if abs(real_pct - entered) > TOLERANCE:
            invalid_sites.append((s.site_code, entered, real_pct))

    if invalid_sites:
        # appliquer pénalité : -5 minutes
        PENALTY = 5 * 60  # secondes
        now = time.time()
        if TIMER_STARTED_AT is None:
            # si timer non démarré, démarre le timer mais avec pénalité appliquée
            TIMER_STARTED_AT = now - PENALTY
        else:
            # recule l'instant de départ pour augmenter l'elapsed (donc réduire remaining)
            TIMER_STARTED_AT = TIMER_STARTED_AT - PENALTY

        remaining = max(TOTAL_DURATION - int(time.time() - TIMER_STARTED_AT), 0)

        # construire message lisible
        lines = []
        for site, entered, expected in invalid_sites:
            if expected is None:
                lines.append(f"{site} (entré={entered}, données introuvables)")
            else:
                lines.append(f"{site} (entré={entered}, attendu≈{expected})")
        msg = "Certains scores sont incohérents : " + " · ".join(lines)

        # Renvoie une erreur détaillée (detail -> objet JSON)
        detail = {"message": msg, "penalty": PENALTY, "remaining": remaining}
        raise HTTPException(status_code=400, detail=detail)

    # tout est bon -> déterminer le site avec score max (selon valeurs saisies)
    best = max(payload.scores, key=lambda x: float(x.score))
    detected = best.site_code

    # récupère le code à partir du mapping si présent sinon génère et mémorise
    if detected in MAPPING:
        secret = MAPPING[detected]
    else:
        secret = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    CURRENT_SECRETS[detected] = secret

    return {"detected_site": detected, "code_secret": secret, "score": float(best.score)}

@app.post("/final")
def final_action(payload: FinalPayload):
    """Vérifie le code final fourni par Joueur B"""
    global CURRENT_SECRETS, MAPPING
    site = payload.site_code
    if not site:
        raise HTTPException(status_code=400, detail="site_code requis")

    expected = CURRENT_SECRETS.get(site)
    if expected is None:
        expected = MAPPING.get(site)
        if expected is None:
            raise HTTPException(status_code=400, detail="Aucun code attendu pour ce site (pas validé).")

    if payload.code_a == expected:
        return {"result": "success", "message": "✅ Pipeline sécurisé. Pollution évitée."}
    else:
        return {"result": "fail", "message": "❌ Code incorrect. Fuite détectée."}

@app.get("/timer")
def get_timer():
    """Retourne le temps restant en secondes. Démarre le timer au premier appel."""
    global TIMER_STARTED_AT
    if TIMER_STARTED_AT is None:
        TIMER_STARTED_AT = time.time()
    elapsed = int(time.time() - TIMER_STARTED_AT)
    remaining = max(TOTAL_DURATION - elapsed, 0)
    return {"remaining": remaining}
