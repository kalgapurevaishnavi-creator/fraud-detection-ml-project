from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from backend.app.database.database import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    step = Column(Integer)
    transaction_type = Column(String)
    amount = Column(Float)
    oldbalanceOrg = Column(Float)
    newbalanceOrig = Column(Float)
    oldbalanceDest = Column(Float)
    newbalanceDest = Column(Float)
    prediction = Column(String)
    fraud_probability = Column(Float)
    threshold = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    alerts = relationship("Alert", back_populates="prediction")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=True)
    transaction_id = Column(Integer, nullable=False)
    transaction_signature = Column(String, unique=True, index=True, nullable=True)
    transaction_type = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    fraud_probability = Column(Float, nullable=False)
    severity = Column(String, nullable=False)
    status = Column(String, default="Unread", nullable=False)
    message = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime, nullable=True)

    prediction = relationship("Prediction", back_populates="alerts")