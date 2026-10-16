import pandas as pd

# Paths
INPUT_PATH = r"data/processed/cleaned_fraud_data.csv"
OUTPUT_PATH = r"ml/data/engineered_fraud_data.csv"


def create_features():
    print("Loading cleaned dataset...")

    df = pd.read_csv(INPUT_PATH)

    # Transaction type encoding
    df = pd.get_dummies(
        df,
        columns=["type"],
        drop_first=True,
        dtype=int
    )

    # Balance difference features
    df["balance_change_orig"] = (
        df["oldbalanceOrg"] - df["newbalanceOrig"]
    )

    df["balance_change_dest"] = (
        df["newbalanceDest"] - df["oldbalanceDest"]
    )

    # Amount to origin balance ratio
    df["amount_to_oldbalance_orig"] = (
        df["amount"] / (df["oldbalanceOrg"] + 1)
    )

    # Remove identifier columns
    df = df.drop(
        columns=["nameOrig", "nameDest"],
        errors="ignore"
    )

    print("\n--- Engineered Dataset Shape ---")
    print(df.shape)

    print("\n--- Engineered Columns ---")
    print(df.columns.tolist())

    # Save engineered dataset
    df.to_csv(OUTPUT_PATH, index=False)

    print("\nFeature engineering completed successfully.")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    create_features()