import os
import time
import random
import string
import pandas as pd
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel
from backend.models.ia_model import predict_confidence
from backend import globals
import asyncio
import json
import threading

router = APIRouter()

# ======================================================
# GESTION DES CONNEXIONS SSE
# ======================================================
# Liste des connexions SSE actives pour la synchronisation
active_connections = []
connection_lock = threading.Lock()

def notify_all_clients(data):
    """Notifier tous les clients connectés d'un changement de timer"""
    print(f"📡 Notifying {len(active_connections)} clients: {data}")
    with connection_lock:
        for connection in active_connections[:]:  # Copie pour éviter les modifications pendant l'itération
            try:
                connection.put_nowait(data)
                print(f"✅ Notification envoyée à un client")
            except Exception as e:
                print(f"❌ Erreur envoi notification: {e}")
                # Supprimer les connexions fermées
                active_connections.remove(connection)

# ======================================================
# SCHEMAS
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
# ROUTES PUZZLE
# ======================================================
@router.get("/puzzle/image")
def get_puzzle_image():
    path = os.path.join(globals.DATA_DIR, "poutine_bears.png")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Image du puzzle manquante")
    return FileResponse(path)

@router.post("/puzzle/validate")
def puzzle_validate(payload: PuzzleValidateRequest):
    if globals.TIMER_STARTED_AT is None:
        globals.TIMER_STARTED_AT = time.time()

    correct_order = list(range(9))
    if payload.positions != correct_order:
        PENALTY = 5 * 60
        globals.TIMER_STARTED_AT -= PENALTY
        remaining = max(globals.TOTAL_DURATION - int(time.time() - globals.TIMER_STARTED_AT), 0)
        
        # Notifier tous les clients du changement de timer
        notify_all_clients({
            "type": "timer_update",
            "remaining": remaining,
            "penalty": PENALTY,
            "timestamp": time.time()
        })
        
        return JSONResponse(
            status_code=400,
            content={"message": "Puzzle incorrect !", "penalty": PENALTY, "remaining": remaining, "sync": True}
        )
    return {"message": "Puzzle validé ! Bravo 😎"}

# ======================================================
# ROUTES IA & VALIDATION
# ======================================================
@router.get("/country/{code}")
def get_country(code: str, x_auth_a: Optional[str] = Header(None)):
    code = code.upper()
    if code != "RU":
        path = os.path.join(globals.DATA_DIR, f"pipelines_{code.lower()}.csv")
        if os.path.exists(path):
            return FileResponse(path, media_type="text/csv", filename=os.path.basename(path))
        raise HTTPException(status_code=404, detail="Aucune donnée pour ce pays (leurre)")
    if x_auth_a:
        path = os.path.join(globals.DATA_DIR, "pipelines_ru.csv")
        if os.path.exists(path):
            return FileResponse(path, media_type="text/csv", filename="pipelines_ru.csv")
        raise HTTPException(status_code=500, detail="Fichier pipelines_ru.csv introuvable.")
    raise HTTPException(status_code=401, detail="Header d'authentification requis (X-Auth-A).")

