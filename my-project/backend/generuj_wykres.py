import numpy as np
import pandas as pd
import joblib
import glob
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path
from sklearn.model_selection import TimeSeriesSplit, train_test_split
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, accuracy_score, log_loss, f1_score
from sklearn.linear_model import LogisticRegression

# Próba importu, żeby obliczenia na żywo działały
try:
    from ml.train_model import calculate_features, LAST_N
    from ml.utils import load_matches_folder
except ImportError:
    print("Ostrzeżenie: Nie udało się zaimportować modułów ML. Uruchom skrypt z właściwego folderu.")

# Ustalenie poprawnych ścieżek niezależnie od miejsca odpalenia
BASE_DIR = Path(__file__).resolve().parent
if (BASE_DIR / "data").exists():
    DATA_DIR = BASE_DIR / "data"
    MODELS_DIR = BASE_DIR / "models"
else:
    DATA_DIR = BASE_DIR / "backend" / "data"
    MODELS_DIR = BASE_DIR / "backend" / "models"

def generuj_class_imbalance():
    etykiety = ['Zwycięstwo gospodarzy (Home)', 'Zwycięstwo gości (Away)', 'Remis (Draw)']
    wartosci = [44.11, 32.22, 23.67] # Twarde dane wyliczone przez model dla Premier League
    kolory = ['#1f77b4', '#d62728', '#7f7f7f'] 

    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.bar(etykiety, wartosci, color=kolory, width=0.6, edgecolor='black')

    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval + 1, f"{yval:.2f}%", ha='center', va='bottom', fontweight='bold', fontsize=12)

    ax.set_ylim(0, 55)
    ax.set_ylabel("Częstotliwość występowania [%]", fontsize=11)
    ax.set_title("Naturalny rozkład wyników - Premier League (Class Imbalance)", fontsize=14, fontweight='bold', pad=15)
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    nazwa_pliku = "class_imbalance.png"
    plt.tight_layout()
    plt.savefig(nazwa_pliku, dpi=300)
    plt.close()
    print(f"[1/5] Sukces! Wygenerowano: {nazwa_pliku}")

def generuj_rolling_window():
    fig, ax = plt.subplots(figsize=(11, 5))
    matches = [f"Mecz {i}" for i in range(1, 10)]
    x_pos = range(len(matches))

    for x in x_pos:
        rect = patches.Rectangle((x - 0.4, 0.3), 0.8, 0.6, linewidth=1.5, edgecolor='black', facecolor='#e0e0e0')
        ax.add_patch(rect)
        ax.text(x, 0.6, matches[x], ha='center', va='center', fontsize=11, fontweight='bold')

    window1 = patches.Rectangle((-0.5, 0.2), 5.0, 0.8, linewidth=2.5, edgecolor='#1f77b4', facecolor='none', linestyle='--')
    ax.add_patch(window1)
    ax.text(2, 1.2, "Krok 1: Agregacja cech z okna N=5", ha='center', color='#1f77b4', fontsize=11, fontweight='bold')

    ax.annotate("", xy=(5, 0.8), xytext=(4.6, 0.8), arrowprops=dict(facecolor='#d62728', width=2, headwidth=10))
    ax.text(5, 1.1, "Predykcja\n(Mecz 6)", ha='center', color='#d62728', fontsize=10, fontweight='bold')
    
    window2 = patches.Rectangle((0.5, 0.1), 5.0, 1.0, linewidth=2.5, edgecolor='#2ca02c', facecolor='none', linestyle=':')
    ax.add_patch(window2)
    ax.text(3, -0.2, "Krok 2: Przesunięcie okna o 1 pozycję", ha='center', color='#2ca02c', fontsize=11, fontweight='bold')

    ax.annotate("", xy=(6, 0.4), xytext=(5.6, 0.4), arrowprops=dict(facecolor='#d62728', width=2, headwidth=10))
    ax.text(6, -0.1, "Predykcja\n(Mecz 7)", ha='center', color='#d62728', fontsize=10, fontweight='bold')

    ax.set_xlim(-1, 8.5)
    ax.set_ylim(-0.5, 1.5)
    ax.axis('off')
    plt.title("Wizualizacja inżynierii cech: Mechanizm okna przesuwnego (Rolling Window)", fontsize=14, fontweight='bold', y=1.05)

    nazwa_pliku = "rolling_window_diagram.png"
    plt.tight_layout()
    plt.savefig(nazwa_pliku, dpi=300)
    plt.close()
    print(f"[2/5] Sukces! Wygenerowano: {nazwa_pliku}")


