from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User, UserRole
from app.models.product import Product
from app.schemas.product import Product as ProductSchema, ProductCreate, ProductUpdate
from app.services.qr_service import QRService
from app.services.blockchain_service import BlockchainService
from app.services.ipfs_service import IPFSService
from app.services.counterfeit_detection_service import CounterfeitDetectionService
from app.models.verification import Verification
from app.api.v1.endpoints.blockchain import get_blockchain_service

from pydantic import BaseModel
from app.models.qrcode import QrCode
from sqlalchemy.orm import selectinload, joinedload

router = APIRouter()
qr_service = QRService()

blockchain_service = BlockchainService()


async def get_blockchain_service():
    """Get initialized blockchain service"""
    # Create a new instance each time to ensure fresh configuration
    service = BlockchainService()
    await service.initialize()
    return service


class VerifyProductRequest(BaseModel):
    qr_data: str
    location: str = "Unknown"
    notes: str = ""


@router.post("/", response_model=ProductSchema)
async def create_product(
    product_in: ProductCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Creatin a new product (manufacturers only)."""
    if current_user.role != UserRole.MANUFACTURER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only manufacturers can create products",
        )

    # Creatingg product in database
    db_product = Product(
        product_name=product_in.product_name,
        product_description=product_in.product_description,
        manufacturing_date=product_in.manufacturing_date,
        batch_number=product_in.batch_number,
        category=product_in.category.value,
        qr_code_hash="",
        manufacturer_id=current_user.id,
    )

    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    # Generating QR code
    product_data = {
        "id": db_product.id,
        "product_name": db_product.product_name,
        "batch_number": db_product.batch_number,
        "manufacturing_date": str(db_product.manufacturing_date),
        "created_at": str(db_product.created_at),
    }

    try:
        qr_file_path, qr_hash, qr_data, secure_url = (
            await qr_service.create_product_qr_code(product_data)
        )
        db_product.qr_code_hash = qr_hash
        db_product.qr_code_path = secure_url
        db.commit()
        db.refresh(db_product)
        print(f" QR code generated for product {db_product.id}: {qr_hash}")
    except Exception as e:
        print(f"Error generating QR code: {e}")
        # If QR generation fails, we can't proceed with blockchain registration
        return db_product

    # Store product data in IPFS
    try:
        ipfs_service = IPFSService()
        ipfs_status = ipfs_service.get_status()
        
        # Prepare product data for IPFS storage
        product_data = {
            "id": db_product.id,
            "product_name": db_product.product_name,
            "product_description": db_product.product_description,
            "manufacturing_date": db_product.manufacturing_date.isoformat(),
            "batch_number": db_product.batch_number,
            "category": db_product.category,
            "qr_code_hash": db_product.qr_code_hash,
            "qr_code_path": db_product.qr_code_path,
            "manufacturer_id": db_product.manufacturer_id,
            "created_at": db_product.created_at.isoformat(),
            "updated_at": db_product.updated_at.isoformat() if db_product.updated_at else None
        }
        
        print(f"Storing product {db_product.id} data in IPFS (mode: {ipfs_status['status']})...")
        ipfs_result = await ipfs_service.store_product_data(product_data)
        
        if ipfs_result.get("success"):
            db_product.ipfs_hash = ipfs_result.get("ipfs_hash")
            db_product.ipfs_url = ipfs_result.get("public_url")
            db.commit()
            print(f"Product {db_product.id} data stored in IPFS: {ipfs_result.get('ipfs_hash')}")
        else:
            print(f"IPFS storage failed: {ipfs_result.get('error')}")
            
    except Exception as e:
        print(f"Error storing product data in IPFS: {e}")
        import traceback
        traceback.print_exc()

    # Register on blockchain if wallet address is available
    if current_user.wallet_address:
        try:
            # Use the Hardhat private key for development
            # In production, this should be securely managed
            hardhat_private_key = (
                "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
            )

            print(f" Attempting blockchain registration for product {db_product.id}")
            print(f"   Wallet: {current_user.wallet_address}")
            print(f"   QR Hash: {db_product.qr_code_hash}")

            # Get initialized blockchain service
            service = await get_blockchain_service()

            blockchain_result = await service.register_product(
                product_name=db_product.product_name,
                product_description=db_product.product_description or "",
                manufacturing_date=int(db_product.manufacturing_date.timestamp()),
                batch_number=db_product.batch_number,
                category=db_product.category,
                qr_code_hash=db_product.qr_code_hash,
                wallet_address=current_user.wallet_address,
                private_key=hardhat_private_key,
            )

            print(f"Blockchain result: {blockchain_result}")

            if blockchain_result.get("success"):
                db_product.blockchain_id = blockchain_result.get("blockchain_id")
                db.commit()
                print(
                    f"Product {db_product.id} registered on blockchain with ID {db_product.blockchain_id}"
                )
            else:
                print(
                    f"Blockchain registration failed: {blockchain_result.get('error')}"
                )

        except Exception as e:
            print(f"Error registering product on blockchain: {e}")
            import traceback

            traceback.print_exc()

    return db_product


@router.get("/", response_model=List[ProductSchema])
async def get_products(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get list of products."""
    if current_user.role == UserRole.MANUFACTURER:
        products = (
            db.query(Product)
            .filter(Product.manufacturer_id == current_user.id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    else:
        products = (
            db.query(Product)
            .filter(Product.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )
    return products


@router.get("/my-products", response_model=List[ProductSchema])
async def get_my_products(
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
) -> Any:
    """products for the current manufacturer user."""
    if current_user.role != UserRole.MANUFACTURER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only manufacturers can access their products",
        )

    try:
        products = (
            db.query(Product)
            .filter(Product.manufacturer_id == current_user.id)
            .order_by(Product.created_at.desc())
            .all()
        )

        return products
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching products: {str(e)}",
        )


@router.get("/{product_id}", response_model=ProductSchema)
async def get_product(
    product_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """specific product by ID."""
    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    # Checks if user has access to this product
    if (
        current_user.role == UserRole.MANUFACTURER
        and product.manufacturer_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    return product


@router.get("/qr/{qr_code_hash}", response_model=ProductSchema)
async def get_product_by_qr_code(
    qr_code_hash: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Getting product by QR code hash."""
    product = (
        db.query(Product)
        .filter(Product.qr_code_hash == qr_code_hash)
        .first()
    )
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    return product


@router.put("/{product_id}", response_model=ProductSchema)
async def update_product(
    product_id: int,
    product_in: ProductUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Updating a product (manufacturers only)."""
    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    if (
        current_user.role != UserRole.MANUFACTURER
        or product.manufacturer_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the product manufacturer can update it",
        )

    update_data = product_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)

    return product


@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Delete a product (manufacturers only)."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    if (
        current_user.role != UserRole.MANUFACTURER
        or product.manufacturer_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the product manufacturer can delete it",
        )

    # Soft delete by setting is_active to False
    product.is_active = False
    db.commit()

    return {"message": "Product deleted successfully"}


@router.post("/{product_id}/qr-code")
async def generate_qr_code(
    product_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Generate QR code for a product."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    if (
        current_user.role != UserRole.MANUFACTURER
        or product.manufacturer_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the product manufacturer can generate QR codes",
        )

    try:
        product_data = {
            "id": product.id,
            "product_name": product.product_name,
            "batch_number": product.batch_number,
            "manufacturing_date": str(product.manufacturing_date),
            "created_at": str(product.created_at),
        }

        qr_file_path, qr_hash, qr_data, secure_url = await qr_service.create_product_qr_code(product_data)

        # Updating product with new QR code path
        product.qr_code_path = qr_file_path
        db.commit()

        return {
            "qr_code_path": qr_file_path,
            "qr_code_url": qr_service.get_qr_code_url(qr_file_path),
            "qr_hash": qr_hash,
            "qr_data": qr_data,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating QR code: {str(e)}",
        )


@router.get("/{product_id}/ipfs-data")
async def get_product_ipfs_data(
    product_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get product data from IPFS storage."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    if not product.ipfs_hash:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product data not stored in IPFS"
        )

    try:
        ipfs_service = IPFSService()
        ipfs_result = await ipfs_service.retrieve_product_data(product.ipfs_hash)
        
        if ipfs_result.get("success"):
            return {
                "product_id": product_id,
                "ipfs_hash": product.ipfs_hash,
                "ipfs_url": product.ipfs_url,
                "product_data": ipfs_result.get("product_data"),
                "metadata": ipfs_result.get("metadata"),
                "retrieved_at": datetime.utcnow().isoformat() + "Z"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve IPFS data: {ipfs_result.get('error')}"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving IPFS data: {str(e)}"
        )


@router.get("/{product_id}/swarm-data")
async def get_product_swarm_data(
    product_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get product data from Swarm storage (legacy endpoint)."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    if not product.swarm_hash:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product data not stored in Swarm"
        )

    try:
        from app.services.swarm_service import SwarmService
        swarm_service = SwarmService()
        swarm_result = await swarm_service.retrieve_product_data(product.swarm_hash)
        
        if swarm_result.get("success"):
            return {
                "product_id": product_id,
                "swarm_hash": product.swarm_hash,
                "swarm_url": product.swarm_url,
                "product_data": swarm_result.get("product_data"),
                "metadata": swarm_result.get("metadata"),
                "retrieved_at": datetime.utcnow().isoformat() + "Z"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve Swarm data: {swarm_result.get('error')}"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving Swarm data: {str(e)}"
        )


@router.post("/verify-product")
async def verify_product_from_qr(
    request: VerifyProductRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Verify a product from QR code data with counterfeit detection."""
    try:
        product = None
        qr_info = None
        
        #validate QR code data
        try:
            validation_result = qr_service.validate_qr_code(request.qr_data)
            if validation_result["valid"]:
                qr_info = validation_result["data"]
                product = db.query(Product).filter(Product.id == qr_info["product_id"]).first()
        except:
            pass 
    
        if not product:
            detection_reasons = ["QR code format invalid or product not found in database"]
            confidence_score = 0.1
            risk_level = "high"
            is_authentic = False
            
            return {
                "product": {
                    "id": None,
                    "product_name": "Unknown Product",
                    "product_description": "Product not found in database",
                    "manufacturing_date": None,
                    "batch_number": "Unknown",
                    "category": "Unknown",
                    "manufacturer": {
                        "full_name": "Unknown",
                        "email": "Unknown",
                    },
                },
                "verification": {
                    "id": None,
                    "is_authentic": is_authentic,
                    "location": request.location,
                    "verification_date": None,
                    "notes": request.notes,
                },
                "blockchain_verified": False,
                "blockchain_verification_id": None,
                "detection_reasons": detection_reasons,
                "confidence_score": confidence_score,
                "risk_level": risk_level,
            }
        else:
            verification_data = {
                'location': request.location,
                'notes': request.notes,
                'verifier_id': current_user.id
            }
            
            # Use the new CounterfeitDetectionService
            detection_service = CounterfeitDetectionService()
            # Extract QR hash from the QR data for counterfeit detection
            provided_qr_hash = qr_info.get("qr_hash") if qr_info else None
            detection_result = await detection_service.detect_counterfeit(
                product, verification_data, db, provided_qr_hash
            )
            is_authentic = detection_result['is_authentic']
            detection_reasons = detection_result['detection_reasons']
            confidence_score = detection_result['confidence_score']
            risk_level = detection_result['risk_level']


        verification = Verification(
            product_id=product.id if product else None,
            verifier_id=current_user.id,
            location=request.location,
            notes=request.notes,
            is_authentic=is_authentic,
        )

        db.add(verification)
        db.commit()
        db.refresh(verification)

        # Verify on blockchain if product has blockchain ID and is authentic
        blockchain_verified = False
        blockchain_verification_id = None

        if product and product.blockchain_id and current_user.wallet_address and is_authentic:
            try:
                blockchain_service = await get_blockchain_service()

                # Use the Hardhat private key for development
                hardhat_private_key = (
                    "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
                )

                blockchain_result = await blockchain_service.verify_product(
                    product_id=product.blockchain_id,
                    location=request.location,
                    notes=request.notes or "",
                    wallet_address=current_user.wallet_address,
                    private_key=hardhat_private_key,
                )

                if blockchain_result.get("success"):
                    blockchain_verified = True
                    blockchain_verification_id = blockchain_result.get(
                        "verification_id"
                    )

                    # Update verification record with blockchain info
                    verification.blockchain_verification_id = blockchain_verification_id
                    db.commit()

            except Exception as e:
                print(f"Blockchain verification failed: {e}")

        # Get manufacturer info if product exists
        manufacturer = None
        if product:
            manufacturer = db.query(User).filter(User.id == product.manufacturer_id).first()

        return {
            "product": {
                "id": product.id if product else None,
                "product_name": product.product_name if product else "Unknown Product",
                "product_description": product.product_description if product else "Product not found in database",
                "manufacturing_date": product.manufacturing_date.isoformat() if product else None,
                "batch_number": product.batch_number if product else "Unknown",
                "category": product.category if product else "Unknown",
                "manufacturer": {
                    "full_name": manufacturer.full_name if manufacturer else "Unknown",
                    "email": manufacturer.email if manufacturer else "Unknown",
                },
            },
            "verification": {
                "id": verification.id,
                "is_authentic": verification.is_authentic,
                "location": verification.location,
                "verification_date": verification.verification_date.isoformat(),
                "notes": verification.notes,
            },
            "blockchain_verified": blockchain_verified,
            "blockchain_verification_id": blockchain_verification_id,
            "detection_reasons": detection_reasons,
            "confidence_score": confidence_score,
            "risk_level": risk_level,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verifying product: {str(e)}",
        )
