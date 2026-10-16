import mlflow
import mlflow.sklearn
import pandas as pd
import joblib
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)

TEST_PATH = r"data/processed/test_processed.csv"
MODEL_PATH = r"models/tuned_random_forest.pkl"

THRESHOLD = 0.9


def track_model():

    print("Loading test data...")
    test_data = pd.read_csv(TEST_PATH)

    X_test = test_data.drop(columns=["isFraud"])
    y_test = test_data["isFraud"]

    print("Loading tuned Random Forest model...")
    model = joblib.load(MODEL_PATH)

    y_prob = model.predict_proba(X_test)[:, 1]
    y_pred = (y_prob >= THRESHOLD).astype(int)

    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    roc_auc = roc_auc_score(y_test, y_prob)

    mlflow.set_experiment("Fraud_Detection")

    with mlflow.start_run():

        mlflow.log_param("model", "Tuned Random Forest")
        mlflow.log_param("threshold", THRESHOLD)

        mlflow.log_metric("precision", precision)
        mlflow.log_metric("recall", recall)
        mlflow.log_metric("f1_score", f1)
        mlflow.log_metric("roc_auc", roc_auc)

        mlflow.sklearn.log_model(
        model,
        name="tuned_random_forest",
        skops_trusted_types=["sklearn.tree._tree.Tree"]
)

        print("\n--- MLflow Tracking Completed ---")
        print("Precision:", precision)
        print("Recall:", recall)
        print("F1 Score:", f1)
        print("ROC-AUC:", roc_auc)


if __name__ == "__main__":
    track_model()