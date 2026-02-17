from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User, UserRole
from app.models.product import Product
from app.services.blockchain_service import BlockchainService

router = APIRouter()
blockchain_service = BlockchainService()


async def get_blockchain_service():
    """Get initialized blockchain service"""
    # Create a new instance each time to ensure fresh configuration
    service = BlockchainService()
    await service.initialize()
    return service


@router.get("/status")
async def get_blockchain_status(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get blockchain network status."""
    try:
        service = await get_blockchain_service()
        network_info = await service.get_network_info()
        return network_info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting blockchain status: {str(e)}",
        )


@router.get("/products/count")
async def get_total_products(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """total number of products on blockchain."""
    try:
        service = await get_blockchain_service()
        total = await service.get_total_products()
        return {"total_products": total}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting total products: {str(e)}",
        )


@router.get("/products/{product_id}")
async def get_blockchain_product(
    product_id: int, current_user: User = Depends(get_current_active_user)
) -> Any:
    """product details from blockchain."""
    try:
        service = await get_blockchain_service()
        product = await service.get_product(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found on blockchain",
            )
        return product
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting product from blockchain: {str(e)}",
        )


@router.get("/products/qr/{qr_code_hash}")
async def get_blockchain_product_by_qr(
    qr_code_hash: str, current_user: User = Depends(get_current_active_user)
) -> Any:
    """product details from blockchain by QR code hash."""
    try:
        service = await get_blockchain_service()
        product = await service.get_product_by_qr_code(qr_code_hash)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found on blockchain",
            )
        return product
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting product from blockchain: {str(e)}",
        )


@router.post("/grant-role")
async def grant_blockchain_role(
    role_data: dict,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Grant role to an address on blockchain (admin only)."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can grant roles",
        )
    
    try:
        service = await get_blockchain_service()
        
        # For now, we'll just grant the MANUFACTURER_ROLE
        # In a real implementation, this would call the smart contract
        role_name = role_data.get("role", "MANUFACTURER_ROLE")
        account = role_data.get("account")
        
        if not account:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account address is required",
            )
        
        # For development, we'll return success
        # In production, this would actually call the smart contract's grantUserRole function
        return {
            "success": True,
            "role": role_name,
            "account": account,
            "message": f"Role {role_name} granted to {account}"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error granting role: {str(e)}",
        )


@router.post("/products/{product_id}/verify")
async def verify_product_on_blockchain(
    product_id: int,
    location: str,
    notes: str = "",
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Verify a product on the blockchain."""
    if not current_user.wallet_address:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wallet address required for blockchain verification",
        )

    try:
        # First,i get the product from database to find the blockchain ID
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found in database",
            )

        if not product.blockchain_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product not registered on blockchain",
            )

        blockchain_product_id = product.blockchain_id

        # for some reason its not reading it in the env so i hardcoded it
        hardhat_private_key = (
            "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
        )

        service = await get_blockchain_service()
        result = await service.verify_product(
            product_id=blockchain_product_id,
            location=location,
            notes=notes,
            wallet_address=current_user.wallet_address,
            private_key=hardhat_private_key,
        )

        if result.get("success"):
            return {
                "success": True,
                "transaction_hash": result.get("transaction_hash"),
                "block_number": result.get("block_number"),
                "gas_used": result.get("gas_used"),
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Blockchain verification failed: {result.get('error')}",
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verifying product on blockchain: {str(e)}",
        )


@router.get("/admin/network-info")
async def get_detailed_network_info(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get detailed blockchain network information (admin only)."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can access detailed network information",
        )

    try:
        service = await get_blockchain_service()
        network_info = await service.get_network_info()
        total_products = await service.get_total_products()

        return {
            **network_info,
            "total_products": total_products,
            "contract_address": service.contract_address,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting network information: {str(e)}",
        )
