from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


FEATURES = [
    "age",
    "monthly_spend",
    "tenure_months",
    "support_tickets_90d",
    "login_days_30d",
    "contract_type",
    "payment_method",
    "region",
]


def generate_synthetic_churn(n_samples: int = 8000, random_state: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(random_state)

    age = rng.integers(18, 75, size=n_samples)
    monthly_spend = rng.normal(loc=72, scale=24, size=n_samples).clip(15, 220)
    tenure_months = rng.integers(1, 72, size=n_samples)
    support_tickets_90d = rng.poisson(2.1, size=n_samples).clip(0, 14)
    login_days_30d = rng.integers(0, 31, size=n_samples)

    contract_type = rng.choice(
        ["month-to-month", "one-year", "two-year"],
        p=[0.58, 0.27, 0.15],
        size=n_samples,
    )
    payment_method = rng.choice(
        ["electronic-check", "bank-transfer", "credit-card"],
        p=[0.39, 0.34, 0.27],
        size=n_samples,
    )
    region = rng.choice(["north", "south", "east", "west"], size=n_samples)

    logits = (
        -0.8
        + 0.024 * monthly_spend
        - 0.031 * tenure_months
        + 0.23 * support_tickets_90d
        - 0.075 * login_days_30d
        + 0.006 * np.maximum(age - 55, 0)
    )
    logits += np.where(contract_type == "month-to-month", 0.6, 0.0)
    logits += np.where(contract_type == "two-year", -0.3, 0.0)
    logits += np.where(payment_method == "electronic-check", 0.25, 0.0)
    logits += rng.normal(0.0, 0.45, size=n_samples)

    churn_prob = 1.0 / (1.0 + np.exp(-logits))
    churn = rng.binomial(1, churn_prob, size=n_samples)

    return pd.DataFrame(
        {
            "age": age,
            "monthly_spend": monthly_spend.round(2),
            "tenure_months": tenure_months,
            "support_tickets_90d": support_tickets_90d,
            "login_days_30d": login_days_30d,
            "contract_type": contract_type,
            "payment_method": payment_method,
            "region": region,
            "churn": churn,
        }
    )


def load_telco_dataset(path: str | Path) -> pd.DataFrame:
    src = Path(path)
    if not src.exists():
        raise FileNotFoundError(f"Telco dataset file not found: {src}")

    df = pd.read_csv(src)
    lower_map = {c.lower(): c for c in df.columns}

    def col(*names: str) -> str:
        for name in names:
            if name.lower() in lower_map:
                return lower_map[name.lower()]
        raise KeyError(f"Could not find any of columns: {names}")

    churn_col = col("Churn", "churn")
    tenure_col = col("tenure", "tenure_months")
    monthly_col = col("MonthlyCharges", "monthly_spend")
    contract_col = col("Contract", "contract_type")
    payment_col = col("PaymentMethod", "payment_method")

    if "TotalCharges" in df.columns:
        total = pd.to_numeric(df["TotalCharges"], errors="coerce")
    else:
        total = pd.to_numeric(df[monthly_col], errors="coerce") * pd.to_numeric(
            df[tenure_col], errors="coerce"
        )

    churn_binary = (
        df[churn_col]
        .astype(str)
        .str.strip()
        .str.lower()
        .map({"yes": 1, "no": 0, "1": 1, "0": 0})
        .fillna(0)
        .astype(int)
    )

    region = np.where(
        pd.to_numeric(total, errors="coerce").fillna(0) > np.nanmedian(total.fillna(0)),
        "north",
        "south",
    )

    out = pd.DataFrame(
        {
            "age": 35,
            "monthly_spend": pd.to_numeric(df[monthly_col], errors="coerce").fillna(0),
            "tenure_months": pd.to_numeric(df[tenure_col], errors="coerce").fillna(0),
            "support_tickets_90d": (
                pd.to_numeric(df[tenure_col], errors="coerce").fillna(0).rsub(72).clip(0, 12)
                / 6
            )
            .round()
            .astype(int),
            "login_days_30d": (
                30
                - (
                    pd.to_numeric(df[monthly_col], errors="coerce").fillna(0)
                    / max(1.0, pd.to_numeric(df[monthly_col], errors="coerce").median())
                    * 7
                )
            )
            .clip(0, 30)
            .round()
            .astype(int),
            "contract_type": (
                df[contract_col]
                .astype(str)
                .str.lower()
                .replace({"month-to-month": "month-to-month", "one year": "one-year", "two year": "two-year"})
            ),
            "payment_method": (
                df[payment_col]
                .astype(str)
                .str.lower()
                .map(
                    {
                        "electronic check": "electronic-check",
                        "bank transfer (automatic)": "bank-transfer",
                        "credit card (automatic)": "credit-card",
                        "mailed check": "bank-transfer",
                    }
                )
                .fillna("bank-transfer")
            ),
            "region": region,
            "churn": churn_binary,
        }
    )
    out["contract_type"] = out["contract_type"].where(
        out["contract_type"].isin(["month-to-month", "one-year", "two-year"]),
        "month-to-month",
    )
    return out


def load_training_frame(
    dataset: str,
    n_samples: int,
    random_state: int,
    telco_path: str | None,
) -> pd.DataFrame:
    if dataset == "synthetic":
        return generate_synthetic_churn(n_samples=n_samples, random_state=random_state)
    if dataset == "telco":
        if telco_path is None:
            raise ValueError("--telco-path is required for dataset=telco")
        return load_telco_dataset(telco_path)
    raise ValueError(f"Unsupported dataset mode: {dataset}")
