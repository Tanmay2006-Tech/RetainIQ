from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def _extract_shap_vector(shap_values: Any) -> np.ndarray:
    values = getattr(shap_values, "values", shap_values)
    arr = np.asarray(values)
    if arr.ndim == 3:
        # Binary tree explainers may return [samples, features, classes].
        arr = arr[:, :, 1]
    if arr.ndim == 2:
        return arr[0]
    return arr


def explain_single(model: Any, background_raw: pd.DataFrame, row_raw: pd.DataFrame) -> list[dict[str, Any]]:
    pre = model.named_steps["preprocess"]
    clf = model.named_steps["model"]

    bg = pre.transform(background_raw)
    row = pre.transform(row_raw)

    try:
        import shap

        feature_names = pre.get_feature_names_out()
        explainer = shap.Explainer(clf, bg, feature_names=feature_names)
        values = explainer(row)
        vec = _extract_shap_vector(values)
    except Exception:
        # Fall back to a safe signal if SHAP fails in a constrained environment.
        feature_names = pre.get_feature_names_out()
        dense_bg = bg.toarray() if hasattr(bg, "toarray") else np.asarray(bg)
        dense_row = row.toarray() if hasattr(row, "toarray") else np.asarray(row)
        baseline = np.nanmean(dense_bg, axis=0)
        vec = (dense_row[0] - baseline) * 0.01

    order = np.argsort(np.abs(vec))[::-1][:6]
    out: list[dict[str, Any]] = []
    for idx in order:
        impact = float(vec[idx])
        out.append(
            {
                "feature": str(feature_names[idx]),
                "impact": round(impact, 5),
                "direction": "increases_churn" if impact >= 0 else "decreases_churn",
            }
        )
    return out


def shap_global_importance(
    model: Any,
    background_raw: pd.DataFrame,
    sample_raw: pd.DataFrame,
    top_n: int = 30,
) -> pd.DataFrame:
    pre = model.named_steps["preprocess"]
    clf = model.named_steps["model"]
    bg = pre.transform(background_raw)
    sample = pre.transform(sample_raw)

    try:
        import shap

        names = pre.get_feature_names_out()
        explainer = shap.Explainer(clf, bg, feature_names=names)
        values = explainer(sample)
        arr = np.asarray(getattr(values, "values", values))
        if arr.ndim == 3:
            arr = arr[:, :, 1]
        impact = np.abs(arr).mean(axis=0)
    except Exception:
        names = pre.get_feature_names_out()
        sample_dense = sample.toarray() if hasattr(sample, "toarray") else np.asarray(sample)
        impact = np.abs(sample_dense).mean(axis=0)

    frame = pd.DataFrame({"feature": names, "importance": impact})
    return frame.sort_values("importance", ascending=False).head(top_n).reset_index(drop=True)
