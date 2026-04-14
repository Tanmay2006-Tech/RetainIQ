from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=3, max_length=128)


class CustomerFeatures(BaseModel):
    age: int = Field(ge=18, le=90)
    monthly_spend: float = Field(ge=0, le=400)
    tenure_months: int = Field(ge=0, le=120)
    support_tickets_90d: int = Field(ge=0, le=50)
    login_days_30d: int = Field(ge=0, le=31)
    contract_type: Literal["month-to-month", "one-year", "two-year"]
    payment_method: Literal["electronic-check", "bank-transfer", "credit-card"]
    region: Literal["north", "south", "east", "west"]


class ExplainFactor(BaseModel):
    feature: str
    impact: float
    direction: Literal["increases_churn", "decreases_churn"]


class PredictionResponse(BaseModel):
    churn_probability: float
    risk_category: Literal["low", "medium", "high"]
    explanation: list[ExplainFactor]
    insights: list[str]
    recommendations: list[str]
