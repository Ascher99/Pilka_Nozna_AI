import pandas as pd
import numpy as np
import glob
from pathlib import Path

def parse_date(s):
    if pd.isna(s):
        return pd.NaT
    try:
        return pd.to_datetime(s, format="%d/%m/%Y")
    except: pass
    try:
        return pd.to_datetime(s, format="%Y-%m-%d")
    except: pass
    try:
        return pd.to_datetime(s, format="%d/%m/%y")
    except: pass
    try:
        dt = pd.to_datetime(s, utc=True)
        if hasattr(dt, 'tzinfo') and dt.tzinfo is not None:
            return dt.tz_localize(None) 
        return dt
    except:
        return pd.NaT

def load_matches_folder(folder_path: Path) -> pd.DataFrame:
    files = glob.glob(str(folder_path / "*.csv"))
    df_list = []
    
    for f in files:
        try:
            temp_df = pd.read_csv(f)
            df_list.append(temp_df)
        except Exception as e:
            print(f"Błąd ładowania pliku {f}: {e}")
            continue
            
    if not df_list:
        raise ValueError(f"Brak plików CSV w {folder_path}")
        
    df = pd.concat(df_list, ignore_index=True)
    
    rename_map = {
        "HomeTeam": "home_team", "AwayTeam": "away_team",
        "FTHG": "home_goals", "FTAG": "away_goals",
        "Date": "date",
        "Home": "home_team", "Away": "away_team",
        "HG": "home_goals", "AG": "away_goals"
    }
    df = df.rename(columns=rename_map)
    df.columns = [str(c).lower() for c in df.columns]
    
    if "date" in df.columns:
        df['date'] = df['date'].apply(parse_date)
                     
    required_cols = ["home_team", "away_team", "home_goals", "away_goals", "date"]
    available_cols = [c for c in required_cols if c in df.columns]
    
    if available_cols:
        df = df.dropna(subset=available_cols)
        
    return df

def calculate_features(df: pd.DataFrame, last_n: int = 5) -> pd.DataFrame:
    df = df.sort_values("date").reset_index(drop=True)
    
    stats_history = {}
    features_list = []
    
    for idx, row in df.iterrows():
        h, a = row["home_team"], row["away_team"]
        hg, ag = int(row["home_goals"]), int(row["away_goals"])
        
        h_pts = 3 if hg > ag else (1 if hg == ag else 0)
        a_pts = 3 if ag > hg else (1 if ag == hg else 0)
        
        if h not in stats_history: stats_history[h] = []
        if a not in stats_history: stats_history[a] = []
        
        h_recent = stats_history[h][-last_n:]
        a_recent = stats_history[a][-last_n:]
        
        h_avg_goals = sum(x["goals"] for x in h_recent) / len(h_recent) if h_recent else 0
        h_avg_pts = sum(x["pts"] for x in h_recent) / len(h_recent) if h_recent else 0
        
        a_avg_goals = sum(x["goals"] for x in a_recent) / len(a_recent) if a_recent else 0
        a_avg_pts = sum(x["pts"] for x in a_recent) / len(a_recent) if a_recent else 0
        
        if hg > ag:
            label = "home"
        elif ag > hg:
            label = "away"
        else:
            label = "draw"
            
        features_list.append({
            "home_avg_goals": h_avg_goals,
            "away_avg_goals": a_avg_goals,
            "home_avg_points": h_avg_pts,
            "away_avg_points": a_avg_pts,
            "label": label
        })
        
        stats_history[h].append({"goals": hg, "pts": h_pts})
        stats_history[a].append({"goals": ag, "pts": a_pts})
        
    features_df = pd.DataFrame(features_list)
    
    if len(features_df) > last_n * 2:
        features_df = features_df.iloc[last_n * 2:].reset_index(drop=True)
        
    return features_df