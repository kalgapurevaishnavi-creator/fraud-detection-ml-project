
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.app.database.crud import (
    create_alert_for_prediction,
    create_prediction,
    delete_alert,
    delete_all_predictions,
    delete_prediction,
    delete_predictions_by_ids,
    get_alerts,
    get_unread_alert_count,
    mark_alert_read,
)
from backend.app.database.database import Base, SessionLocal, engine
from backend.app.database.models import Prediction
from backend.app.schemas.transaction import SelectedTransactionsRequest, TransactionRequest
from backend.app.services.analytics_service import get_prediction_summary
from backend.app.services.monitoring_service import get_monitoring_summary
from backend.app.services.prediction_service import predict_fraud
from backend.app.services.report_service import get_model_performance_metrics
from backend.app.services.transaction_service import preprocess_transaction

def ensure_database_compatibility():
    with engine.begin() as connection:
        alert_table = connection.execute(
            text(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name='alerts'"
            )
        ).fetchone()
        if alert_table is None:
            return

        columns = connection.execute(text("PRAGMA table_info(alerts)")).fetchall()
        prediction_id_column = next(
            (column for column in columns if column[1] == "prediction_id"),
            None,
        )
        if prediction_id_column is not None and prediction_id_column[3] == 1:
            connection.execute(text("ALTER TABLE alerts RENAME TO alerts_old"))
            connection.execute(
                text(
                    """
                    CREATE TABLE alerts (
                        id INTEGER PRIMARY KEY,
                        prediction_id INTEGER,
                        transaction_id INTEGER NOT NULL,
                        transaction_signature VARCHAR,
                        transaction_type VARCHAR NOT NULL,
                        amount FLOAT NOT NULL,
                        fraud_probability FLOAT NOT NULL,
                        severity VARCHAR NOT NULL,
                        status VARCHAR NOT NULL DEFAULT 'Unread',
                        message VARCHAR NOT NULL,
                        created_at DATETIME,
                        read_at DATETIME
                    )
                    """
                )
            )
            connection.execute(
                text(
                    """
                    INSERT INTO alerts (
                        id, prediction_id, transaction_id, transaction_signature,
                        transaction_type, amount, fraud_probability, severity,
                        status, message, created_at, read_at
                    )
                    SELECT
                        id, prediction_id, transaction_id, transaction_signature,
                        transaction_type, amount, fraud_probability, severity,
                        status, message, created_at, read_at
                    FROM alerts_old
                    """
                )
            )
            connection.execute(text("DROP TABLE alerts_old"))
            connection.execute(
                text(
                    "CREATE UNIQUE INDEX IF NOT EXISTS ix_alerts_transaction_signature ON alerts (transaction_signature)"
                )
            )
            connection.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS ix_alerts_prediction_id ON alerts (prediction_id)"
                )
            )


# Create database tables
Base.metadata.create_all(bind=engine)
ensure_database_compatibility()


# Initialize FastAPI
app = FastAPI(
    title="Fraud Detection API",
    description="API for detecting fraudulent transactions",
    version="1.0.0",
)


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Database session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Home endpoint
@app.get("/")
def home():
    return {"message": "Fraud Detection API is running"}


def serialize_alert(alert):
    return {
        "id": alert.id,
        "prediction_id": alert.prediction_id,
        "transaction_id": alert.transaction_id,
        "transaction_type": alert.transaction_type,
        "amount": alert.amount,
        "fraud_probability": alert.fraud_probability,
        "severity": alert.severity,
        "status": alert.status,
        "message": alert.message,
        "created_at": alert.created_at.isoformat() if alert.created_at else None,
        "read_at": alert.read_at.isoformat() if alert.read_at else None,
    }


# Fraud prediction endpoint
@app.post("/predict")
def predict(transaction: TransactionRequest, db: Session = Depends(get_db)):
    transaction_data = preprocess_transaction(transaction)
    result = predict_fraud(transaction_data)

    db_prediction = create_prediction(
        db=db,
        step=transaction.step,
        transaction_type=transaction.type,
        amount=transaction.amount,
        oldbalanceOrg=transaction.oldbalanceOrg,
        newbalanceOrig=transaction.newbalanceOrig,
        oldbalanceDest=transaction.oldbalanceDest,
        newbalanceDest=transaction.newbalanceDest,
        prediction=result["prediction"],
        fraud_probability=result["fraud_probability"],
        threshold=result["threshold"],
    )

    alert = None
    if result["prediction"] == "Fraud":
        alert = create_alert_for_prediction(db, db_prediction, result)

    response = dict(result)
    response["alert_created"] = alert is not None
    return response


# Analytics endpoint
@app.get("/analysis")
def analysis(db: Session = Depends(get_db)):
    return get_prediction_summary(db)


# Monitoring endpoint
@app.get("/monitoring")
def monitoring(db: Session = Depends(get_db)):
    return get_monitoring_summary(db)


@app.get("/reports")
def reports(db: Session = Depends(get_db)):
    summary = get_monitoring_summary(db)
    model_metrics = get_model_performance_metrics()
    return {
        "summary": summary,
        "model_metrics": model_metrics,
    }


# Transactions history endpoint
@app.get("/transactions")
def get_transactions(db: Session = Depends(get_db)):
    transactions = db.query(Prediction).order_by(Prediction.id.desc()).all()

    return [
        {
            "id": item.id,
            "step": item.step,
            "type": item.transaction_type,
            "amount": item.amount,
            "prediction": item.prediction,
            "fraud_probability": item.fraud_probability,
            "threshold": item.threshold,
            "created_at": item.created_at.isoformat() if item.created_at else None,
        }
        for item in transactions
    ]


@app.delete("/transactions/selected")
def delete_selected_transactions(
    request: SelectedTransactionsRequest,
    db: Session = Depends(get_db),
):
    deleted_count = delete_predictions_by_ids(db, request.transaction_ids)
    return {
        "message": "Selected transactions deleted successfully",
        "deleted_count": deleted_count,
    }


@app.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    deleted = delete_prediction(db, transaction_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"message": "Transaction deleted successfully", "deleted_transaction_id": transaction_id}


@app.delete("/transactions")
def delete_all_transactions(db: Session = Depends(get_db)):
    deleted_count = delete_all_predictions(db)
    return {
        "message": "All transaction history deleted successfully",
        "deleted_count": deleted_count,
    }


# Alert endpoints
@app.get("/alerts")
def get_alerts_endpoint(db: Session = Depends(get_db)):
    alerts = get_alerts(db)
    return [serialize_alert(alert) for alert in alerts]


@app.get("/alerts/unread-count")
def get_unread_alerts_count_endpoint(db: Session = Depends(get_db)):
    return {"unread_alerts": get_unread_alert_count(db)}


@app.patch("/alerts/{alert_id}/read")
def read_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = mark_alert_read(db, alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    return serialize_alert(alert)


@app.delete("/alerts/{alert_id}")
def remove_alert(alert_id: int, db: Session = Depends(get_db)):
    deleted = delete_alert(db, alert_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"message": "Alert deleted successfully"}
