from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
from app.core.database import Base
from sqlalchemy.orm import relationship


class QrCode(Base):
    __tablename__ = "qrcodes"

    id = Column(Integer, primary_key=True, index=True)
    qr_image_path = Column(String)
    qr_code_hash = Column(String)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    product = relationship("Product", back_populates="qrcode")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<QrCode(id={self.id}, product_id={self.product_id})>"
