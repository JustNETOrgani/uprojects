from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.product import Product
from app.models.verification import Verification
from app.schemas.verification import (
    Verification as VerificationSchema,
    VerificationCreate,
)
from app.services.blockchain_service import BlockchainService
from app.services.counterfeit_detection_service import CounterfeitDetectionService
import hashlib
import json
from datetime import datetime

router = APIRouter()

async def get_blockchain_service():
    """Get initialized blockchain service"""
    # Create a new instance each time to ensure fresh configuration
    service = BlockchainService()
    await service.initialize()
    return service


def detect_counterfeit(product: Product, verification_data: dict, db: Session, provided_qr_hash: str = None) -> dict:
    """
    Comprehensive counterfeit detection logic with duplicate QR code detection
    Returns: dict with 'is_authentic' (bool) and 'detection_reasons' (list)
    """
    detection_reasons = []
    is_authentic = True  # Start with True, set to False if issues found

    # 1. QR Code Validation
    if product.qr_code_hash:
        # Check QR code hash length (SHA-256 hash)
        if len(product.qr_code_hash) != 64:
            is_authentic = False
            detection_reasons.append("Invalid QR code hash format - possible counterfeit")
        else:
            # If a QR code hash was provided during verification, validate it matches
            if provided_qr_hash:
                if product.qr_code_hash != provided_qr_hash:
                    is_authentic = False
                    detection_reasons.append("QR code hash mismatch - possible counterfeit")
                else:
                    detection_reasons.append("QR code hash validated and matches product")
            else:
                detection_reasons.append("QR code hash validated (no verification hash provided)")

            # Check for duplicate QR hash across different products
            duplicate_product = (
                db.query(Product)
                .filter(Product.qr_code_hash == product.qr_code_hash, Product.id != product.id)
                .first()
            )
            if duplicate_product:
                is_authentic = False
                detection_reasons.append(
                    f"Duplicate QR code hash detected on product ID {duplicate_product.id} - possible counterfeit"
                )
    else:
        detection_reasons.append("No QR code hash available - verification limited")

    # 2. Blockchain Verification
    if product.blockchain_id:
        detection_reasons.append("Product registered on blockchain")
    else:
        detection_reasons.append("Product not yet registered on blockchain")
        # Not marking counterfeit solely on this condition

    # 3. Location Anomaly Detection
    if verification_data.get('location'):
        suspicious_locations = ['unknown', 'suspicious', 'unverified']
        if any(loc in verification_data['location'].lower() for loc in suspicious_locations):
            detection_reasons.append("Suspicious verification location")
            # Warn, but do not mark counterfeit merely for location

    # 4. Multiple Verification Detection
    recent_verifications = db.query(Verification).filter(
        Verification.product_id == product.id
    ).count()
    
    if recent_verifications > 10:
        detection_reasons.append("High frequency of verifications - potential suspicious activity")

    # 5. Manufacturer Verification
    # (Add manufacturer whitelist checks if implemented)

    # 6. Product Details Validation
    if not product.product_name or not product.product_description:
        detection_reasons.append("Incomplete product information")

    # 7. Batch Number Validation
    if product.batch_number:
        if len(product.batch_number) < 3:
            detection_reasons.append("Invalid batch number format")

    # 8. Overall Assessment
    if is_authentic and product.qr_code_hash and len(product.qr_code_hash) == 64:
        detection_reasons.append("Product appears authentic based on available data")

    return {
        'is_authentic': is_authentic,
        'detection_reasons': detection_reasons,
        'confidence_score': calculate_confidence_score(is_authentic, detection_reasons)
    }


