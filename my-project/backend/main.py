from pathlib import Path
import joblib
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import glob

# Poprawiony import
from ml.utils import load_matches_folder 

# --- KONFIGURACJA ---
BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models" # Nowy folder na modele
DATA_DIR = BASE_DIR / "data"
LAST_N = 5

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

class PredictIn(BaseModel):
    league_id: str # Dodany parametr
    home_team: str
    away_team: str

# Globalny słownik przechowujący artefakty dla każdej ligi
# models[league_id] = {'model': ..., 'scaler': ..., 'target_encoder': ...}
models = {} 
# Globalny słownik przechowujący statystyki dla każdej ligi
# stats[league_id][team_name] = [avg_goals, avg_points]
last_stats = {} 
# Globalny słownik przechowujący historię W/D/L
# histories[league_id][team_name] = ["W", "D", "L", "W", "D"]
raw_histories = {}


def pts_to_char(pts: int) -> str:
    if pts == 3: return "W"
    if pts == 1: return "D"
    return "L"

def load_latest_stats_for_league(league_id: str, league_dir: Path) -> tuple[dict, dict]:
    """Przelicza aktualną formę drużyn dla danej ligi."""
    try:
        df = load_matches_folder(league_dir)
        df = df.sort_values("date")
        
        # Słownik do przechowywania wszystkich historycznych wyników (gole, punkty)
        stats_history = {} 
        
        for _, row in df.iterrows():
            h, a = row["home_team"], row["away_team"]
            hg, ag = row["home_goals"], row["away_goals"]
            
            h_pts = 3 if hg > ag else (1 if hg == ag else 0)
            a_pts = 3 if ag > hg else (1 if ag == hg else 0)
            
            if h not in stats_history: stats_history[h] = []
            if a not in stats_history: stats_history[a] = []
            
            stats_history[h].append((hg, h_pts))
            stats_history[a].append((ag, a_pts))
            
        final_form = {} # Słownik ze średnią formą (dane dla modelu)
        histories = {}  # Słownik z historią W/D/L (dane dla frontendu)

        for team, history in stats_history.items():
            recent = history[-LAST_N:]
            
            # 1. Dane dla modelu (średnie z ostatnich 5)
            avg_g = sum(x[0] for x in recent) / len(recent) if recent else 0
            avg_p = sum(x[1] for x in recent) / len(recent) if recent else 0
            final_form[team] = [avg_g, avg_p]

            # 2. Dane dla frontendu (W/D/L)
            histories[team] = [pts_to_char(x[1]) for x in recent]
            
        return final_form, histories
    except Exception as e:
        print(f"⚠️ Błąd liczenia statystyk dla {league_id}: {e}")
        return {}, {}

def load_all_models():
    """Ładuje modele i oblicza statystyki dla wszystkich lig."""
    model_files = glob.glob(str(MODELS_DIR / "model_*.pkl"))
    if not model_files:
        print("⚠️ Brak wytrenowanych modeli w folderze 'models'. Używam trybu MOCK.")
        return

    for f_path in model_files:
        p = Path(f_path)
        # Oczekiwany format nazwy: model_ekstraklasa.pkl
        league_id = p.stem.replace("model_", "")
        
        try:
            models[league_id] = joblib.load(p)
            league_dir = DATA_DIR / league_id
            
            if league_dir.exists():
                last_stats[league_id], raw_histories[league_id] = load_latest_stats_for_league(league_id, league_dir)
                print(f"✅ Załadowano model i statystyki dla ligi: {league_id.upper()}")
            else:
                print(f"❌ Brakuje folderu danych dla ligi {league_id}. Statystyki niedostępne.")

        except Exception as e:
            print(f"❌ Błąd ładowania modelu dla ligi {league_id}: {e}")

load_all_models()


@app.get("/health")
def health():
    return {"status": "ok", "models_loaded": len(models)}


@app.post("/api/predict")
def predict(inp: PredictIn):
    league_id = inp.league_id.lower()
    
    # 1. Weryfikacja czy model dla ligi istnieje
    if league_id not in models:
        # Ten warunek łapie Premier League dopóki nie dodasz danych CSV
        print(f"⚠️ Brak modelu dla ligi {league_id}. Używam trybu MOCK.")
        return {
            "label": "draw", 
            "probs": {"home": 0.33, "draw": 0.34, "away": 0.33},
            "home_form": [], 
            "away_form": []
        }
        
    model_artifacts = models[league_id]
    current_stats = last_stats.get(league_id, {})
    current_histories = raw_histories.get(league_id, {})

    # 2. Weryfikacja czy drużyny mają historię
    h_form = current_stats.get(inp.home_team)
    a_form = current_stats.get(inp.away_team)

    if h_form is None or a_form is None:
        print(f"⚠️ Nieznana drużyna w {league_id}. Używam trybu MOCK.")
        return {
            "label": "draw", 
            "probs": {"home": 0.33, "draw": 0.34, "away": 0.33},
            "home_form": current_histories.get(inp.home_team, []),
            "away_form": current_histories.get(inp.away_team, [])
        }

    # 3. Predykcja AI
    features = np.array([[ h_form[0], a_form[0], h_form[1], a_form[1] ]])
    features_scaled = model_artifacts["scaler"].transform(features)
    probs_raw = model_artifacts["model"].predict_proba(features_scaled)[0]
    
    # Dekodowanie
    classes = model_artifacts["model"].classes_
    class_labels = model_artifacts["target_encoder"].inverse_transform(classes)
    
    probs = {}
    for label, prob in zip(class_labels, probs_raw):
        probs[label] = float(prob)
        
    label = max(probs, key=probs.get)
    
    # 4. Zwrócenie wyniku z historią
    return {
        "label": label, 
        "probs": probs,
        "home_form": current_histories.get(inp.home_team, []),
        "away_form": current_histories.get(inp.away_team, [])
    }