def generuj_tabele_wynikow():
    print(f"[3/5] Generowanie w pełni dynamicznej tabeli (Testuję modele na żywo - to może potrwać kilkanaście sekund)...")
    
    model_files = glob.glob(str(MODELS_DIR / "model_*.pkl"))
    dane_do_tabeli = []

    slownik_nazw = {
        "premier": "Premier League (ENG)", "championship": "Championship (ENG)",
        "laliga": "La Liga (ESP)", "seriea": "Serie A (ITA)",
        "bundesliga": "Bundesliga (GER)", "ligue1": "Ligue 1 (FRA)",
        "eredivisie": "Eredivisie (NED)", "primeira": "Primeira Liga (POR)",
        "superlig": "Super Lig (TUR)", "ekstraklasa": "Ekstraklasa (POL)"
    }

    for mf in model_files:
        try:
            mf_path = Path(mf)
            league_id = mf_path.stem.replace("model_", "")
            
            # Ładujemy model
            zapisany_stan = joblib.load(mf_path)
            model = zapisany_stan["model"]
            scaler = zapisany_stan["scaler"]
            target_enc = zapisany_stan["target_encoder"]
            
            # Identyfikacja kto wygrał
            model_name = "Regresja Logistyczna" if isinstance(model, LogisticRegression) else "Random Forest"
            
            # Pobieramy dane ligi i wyliczamy metryki na testowym (ostatnie 20%)
            league_dir = DATA_DIR / league_id
            raw_df = load_matches_folder(league_dir)
            out = calculate_features(raw_df)
            df = out[0] if isinstance(out, tuple) else out
            
            df = df.iloc[LAST_N * 2:]
            y = target_enc.transform(df["target"])
            features = ["h_form_goals", "a_form_goals", "h_form_points", "a_form_points"]
            X = df[features].values
            X = scaler.transform(X)
            
            _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
            
            y_pred = model.predict(X_test)
            y_proba = model.predict_proba(X_test)
            
            acc = accuracy_score(y_test, y_pred)
            loss = log_loss(y_test, y_proba)
            f1 = f1_score(y_test, y_pred, average='macro')
            
            ladna_nazwa = slownik_nazw.get(league_id, league_id.upper())
            dane_do_tabeli.append({
                "liga": ladna_nazwa, "model": model_name, "acc": acc, "loss": loss, "f1": f1
            })
        except Exception as e:
            print(f"Pominąłem {mf.name} z powodu błędu: {e}")

    # Sortujemy od najlepszego Log Loss do najgorszego
    dane_do_tabeli.sort(key=lambda x: x["loss"])
    
    # Formatowanie komórek
    dane = []
    for w in dane_do_tabeli:
        dane.append([
            w["liga"], w["model"], 
            f"{w['acc']*100:.2f}%".replace(".", ","),
            f"{w['loss']:.4f}".replace(".", ","),
            f"{w['f1']*100:.2f}%".replace(".", ",")
        ])
    
    kolumny = ["Rozgrywki\n(Zbiór testowy)", "Zwycięski algorytm\n(Z dynamicznego pliku .pkl)", "Dokładność\n(Accuracy)", "Funkcja straty\n(Log Loss)", "Miara F1\n(F1-Score Macro)"]

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.axis('off')
    ax.axis('tight')

    tabela = ax.table(cellText=dane, colLabels=kolumny, cellLoc='center', loc='center')
    tabela.auto_set_font_size(False)
    tabela.set_fontsize(11)
    tabela.scale(1.2, 2.0)

    for i, key in enumerate(tabela.get_celld().keys()):
        cell = tabela.get_celld()[key]
        if key[0] == 0:
            cell.set_text_props(weight='bold', color='white')
            cell.set_facecolor('#1f4e79')
        else:
            if key[1] == 0:
                cell.set_text_props(weight='bold')
            if key[0] % 2 != 0:
                cell.set_facecolor('#f2f2f2')
            
            try:
                tekst_straty = cell.get_text().get_text().replace(',','.')
                wartosc_straty = float(tekst_straty)
                if key[1] == 3 and key[0] > 0:
                     if wartosc_straty > 1.1:
                          cell.set_text_props(color='red', weight='bold')
                     elif wartosc_straty < 1.0:
                          cell.set_text_props(color='green', weight='bold')
            except: pass

    nazwa_pliku = "prawdziwa_tabela_wynikow_10lig.png"
    plt.title("Ewaluacja modeli ML na niezależnym zbiorze testowym", fontsize=16, fontweight='bold', pad=20)
    plt.savefig(nazwa_pliku, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[3/5] Sukces! Wygenerowano dynamicznie: {nazwa_pliku}")

def generuj_time_series_split():
    X = np.random.randn(100, 2)
    y = np.random.randint(0, 2, 100)
    tscv = TimeSeriesSplit(n_splits=5)

    fig, ax = plt.subplots(figsize=(10, 6))
    for ii, (tr, tt) in enumerate(tscv.split(X, y)):
        ax.scatter(tr, [ii + .5] * len(tr), c='blue', marker='_', lw=10, label='Zbiór treningowy' if ii==0 else "")
        ax.scatter(tt, [ii + .5] * len(tt), c='orange', marker='_', lw=10, label='Zbiór testowy' if ii==0 else "")

    ax.set(yticks=np.arange(5) + .5, yticklabels=[f"Iteracja walidacji {i+1}" for i in range(5)],
           xlabel="Oś czasu (kolejne, historyczne rekordy spotkań piłkarskich)", title="Wizualizacja procedury podziału danych Time Series Split")
    ax.legend(loc="upper left")
    ax.grid(axis='x', linestyle='--', alpha=0.7)

    nazwa_pliku = "time_series_split_wykres.png"
    plt.tight_layout()
    plt.savefig(nazwa_pliku, dpi=300)
    plt.close()
    print(f"[4/5] Sukces! Wygenerowano: {nazwa_pliku}")

def generuj_macierz_bledow_dynamicznie():
    model_path = MODELS_DIR / "model_premier.pkl"
    league_dir = DATA_DIR / "premier"
    
    if not model_path.exists():
        print(f"[5/5] Ostrzeżenie: Nie znaleziono modelu w {model_path}. Pominę generowanie macierzy dynamicznej.")
        return

    try:
        zapisany_stan = joblib.load(model_path)
        model = zapisany_stan["model"]
        scaler = zapisany_stan["scaler"]
        target_enc = zapisany_stan["target_encoder"]
        
        raw_df = load_matches_folder(league_dir)
        out = calculate_features(raw_df)
        df = out[0] if isinstance(out, tuple) else out
        df = df.iloc[LAST_N * 2:] 
        
        y = target_enc.transform(df["target"])
        features = ["h_form_goals", "a_form_goals", "h_form_points", "a_form_points"]
        X = df[features].values
        X = scaler.transform(X)
        
        _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
        
        y_pred = model.predict(X_test)
        cm = confusion_matrix(y_test, y_pred)
        
        fig, ax = plt.subplots(figsize=(7, 5))
        disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=target_enc.classes_)
        disp.plot(cmap='Blues', ax=ax, values_format='d')
        
        plt.title("Macierz błędów - Premier League", pad=15, fontweight='bold')
        plt.xlabel("Przewidywana klasa (Predicted label)")
        plt.ylabel("Rzeczywista klasa (True label)")
        plt.tight_layout()
        
        nazwa_pliku = "macierz_bledow_premier_wykresy.png"
        plt.savefig(nazwa_pliku, dpi=300)
        plt.close()
        print(f"[5/5] Sukces! Wygenerowano dynamicznie: {nazwa_pliku}")
    except Exception as e:
         print(f"[5/5] Ostrzeżenie: Błąd generowania macierzy dynamicznej: {e}. Użyj tej wygenerowanej przy trenowaniu!")

if __name__ == "__main__":
    generuj_class_imbalance()
    generuj_rolling_window()
    generuj_tabele_wynikow()
    generuj_time_series_split()
    generuj_macierz_bledow_dynamicznie()