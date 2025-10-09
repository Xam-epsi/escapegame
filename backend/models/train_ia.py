# backend/models/train_ia.py
from ia_model import train_or_load_model, predict_confidence

def main():
    # Entraîne ou charge le modèle
    model = train_or_load_model()
    
    # Test de prédiction pour vérifier que ça fonctionne
    test_pipeline = {
        "lat": 61.2345,
        "lon": 30.1234,
        "capacity": 50000,
        "year": 1998
    }
    
    score = predict_confidence(
        model,
        lat=test_pipeline["lat"],
        lon=test_pipeline["lon"],
        capacity=test_pipeline["capacity"],
        year=test_pipeline["year"]
    )
    
    print("Score de confiance pour le pipeline test :", score)

if __name__ == "__main__":
    main()
