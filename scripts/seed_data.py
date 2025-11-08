#!/usr/bin/env python3
"""Seed the database with sample data."""
import asyncio
import sys
import os
from uuid import UUID

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import AsyncSessionLocal
from app.models import User
from passlib.context import CryptContext
from app.core.logging import logger

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Use the same temp user ID as in the API
TEMP_USER_ID = UUID("00000000-0000-0000-0000-000000000001")


async def seed_data():
    """Seed database with sample data."""
    async with AsyncSessionLocal() as session:
        try:
            # Check if user already exists
            from sqlalchemy import select
            existing_user = await session.execute(
                select(User).where(User.id == TEMP_USER_ID)
            )
            if existing_user.scalar_one_or_none():
                logger.info("Sample user already exists")
                return
            
            # Create a sample user with fixed ID
            password = "admin123"
            sample_user = User(
                id=TEMP_USER_ID,
                email="admin@example.com",
                password_hash=pwd_context.hash(password[:72]),  # bcrypt limitation
                role="admin",
                is_active=True
            )
            
            session.add(sample_user)
            await session.commit()
            
            logger.info("Sample user created:")
            logger.info("  Email: admin@example.com")
            logger.info("  Password: admin123")
            logger.info("  ID: " + str(TEMP_USER_ID))
            logger.info("Database seeded successfully!")
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Error seeding database: {e}")
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(seed_data())
