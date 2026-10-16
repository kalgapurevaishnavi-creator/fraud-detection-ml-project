
import pandas as pd
import joblib

from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE


# --------------------------------------------------
# Paths
# --------------------------------------------------

DATA_PATH = Path("ml/data/engineered_fraud_data.csv")

TRAIN_PATH = Path("data/processed/train_processed.csv")
VAL_PATH = Path("data/processed/validation_processed.csv")
TEST_PATH = Path("data/processed/test_processed.csv")

SCALER_PATH = Path("artifacts/fraud_scaler.pkl")


def split_data():

    print("Loading engineered dataset...")

    # --------------------------------------------------
    # Load Dataset
    # --------------------------------------------------

    df = pd.read_csv(DATA_PATH)

    # Separate features and target
    X = df.drop(columns=["isFraud"])
    y = df["isFraud"]

    # --------------------------------------------------
    # Train / Validation / Test Split
    # --------------------------------------------------

    # Training: 70%, Temporary: 30%
    X_train, X_temp, y_train, y_temp = train_test_split(
        X,
        y,
        test_size=0.30,
        random_state=42,
        stratify=y
    )

    # Validation: 15%, Test: 15%
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp,
        y_temp,
        test_size=0.50,
        random_state=42,
        stratify=y_temp
    )

    print("\n--- Dataset Split ---")
    print("Training:", X_train.shape)
    print("Validation:", X_val.shape)
    print("Testing:", X_test.shape)

    print("\n--- Target Distribution ---")

    print("\nTraining:")
    print(y_train.value_counts())

    print("\nValidation:")
    print(y_val.value_counts())

    print("\nTesting:")
    print(y_test.value_counts())

    # --------------------------------------------------
    # Standard Scaling
    # --------------------------------------------------

    print("\nApplying StandardScaler...")

    scaler = StandardScaler()

    # Fit scaler ONLY on training data
    X_train_scaled = scaler.fit_transform(X_train)

    # Transform validation and test data
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)

    print("Training scaled:", X_train_scaled.shape)
    print("Validation scaled:", X_val_scaled.shape)
    print("Testing scaled:", X_test_scaled.shape)

    # Save fitted scaler for backend predictions
    SCALER_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    joblib.dump(scaler, SCALER_PATH)

    print("\nScaler saved successfully:")
    print(SCALER_PATH)

    # --------------------------------------------------
    # SMOTE - Handle Class Imbalance
    # --------------------------------------------------

    print("\nApplying SMOTE to training data only...")

    smote = SMOTE(random_state=42)

    X_train_smote, y_train_smote = smote.fit_resample(
        X_train_scaled,
        y_train
    )

    print("\n--- SMOTE Completed ---")

    print("\nBefore SMOTE:")
    print(y_train.value_counts())

    print("\nAfter SMOTE:")
    print(y_train_smote.value_counts())

    print("\nTraining shape after SMOTE:")
    print(X_train_smote.shape)

    # --------------------------------------------------
    # Create Processed DataFrames
    # --------------------------------------------------

    train_data = pd.DataFrame(
        X_train_smote,
        columns=X_train.columns
    )

    train_data["isFraud"] = y_train_smote.to_numpy()

    val_data = pd.DataFrame(
        X_val_scaled,
        columns=X_val.columns
    )

    val_data["isFraud"] = y_val.to_numpy()

    test_data = pd.DataFrame(
        X_test_scaled,
        columns=X_test.columns
    )

    test_data["isFraud"] = y_test.to_numpy()

    # --------------------------------------------------
    # Save Processed Datasets
    # --------------------------------------------------

    TRAIN_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    TRAIN_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    train_data.to_csv(
        TRAIN_PATH,
        index=False
    )

    val_data.to_csv(
        VAL_PATH,
        index=False
    )

    test_data.to_csv(
        TEST_PATH,
        index=False
    )

    print("\n--- Processed Data Saved ---")
    print("Training:", TRAIN_PATH)
    print("Validation:", VAL_PATH)
    print("Testing:", TEST_PATH)
    print("Scaler:", SCALER_PATH)

    print("\nData preprocessing completed successfully!")


if __name__ == "__main__":
    split_data()
