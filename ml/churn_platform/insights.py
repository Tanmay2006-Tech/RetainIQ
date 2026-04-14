from __future__ import annotations

from typing import Any


def generate_recommendations(
    payload: dict[str, Any],
    churn_probability: float,
    explanation: list[dict[str, Any]],
) -> dict[str, list[str]]:
    insights: list[str] = []
    recs: list[str] = []

    if payload.get("login_days_30d", 0) <= 8:
        insights.append("Low login activity indicates weak product engagement.")
        recs.append("Send engagement email with product tips and onboarding nudges.")

    if payload.get("support_tickets_90d", 0) >= 4:
        insights.append("High support volume suggests unresolved friction.")
        recs.append("Route account to success manager and prioritize ticket resolution.")

    if payload.get("contract_type") == "month-to-month":
        insights.append("Month-to-month plans show higher churn volatility.")
        recs.append("Offer annual plan discount and loyalty incentives.")

    if payload.get("payment_method") == "electronic-check":
        insights.append("Electronic check users have elevated payment-related churn risk.")
        recs.append("Promote auto-pay migration with a one-time credit.")

    if churn_probability >= 0.7:
        recs.append("Trigger immediate retention workflow within 24 hours.")
    elif churn_probability >= 0.4:
        recs.append("Queue personalized outreach campaign this week.")

    if not insights:
        top = explanation[:2]
        if top:
            factor_names = ", ".join(item["feature"] for item in top)
            insights.append(f"Main model drivers for this customer are: {factor_names}.")
        else:
            insights.append("Customer profile is currently stable with no dominant churn trigger.")

    if not recs:
        recs.append("Maintain proactive engagement and monitor monthly behavior shifts.")

    return {"insights": insights[:4], "recommendations": recs[:5]}
