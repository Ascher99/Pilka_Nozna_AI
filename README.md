# ⚽ Piłka Nożna AI (Football AI Prediction)

Projekt **Piłka Nożna AI** to aplikacja typu Full-Stack służąca do analizy danych i przewidywania wyników meczów piłkarskich w różnych ligach. Wykorzystuje uczenie maszynowe (Machine Learning) do szacowania prawdopodobieństwa zwycięstwa, remisu lub porażki na podstawie aktualnej formy zespołów.

## ✨ Główne funkcjonalności

* **Predykcja wyników:** Automatyczne szacowanie wyników meczów (Home/Draw/Away) z podziałem procentowym szans dla każdego scenariusza.
* **Analiza formy (Last 5):** Algorytm oblicza średnią liczbę zdobywanych bramek i zdobywanych punktów z ostatnich 5 spotkań obu rywalizujących drużyn.
* **Tabele ligowe na żywo:** Automatyczne generowanie i przeliczanie tabel ligowych (punkty, różnica bramek, rozegrane mecze) na podstawie zestawów danych `.csv`.
* **Wybór najlepszego modelu:** W procesie treningowym aplikacja weryfikuje skuteczność modeli (Regresji Logistycznej i Random Forest), wybierając ten o najmniejszym błędzie wskaźnika *Log Loss*.
* **Nowoczesny interfejs GUI:** Szybki, responsywny i przejrzysty frontend pozwalający na łatwe interakcje z systemem ML.

## 🛠 Wykorzystany Stos Technologiczny (Tech Stack)

### W warstwie Frontend:
* **Framework:** Next.js 16 / React 19
* **Język:** TypeScript
* **Stylizowanie:** Tailwind CSS v4

### W warstwie Backend & Machine Learning:
* **API:** FastAPI, Uvicorn (Python)
* **Analiza Danych:** Pandas, NumPy
* **Uczenie Maszynowe:** Scikit-Learn (Logistic Regression, Random Forest, StandardScaler)
* **Zarządzanie modelami:** Joblib

## 🚀 Instalacja i Uruchomienie lokalne

### 1. Klonowanie repozytorium
```bash
git clone [https://github.com/Ascher99/Pilka_Nozna_AI.git](https://github.com/Ascher99/Pilka_Nozna_AI.git)
cd Pilka_Nozna_AI/my-project
2. Uruchomienie Backendu (API)
Przejdź do katalogu backendu, zainstaluj zależności i uruchom serwer FastAPI.

Bash
cd backend
python -m venv venv
source venv/bin/activate  # Dla środowisk Linux/Mac
venv\Scripts\activate     # Dla środowiska Windows

pip install -r requirements.txt
uvicorn main:app --reload
```
Aplikacja backendowa będzie dostępna pod adresem: http://localhost:8000.

(Opcjonalnie) Aby wytrenować modele od nowa z najnowszymi danymi ligowymi, przygotuj foldery z plikami CSV w backend/data/ i uruchom skrypt trenujący:

```bash
python ml/train_model.py
3. Uruchomienie Frontendu
```
Otwórz drugie okno terminala i z głównego katalogu frontendowego (my-project) uruchom serwer deweloperski Next.js.


```bash
npm install
npm run dev
```
Interfejs użytkownika (UI) uruchomi się pod adresem: http://localhost:3000.

🧠 Architektura Systemu ML
Wytrenowany system działa w następujący sposób:

Pobiera historię spotkań danej ligi z folderu data.

Mapuje i przetwarza wyniki, generując dla każdej drużyny uśrednione cechy (features) formy (gole i punkty zdobyte w ostatnich spotkaniach).

Funkcja ucząca testuje system CalibratedClassifierCV z lasami losowymi oraz regresję logistyczną z balansem klas.

Po ustaleniu lepszego klasyfikatora, model zapisywany jest z dołączonym formaterem danych (StandardScaler) i staje się gotowy do przyjmowania requestów od użytkownika w endpointach FastAPI.

