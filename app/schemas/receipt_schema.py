from pydantic import BaseModel, Field


class ExtractedReceiptData(BaseModel):
    amount: str | None = None
    currency: str | None = None
    date: str | None = None
    time: str | None = None
    recipient: str | None = None
    sender: str | None = None
    transaction_id: str | None = None
    status: str | None = None
    bank: str | None = None


class ReceiptCheckResponse(BaseModel):
    is_fake: bool
    confidence: float = Field(ge=0, le=1)
    risk_score: int = Field(ge=0, le=100)
    reason: str
    ocr_text: str | None = None
    qr_payload: str | None = None
    extracted_data: ExtractedReceiptData