def calculate_confidence_score(is_authentic: bool, detection_reasons: list) -> float:
    """
    Calculate confidence score based on detection results
    Returns: float between 0.0 and 1.0
    """
    if is_authentic:
        # Higher confidence if fewer suspicious flags
        base_score = 0.9
        
        # Count different types of issues
        suspicious_count = len([r for r in detection_reasons if 'suspicious' in r.lower()])
        invalid_count = len([r for r in detection_reasons if 'invalid' in r.lower()])
        warning_count = len([r for r in detection_reasons if 'warning' in r.lower() or 'limited' in r.lower()])
        
        # Apply penalties based on severity
        penalty = (suspicious_count * 0.15) + (invalid_count * 0.1) + (warning_count * 0.05)
        
        return max(0.3, base_score - penalty)
    else:
        # Lower confidence if marked as counterfeit
        base_score = 0.1
        
        # Count counterfeit indicators
        counterfeit_count = len([r for r in detection_reasons if 'counterfeit' in r.lower()])
        mismatch_count = len([r for r in detection_reasons if 'mismatch' in r.lower()])
        duplicate_count = len([r for r in detection_reasons if 'duplicate' in r.lower()])
        
        # Apply penalties based on severity
        penalty = (counterfeit_count * 0.2) + (mismatch_count * 0.15) + (duplicate_count * 0.1)
        
        return max(0.0, base_score - penalty)


