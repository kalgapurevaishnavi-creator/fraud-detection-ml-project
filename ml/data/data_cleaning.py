import pandas as pd

# Paths
RAW_DATA_PATH = r"data/raw/PS_20174392719_1491204439457_log.csv"
CLEAN_DATA_PATH = r"data/processed/cleaned_fraud_data.csv"


def clean_data():
    print("Loading raw dataset...")

    df = pd.read_csv(RAW_DATA_PATH)

    print("\n--- Original Shape ---")
    print(df.shape)

    # Remove duplicate rows
    df = df.drop_duplicates()

    # Handle missing values
    print("\n--- Missing Values Before Cleaning ---")
    print(df.isnull().sum().sum())

    # Remove rows with missing values
    df = df.dropna()

    print("\n--- Missing Values After Cleaning ---")
    print(df.isnull().sum().sum())

    print("\n--- Shape After Cleaning ---")
    print(df.shape)

    # Save cleaned dataset
    df.to_csv(CLEAN_DATA_PATH, index=False)

    print("\nCleaned dataset saved successfully.")
    print(CLEAN_DATA_PATH)


if __name__ == "__main__":
    clean_data()