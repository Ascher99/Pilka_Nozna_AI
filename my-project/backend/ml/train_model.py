from __future__ import annotations
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss, brier_score_loss

from utils import load_matches_folder

BASE_DIR = Path(__file__).resolve().parents[1]  # -> backend/
DATA_DIR = BASE_DIR / "data" / "Ekstraklasa"
MODEL_PATH = BASE_DIR / "model.pkl"
ENCODER_PATH = BASE_DIR / "label_encoder.pkl"


def result_label(hg: int, ag: int) -> int:
    if hg > ag:
        return 1     # home
    if hg < ag:
        return -1    # away
    return 0         # draw


def main():
    print(f"Ładowanie CSV z: {DATA_DIR}")
    df = load_matches_folder(DATA_DIR)

    # 🔍 DEBUG – sprawdzenie, że bierzemy wszystkie sezony
    print("Liczba wierszy (wszystkie sezony razem):", df.shape[0])
    print("Zakres dat:", df["date"].min(), "→", df["date"].max())
    print("Unikalne drużyny (home):", df["home_team"].nunique())
    print("Unikalne drużyny (away):", df["away_team"].nunique())
    print("Przykładowe mecze:")
    print(df.head(5))
    print("-" * 60)

    # etykiety
    df["result"] = [result_label(h, a) for h, a in zip(df["home_goals"], df["away_goals"])]

    # enkoder zespołów
    le = LabelEncoder()
    teams_all = pd.unique(pd.concat([df["home_team"], df["away_team"]], axis=0))
    le.fit(teams_all)

    df["home_enc"] = le.transform(df["home_team"])
    df["away_enc"] = le.transform(df["away_team"])

    # Prosty baseline: tylko identyfikatory drużyn
    X = df[["home_enc", "away_enc"]].values
    y = df["result"].values

    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    clf = LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
        multi_class="auto",
    )
    clf.fit(X_tr, y_tr)

    # ewaluacja
    y_proba = clf.predict_proba(X_te)
    y_pred = clf.predict(X_te)

    classes = clf.classes_  # np. [-1, 0, 1]
    acc = accuracy_score(y_te, y_pred)
    ll = log_loss(y_te, y_proba, labels=classes)

    # brier multi-class – średnia po klasach
    briers = []
    for idx, c in enumerate(classes):
        y_true_bin = (y_te == c).astype(int)
        y_prob_bin = y_proba[:, idx]
        briers.append(brier_score_loss(y_true_bin, y_prob_bin))
    brier = float(np.mean(briers))

    print(f"Accuracy: {acc:.3f} | LogLoss: {ll:.3f} | Brier: {brier:.3f}")
    print(f"Zespołów w encoderze: {len(le.classes_)}")

    joblib.dump(clf, MODEL_PATH)
    joblib.dump(le, ENCODER_PATH)
    print(f"Zapisano: {MODEL_PATH.name}, {ENCODER_PATH.name}")


if __name__ == "__main__":
    main()
