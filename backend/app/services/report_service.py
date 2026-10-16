from pathlib import Path

import pandas as pd


REPORT_PATH = Path(__file__).resolve().parents[3] / "artifacts" / "threshold_evaluation.csv"


def get_model_performance_metrics():
    if not REPORT_PATH.exists():
        return {
            "threshold": 0.9,
            "precision": 0.0,
            "recall": 0.0,
            "f1_score": 0.0,
        }

    df = pd.read_csv(REPORT_PATH)
    row = df.loc[df["threshold"].astype(float).idxmax()]

    return {
        "threshold": float(row["threshold"]),
        "precision": float(row["precision"]),
        "recall": float(row["recall"]),
        "f1_score": float(row["f1_score"]),
    }
