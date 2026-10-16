
import pandas as pd

from backend.app.services.model_service import load_scaler


def preprocess_transaction(transaction):

    data = {
        "step": transaction.step,
        "amount": transaction.amount,
        "oldbalanceOrg": transaction.oldbalanceOrg,
        "newbalanceOrig": transaction.newbalanceOrig,
        "oldbalanceDest": transaction.oldbalanceDest,
        "newbalanceDest": transaction.newbalanceDest,
        "isFlaggedFraud": 0,
    }

    df = pd.DataFrame([data])

    # Transaction type encoding
    for transaction_type in [
        "CASH_OUT",
        "DEBIT",
        "PAYMENT",
        "TRANSFER",
    ]:
        df[f"type_{transaction_type}"] = int(
            transaction.type == transaction_type
        )

    # Feature engineering
    df["balance_change_orig"] = (
        df["oldbalanceOrg"] - df["newbalanceOrig"]
    )

    df["balance_change_dest"] = (
        df["newbalanceDest"] - df["oldbalanceDest"]
    )

    df["amount_to_oldbalance_orig"] = (
        df["amount"] / (df["oldbalanceOrg"] + 1)
    )

    # Keep the same feature order as model training
    feature_order = [
        "step",
        "amount",
        "oldbalanceOrg",
        "newbalanceOrig",
        "oldbalanceDest",
        "newbalanceDest",
        "isFlaggedFraud",
        "type_CASH_OUT",
        "type_DEBIT",
        "type_PAYMENT",
        "type_TRANSFER",
        "balance_change_orig",
        "balance_change_dest",
        "amount_to_oldbalance_orig",
    ]

    df = df[feature_order]

    # Apply the saved training scaler
    scaler = load_scaler()

    scaled_values = scaler.transform(df)

    scaled_df = pd.DataFrame(
        scaled_values,
        columns=feature_order,
    )

    return scaled_df
