from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
from sklearn.inspection import permutation_importance
from sklearn.model_selection import train_test_split

from churnintel.data import generate_churn_dataset
from churnintel.modeling import evaluate_classification, train_best_model


def run_training(
    output_dir: Path,
    n_samples: int = 8000,
    random_state: int = 42,
) -> dict[str, object]:
    df = generate_churn_dataset(n_samples=n_samples, random_state=random_state)
    x = df.drop(columns=["churn"])
    y = df["churn"]

    x_train, x_temp, y_train, y_temp = train_test_split(
        x,
        y,
        test_size=0.30,
        stratify=y,
        random_state=random_state,
    )
    x_valid, x_test, y_valid, y_test = train_test_split(
        x_temp,
        y_temp,
        test_size=0.50,
        stratify=y_temp,
        random_state=random_state,
    )

    result = train_best_model(x_train, y_train, random_state=random_state)
    valid_metrics = evaluate_classification(result.best_pipeline, x_valid, y_valid)
    test_metrics = evaluate_classification(result.best_pipeline, x_test, y_test)

    output_dir.mkdir(parents=True, exist_ok=True)

    model_path = output_dir / "model.joblib"
    metrics_path = output_dir / "metrics.json"
    leaderboard_path = output_dir / "leaderboard.csv"
    feature_path = output_dir / "feature_importance.csv"

    joblib.dump(result.best_pipeline, model_path)
    result.leaderboard.to_csv(leaderboard_path, index=False)

    metrics = {
        "best_model": result.best_name,
        "validation": valid_metrics,
        "test": test_metrics,
    }
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    # Permutation importance provides model-agnostic feature ranking.
    perm = permutation_importance(
        result.best_pipeline,
        x_valid,
        y_valid,
        n_repeats=8,
        random_state=random_state,
        n_jobs=-1,
        scoring="roc_auc",
    )
    feature_importance = (
        __import__("pandas").DataFrame(
            {
                "feature": x_valid.columns,
                "importance_mean": perm.importances_mean,
                "importance_std": perm.importances_std,
            }
        )
        .sort_values(by="importance_mean", ascending=False)
        .reset_index(drop=True)
    )
    feature_importance.to_csv(feature_path, index=False)

    return {
        "model_path": str(model_path),
        "metrics_path": str(metrics_path),
        "leaderboard_path": str(leaderboard_path),
        "feature_path": str(feature_path),
        "metrics": metrics,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Train churn prediction model")
    parser.add_argument("--n-samples", type=int, default=8000)
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument("--output-dir", type=str, default="artifacts")
    args = parser.parse_args()

    summary = run_training(
        output_dir=Path(args.output_dir),
        n_samples=args.n_samples,
        random_state=args.random_state,
    )
    print(json.dumps(summary["metrics"], indent=2))


if __name__ == "__main__":
    main()
