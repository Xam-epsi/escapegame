# tests/test_model_logic.py
import os
import pytest
import pandas as pd
from backend.models import ia_model

# Chemin vers le CSV test / réel
BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
CSV_PATH = os.path.join(BASE_DIR, "pipelines_ru.csv")


@pytest.fixture(scope="module")
def model():
    """Charge ou entraîne le modèle pour tous les tests"""
    return ia_model.train_or_load_model(CSV_PATH)


@pytest.fixture(scope="module")
def training_df():
    """Charge le CSV nettoyé"""
    df = pd.read_csv(CSV_PATH, sep=";")
    df = df[df["name"].notna() & (df["name"] != "REMOVED")]
    return df


def test_model_train_and_predict(model, training_df):
    """Test que chaque pipeline sort dans le top-3"""
    correct = 0
    for i, row in training_df.iterrows():
        lat = float(row["lat"])
        lon = float(row["lon"])
        capacity = float(row["capacity"])
        year = int(row["year"])
        operator = row["operator"]

        preds = ia_model.predict_topk(model, lat, lon, capacity, year, operator, k=3)

        # Vérifie que la bonne prediction est dans le top-3
        names = [p["name"] for p in preds]
        if row["name"] in names:
            correct += 1

    assert correct == len(training_df), f"{correct}/{len(training_df)} pipelines correctement détectés"


def test_confidence_values(model, training_df):
    """Vérifie que les confidences sont entre 0 et 1"""
    row = training_df.iloc[0]
    preds = ia_model.predict_topk(model, row["lat"], row["lon"], row["capacity"], row["year"], row["operator"], k=3)
    for p in preds:
        assert 0 <= p["confidence"] <= 1, f"Confiance invalide: {p['confidence']}"


def test_model_handles_unknown_operator(model):
    """Vérifie qu'un opérateur inconnu ne casse pas le modèle"""
    preds = ia_model.predict_topk(model, lat=61.0, lon=30.0, capacity=50000, year=2025, operator="Unknown", k=3)
    assert isinstance(preds, list)
    assert len(preds) <= 3


def test_model_retraining():
    """Vérifie que le modèle peut se ré-entraîner sans erreur"""
    model = ia_model.train_and_save_model(CSV_PATH, n_neighbors=1)
    assert model is not None
