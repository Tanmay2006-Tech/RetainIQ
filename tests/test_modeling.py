from churnintel.data import generate_churn_dataset
from churnintel.modeling import evaluate_classification, train_best_model


def test_training_and_metrics_shape() -> None:
    df = generate_churn_dataset(n_samples=1200, random_state=7)
    x = df.drop(columns=["churn"])
    y = df["churn"]

    result = train_best_model(x, y, random_state=7, cv_splits=3)
    metrics = evaluate_classification(result.best_pipeline, x, y)

    assert result.best_name in {"logistic_regression", "random_forest"}
    assert "cv_roc_auc_mean" in result.leaderboard.columns
    assert 0.0 <= metrics["roc_auc"] <= 1.0
    assert 0.0 <= metrics["f1"] <= 1.0
