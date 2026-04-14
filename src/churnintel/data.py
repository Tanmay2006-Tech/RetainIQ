from __future__ import annotations

import numpy as np
import pandas as pd


def generate_churn_dataset(n_samples: int = 8000, random_state: int = 42) -> pd.DataFrame:
    """Generate a realistic synthetic churn dataset for demo and training."""
    rng = np.random.default_rng(random_state)

    age = rng.integers(18, 75, size=n_samples)
    monthly_spend = rng.normal(loc=72, scale=24, size=n_samples).clip(15, 220)
    tenure_months = rng.integers(1, 72, size=n_samples)
    support_tickets_90d = rng.poisson(2.2, size=n_samples).clip(0, 15)
    login_days_30d = rng.integers(0, 31, size=n_samples)

    contract_type = rng.choice(
        ["month-to-month", "one-year", "two-year"],
        size=n_samples,
        p=[0.58, 0.27, 0.15],
    )
    payment_method = rng.choice(
        ["electronic-check", "bank-transfer", "credit-card"],
        size=n_samples,
        p=[0.39, 0.34, 0.27],
    )
    region = rng.choice(["north", "south", "east", "west"], size=n_samples)

    # Non-linear logit builds realistic churn patterns.
    logits = (
        -0.8
        + 0.024 * monthly_spend
        - 0.031 * tenure_months
        + 0.22 * support_tickets_90d
        - 0.07 * login_days_30d
        + 0.006 * np.maximum(age - 55, 0)
    )

    logits += np.where(contract_type == "month-to-month", 0.55, 0.0)
    logits += np.where(contract_type == "two-year", -0.25, 0.0)
    logits += np.where(payment_method == "electronic-check", 0.3, 0.0)
    logits += rng.normal(0.0, 0.45, size=n_samples)

    prob = 1.0 / (1.0 + np.exp(-logits))
    churn = rng.binomial(1, prob, size=n_samples)

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
