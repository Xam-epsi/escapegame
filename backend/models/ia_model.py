# backend/models/ia_model.py
import os
import joblib
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import Pipeline

# 🔧 Chemins
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../..", "data"))
MODEL_PATH = os.path.join(BASE_DIR, "knn_regressor_model.joblib")
CSV_PATH = os.path.join(BASE_DIR, "pipelines_ru.csv")

def _load_training_df(csv_path=CSV_PATH):
    """Charge le CSV et génère un score synthétique"""
    df = pd.read_csv(csv_path, sep=";")
    # garder seulement les lignes avec lat, lon, capacity, year
    df = df.dropna(subset=["lat","lon","capacity","year"]).copy()
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
    df["capacity"] = pd.to_numeric(df["capacity"], errors="coerce")
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    
    # Générer un score synthétique pour l'entraînement
    df['confidence_score'] = (
        0.4 * ((2025 - df['year']) / (2025 - df['year'].min())) +
        0.6 * (df['capacity'] / df['capacity'].max())
    ).clip(0,1)
    
    return df

def train_and_save_model(csv_path=CSV_PATH, model_path=MODEL_PATH, n_neighbors=3):
    """Entraîne le KNN Regressor et le sauvegarde"""
    df = _load_training_df(csv_path)
    X = df[["lat","lon","capacity","year"]]
    y = df["confidence_score"]

    numeric_transformer = StandardScaler()
    pipeline = Pipeline([
        ("scaler", numeric_transformer),
        ("knn", KNeighborsRegressor(n_neighbors=n_neighbors, weights='distance'))
    ])
    pipeline.fit(X, y)
    joblib.dump(pipeline, model_path)
    return pipeline

def load_model(model_path=MODEL_PATH):
    if os.path.exists(model_path):
        return joblib.load(model_path)
    return None

def train_or_load_model(csv_path=CSV_PATH, model_path=MODEL_PATH):
    model = load_model(model_path)
    if model is None:
        model = train_and_save_model(csv_path, model_path)
    return model

def predict_confidence(model, lat, lon, capacity, year):
    """Retourne un score de confiance pour un pipeline"""
    X_pred = pd.DataFrame([{
        "lat": float(lat),
        "lon": float(lon),
        "capacity": float(capacity),
        "year": int(year)
    }])
    score = model.predict(X_pred)[0]
    return float(round(score,2))
