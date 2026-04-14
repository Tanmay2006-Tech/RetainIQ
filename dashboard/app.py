from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from churnintel.inference import load_model, predict_one


st.set_page_config(page_title="Churn Intelligence Dashboard", layout="wide")
st.title("Churn Intelligence Dashboard")
st.caption("Real-time churn scoring and model artifact insights")

artifact_dir = Path(__file__).resolve().parents[1] / "artifacts"
model_path = artifact_dir / "model.joblib"
metrics_path = artifact_dir / "metrics.json"
feature_path = artifact_dir / "feature_importance.csv"

if not model_path.exists():
    st.warning("Model artifact not found. Run training first.")
    st.stop()

model = load_model(model_path)

col1, col2, col3 = st.columns(3)
with col1:
    age = st.number_input("Age", min_value=18, max_value=90, value=35)
    monthly_spend = st.number_input("Monthly Spend", min_value=0.0, max_value=400.0, value=80.0)
    tenure_months = st.number_input("Tenure (months)", min_value=0, max_value=120, value=12)
with col2:
    support_tickets_90d = st.number_input("Support Tickets (90d)", min_value=0, max_value=50, value=2)
    login_days_30d = st.number_input("Login Days (30d)", min_value=0, max_value=31, value=14)
with col3:
    contract_type = st.selectbox("Contract", ["month-to-month", "one-year", "two-year"])
    payment_method = st.selectbox("Payment Method", ["electronic-check", "bank-transfer", "credit-card"])
    region = st.selectbox("Region", ["north", "south", "east", "west"])

if st.button("Predict Churn Risk"):
    payload = {
        "age": int(age),
        "monthly_spend": float(monthly_spend),
        "tenure_months": int(tenure_months),
        "support_tickets_90d": int(support_tickets_90d),
        "login_days_30d": int(login_days_30d),
        "contract_type": contract_type,
        "payment_method": payment_method,
        "region": region,
    }
    result = predict_one(model, payload)
    st.subheader("Prediction")
    st.json(result)

st.divider()
left, right = st.columns(2)

with left:
    st.subheader("Model Metrics")
    if metrics_path.exists():
        st.json(json.loads(metrics_path.read_text(encoding="utf-8")))
    else:
        st.info("metrics.json not found.")

with right:
    st.subheader("Top Features")
    if feature_path.exists():
        importance_df = pd.read_csv(feature_path)
        st.dataframe(importance_df.head(10), use_container_width=True)
    else:
        st.info("feature_importance.csv not found.")
