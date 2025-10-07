🤖 ÉTAPE 5 — Modèle IA prédictif

Fichier : /backend/models/ia_model.py

import pandas as pd
from sklearn.neighbors import KNeighborsClassifier

def train_knn_model(csv_path="data/pipelines_ru.csv"):
    df = pd.read_csv(csv_path, sep=';')
    df = df[df["name"] != "REMOVED"]
    X = df[["lat", "lon", "capacity", "year"]]
    y = df["name"]
    model = KNeighborsClassifier(n_neighbors=3)
    model.fit(X, y)
    return model

def predict(model, lat, lon, capacity, year):
    X_pred = [[lat, lon, capacity, year]]
    probs = model.predict_proba(X_pred)[0]
    names = model.classes_
    results = sorted(zip(names, probs), key=lambda x: -x[1])[:3]
    return [{"name": n, "confidence": round(float(p), 2)} for n, p in results]
    