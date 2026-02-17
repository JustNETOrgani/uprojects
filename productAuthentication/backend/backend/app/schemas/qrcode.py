from pydantic import BaseModel


class ProductBase(BaseModel):
    id: int
    product_name: str
    batch_number: str


class QRCodeInDB(BaseModel):
    id: int
    qr_code_hash: str
    qr_image_path: str
    created_at: str
    updated_at: str
    product: ProductBase


class QrCreate(BaseModel):
    product_id: int
    qr_code_hash: str
    qr_image_path: str
