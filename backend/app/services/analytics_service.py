from sqlalchemy.orm import Session

from backend.app.database.models import Prediction


def get_prediction_summary(db: Session):

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

    return {
        "total_predictions": total_predictions,
        "fraud_predictions": fraud_predictions,
        "legitimate_predictions": legitimate_predictions
    }