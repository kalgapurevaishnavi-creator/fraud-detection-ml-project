from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database.crud import (
    create_alert_for_prediction,
    create_prediction,
    delete_all_predictions,
    delete_prediction,
    delete_predictions_by_ids,
    get_unread_alert_count,
)
from backend.app.database.database import Base
from backend.app.database.models import Alert, Prediction


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()


def test_alert_model_persists_and_tracks_status(db_session):
    prediction = Prediction(
        step=1,
        transaction_type="TRANSFER",
        amount=1000.0,
        oldbalanceOrg=5000.0,
        newbalanceOrig=4000.0,
        oldbalanceDest=2000.0,
        newbalanceDest=3000.0,
        prediction="Fraud",
        fraud_probability=0.96,
        threshold=0.9,
        created_at=datetime.utcnow(),
    )
    db_session.add(prediction)
    db_session.commit()
    db_session.refresh(prediction)

    alert = Alert(
        prediction_id=prediction.id,
        transaction_id=prediction.id,
        transaction_type="TRANSFER",
        amount=1000.0,
        fraud_probability=0.96,
        severity="High",
        status="Unread",
        message="⚠️ Fraud Alert: This transaction has been classified as potentially fraudulent. Please verify it immediately.",
        created_at=datetime.utcnow(),
    )
    db_session.add(alert)
    db_session.commit()
    db_session.refresh(alert)

    assert alert.id is not None
    assert alert.status == "Unread"
    assert alert.severity == "High"
    assert alert.transaction_id == prediction.id


def test_alert_is_marked_read_when_updated(db_session):
    prediction = Prediction(
        step=2,
        transaction_type="CASH_OUT",
        amount=5000.0,
        oldbalanceOrg=7000.0,
        newbalanceOrig=2000.0,
        oldbalanceDest=1000.0,
        newbalanceDest=8000.0,
        prediction="Fraud",
        fraud_probability=0.93,
        threshold=0.9,
        created_at=datetime.utcnow(),
    )
    db_session.add(prediction)
    db_session.commit()
    db_session.refresh(prediction)

    alert = Alert(
        prediction_id=prediction.id,
        transaction_id=prediction.id,
        transaction_type="CASH_OUT",
        amount=5000.0,
        fraud_probability=0.93,
        severity="Critical",
        status="Unread",
        message="⚠️ Fraud Alert: This transaction has been classified as potentially fraudulent. Please verify it immediately.",
        created_at=datetime.utcnow(),
    )
    db_session.add(alert)
    db_session.commit()

    alert.status = "Read"
    db_session.commit()

    assert alert.status == "Read"


def test_delete_prediction_keeps_alert_record(db_session):
    prediction = create_prediction(
        db_session,
        step=5,
        transaction_type="TRANSFER",
        amount=2500.0,
        oldbalanceOrg=7000.0,
        newbalanceOrig=4500.0,
        oldbalanceDest=1000.0,
        newbalanceDest=2500.0,
        prediction="Fraud",
        fraud_probability=0.97,
        threshold=0.9,
    )
    alert = create_alert_for_prediction(
        db_session,
        prediction,
        {"prediction": "Fraud", "fraud_probability": 0.97, "threshold": 0.9},
    )

    deleted = delete_prediction(db_session, prediction.id)

    assert deleted is True
    assert db_session.query(Prediction).count() == 0
    assert db_session.query(Alert).count() == 1
    db_session.refresh(alert)
    assert alert.prediction_id is None
    assert alert.transaction_id == prediction.id


def test_delete_all_predictions_keeps_alert_history(db_session):
    first = create_prediction(
        db_session,
        step=1,
        transaction_type="TRANSFER",
        amount=1000.0,
        oldbalanceOrg=5000.0,
        newbalanceOrig=4000.0,
        oldbalanceDest=2000.0,
        newbalanceDest=3000.0,
        prediction="Fraud",
        fraud_probability=0.95,
        threshold=0.9,
    )
    second = create_prediction(
        db_session,
        step=2,
        transaction_type="CASH_OUT",
        amount=2000.0,
        oldbalanceOrg=6000.0,
        newbalanceOrig=4000.0,
        oldbalanceDest=2500.0,
        newbalanceDest=5000.0,
        prediction="Legitimate",
        fraud_probability=0.35,
        threshold=0.9,
    )
    create_alert_for_prediction(
        db_session,
        first,
        {"prediction": "Fraud", "fraud_probability": 0.95, "threshold": 0.9},
    )
    create_alert_for_prediction(
        db_session,
        second,
        {"prediction": "Legitimate", "fraud_probability": 0.35, "threshold": 0.9},
    )

    deleted_count = delete_all_predictions(db_session)

    assert deleted_count == 2
    assert db_session.query(Prediction).count() == 0
    assert db_session.query(Alert).count() == 1
    assert db_session.query(Alert).filter(Alert.status == "Unread").count() == 1


def test_delete_selected_predictions_keeps_other_history_and_alerts(db_session):
    first = create_prediction(
        db_session,
        step=1,
        transaction_type="TRANSFER",
        amount=1000.0,
        oldbalanceOrg=5000.0,
        newbalanceOrig=4000.0,
        oldbalanceDest=2000.0,
        newbalanceDest=3000.0,
        prediction="Fraud",
        fraud_probability=0.96,
        threshold=0.9,
    )
    second = create_prediction(
        db_session,
        step=2,
        transaction_type="CASH_OUT",
        amount=2500.0,
        oldbalanceOrg=7000.0,
        newbalanceOrig=4500.0,
        oldbalanceDest=1000.0,
        newbalanceDest=3500.0,
        prediction="Fraud",
        fraud_probability=0.92,
        threshold=0.9,
    )
    first_alert = create_alert_for_prediction(
        db_session,
        first,
        {"prediction": "Fraud", "fraud_probability": 0.96, "threshold": 0.9},
    )
    second_alert = create_alert_for_prediction(
        db_session,
        second,
        {"prediction": "Fraud", "fraud_probability": 0.92, "threshold": 0.9},
    )
    first_alert.status = "Unread"
    second_alert.status = "Read"
    db_session.commit()

    deleted_count = delete_predictions_by_ids(db_session, [first.id])

    assert deleted_count == 1
    assert db_session.query(Prediction).count() == 1
    assert db_session.query(Prediction).filter(Prediction.id == first.id).count() == 0
    assert db_session.query(Prediction).filter(Prediction.id == second.id).count() == 1
    assert db_session.query(Alert).count() == 2
    db_session.refresh(first_alert)
    db_session.refresh(second_alert)
    assert first_alert.prediction_id is None
    assert second_alert.prediction_id == second.id
    assert get_unread_alert_count(db_session) == 1
