import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_categories_api_get_all(auth_client: AsyncClient, test_category, test_user):
    response = await auth_client.get('/categories/all')
    result = response.json()

    if test_user.is_admin:
        assert response.status_code == 200
        assert isinstance(result, list)
        for res in result:
            assert isinstance(res, dict)
            assert 'id' in res.keys()
            assert 'name' in res.keys()
            assert 'is_public' in res.keys()
            assert 'type' in res.keys()
    else:
        assert response.status_code == 500
        assert result == {'detail': 'Ошибка сервера: 403: У вас нет прав на данное действие.'}


@pytest.mark.asyncio
async def test_categories_api_get_by_id(auth_client: AsyncClient, test_category, test_user):
    response = await auth_client.get('/categories/1')
    result = response.json()

    if test_user.is_admin:
        assert response.status_code == 200
        assert isinstance(result, dict)
        assert 'id' in result.keys()
        assert 'name' in result.keys()
        assert 'is_public' in result.keys()
        assert 'type' in result.keys()

        assert result['id'] == test_category.id
        assert result['name'] == test_category.name
        assert result['is_public'] == test_category.is_public
        assert result['type'] == test_category.type
    else:
        assert response.status_code == 500
        assert result == {'detail': 'Ошибка сервера: 403: У вас нет прав на данное действие.'}



@pytest.mark.asyncio
async def test_categories_api_get_by_id_fail(auth_client: AsyncClient, test_category, test_user):
    response = await auth_client.get('/categories/2')
    assert response.status_code == 500

    result = response.json()
    if test_user.is_admin:
        assert result == {'detail': f'Ошибка сервера: 404: Категория с id=2 не была найдена.'}
    else:
        assert result == {'detail': 'Ошибка сервера: 403: У вас нет прав на данное действие.'}


@pytest.mark.asyncio
async def test_categories_api_create(auth_client: AsyncClient, test_category, test_user):
    data = {
        'name': 'new_category',
        'is_public': True,
        'type': 'Income'
    }

    response = await auth_client.post('/categories/create', json=data)
    assert response.status_code == 200

    result = response.json()

    assert isinstance(result, dict)
    assert 'name' in result.keys()
    assert 'is_public' in result.keys()
    assert 'type' in result.keys()

    assert result['name'] == data['name']
    if test_user.is_admin:
        assert result['is_public'] == data['is_public']
    else:
        assert result['is_public'] == True
    assert result['type'] == data['type']


@pytest.mark.asyncio
async def test_categories_api_update(auth_client: AsyncClient, test_category, test_user):
    data = {
        'name': 'new_category',
        'is_public': False,
        'type': 'Income'
    }

    response = await auth_client.patch('/categories/update/1', json=data)
    assert response.status_code == 200

    result = response.json()

    assert isinstance(result, dict)
    assert 'name' in result.keys()
    assert 'is_public' in result.keys()
    assert 'type' in result.keys()

    assert result['name'] == data['name']
    if test_user.is_admin:
        assert result['is_public'] == data['is_public']
    else:
        assert result['is_public'] == True
    assert result['type'] == data['type']


@pytest.mark.asyncio
async def test_categories_api_update_fail(auth_client: AsyncClient, test_category):
    data = {
        'name': 'new_category',
        'is_public': False,
        'type': 'Income'
    }

    response = await auth_client.patch('/categories/update/2', json=data)
    assert response.status_code == 500

    result = response.json()
    assert result == {'detail': f'Ошибка сервера: 404: Категория с id=2 не была найдена.'}


@pytest.mark.asyncio
async def test_categories_api_delete(auth_client: AsyncClient, test_category, test_user):
    response = await auth_client.delete('/categories/delete/1')
    result = response.json()

    if test_user.is_admin:
        assert response.status_code == 200
        assert result == {'message': f'Удаление записи с id={test_category.id} прошло успешно.'}
    elif not test_category.is_public:
        assert response.status_code == 500
        assert result == {'message': f'Данная категория установлена по умолчанию, ее нельзя изменить.'}


@pytest.mark.asyncio
async def test_categories_api_delete_fail(auth_client: AsyncClient, test_category, test_user):
    response = await auth_client.delete('/categories/delete/2')
    assert response.status_code == 500

    result = response.json()
    assert result == {'detail': f'Ошибка сервера: 404: Категория с id=2 не была найдена.'}

