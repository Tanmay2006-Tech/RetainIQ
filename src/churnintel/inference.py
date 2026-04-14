from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import pandas as pd


def load_model(model_path: str | Path):
    return joblib.load(model_path)


def risk_band(probability: float) -> str:
    if probability >= 0.7:
        return "high"
    if probability >= 0.4:
        return "medium"
    return "low"


def predict_one(model: Any, payload: dict[str, Any]) -> dict[str, Any]:
    row = pd.DataFrame([payload])
    proba = float(model.predict_proba(row)[:, 1][0])
    return {
        "churn_probability": round(proba, 4),
        "risk_band": risk_band(proba),
    }
