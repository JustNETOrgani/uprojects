#!/usr/bin/env python3
"""
Migration script to add Swarm columns to the products table
Run this script to update the database schema
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.database import Base
from app.models.product import Product
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migration():
    """Add Swarm columns to products table"""
    try:
        # Create engine
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as connection:
            # Check if columns already exist
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'products' 
                AND column_name IN ('swarm_hash', 'swarm_url')
            """))
            
            existing_columns = [row[0] for row in result.fetchall()]
            
            # Add swarm_hash column if it doesn't exist
            if 'swarm_hash' not in existing_columns:
                logger.info("Adding swarm_hash column...")
                connection.execute(text("""
                    ALTER TABLE products 
                    ADD COLUMN swarm_hash VARCHAR UNIQUE
                """))
                connection.commit()
                logger.info("swarm_hash column added successfully")
            else:
                logger.info("swarm_hash column already exists")
            
            # Add swarm_url column if it doesn't exist
            if 'swarm_url' not in existing_columns:
                logger.info("Adding swarm_url column...")
                connection.execute(text("""
                    ALTER TABLE products 
                    ADD COLUMN swarm_url VARCHAR
                """))
                connection.commit()
                logger.info("swarm_url column added successfully")
            else:
                logger.info("swarm_url column already exists")
            
            # Create index on swarm_hash for better performance
            try:
                logger.info("Creating index on swarm_hash...")
                connection.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_products_swarm_hash 
                    ON products(swarm_hash)
                """))
                connection.commit()
                logger.info("Index on swarm_hash created successfully")
            except Exception as e:
                logger.warning(f"Index creation failed (might already exist): {e}")
            
            logger.info("Migration completed successfully!")
            
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise

if __name__ == "__main__":
    run_migration()
