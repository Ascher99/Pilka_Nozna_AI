from __future__ import annotations
import pandas as pd
from pathlib import Path
from typing import List

COLMAP = {
    "date": ["date", "match_date", "Date"],
    "home_team": ["home_team", "HomeTeam", "home", "Home"],
    "away_team": ["away_team", "AwayTeam", "away", "Away"],
    "home_goals": ["home_goals", "FTHG", "HG", "home_score", "HomeGoals"],
    "away_goals": ["away_goals", "FTAG", "AG", "away_score", "AwayGoals"],
}

# Słownik mapujący nazwy z CSV (klucz) na nazwy z Frontendu (wartość)
TEAM_MAPPING = {
    "Man City": "Manchester City",
    "Man United": "Manchester United",
    "Nott'm Forest": "Nottingham Forest",
    "Newcastle": "Newcastle United",
    "Leicester": "Leicester City",
    "Ipswich": "Ipswich Town",
    "Wolverhampton": "Wolves", # Na wypadek gdyby w innym pliku było inaczej
    "West Ham United": "West Ham", # Na wypadek innej wersji
}

def pick_col(df: pd.DataFrame, wanted: List[str]) -> str:
    cols = {c.lower(): c for c in df.columns}
    for w in wanted:
        lw = w.lower()
        if lw in cols:
            return cols[lw]
    for w in wanted:
        for c in df.columns:
            if w.lower() in c.lower():
                return c
    raise KeyError(f"Nie znaleziono kolumny pasującej do: {wanted}")

def load_matches_folder(folder: Path) -> pd.DataFrame:
    files = sorted(list(folder.glob("*.csv")))
    if not files:
        print(f"⚠️ Ostrzeżenie: Brak plików CSV w {folder}")
        return pd.DataFrame()

    frames = []
    for f in files:
        try:
            try:
                df = pd.read_csv(f, encoding="utf-8")
            except UnicodeDecodeError:
                df = pd.read_csv(f, encoding="latin1")

            date_col = pick_col(df, COLMAP["date"]) if any(k in " ".join(df.columns) for k in COLMAP["date"]) else None
            home_col = pick_col(df, COLMAP["home_team"])
            away_col = pick_col(df, COLMAP["away_team"])
            hg_col = pick_col(df, COLMAP["home_goals"])
            ag_col = pick_col(df, COLMAP["away_goals"])

            # Obsługa daty z dayfirst=True (dla formatu DD/MM/YYYY w Premier League)
            if date_col:
                date_series = pd.to_datetime(df[date_col], dayfirst=True, errors='coerce')
            else:
                date_series = pd.NaT

            out = pd.DataFrame({
                "date": date_series,
                "home_team": df[home_col].astype(str).str.strip(),
                "away_team": df[away_col].astype(str).str.strip(),
                "home_goals": pd.to_numeric(df[hg_col], errors="coerce").fillna(0).astype(int),
                "away_goals": pd.to_numeric(df[ag_col], errors="coerce").fillna(0).astype(int),
            })
            
            # --- NORMALIZACJA NAZW (Mapowanie) ---
            out["home_team"] = out["home_team"].replace(TEAM_MAPPING)
            out["away_team"] = out["away_team"].replace(TEAM_MAPPING)
            # -------------------------------------

            out = out.dropna(subset=["date"])
            frames.append(out)
            
        except Exception as e:
            print(f"⚠️ Pomijam plik {f.name} z powodu błędu: {e}")

    if not frames:
        return pd.DataFrame()

    all_df = pd.concat(frames, ignore_index=True)
    # Filtrowanie błędnych wierszy
    all_df = all_df[all_df["home_team"].ne(all_df["away_team"])]
    all_df = all_df.dropna(subset=["home_team", "away_team"])
    
    return all_df.reset_index(drop=True)