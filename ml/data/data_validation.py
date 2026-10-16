import pandas as pd

# Raw dataset path
DATA_PATH = r"data/raw/PS_20174392719_1491204439457_log.csv"


def validate_data():
    print("Loading dataset...")
    df = pd.read_csv(DATA_PATH)

    print("\n--- Dataset Shape ---")
    print(df.shape)

    print("\n--- Columns ---")
    print(df.columns.tolist())

    print("\n--- Data Types ---")
    print(df.dtypes)

    print("\n--- Missing Values ---")
    print(df.isnull().sum())

    print("\n--- Duplicate Rows ---")
    print(df.duplicated().sum())

    print("\n--- Target Distribution ---")
    print(df["isFraud"].value_counts())

    print("\n--- Target Percentage ---")
    print(df["isFraud"].value_counts(normalize=True) * 100)

    print("\nData validation completed successfully.")


if __name__ == "__main__":
    validate_data()