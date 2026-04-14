from pathlib import Path

from ml.churn_platform.train import run_training


def test_training_pipeline_writes_artifacts(tmp_path: Path) -> None:
    result = run_training(
        dataset="synthetic",
        output_dir=tmp_path,
        n_samples=900,
        random_state=5,
    )

    assert Path(result["model_path"]).exists()
    assert Path(result["metrics_path"]).exists()
    assert Path(result["leaderboard_path"]).exists()
    assert Path(result["feature_path"]).exists()
    assert Path(result["background_path"]).exists()
    assert Path(result["shap_path"]).exists()
