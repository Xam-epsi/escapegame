import os
import time
import random
import string
import tempfile
import shutil
from typing import Optional, List, Dict

import pandas as pd
from fastapi import FastAPI, HTTPException, Header, Request, File, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# --- IMPORTS MODELES IA ---
from backend.models.ia_model import train_or_load_model, predict_confidence
from backend.models.image_ia import verify_puzzle
from backend.utils.loader import load_mapping_codes

# ======================================================
# CONFIGURATION DE L’APPLICATION
# ======================================================
app = FastAPI(title="Pipeline Rescue Backend")

BASE_DIR = os.path.dirname(__file__)

# 🟢 Nouveau chemin vers le frontend
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")

# On monte le dossier "frontend/static"
app.mount("/static", StaticFiles(directory=os.path.join(FRONTEND_DIR, "static")), name="static")

# Et on indique à Jinja2 où trouver les templates
templates = Jinja2Templates(directory=os.path.join(FRONTEND_DIR, "templates"))

# ======================================================
# MIDDLEWARE
# ======================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ======================================================
# VARIABLES GLOBALES
# ======================================================
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
MODEL = None
MAPPING: Dict[str, str] = {}
TIMER_STARTED_AT: Optional[float] = None
TOTAL_DURATION = 30 * 60
CURRENT_SECRETS: Dict[str, str] = {}

# ======================================================
# ÉVÈNEMENT DE DÉMARRAGE
# ======================================================
@app.on_event("startup")
def startup_event():
    global MODEL, MAPPING
    try:
        MODEL = train_or_load_model()
        print("✅ Modèle IA chargé avec succès.")
    except Exception as e:
        MODEL = None
        print("⚠️ Warning: modèle IA non chargé:", e)

    try:
        MAPPING = load_mapping_codes()
        print("✅ Mapping codes secrets chargé.")
    except Exception as e:
        MAPPING = {}
        print("⚠️ Warning: mapping non chargé:", e)

# ======================================================
# SCHÉMAS Pydantic
# ======================================================
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
    code_a: str

class PuzzleValidateRequest(BaseModel):
    positions: List[int]

# ======================================================
# ROUTES FRONTEND
# ======================================================
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    """
    Page d'accueil : redirige directement vers le choix du pays.
    """
    return templates.TemplateResponse("select_country.html", {"request": request})

@app.get("/select_country", response_class=HTMLResponse)
def select_country(request: Request):
    """
    Page intermédiaire pour choisir le pays.
    """
    return templates.TemplateResponse("select_country.html", {"request": request})

@app.get("/select_country/choose/{country}", response_class=HTMLResponse)
def choose_country(request: Request, country: str):
    """
    Gère le choix du pays.
    - Russie → redirige vers login
    - Autres → pénalité de 5 minutes et reste sur select_country
    """
    global TIMER_STARTED_AT
    country = country.lower()
    if TIMER_STARTED_AT is None:
        TIMER_STARTED_AT = time.time()

    if country == "russie":
        # Redirige vers login pour keep/calm
        return RedirectResponse(url="/login")
    else:
        # pénalité 5 min
        PENALTY = 5*60
        TIMER_STARTED_AT -= PENALTY
        remaining = max(TOTAL_DURATION - int(time.time() - TIMER_STARTED_AT), 0)
        return templates.TemplateResponse(
            "select_country.html",
            {
                "request": request,
                "error": f"❌ Mauvais pays ! Temps réduit de 5 min. Temps restant: {remaining//60}:{remaining%60:02d}"
            }
        )

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    """
    Page de saisie du code 'keep' ou 'calm'.
    Accessible après sélection du pays.
    """
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/joueur1", response_class=HTMLResponse)
def joueur1_page(request: Request):
    """
    Interface Joueur 1 (complet) après code 'keep'.
    """
    return templates.TemplateResponse("joueur1.html", {"request": request})

@app.get("/joueur2", response_class=HTMLResponse)
def joueur2_page(request: Request):
    """
    Interface Joueur 2 (IA) après code 'calm'.
    """
    return templates.TemplateResponse("joueur2.html", {"request": request})

# ======================================================
# ROUTES PUZZLE
# ======================================================
@app.get("/puzzle/image")
def get_puzzle_image():
    path = os.path.join(DATA_DIR, "poutine_bears.png")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Image du puzzle manquante")
    return FileResponse(path)

