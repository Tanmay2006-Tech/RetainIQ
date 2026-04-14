from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd

from ml.churn_platform.insights import generate_recommendations
from ml.churn_platform.predictor import ChurnPredictor


def artifact_dir() -> Path:
    return Path(os.getenv("CHURN_ARTIFACT_DIR", "artifacts")).resolve()


@lru_cache
def predictor() -> ChurnPredictor:
    return ChurnPredictor.load(artifact_dir())


def predict_customer(payload: dict[str, Any]) -> dict[str, Any]:
    pred = predictor().predict_with_explanation(payload)
    smart = generate_recommendations(payload, pred["churn_probability"], pred["explanation"])
    pred["insights"] = smart["insights"]
    pred["recommendations"] = smart["recommendations"]
    return pred


def get_metrics() -> dict[str, Any]:
    path = artifact_dir() / "metrics.json"
    if not path.exists():
        return {"status": "missing", "detail": "Train model first"}
    return json.loads(path.read_text(encoding="utf-8"))


def get_feature_importance(limit: int = 20) -> list[dict[str, Any]]:
    path = artifact_dir() / "feature_importance.csv"
    if not path.exists():
        return []
    df = pd.read_csv(path).head(limit)
    return df.to_dict(orient="records")


def get_segment_snapshot() -> dict[str, Any]:
    pred = predictor()
    population = pred.background_df.copy()
    scores = pred.predict_batch(population)
    population["churn_probability"] = scores
    population["risk"] = population["churn_probability"].map(pred.risk_band)
    population["revenue_at_risk"] = (
        population["monthly_spend"].astype(float)
        * population["churn_probability"].astype(float)
        * population["tenure_months"].clip(lower=1).astype(float)
    )

    total = int(len(population))
    high_risk = int((population["risk"] == "high").sum())
    churn_rate = float((population["churn_probability"] >= 0.5).mean())
    revenue_at_risk = float(population["revenue_at_risk"].sum())

    segments = (
        population.groupby("risk")
        .size()
        .rename("count")
        .reset_index()
        .sort_values(by="count", ascending=False)
    )
    return {
        "kpis": {
            "total_customers": total,
            "high_risk_users": high_risk,
            "predicted_churn_rate": round(churn_rate, 4),
            "revenue_at_risk": round(revenue_at_risk, 2),
        },
        "segments": segments.to_dict(orient="records"),
        "sample_rows": population.head(120).to_dict(orient="records"),
    }


def get_revenue_impact() -> dict[str, Any]:
    pred = predictor()
    population = pred.background_df.copy()
    scores = pred.predict_batch(population)
    population["churn_probability"] = scores
    population["risk"] = population["churn_probability"].map(pred.risk_band)
    population["revenue_at_risk"] = (
        population["monthly_spend"].astype(float)
        * population["churn_probability"].astype(float)
        * population["tenure_months"].clip(lower=1).astype(float)
    )

    top = (
        population.sort_values(by="revenue_at_risk", ascending=False)
        .head(10)
        .assign(
            retained_if_saved=lambda df: df["revenue_at_risk"] * 0.7,
            customer_label=lambda df: [f"User {i+1}" for i in range(len(df))],
        )
    )
    return {
        "total_risk_revenue": round(float(population["revenue_at_risk"].sum()), 2),
        "top_10_retained_revenue": round(float(top["retained_if_saved"].sum()), 2),
        "top_customers": top[
            ["customer_label", "monthly_spend", "churn_probability", "revenue_at_risk", "risk"]
        ].rename(columns={"customer_label": "customer"}).to_dict(orient="records"),
        "currency": "INR",
    }
