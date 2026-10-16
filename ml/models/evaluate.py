import pandas as pd
import joblib
from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    roc_auc_score
)

TEST_PATH = r"data/processed/test_processed.csv"
MODEL_PATH = r"models/tuned_random_forest.pkl"

THRESHOLD = 0.9


def evaluate_model():

    print("Loading test data...")
    test_data = pd.read_csv(TEST_PATH)

    X_test = test_data.drop(columns=["isFraud"])
    y_test = test_data["isFraud"]

    print("Loading tuned Random Forest model...")
    model = joblib.load(MODEL_PATH)

    y_prob = model.predict_proba(X_test)[:, 1]

    y_pred = (y_prob >= THRESHOLD).astype(int)

    print("\n--- Final Model Evaluation ---")
    print("Threshold:", THRESHOLD)

    print("\n--- Confusion Matrix ---")
    print(confusion_matrix(y_test, y_pred))

    print("\n--- Classification Report ---")
    print(classification_report(y_test, y_pred, zero_division=0))

    print("\n--- ROC-AUC Score ---")
    print(roc_auc_score(y_test, y_prob))

    print("\nEvaluation completed successfully.")


if __name__ == "__main__":
    evaluate_model()