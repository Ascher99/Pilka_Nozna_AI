from __future__ import annotations
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, f1_score, log_loss, confusion_matrix
from collections import defaultdict
import json


from ml.utils import load_matches_folder


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"  
MODELS_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

LAST_N = 5

def pts_to_char(pts: int) -> str:
    if pts == 3: return "W"
    if pts == 1: return "D"
    return "L"

def calculate_features(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    
    df = df.sort_values("date").reset_index(drop=True)
    team_stats = defaultdict(list)
    h_avg_goals, a_avg_goals = [], []
    h_avg_points, a_avg_points = [], []
    raw_histories = {}

    for idx, row in df.iterrows():
        home, away = row["home_team"], row["away_team"]
        hg, ag = row["home_goals"], row["away_goals"]

        def get_avg(team, n=LAST_N):
            history = team_stats[team]
            if not history: return 0.0, 1.3 
            recent = history[-n:]
            avg_g = sum(x[0] for x in recent) / len(recent)
            avg_p = sum(x[1] for x in recent) / len(recent)
            return avg_g, avg_p

        h_g, h_p = get_avg(home)
        a_g, a_p = get_avg(away)
        
        h_avg_goals.append(h_g); h_avg_points.append(h_p)
        a_avg_goals.append(a_g); a_avg_points.append(a_p)

        h_pts = 3 if hg > ag else (1 if hg == ag else 0)
        a_pts = 3 if ag > hg else (1 if ag == hg else 0)
        
        team_stats[home].append((hg, h_pts))
        team_stats[away].append((ag, a_pts))

    for team, history in team_stats.items():
        recent = history[-LAST_N:]
        raw_histories[team] = [pts_to_char(x[1]) for x in recent]

    df["h_form_goals"] = h_avg_goals
    df["a_form_goals"] = a_avg_goals
    df["h_form_points"] = h_avg_points
    df["a_form_points"] = a_avg_points

    results = []
    for h, a in zip(df["home_goals"], df["away_goals"]):
        if h > a: results.append("home")
        elif a > h: results.append("away")
        else: results.append("draw")
    df["target"] = results
    
    return df, raw_histories

def train_and_evaluate(league_id: str, league_dir: Path):
    print(f"\n=======================================================")
    print(f"🧪 Eksperyment ML dla Ligi: {league_id.upper()}")

    raw_df = load_matches_folder(league_dir)
    df, _ = calculate_features(raw_df)
    
    
    df = df.iloc[LAST_N * 2:] 
    
    if len(df) < 50:
        print("⚠️ Za mało danych.")
        return

    
    target_enc = LabelEncoder()
    y = target_enc.fit_transform(df["target"]) 
    
    features = ["h_form_goals", "a_form_goals", "h_form_points", "a_form_points"]
    X = df[features].values
    
   
    split_idx = int(len(df) * 0.8)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

   
    models = {
        "Baseline (LogReg)": LogisticRegression(multi_class='multinomial', max_iter=2000, random_state=42),
        "Challenger (RandomForest)": RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    }

    results = {}
    best_score = 0
    best_model_obj = None
    best_model_name = ""

    print(f"📊 Zbiór treningowy: {len(X_train)} spotkań, Testowy: {len(X_test)} spotkań")

    for name, model in models.items():
        print(f"   ⚙️ Trenowanie: {name}...")
        model.fit(X_train, y_train)
        
        
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)
        
        
        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average='macro')
        ll = log_loss(y_test, y_prob)
        
        results[name] = {
            "accuracy": round(acc, 4),
            "f1_macro": round(f1, 4),
            "log_loss": round(ll, 4)
        }
        
        print(f"      -> Accuracy: {acc:.2%}, F1: {f1:.2f}, Log Loss: {ll:.2f}")

        
        if acc > best_score:
            best_score = acc
            best_model_obj = model
            best_model_name = name

    
    final_model_path = MODELS_DIR / f"model_{league_id}.pkl"
    joblib.dump({
        "model": best_model_obj,
        "scaler": scaler,
        "target_encoder": target_enc,
        "model_type": best_model_name
    }, final_model_path)

    
    report_path = REPORTS_DIR / f"report_{league_id}.json"
    with open(report_path, "w") as f:
        json.dump(results, f, indent=4)
        
    print(f"✅ Zapisano raport eksperymentu: {report_path}")
    print(f"🏆 Najlepszy model wdrożony do API: {best_model_name}")

def main():
    league_dirs = [d for d in DATA_DIR.iterdir() if d.is_dir() and d.name != '__pycache__']
    for league_dir in league_dirs:
        train_and_evaluate(league_dir.name.lower(), league_dir)

if __name__ == "__main__":
    main()