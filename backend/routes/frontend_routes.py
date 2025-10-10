import time
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from backend import globals
from fastapi.templating import Jinja2Templates
import os

router = APIRouter()

BASE_DIR = os.path.dirname(__file__)
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "..", "frontend")
templates = Jinja2Templates(directory=os.path.join(FRONTEND_DIR, "templates"))

# ======================================================
# ROUTES FRONTEND
# ======================================================
@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("select_country.html", {"request": request})

@router.get("/select_country", response_class=HTMLResponse)
def select_country(request: Request):
    # Réinitialiser le timer pour une nouvelle partie
    globals.TIMER_STARTED_AT = None
    globals.GAME_COMPLETED = False
    return templates.TemplateResponse("select_country.html", {"request": request})

@router.get("/select_country/choose/{country}", response_class=HTMLResponse)
async def choose_country(request: Request, country: str):
    country = country.lower()
    
    # Ne pas réinitialiser le timer s'il est déjà démarré
    if globals.TIMER_STARTED_AT is None:
        globals.TIMER_STARTED_AT = time.time()

    if country == "russie":
        return RedirectResponse(url="/login")
    else:
        PENALTY = 5*60
        
        # Appliquer la pénalité instantanément
        if globals.TIMER_STARTED_AT is not None:
            globals.TIMER_STARTED_AT -= PENALTY
        else:
            # Si le timer n'était pas démarré, le démarrer avec la pénalité
            globals.TIMER_STARTED_AT = time.time() - PENALTY
            
        remaining = max(globals.TOTAL_DURATION - int(time.time() - globals.TIMER_STARTED_AT), 0)
        
        # Notifier tous les clients du changement de timer INSTANTANÉMENT
        from backend.routes.backend_routes import notify_all_websockets
        await notify_all_websockets({
            "type": "timer_update",
            "remaining": remaining,
            "penalty": PENALTY,
            "timestamp": time.time()
        })
        
        return templates.TemplateResponse(
            "select_country.html",
            {
                "request": request,
                "error": f"❌ Mauvais pays ! Temps réduit de 5 min. Temps restant: {remaining//60}:{remaining%60:02d}"
            }
        )

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    # Initialiser le timer global si ce n'est pas déjà fait
    if globals.TIMER_STARTED_AT is None:
        globals.TIMER_STARTED_AT = time.time()
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/joueur1", response_class=HTMLResponse)
def joueur1_page(request: Request):
    # Initialiser le timer global si ce n'est pas déjà fait
    if globals.TIMER_STARTED_AT is None:
        globals.TIMER_STARTED_AT = time.time()
    return templates.TemplateResponse("joueur1.html", {"request": request})

@router.get("/joueur2", response_class=HTMLResponse)
def joueur2_page(request: Request):
    # Initialiser le timer global si ce n'est pas déjà fait
    if globals.TIMER_STARTED_AT is None:
        globals.TIMER_STARTED_AT = time.time()
    return templates.TemplateResponse("joueur2.html", {"request": request})
