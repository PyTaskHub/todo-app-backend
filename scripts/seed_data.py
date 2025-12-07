#!/usr/bin/env python3
"""
Script for adding test data to the database

Test data:

  5-10 users with descriptive names (testuser1, testuser2, etc.)
  3-5 categories per user (Work, Personal, Urgent, etc.)
  20-50 tasks per user with different parameters
"""
import sys
import os

from sqlalchemy import delete, select
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import asyncio
import random
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.models import User, Category, Task
from app.core.config import settings
from app.models.task import Status, Priority

async def main():
    engine = create_async_engine(settings.DATABASE_URL)
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    
    async with AsyncSessionLocal() as db:
        # Deleting old test data
        result = await db.execute(
            select(User).where(User.username.like("testuser%"))
        )
        test_users = result.scalars().all()
        
        if test_users:
            user_ids = [user.id for user in test_users]
            
            await db.execute(delete(Task).where(Task.user_id.in_(user_ids)))
            await db.execute(delete(Category).where(Category.user_id.in_(user_ids)))
            await db.execute(delete(User).where(User.id.in_(user_ids)))
            
            await db.commit()
        
        # Creating new users
        users = []
        for i in range(1, 9):
            users.append(User(
                username=f"testuser{i}",
                email=f"testuser{i}@example.com",
                # hashed password - "password123"
                password_hash="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"
            ))
        
        db.add_all(users)
        await db.flush()
        
        # Creating categories
        categories = []
        for user in users:
            for name in ["Work", "Personal", "Home"]:
                categories.append(Category(name=name, user_id=user.id))
        
        db.add_all(categories)
        await db.flush()
        
        # Create tasks
        tasks = []
        for user in users:
            for i in range(30):  # 30 tasks per user
                tasks.append(Task(
                    title=f"Task {i+1}",
                    description="Some description",
                    status=random.choice([Status.pending, Status.completed]),
                    priority=random.choice([Priority.high, Priority.low, Priority.medium]),
                    user_id=user.id,
                    category_id=random.choice(categories).id if random.choice([True, False]) else None
                ))
        
        db.add_all(tasks)
        await db.commit()
        
        print("All test data has been generated!")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())