from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.product import ProductCategory
from app.models.qrcode import QrCode


class ProductBase(BaseModel):
    product_name: str
    product_description: Optional[str] = None
    manufacturing_date: datetime
    batch_number: str
    category: ProductCategory


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    product_name: Optional[str] = None
    product_description: Optional[str] = None
    manufacturing_date: Optional[datetime] = None
    batch_number: Optional[str] = None
    category: Optional[ProductCategory] = None
    is_active: Optional[bool] = None


class QrCodeSchema(BaseModel):
    qr_image_path: Optional[str] = None
    qr_code_hash: Optional[str] = None

    @classmethod
    def from_orm(cls, qr_code: QrCode):
        return cls(
            qr_image_path=qr_code.qr_image_path,
            qr_code_hash=qr_code.qr_code_hash,
        )


class ProductInDBBase(ProductBase):
    id: int
    blockchain_id: Optional[int] = None
    qr_code_hash: str
    qr_code_path: Optional[str] = None
    ipfs_hash: Optional[str] = None
    ipfs_url: Optional[str] = None
    # Legacy Swarm fields (for backward compatibility)
    manufacturer_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Product(ProductInDBBase):
    pass


class ProductInDB(ProductInDBBase):
    pass


class ProductWithVerifications(Product):
    verifications: List["Verification"] = []
