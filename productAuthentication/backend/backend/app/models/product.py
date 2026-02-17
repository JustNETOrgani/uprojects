from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class ProductCategory(str, enum.Enum):
    PHARMACEUTICALS = "pharmaceuticals"
    ELECTRONICS = "electronics"
    LUXURY_GOODS = "luxury_goods"
    CLOTHING = "clothing"
    FOOD = "food"
    OTHER = "other"


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    blockchain_id = Column(
        Integer, index=True
    )  # this id  will come from the  smart contract
    product_name = Column(String, nullable=False)
    product_description = Column(Text)
    manufacturing_date = Column(DateTime, nullable=False)
    batch_number = Column(String, nullable=False)
    category = Column(String, nullable=False)
    qr_code_hash = Column(String, unique=True, index=True, nullable=False)
    qr_code_path = Column(String,nullable=True)  # Path to stored QR code image
    ipfs_hash = Column(String, unique=True, index=True, nullable=True)  # IPFS hash for product data
    ipfs_url = Column(String, nullable=True)  # Public IPFS URL
    # Legacy Swarm fields (for backward compatibility)
    swarm_hash = Column(String, unique=True, index=True, nullable=True)  # Swarm hash for product data
    swarm_url = Column(String, nullable=True)  # Public Swarm URL
    manufacturer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    manufacturer = relationship("User", back_populates="products")
    verifications = relationship("Verification", back_populates="product")
    qrcode = relationship(
        "QrCode", back_populates="product", uselist=False, lazy="select"
    )

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.product_name}', blockchain_id={self.blockchain_id})>"
