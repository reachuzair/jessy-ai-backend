"""
Database initialization script to create all tables.
Run this script to set up the database schema.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the parent directory to Python path so imports work
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

from sqlalchemy.ext.asyncio import create_async_engine
from src.config.database import DATABASE_URL
from src.models.user import Base
from src.models.token_blacklist import TokenBlacklist  # Import to ensure table is registered
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_tables():
    """Create all database tables"""
    try:
        engine = create_async_engine(DATABASE_URL, echo=True)
        
        logger.info("Creating database tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("✅ Database tables created successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error creating database tables: {e}")
        raise
    finally:
        await engine.dispose()

async def drop_tables():
    """Drop all database tables (use with caution!)"""
    try:
        engine = create_async_engine(DATABASE_URL, echo=True)
        
        logger.warning("Dropping all database tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        
        logger.info("✅ Database tables dropped successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error dropping database tables: {e}")
        raise
    finally:
        await engine.dispose()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "drop":
        print("⚠️  WARNING: This will drop all database tables!")
        confirm = input("Are you sure? Type 'yes' to confirm: ")
        if confirm.lower() == "yes":
            asyncio.run(drop_tables())
        else:
            print("Operation cancelled.")
    else:
        asyncio.run(create_tables())
