import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score
)
import joblib

TRAIN_PATH = r"data/processed/train_processed.csv"
VAL_PATH = r"data/processed/validation_processed.csv"

LOGISTIC_MODEL_PATH = r"models/baseline_logistic_regression.pkl"
RF_MODEL_PATH = r"models/random_forest_model.pkl"


def train_model():

    print("Loading processed datasets...")

    train_data = pd.read_csv(TRAIN_PATH)
    val_data = pd.read_csv(VAL_PATH)

    X_train = train_data.drop(columns=["isFraud"])
    y_train = train_data["isFraud"]

    X_val = val_data.drop(columns=["isFraud"])
    y_val = val_data["isFraud"]

    print("\n--- Dataset Shapes ---")
    print("Training:", X_train.shape)
    print("Validation:", X_val.shape)

    # Logistic Regression
    print("\nTraining Logistic Regression...")

    model = LogisticRegression(
        max_iter=1000,
        random_state=42
    )

    model.fit(X_train, y_train)

    print("Logistic Regression training completed.")

    y_pred = model.predict(X_val)
    y_prob = model.predict_proba(X_val)[:, 1]

    print("\n--- Logistic Regression Confusion Matrix ---")
    print(confusion_matrix(y_val, y_pred))

    print("\n--- Logistic Regression Classification Report ---")
    print(classification_report(y_val, y_pred))

    print("\n--- Logistic Regression ROC-AUC Score ---")
    print(roc_auc_score(y_val, y_prob))

    joblib.dump(model, LOGISTIC_MODEL_PATH)

    print("\n--- Logistic Regression Model Saved ---")
    print(LOGISTIC_MODEL_PATH)

    # Random Forest
    print("\nTraining Random Forest...")

    rf_model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        n_jobs=-1
    )

    rf_model.fit(X_train, y_train)

    print("Random Forest training completed.")

    rf_pred = rf_model.predict(X_val)
    rf_prob = rf_model.predict_proba(X_val)[:, 1]

    print("\n--- Random Forest Confusion Matrix ---")
    print(confusion_matrix(y_val, rf_pred))

    print("\n--- Random Forest Classification Report ---")
    print(classification_report(y_val, rf_pred))

    print("\n--- Random Forest ROC-AUC ---")
    print(roc_auc_score(y_val, rf_prob))

    joblib.dump(rf_model, RF_MODEL_PATH)

    print("\n--- Random Forest Model Saved ---")
    print(RF_MODEL_PATH)


if __name__ == "__main__":
    train_model()