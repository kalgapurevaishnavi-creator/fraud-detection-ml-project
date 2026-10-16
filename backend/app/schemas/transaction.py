from pydantic import BaseModel, Field


class TransactionRequest(BaseModel):
    step: int = Field(..., ge=1)
    type: str = Field(
        ...,
        pattern="^(PAYMENT|TRANSFER|CASH_OUT|DEBIT|CASH_IN)$"
    )
    amount: float = Field(..., ge=0)
    oldbalanceOrg: float = Field(..., ge=0)
    newbalanceOrig: float = Field(..., ge=0)
    oldbalanceDest: float = Field(..., ge=0)
    newbalanceDest: float = Field(..., ge=0)


class SelectedTransactionsRequest(BaseModel):
    transaction_ids: list[int] = Field(..., min_length=1)