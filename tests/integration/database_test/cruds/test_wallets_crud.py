import pytest
from database.cruds import wallet
from database.models import Wallets


@pytest.mark.asyncio
async def test_get_all_wallets(test_wallet, test_user, db_session):
    """
    Тест для получения всех кошельков.
    """
    wallet_crud = wallet()
    result = await wallet_crud.get_all(db_session)

    assert result is not None

    wallets_ids = [wallets.id for wallets in result]
    assert test_wallet.id in wallets_ids


@pytest.mark.asyncio
async def test_get_wallet_by_id(test_wallet, test_user, db_session):
    """
    Тест для получения кошелька по id.
    """
    wallet_crud = wallet()
    result = await wallet_crud.get_by_id(db_session, test_wallet.id)

    assert result is not None
    assert test_wallet.id == result.id


@pytest.mark.asyncio
async def test_add_wallet(test_wallet, test_user, db_session):
    """
    Тест для добавления кошелька.
    """
    wallet_crud = wallet()
    wallet_add = Wallets(
        type_of_wallet='Card',
        amount=3000,
        user_id=test_user.id
    )

    result = await wallet_crud.create(db_session, wallet_add)

    assert result is not None
    assert isinstance(result, dict)

    assert result['type_of_wallet'] == 'Card'
    assert result['amount'] == 3000
    assert result['user_id'] == test_user.id

    from sqlalchemy import select
    query = select(Wallets).where(Wallets.id == test_wallet.id)
    saved_wallet = (await db_session.execute(query)).scalar_one_or_none()

    assert saved_wallet is not None
    assert saved_wallet.id == test_wallet.id


changes_list = [
    {'type_of_wallet': 'Cash'},
    {'amount': 5000},
    {'type_of_wallet': 'Bank', 'amount': 10000}
]


@pytest.mark.asyncio
@pytest.mark.parametrize('changes', changes_list)
async def test_update_wallet(test_wallet, db_session, changes):
    """
    Тест для обновления кошелька.
    """
    wallet_crud = wallet()
    result = await wallet_crud.update(db_session, test_wallet.id, changes)

    assert result is not None
    assert isinstance(result, dict)

    if 'type_of_wallet' in changes.keys():
        assert result['type_of_wallet'] == changes['type_of_wallet']
    if 'amount' in changes.keys():
        assert result['amount'] == changes['amount']

    from sqlalchemy import select
    query = select(Wallets).where(Wallets.id == test_wallet.id)
    updated_wallet = (await db_session.execute(query)).scalar_one_or_none()

    assert updated_wallet is not None
    assert updated_wallet.id == test_wallet.id


@pytest.mark.asyncio
async def test_delete_wallet(test_wallet, db_session):
    """
    Тест для удаления кошелька.
    """
    wallet_crud = wallet()
    result = await wallet_crud.delete(db_session, test_wallet.id)

    assert result is not None
    assert result == {'message': f'Удаление записи с id={test_wallet.id} прошло успешно.'}

    from sqlalchemy import select
    query = select(Wallets).where(Wallets.id == test_wallet.id)
    deleted_wallet = (await db_session.execute(query)).scalar_one_or_none()

    assert deleted_wallet is None