@router.post("/", response_model=VerificationSchema)
async def create_verification(
    verification_in: VerificationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    blockchain_service: BlockchainService = Depends(get_blockchain_service)
) -> Any:
    """Create a new verification record with counterfeit detection."""
    product = db.query(Product).filter(Product.id == verification_in.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    # Perform counterfeit detection using the new service
    verification_data = {
        'location': verification_in.location,
        'notes': verification_in.notes,
        'verifier_id': current_user.id
    }
    
    # Get QR code hash from verification data if provided
    provided_qr_hash = getattr(verification_in, 'qr_code_hash', None)
    
    # Use the new counterfeit detection service
    detection_service = CounterfeitDetectionService()
    detection_result = await detection_service.detect_counterfeit(product, verification_data, db, provided_qr_hash)
    
    db_verification = Verification(
        product_id=verification_in.product_id,
        verifier_id=current_user.id,
        location=verification_in.location,
        notes=verification_in.notes,
        is_authentic=detection_result['is_authentic'],
        detection_reasons=detection_result['detection_reasons'],
        confidence_score=detection_result['confidence_score'],
        risk_level=detection_result.get('risk_level', 'low'),
        blockchain_verified=False,  # Will be updated after blockchain verification
    )

    db.add(db_verification)
    db.commit()
    db.refresh(db_verification)

    # Verifies on blockchain if wallet address is available
    if current_user.wallet_address and product.blockchain_id:
        try:
            blockchain_result = await blockchain_service.verify_product(
                product_id=product.blockchain_id,
                location=verification_in.location,
                notes=verification_in.notes or "",
                wallet_address=current_user.wallet_address,
                private_key="0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80",
                qr_code_hash=product.qr_code_hash
            )
            
            print(blockchain_result)
            
            if blockchain_result.get("success"):
                # Update verification result based on blockchain verification
                blockchain_authentic = blockchain_result.get("verification_result", True)
                if not blockchain_authentic:
                    db_verification.is_authentic = False
                    detection_result['is_authentic'] = False
                    detection_result['detection_reasons'].append("Blockchain verification failed - product marked as counterfeit")
                
                db_verification.blockchain_verification_id = blockchain_result.get(
                    "verification_id"
                )
                db_verification.blockchain_verified = True
                db.commit()
        except Exception as e:
            print(f"Error verifying product on blockchain: {e}")
            # If blockchain verification fails, mark as suspicious
            detection_result['detection_reasons'].append("Blockchain verification error")

    # Return the verification object directly (as expected by the schema)
    # The detection result is already stored in the verification record
    return db_verification


@router.post("/analyze-counterfeit/{product_id}")
async def analyze_counterfeit_detection(
    product_id: int,
    qr_code_hash: str = None,
    location: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    blockchain_service: BlockchainService = Depends(get_blockchain_service)
) -> Any:
    """Perform detailed counterfeit analysis for a product."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    verification_data = {
        'location': location or "Unknown",
        'notes': f"Counterfeit analysis by {current_user.email}",
        'verifier_id': current_user.id
    }
    
    # Perform comprehensive counterfeit detection using the new service
    detection_service = CounterfeitDetectionService()
    detection_result = await detection_service.detect_counterfeit(product, verification_data, db, qr_code_hash)
    
    # Additional blockchain analysis
    blockchain_analysis = {}
    if current_user.wallet_address and product.blockchain_id:
        try:
            blockchain_result = await blockchain_service.verify_product(
                product_id=product.blockchain_id,
                location=location or "Analysis",
                notes="Counterfeit analysis",
                wallet_address=current_user.wallet_address,
                private_key="0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80",
                qr_code_hash=qr_code_hash or product.qr_code_hash
            )
            
            blockchain_analysis = {
                "blockchain_verification": blockchain_result.get("success", False),
                "verification_result": blockchain_result.get("verification_result", True),
                "transaction_hash": blockchain_result.get("transaction_hash"),
                "block_number": blockchain_result.get("block_number")
            }
            
            # Update detection result based on blockchain analysis
            if not blockchain_result.get("success"):
                detection_result['detection_reasons'].append("Blockchain verification failed")
            elif not blockchain_result.get("verification_result", True):
                detection_result['is_authentic'] = False
                detection_result['detection_reasons'].append("Blockchain marked product as counterfeit")
                
        except Exception as e:
            blockchain_analysis = {
                "error": str(e),
                "blockchain_verification": False
            }
            detection_result['detection_reasons'].append("Blockchain verification error")
    
    # Get verification history for pattern analysis
    verification_history = db.query(Verification).filter(
        Verification.product_id == product_id
    ).all()
    
    pattern_analysis = {
        "total_verifications": len(verification_history),
        "authentic_verifications": len([v for v in verification_history if v.is_authentic]),
        "counterfeit_verifications": len([v for v in verification_history if not v.is_authentic]),
        "verification_frequency": "Normal" if len(verification_history) < 10 else "High",
        "suspicious_patterns": []
    }
    
    # Check for suspicious patterns
    if len(verification_history) > 50:
        pattern_analysis["suspicious_patterns"].append("Excessive verification attempts")
    
    if len([v for v in verification_history if not v.is_authentic]) > 0:
        pattern_analysis["suspicious_patterns"].append("Previous counterfeit detections")
    
    # Calculate risk score
    risk_factors = len(detection_result['detection_reasons']) + len(pattern_analysis['suspicious_patterns'])
    risk_score = min(100, risk_factors * 20)  # 0-100 scale
    
    return {
        "product_id": product_id,
        "product_name": product.product_name,
        "manufacturer_id": product.manufacturer_id,
        "detection_result": detection_result,
        "blockchain_analysis": blockchain_analysis,
        "pattern_analysis": pattern_analysis,
        "risk_assessment": {
            "risk_score": risk_score,
            "risk_level": "Low" if risk_score < 30 else "Medium" if risk_score < 70 else "High",
            "recommendation": get_risk_recommendation(risk_score, detection_result['is_authentic'])
        },
        "analysis_timestamp": datetime.utcnow().isoformat() + "Z"
    }


def get_risk_recommendation(risk_score: int, is_authentic: bool) -> str:
    """Generate recommendation based on risk score and authenticity."""
    if not is_authentic:
        return "Product appears to be counterfeit. Do not purchase or use."
    elif risk_score >= 70:
        return "High risk product. Exercise extreme caution and verify through official channels."
    elif risk_score >= 40:
        return "Medium risk product. Additional verification recommended."
    else:
        return "Low risk product. Appears authentic based on current analysis."


@router.get("/", response_model=List[VerificationSchema])
async def get_verifications(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get list of verifications."""
    verifications = db.query(Verification).offset(skip).limit(limit).all()
    return verifications


@router.get("/{verification_id}", response_model=VerificationSchema)
async def get_verification(
    verification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get a specific verification."""
    verification = (
        db.query(Verification).filter(Verification.id == verification_id).first()
    )
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Verification not found"
        )

    return verification


@router.get("/product/{product_id}", response_model=List[VerificationSchema])
async def get_product_verifications(
    product_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get all verifications for a specific product."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    verifications = (
        db.query(Verification).filter(Verification.product_id == product_id).all()
    )
    return verifications