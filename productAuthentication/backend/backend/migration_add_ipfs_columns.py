#!/usr/bin/env python3
"""
Database migration script to add IPFS columns to the products table.
This script adds ipfs_hash and ipfs_url columns while keeping the existing swarm columns for backward compatibility.
"""

import sqlite3
import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.database import engine, Base
from app.models.product import Product
from sqlalchemy import text

def run_migration():
    """Run the database migration to add IPFS columns"""
    print("🔄 Starting IPFS columns migration...")
    
    try:
        # Check if columns already exist (PostgreSQL version)
        with engine.connect() as conn:
            # Check if ipfs_hash column exists
            result = conn.execute(text("""
                SELECT COUNT(*) as count 
                FROM information_schema.columns 
                WHERE table_name = 'products' AND column_name = 'ipfs_hash'
            """))
            ipfs_hash_exists = result.fetchone()[0] > 0
            
            # Check if ipfs_url column exists
            result = conn.execute(text("""
                SELECT COUNT(*) as count 
                FROM information_schema.columns 
                WHERE table_name = 'products' AND column_name = 'ipfs_url'
            """))
            ipfs_url_exists = result.fetchone()[0] > 0
            
            if ipfs_hash_exists and ipfs_url_exists:
                print("✅ IPFS columns already exist. Migration not needed.")
                return True
            
            # Add ipfs_hash column if it doesn't exist
            if not ipfs_hash_exists:
                print("📝 Adding ipfs_hash column...")
                conn.execute(text("""
                    ALTER TABLE products 
                    ADD COLUMN ipfs_hash VARCHAR UNIQUE
                """))
                conn.commit()
                print("✅ ipfs_hash column added successfully")
            else:
                print("✅ ipfs_hash column already exists")
            
            # Add ipfs_url column if it doesn't exist
            if not ipfs_url_exists:
                print("📝 Adding ipfs_url column...")
                conn.execute(text("""
                    ALTER TABLE products 
                    ADD COLUMN ipfs_url VARCHAR
                """))
                conn.commit()
                print("✅ ipfs_url column added successfully")
            else:
                print("✅ ipfs_url column already exists")
            
            # Create index on ipfs_hash for better performance
            try:
                print("📝 Creating index on ipfs_hash...")
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_products_ipfs_hash 
                    ON products(ipfs_hash)
                """))
                conn.commit()
                print("✅ Index on ipfs_hash created successfully")
            except Exception as e:
                print(f"⚠️  Warning: Could not create index on ipfs_hash: {e}")
            
            print("🎉 IPFS columns migration completed successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def rollback_migration():
    """Rollback the migration (remove IPFS columns)"""
    print("🔄 Rolling back IPFS columns migration...")
    
    try:
        with engine.connect() as conn:
            # Drop index first
            try:
                conn.execute(text("DROP INDEX IF EXISTS idx_products_ipfs_hash"))
                conn.commit()
                print("✅ Index dropped successfully")
            except Exception as e:
                print(f"⚠️  Warning: Could not drop index: {e}")
            
            # Drop columns (SQLite doesn't support DROP COLUMN directly)
            # We would need to recreate the table, which is complex
            print("⚠️  Note: SQLite doesn't support DROP COLUMN directly.")
            print("   To rollback, you would need to recreate the table.")
            print("   Consider backing up your data before making schema changes.")
            
    except Exception as e:
        print(f"❌ Rollback failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        rollback_migration()
    else:
        success = run_migration()
        if success:
            print("\n📋 Migration Summary:")
            print("   - Added ipfs_hash column (VARCHAR UNIQUE)")
            print("   - Added ipfs_url column (VARCHAR)")
            print("   - Created index on ipfs_hash")
            print("   - Kept existing swarm columns for backward compatibility")
            print("\n🚀 You can now use IPFS for product data storage!")
        else:
            print("\n❌ Migration failed. Please check the error messages above.")
            sys.exit(1)
