from datetime import datetime

from sqlalchemy.orm import Session

from backend.app.database.models import Alert, Prediction


def _build_transaction_signature(
    step: int,
    transaction_type: str,
    amount: float,
    oldbalanceOrg: float,
    newbalanceOrig: float,
    oldbalanceDest: float,
    newbalanceDest: float,
):
    return (
        f"{step}|{transaction_type}|{amount}|{oldbalanceOrg}|"
        f"{newbalanceOrig}|{oldbalanceDest}|{newbalanceDest}"
    )


def create_prediction(
    db: Session,
    step: int,
    transaction_type: str,
    amount: float,
    oldbalanceOrg: float,
    newbalanceOrig: float,
    oldbalanceDest: float,
    newbalanceDest: float,
    prediction: str,
    fraud_probability: float,
    threshold: float,
):
    db_prediction = Prediction(
        step=step,
        transaction_type=transaction_type,
        amount=amount,
        oldbalanceOrg=oldbalanceOrg,
        newbalanceOrig=newbalanceOrig,
        oldbalanceDest=oldbalanceDest,
        newbalanceDest=newbalanceDest,
        prediction=prediction,
        fraud_probability=fraud_probability,
        threshold=threshold,
    )

    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)

    return db_prediction


def _calculate_severity(probability: float) -> str:
    if probability >= 0.95:
        return "Critical"
    if probability >= 0.9:
        return "High"
    return "Medium"


def create_alert_for_prediction(db: Session, prediction: Prediction, result: dict):
    if prediction.prediction != "Fraud":
        return None

    signature = _build_transaction_signature(
        prediction.step,
        prediction.transaction_type,
        prediction.amount,
        prediction.oldbalanceOrg,
        prediction.newbalanceOrig,
        prediction.oldbalanceDest,
        prediction.newbalanceDest,
    )

    existing_alert = (
        db.query(Alert)
        .filter(Alert.transaction_signature == signature)
        .first()
    )
    if existing_alert is not None:
        return existing_alert

    alert = Alert(
        prediction_id=prediction.id,
        transaction_id=prediction.id,
        transaction_signature=signature,
        transaction_type=prediction.transaction_type,
        amount=prediction.amount,
        fraud_probability=prediction.fraud_probability,
        severity=_calculate_severity(prediction.fraud_probability),
        status="Unread",
        message=(
            "⚠️ Fraud Alert: This transaction has been classified as "
            "potentially fraudulent. Please verify it immediately."
        ),
        created_at=datetime.utcnow(),
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def get_alerts(db: Session):
    return db.query(Alert).order_by(Alert.created_at.desc()).all()


def get_unread_alert_count(db: Session):
    return db.query(Alert).filter(Alert.status == "Unread").count()


def mark_alert_read(db: Session, alert_id: int):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if alert is None:
        return None

    alert.status = "Read"
    alert.read_at = datetime.utcnow()
    db.commit()
    db.refresh(alert)
    return alert


def delete_predictions_by_ids(db: Session, prediction_ids: list[int]):
    normalized_ids = []
    for prediction_id in prediction_ids:
        if prediction_id is None:
            continue
        try:
            normalized_ids.append(int(prediction_id))
        except (TypeError, ValueError):
            continue

    normalized_ids = sorted(set(normalized_ids))
    if not normalized_ids:
        return 0

    predictions = (
        db.query(Prediction)
        .filter(Prediction.id.in_(normalized_ids))
        .all()
    )
    if not predictions:
        return 0

    prediction_id_set = {prediction.id for prediction in predictions}
    db.query(Alert).filter(Alert.prediction_id.in_(list(prediction_id_set))).update(
        {Alert.prediction_id: None},
        synchronize_session=False,
    )

    for prediction in predictions:
        db.delete(prediction)

    db.commit()
    return len(predictions)


def delete_prediction(db: Session, prediction_id: int):
    prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    if prediction is None:
        return None

    db.query(Alert).filter(Alert.prediction_id == prediction_id).update(
        {Alert.prediction_id: None},
        synchronize_session=False,
    )
    db.delete(prediction)
    db.commit()
    return True


def delete_all_predictions(db: Session):
    predictions = db.query(Prediction).all()
    if not predictions:
        return 0

    db.query(Alert).filter(Alert.prediction_id.isnot(None)).update(
        {Alert.prediction_id: None},
        synchronize_session=False,
    )

    for prediction in predictions:
        db.delete(prediction)

    db.commit()
    return len(predictions)


def delete_alert(db: Session, alert_id: int):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if alert is None:
        return None

    db.delete(alert)
    db.commit()
    return True