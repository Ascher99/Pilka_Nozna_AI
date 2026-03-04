from pathlib import Path
import os
import joblib
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import glob

from ml.utils import load_matches_folder 

BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models" 
DATA_DIR = BASE_DIR / "data"
LAST_N = 5

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",") if os.getenv("ALLOWED_ORIGINS") else ["*"]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    allow_credentials=True,
)

class PredictIn(BaseModel):
    league_id: str 
    home_team: str
    away_team: str

models = {} 
last_stats = {} 
raw_histories = {}
league_tables = {} 

def pts_to_char(pts: int) -> str:
    if pts == 3: return "W"
    if pts == 1: return "D"
    return "L"

def load_latest_stats_for_league(league_id: str, league_dir: Path) -> tuple[dict, dict, dict]:
    try:
        df = load_matches_folder(league_dir)
        df = df.dropna(subset=["date"]) 
        df = df.sort_values("date")
        
        max_date = df["date"].max()
        if max_date.month >= 7: 
            season_start = pd.Timestamp(year=max_date.year, month=7, day=1)
        else:
            season_start = pd.Timestamp(year=max_date.year - 1, month=7, day=1)

        stats_history = {} 
        table = {} 
        
        for _, row in df.iterrows():
            h, a = row["home_team"], row["away_team"]
            hg, ag = int(row["home_goals"]), int(row["away_goals"])
            match_date = row["date"]
            
            h_pts = 3 if hg > ag else (1 if hg == ag else 0)
            a_pts = 3 if ag > hg else (1 if ag == hg else 0)
            
            if h not in stats_history: stats_history[h] = []
            if a not in stats_history: stats_history[a] = []
            
            score_str = f"{h} {hg} - {ag} {a}"
            stats_history[h].append({"goals": hg, "pts": h_pts, "result": pts_to_char(h_pts), "score": score_str})
            stats_history[a].append({"goals": ag, "pts": a_pts, "result": pts_to_char(a_pts), "score": score_str})
            
            if match_date >= season_start:
                if h not in table: table[h] = {"points": 0, "gd": 0, "gf": 0, "mp": 0}
                if a not in table: table[a] = {"points": 0, "gd": 0, "gf": 0, "mp": 0}
                
                table[h]["points"] += h_pts
                table[h]["gd"] += (hg - ag)
                table[h]["gf"] += hg
                table[h]["mp"] += 1
                
                table[a]["points"] += a_pts
                table[a]["gd"] += (ag - hg)
                table[a]["gf"] += ag
                table[a]["mp"] += 1
            
        final_form = {}
        histories = {}  

        for team, history in stats_history.items():
            recent = history[-LAST_N:]
            avg_g = sum(x["goals"] for x in recent) / len(recent) if recent else 0
            avg_p = sum(x["pts"] for x in recent) / len(recent) if recent else 0
            final_form[team] = [avg_g, avg_p]
            histories[team] = [{"result": x["result"], "score": x["score"]} for x in recent]
            
        sorted_teams = sorted(table.keys(), key=lambda t: (table[t]["points"], table[t]["gd"], table[t]["gf"]), reverse=True)
        ranked_table = {}
        for rank, t in enumerate(sorted_teams, 1):
            ranked_table[t] = {
                "rank": rank,
                "points": table[t]["points"],
                "gd": table[t]["gd"],
                "mp": table[t]["mp"]
            }
            
        return final_form, histories, ranked_table
    except Exception as e:
        print(f"[WARNING] Blad liczenia statystyk dla {league_id}: {e}")
        return {}, {}, {}

def load_all_models():
    model_files = glob.glob(str(MODELS_DIR / "model_*.pkl"))
    if not model_files:
        print("[WARNING] Brak wytrenowanych modeli w folderze 'models'.")
        return

    for f_path in model_files:
        p = Path(f_path)
        league_id = p.stem.replace("model_", "")
        
        try:
            models[league_id] = joblib.load(p)
            league_dir = DATA_DIR / league_id
            
            if league_dir.exists():
                last_stats[league_id], raw_histories[league_id], league_tables[league_id] = load_latest_stats_for_league(league_id, league_dir)
                print(f"[OK] Zaladowano model i tabele dla ligi: {league_id.upper()}")
        except Exception as e:
            print(f"[WARNING] Blad dla ligi {league_id}.")

load_all_models()

@app.get("/health")
def health():
    return {"status": "ok", "models_loaded": len(models)}

@app.post("/api/predict")
def predict(inp: PredictIn):
    league_id = inp.league_id.lower()
    
    if league_id not in models or inp.home_team not in last_stats.get(league_id, {}) or inp.away_team not in last_stats.get(league_id, {}):
        return {
            "label": "draw", 
            "probs": {"home": 0.33, "draw": 0.34, "away": 0.33},
            "home_form": [], "away_form": [],
            "home_stats": {"avg_goals": 0.0, "avg_points": 0.0},
            "away_stats": {"avg_goals": 0.0, "avg_points": 0.0},
            "home_table": {"rank": 0, "points": 0, "gd": 0, "mp": 0},
            "away_table": {"rank": 0, "points": 0, "gd": 0, "mp": 0}
        }
        
    model_artifacts = models[league_id]
    current_stats = last_stats[league_id]
    current_histories = raw_histories[league_id]
    current_table = league_tables[league_id]

    h_form = current_stats[inp.home_team]
    a_form = current_stats[inp.away_team]

    features = np.array([[ h_form[0], a_form[0], h_form[1], a_form[1] ]])
    features_scaled = model_artifacts["scaler"].transform(features)
    probs_raw = model_artifacts["model"].predict_proba(features_scaled)[0]
    
    classes = model_artifacts["model"].classes_
    class_labels = model_artifacts["target_encoder"].inverse_transform(classes)
    
    probs = {l: float(p) for l, p in zip(class_labels, probs_raw)}
    best_label = max(probs.items(), key=lambda item: item[1])[0] 

    return {
        "label": best_label, 
        "probs": probs,
        "home_form": current_histories.get(inp.home_team, []),
        "away_form": current_histories.get(inp.away_team, []),
        "home_stats": {"avg_goals": round(float(h_form[0]), 2), "avg_points": round(float(h_form[1]), 2)},
        "away_stats": {"avg_goals": round(float(a_form[0]), 2), "avg_points": round(float(a_form[1]), 2)},
        "home_table": current_table.get(inp.home_team, {"rank": 0, "points": 0, "gd": 0, "mp": 0}),
        "away_table": current_table.get(inp.away_team, {"rank": 0, "points": 0, "gd": 0, "mp": 0})
    }