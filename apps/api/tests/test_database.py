"""
Database Tests
================
Tests for database operations and model validation.
"""

import pytest
from datetime import datetime
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.shared_core.database.session import Base, get_db_session
from apps.api.models.accounting import Account, AccountType, JournalEntry, JournalItem, EntryType
from apps.api.models.agriculture_school import AgricultureSchool, SchoolField


@pytest.fixture
async def db_session():
    """Create a test database session."""
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
    
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with async_session() as session:
        yield session
    
    await engine.dispose()


@pytest.mark.asyncio
async def test_account_crud(db_session: AsyncSession):
    """Test account CRUD operations."""
    # Create
    account = Account(
        id="1",
        code="1000",
        name="Cash",
        account_type=AccountType.ASSET,
    )
    db_session.add(account)
    await db_session.flush()
    
    # Read
    result = await db_session.execute(select(Account).where(Account.id == "1"))
    fetched = result.scalar_one_or_none()
    assert fetched is not None
    assert fetched.code == "1000"
    assert fetched.name == "Cash"
    
    # Update
    fetched.name = "Cash Account"
    await db_session.flush()
    
    result = await db_session.execute(select(Account).where(Account.id == "1"))
    updated = result.scalar_one()
    assert updated.name == "Cash Account"
    
    # Delete
    await db_session.delete(updated)
    await db_session.flush()
    
    result = await db_session.execute(select(Account).where(Account.id == "1"))
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_journal_entry_double_entry(db_session: AsyncSession):
    """Test journal entry double-entry validation."""
    # Create accounts
    cash = Account(id="2", code="1000", name="Cash", account_type=AccountType.ASSET)
    revenue = Account(id="3", code="4000", name="Revenue", account_type=AccountType.INCOME)
    db_session.add_all([cash, revenue])
    await db_session.flush()
    
    # Create balanced entry
    entry = JournalEntry(
        id="JE001",
        date=datetime.now(),
        description="Test transaction",
        items=[
            JournalItem(entry_id="JE001", account_id="1000", entry_type=EntryType.DEBIT, amount=Decimal("100")),
            JournalItem(entry_id="JE001", account_id="4000", entry_type=EntryType.CREDIT, amount=Decimal("100")),
        ]
    )
    db_session.add(entry)
    await db_session.flush()
    
    # Verify balance
    result = await db_session.execute(select(JournalEntry).where(JournalEntry.id == "JE001"))
    fetched = result.scalar_one()
    assert fetched.is_balanced is True
    assert fetched.total_debits == Decimal("100")
    assert fetched.total_credits == Decimal("100")


@pytest.mark.asyncio
async def test_agriculture_school_crud(db_session: AsyncSession):
    """Test agriculture school CRUD operations."""
    # Create
    school = AgricultureSchool(
        name="Test University",
        province="Tehran",
        city="Tehran",
        school_type="university",
        established=1950,
        students_count=5000,
    )
    db_session.add(school)
    await db_session.flush()
    
    # Read
    result = await db_session.execute(select(AgricultureSchool).where(AgricultureSchool.name == "Test University"))
    fetched = result.scalar_one_or_none()
    assert fetched is not None
    assert fetched.city == "Tehran"
    
    # Delete
    await db_session.delete(fetched)
    await db_session.flush()
    
    result = await db_session.execute(select(AgricultureSchool).where(AgricultureSchool.name == "Test University"))
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_account_type_enum():
    """Test account type enum values."""
    assert AccountType.ASSET == "asset"
    assert AccountType.LIABILITY == "liability"
    assert AccountType.EQUITY == "equity"
    assert AccountType.INCOME == "income"
    assert AccountType.EXPENSE == "expense"


@pytest.mark.asyncio
async def test_entry_type_enum():
    """Test journal entry type enum."""
    assert EntryType.DEBIT == "debit"
    assert EntryType.CREDIT == "credit"