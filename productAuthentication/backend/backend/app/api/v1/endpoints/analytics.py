from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, text
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.product import Product
from app.models.verification import Verification

router = APIRouter()


@router.get("/overview")
async def get_analytics_overview(
    range: str = Query("7d", description="Time range: 7d, 30d, 90d, 1y"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get analytics overview data."""

    # Calculating date range
    end_date = datetime.utcnow()
    if range == "7d":
        start_date = end_date - timedelta(days=7)
    elif range == "30d":
        start_date = end_date - timedelta(days=30)
    elif range == "90d":
        start_date = end_date - timedelta(days=90)
    elif range == "1y":
        start_date = end_date - timedelta(days=365)
    else:
        start_date = end_date - timedelta(days=7)

    # basic counts
    total_products = db.query(Product).count()
    total_users = db.query(User).count()

    # verification counts for the date range
    verifications = (
        db.query(Verification)
        .filter(
            Verification.verification_date >= start_date,
            Verification.verification_date <= end_date,
        )
        .count()
    )

    # blockchain transaction count (mock for now)
    blockchain_transactions = verifications  # assumpution***

    # Get counterfeit alerts (mock for now)
    counterfeit_alerts = (
        db.query(Verification)
        .filter(
            Verification.verification_date >= start_date,
            Verification.verification_date <= end_date,
            Verification.is_authentic == False,
        )
        .count()
    )

    # supply chain events (mock for now)
    supply_chain_events = verifications + total_products  # Mock calculation

    # Calculate authentic vs counterfeit products
    authentic_products = (
        db.query(Verification)
        .filter(
            Verification.verification_date >= start_date,
            Verification.verification_date <= end_date,
            Verification.is_authentic == True,
        )
        .count()
    )
    
    counterfeit_products = counterfeit_alerts  # Already calculated above
    
    # Get verification trends data
    verification_trends_data = (
        db.query(
            func.strftime("%Y-%m-%d", Verification.verification_date).label("date"),
            func.count(Verification.id).label("count"),
        )
        .filter(
            Verification.verification_date >= start_date,
            Verification.verification_date <= end_date,
        )
        .group_by(func.strftime("%Y-%m-%d", Verification.verification_date))
        .order_by(func.strftime("%Y-%m-%d", Verification.verification_date))
        .all()
    )
    
    verification_trends = [
        {"date": data.date, "count": data.count or 0} 
        for data in verification_trends_data
    ]
    
    # Get category distribution
    category_data = (
        db.query(Product.category, func.count(Product.id).label("count"))
        .group_by(Product.category)
        .all()
    )
    
    category_distribution = [
        {"category": data.category.capitalize() if data.category else "Unknown", "count": data.count or 0}
        for data in category_data
    ]
    
    # Get manufacturer stats
    manufacturer_data = (
        db.query(
            User.full_name.label("manufacturer_name"),
            func.count(Product.id).label("product_count"),
            func.count(Verification.id).label("verification_count")
        )
        .join(Product, User.id == Product.manufacturer_id)
        .outerjoin(Verification, Product.id == Verification.product_id)
        .group_by(User.id, User.full_name)
        .all()
    )
    
    manufacturer_stats = [
        {
            "manufacturer_name": data.manufacturer_name,
            "product_count": data.product_count or 0,
            "verification_count": data.verification_count or 0
        }
        for data in manufacturer_data
    ]

    return {
        "total_products": total_products,
        "total_users": total_users,
        "total_verifications": verifications,
        "authentic_products": authentic_products,
        "counterfeit_products": counterfeit_products,
        "verification_trends": verification_trends,
        "category_distribution": category_distribution,
        "manufacturer_stats": manufacturer_stats,
        # Keep original fields for backward compatibility
        "totalProducts": total_products,
        "totalUsers": total_users,
        "totalVerifications": verifications,
        "blockchainTransactions": blockchain_transactions,
        "counterfeitAlerts": counterfeit_alerts,
        "supplyChainEvents": supply_chain_events,
    }


@router.get("/verification-trends")
async def get_verification_trends(
    range: str = Query("7d", description="Time range: 7d, 30d, 90d, 1y"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get verification trends over time."""

    # Calculate date range
    end_date = datetime.utcnow()
    if range == "7d":
        start_date = end_date - timedelta(days=7)
    elif range == "30d":
        start_date = end_date - timedelta(days=30)
    elif range == "90d":
        start_date = end_date - timedelta(days=90)
    elif range == "1y":
        start_date = end_date - timedelta(days=365)
    else:
        start_date = end_date - timedelta(days=7)

    # SQLite-compatible date grouping
    verification_data = (
        db.query(
            func.strftime("%Y-%m-%d", Verification.verification_date).label("date"),
            func.count(Verification.id).label("count"),
            func.sum(
                func.case([(Verification.is_authentic == True, 1)], else_=0)
            ).label("authentic"),
            func.sum(
                func.case([(Verification.is_authentic == False, 1)], else_=0)
            ).label("counterfeit"),
        )
        .filter(
            Verification.verification_date >= start_date,
            Verification.verification_date <= end_date,
        )
        .group_by(func.strftime("%Y-%m-%d", Verification.verification_date))
        .order_by(func.strftime("%Y-%m-%d", Verification.verification_date))
        .all()
    )

    # Formatting the data
    result = []
    for data in verification_data:
        result.append(
            {
                "date": data.date,
                "count": data.count or 0,
                "authentic": data.authentic or 0,
                "counterfeit": data.counterfeit or 0,
            }
        )

    return result


@router.get("/product-categories")
async def get_product_categories(
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
) -> Any:
    """product distribution by category."""

    # product counts by category
    category_data = (
        db.query(Product.category, func.count(Product.id).label("count"))
        .group_by(Product.category)
        .all()
    )

    # colors for categories
    colors = [
        "#3B82F6",
        "#10B981",
        "#F59E0B",
        "#8B5CF6",
        "#EF4444",
        "#06B6D4",
        "#84CC16",
        "#F97316",
    ]

    result = []
    for i, data in enumerate(category_data):
        result.append(
            {
                "name": data.category.capitalize() if data.category else "Unknown",
                "value": data.count or 0,
                "color": colors[i % len(colors)],
            }
        )

    return result


@router.get("/supply-chain-events")
async def get_supply_chain_events(
    limit: int = Query(10, description="Number of events to return"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """recent supply chain events."""

    # recent verifications as supply chain events
    verifications = (
        db.query(Verification)
        .order_by(desc(Verification.verification_date))
        .limit(limit)
        .all()
    )

    # Mock supply chain events based on verifications
    events = []
    for i, verification in enumerate(verifications):
        # product info
        product = (
            db.query(Product).filter(Product.id == verification.product_id).first()
        )

        # Mock event types
        event_types = ["manufactured", "shipped", "delivered", "verified", "suspicious"]
        event_type = event_types[i % len(event_types)]

        # Mock locations
        locations = [
            "Shenzhen, China",
            "Portland, OR",
            "New York, NY",
            "London, UK",
            "Tokyo, Japan",
        ]
        location = locations[i % len(locations)]

        # Mock status
        statuses = ["completed", "pending", "failed"]
        status = statuses[i % len(statuses)]

        events.append(
            {
                "id": str(i + 1),
                "productId": str(verification.product_id),
                "productName": (
                    product.product_name
                    if product
                    else f"Product {verification.product_id}"
                ),
                "eventType": event_type,
                "location": location,
                "timestamp": verification.verification_date.isoformat(),
                "status": status,
            }
        )

    return events


@router.get("/counterfeit-alerts")
async def get_counterfeit_alerts(
    limit: int = Query(10, description="Number of alerts to return"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get counterfeit alerts."""

    # verifications that failed authenticity check
    failed_verifications = (
        db.query(Verification)
        .filter(Verification.is_authentic == False)
        .order_by(desc(Verification.verification_date))
        .limit(limit)
        .all()
    )

    # Convert to counterfeit alerts
    alerts = []
    for i, verification in enumerate(failed_verifications):
        # product info
        product = (
            db.query(Product).filter(Product.id == verification.product_id).first()
        )

        # Mock severity based on verification count
        severity_levels = ["low", "medium", "high", "critical"]
        severity = severity_levels[i % len(severity_levels)]

        # Mock descriptions
        descriptions = [
            "Multiple verification failures in same location",
            "QR code mismatch detected",
            "Product not found in blockchain",
            "Suspicious verification pattern",
            "Location verification failed",
        ]
        description = descriptions[i % len(descriptions)]

        # Mock status
        statuses = ["open", "investigating", "resolved"]
        status = statuses[i % len(statuses)]

        alerts.append(
            {
                "id": str(i + 1),
                "productId": str(verification.product_id),
                "productName": (
                    product.product_name
                    if product
                    else f"Product {verification.product_id}"
                ),
                "severity": severity,
                "description": description,
                "timestamp": verification.verification_date.isoformat(),
                "status": status,
            }
        )

    return alerts


@router.get("/user-activity")
async def get_user_activity(
    range: str = Query("7d", description="Time range: 7d, 30d, 90d, 1y"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get user activity metrics."""

    # date range
    end_date = datetime.utcnow()
    if range == "7d":
        start_date = end_date - timedelta(days=7)
    elif range == "30d":
        start_date = end_date - timedelta(days=30)
    elif range == "90d":
        start_date = end_date - timedelta(days=90)
    elif range == "1y":
        start_date = end_date - timedelta(days=365)
    else:
        start_date = end_date - timedelta(days=7)

    # user registrations over time using SQLite-compatible date functions
    user_registrations = (
        db.query(
            func.strftime("%Y-%m-%d", User.created_at).label("date"),
            func.count(User.id).label("count"),
        )
        .filter(User.created_at >= start_date, User.created_at <= end_date)
        .group_by(func.strftime("%Y-%m-%d", User.created_at))
        .order_by(func.strftime("%Y-%m-%d", User.created_at))
        .all()
    )

    # Gverification activity over time using SQLite-compatible date functions
    verification_activity = (
        db.query(
            func.strftime("%Y-%m-%d", Verification.verification_date).label("date"),
            func.count(Verification.id).label("count"),
        )
        .filter(
            Verification.verification_date >= start_date,
            Verification.verification_date <= end_date,
        )
        .group_by(func.strftime("%Y-%m-%d", Verification.verification_date))
        .order_by(func.strftime("%Y-%m-%d", Verification.verification_date))
        .all()
    )

    return {
        "userRegistrations": [
            {"date": data.date, "count": data.count or 0} for data in user_registrations
        ],
        "verificationActivity": [
            {"date": data.date, "count": data.count or 0}
            for data in verification_activity
        ],
    }


@router.get("/blockchain-stats")
async def get_blockchain_stats(
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
) -> Any:
    """blockchain statistics."""

    # total products on blockchain
    total_products = db.query(Product).filter(Product.blockchain_id.isnot(None)).count()

    # total verifications
    total_verifications = db.query(Verification).count()

    # successful verifications
    successful_verifications = (
        db.query(Verification).filter(Verification.is_authentic == True).count()
    )

    # failed verifications
    failed_verifications = (
        db.query(Verification).filter(Verification.is_authentic == False).count()
    )

    return {
        "totalProductsOnBlockchain": total_products,
        "totalVerifications": total_verifications,
        "successfulVerifications": successful_verifications,
        "failedVerifications": failed_verifications,
        "successRate": (
            (successful_verifications / total_verifications * 100)
            if total_verifications > 0
            else 0
        ),
    }
