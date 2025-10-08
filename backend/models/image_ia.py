# backend/models/image_ia.py
import cv2
import numpy as np
import os

BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
REFERENCE_IMAGE_PATH = os.path.join(BASE_DIR, "poutine_bears.png")

def verify_puzzle(uploaded_image_path: str):
    """
    Compare l'image uploadée par le joueur avec l'image de référence du puzzle.
    Retourne un dict avec :
        - is_valid : bool
        - similarity : float (0..1)
    """
    # Charger image référence et uploadée
    ref = cv2.imread(REFERENCE_IMAGE_PATH, cv2.IMREAD_GRAYSCALE)
    uploaded = cv2.imread(uploaded_image_path, cv2.IMREAD_GRAYSCALE)
    
    if ref is None or uploaded is None:
        return {"is_valid": False, "similarity": 0.0}

    # redimensionner upload pour correspondre à référence
    uploaded_resized = cv2.resize(uploaded, (ref.shape[1], ref.shape[0]))

    # comparer via corrélation ou MSE
    diff = cv2.absdiff(ref, uploaded_resized)
    score = 1 - (np.sum(diff) / (ref.shape[0]*ref.shape[1]*255))

    is_valid = score >= 0.95  # tolérance 95%
    return {"is_valid": is_valid, "similarity": round(score, 4)}
