from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.inspection import permutation_importance
from sklearn.model_selection import train_test_split

from ml.churn_platform.data import FEATURES, load_training_frame
from ml.churn_platform.explain import shap_global_importance
from ml.churn_platform.modeling import ensure_feature_columns, evaluate_split, train_best


def run_training(
    dataset: str,
    output_dir: Path,
    n_samples: int = 12000,
    random_state: int = 42,
    telco_path: str | None = None,
) -> dict[str, object]:
    frame = load_training_frame(
        dataset=dataset,
        n_samples=n_samples,
        random_state=random_state,
        telco_path=telco_path,
    )

    x = ensure_feature_columns(frame)
    y = frame["churn"].astype(int)

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

    result = train_best(x_train, y_train, random_state=random_state)
    valid_metrics = evaluate_split(result.model, x_valid, y_valid)
    test_metrics = evaluate_split(result.model, x_test, y_test)

    output_dir.mkdir(parents=True, exist_ok=True)

    model_path = output_dir / "model.joblib"
    metrics_path = output_dir / "metrics.json"
    leaderboard_path = output_dir / "leaderboard.csv"
    feature_path = output_dir / "feature_importance.csv"
    bg_path = output_dir / "background_sample.csv"
    shap_path = output_dir / "shap_global.csv"

    joblib.dump(result.model, model_path)
    result.leaderboard.to_csv(leaderboard_path, index=False)

    perm = permutation_importance(
        result.model,
        x_valid,
        y_valid,
        n_repeats=8,
        random_state=random_state,
        n_jobs=-1,
        scoring="roc_auc",
    )
    feature_importance = pd.DataFrame(
        {
            "feature": FEATURES,
            "importance_mean": perm.importances_mean,
            "importance_std": perm.importances_std,
        }
    ).sort_values(by="importance_mean", ascending=False)
    feature_importance.to_csv(feature_path, index=False)

    background = x_train.sample(min(200, len(x_train)), random_state=random_state)
    background.to_csv(bg_path, index=False)

    shap_df = shap_global_importance(
        result.model,
        background_raw=background,
        sample_raw=x_valid.sample(min(300, len(x_valid)), random_state=random_state),
    )
    shap_df.to_csv(shap_path, index=False)

    metrics = {
        "dataset": dataset,
        "best_model": result.best_name,
        "validation": valid_metrics,
        "test": test_metrics,
        "leaderboard": result.leaderboard.to_dict(orient="records"),
    }
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    return {
        "model_path": str(model_path),
        "metrics_path": str(metrics_path),
        "leaderboard_path": str(leaderboard_path),
        "feature_path": str(feature_path),
        "background_path": str(bg_path),
        "shap_path": str(shap_path),
        "metrics": metrics,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Train Churn Intelligence model")
    parser.add_argument("--dataset", choices=["synthetic", "telco"], default="synthetic")
    parser.add_argument("--telco-path", type=str, default=None)
    parser.add_argument("--n-samples", type=int, default=12000)
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument("--output-dir", type=str, default="artifacts")
    args = parser.parse_args()

    summary = run_training(
        dataset=args.dataset,
        output_dir=Path(args.output_dir),
        n_samples=args.n_samples,
        random_state=args.random_state,
        telco_path=args.telco_path,
    )
    print(json.dumps(summary["metrics"], indent=2))


if __name__ == "__main__":
    main()
