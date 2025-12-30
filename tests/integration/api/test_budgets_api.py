from decimal import Decimal
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_budgets_api_get_all(auth_client: AsyncClient, test_budget, test_user, test_category):
    response = await auth_client.get('/budgets/all')
    result = response.json()

    assert response.status_code == 200
    assert isinstance(result, list)
    for res in result:
        assert isinstance(res, dict)
        assert 'id' in res.keys()
        assert 'name' in res.keys()
        assert 'amount' in res.keys()
        assert 'category_id' in res.keys()
        assert 'user_id' in res.keys()


@pytest.mark.asyncio
async def test_budgets_api_get_by_id(auth_client: AsyncClient, test_budget, test_user, test_category):
    response = await auth_client.get('/budgets/1')
    result = response.json()

    assert response.status_code == 200
    assert isinstance(result, dict)
    assert 'id' in result.keys()
    assert 'name' in result.keys()
    assert 'amount' in result.keys()
    assert 'category_id' in result.keys()
    assert 'user_id' in result.keys()

    assert result['id'] == test_budget.id
    assert result['name'] == test_budget.name
    assert Decimal(result['amount']) == Decimal(test_budget.amount)
    assert result['category_id'] == test_category.id
    assert result['user_id'] == test_user.id


@pytest.mark.asyncio
async def test_budgets_api_get_by_id_fail(auth_client: AsyncClient, test_budget, test_user):
    response = await auth_client.get('/budgets/2')
    assert response.status_code == 500

    result = response.json()
    assert result == {'detail': f'Ошибка сервера: 404: Бюджет с id=2 не найден.'}


@pytest.mark.asyncio
async def test_budgets_api_create(auth_client: AsyncClient, test_budget, test_user, test_category):
    data = {
        'name': 'new_budget',
        'amount': 3000,
        'category_id': test_category.id,
        'user_id': test_user.id
    }

    response = await auth_client.post('/budgets/create', json=data)
    assert response.status_code == 200

    result = response.json()

    assert isinstance(result, dict)
    assert 'name' in result.keys()
    assert 'amount' in result.keys()
    assert 'category_id' in result.keys()
    assert 'user_id' in result.keys()

    assert result['name'] == data['name']
    assert Decimal(result['amount']) == Decimal(data['amount'])
    assert result['category_id'] == data['category_id']
    assert result['user_id'] == data['user_id']


@pytest.mark.asyncio
async def test_budgets_api_update(auth_client: AsyncClient, test_budget, test_user, test_category):
    data = {
        'name': 'new_budget_update1',
        'amount': 10000,
        'category_id': test_category.id,
        'user_id': test_user.id
    }

    response = await auth_client.patch('/budgets/update/1', json=data)
    print(response)
    assert response.status_code == 200

    result = response.json()

    assert isinstance(result, dict)
    assert 'name' in result.keys()
    assert 'amount' in result.keys()
    assert 'category_id' in result.keys()
    assert 'user_id' in result.keys()

    assert result['name'] == data['name']
    assert Decimal(result['amount']) == Decimal(data['amount'])
    assert result['category_id'] == data['category_id']
    assert result['user_id'] == data['user_id']


@pytest.mark.asyncio
async def test_budgets_api_update_fail(auth_client: AsyncClient, test_budget, test_user, test_category):
    data = {
        'name': 'new_budget_update',
        'amount': 10000,
        'category_id': test_category.id,
        'user_id': test_user.id
    }

    response = await auth_client.patch('/budgets/update/2', json=data)
    assert response.status_code == 500

    result = response.json()
    assert result == {'detail': f'Ошибка сервера: 404: Бюджет с id=2 не найден.'}


@pytest.mark.asyncio
async def test_budgets_api_delete(auth_client: AsyncClient, test_budget, test_user):
    response = await auth_client.delete('/budgets/delete/1')
    if test_user.is_admin:
        assert response.status_code == 200

    result = response.json()
    assert result == {'message': f'Удаление записи с id={test_budget.id} прошло успешно.'}


@pytest.mark.asyncio
async def test_budgets_api_delete_fail(auth_client: AsyncClient, test_budget, test_user):
    response = await auth_client.delete('/budgets/delete/2')
    assert response.status_code == 500

    result = response.json()
    assert result == {'detail': f'Ошибка сервера: 404: Бюджет с id=2 не найден.'}

