from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from ml.churn_platform.data import FEATURES
from ml.churn_platform.explain import explain_single


@dataclass
class ChurnPredictor:
    model: Any
    background_df: pd.DataFrame

    @classmethod
    def load(cls, artifacts_dir: str | Path) -> "ChurnPredictor":
        root = Path(artifacts_dir)
        model = joblib.load(root / "model.joblib")
        bg_path = root / "background_sample.csv"
        if bg_path.exists():
            bg = pd.read_csv(bg_path)
        else:
            # Minimal safe default if background sample is unavailable.
            bg = pd.DataFrame(
                [
                    {
                        "age": 34,
                        "monthly_spend": 79,
                        "tenure_months": 22,
                        "support_tickets_90d": 1,
                        "login_days_30d": 18,
                        "contract_type": "one-year",
                        "payment_method": "credit-card",
                        "region": "north",
                    }
                ]
            )
        return cls(model=model, background_df=bg[FEATURES])

    @staticmethod
    def risk_band(probability: float) -> str:
        if probability >= 0.7:
            return "high"
        if probability >= 0.4:
            return "medium"
        return "low"

    def predict_batch(self, frame: pd.DataFrame) -> pd.Series:
        probs = self.model.predict_proba(frame[FEATURES])[:, 1]
        return pd.Series(probs)

    def predict_with_explanation(self, payload: dict[str, Any]) -> dict[str, Any]:
        row = pd.DataFrame([payload])[FEATURES]
        probability = float(self.model.predict_proba(row)[:, 1][0])
        explanation = explain_single(self.model, self.background_df, row)
        return {
            "churn_probability": round(probability, 4),
            "risk_category": self.risk_band(probability),
            "explanation": explanation,
        }
