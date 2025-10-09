import os
import time
import random
import string
import pandas as pd
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Header, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel
from backend.models.ia_model import predict_confidence
from backend import globals
import asyncio
import json
import threading

router = APIRouter()

# ======================================================
# GESTION DES CONNEXIONS WEBSOCKET
# ======================================================
# Liste des connexions WebSocket actives pour la synchronisation
active_websockets = []
websocket_lock = threading.Lock()

async def notify_all_websockets(data):
    """Notifier tous les clients WebSocket connectés d'un changement de timer"""
    print(f"📡 Notifying {len(active_websockets)} WebSocket clients: {data}")
    with websocket_lock:
        for websocket in active_websockets[:]:  # Copie pour éviter les modifications pendant l'itération
            try:
                await websocket.send_text(json.dumps(data))
                print(f"✅ Notification WebSocket envoyée à un client")
            except Exception as e:
                print(f"Erreur envoi WebSocket: {e}")
                # Supprimer les connexions fermées
                active_websockets.remove(websocket)

# ======================================================
# ROUTE WEBSOCKET POUR LE TIMER
# ======================================================
@router.websocket("/timer/ws")
async def timer_websocket(websocket: WebSocket):
    try:
        await websocket.accept()
        print(f"Nouvelle connexion WebSocket timer acceptee")
        
        # Ajouter cette connexion à la liste
        with websocket_lock:
            active_websockets.append(websocket)
        
        print(f"Nouvelle connexion WebSocket timer. Total: {len(active_websockets)}")
        
        while True:
            # Vérifier si le jeu est terminé
            if globals.GAME_COMPLETED:
                data = {
                    "type": "timer_update",
                    "remaining": 0,
                    "elapsed": 0,
                    "timestamp": time.time(),
                    "game_completed": True
                }
                await websocket.send_text(json.dumps(data))
                break
            
            if globals.TIMER_STARTED_AT is None:
                globals.TIMER_STARTED_AT = time.time()
            
            elapsed = int(time.time() - globals.TIMER_STARTED_AT)
            remaining = max(globals.TOTAL_DURATION - elapsed, 0)
            
            # Envoyer l'état du timer
            data = {
                "type": "timer_update",
                "remaining": remaining,
                "elapsed": elapsed,
                "timestamp": time.time(),
                "game_completed": False
            }
            
            await websocket.send_text(json.dumps(data))
            
            # Attendre 1 seconde avant la prochaine mise à jour
            await asyncio.sleep(1)
            
            # Arrêter si le temps est écoulé
            if remaining <= 0:
                break
                
    except WebSocketDisconnect:
        print("WebSocket timer deconnecte")
    except Exception as e:
        print(f"Erreur WebSocket timer: {e}")
    finally:
        # Supprimer cette connexion de la liste
        with websocket_lock:
            if websocket in active_websockets:
                active_websockets.remove(websocket)
        print(f"WebSocket timer ferme. Total restant: {len(active_websockets)}")

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
async def puzzle_validate(payload: PuzzleValidateRequest):
    if globals.TIMER_STARTED_AT is None:
        globals.TIMER_STARTED_AT = time.time()

    correct_order = list(range(9))
    if payload.positions != correct_order:
        PENALTY = 5 * 60
        globals.TIMER_STARTED_AT -= PENALTY
        remaining = max(globals.TOTAL_DURATION - int(time.time() - globals.TIMER_STARTED_AT), 0)
        
        # Notifier tous les clients du changement de timer
        await notify_all_websockets({
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
    print(f"Prediction IA demandee: lat={req.lat}, lon={req.lon}, capacity={req.capacity}, year={req.year}")
    if globals.MODEL is None:
        print("Modele IA non disponible")
        raise HTTPException(status_code=500, detail="Modèle IA non disponible.")
    try:
        score = predict_confidence(globals.MODEL, req.lat, req.lon, req.capacity, req.year)
        print(f"Score calcule: {score}")
    except Exception as e:
        print(f"Erreur lors du calcul: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    return {"score": score}

@router.post("/validate")
async def validate(payload: ValidatePayload):
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
        await notify_all_websockets({
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
async def final_action(payload: FinalPayload):
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
        await notify_all_websockets(victory_data)
        
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
