from decimal import Decimal
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_goals_api_get_all(auth_client: AsyncClient, test_goal, test_user):
    response = await auth_client.get('/goals/all')
    result = response.json()

    assert response.status_code == 200
    assert isinstance(result, list)
    for res in result:
        assert isinstance(res, dict)
        assert 'id' in res.keys()
        assert 'name' in res.keys()
        assert 'cost' in res.keys()
        assert 'deadline' in res.keys()
        assert 'actual_amount' in res.keys()
        assert 'user_id' in res.keys()


@pytest.mark.asyncio
async def test_goals_api_get_by_id(auth_client: AsyncClient, test_goal, test_user,):
    response = await auth_client.get('/goals/1')
    result = response.json()

    assert response.status_code == 200
    assert isinstance(result, dict)
    assert 'id' in result.keys()
    assert 'name' in result.keys()
    assert 'cost' in result.keys()
    assert 'deadline' in result.keys()
    assert 'actual_amount' in result.keys()
    assert 'user_id' in result.keys()

    assert result['id'] == test_goal.id
    assert result['name'] == test_goal.name
    assert Decimal(result['cost']) == Decimal(test_goal.cost)
    assert result['deadline'] == str(test_goal.deadline)
    assert Decimal(result['actual_amount']) == Decimal(test_goal.actual_amount)
    assert result['user_id'] == test_user.id


@pytest.mark.asyncio
async def test_goals_api_get_by_id_fail(auth_client: AsyncClient, test_goal, test_user):
    response = await auth_client.get('/goals/2')
    assert response.status_code == 500

    result = response.json()
    assert result == {'detail': f'Ошибка сервера: 404: Цель с id=2 не была найдена.'}


@pytest.mark.asyncio
async def test_goals_api_create(auth_client: AsyncClient, test_goal, test_user):
    data = {
        'name': 'new_goal',
        'cost': 3000,
        'deadline': '2027-01-01',
        'actual_amount': 1000,
        'user_id': test_user.id
    }

    response = await auth_client.post('/goals/create', json=data)
    assert response.status_code == 200

    result = response.json()

    assert isinstance(result, dict)
    assert 'name' in result.keys()
    assert 'cost' in result.keys()
    assert 'deadline' in result.keys()
    assert 'actual_amount' in result.keys()
    assert 'user_id' in result.keys()

    assert result['name'] == data['name']
    assert Decimal(result['cost']) == Decimal(data['cost'])
    assert result['deadline'] == data['deadline']
    assert Decimal(result['actual_amount']) == Decimal(data['actual_amount'])
    assert result['user_id'] == data['user_id']


@pytest.mark.asyncio
async def test_goals_api_update(auth_client: AsyncClient, test_goal, test_user):
    data = {
        'name': 'new_goal',
        'cost': 3000,
        'deadline': '2027-01-01',
        'actual_amount': 1000,
        'user_id': test_user.id
    }

    response = await auth_client.patch('/goals/update/1', json=data)
    assert response.status_code == 200

    result = response.json()

    assert isinstance(result, dict)
    assert 'name' in result.keys()
    assert 'cost' in result.keys()
    assert 'deadline' in result.keys()
    assert 'actual_amount' in result.keys()
    assert 'user_id' in result.keys()

    assert result['name'] == data['name']
    assert Decimal(result['cost']) == Decimal(data['cost'])
    assert result['deadline'] == data['deadline']
    assert Decimal(result['actual_amount']) == Decimal(data['actual_amount'])
    assert result['user_id'] == data['user_id']


@pytest.mark.asyncio
async def test_goals_api_update_fail(auth_client: AsyncClient, test_goal, test_user, test_category):
    data = {
        'name': 'new_goal',
        'cost': 3000,
        'deadline': '2027-01-01',
        'actual_amount': 1000,
        'user_id': test_user.id
    }

    response = await auth_client.patch('/goals/update/2', json=data)
    assert response.status_code == 500

    result = response.json()
    assert result == {'detail': f'Ошибка сервера: 404: Цель с id=2 не была найдена.'}


@pytest.mark.asyncio
async def test_goals_api_delete(auth_client: AsyncClient, test_goal, test_user):
    response = await auth_client.delete('/goals/delete/1')
    result = response.json()

    if test_user.is_admin:
        assert response.status_code == 200
        assert result == {'message': f'Удаление записи с id={test_goal.id} прошло успешно.'}
    elif test_goal.user_id != test_user.id:
        assert response.status_code == 500
        assert result == {'message': f'Данная категория установлена по умолчанию, ее нельзя изменить.'}




@pytest.mark.asyncio
async def test_goals_api_delete_fail(auth_client: AsyncClient, test_goal, test_user):
    response = await auth_client.delete('/goals/delete/2')
    assert response.status_code == 500

    result = response.json()
    assert result == {'detail': f'Ошибка сервера: 404: Цель с id=2 не найдена.'}

