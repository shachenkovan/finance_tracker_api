import pytest
from database.cruds import transaction
from database.models import Transactions


@pytest.mark.asyncio
async def test_get_all_transactions(test_transaction, test_wallet, test_category, db_session):
    """
    Тест для получения всех транзакций.
    """
    transaction_crud = transaction()
    result = await transaction_crud.get_all(db_session)

    assert result is not None

    transactions_ids = [transactions.id for transactions in result]
    assert test_transaction.id in transactions_ids


@pytest.mark.asyncio
async def test_get_transaction_by_id(test_transaction, test_wallet, test_category, db_session):
    """
    Тест для получения транзакции по id.
    """
    transaction_crud = transaction()
    result = await transaction_crud.get_by_id(db_session, test_transaction.id)

    assert result is not None
    assert test_transaction.id == result.id


@pytest.mark.asyncio
async def test_add_transaction(test_transaction, test_wallet, test_category, db_session):
    """
    Тест для добавления транзакции.
    """
    transaction_crud = transaction()
    transaction_add = Transactions(
        amount=5000,
        wallet_id=test_wallet.id,
        category_id=test_category.id
    )

    result = await transaction_crud.create(db_session, transaction_add)

    assert result is not None
    assert isinstance(result, dict)

    assert result['amount'] == 5000
    assert result['wallet_id'] == test_wallet.id
    assert result['category_id'] == test_category.id

    from sqlalchemy import select
    query = select(Transactions).where(Transactions.id == test_transaction.id)
    saved_transaction = (await db_session.execute(query)).scalar_one_or_none()

    assert saved_transaction is not None
    assert saved_transaction.id == test_transaction.id


changes_list = [
    {'amount': 2000},
    {'amount': 3500},
    {'amount': 265}
]


@pytest.mark.asyncio
@pytest.mark.parametrize('changes', changes_list)
async def test_update_transaction(test_transaction, db_session, changes):
    """
    Тест для обновления транзакции.
    """
    transaction_crud = transaction()
    result = await transaction_crud.update(db_session, test_transaction.id, changes)

    assert result is not None
    assert isinstance(result, dict)

    assert result['amount'] == changes['amount']

    from sqlalchemy import select
    query = select(Transactions).where(Transactions.id == test_transaction.id)
    updated_transaction = (await db_session.execute(query)).scalar_one_or_none()

    assert updated_transaction is not None
    assert updated_transaction.id == test_transaction.id


@pytest.mark.asyncio
async def test_delete_transaction(test_transaction, db_session):
    """
    Тест для удаления транзакции.
    """
    transaction_crud = transaction()
    result = await transaction_crud.delete(db_session, test_transaction.id)

    assert result is not None
    assert result == {'message': f'Удаление записи с id={test_transaction.id} прошло успешно.'}

    from sqlalchemy import select
    query = select(Transactions).where(Transactions.id == test_transaction.id)
    deleted_transaction = (await db_session.execute(query)).scalar_one_or_none()

    assert deleted_transaction is None
