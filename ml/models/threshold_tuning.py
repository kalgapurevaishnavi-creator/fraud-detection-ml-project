import pandas as pd
import joblib
from sklearn.metrics import precision_score, recall_score, f1_score

VAL_PATH = r"data/processed/validation_processed.csv"
MODEL_PATH = r"models/tuned_random_forest.pkl"


def tune_threshold():

    print("Loading validation data...")
    val_data = pd.read_csv(VAL_PATH)

    X_val = val_data.drop(columns=["isFraud"])
    y_val = val_data["isFraud"]

    print("Loading tuned Random Forest model...")
    model = joblib.load(MODEL_PATH)

    y_prob = model.predict_proba(X_val)[:, 1]

    thresholds = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

    print("\n--- Threshold Comparison ---")

    for threshold in thresholds:

        y_pred = (y_prob >= threshold).astype(int)

        precision = precision_score(
            y_val,
            y_pred,
            zero_division=0
        )

        recall = recall_score(
            y_val,
            y_pred,
            zero_division=0
        )

        f1 = f1_score(
            y_val,
            y_pred,
            zero_division=0
        )

        print(
            f"Threshold: {threshold:.1f} | "
            f"Precision: {precision:.4f} | "
            f"Recall: {recall:.4f} | "
            f"F1: {f1:.4f}"
        )


if __name__ == "__main__":
    tune_threshold()