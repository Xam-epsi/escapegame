# data/generate_saved_scores.py
import os
import pandas as pd
from backend.models.ia_model import train_or_load_model, predict_confidence

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "pipelines_ru.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "saved_scores.csv")

# charger modèle IA
model = train_or_load_model()

# lire CSV
df = pd.read_csv(CSV_PATH, sep=';')

# calculer les scores
scores = []
for _, row in df.iterrows():
    try:
        score = predict_confidence(
            model,
            float(row["lat"]),
            float(row["lon"]),
            float(row["capacity"]),
            int(row["year"])
        )
        scores.append({
            "site_code": row["site_code"],
            "score": round(score * 100, 2)
        })
    except Exception as e:
        print(f"Erreur pour {row['site_code']}: {e}")

# enregistrer CSV
pd.DataFrame(scores).to_csv(OUTPUT_PATH, index=False, sep=';')
print(f"✅ Scores sauvegardés dans {OUTPUT_PATH}")
