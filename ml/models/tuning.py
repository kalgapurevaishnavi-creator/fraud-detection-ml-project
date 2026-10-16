
import pandas as pd
import joblib

from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import (
    classification_report,
    roc_auc_score,
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score
)


# --------------------------------------------------
# Paths
# --------------------------------------------------

TRAIN_PATH = Path("data/processed/train_processed.csv")
VAL_PATH = Path("data/processed/validation_processed.csv")
MODEL_PATH = Path("models/tuned_random_forest.pkl")


def tune_model():

    # --------------------------------------------------
    # Load datasets
    # --------------------------------------------------

    print("\nLoading processed datasets...")

    train_data = pd.read_csv(TRAIN_PATH)
    val_data = pd.read_csv(VAL_PATH)

    X_train = train_data.drop(columns=["isFraud"])
    y_train = train_data["isFraud"]

    X_val = val_data.drop(columns=["isFraud"])
    y_val = val_data["isFraud"]

    print("\n--- Original Dataset Shapes ---")
    print("Training:", X_train.shape)
    print("Validation:", X_val.shape)

    # --------------------------------------------------
    # Sample training data for tuning
    # --------------------------------------------------

    SAMPLE_SIZE = 500000

    if len(X_train) > SAMPLE_SIZE:

        sample_data = train_data.sample(
            n=SAMPLE_SIZE,
            random_state=42
        )

        X_tune = sample_data.drop(columns=["isFraud"])
        y_tune = sample_data["isFraud"]

    else:

        X_tune = X_train
        y_tune = y_train

    print("\n--- Tuning Dataset ---")
    print("Training samples used:", X_tune.shape)

    print("\nTraining fraud class distribution:")
    print(y_tune.value_counts())

    # --------------------------------------------------
    # Random Forest model
    # --------------------------------------------------

    rf_model = RandomForestClassifier(
        random_state=42,
        n_jobs=-1
    )

    # --------------------------------------------------
    # Hyperparameter Search
    # --------------------------------------------------

    param_grid = {
        "n_estimators": [50, 100],
        "max_depth": [10, 20, None],
        "min_samples_split": [2, 5],
        "min_samples_leaf": [1, 2]
    }

    print("\nStarting Random Forest tuning...")

    random_search = RandomizedSearchCV(
        estimator=rf_model,
        param_distributions=param_grid,
        n_iter=4,
        scoring="roc_auc",
        cv=3,
        random_state=42,
        n_jobs=-1,
        verbose=2
    )

    random_search.fit(X_tune, y_tune)

    # --------------------------------------------------
    # Best parameters
    # --------------------------------------------------

    print("\n--- Best Parameters ---")
    print(random_search.best_params_)

    print("\n--- Best Cross-Validation ROC-AUC ---")
    print(random_search.best_score_)

    # --------------------------------------------------
    # Validate best model
    # --------------------------------------------------

    best_model = random_search.best_estimator_

    y_pred = best_model.predict(X_val)
    y_prob = best_model.predict_proba(X_val)[:, 1]

    print("\n--- Default Classification Report ---")
    print(classification_report(
        y_val,
        y_pred,
        zero_division=0
    ))

    print("\n--- Tuned Random Forest ROC-AUC ---")
    print(roc_auc_score(y_val, y_prob))

    # --------------------------------------------------
    # Evaluate different decision thresholds
    # --------------------------------------------------

    thresholds = [0.1, 0.2, 0.3, 0.5, 0.9]

    threshold_results = []

    print("\n" + "=" * 65)
    print("THRESHOLD EVALUATION")
    print("=" * 65)

    for threshold in thresholds:

        # Convert probabilities into class predictions
        threshold_pred = (y_prob >= threshold).astype(int)

        precision = precision_score(
            y_val,
            threshold_pred,
            zero_division=0
        )

        recall = recall_score(
            y_val,
            threshold_pred,
            zero_division=0
        )

        f1 = f1_score(
            y_val,
            threshold_pred,
            zero_division=0
        )

        cm = confusion_matrix(
            y_val,
            threshold_pred,
            labels=[0, 1]
        )

        tn, fp, fn, tp = cm.ravel()

        threshold_results.append({
            "threshold": threshold,
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "true_negatives": tn,
            "false_positives": fp,
            "false_negatives": fn,
            "true_positives": tp
        })

        print(f"\n--- Threshold: {threshold:.2f} ---")
        print(f"Precision: {precision:.4f}")
        print(f"Recall:    {recall:.4f}")
        print(f"F1-score:  {f1:.4f}")

        print("\nConfusion Matrix:")
        print(cm)

        print("\nClassification Report:")
        print(classification_report(
            y_val,
            threshold_pred,
            labels=[0, 1],
            target_names=["Legitimate", "Fraud"],
            zero_division=0
        ))

    # --------------------------------------------------
    # Save threshold results
    # --------------------------------------------------

    results_df = pd.DataFrame(threshold_results)

    results_path = Path("artifacts/threshold_evaluation.csv")
    results_path.parent.mkdir(parents=True, exist_ok=True)

    results_df.to_csv(results_path, index=False)

    print("\n--- Threshold Comparison ---")
    print(results_df.to_string(index=False))

    print("\nThreshold results saved to:")
    print(results_path)

    # --------------------------------------------------
    # Save tuned model
    # --------------------------------------------------

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(best_model, MODEL_PATH)

    print("\n--- Tuned Model Saved Successfully ---")
    print(MODEL_PATH.resolve())


if __name__ == "__main__":
    tune_model()
