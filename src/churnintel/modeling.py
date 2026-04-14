from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


NUMERIC_FEATURES = [
    "age",
    "monthly_spend",
    "tenure_months",
    "support_tickets_90d",
    "login_days_30d",
]

CATEGORICAL_FEATURES = ["contract_type", "payment_method", "region"]


def build_preprocessor() -> ColumnTransformer:
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, NUMERIC_FEATURES),
            ("cat", categorical_pipeline, CATEGORICAL_FEATURES),
        ]
    )


def candidate_models(random_state: int = 42) -> dict[str, object]:
    return {
        "logistic_regression": LogisticRegression(max_iter=1000, n_jobs=None),
        "random_forest": RandomForestClassifier(
            n_estimators=350,
            min_samples_leaf=2,
            random_state=random_state,
            n_jobs=-1,
        ),
    }


@dataclass
class TrainingResult:
    best_name: str
    best_pipeline: Pipeline
    leaderboard: pd.DataFrame


def train_best_model(
    x_train: pd.DataFrame,
    y_train: pd.Series,
    random_state: int = 42,
    cv_splits: int = 5,
) -> TrainingResult:
    preprocessor = build_preprocessor()
    models = candidate_models(random_state=random_state)
    cv = StratifiedKFold(n_splits=cv_splits, shuffle=True, random_state=random_state)

    rows: list[dict[str, float | str]] = []
    best_name = ""
    best_score = -1.0
    best_pipeline: Pipeline | None = None

    for name, model in models.items():
        pipeline = Pipeline(
            steps=[
                ("preprocess", preprocessor),
                ("model", model),
            ]
        )

        scores = cross_val_score(
            pipeline,
            x_train,
            y_train,
            scoring="roc_auc",
            cv=cv,
            n_jobs=-1,
        )
        mean_score = float(scores.mean())

        rows.append(
            {
                "model": name,
                "cv_roc_auc_mean": mean_score,
                "cv_roc_auc_std": float(scores.std()),
            }
        )

        if mean_score > best_score:
            best_name = name
            best_score = mean_score
            best_pipeline = pipeline

    assert best_pipeline is not None
    best_pipeline.fit(x_train, y_train)

    leaderboard = pd.DataFrame(rows).sort_values(
        by="cv_roc_auc_mean", ascending=False
    )
    return TrainingResult(
        best_name=best_name,
        best_pipeline=best_pipeline,
        leaderboard=leaderboard,
    )


def evaluate_classification(pipeline: Pipeline, x: pd.DataFrame, y: pd.Series) -> dict[str, float]:
    pred = pipeline.predict(x)
    pred_prob = pipeline.predict_proba(x)[:, 1]

    return {
        "roc_auc": float(roc_auc_score(y, pred_prob)),
        "pr_auc": float(average_precision_score(y, pred_prob)),
        "f1": float(f1_score(y, pred)),
        "precision": float(precision_score(y, pred)),
        "recall": float(recall_score(y, pred)),
    }
