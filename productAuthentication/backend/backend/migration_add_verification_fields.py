#!/usr/bin/env python3
"""
Migration script to add missing fields to the verifications table.
This adds risk_level and blockchain_verified columns.
"""

import sqlite3
import os
from sqlalchemy import create_engine, text
from app.core.config import settings

def run_migration():
    """Add missing columns to verifications table"""
    print("🔄 Starting verification fields migration...")
    
    try:
        # Create engine
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as conn:
            # Check if columns already exist
            if settings.DATABASE_URL.startswith("sqlite"):
                # SQLite syntax
                result = conn.execute(text("PRAGMA table_info(verifications)"))
                columns = [row[1] for row in result.fetchall()]
            else:
                # PostgreSQL syntax
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'verifications'
                """))
                columns = [row[0] for row in result.fetchall()]
            
            print(f"📋 Existing columns: {columns}")
            
            # Add risk_level column if it doesn't exist
            if 'risk_level' not in columns:
                print("➕ Adding risk_level column...")
                conn.execute(text("ALTER TABLE verifications ADD COLUMN risk_level VARCHAR"))
                conn.commit()
                print("✅ risk_level column added successfully")
            else:
                print("ℹ️ risk_level column already exists")
            
            # Add blockchain_verified column if it doesn't exist
            if 'blockchain_verified' not in columns:
                print("➕ Adding blockchain_verified column...")
                conn.execute(text("ALTER TABLE verifications ADD COLUMN blockchain_verified BOOLEAN"))
                conn.commit()
                print("✅ blockchain_verified column added successfully")
            else:
                print("ℹ️ blockchain_verified column already exists")
            
            # Verify the changes
            if settings.DATABASE_URL.startswith("sqlite"):
                result = conn.execute(text("PRAGMA table_info(verifications)"))
                columns = [row[1] for row in result.fetchall()]
            else:
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'verifications'
                """))
                columns = [row[0] for row in result.fetchall()]
            
            print(f"📋 Updated columns: {columns}")
            
            # Check if new columns are present
            if 'risk_level' in columns and 'blockchain_verified' in columns:
                print("✅ Migration completed successfully!")
                print("📊 New columns added:")
                print("   - risk_level (VARCHAR)")
                print("   - blockchain_verified (BOOLEAN)")
            else:
                print("❌ Migration failed - new columns not found")
                
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()

def rollback_migration():
    """Rollback the migration (remove the new columns)"""
    print("🔄 Rolling back verification fields migration...")
    
    try:
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as conn:
            # Note: SQLite doesn't support DROP COLUMN directly
            # This would require recreating the table
            print("⚠️ Rollback not implemented for SQLite")
            print("   To rollback, you would need to recreate the table")
            
    except Exception as e:
        print(f"❌ Rollback failed: {str(e)}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        rollback_migration()
    else:
        run_migration()
