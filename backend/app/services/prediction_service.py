
from backend.app.services.model_service import load_model

THRESHOLD = 0.9


def predict_fraud(transaction_data):
    model = load_model()

    # Predict fraud probability using scaled features
    fraud_probability = model.predict_proba(transaction_data)[0][1]

    print("\n--- Fraud Prediction Results ---")
    print("Input shape:", transaction_data.shape)
    print("Input columns:", list(transaction_data.columns))
    print("Fraud probability:", fraud_probability)
    print("Detection threshold:", THRESHOLD)

    if fraud_probability >= THRESHOLD:
        prediction = "Fraud"
    else:
        prediction = "Legitimate"

    print("Final prediction:", prediction)
    print("--------------------------------\n")

    return {
        "prediction": prediction,
        "fraud_probability": float(fraud_probability),
        "threshold": THRESHOLD,
    }
