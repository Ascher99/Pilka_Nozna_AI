# Inteligentna platforma do analizy i predykcji wyników meczów piłkarskich

**Praca dyplomowa** | Autor: Vu Minh Grzegorczyk

Aplikacja wykorzystująca uczenie maszynowe do przewidywania wyników meczów piłkarskich. System analizuje formę drużyn z ostatnich 5 meczów i generuje procentowe prawdopodobieństwa wyniku (wygrana gospodarza, remis, wygrana gościa).

---

# Intelligent Platform for Football Match Analysis and Prediction

**Thesis Project** | Author: Vu Minh Grzegorczyk

An application using machine learning to predict football match results. The system analyzes team form from the last 5 matches and generates probability percentages for outcomes (home win, draw, away win).

---

## Spis treści | Table of Contents

- [Przegląd projektu](#przegląd-projektu) | [Project Overview](#project-overview)
- [Architektura](#architektura) | [Architecture](#architecture)
- [Funkcjonalności](#funkcjonalności) | [Features](#features)
- [Struktura projektu](#struktura-projektu) | [Project Structure](#project-structure)
- [Wymagania systemowe](#wymagania-systemowe) | [System Requirements](#system-requirements)
- [Instalacja i uruchomienie](#instalacja-i-uruchomienie) | [Installation & Setup](#installation--setup)
- [Dostępne ligi](#dostępne-ligi) | [Available Leagues](#available-leagues)
- [Dokumentacja API](#dokumentacja-api) | [API Documentation](#api-documentation)
- [Model ML](#model-ml) | [ML Model](#ml-model)
- [Środowisko rozwojowe](#środowisko-rozwojowe) | [Development Environment](#development-environment)
- [Plany rozwoju](#plany-rozwoju) | [Future Improvements](#future-improvements)
- [Licencja](#licencja)

---

## Przegląd projektu

### Cel
Platforma do automatycznej analizy danych historycznych i przewidywania wyników meczów piłkarskich z wykorzystaniem technik uczenia maszynowego.

### Zakres
- Obsługa dwóch lig: Premier League (Anglia) i Ekstraklasa (Polska)
- Analiza formy drużyn z ostatnich 5 meczów
- Generowanie prawdopodobieństw wyników (home/draw/away)
- Wizualizacja wyników w formie interaktywnego interfejsu

### Metodologia
Projekt wykorzystuje uczenie nadzorowane z algorytmem regresji logistycznej do klasyfikacji wyników meczów na podstawie cech wyznaczonych z formy drużyn.

### Kontekst akademicki
Praca dyplomowa na wydziale informatyki, prezentująca praktyczne zastosowanie technik uczenia maszynowego w domenie sportowej.

---

## Project Overview

### Goal
A platform for automatic historical data analysis and football match result prediction using machine learning techniques.

### Scope
- Support for two leagues: Premier League (England) and Ekstraklasa (Poland)
- Team form analysis from the last 5 matches
- Generation of outcome probabilities (home/draw/away)
- Interactive visualization interface for results

### Methodology
The project uses supervised learning with logistic regression algorithm to classify match results based on features derived from team form.

### Academic Context
Thesis project at the Faculty of Computer Science, demonstrating practical application of machine learning techniques in the sports domain.

---

## Architektura

### Diagram
```
┌─────────────────┐         ┌─────────────────┐
│   Next.js 16    │◄────────┤  FastAPI (8000) │
│  React 19       │  HTTP   │  Python 3.14    │
│  TypeScript     │         │  scikit-learn   │
└─────────────────┘         └────────┬────────┘
                                    │
                            ┌───────┴───────┐
                            │  ML Models    │
                            │  - Premier    │
                            │  - Ekstraklasa│
                            └───────────────┘
```

### Stack technologiczny
- **Frontend**: Next.js 16, React 19, TypeScript, Tailwind CSS 4
- **Backend**: FastAPI, Python 3.14, uvicorn
- **ML**: scikit-learn, pandas, numpy, joblib
- **Dane**: football-data.co.uk (2021-2024)

---

## Architecture

### Diagram
```
┌─────────────────┐         ┌─────────────────┐
│   Next.js 16    │◄────────┤  FastAPI (8000) │
│  React 19       │  HTTP   │  Python 3.14    │
│  TypeScript     │         │  scikit-learn   │
└─────────────────┘         └────────┬────────┘
                                    │
                            ┌───────┴───────┐
                            │  ML Models    │
                            │  - Premier    │
                            │  - Ekstraklasa│
                            └───────────────┘
```

### Tech Stack
- **Frontend**: Next.js 16, React 19, TypeScript, Tailwind CSS 4
- **Backend**: FastAPI, Python 3.14, uvicorn
- **ML**: scikit-learn, pandas, numpy, joblib
- **Data**: football-data.co.uk (2021-2024)

---

## Funkcjonalności

- ⚽ **Przewidywanie wyników**: Automatyczna analiza i predykcja meczów piłkarskich
- 📊 **Wizualizacja formy**: Graficzne przedstawienie ostatnich 5 meczów (W/D/L)
- 🏆 **Wiele lig**: Obsługa Premier League (20 drużyn) i Ekstraklasa (16 drużyn)
- 🔄 **Tryb mock**: Możliwość testowania aplikacji bez backendu
- 📈 **Prawdopodobieństwa**: Szczegółowe procenty wyniku (np. Home: 52%, Draw: 24%, Away: 24%)
- 🎨 **Responsywny design**: Adaptacja do różnych rozmiarów ekranu
- ⚡ **Real-time predictions**: Szybkie generowanie wyników w czasie rzeczywistym

---

## Features

- ⚽ **Match Prediction**: Automatic analysis and prediction of football matches
- 📊 **Form Visualization**: Graphical representation of the last 5 matches (W/D/L)
- 🏆 **Multiple Leagues**: Support for Premier League (20 teams) and Ekstraklasa (16 teams)
- 🔄 **Mock Mode**: Ability to test the application without backend
- 📈 **Probability Percentages**: Detailed outcome percentages (e.g., Home: 52%, Draw: 24%, Away: 24%)
- 🎨 **Responsive Design**: Adaptation to different screen sizes
- ⚡ **Real-time Predictions**: Fast generation of results in real-time

---

## Struktura projektu

```bash
my-project/
├── app/                          # Next.js App Router
│   ├── api/predict/route.ts     # API route proxy (optional)
│   ├── globals.css              # Global styles
│   ├── layout.tsx               # Root layout
│   └── page.tsx                 # Homepage
├── backend/                      # Python FastAPI
│   ├── data/                    # Historical data
│   │   ├── premier/             # Premier League (2021-2024)
│   │   └── Ekstraklasa/         # Ekstraklasa (2021-2024)
│   ├── ml/                      # ML modules
│   │   ├── train_model.py       # Model training
│   │   └── utils.py             # Data loading utilities
│   ├── models/                  # Trained models
│   │   ├── model_premier.pkl    # Premier League model
│   │   └── model_ekstraklasa.pkl # Ekstraklasa model
│   ├── main.py                  # FastAPI application
│   ├── update_data.py           # Data fetching
│   └── venv/                    # Python virtual environment
├── components/                   # React components
│   ├── Predictor.tsx            # Main prediction component
│   ├── Card.tsx                 # Result card
│   ├── Button.tsx               # Button component
│   └── Select.tsx               # Selector component
├── lib/                         # TypeScript utilities
│   ├── api.ts                   # API functions
│   └── config.ts                # Configuration
├── types/                       # TypeScript definitions
│   └── predict.ts               # API types
└── data/                        # Static data
    └── teams.ts                 # League and team list
```

---

## Project Structure

```bash
my-project/
├── app/                          # Next.js App Router
│   ├── api/predict/route.ts     # API route proxy (optional)
│   ├── globals.css              # Global styles
│   ├── layout.tsx               # Root layout
│   └── page.tsx                 # Homepage
├── backend/                      # Python FastAPI
│   ├── data/                    # Historical data
│   │   ├── premier/             # Premier League (2021-2024)
│   │   └── Ekstraklasa/         # Ekstraklasa (2021-2024)
│   ├── ml/                      # ML modules
│   │   ├── train_model.py       # Model training
│   │   └── utils.py             # Data loading utilities
│   ├── models/                  # Trained models
│   │   ├── model_premier.pkl    # Premier League model
│   │   └── model_ekstraklasa.pkl # Ekstraklasa model
│   ├── main.py                  # FastAPI application
│   ├── update_data.py           # Data fetching
│   └── venv/                    # Python virtual environment
├── components/                   # React components
│   ├── Predictor.tsx            # Main prediction component
│   ├── Card.tsx                 # Result card
│   ├── Button.tsx               # Button component
│   └── Select.tsx               # Selector component
├── lib/                         # TypeScript utilities
│   ├── api.ts                   # API functions
│   └── config.ts                # Configuration
├── types/                       # TypeScript definitions
│   └── predict.ts               # API types
└── data/                        # Static data
    └── teams.ts                 # League and team list
```

---

## Wymagania systemowe

- **Node.js**: >= 20.0.0
- **Python**: >= 3.11 (aktualnie 3.14.0)
- **npm**: >= 9.0.0 (lub yarn/pnpm)
- **System**: Windows/Linux/macOS

---

## System Requirements

- **Node.js**: >= 20.0.0
- **Python**: >= 3.11 (currently 3.14.0)
- **npm**: >= 9.0.0 (or yarn/pnpm)
- **System**: Windows/Linux/macOS

---

## Instalacja i uruchomienie

### KROK 1: Klonowanie repozytorium
```bash
git clone https://github.com/Ascher99/Pilka_Nozna_AI.git
cd Pilka_Nozna_AI
```

### KROK 2: Konfiguracja Frontend
```bash
# Instalacja zależności
npm install

# Uruchomienie serwera deweloperskiego (http://localhost:3000)
npm run dev
```

### KROK 3: Konfiguracja Backend
```bash
# Przejdź do katalogu backend
cd backend

# Utwórz wirtualne środowisko
python -m venv venv

# Aktywuj środowisko
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Zainstaluj zależności Pythona
pip install -r requirements.txt
```

### KROK 4: Trenowanie modeli ML
```bash
# Trenuj modele dla wszystkich lig
python -m ml.train_model
```

*Przykładowe wyjście:*
```
=======================================================
🤖 Rozpoczynam trening dla Ligi: PREMIER
📊 Trenuję na 1585 meczach.
🏆 Skuteczność modelu (Accuracy): 52.3%
              precision    recall  f1-score   support
        away       0.51      0.51      0.51       317
        draw       0.43      0.28      0.34       317
        home       0.57      0.78      0.66       317

Zapisano model ligi PREMIER do: backend/models/model_premier.pkl
```

### KROK 5: Uruchomienie FastAPI
```bash
# Uruchom serwer FastAPI (http://127.0.0.1:8000)
uvicorn main:app --reload
```

---

## Installation & Setup

### STEP 1: Clone Repository
```bash
git clone https://github.com/Ascher99/Pilka_Nozna_AI.git
cd Pilka_Nozna_AI
```

### STEP 2: Configure Frontend
```bash
# Install dependencies
npm install

# Start development server (http://localhost:3000)
npm run dev
```

### STEP 3: Configure Backend
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### STEP 4: Train ML Models
```bash
# Train models for all leagues
python -m ml.train_model
```

*Sample output:*
```
=======================================================
🤖 Starting training for League: PREMIER
📊 Training on 1585 matches.
🏆 Model Accuracy: 52.3%
              precision    recall  f1-score   support
        away       0.51      0.51      0.51       317
        draw       0.43      0.28      0.34       317
        home       0.57      0.78      0.66       317

Saved PREMIER league model to: backend/models/model_premier.pkl
```

### STEP 5: Run FastAPI
```bash
# Start FastAPI server (http://127.0.0.1:8000)
uvicorn main:app --reload
```

---

## Dostępne ligi

| Liga (League) | Kod (Code) | Drużyny (Teams) | Meczów (Matches) |
|--------------|-----------|----------------|-----------------|
| Premier League | `premier` | 20 | ~1650 |
| Ekstraklasa | `ekstraklasa` | 16 | ~650 |

**Dane historyczne**: 2021-2024 (sezon 21/22 - 24/25)

---

## Available Leagues

| League | Code | Teams | Matches |
|--------|------|-------|---------|
| Premier League | `premier` | 20 | ~1650 |
| Ekstraklasa | `ekstraklasa` | 16 | ~650 |

**Historical Data**: 2021-2024 (season 21/22 - 24/25)

---

## Dokumentacja API

### POST /api/predict

Przewidywanie wyniku meczu na podstawie formy drużyn.

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/api/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "league_id": "premier",
    "home_team": "Arsenal",
    "away_team": "Manchester United"
  }'
```

**Response:**
```json
{
  "label": "home",
  "probs": {
    "home": 0.52,
    "draw": 0.24,
    "away": 0.24
  },
  "home_form": ["W", "D", "W", "L", "W"],
  "away_form": ["L", "L", "D", "W", "L"]
}
```

**Pola:**
- `label`: Przewidywany wynik (`home` / `draw` / `away`)
- `probs`: Prawdopodobieństwa procentowe
- `home_form`: Forma gospodarza (ostatnie 5 meczów: W=Win, D=Draw, L=Loss)
- `away_form`: Forma gościa (ostatnie 5 meczów)

---

### GET /health

Status serwera i załadowanych modeli.

**Response:**
```json
{
  "status": "ok",
  "models_loaded": 2
}
```

---

## API Documentation

### POST /api/predict

Predict match result based on team form.

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/api/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "league_id": "premier",
    "home_team": "Arsenal",
    "away_team": "Manchester United"
  }'
```

**Response:**
```json
{
  "label": "home",
  "probs": {
    "home": 0.52,
    "draw": 0.24,
    "away": 0.24
  },
  "home_form": ["W", "D", "W", "L", "W"],
  "away_form": ["L", "L", "D", "W", "L"]
}
```

**Fields:**
- `label`: Predicted outcome (`home` / `draw` / `away`)
- `probs`: Probability percentages
- `home_form`: Home team form (last 5 matches: W=Win, D=Draw, L=Loss)
- `away_form`: Away team form (last 5 matches)

---

### GET /health

Server status and loaded models.

**Response:**
```json
{
  "status": "ok",
  "models_loaded": 2
}
```

---

## Model ML

### Algorytm
Logistic Regression (Multinomial)

### Cechy (Features)
- `h_form_goals`: Średnia goli gospodarza (ostatnie 5 meczów)
- `a_form_goals`: Średnia goli gościa (ostatnie 5 meczów)
- `h_form_points`: Średnia punktów gospodarza (ostatnie 5 meczów)
- `a_form_points`: Średnia punktów gościa (ostatnie 5 meczów)

### Źródła danych
- football-data.co.uk (Premier League)
- Dane lokalne (Ekstraklasa)
- Zakres czasowy: 2021-2024

### Metryki wydajności
| Liga | Accuracy | Precision | Recall | F1-Score |
|------|----------|-----------|--------|----------|
| Premier League | ~52% | ~50% | ~52% | ~50% |
| Ekstraklasa | ~54% | ~52% | ~54% | ~53% |

*Uwaga: Metryki są przybliżone i mogą się różnić w zależności od aktualności danych.*

---

## ML Model

### Algorithm
Logistic Regression (Multinomial)

### Features
- `h_form_goals`: Average home team goals (last 5 matches)
- `a_form_goals`: Average away team goals (last 5 matches)
- `h_form_points`: Average home team points (last 5 matches)
- `a_form_points`: Average away team points (last 5 matches)

### Data Sources
- football-data.co.uk (Premier League)
- Local data (Ekstraklasa)
- Time range: 2021-2024

### Performance Metrics
| League | Accuracy | Precision | Recall | F1-Score |
|--------|----------|-----------|--------|----------|
| Premier League | ~52% | ~50% | ~52% | ~50% |
| Ekstraklasa | ~54% | ~52% | ~54% | ~53% |

*Note: Metrics are approximate and may vary depending on data currency.*

---

## Środowisko rozwojowe

### Tryb Mock
Możliwość testowania aplikacji bez backendu. Ustaw w pliku `.env`:
```env
NEXT_PUBLIC_USE_MOCK=1
```

### Aktualizacja danych
```bash
cd backend
python update_data.py
```

### Trenowanie nowego modelu
```bash
cd backend
python -m ml.train_model
```

### Dokumentacja Swagger UI
Otwórz: `http://127.0.0.1:8000/docs` (jeśli włączono `--docs-url`)

---

## Development Environment

### Mock Mode
Ability to test the application without backend. Set in `.env` file:
```env
NEXT_PUBLIC_USE_MOCK=1
```

### Update Data
```bash
cd backend
python update_data.py
```

### Train New Model
```bash
cd backend
python -m ml.train_model
```

### Swagger UI Documentation
Open: `http://127.0.0.1:8000/docs` (if `--docs-url` is enabled)

---

## Plany rozwoju

### Krótka lista
- 🔄 Automatyczne aktualizowanie danych (cron/scheduled tasks)
- 📊 Dodatkowe statystyki (H2H, kontuzje, rankingi FIFA)
- 🌐 Nowe ligi (La Liga, Serie A, Bundesliga)
- 🤂 Bardziej zaawansowane modele ML (Random Forest, XGBoost, Neural Networks)
- ✅ Testy jednostkowe i integracyjne (pytest, Jest)
- 📈 Rozbudowane metryki (precision, recall, F1, confusion matrix)
- 🔐 OAuth 2.0 / JWT authentication
- 📱 PWA (Progressive Web App)
- 🎨 Dark mode

### Szczegółowy roadmap
| Priorytet | Zadanie | Status |
|----------|---------|--------|
| Wysoki | requirements.txt + dokumentacja | ⏳ W trakcie |
| Wysoki | Testy backend (pytest) | ⏳ W trakcie |
| Wysoki | Poprawa CORS security | ⏳ W trakcie |
| Średni | Testy frontend (Jest) | 📋 Planowane |
| Średni | Nowe ligi | 📋 Planowane |
| Średni | Lepszy model ML | 📋 Planowane |
| Niski | PWA + Dark mode | 📋 Planowane |

---

## Future Improvements

### Short List
- 🔄 Automatic data updates (cron/scheduled tasks)
- 📊 Additional statistics (H2H, injuries, FIFA rankings)
- 🌐 New leagues (La Liga, Serie A, Bundesliga)
- 🤂 More advanced ML models (Random Forest, XGBoost, Neural Networks)
- ✅ Unit and integration tests (pytest, Jest)
- 📈 Extended metrics (precision, recall, F1, confusion matrix)
- 🔐 OAuth 2.0 / JWT authentication
- 📱 PWA (Progressive Web App)
- 🎨 Dark mode

### Detailed Roadmap
| Priority | Task | Status |
|----------|------|--------|
| High | requirements.txt + documentation | ⏳ In Progress |
| High | Backend tests (pytest) | ⏳ In Progress |
| High | CORS security improvement | ⏳ In Progress |
| Medium | Frontend tests (Jest) | 📋 Planned |
| Medium | New leagues | 📋 Planned |
| Medium | Better ML model | 📋 Planned |
| Low | PWA + Dark mode | 📋 Planned |

---

## Licencja

```
MIT License

Copyright (c) 2025 Vu Minh Grzegorczyk

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## Kontakt (Contact)

**Autor:** Vu Minh Grzegorczyk
**Repozytorium:** https://github.com/Ascher99/Pilka_Nozna_AI

---

## Autor (Author)

**Vu Minh Grzegorczyk**

Thesis project demonstrating practical application of machine learning in football match prediction.

---

## Linki (Links)

- [Repozytorium GitHub](https://github.com/Ascher99/Pilka_Nozna_AI)
- [Next.js Documentation](https://nextjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [scikit-learn Documentation](https://scikit-learn.org/stable/documentation.html)

---

**Uwaga:** Projekt jest w trakcie rozwoju. Przed użyciem na produkcji zalecane jest przetestowanie i dostosowanie do własnych potrzeb.

---

**Note:** Project is under development. Before using in production, testing and adaptation to your needs is recommended.
