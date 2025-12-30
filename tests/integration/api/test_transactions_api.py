from decimal import Decimal
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_transactions_api_get_all(auth_client: AsyncClient, test_transaction, test_wallet, test_category, test_user):
    response = await auth_client.get('/transactions/all')
    result = response.json()

    assert response.status_code == 200
    assert isinstance(result, list)
    for res in result:
        assert isinstance(res, dict)
        assert 'id' in res.keys()
        assert 'amount' in res.keys()
        assert 'wallet_id' in res.keys()
        assert 'category_id' in res.keys()


@pytest.mark.asyncio
async def test_transactions_api_get_by_id(auth_client: AsyncClient, test_transaction, test_wallet, test_category):
    response = await auth_client.get('/transactions/1')
    result = response.json()

    assert response.status_code == 200
    assert isinstance(result, dict)
    assert 'id' in result.keys()
    assert 'amount' in result.keys()
    assert 'wallet_id' in result.keys()
    assert 'category_id' in result.keys()

    assert result['id'] == test_transaction.id
    assert Decimal(result['amount']) == Decimal(test_transaction.amount)
    assert result['wallet_id'] == test_wallet.id
    assert result['category_id'] == test_category.id


@pytest.mark.asyncio
async def test_transactions_api_get_by_id_fail(auth_client: AsyncClient, test_transaction, test_wallet, test_category):
    response = await auth_client.get('/transactions/2')
    assert response.status_code == 500

    result = response.json()
    assert result == {'detail': f'Ошибка сервера: 404: Транзакция с id=2 не найдена.'}


@pytest.mark.asyncio
async def test_transactions_api_create(auth_client: AsyncClient, test_transaction, test_wallet, test_category):
    data = {
        'amount': 500,
        'wallet_id': test_wallet.id,
        'category_id': test_category.id
    }

    response = await auth_client.post('/transactions/create', json=data)
    assert response.status_code == 200

    result = response.json()

    assert isinstance(result, dict)
    assert 'amount' in result.keys()
    assert 'wallet_id' in result.keys()
    assert 'category_id' in result.keys()

    assert Decimal(result['amount']) == data['amount']
    assert result['wallet_id'] == data['wallet_id']
    assert result['category_id'] == data['category_id']


@pytest.mark.asyncio
async def test_transactions_api_update(auth_client: AsyncClient, test_transaction, test_wallet, test_category):
    data = {
        'amount': 1000,
        'wallet_id': test_wallet.id,
        'category_id': test_category.id
    }

    response = await auth_client.patch('/transactions/update/1', json=data)
    assert response.status_code == 200

    result = response.json()

    assert isinstance(result, dict)
    assert 'amount' in result.keys()
    assert 'wallet_id' in result.keys()
    assert 'category_id' in result.keys()

    assert Decimal(result['amount']) == data['amount']
    assert result['wallet_id'] == data['wallet_id']
    assert result['category_id'] == data['category_id']


@pytest.mark.asyncio
async def test_transactions_api_update_fail(auth_client: AsyncClient, test_transaction, test_wallet, test_category):
    data = {
        'amount': 500,
        'wallet_id': test_wallet.id,
        'category_id': test_category.id
    }

    response = await auth_client.patch('/transactions/update/2', json=data)
    assert response.status_code == 500

    result = response.json()
    assert result == {'detail': f'Ошибка сервера: 404: Транзакция с id=2 не найдена.'}


@pytest.mark.asyncio
async def test_transactions_api_delete(auth_client: AsyncClient, test_transaction, test_wallet, test_category, test_user):
    response = await auth_client.delete('/transactions/delete/1')
    result = response.json()

    assert response.status_code == 200
    assert result == {'message': f'Удаление записи с id={test_transaction.id} прошло успешно.'}


@pytest.mark.asyncio
async def test_transactions_api_delete_fail(auth_client: AsyncClient, test_wallet, test_category, test_user):
    response = await auth_client.delete('/transactions/delete/2')
    assert response.status_code == 500

    result = response.json()
    print(result)
    if test_user.is_admin:
        assert result == {'detail': f'Ошибка сервера: Транзакция с id=2 не найдена.'}
    else:
        assert result == {'detail': f'Ошибка сервера: 404: Транзакция с id=2 не найдена.'}

