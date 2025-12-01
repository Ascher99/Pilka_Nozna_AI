from __future__ import annotations
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from collections import defaultdict
import glob

from ml.utils import load_matches_folder # Poprawiony import

# --- KONFIGURACJA ---
BASE_DIR = Path(__file__).resolve().parents[1]  # -> backend/
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models" # Nowy folder na modele
MODELS_DIR.mkdir(exist_ok=True)

LAST_N = 5  # Z ilu ostatnich meczów liczymy formę

def pts_to_char(pts: int) -> str:
    if pts == 3: return "W"
    if pts == 1: return "D"
    return "L"

def calculate_features(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, list[str]]]:
    # ... (kod funkcji calculate_features pozostaje bez zmian)
    # Wklej całą funkcję z poprzedniego kroku:

    df = df.sort_values("date").reset_index(drop=True)

    team_stats = defaultdict(list)
    h_avg_goals = []
    a_avg_goals = []
    h_avg_points = []
    a_avg_points = []
    raw_histories = {} # Do zbierania historii W/D/L

    for idx, row in df.iterrows():
        home = row["home_team"]
        away = row["away_team"]
        hg = row["home_goals"]
        ag = row["away_goals"]

        def get_avg(team, n=LAST_N):
            history = team_stats[team]
            if not history:
                return 0.0, 1.3
            recent = history[-n:] 
            avg_g = sum(x[0] for x in recent) / len(recent)
            avg_p = sum(x[1] for x in recent) / len(recent)
            return avg_g, avg_p

        h_g, h_p = get_avg(home)
        a_g, a_p = get_avg(away)

        h_avg_goals.append(h_g)
        h_avg_points.append(h_p)
        a_avg_goals.append(a_p)
        a_avg_points.append(a_p)

        h_pts = 3 if hg > ag else (1 if hg == ag else 0)
        a_pts = 3 if ag > hg else (1 if ag == hg else 0)

        # Zapisujemy historię (gole, punkty)
        team_stats[home].append((hg, h_pts))
        team_stats[away].append((ag, a_pts))

    # Obliczamy finalne historyczne W/D/L dla każdego zespołu
    for team, history in team_stats.items():
        recent = history[-LAST_N:]
        # Konwertujemy punkty na literki
        raw_histories[team] = [pts_to_char(x[1]) for x in recent]
    
    # Przypisujemy obliczone kolumny do DataFrame
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

def train_for_league(league_id: str, league_dir: Path):
    """Trenuje model dla jednej ligi i zapisuje artefakty."""
    print(f"\n=======================================================")
    print(f"🤖 Rozpoczynam trening dla Ligi: {league_id.upper()}")
    
    # Ładowanie i inżynieria cech
    raw_df = load_matches_folder(league_dir)
    df, _ = calculate_features(raw_df)
    
    # Usuwamy mecze z niepełną historią (cold start)
    df = df.iloc[LAST_N * 2:] 

    if len(df) < 50:
        print(f"⚠️ Za mało danych ({len(df)} meczów). Pomiń trening dla {league_id.upper()}.")
        return

    print(f"📊 Trenuję na {len(df)} meczach.")
    
    # 1. Enkoder etykiet
    target_enc = LabelEncoder()
    y = target_enc.fit_transform(df["target"])

    # 2. Wybór cech i Skalowanie
    features = ["h_form_goals", "a_form_goals", "h_form_points", "a_form_points"]
    X = df[features].values

    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    # 3. Podział na zbiór treningowy i testowy
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    # 4. Trening modelu
    model = LogisticRegression(multi_class='multinomial', solver='lbfgs', max_iter=2000)
    model.fit(X_train, y_train)

    # 5. Ewaluacja
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    
    print(f"🏆 Skuteczność modelu (Accuracy): {acc:.2%}")
    print(classification_report(y_test, y_pred, target_names=target_enc.classes_))
    
    # 6. Zapis artefaktów
    to_save = {
        "model": model,
        "scaler": scaler,
        "target_encoder": target_enc,
    }
    model_path = MODELS_DIR / f"model_{league_id}.pkl"
    joblib.dump(to_save, model_path)
    print(f"Zapisano model ligi {league_id.upper()} do: {model_path}")


def main():
    # 1. Znajdujemy wszystkie foldery lig w katalogu data/
    league_dirs = [d for d in DATA_DIR.iterdir() if d.is_dir() and d.name != '__pycache__']
    
    if not league_dirs:
        print("Błąd: Nie znaleziono żadnych folderów z danymi lig w 'backend/data/'.")
        return

    for league_dir in league_dirs:
        league_id = league_dir.name.lower()
        train_for_league(league_id, league_dir)

if __name__ == "__main__":
    main()