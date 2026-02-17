import hashlib
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.product import Product
from app.models.verification import Verification
from app.models.user import User
from app.services.swarm_service import SwarmService
import logging

logger = logging.getLogger(__name__)


class CounterfeitDetectionService:
    """
    Advanced counterfeit detection service with multiple validation layers
    """
    
    def __init__(self):
        self.swarm_service = SwarmService()
        
    async def detect_counterfeit(
        self, 
        product: Product, 
        verification_data: Dict[str, Any], 
        db: Session, 
        provided_qr_hash: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive counterfeit detection with multiple validation layers
        
        Returns:
            Dict with 'is_authentic', 'detection_reasons', 'confidence_score', 'risk_level'
        """
        detection_reasons = []
        risk_factors = []
        is_authentic = True
        
        try:
            # 1. QR Code Validation
            qr_validation = await self._validate_qr_code(product, provided_qr_hash, db)
            detection_reasons.extend(qr_validation['reasons'])
            if not qr_validation['is_valid']:
                is_authentic = False
                risk_factors.append('qr_invalid')
            
            # 2. IPFS Data Integrity Check
            ipfs_validation = await self._validate_ipfs_data(product)
            detection_reasons.extend(ipfs_validation['reasons'])
            if not ipfs_validation['is_valid']:
                is_authentic = False
                risk_factors.append('ipfs_invalid')
            
            # 3. Blockchain Verification
            blockchain_validation = await self._validate_blockchain_data(product)
            detection_reasons.extend(blockchain_validation['reasons'])
            if not blockchain_validation['is_valid']:
                risk_factors.append('blockchain_invalid')
            
            # 4. Duplicate Detection
            duplicate_check = await self._check_duplicates(product, db)
            detection_reasons.extend(duplicate_check['reasons'])
            if duplicate_check['has_duplicates']:
                is_authentic = False
                risk_factors.append('duplicate_detected')
            
            # 5. Verification Pattern Analysis
            pattern_analysis = await self._analyze_verification_patterns(product, db)
            detection_reasons.extend(pattern_analysis['reasons'])
            if pattern_analysis['suspicious_pattern']:
                risk_factors.append('suspicious_pattern')
            
            # 6. Manufacturer Validation
            manufacturer_validation = await self._validate_manufacturer(product, db)
            detection_reasons.extend(manufacturer_validation['reasons'])
            if not manufacturer_validation['is_valid']:
                risk_factors.append('manufacturer_invalid')
            
            # 7. Product Data Consistency
            consistency_check = await self._check_data_consistency(product, verification_data)
            detection_reasons.extend(consistency_check['reasons'])
            if not consistency_check['is_consistent']:
                risk_factors.append('data_inconsistent')
            
            # Calculate confidence score and risk level
            confidence_score = self._calculate_confidence_score(is_authentic, risk_factors, detection_reasons)
            risk_level = self._calculate_risk_level(risk_factors, confidence_score)
            
            return {
                'is_authentic': is_authentic,
                'detection_reasons': detection_reasons,
                'confidence_score': confidence_score,
                'risk_level': risk_level,
                'risk_factors': risk_factors,
                'validation_summary': {
                    'qr_valid': qr_validation['is_valid'],
                    'blockchain_valid': blockchain_validation['is_valid'],
                    'no_duplicates': not duplicate_check['has_duplicates'],
                    'normal_pattern': not pattern_analysis['suspicious_pattern'],
                    'manufacturer_valid': manufacturer_validation['is_valid'],
                    'data_consistent': consistency_check['is_consistent']
                }
            }
            
        except Exception as e:
            logger.error(f"Error in counterfeit detection: {e}")
            return {
                'is_authentic': False,
                'detection_reasons': [f"Detection error: {str(e)}"],
                'confidence_score': 0.0,
                'risk_level': 'high',
                'risk_factors': ['detection_error'],
                'validation_summary': {}
            }
    
    async def _validate_qr_code(self, product: Product, provided_qr_hash: Optional[str], db: Session) -> Dict[str, Any]:
        """Validate QR code hash and check for duplicates"""
        reasons = []
        is_valid = True
        
        # Check QR code hash format (SHA-256 should be 64 characters)
        if not product.qr_code_hash or len(product.qr_code_hash) != 64:
            is_valid = False
            reasons.append("Invalid QR code hash format - possible counterfeit")
        else:
            reasons.append("QR code hash format is valid")
            
            # Check if provided QR hash matches stored hash
            if provided_qr_hash:
                if product.qr_code_hash != provided_qr_hash:
                    is_valid = False
                    reasons.append("QR code hash mismatch - possible counterfeit")
                else:
                    reasons.append("QR code hash matches stored value")
            
            # Check for duplicate QR codes across different products
            duplicate_count = db.query(Product).filter(
                Product.qr_code_hash == product.qr_code_hash,
                Product.id != product.id
            ).count()
            
            if duplicate_count > 0:
                is_valid = False
                reasons.append(f"Duplicate QR code detected on {duplicate_count} other products - counterfeit")
            else:
                reasons.append("QR code is unique - no duplicates found")
        
        return {'is_valid': is_valid, 'reasons': reasons}
    
    async def _validate_ipfs_data(self, product: Product) -> Dict[str, Any]:
        """Validate IPFS data integrity"""
        reasons = []
        is_valid = True
        
        if not product.ipfs_hash:
            reasons.append("No IPFS data available - limited verification")
            return {'is_valid': True, 'reasons': reasons}  # Not invalid, just limited
        
        try:
            # Retrieve data from IPFS
            from app.services.ipfs_service import IPFSService
            ipfs_service = IPFSService()
            ipfs_result = await ipfs_service.retrieve_product_data(product.ipfs_hash)
            
            if not ipfs_result['success']:
                is_valid = False
                reasons.append(f"IPFS data retrieval failed: {ipfs_result.get('error')}")
            else:
                ipfs_data = ipfs_result['product_data']
                
                # Validate data consistency
                if ipfs_data.get('product_name') != product.product_name:
                    is_valid = False
                    reasons.append("IPFS data product name mismatch")
                elif ipfs_data.get('batch_number') != product.batch_number:
                    is_valid = False
                    reasons.append("IPFS data batch number mismatch")
                else:
                    reasons.append("IPFS data integrity verified")
                    
        except Exception as e:
            is_valid = False
            reasons.append(f"IPFS validation error: {str(e)}")
        
        return {'is_valid': is_valid, 'reasons': reasons}
    
    async def _validate_swarm_data(self, product: Product) -> Dict[str, Any]:
        """Validate Swarm data integrity (legacy)"""
        reasons = []
        is_valid = True
        
        if not product.swarm_hash:
            reasons.append("No Swarm data available - limited verification")
            return {'is_valid': True, 'reasons': reasons}  # Not invalid, just limited
        
        try:
            # Retrieve data from Swarm
            from app.services.swarm_service import SwarmService
            swarm_service = SwarmService()
            swarm_result = await swarm_service.retrieve_product_data(product.swarm_hash)
            
            if not swarm_result['success']:
                is_valid = False
                reasons.append(f"Swarm data retrieval failed: {swarm_result.get('error')}")
            else:
                swarm_data = swarm_result['product_data']
                
                # Validate data consistency
                if swarm_data.get('product_name') != product.product_name:
                    is_valid = False
                    reasons.append("Swarm data product name mismatch")
                elif swarm_data.get('batch_number') != product.batch_number:
                    is_valid = False
                    reasons.append("Swarm data batch number mismatch")
                else:
                    reasons.append("Swarm data integrity verified")
                    
        except Exception as e:
            is_valid = False
            reasons.append(f"Swarm validation error: {str(e)}")
        
        return {'is_valid': is_valid, 'reasons': reasons}
    
    async def _validate_blockchain_data(self, product: Product) -> Dict[str, Any]:
        """Validate blockchain registration"""
        reasons = []
        is_valid = True
        
        if not product.blockchain_id:
            reasons.append("Product not registered on blockchain")
            return {'is_valid': False, 'reasons': reasons}
        
        reasons.append("Product registered on blockchain")
        return {'is_valid': is_valid, 'reasons': reasons}
    
    async def _check_duplicates(self, product: Product, db: Session) -> Dict[str, Any]:
        """Check for duplicate products with same characteristics"""
        reasons = []
        has_duplicates = False
        
        # Check for products with same batch number and manufacturer
        duplicate_products = db.query(Product).filter(
            Product.batch_number == product.batch_number,
            Product.manufacturer_id == product.manufacturer_id,
            Product.id != product.id,
            Product.is_active == True
        ).all()
        
        if duplicate_products:
            has_duplicates = True
            reasons.append(f"Found {len(duplicate_products)} products with same batch number from same manufacturer")
        else:
            reasons.append("No duplicate products found with same batch number")
        
        return {'has_duplicates': has_duplicates, 'reasons': reasons}
    
    async def _analyze_verification_patterns(self, product: Product, db: Session) -> Dict[str, Any]:
        """Analyze verification patterns for suspicious activity"""
        reasons = []
        suspicious_pattern = False
        
        # Get recent verifications
        recent_verifications = db.query(Verification).filter(
            Verification.product_id == product.id,
            Verification.verification_date >= datetime.utcnow() - timedelta(days=30)
        ).all()
        
        total_verifications = len(recent_verifications)
        counterfeit_verifications = len([v for v in recent_verifications if not v.is_authentic])
        
        # Check for excessive verification attempts
        if total_verifications > 20:
            suspicious_pattern = True
            reasons.append(f"Excessive verification attempts: {total_verifications} in 30 days")
        elif total_verifications > 10:
            reasons.append(f"High verification frequency: {total_verifications} in 30 days")
        else:
            reasons.append(f"Normal verification pattern: {total_verifications} in 30 days")
        
        # Check for counterfeit detection rate
        if total_verifications > 0:
            counterfeit_rate = counterfeit_verifications / total_verifications
            if counterfeit_rate > 0.5:
                suspicious_pattern = True
                reasons.append(f"High counterfeit detection rate: {counterfeit_rate:.1%}")
            elif counterfeit_rate > 0.2:
                reasons.append(f"Moderate counterfeit detection rate: {counterfeit_rate:.1%}")
            else:
                reasons.append(f"Low counterfeit detection rate: {counterfeit_rate:.1%}")
        
        return {'suspicious_pattern': suspicious_pattern, 'reasons': reasons}
    
    async def _validate_manufacturer(self, product: Product, db: Session) -> Dict[str, Any]:
        """Validate manufacturer credentials"""
        reasons = []
        is_valid = True
        
        manufacturer = db.query(User).filter(User.id == product.manufacturer_id).first()
        
        if not manufacturer:
            is_valid = False
            reasons.append("Manufacturer not found in database")
        elif not manufacturer.is_active:
            is_valid = False
            reasons.append("Manufacturer account is inactive")
        elif not manufacturer.is_verified:
            reasons.append("Manufacturer account is not verified")
        else:
            reasons.append("Manufacturer account is valid and verified")
        
        return {'is_valid': is_valid, 'reasons': reasons}
    
    async def _check_data_consistency(self, product: Product, verification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check data consistency across different sources"""
        reasons = []
        is_consistent = True
        
        # Check if product has required fields
        if not product.product_name or not product.batch_number:
            is_consistent = False
            reasons.append("Missing required product information")
        else:
            reasons.append("Product information is complete")
        
        # Check manufacturing date reasonableness
        if product.manufacturing_date:
            if product.manufacturing_date > datetime.utcnow():
                is_consistent = False
                reasons.append("Manufacturing date is in the future")
            elif product.manufacturing_date < datetime.utcnow() - timedelta(days=365*10):  # 10 years ago
                reasons.append("Product is very old - verify authenticity")
            else:
                reasons.append("Manufacturing date is reasonable")
        
        return {'is_consistent': is_consistent, 'reasons': reasons}
    
    def _calculate_confidence_score(self, is_authentic: bool, risk_factors: List[str], detection_reasons: List[str]) -> float:
        """Calculate confidence score based on validation results"""
        if not is_authentic:
            return 0.0
        
        base_score = 0.9
        
        # Apply penalties based on risk factors
        penalties = {
            'qr_invalid': 0.4,
            'swarm_invalid': 0.3,
            'blockchain_invalid': 0.2,
            'duplicate_detected': 0.5,
            'suspicious_pattern': 0.3,
            'manufacturer_invalid': 0.2,
            'data_inconsistent': 0.2,
            'detection_error': 0.5
        }
        
        total_penalty = sum(penalties.get(factor, 0.1) for factor in risk_factors)
        
        # Apply additional penalties for warning reasons
        warning_count = len([r for r in detection_reasons if any(word in r.lower() for word in ['warning', 'limited', 'old', 'high'])])
        warning_penalty = warning_count * 0.05
        
        final_score = max(0.0, base_score - total_penalty - warning_penalty)
        return round(final_score, 2)
    
    def _calculate_risk_level(self, risk_factors: List[str], confidence_score: float) -> str:
        """Calculate risk level based on factors and confidence score"""
        if confidence_score < 0.3:
            return 'high'
        elif confidence_score < 0.7:
            return 'medium'
        else:
            return 'low'
    
    async def get_detailed_analysis(self, product: Product, db: Session) -> Dict[str, Any]:
        """Get detailed counterfeit analysis for a product"""
        try:
            # Perform comprehensive detection
            detection_result = await self.detect_counterfeit(product, {}, db)
            
            # Get verification history
            verifications = db.query(Verification).filter(
                Verification.product_id == product.id
            ).order_by(Verification.verification_date.desc()).limit(10).all()
            
            # Get manufacturer info
            manufacturer = db.query(User).filter(User.id == product.manufacturer_id).first()
            
            return {
                'product_id': product.id,
                'product_name': product.product_name,
                'detection_result': detection_result,
                'verification_history': [
                    {
                        'id': v.id,
                        'verification_date': v.verification_date,
                        'is_authentic': v.is_authentic,
                        'location': v.location,
                        'confidence_score': v.confidence_score
                    } for v in verifications
                ],
                'manufacturer_info': {
                    'id': manufacturer.id if manufacturer else None,
                    'name': manufacturer.full_name if manufacturer else None,
                    'email': manufacturer.email if manufacturer else None,
                    'is_verified': manufacturer.is_verified if manufacturer else False,
                    'is_active': manufacturer.is_active if manufacturer else False
                } if manufacturer else None,
                'analysis_timestamp': datetime.utcnow().isoformat() + "Z"
            }
            
        except Exception as e:
            logger.error(f"Error in detailed analysis: {e}")
            return {
                'error': str(e),
                'analysis_timestamp': datetime.utcnow().isoformat() + "Z"
            }
