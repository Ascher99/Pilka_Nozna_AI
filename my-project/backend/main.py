from pathlib import Path
import joblib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model.pkl"
ENCODER_PATH = BASE_DIR / "label_encoder.pkl"

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

class PredictIn(BaseModel):
    home_team: str
    away_team: str

model = None
le = None
if MODEL_PATH.exists() and ENCODER_PATH.exists():
    model = joblib.load(MODEL_PATH)
    le = joblib.load(ENCODER_PATH)
else:
    print("⚠️  Brak model.pkl/label_encoder.pkl – używam trybu MOCK.")

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": bool(model)}

@app.post("/api/predict")
def predict(inp: PredictIn):
    if model is not None and le is not None:
        try:
            home_enc = le.transform([inp.home_team])[0]
            away_enc = le.transform([inp.away_team])[0]
        except Exception:
            # drużyna nieznana encoderowi – bez crasha:
            return {"label": "home", "probs": {"home": 0.34, "draw": 0.33, "away": 0.33}}
        X = [[home_enc, away_enc]]
        probs_raw = model.predict_proba(X)[0]
        classes = model.classes_  # np. [-1, 0, 1]
        m = {int(c): float(p) for c, p in zip(classes, probs_raw)}
        probs = {"home": m.get(1, 0.0), "draw": m.get(0, 0.0), "away": m.get(-1, 0.0)}
        label = max(probs, key=probs.get)
        return {"label": label, "probs": probs}

    # MOCK (gdy brak modelu)
    seed = (len(inp.home_team) * 13 + len(inp.away_team) * 7) % 100
    home = 0.42 + (seed % 10) / 100
    away = 0.25 + ((seed + 3) % 10) / 100
    draw = max(0.0, 1 - home - away)
    probs = {"home": home, "draw": draw, "away": away}
    label = max(probs, key=probs.get)
    return {"label": label, "probs": probs}
