from __future__ import annotations

from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from churnintel.inference import load_model, predict_one


class CustomerFeatures(BaseModel):
    age: int = Field(ge=18, le=90)
    monthly_spend: float = Field(ge=0, le=400)
    tenure_months: int = Field(ge=0, le=120)
    support_tickets_90d: int = Field(ge=0, le=50)
    login_days_30d: int = Field(ge=0, le=31)
    contract_type: Literal["month-to-month", "one-year", "two-year"]
    payment_method: Literal["electronic-check", "bank-transfer", "credit-card"]
    region: Literal["north", "south", "east", "west"]


app = FastAPI(title="Churn Intelligence API", version="1.0.0")

MODEL_PATH = Path(__file__).resolve().parents[1] / "artifacts" / "model.joblib"
MODEL = None


@app.on_event("startup")
def startup_event() -> None:
    global MODEL
    if MODEL_PATH.exists():
        MODEL = load_model(MODEL_PATH)


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok" if MODEL is not None else "model_not_loaded",
    }


@app.post("/predict")
def predict(customer: CustomerFeatures) -> dict[str, object]:
    if MODEL is None:
        raise HTTPException(status_code=503, detail="Model not loaded. Train first.")

    payload = customer.model_dump()
    return {
        "input": payload,
        "prediction": predict_one(MODEL, payload),
    }
