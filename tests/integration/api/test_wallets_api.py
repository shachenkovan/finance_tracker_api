from decimal import Decimal
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_wallets_api_get_all(auth_client: AsyncClient, test_wallet, test_user):
    response = await auth_client.get('/wallets/all')
    result = response.json()

    assert response.status_code == 200
    assert isinstance(result, list)
    for res in result:
        assert isinstance(res, dict)
        assert 'id' in res.keys()
        assert 'type_of_wallet' in res.keys()
        assert 'amount' in res.keys()
        assert 'user_id' in res.keys()


@pytest.mark.asyncio
async def test_wallets_api_get_by_id(auth_client: AsyncClient, test_wallet, test_user):
    response = await auth_client.get('/wallets/1')
    result = response.json()

    if test_user.is_admin:
        assert response.status_code == 200
        assert isinstance(result, dict)
        assert 'id' in result.keys()
        assert 'type_of_wallet' in result.keys()
        assert 'amount' in result.keys()
        assert 'user_id' in result.keys()

        assert result['id'] == test_wallet.id
        assert result['type_of_wallet'] == test_wallet.type_of_wallet
        assert Decimal(result['amount']) == Decimal(test_wallet.amount)
        assert result['user_id'] == test_user.id
    else:
        assert response.status_code == 500


@pytest.mark.asyncio
async def test_wallets_api_get_by_id_fail(auth_client: AsyncClient, test_wallet, test_user):
    response = await auth_client.get('/wallets/2')
    assert response.status_code == 500

    result = response.json()
    assert result == {'detail': f'Ошибка сервера: 404: Кошелек с id=2 не был найден.'}


@pytest.mark.asyncio
async def test_wallets_api_create(auth_client: AsyncClient, test_wallet, test_user):
    data = {
        'type_of_wallet': 'Cash',
        'amount': 5000,
        'user_id': test_user.id
    }

    response = await auth_client.post('/wallets/create', json=data)
    assert response.status_code == 200

    result = response.json()

    assert isinstance(result, dict)
    assert 'type_of_wallet' in result.keys()
    assert 'amount' in result.keys()
    assert 'user_id' in result.keys()

    assert result['type_of_wallet'] == data['type_of_wallet']
    assert Decimal(result['amount']) == Decimal(data['amount'])
    assert result['user_id'] == data['user_id']


@pytest.mark.asyncio
async def test_wallets_api_update(auth_client: AsyncClient, test_wallet, test_user):
    data = {
        'type_of_wallet': 'Card',
        'amount': 1000
    }

    response = await auth_client.patch('/wallets/update/1', json=data)
    assert response.status_code == 200

    result = response.json()

    assert isinstance(result, dict)
    assert 'type_of_wallet' in result.keys()
    assert 'amount' in result.keys()

    assert result['type_of_wallet'] == data['type_of_wallet']
    assert Decimal(result['amount']) == Decimal(data['amount'])


@pytest.mark.asyncio
async def test_wallets_api_update_fail(auth_client: AsyncClient, test_wallet, test_user):
    data = {
        'type_of_wallet': 'Card',
        'amount': 1000
    }

    response = await auth_client.patch('/wallets/update/2', json=data)
    assert response.status_code == 500

    result = response.json()
    assert result == {'detail': f'Ошибка сервера: 404: Кошелек с id=2 не был найден.'}


@pytest.mark.asyncio
async def test_wallets_api_delete(auth_client: AsyncClient, test_wallet, test_user):
    response = await auth_client.delete('/wallets/delete/1')
    if test_user.is_admin:
        assert response.status_code == 200

    result = response.json()
    assert result == {'message': f'Удаление записи с id={test_wallet.id} прошло успешно.'}


@pytest.mark.asyncio
async def test_wallets_api_delete_fail(auth_client: AsyncClient, test_wallet, test_user):
    response = await auth_client.delete('/wallets/delete/2')
    assert response.status_code == 500

    result = response.json()
    assert result == {'detail': f'Ошибка сервера: 404: Кошелек с id=2 не найден.'}

