import os
import pandas as pd

# Remonter correctement jusqu'à la racine du projet
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))

def load_csv_for_country(code: str):
    filename = {
        "RU": "pipelines_ru.csv",
        "IN": "pipelines_in.csv",
        "AU": "pipelines_au.csv",
        "US": "pipelines_us.csv"
    }.get(code.upper())
    if filename is None:
        raise FileNotFoundError("Country code non supporté.")
    path = os.path.join(BASE_DIR, filename)
    if not os.path.exists(path):
        return pd.DataFrame()
    df = pd.read_csv(path, sep=";")
    return df

def load_mapping_codes():
    path = os.path.join(BASE_DIR, "mapping_codes.csv")
    if not os.path.exists(path):
        print(f"⚠️ mapping_codes.csv non trouvé à {path}")
        return {}
    df = pd.read_csv(path, sep=";")
    return dict(zip(df["site_code"].astype(str), df["shutdown_code"].astype(str)))