@router.post("/predict")
def predict(req: PredictRequest):
    print(f"🔍 Prédiction IA demandée: lat={req.lat}, lon={req.lon}, capacity={req.capacity}, year={req.year}")
    if globals.MODEL is None:
        print("❌ Modèle IA non disponible")
        raise HTTPException(status_code=500, detail="Modèle IA non disponible.")
    try:
        score = predict_confidence(globals.MODEL, req.lat, req.lon, req.capacity, req.year)
        print(f"✅ Score calculé: {score}")
    except Exception as e:
        print(f"❌ Erreur lors du calcul: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    return {"score": score}

@router.post("/validate")
def validate(payload: ValidatePayload):
    if globals.MODEL is None:
        raise HTTPException(status_code=500, detail="Modèle IA non disponible.")
    if not payload.scores:
        raise HTTPException(status_code=400, detail="Aucun score fourni.")

    csv_path = os.path.join(globals.DATA_DIR, "pipelines_ru.csv")
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
            real_score = predict_confidence(globals.MODEL, float(r["lat"]), float(r["lon"]),
                                            float(r["capacity"]), int(r["year"]))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur IA pour {s.site_code}: {e}")
        real_pct = float(round(real_score * 100, 2))
        if abs(real_pct - entered) > 10.0:
            invalid_sites.append((s.site_code, entered, real_pct))

    if invalid_sites:
        PENALTY = 5 * 60
        now = time.time()
        globals.TIMER_STARTED_AT = now - PENALTY if globals.TIMER_STARTED_AT is None else globals.TIMER_STARTED_AT - PENALTY
        remaining = max(globals.TOTAL_DURATION - int(time.time() - globals.TIMER_STARTED_AT), 0)
        
        # Notifier tous les clients du changement de timer
        notify_all_clients({
            "type": "timer_update",
            "remaining": remaining,
            "penalty": PENALTY,
            "timestamp": time.time()
        })
        
        detail = {"message": "⚠️ Scores incohérents. Temps réduit de 5 min.", "penalty": PENALTY, "remaining": remaining, "sync": True}
        raise HTTPException(status_code=400, detail=detail)

    best = max(payload.scores, key=lambda x: float(x.score))
    detected = best.site_code
    secret = globals.MAPPING.get(detected, ''.join(random.choices(string.ascii_uppercase + string.digits, k=6)))
    globals.CURRENT_SECRETS[detected] = secret

    return {"detected_site": detected, "code_secret": secret, "score": float(best.score)}

@router.post("/final")
def final_action(payload: FinalPayload):
    site = payload.site_code
    if not site:
        raise HTTPException(status_code=400, detail="site_code requis")

    expected = globals.CURRENT_SECRETS.get(site) or globals.MAPPING.get(site)
    if expected is None:
        raise HTTPException(status_code=400, detail="Aucun code attendu pour ce site (pas validé).")

    if payload.code_a == expected:
        # Marquer le jeu comme terminé
        globals.GAME_COMPLETED = True
        
        # Notifier tous les clients de la victoire
        victory_data = {
            "type": "game_success",
            "message": "✅ Pipeline sécurisé. Pollution évitée.",
            "timestamp": time.time()
        }
        print(f"📢 Envoi notification victoire: {victory_data}")
        notify_all_clients(victory_data)
        
        return {"result": "success", "message": "✅ Pipeline sécurisé. Pollution évitée."}
    else:
        return {"result": "fail", "message": "❌ Code incorrect. Fuite détectée."}

@router.get("/timer")
def get_timer():
    if globals.GAME_COMPLETED:
        return {"remaining": 0, "game_completed": True}
    
    if globals.TIMER_STARTED_AT is None:
        globals.TIMER_STARTED_AT = time.time()
    elapsed = int(time.time() - globals.TIMER_STARTED_AT)
    remaining = max(globals.TOTAL_DURATION - elapsed, 0)
    return {"remaining": remaining, "game_completed": False}

@router.get("/timer/stream")
async def timer_stream():
    """Stream en temps réel du timer pour synchroniser les joueurs"""
    async def generate_timer_events():
        # Créer une queue pour cette connexion
        queue = asyncio.Queue()
        
        # Ajouter cette connexion à la liste
        with connection_lock:
            active_connections.append(queue)
        
        try:
            while True:
                # Vérifier si le jeu est terminé
                if globals.GAME_COMPLETED:
                    data = {
                        "remaining": 0,
                        "elapsed": 0,
                        "timestamp": time.time(),
                        "game_completed": True
                    }
                    yield f"data: {json.dumps(data)}\n\n"
                    break
                
                if globals.TIMER_STARTED_AT is None:
                    globals.TIMER_STARTED_AT = time.time()
                
                elapsed = int(time.time() - globals.TIMER_STARTED_AT)
                remaining = max(globals.TOTAL_DURATION - elapsed, 0)
                
                # Envoyer l'état du timer
                data = {
                    "remaining": remaining,
                    "elapsed": elapsed,
                    "timestamp": time.time(),
                    "game_completed": False
                }
                
                yield f"data: {json.dumps(data)}\n\n"
                
                # Attendre 1 seconde avant la prochaine mise à jour
                await asyncio.sleep(1)
                
                # Arrêter si le temps est écoulé
                if remaining <= 0:
                    break
        finally:
            # Supprimer cette connexion de la liste
            with connection_lock:
                if queue in active_connections:
                    active_connections.remove(queue)
    
    return StreamingResponse(
        generate_timer_events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )

@router.post("/timer/sync")
def force_timer_sync():
    """Force la synchronisation du timer après une pénalité"""
    if globals.TIMER_STARTED_AT is None:
        globals.TIMER_STARTED_AT = time.time()
    
    elapsed = int(time.time() - globals.TIMER_STARTED_AT)
    remaining = max(globals.TOTAL_DURATION - elapsed, 0)
    
    return {
        "remaining": remaining,
        "elapsed": elapsed,
        "timestamp": time.time(),
        "synced": True
    }
