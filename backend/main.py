import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# --- IMPORT ROUTES ---
from backend.routes import frontend_routes, backend_routes

# --- IMPORT MODELES & UTILS ---
from backend.models.ia_model import train_or_load_model
from backend.utils.loader import load_mapping_codes
from backend import globals

# --- IMPORT CONFIGURATION AZURE ---
try:
    from azure_config import get_azure_config, AZURE_CONFIG
    azure_info = get_azure_config()
    print(f"🔵 Configuration Azure: {azure_info}")
except ImportError:
    azure_info = {"is_azure": False}
    print("🔵 Configuration Azure non disponible")

# ======================================================
# CONFIGURATION DE L’APPLICATION
# ======================================================
app = FastAPI(title="Pipeline Rescue Backend")

BASE_DIR = os.path.dirname(__file__)

# --- Chargement des globals ---
globals.MODEL = train_or_load_model()
globals.MAPPING = load_mapping_codes()
globals.DATA_DIR = os.path.join(BASE_DIR, "..", "data")

# --- Frontend ---
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")
app.mount("/static", StaticFiles(directory=os.path.join(FRONTEND_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(FRONTEND_DIR, "templates"))

# --- Middleware CORS ---
# Configuration CORS optimisée pour Azure
cors_origins = ["*"]
if azure_info.get("is_azure"):
    # Sur Azure, être plus restrictif avec les origines
    cors_origins = [
        "https://*.azurewebsites.net",
        "https://*.azurestaticapps.net", 
        "http://localhost:*",
        "https://localhost:*"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================================================
# ÉVÈNEMENT DE DÉMARRAGE
# ======================================================
@app.on_event("startup")
def startup_event():
    try:
        globals.MODEL = train_or_load_model()
        print("Modele IA charge avec succes.")
    except Exception as e:
        globals.MODEL = None
        print("Warning: modele IA non charge:", e)

    try:
        globals.MAPPING = load_mapping_codes()
        print("Mapping codes secrets charge.")
    except Exception as e:
        globals.MAPPING = {}
        print("Warning: mapping non charge:", e)

# ======================================================
# INCLUSION DES ROUTES
# ======================================================
app.include_router(frontend_routes.router)
app.include_router(backend_routes.router)
