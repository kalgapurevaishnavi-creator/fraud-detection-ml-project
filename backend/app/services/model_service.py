
import joblib
from pathlib import Path


# --------------------------------------------------
# Project Root
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]


# --------------------------------------------------
# Model and Scaler Paths
# --------------------------------------------------

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "tuned_random_forest.pkl"
)

SCALER_PATH = (
    PROJECT_ROOT
    / "artifacts"
    / "fraud_scaler.pkl"
)


# --------------------------------------------------
# Load Trained Model
# --------------------------------------------------

def load_model():

    print("\n--- Loading Fraud Detection Model ---")
    print("Model path:", MODEL_PATH)

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model file not found: {MODEL_PATH}"
        )

    model = joblib.load(MODEL_PATH)

    print("Loaded model type:", type(model).__name__)
    print("Model loaded successfully!")

    if hasattr(model, "feature_names_in_"):
        print(
            "Expected feature count:",
            len(model.feature_names_in_)
        )
        print(
            "Expected features:",
            list(model.feature_names_in_)
        )

    print("------------------------------------\n")

    return model


# --------------------------------------------------
# Load Fitted Scaler
# --------------------------------------------------

def load_scaler():

    print("\n--- Loading Fraud Detection Scaler ---")
    print("Scaler path:", SCALER_PATH)

    if not SCALER_PATH.exists():
        raise FileNotFoundError(
            f"Scaler file not found: {SCALER_PATH}"
        )

    scaler = joblib.load(SCALER_PATH)

    print("Scaler loaded successfully!")
    print("--------------------------------------\n")

    return scaler
