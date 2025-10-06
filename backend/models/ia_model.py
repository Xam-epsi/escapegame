# backend/models/ia_model.py
import os
import joblib
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.exceptions import NotFittedError

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "knn_model.joblib")
CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "pipelines_ru.csv")

def _load_training_df(csv_path=CSV_PATH):
    df = pd.read_csv(csv_path, sep=";")
    # keep only rows with a name (exclude REMOVED)
    df_train = df[df["name"].notna() & (df["name"] != "REMOVED")].copy()
    # Ensure types
    df_train["lat"] = pd.to_numeric(df_train["lat"], errors="coerce")
    df_train["lon"] = pd.to_numeric(df_train["lon"], errors="coerce")
    df_train["capacity"] = pd.to_numeric(df_train["capacity"], errors="coerce")
    df_train["year"] = pd.to_numeric(df_train["year"], errors="coerce")
    df_train = df_train.dropna(subset=["lat","lon","capacity","year"])
    return df_train

def train_and_save_model(csv_path=CSV_PATH, model_path=MODEL_PATH, n_neighbors=3):
    df = _load_training_df(csv_path)
    if df.shape[0] < 3:
        raise ValueError("Pas assez de lignes valides pour entraîner le modèle.")
    X = df[["lat","lon","capacity","year","operator"]]
    y = df["name"].astype(str)

    # Preprocessing
    numeric_features = ["lat","lon","capacity","year"]
    numeric_transformer = StandardScaler()

    categorical_features = ["operator"]
    categorical_transformer = OneHotEncoder(handle_unknown="ignore", sparse=False)

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features),
        ],
        remainder="drop"
    )

    # KNN classifier with probability support
    knn = KNeighborsClassifier(n_neighbors=n_neighbors)

    pipeline = Pipeline(steps=[
        ("preproc", preprocessor),
        ("knn", knn)
    ])

    pipeline.fit(X, y)

    # Save pipeline and the label classes
    joblib.dump(pipeline, model_path)
    return pipeline

def load_model(model_path=MODEL_PATH):
    if os.path.exists(model_path):
        return joblib.load(model_path)
    return None

def train_or_load_model(csv_path=CSV_PATH, model_path=MODEL_PATH):
    model = load_model(model_path)
    if model is not None:
        # quick check
        try:
            _ = model.predict([[0,0,0,0,"dummy"]])  # will raise if mismatch
        except Exception:
            # try retraining
            model = train_and_save_model(csv_path, model_path)
    else:
        model = train_and_save_model(csv_path, model_path)
    return model

def predict_topk(model, lat, lon, capacity, year, operator, k=3):
    """Return list of dicts: [{name, confidence}, ...] sorted desc."""
    X_pred = pd.DataFrame([{
        "lat": float(lat), "lon": float(lon), "capacity": float(capacity),
        "year": int(year), "operator": operator
    }])
    try:
        probs = model.predict_proba(X_pred)[0]  # array of probabilities aligned with classes_
    except (AttributeError, NotFittedError):
        raise RuntimeError("Le modèle n'est pas chargé / entraîné.")
    classes = model.classes_
    # zip classes/probs and sort
    pairs = sorted(zip(classes, probs), key=lambda x: -x[1])[:k]
    results = [{"name": name, "confidence": float(round(conf, 2))} for name, conf in pairs]
    return results
