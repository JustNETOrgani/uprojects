from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class VerificationBase(BaseModel):
    location: str
    notes: Optional[str] = None


class VerificationCreate(VerificationBase):
    product_id: int
    qr_code_hash: Optional[str] = None


class VerificationUpdate(BaseModel):
    location: Optional[str] = None
    notes: Optional[str] = None
    is_authentic: Optional[bool] = None


class VerificationInDBBase(VerificationBase):
    id: int
    blockchain_verification_id: Optional[int] = None
    product_id: int
    verifier_id: int
    is_authentic: bool
    verification_date: datetime
    detection_reasons: Optional[list] = None
    confidence_score: Optional[float] = None
    risk_level: Optional[str] = None
    blockchain_verified: Optional[bool] = None

    class Config:
        from_attributes = True


class Verification(VerificationInDBBase):
    pass


class VerificationInDB(VerificationInDBBase):
    pass
