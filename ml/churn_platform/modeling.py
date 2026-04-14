from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from ml.churn_platform.data import FEATURES

NUMERIC = [
    "age",
    "monthly_spend",
    "tenure_months",
    "support_tickets_90d",
    "login_days_30d",
]
CATEGORICAL = ["contract_type", "payment_method", "region"]


def build_preprocessor() -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            (
                "num",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                NUMERIC,
            ),
            (
                "cat",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                CATEGORICAL,
            ),
        ]
    )


def model_candidates(random_state: int = 42) -> dict[str, object]:
    candidates: dict[str, object] = {
        "logistic_regression": LogisticRegression(max_iter=1200),
        "random_forest": RandomForestClassifier(
            n_estimators=320,
            max_depth=8,
            random_state=random_state,
            n_jobs=-1,
        ),
    }
    try:
        from xgboost import XGBClassifier

        candidates["xgboost"] = XGBClassifier(
            n_estimators=260,
            learning_rate=0.05,
            max_depth=5,
            subsample=0.9,
            colsample_bytree=0.9,
            objective="binary:logistic",
            eval_metric="logloss",
            random_state=random_state,
            n_jobs=-1,
        )
    except Exception:
        # XGBoost is optional at runtime; pipeline remains functional without it.
        pass
    return candidates


@dataclass
class FitResult:
    best_name: str
    model: Pipeline
    leaderboard: pd.DataFrame


def train_best(x: pd.DataFrame, y: pd.Series, random_state: int = 42) -> FitResult:
    pre = build_preprocessor()
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=random_state)
    scoring = ["roc_auc", "f1", "precision", "recall"]

    best_score = -1.0
    best_name = ""
    best_pipeline: Pipeline | None = None
    rows: list[dict[str, float | str]] = []

    for name, model in model_candidates(random_state=random_state).items():
        pipe = Pipeline([("preprocess", pre), ("model", model)])
        scores = cross_validate(pipe, x, y, cv=cv, scoring=scoring, n_jobs=-1)

        row = {
            "model": name,
            "roc_auc_mean": float(scores["test_roc_auc"].mean()),
            "f1_mean": float(scores["test_f1"].mean()),
            "precision_mean": float(scores["test_precision"].mean()),
            "recall_mean": float(scores["test_recall"].mean()),
        }
        rows.append(row)

        if row["roc_auc_mean"] > best_score:
            best_score = row["roc_auc_mean"]
            best_name = name
            best_pipeline = pipe

    assert best_pipeline is not None
    best_pipeline.fit(x, y)

    leaderboard = pd.DataFrame(rows).sort_values(by="roc_auc_mean", ascending=False)
    return FitResult(best_name=best_name, model=best_pipeline, leaderboard=leaderboard)


def evaluate_split(model: Pipeline, x: pd.DataFrame, y: pd.Series) -> dict[str, float]:
    prob = model.predict_proba(x)[:, 1]
    pred = (prob >= 0.5).astype(int)
    return {
        "roc_auc": float(roc_auc_score(y, prob)),
        "f1": float(f1_score(y, pred, zero_division=0)),
        "precision": float(precision_score(y, pred, zero_division=0)),
        "recall": float(recall_score(y, pred, zero_division=0)),
    }


def ensure_feature_columns(df: pd.DataFrame) -> pd.DataFrame:
    return df[FEATURES].copy()
