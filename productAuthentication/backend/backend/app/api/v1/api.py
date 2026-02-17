from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    users,
    products,
    verifications,
    blockchain,
    analytics,
)

api_router = APIRouter()

# endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(
    verifications.router, prefix="/verifications", tags=["verifications"]
)
api_router.include_router(blockchain.router, prefix="/blockchain", tags=["blockchain"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
