import requests
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

LEAGUES_URLS = {
    # Premier League (Anglia)
    "premier": "https://www.football-data.co.uk/mmz4281/2526/E0.csv",
    # "laliga": "https://www.football-data.co.uk/mmz4281/2425/SP1.csv",
    # "seriea": "https://www.football-data.co.uk/mmz4281/2425/I1.csv",
}

def update_league(league_id, url):
    print(f"⬇️  Pobieranie danych dla: {league_id.upper()}...")
    
    target_dir = DATA_DIR / league_id
    target_dir.mkdir(parents=True, exist_ok=True)
    
    target_file = target_dir / "matches_current_season.csv"

    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            with open(target_file, 'wb') as f:
                f.write(response.content)
            print(f"✅ Sukces! Zapisano w: {target_file}")
        else:
            print(f"❌ Błąd HTTP {response.status_code} dla {url}")
            
    except Exception as e:
        print(f"❌ Błąd pobierania {league_id}: {e}")

def main():
    print("--- AUTOMATYCZNA AKTUALIZACJA DANYCH ---")
    
    try:
        import requests
    except ImportError:
        print("❌ Brakuje biblioteki 'requests'. Zainstaluj ją komendą:")
        print("   pip install requests")
        return

    for league_id, url in LEAGUES_URLS.items():
        update_league(league_id, url)
        
    print("\n Gotowe. Teraz uruchom trening modelu:")
    print("   python -m ml.train_model")

if __name__ == "__main__":
    main()