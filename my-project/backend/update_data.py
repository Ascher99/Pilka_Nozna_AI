import requests
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

LEAGUES_CODES = {
    "premier": "E0",
    "championship": "E1",
    "laliga": "SP1",
    "seriea": "I1",
    "bundesliga": "D1",
    "ligue1": "F1",
    "eredivisie": "N1",
    "primeira": "P1",
    "superlig": "T1",
}

SEASONS = ["2122", "2223", "2324", "2425", "2526"]

def update_league(league_id, code):
    print(f"\n⬇️  Pobieranie historii danych dla: {league_id.upper()}...")
    
    target_dir = DATA_DIR / league_id
    target_dir.mkdir(parents=True, exist_ok=True)

    for season in SEASONS:
        url = f"https://www.football-data.co.uk/mmz4281/{season}/{code}.csv"
        
        filename = f"matches_current_season.csv" if season == "2526" else f"matches_{season}.csv"
        target_file = target_dir / filename

        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                with open(target_file, 'wb') as f:
                    f.write(response.content)
                print(f"  ✅ Sezon {season}: Zapisano pomyślnie ({filename})")
            else:
                print(f"  ❌ Sezon {season}: Brak danych (Błąd {response.status_code})")
                
        except Exception as e:
            print(f"  ❌ Błąd pobierania sezonu {season}: {e}")

def main():
    print("--- AUTOMATYCZNA AKWIZYCJA DANYCH HISTORYCZNYCH (5 LAT) ---")
    
    try:
        import requests
    except ImportError:
        print("❌ Brakuje biblioteki 'requests'. Zainstaluj ją komendą: pip install requests")
        return

    for league_id, code in LEAGUES_CODES.items():
        update_league(league_id, code)
        
    print("\n✅ Gotowe! Pobrane pełne 5 lat historii dla wszystkich lig.")
    print("Teraz uruchom trening modeli komendą:")
    print("   python -m ml.train_model")

if __name__ == "__main__":
    main()