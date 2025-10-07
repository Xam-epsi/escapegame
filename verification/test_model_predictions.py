import os
import pandas as pd
from backend.models.ia_model import train_or_load_model, predict_topk

# Définir les chemins
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "pipelines_ru.csv")

print("🔍 Chargement du modèle et du CSV...")

# Charger le modèle
model = train_or_load_model(DATA_PATH)

# Charger le CSV
df = pd.read_csv(DATA_PATH, sep=";")

# Nettoyer le CSV comme dans ia_model.py
df = df[df["name"].notna() & (df["name"] != "REMOVED")]

# Itérer sur chaque ligne pour tester les prédictions
print(f"✅ {len(df)} lignes trouvées — test en cours...\n")

correct = 0

for i, row in df.iterrows():
    lat = float(row["lat"])
    lon = float(row["lon"])
    capacity = float(row["capacity"])
    year = int(row["year"])
    operator = row["operator"]

    preds = predict_topk(model, lat, lon, capacity, year, operator, k=3)

    print(f"Test {i+1}: {row['name']}")
    for p in preds:
        print(f"  → {p['name']} (confiance: {p['confidence']})")

    # Vérifier si le pipeline correct est dans les top-3
    if any(p["name"] == row["name"] for p in preds):
        correct += 1
        print("  ✅ Trouvé dans le top 3\n")
    else:
        print("  ❌ Pas trouvé\n")

print("------")
print(f"Résultat final : {correct}/{len(df)} pipelines correctement détectés ({(correct/len(df))*100:.1f}%)")
print("------")
