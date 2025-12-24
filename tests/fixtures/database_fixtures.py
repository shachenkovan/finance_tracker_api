from datetime import date

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from database.models import Users, Budgets, Goals, Categories, Transactions, Wallets


@pytest.fixture(scope='function')
async def db_session():
    """
    Тестовая БД.
    """
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=True
    )

    from database.database import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """
    Тестовый пользователь.
    """
    user = Users(
        name='name_test',
        lastname='lastname_test',
        date_of_birth=date(2001, 1, 1),
        passport='1234 567890',
        login='test_user',
        password='test_pass',
        is_admin=False
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_budget(db_session: AsyncSession, test_user, test_category):
    """
    Тестовый бюджет.
    """
    budget =  Budgets(
        name='test_budget',
        amount='22000',
        category_id=test_category.id,
        user_id=test_user.id
    )
    db_session.add(budget)
    await db_session.commit()
    await db_session.refresh(budget)
    return budget


@pytest.fixture
async def test_goal(db_session: AsyncSession, test_user):
    """
    Тестовая цель.
    """
    goal = Goals(
        name='test_goal',
        cost='3500',
        deadline=date(2027, 7 , 7),
        actual_amount='500',
        user_id=test_user.id
    )
    db_session.add(goal)
    await db_session.commit()
    await db_session.refresh(goal)
    return goal


@pytest.fixture
async def test_category(db_session: AsyncSession):
    """
    Тестовая категория.
    """
    category = Categories(
        name='test_category',
        is_public=True,
        type='Expense'
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)
    return category


@pytest.fixture
async def test_transaction(db_session: AsyncSession, test_category, test_wallet):
    """
    Тестовая транзакция.
    """
    transaction = Transactions(
        amount='350',
        category_id=test_category.id,
        wallet_id=test_wallet.id
    )
    db_session.add(transaction)
    await db_session.commit()
    await db_session.refresh(transaction)
    return transaction


@pytest.fixture
async def test_wallet(db_session: AsyncSession, test_user):
    """
    Тестовый кошелек.
    """
    wallet = Wallets(
        amount='5000',
        type_of_wallet='Card',
        user_id=test_user.id
    )
    db_session.add(wallet)
    await db_session.commit()
    await db_session.refresh(wallet)
    return wallet

