from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.product import Product
from app.models.qrcode import QrCode
from app.schemas.qrcode import QrCreate, QRCodeInDB
from pydantic import BaseModel
import logging

from backend.app.services.qr_service import QRService


router = APIRouter()
qr_service = QRService()
logger = logging.getLogger(__name__)


@router.post("/create-qr-code", response_model=QRCodeInDB)
async def create_qr_code(
    qr_data: QrCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    product: Product = Depends(get_db),
) -> Any:
    try:
        product = db.query(Product).filter(Product.id == qr_data.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )

        qr_code = qr_service.create_qr_code(qr_data, product)
        db.add(qr_code)
        db.commit()
        db.refresh(qr_code)

        return qr_code

    except Exception as e:
        logger.warning(str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating QR code",
        )