@app.post("/puzzle/validate")
def puzzle_validate(payload: PuzzleValidateRequest):
    """Validation du puzzle avec pénalité si incorrect."""
    global TIMER_STARTED_AT
    if TIMER_STARTED_AT is None:
        TIMER_STARTED_AT = time.time()
    
    correct_order = list(range(9))
    if payload.positions != correct_order:
        PENALTY = 5*60
        TIMER_STARTED_AT -= PENALTY
        remaining = max(TOTAL_DURATION - int(time.time() - TIMER_STARTED_AT), 0)
        return JSONResponse(
            status_code=400,
            content={"message": "Puzzle incorrect !", "penalty": PENALTY, "remaining": remaining}
        )
    return {"message": "Puzzle validé ! Bravo 😎"}

# ======================================================
# ROUTES IA & VALIDATION PIPELINES
# ======================================================
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
    global MODEL, MAPPING, CURRENT_SECRETS, TIMER_STARTED_AT
    if MODEL is None:
        raise HTTPException(status_code=500, detail="Modèle IA non disponible.")
    if not payload.scores:
        raise HTTPException(status_code=400, detail="Aucun score fourni.")
    
    csv_path = os.path.join(DATA_DIR, "pipelines_ru.csv")
    if not os.path.exists(csv_path):
        raise HTTPException(status_code=500, detail="Fichier de données introuvable.")

    df = pd.read_csv(csv_path, sep=";")
    invalid_sites = []

    for s in payload.scores:
        try:
            entered = float(s.score)
        except Exception:
            raise HTTPException(status_code=400, detail=f"Score invalide pour {s.site_code}")
        if entered < 0 or entered > 100:
            raise HTTPException(status_code=400, detail=f"Score hors bornes (0-100) pour {s.site_code}")
        
        mask = df["site_code"].astype(str).str.strip() == str(s.site_code).strip()
        row = df[mask]
        if row.empty:
            invalid_sites.append((s.site_code, entered, None))
            continue

        r = row.iloc[0]
        try:
            real_score = predict_confidence(MODEL, float(r["lat"]), float(r["lon"]),
                                            float(r["capacity"]), int(r["year"]))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur calcul IA pour {s.site_code}: {e}")
        real_pct = float(round(real_score * 100, 2))
        if abs(real_pct - entered) > 10.0:
            invalid_sites.append((s.site_code, entered, real_pct))

    if invalid_sites:
        PENALTY = 5*60
        now = time.time()
        if TIMER_STARTED_AT is None:
            TIMER_STARTED_AT = now - PENALTY
        else:
            TIMER_STARTED_AT -= PENALTY

        remaining = max(TOTAL_DURATION - int(time.time() - TIMER_STARTED_AT), 0)

        # ⚠️ Nouveau message sans révéler les valeurs attendues
        msg = "⚠️ Certains scores sont incohérents. Temps réduit de 5 minutes."

        # on ne précise pas le détail des sites
        detail = {"message": msg, "penalty": PENALTY, "remaining": remaining}
        raise HTTPException(status_code=400, detail=detail)


    best = max(payload.scores, key=lambda x: float(x.score))
    detected = best.site_code
    secret = MAPPING.get(detected, ''.join(random.choices(string.ascii_uppercase + string.digits, k=6)))
    CURRENT_SECRETS[detected] = secret

    return {"detected_site": detected, "code_secret": secret, "score": float(best.score)}

@app.post("/final")
def final_action(payload: FinalPayload):
    """Vérifie le code final envoyé par le Joueur 2 et stoppe le timer si correct."""
    global CURRENT_SECRETS, MAPPING, TIMER_STARTED_AT
    site = payload.site_code
    if not site:
        raise HTTPException(status_code=400, detail="site_code requis")

    expected = CURRENT_SECRETS.get(site) or MAPPING.get(site)
    if expected is None:
        raise HTTPException(status_code=400, detail="Aucun code attendu pour ce site (pas validé).")

    if payload.code_a == expected:
        # ✅ Stop le timer
        TIMER_STARTED_AT = None
        return {"result": "success", "message": "✅ Pipeline sécurisé. Pollution évitée."}
    else:
        return {"result": "fail", "message": "❌ Code incorrect. Fuite détectée."}


# ======================================================
# TIMER
# ======================================================
@app.get("/timer")
def get_timer():
    global TIMER_STARTED_AT
    if TIMER_STARTED_AT is None:
        TIMER_STARTED_AT = time.time()
    elapsed = int(time.time() - TIMER_STARTED_AT)
    remaining = max(TOTAL_DURATION - elapsed, 0)
    return {"remaining": remaining}
