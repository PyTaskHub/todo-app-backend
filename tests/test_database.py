"""
Tests for database configuration and connectivity.
"""

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal, Base, engine, get_db


class TestDatabaseConnection:
    """Test database connection and configuration."""

    @pytest.mark.asyncio
    async def test_database_connection(self):
        """Test that we can connect to the database."""
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            assert result.scalar() == 1

    @pytest.mark.asyncio
    async def test_session_creation(self):
        """Test that we can create a database session."""
        async with AsyncSessionLocal() as session:
            assert isinstance(session, AsyncSession)
            assert session.is_active

    @pytest.mark.asyncio
    async def test_get_db_dependency(self):
        """Test the get_db dependency works correctly."""
        async for session in get_db():
            assert isinstance(session, AsyncSession)
            assert session.is_active
            # Test a simple query
            result = await session.execute(text("SELECT 1"))
            assert result.scalar() == 1

    @pytest.mark.asyncio
    async def test_base_metadata(self):
        """Test that Base has correct metadata."""
        assert Base.metadata is not None
        # Base should have common columns defined
        assert hasattr(Base, "id")
        assert hasattr(Base, "created_at")
        assert hasattr(Base, "updated_at")


class TestDatabaseOperations:
    """Test basic database operations."""

    @pytest.mark.asyncio
    async def test_transaction_commit(self):
        """Test that transactions can be committed."""
        async with AsyncSessionLocal() as session:
            # Execute a simple query
            result = await session.execute(text("SELECT 1 as value"))
            row = result.first()
            assert row.value == 1
            await session.commit()

    @pytest.mark.asyncio
    async def test_transaction_rollback(self):
        """Test that transactions can be rolled back."""
        async with AsyncSessionLocal() as session:
            try:
                # This should work
                await session.execute(text("SELECT 1"))
                await session.rollback()
            except Exception as e:
                pytest.fail(f"Rollback failed: {e}")
