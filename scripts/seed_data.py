#!/usr/bin/env python3
"""Seed the database with sample data."""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import AsyncSessionLocal
from app.models import User
from passlib.context import CryptContext
from app.core.logging import logger

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def seed_data():
    """Seed database with sample data."""
    async with AsyncSessionLocal() as session:
        try:
            # Create a sample user
            sample_user = User(
                email="admin@example.com",
                password_hash=pwd_context.hash("admin123"),
                role="admin",
                is_active=True
            )
            
            session.add(sample_user)
            await session.commit()
            
            logger.info("Sample user created:")
            logger.info("  Email: admin@example.com")
            logger.info("  Password: admin123")
            logger.info("Database seeded successfully!")
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Error seeding database: {e}")
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(seed_data())
