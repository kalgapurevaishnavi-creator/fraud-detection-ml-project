from sqlalchemy.orm import Session

from backend.app.database.models import Prediction


def get_monitoring_summary(db: Session):

    total_predictions = db.query(Prediction).count()

    fraud_predictions = (
        db.query(Prediction)
        .filter(Prediction.prediction == "Fraud")
        .count()
    )

    legitimate_predictions = (
        db.query(Prediction)
        .filter(Prediction.prediction == "Legitimate")
        .count()
    )

    if total_predictions > 0:
        fraud_rate = fraud_predictions / total_predictions
    else:
        fraud_rate = 0

    return {
        "total_predictions": total_predictions,
        "fraud_predictions": fraud_predictions,
        "legitimate_predictions": legitimate_predictions,
        "fraud_rate": fraud_rate
    }