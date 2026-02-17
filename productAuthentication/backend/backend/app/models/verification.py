from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Verification(Base):
    __tablename__ = "verifications"

    id = Column(Integer, primary_key=True, index=True)
    blockchain_verification_id = Column(
        Integer, unique=True, index=True
    )  # ID from smart contract
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    verifier_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    location = Column(String, nullable=False)
    is_authentic = Column(Boolean, default=True)
    notes = Column(Text)
    verification_date = Column(DateTime(timezone=True), server_default=func.now())
    detection_reasons = Column(JSON, nullable=True)  # Store detection reasons as JSON
    confidence_score = Column(Float, nullable=True)  # Store confidence score
    risk_level = Column(String, nullable=True)  # Store risk level (low, medium, high)
    blockchain_verified = Column(Boolean, nullable=True)  # Store blockchain verification status

    # Relationships
    product = relationship("Product", back_populates="verifications")
    verifier = relationship("User", back_populates="verifications")

    def __repr__(self):
        return f"<Verification(id={self.id}, product_id={self.product_id}, authentic={self.is_authentic})>"
